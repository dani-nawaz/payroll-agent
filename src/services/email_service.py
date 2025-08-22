"""Email service for sending notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from datetime import datetime
import asyncio

from src.config import settings
from src.models.timesheet import TimesheetAnomaly, EmployeeTimesheetSummary


class EmailService:
    """Service for sending emails to employees."""
    
    def __init__(self):
        """Initialize email service with configuration."""
        self.config = settings.email
        self.from_email = self.config.username
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send an email to a recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email_sync, msg, to_email)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _send_email_sync(self, msg: MIMEMultipart, to_email: str):
        """Synchronous email sending (to be run in executor)."""
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.username, self.config.password)
            server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
    
    async def send_anomaly_notification(
        self,
        employee_email: str,
        employee_name: str,
        anomalies: List[TimesheetAnomaly]
    ) -> bool:
        """Send notification about timesheet anomalies to an employee.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's name
            anomalies: List of detected anomalies
            
        Returns:
            True if email was sent successfully
        """
        subject = "Action Required: Timesheet Anomalies Detected"
        
        # Build plain text body
        body = f"""Dear {employee_name},

We have detected the following issues with your timesheet submissions:

"""
        for anomaly in anomalies:
            body += f"• {anomaly.date.strftime('%Y-%m-%d')}: {anomaly.description}\n"
        
        body += """
Please review and update your timesheet entries or provide an explanation for these discrepancies.

If you have any questions or need assistance, please reply to this email with your explanation.

Best regards,
Payroll Team
"""
        
        # Build HTML body for better formatting
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Timesheet Anomalies Detected</h2>
                <p>Dear {employee_name},</p>
                <p>We have detected the following issues with your timesheet submissions:</p>
                <ul>
        """
        
        for anomaly in anomalies:
            severity_color = {
                'high': '#ff0000',
                'medium': '#ff9900',
                'low': '#ffcc00'
            }.get(anomaly.severity, '#000000')
            
            html_body += f"""
                    <li>
                        <strong>{anomaly.date.strftime('%Y-%m-%d')}</strong>: 
                        {anomaly.description}
                        <span style="color: {severity_color};">
                            (Severity: {anomaly.severity})
                        </span>
                    </li>
            """
        
        html_body += """
                </ul>
                <p>Please review and update your timesheet entries or provide an explanation for these discrepancies.</p>
                <p>If you have any questions or need assistance, please reply to this email with your explanation.</p>
                <br>
                <p>Best regards,<br>Payroll Team</p>
            </body>
        </html>
        """
        
        return await self.send_email(employee_email, subject, body, html_body)
    
    async def send_summary_report(
        self,
        recipient_email: str,
        summaries: List[EmployeeTimesheetSummary]
    ) -> bool:
        """Send a summary report of timesheet anomalies.
        
        Args:
            recipient_email: Email address to send the report to
            summaries: List of employee timesheet summaries
            
        Returns:
            True if email was sent successfully
        """
        subject = f"Timesheet Anomaly Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        total_anomalies = sum(len(s.anomalies) for s in summaries)
        
        body = f"""Timesheet Anomaly Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Summary:
- Total Employees Reviewed: {len(summaries)}
- Total Anomalies Found: {total_anomalies}

Details by Employee:
"""
        
        for summary in summaries:
            if summary.anomalies:
                body += f"\n{summary.employee_name} ({summary.employee_email}):\n"
                body += f"  Period: {summary.period_start.strftime('%Y-%m-%d')} to {summary.period_end.strftime('%Y-%m-%d')}\n"
                body += f"  Total Hours: {summary.total_hours:.1f}\n"
                body += f"  Average Hours/Day: {summary.average_hours_per_day:.1f}\n"
                body += f"  Anomalies: {len(summary.anomalies)}\n"
        
        return await self.send_email(recipient_email, subject, body)
    
    async def send_batch_notifications(
        self,
        notifications: Dict[str, List[TimesheetAnomaly]]
    ) -> Dict[str, bool]:
        """Send batch notifications to multiple employees.
        
        Args:
            notifications: Dictionary mapping employee email to their anomalies
            
        Returns:
            Dictionary mapping employee email to success status
        """
        results = {}
        
        # Send emails concurrently
        tasks = []
        for email, anomalies in notifications.items():
            if anomalies:
                # Extract employee name from first anomaly
                employee_name = anomalies[0].employee_name
                task = self.send_anomaly_notification(email, employee_name, anomalies)
                tasks.append((email, task))
        
        # Wait for all emails to be sent
        for email, task in tasks:
            results[email] = await task
        
        return results
