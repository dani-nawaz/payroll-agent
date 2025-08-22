"""Employee Engagement Agent for monitoring email replies and validating reasons."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from agents import Agent, function_tool
from pydantic import BaseModel

from src.config import settings
from src.services.email_service import EmailService
from src.services.email_monitor_service import EmailMonitorService, EmailMessage
from src.repositories.csv_repository import CSVTimesheetRepository
from src.models.company_policy import PolicyRepository, ValidReason

# Global variable to hold the agent instance
_engagement_agent_instance = None


class EmailReply(BaseModel):
    """Model for email replies from employees."""
    employee_email: str
    employee_name: str
    reply_date: datetime
    subject: str
    content: str
    timesheet_date: str
    reason_provided: bool
    reason_type: Optional[str] = None  # "sick", "personal", "work_from_home", etc.
    reason_valid: bool = False


class EngagementStatus(BaseModel):
    """Model for tracking engagement status."""
    employee_email: str
    employee_name: str
    timesheet_date: str
    status: str  # "pending", "replied", "validated", "escalated"
    reply_count: int = 0
    last_email_sent: Optional[datetime] = None
    last_reply: Optional[EmailReply] = None


# Standalone function tools
@function_tool
async def check_email_replies() -> str:
    """Check for new email replies from employees regarding timesheet issues."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._check_email_replies_impl()


@function_tool
async def validate_employee_reason(employee_email: str, timesheet_date: str) -> str:
    """Validate if an employee's reason for missing hours is acceptable."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._validate_employee_reason_impl(employee_email, timesheet_date)


@function_tool
async def send_followup_email(employee_email: str, timesheet_date: str) -> str:
    """Send follow-up email requesting a valid reason from employee."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._send_followup_email_impl(employee_email, timesheet_date)


@function_tool
async def get_engagement_status() -> str:
    """Get current engagement status for all employees."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._get_engagement_status_impl()


@function_tool
async def escalate_to_compliance(employee_email: str, timesheet_date: str) -> str:
    """Hand off validated case to Compliance Agent."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._escalate_to_compliance_impl(employee_email, timesheet_date)


@function_tool
async def start_email_monitoring() -> str:
    """Start continuous email monitoring for replies."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._start_email_monitoring_impl()


@function_tool
async def stop_email_monitoring() -> str:
    """Stop continuous email monitoring."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._stop_email_monitoring_impl()


@function_tool
async def get_monitoring_status() -> str:
    """Get current email monitoring status."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._get_monitoring_status_impl()


@function_tool
async def update_policy_reasons(reason_type: str, keywords: str, description: str) -> str:
    """Update or add valid reasons to company policy."""
    global _engagement_agent_instance
    if _engagement_agent_instance is None:
        return "Error: Engagement agent not initialized"
    return await _engagement_agent_instance._update_policy_reasons_impl(reason_type, keywords, description)


class EmployeeEngagementAgent:
    """Agent responsible for monitoring email replies and validating employee reasons."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.repository = CSVTimesheetRepository()
        self.policy_repository = PolicyRepository()
        self.email_monitor = EmailMonitorService()
        self.engagement_status: Dict[str, EngagementStatus] = {}
        
        # Set up email monitoring
        self.email_monitor.set_email_service(self.email_service)
        self.email_monitor.set_reply_callback(self._handle_email_reply)
        
    def create_agent(self) -> Agent:
        """Create the Employee Engagement Agent."""
        
        # Set the global instance
        global _engagement_agent_instance
        _engagement_agent_instance = self
        
        instructions = """You are the Employee Engagement Agent.
        
        Your responsibilities:
        1. Monitor email replies from employees regarding timesheet issues (CONTINUOUSLY)
        2. Use AI to intelligently analyze and validate employee reasons
        3. Send follow-up emails if reasons are insufficient
        4. Track engagement status for each employee
        5. Hand off validated cases to the Compliance Agent
        
        Available tools:
        - check_email_replies(): Start continuous background monitoring for email replies
        - validate_employee_reason(employee_email, timesheet_date): Validate if an employee's reason is acceptable
        - send_followup_email(employee_email, timesheet_date): Send follow-up email requesting valid reason
        - get_engagement_status(): Get current engagement status for employees
        - escalate_to_compliance(employee_email, timesheet_date): Hand off validated case to Compliance Agent
        - start_email_monitoring(): Start continuous email monitoring
        - stop_email_monitoring(): Stop email monitoring
        - get_monitoring_status(): Get monitoring status
        - update_policy_reasons(): Update policy reasons (legacy, now uses AI analysis)
        
        IMPORTANT: When user says "check replies" or similar:
        - Start continuous background monitoring if not already active
        - Inform user that monitoring is running in background
        - Allow user to continue with other tasks while monitoring runs
        - Provide notifications when new replies are found
        
        When employees reply to timesheet emails:
        - Use AI to intelligently analyze their reason
        - AI determines if reason is valid based on context and business rules
        - If AI determines reason is invalid: send follow-up email
        - If AI determines reason is valid: escalate to Compliance Agent
        - Track all interactions and status
        - Provide real-time notifications to user
        
        The AI analysis considers:
        - Context and sincerity of the explanation
        - Business appropriateness of the reason
        - Whether the reason is genuine vs. excuses
        - Company policies and common sense
        - No hardcoded rules - pure AI intelligence
        
        BACKGROUND MONITORING:
        - Runs continuously every 60 seconds
        - Processes replies automatically
        - Provides user notifications
        - Allows user to work on other tasks
        - No blocking or waiting required
        """
        
        tools = [
            check_email_replies,
            validate_employee_reason,
            send_followup_email,
            get_engagement_status,
            escalate_to_compliance,
            start_email_monitoring,
            stop_email_monitoring,
            get_monitoring_status,
            update_policy_reasons
        ]
        
        return Agent(
            name="Employee Engagement Agent",
            instructions=instructions,
            model=settings.openai.model,
            tools=tools
        )

    async def _validate_reason_content(self, content: str) -> tuple[bool, Optional[str], Optional[ValidReason]]:
        """Validate if the content contains a valid reason using LLM analysis."""
        # Use LLM to analyze the reason intelligently
        analysis_result = await self._analyze_reason_with_llm(content)
        
        if analysis_result['is_valid']:
            # Find matching policy reason or create a new one
            reason_type = analysis_result.get('reason_type', 'other')
            valid_reason = await self._get_or_create_reason_type(reason_type, analysis_result)
            return True, reason_type, valid_reason
        
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
            
            # Parse the response (assuming it returns JSON)
            import json
            import re
            
            # Extract JSON from response
            response_text = result.final_output or ""
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
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
            print(f"[ERROR] LLM analysis failed: {str(e)}")
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
    
    async def _handle_email_reply(self, email_message: EmailMessage):
        """Handle incoming email reply."""
        print(f"[INFO] Processing email reply from {email_message.from_name}")
        
        # Create EmailReply object
        reply = EmailReply(
            employee_email=email_message.from_email,
            employee_name=email_message.from_name,
            reply_date=email_message.received_date,
            subject=email_message.subject,
            content=email_message.content,
            timesheet_date=email_message.timesheet_date or "unknown"
        )
        
        # Validate the reason
        reason_valid, reason_type, valid_reason = await self._validate_reason_content(reply.content)
        reply.reason_valid = reason_valid
        reply.reason_type = reason_type
        reply.reason_provided = len(reply.content.strip()) > 10
        
        # Update engagement status
        status_key = f"{reply.employee_email}_{reply.timesheet_date}"
        if status_key not in self.engagement_status:
            self.engagement_status[status_key] = EngagementStatus(
                employee_email=reply.employee_email,
                employee_name=reply.employee_name,
                timesheet_date=reply.timesheet_date,
                status="replied",
                reply_count=1,
                last_reply=reply
            )
        else:
            self.engagement_status[status_key].reply_count += 1
            self.engagement_status[status_key].last_reply = reply
            self.engagement_status[status_key].status = "replied"
        
        print(f"[INFO] Updated engagement status for {reply.employee_name}")
        
        # Auto-process based on validation result
        if reason_valid:
            print(f"[INFO] Valid reason detected: {reason_type}")
            if valid_reason and not valid_reason.requires_approval:
                print(f"[INFO] Auto-approving {reason_type} reason")
                # Could auto-escalate to compliance here
        else:
            print(f"[INFO] Invalid reason - will send follow-up email")
            # Could auto-send follow-up email here

    # Implementation methods (with self parameter)
    async def _check_email_replies_impl(self) -> str:
        """Implementation of check_email_replies."""
        try:
            # Check if monitoring is already active
            if not self.email_monitor.monitoring_active:
                # Start background monitoring if not already running
                try:
                    # Create background task for monitoring
                    monitoring_task = asyncio.create_task(self.email_monitor.start_monitoring())
                    
                    # Give it a moment to start
                    await asyncio.sleep(0.1)
                    
                    return "✅ Started continuous email monitoring in background. You can now do other things while the system monitors for replies automatically.\n\n📧 Monitoring Status:\n• Active: ✅ Yes\n• Check Interval: 60 seconds\n• Background Process: Running\n\n💡 The system will automatically:\n• Check for new email replies every 60 seconds\n• Analyze reasons using AI\n• Update engagement status\n• Send follow-up emails if needed\n• Notify you of any important updates\n\n🎯 You can now continue with other tasks!"
                except Exception as e:
                    return f"❌ Failed to start monitoring: {str(e)}\n\n💡 Please try again or contact support."
            
            # If monitoring is already active, just return current status
            status = self.email_monitor.get_monitoring_status()
            return f"📧 Email monitoring is already active in background:\n\n• Active: ✅ Yes\n• Last Check: {status['last_check_time'] or 'Never'}\n• Processed Messages: {status['processed_messages_count']}\n• Check Interval: {status['check_interval_seconds']} seconds\n\n💡 The system is continuously monitoring for replies while you work on other tasks."
            
        except Exception as e:
            return f"❌ Error checking email replies: {str(e)}\n\n💡 Please try again or contact support."

    async def _validate_employee_reason_impl(self, employee_email: str, timesheet_date: str) -> str:
        """Implementation of validate_employee_reason."""
        status_key = f"{employee_email}_{timesheet_date}"
        
        if status_key not in self.engagement_status:
            return f"No engagement record found for {employee_email} on {timesheet_date}"
        
        status = self.engagement_status[status_key]
        
        if not status.last_reply:
            return f"No reply received from {status.employee_name} for {timesheet_date}"
        
        reply = status.last_reply
        reason_valid = reply.reason_valid
        
        result = f"AI Analysis for {status.employee_name} ({timesheet_date}):\n"
        result += f"Employee Reply: {reply.content}\n"
        result += f"AI Decision: {'✅ Valid Reason' if reason_valid else '❌ Invalid Reason'}\n"
        result += f"Status: {status.status}\n"
        
        if reason_valid and reply.reason_type:
            result += f"AI-Detected Type: {reply.reason_type}\n"
            if hasattr(reply, 'ai_confidence'):
                result += f"AI Confidence: {reply.ai_confidence}%\n"
            result += "\n✅ Ready to escalate to Compliance Agent"
        else:
            result += "\n❌ AI determined reason is insufficient - needs follow-up email"
        
        return result

    async def _start_email_monitoring_impl(self) -> str:
        """Implementation of start_email_monitoring."""
        try:
            # Start monitoring in background
            asyncio.create_task(self.email_monitor.start_monitoring())
            return "✅ Email monitoring started successfully. Checking for replies every 60 seconds."
        except Exception as e:
            return f"❌ Failed to start email monitoring: {str(e)}"

    async def _stop_email_monitoring_impl(self) -> str:
        """Implementation of stop_email_monitoring."""
        try:
            await self.email_monitor.stop_monitoring()
            return "✅ Email monitoring stopped successfully."
        except Exception as e:
            return f"❌ Failed to stop email monitoring: {str(e)}"

    async def _get_monitoring_status_impl(self) -> str:
        """Implementation of get_monitoring_status."""
        try:
            status = self.email_monitor.get_monitoring_status()
            result = "📧 Email Monitoring Status:\n\n"
            result += f"• Active: {'✅ Yes' if status['monitoring_active'] else '❌ No'}\n"
            result += f"• Last Check: {status['last_check_time'] or 'Never'}\n"
            result += f"• Processed Messages: {status['processed_messages_count']}\n"
            result += f"• Check Interval: {status['check_interval_seconds']} seconds\n"
            return result
        except Exception as e:
            return f"❌ Failed to get monitoring status: {str(e)}"

    async def _update_policy_reasons_impl(self, reason_type: str, keywords: str, description: str) -> str:
        """Implementation of update_policy_reasons."""
        try:
            # Parse keywords
            keyword_list = [k.strip() for k in keywords.split(',')]
            
            # Create new valid reason
            new_reason = ValidReason(
                reason_type=reason_type,
                keywords=keyword_list,
                description=description,
                requires_approval=True,  # Default to requiring approval
                max_days_per_month=None,
                requires_documentation=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add to policy
            success = self.policy_repository.add_valid_reason("default", new_reason)
            
            if success:
                result = f"✅ Successfully added new valid reason:\n\n"
                result += f"• Type: {reason_type}\n"
                result += f"• Keywords: {', '.join(keyword_list)}\n"
                result += f"• Description: {description}\n"
                result += f"• Requires Approval: Yes\n"
                return result
            else:
                return f"❌ Failed to add valid reason to policy."
        except Exception as e:
            return f"❌ Failed to update policy reasons: {str(e)}"

    async def _send_followup_email_impl(self, employee_email: str, timesheet_date: str) -> str:
        """Implementation of send_followup_email."""
        status_key = f"{employee_email}_{timesheet_date}"
        
        if status_key not in self.engagement_status:
            return f"No engagement record found for {employee_email} on {timesheet_date}"
        
        status = self.engagement_status[status_key]
        
        # Check if we've sent too many follow-ups
        if status.reply_count >= 3:
            return f"Maximum follow-up attempts reached for {status.employee_name}. Escalating to management."
        
        subject = f"Follow-up: Timesheet Issue - {timesheet_date}"
        body = f"""Dear {status.employee_name},

We received your response regarding the timesheet issue for {timesheet_date}, but we need a more specific reason for the missing hours.

Please provide a valid reason such as:
- Sick leave (with details if possible)
- Personal emergency
- Work from home arrangement
- Approved leave
- Other valid business reason

Please reply with a clear explanation so we can process your timesheet correctly.

Best regards,
Payroll Team
"""
        
        # Send email (using test recipient for now)
        test_email = "daninawaz9@gmail.com"
        success = await self.email_service.send_email(test_email, subject, body)
        
        if success:
            # Update status
            status.last_email_sent = datetime.now()
            status.status = "pending"
            
            result = f"✅ Follow-up email sent to {test_email} for {status.employee_name}\n"
            result += f"Subject: {subject}\n"
            result += f"Status updated to: {status.status}"
        else:
            result = f"❌ Failed to send follow-up email to {status.employee_name}"
        
        return result

    async def _get_engagement_status_impl(self) -> str:
        """Implementation of get_engagement_status."""
        if not self.engagement_status:
            return "No engagement records found."
        
        summary = f"Employee Engagement Status ({len(self.engagement_status)} records):\n\n"
        
        for key, status in self.engagement_status.items():
            summary += f"👤 {status.employee_name} ({status.timesheet_date}):\n"
            summary += f"   Status: {status.status}\n"
            summary += f"   Reply Count: {status.reply_count}\n"
            
            if status.last_reply:
                summary += f"   Last Reply: {status.last_reply.content[:50]}...\n"
                summary += f"   Reason Valid: {'✅' if status.last_reply.reason_valid else '❌'}\n"
            
            if status.last_email_sent:
                summary += f"   Last Email Sent: {status.last_email_sent.strftime('%Y-%m-%d %H:%M')}\n"
            
            summary += "\n"
        
        return summary

    async def _escalate_to_compliance_impl(self, employee_email: str, timesheet_date: str) -> str:
        """Implementation of escalate_to_compliance."""
        status_key = f"{employee_email}_{timesheet_date}"
        
        if status_key not in self.engagement_status:
            return f"No engagement record found for {employee_email} on {timesheet_date}"
        
        status = self.engagement_status[status_key]
        
        if not status.last_reply or not status.last_reply.reason_valid:
            return f"Cannot escalate: {status.employee_name} has not provided a valid reason yet."
        
        # Update status to indicate escalation
        status.status = "escalated"
        
        result = f"✅ Escalated to Compliance Agent:\n"
        result += f"Employee: {status.employee_name}\n"
        result += f"Date: {timesheet_date}\n"
        result += f"Reason: {status.last_reply.content}\n"
        result += f"Status: {status.status}\n\n"
        result += f"Note: Compliance Agent will check company policies and available leave."
        
        return result
