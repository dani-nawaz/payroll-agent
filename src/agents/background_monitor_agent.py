"""Background Monitor Agent - Runs continuously in separate process."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import signal
import sys
import os

from agents import Agent, function_tool
from pydantic import BaseModel

from src.config import settings
from src.services.email_service import EmailService
from src.services.email_monitor_service import EmailMonitorService, EmailMessage
from src.repositories.csv_repository import CSVTimesheetRepository
from src.models.company_policy import PolicyRepository, ValidReason


class MonitoringLog(BaseModel):
    """Model for monitoring log entries."""
    timestamp: datetime
    level: str  # "INFO", "WARNING", "ERROR", "NOTIFICATION"
    message: str
    details: Optional[Dict] = None


class BackgroundMonitorAgent:
    """Background agent that runs continuously to monitor email replies."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.repository = CSVTimesheetRepository()
        self.policy_repository = PolicyRepository()
        self.email_monitor = EmailMonitorService()
        self.monitoring_active = False
        self.logs: List[MonitoringLog] = []
        self.log_file = Path("logs/background_monitor.log")
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Set up logging
        self._setup_logging()
        
        # Set up email monitoring
        self.email_monitor.set_email_service(self.email_service)
        self.email_monitor.set_reply_callback(self._handle_email_reply)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop_monitoring()
        sys.exit(0)
    
    def log_entry(self, level: str, message: str, details: Optional[Dict] = None):
        """Add a log entry."""
        log_entry = MonitoringLog(
            timestamp=datetime.now(),
            level=level,
            message=message,
            details=details
        )
        self.logs.append(log_entry)
        
        # Keep only last 1000 logs in memory
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
        
        # Log to file
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "NOTIFICATION":
            self.logger.info(f"[NOTIFICATION] {message}")
        else:
            self.logger.info(message)
    
    async def start_background_monitoring(self):
        """Start the background monitoring process."""
        self.log_entry("INFO", "Starting Background Monitor Agent")
        self.log_entry("INFO", f"Log file: {self.log_file.absolute()}")
        
        self.monitoring_active = True
        
        try:
            # Start email monitoring
            await self.email_monitor.start_monitoring()
            
            # Keep the process running
            while self.monitoring_active:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.log_entry("ERROR", f"Background monitoring error: {str(e)}")
            raise e
        finally:
            self.log_entry("INFO", "Background Monitor Agent stopped")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.log_entry("INFO", "Stopping background monitoring...")
        self.monitoring_active = False
        asyncio.create_task(self.email_monitor.stop_monitoring())
    
    async def _handle_email_reply(self, email_message: EmailMessage):
        """Handle incoming email reply."""
        self.log_entry("NOTIFICATION", f"New email reply from {email_message.from_name}")
        
        try:
            # Analyze the reason using AI
            reason_valid, reason_type, valid_reason = await self._validate_reason_content(email_message.content)
            
            # Log the analysis
            analysis_details = {
                "from_email": email_message.from_email,
                "from_name": email_message.from_name,
                "subject": email_message.subject,
                "content_preview": email_message.content[:100] + "...",
                "reason_valid": reason_valid,
                "reason_type": reason_type,
                "timesheet_date": email_message.timesheet_date
            }
            
            if reason_valid:
                self.log_entry("INFO", f"Valid reason detected: {reason_type}", analysis_details)
            else:
                self.log_entry("WARNING", "Invalid reason - needs follow-up", analysis_details)
            
        except Exception as e:
            self.log_entry("ERROR", f"Error processing email reply: {str(e)}")
    
    async def _validate_reason_content(self, content: str) -> tuple[bool, Optional[str], Optional[ValidReason]]:
        """Validate if the content contains a valid reason using LLM analysis."""
        try:
            # Use LLM to analyze the reason intelligently
            analysis_result = await self._analyze_reason_with_llm(content)
            
            if analysis_result['is_valid']:
                # Find matching policy reason or create a new one
                reason_type = analysis_result.get('reason_type', 'other')
                valid_reason = await self._get_or_create_reason_type(reason_type, analysis_result)
                return True, reason_type, valid_reason
            
            return False, None, None
            
        except Exception as e:
            self.log_entry("ERROR", f"LLM analysis failed: {str(e)}")
            return False, None, None
    
    async def _analyze_reason_with_llm(self, content: str) -> dict:
        """Use LLM to intelligently analyze employee reason."""
        prompt = f"""
        Analyze this employee's reason for missing work hours and determine if it's valid:

        Employee Response: "{content}"

        Please analyze this response and provide:
        1. Is this a valid business reason for missing work? (true/false)
        2. What type of reason is this? (sick, personal, work_from_home, leave, training, bereavement, other)
        3. Confidence level (0-100)
        4. Brief explanation of your reasoning

        Respond in JSON format:
        {{
            "is_valid": true/false,
            "reason_type": "type",
            "confidence": 85,
            "explanation": "Brief explanation",
            "requires_approval": true/false,
            "suggested_keywords": ["keyword1", "keyword2"]
        }}
        """
        
        try:
            # Use the agent's model to analyze
            from agents import Agent
            analysis_agent = Agent(
                name="Reason Analyzer",
                instructions="You are an expert at analyzing employee reasons for missing work. Provide accurate, fair analysis.",
                model=settings.openai.model,
                tools=[]
            )
            
            # Get LLM response
            from agents import Runner
            runner = Runner()
            result = await runner.run(analysis_agent, prompt)
            
            # Parse the response
            import re
            
            # Extract JSON from response
            response_text = result.final_output or ""
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                import json
                analysis = json.loads(json_match.group())
                return analysis
            else:
                # Fallback analysis
                return {
                    "is_valid": len(content.strip()) > 10 and "forgot" not in content.lower(),
                    "reason_type": "other",
                    "confidence": 50,
                    "explanation": "Fallback analysis",
                    "requires_approval": True,
                    "suggested_keywords": []
                }
                
        except Exception as e:
            self.log_entry("ERROR", f"LLM analysis failed: {str(e)}")
            # Fallback to basic validation
            return {
                "is_valid": len(content.strip()) > 10,
                "reason_type": "other",
                "confidence": 30,
                "explanation": "Analysis failed, using fallback",
                "requires_approval": True,
                "suggested_keywords": []
            }
    
    async def _get_or_create_reason_type(self, reason_type: str, analysis: dict) -> ValidReason:
        """Get existing reason type or create new one based on LLM analysis."""
        # Check if reason type already exists
        existing_reasons = self.policy_repository.get_valid_reasons()
        for reason in existing_reasons:
            if reason.reason_type == reason_type:
                return reason
        
        # Create new reason type based on LLM analysis
        new_reason = ValidReason(
            reason_type=reason_type,
            keywords=analysis.get('suggested_keywords', [reason_type]),
            description=analysis.get('explanation', f'LLM-identified {reason_type} reason'),
            requires_approval=analysis.get('requires_approval', True),
            max_days_per_month=None,
            requires_documentation=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add to policy repository
        self.policy_repository.add_valid_reason("default", new_reason)
        return new_reason
    
    def get_logs(self, limit: int = 50, level: Optional[str] = None) -> List[MonitoringLog]:
        """Get monitoring logs."""
        logs = self.logs
        
        if level:
            logs = [log for log in logs if log.level == level]
        
        return logs[-limit:] if limit else logs
    
    def get_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            "monitoring_active": self.monitoring_active,
            "total_logs": len(self.logs),
            "log_file": str(self.log_file.absolute()),
            "last_log": self.logs[-1].dict() if self.logs else None,
            "email_monitor_status": self.email_monitor.get_monitoring_status()
        }


# Global instance for the background agent
_background_monitor_instance = None


@function_tool
async def start_background_monitor() -> str:
    """Start the background monitoring agent."""
    global _background_monitor_instance
    
    if _background_monitor_instance and _background_monitor_instance.monitoring_active:
        return "Background monitor is already running."
    
    try:
        _background_monitor_instance = BackgroundMonitorAgent()
        asyncio.create_task(_background_monitor_instance.start_background_monitoring())
        return "✅ Background monitor started successfully. Check logs with 'get monitor logs'"
    except Exception as e:
        return f"❌ Failed to start background monitor: {str(e)}"


@function_tool
async def stop_background_monitor() -> str:
    """Stop the background monitoring agent."""
    global _background_monitor_instance
    
    if not _background_monitor_instance:
        return "Background monitor is not running."
    
    try:
        _background_monitor_instance.stop_monitoring()
        return "✅ Background monitor stopped successfully."
    except Exception as e:
        return f"❌ Failed to stop background monitor: {str(e)}"


@function_tool
async def get_monitor_logs(limit: int = 20, level: Optional[str] = None) -> str:
    """Get monitoring logs."""
    global _background_monitor_instance
    
    if not _background_monitor_instance:
        return "Background monitor is not running. Start it with 'start background monitor'"
    
    try:
        logs = _background_monitor_instance.get_logs(limit, level)
        
        if not logs:
            return "No logs found."
        
        result = f"📋 Background Monitor Logs (showing last {len(logs)} entries):\n\n"
        
        for log in logs:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            level_icon = {
                "INFO": "[INFO]",
                "WARNING": "[WARNING]", 
                "ERROR": "[ERROR]",
                "NOTIFICATION": "[NOTIFICATION]"
            }.get(log.level, "[INFO]")
            
            result += f"{level_icon} [{timestamp}] {log.level}: {log.message}\n"
            
            if log.details:
                result += f"   Details: {json.dumps(log.details, indent=2)}\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"[ERROR] Failed to get logs: {str(e)}"


@function_tool
async def get_monitor_status() -> str:
    """Get background monitor status."""
    global _background_monitor_instance
    
    if not _background_monitor_instance:
        return "Background monitor is not running. Start it with 'start background monitor'"
    
    try:
        status = _background_monitor_instance.get_status()
        
        result = "Background Monitor Status:\n\n"
        result += f"• Active: {'Yes' if status['monitoring_active'] else 'No'}\n"
        result += f"• Total Logs: {status['total_logs']}\n"
        result += f"• Log File: {status['log_file']}\n"
        
        if status['last_log']:
            result += f"• Last Log: {status['last_log']['timestamp']} - {status['last_log']['message']}\n"
        
        # Email monitor status
        email_status = status['email_monitor_status']
        result += f"\nEmail Monitoring:\n"
        result += f"• Active: {'Yes' if email_status['monitoring_active'] else 'No'}\n"
        result += f"• Last Check: {email_status['last_check_time'] or 'Never'}\n"
        result += f"• Processed Messages: {email_status['processed_messages_count']}\n"
        result += f"• Check Interval: {email_status['check_interval_seconds']} seconds\n"
        
        return result
        
    except Exception as e:
        return f"[ERROR] Failed to get status: {str(e)}"


def create_background_monitor_agent() -> Agent:
    """Create the Background Monitor Agent."""
    
    instructions = """You are the Background Monitor Agent.
    
    Your responsibilities:
    1. Run continuously in the background to monitor email replies
    2. Process and analyze email replies using AI
    3. Maintain detailed logs of all activities
    4. Provide status and log access to users
    
    Available tools:
    - start_background_monitor(): Start the background monitoring process
    - stop_background_monitor(): Stop the background monitoring process
    - get_monitor_logs(limit, level): Get monitoring logs
    - get_monitor_status(): Get current monitoring status
    
    IMPORTANT: This agent runs in a separate background process and maintains its own logs.
    Users can check logs and status anytime without interrupting the monitoring.
    """
    
    tools = [
        start_background_monitor,
        stop_background_monitor,
        get_monitor_logs,
        get_monitor_status
    ]
    
    return Agent(
        name="Background Monitor Agent",
        instructions=instructions,
        model=settings.openai.model,
        tools=tools
    )


# Standalone script to run the background monitor
async def run_background_monitor():
    """Run the background monitor as a standalone process."""
    print("[INFO] Starting Background Monitor Agent...")
    
    monitor = BackgroundMonitorAgent()
    
    try:
        await monitor.start_background_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt, shutting down...")
        monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(run_background_monitor())
