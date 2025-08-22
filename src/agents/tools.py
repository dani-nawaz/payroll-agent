"""Tools for the payroll agents."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from agents import function_tool

from src.repositories.csv_repository import CSVTimesheetRepository
from src.services.email_service import EmailService
from src.models.timesheet import TimesheetAnomaly, EmployeeTimesheetSummary


# Initialize services
repository = CSVTimesheetRepository()
email_service = EmailService()


@function_tool
async def analyze_timesheets(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    check_all_pending: bool = True
) -> str:
    """Analyze timesheets for anomalies and missing hours.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (default: 7 days ago)
        end_date: End date in YYYY-MM-DD format (default: today)
        check_all_pending: If True, check all pending timesheets regardless of date
        
    Returns:
        String summary of anomalies found
    """

    # Parse dates or use defaults
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime.now() - timedelta(days=7)
    
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = datetime.now()
    
    # Get timesheets to analyze
    if check_all_pending:
        timesheets = await repository.get_pending_timesheets()
    else:
        timesheets = await repository.get_timesheets_by_date_range(start, end)
    
    # Group by employee
    employee_timesheets = {}
    for ts in timesheets:
        if ts.employee_email not in employee_timesheets:
            employee_timesheets[ts.employee_email] = []
        employee_timesheets[ts.employee_email].append(ts)
    
    # Analyze each employee's timesheets
    anomalies_by_employee = {}
    
    for email, emp_timesheets in employee_timesheets.items():
        anomalies = []
        
        for ts in emp_timesheets:
            # Check for missing hours
            if ts.hours_worked < 8:
                anomalies.append(TimesheetAnomaly(
                    employee_id=ts.employee_id,
                    employee_name=ts.employee_name,
                    employee_email=ts.employee_email,
                    date=ts.date,
                    expected_hours=8.0,
                    actual_hours=ts.hours_worked,
                    anomaly_type="missing_hours",
                    description=f"Only {ts.hours_worked} hours logged, expected at least 8 hours",
                    severity="high" if ts.hours_worked < 4 else "medium"
                ))
            
            # Check for excessive hours
            elif ts.hours_worked > 12:
                anomalies.append(TimesheetAnomaly(
                    employee_id=ts.employee_id,
                    employee_name=ts.employee_name,
                    employee_email=ts.employee_email,
                    date=ts.date,
                    expected_hours=8.0,
                    actual_hours=ts.hours_worked,
                    anomaly_type="excessive_hours",
                    description=f"{ts.hours_worked} hours logged, which exceeds normal working hours",
                    severity="medium"
                ))
        
        if anomalies:
            anomalies_by_employee[email] = anomalies
    
    # Format results as string for the agent
    result = f"Found anomalies for {len(anomalies_by_employee)} employees:\n\n"
    for email, anomalies in anomalies_by_employee.items():
        result += f"{email}:\n"
        for anomaly in anomalies:
            result += f"  - {anomaly.date.strftime('%Y-%m-%d')}: {anomaly.description}\n"
        result += "\n"
    
    if not anomalies_by_employee:
        result = "No anomalies found in the timesheet data."
    
    return result


@function_tool
async def send_anomaly_emails() -> str:
    """Send email notifications to employees with timesheet anomalies.
    
    Returns:
        String summary of email sending results
    """

    # First analyze timesheets to get anomalies
    analysis_result = await analyze_timesheets()
    
    # For now, just return a summary
    summary = f"Email notification system ready.\n"
    summary += f"Analysis result: {analysis_result[:200]}...\n"
    summary += f"Note: Email sending is configured but requires valid credentials."
    
    return summary


@function_tool
async def get_employee_summary(
    employee_id: str,
    start_date: str,
    end_date: str
) -> str:
    """Get a summary of an employee's timesheets for a period.
    
    Args:
        employee_id: Employee ID
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Employee timesheet summary or None if not found
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    summary = await repository.get_employee_summary(employee_id, start, end)
    
    if summary:
        result = f"Employee: {summary.employee_name}\n"
        result += f"Period: {start_date} to {end_date}\n"
        result += f"Total Hours: {summary.total_hours:.1f}\n"
        result += f"Average Hours/Day: {summary.average_hours_per_day:.1f}\n"
        result += f"Anomalies Found: {len(summary.anomalies)}"
        return result
    else:
        return f"No timesheet data found for employee {employee_id}"


@function_tool
async def list_pending_timesheets() -> str:
    """List all pending timesheets that need review.
    
    Returns:
        List of pending timesheet entries
    """
    timesheets = await repository.get_pending_timesheets()
    
    # Convert to dict for easier display
    result = []
    for ts in timesheets:
        result.append({
            "employee": ts.employee_name,
            "email": ts.employee_email,
            "date": ts.date.strftime("%Y-%m-%d"),
            "hours": ts.hours_worked,
            "project": ts.project or "N/A",
            "status": ts.status
        })
    
    # Format results as string
    if result:
        output = f"Found {len(result)} pending timesheets:\n\n"
        for ts in result[:10]:  # Show first 10
            output += f"- {ts['employee']} ({ts['date']}): {ts['hours']} hours - {ts['project']}\n"
        if len(result) > 10:
            output += f"\n... and {len(result) - 10} more"
    else:
        output = "No pending timesheets found."
    
    return output


@function_tool
async def update_timesheet_status(
    employee_id: str,
    date: str,
    new_status: str
) -> bool:
    """Update the status of a timesheet entry.
    
    Args:
        employee_id: Employee ID
        date: Date in YYYY-MM-DD format
        new_status: New status (approved, rejected, pending)
        
    Returns:
        True if update was successful
    """
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    success = await repository.update_timesheet_status(
        employee_id, date_obj, new_status
    )
    
    if success:
        print(f"[OK] Updated timesheet status for employee {employee_id} on {date} to {new_status}")
    else:
        print(f"[ERROR] Failed to update timesheet status")
    
    return f"Timesheet status update {'successful' if success else 'failed'} for employee {employee_id} on {date}"


@function_tool
async def send_pending_notifications() -> str:
    """Send email notifications to all employees with pending timesheets.
    
    Returns:
        String summary of the email sending results
    """
    # Get all pending timesheets
    timesheets = await repository.get_pending_timesheets()
    
    if not timesheets:
        return "No pending timesheets found. No emails to send."
    
    # Group by employee
    employee_timesheets = {}
    for ts in timesheets:
        if ts.employee_email not in employee_timesheets:
            employee_timesheets[ts.employee_email] = []
        employee_timesheets[ts.employee_email].append(ts)
    
    # Send notifications to each employee
    results = {}
    total_sent = 0
    total_failed = 0
    
    for email, emp_timesheets in employee_timesheets.items():
        employee_name = emp_timesheets[0].employee_name
        
        # For testing, send to the specified email
        test_email = "daninawaz9@gmail.com"
        
        # Create a simple notification about pending timesheets
        subject = "Action Required: Pending Timesheets"
        body = f"""Dear {employee_name},

You have {len(emp_timesheets)} pending timesheet entries that require your attention:

"""
        
        for ts in emp_timesheets:
            body += f"• {ts.date.strftime('%Y-%m-%d')}: {ts.hours_worked} hours - {ts.project or 'No project specified'}\n"
        
        body += """

Please review and update these timesheet entries as soon as possible.

Best regards,
Payroll Team
"""
        
        try:
            success = await email_service.send_email(test_email, subject, body)
            results[email] = success
            
            if success:
                total_sent += 1
                print(f"[OK] Email sent to {test_email} for {employee_name} ({len(emp_timesheets)} pending timesheets)")
            else:
                total_failed += 1
                print(f"[ERROR] Failed to send email to {test_email} for {employee_name}")
        except Exception as e:
            total_failed += 1
            results[email] = False
            print(f"[ERROR] Exception sending email to {test_email} for {employee_name}: {str(e)}")
    
    # Return summary
    summary = f"Email notification results:\n"
    summary += f"• Total employees with pending timesheets: {len(employee_timesheets)}\n"
    summary += f"• Emails sent successfully: {total_sent}\n"
    summary += f"• Emails failed: {total_failed}\n"
    summary += f"• Test recipient: daninawaz9@gmail.com\n"
    
    if total_sent > 0:
        summary += f"\n[OK] Successfully sent {total_sent} email notifications to daninawaz9@gmail.com"
    else:
        summary += f"\n[ERROR] No emails were sent successfully"
    
    return summary
