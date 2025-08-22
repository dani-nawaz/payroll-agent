"""Simplified agent implementation for the payroll system."""

from agents import Agent
from src.config import settings
from src.agents.tools import (
    analyze_timesheets,
    list_pending_timesheets,
    send_pending_notifications
)


def create_payroll_agent() -> Agent:
    """Create a simplified payroll agent that handles requests directly."""
    
    instructions = """You are the Payroll Assistant Agent.
    
    Your responsibilities:
    1. Help users analyze timesheets and find anomalies
    2. Identify employees with missing or excessive hours
    3. Generate reports about timesheet issues
    4. Assist with timesheet management tasks
    5. Send email notifications to employees with pending timesheets
    
    Available tools:
    - analyze_timesheets(): Analyze timesheets for anomalies and missing hours
    - list_pending_timesheets(): List all pending timesheets that need review
    - send_pending_notifications(): Send email notifications to all employees with pending timesheets
    
    When users ask you to:
    - "analyze" or "find anomalies": Use analyze_timesheets() to find timesheet issues
    - "list pending": Use list_pending_timesheets() to show pending timesheets
    - "send email" or "send notifications": Use send_pending_notifications() to notify employees
    
    Always use the appropriate tools to perform actions. Be helpful and provide clear, structured responses about timesheet data.
    
    Sample data context:
    - The system has 5 employees: John Smith, Jane Doe, Bob Johnson, Alice Williams, Charlie Brown
    - Common issues include: missing hours (<8 hours/day), excessive hours (>12 hours/day)
    - Email notifications are sent to daninawaz9@gmail.com for testing
    """
    
    tools = [
        analyze_timesheets,
        list_pending_timesheets,
        send_pending_notifications
    ]
    
    return Agent(
        name="Payroll Assistant",
        instructions=instructions,
        model=settings.openai.model,
        tools=tools
    )
