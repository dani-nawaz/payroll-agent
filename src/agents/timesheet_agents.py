"""Timesheet processing agents using OpenAI Agents SDK."""

from agents import Agent
from typing import Optional

from src.agents.tools import (
    analyze_timesheets,
    send_anomaly_emails,
    get_employee_summary,
    list_pending_timesheets,
    update_timesheet_status
)
from src.config import settings


def create_orchestrator_agent() -> Agent:
    """Create the main orchestrator agent that handles initial requests."""
    
    instructions = """You are the Orchestrator Agent for the payroll system.
    
    Your responsibilities:
    1. Understand what the user wants to do
    2. Analyze timesheets to find anomalies and missing hours
    3. Send email notifications to employees about issues
    4. Provide summaries and reports of findings
    
    Process:
    1. First, analyze timesheets to find anomalies
    2. If anomalies are found, send email notifications to affected employees
    3. Report back on what was found and who was notified
    
    Always provide clear summaries of:
    - How many timesheets were analyzed
    - How many anomalies were found
    - Which employees were notified
    """
    
    # For now, the orchestrator will handle everything directly
    # We can add handoffs later when the SDK documentation is clearer
    tools = [
        analyze_timesheets,
        send_anomaly_emails,
        get_employee_summary,
        list_pending_timesheets,
        update_timesheet_status
    ]
    
    return Agent(
        name="Orchestrator",
        instructions=instructions,
        model=settings.openai.model,
        tools=tools
    )


def create_timesheet_analyzer_agent() -> Agent:
    """Create the timesheet analyzer agent that processes timesheets."""
    
    instructions = """You are the Timesheet Analyzer Agent.
    
    Your responsibilities:
    1. Analyze timesheets for anomalies and missing hours
    2. Identify employees with incomplete or incorrect timesheet entries
    3. Send email notifications to employees about issues
    4. Provide summaries and reports of findings
    
    Process:
    1. First, analyze timesheets to find anomalies
    2. If anomalies are found, send email notifications to affected employees
    3. Report back on what was found and who was notified
    
    Always provide clear summaries of:
    - How many timesheets were analyzed
    - How many anomalies were found
    - Which employees were notified
    """
    
    tools = [
        analyze_timesheets,
        send_anomaly_emails,
        get_employee_summary,
        list_pending_timesheets,
        update_timesheet_status
    ]
    
    return Agent(
        name="Timesheet Analyzer",
        instructions=instructions,
        model=settings.openai.model,
        tools=tools
    )


def create_employee_engagement_agent() -> Agent:
    """Create the employee engagement agent (placeholder for future implementation)."""
    
    instructions = """You are the Employee Engagement Agent.
    
    Your responsibilities:
    1. Monitor employee email responses
    2. Follow up with employees who haven't responded
    3. Collect explanations and justifications
    4. Hand off to Compliance Agent when sufficient information is gathered
    
    Note: This agent is a placeholder for future implementation when email monitoring is set up.
    """
    
    return Agent(
        name="Employee Engagement",
        instructions=instructions,
        model=settings.openai.model
    )


def create_compliance_agent() -> Agent:
    """Create the compliance agent (placeholder for future implementation)."""
    
    instructions = """You are the Compliance Agent.
    
    Your responsibilities:
    1. Review employee explanations against company policies
    2. Check leave balances and entitlements
    3. Approve or reject timesheet adjustments
    4. Send final decisions to employees
    
    Note: This agent is a placeholder for future implementation when policy rules are configured.
    """
    
    return Agent(
        name="Compliance",
        instructions=instructions,
        model=settings.openai.model
    )
