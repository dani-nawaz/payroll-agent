"""Demo script showing the complete workflow with email notifications."""

import asyncio
from src.agents.tools import analyze_timesheets, send_anomaly_emails
from src.repositories.csv_repository import CSVTimesheetRepository
from src.services.email_service import EmailService


async def demo_full_workflow():
    """Demonstrate the complete workflow from analysis to notification."""
    print("="*60)
    print("Payroll Agent System - Full Workflow Demo")
    print("="*60)
    
    # Step 1: Analyze timesheets
    print("\n[STEP 1] Analyzing timesheets for anomalies...")
    print("-"*40)
    
    # Get the raw anomalies data (not just the string)
    repository = CSVTimesheetRepository()
    anomalies_by_employee = {}
    
    # Analyze timesheets
    timesheets = await repository.get_pending_timesheets()
    print(f"Found {len(timesheets)} pending timesheets to analyze")
    
    # Group by employee and find anomalies
    from src.models.timesheet import TimesheetAnomaly
    
    employee_timesheets = {}
    for ts in timesheets:
        if ts.employee_email not in employee_timesheets:
            employee_timesheets[ts.employee_email] = []
        employee_timesheets[ts.employee_email].append(ts)
    
    for email, emp_timesheets in employee_timesheets.items():
        anomalies = []
        for ts in emp_timesheets:
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
        
        if anomalies:
            anomalies_by_employee[email] = anomalies
    
    print(f"\nFound anomalies for {len(anomalies_by_employee)} employees:")
    for email in anomalies_by_employee:
        print(f"  - {email}: {len(anomalies_by_employee[email])} anomalies")
    
    # Step 2: Prepare email notifications
    print("\n[STEP 2] Preparing email notifications...")
    print("-"*40)
    
    email_service = EmailService()
    print(f"Email service configured:")
    print(f"  From: {email_service.from_email}")
    print(f"  SMTP: {email_service.config.smtp_server}:{email_service.config.smtp_port}")
    
    # Step 3: Send notifications (simulated)
    print("\n[STEP 3] Sending notifications (simulated)...")
    print("-"*40)
    
    for email, anomalies in anomalies_by_employee.items():
        employee_name = anomalies[0].employee_name
        print(f"\n📧 Would send email to: {employee_name} ({email})")
        print(f"   Subject: Action Required: Timesheet Anomalies Detected")
        print(f"   Anomalies to report:")
        for anomaly in anomalies[:3]:  # Show first 3
            print(f"     - {anomaly.date.strftime('%Y-%m-%d')}: {anomaly.description}")
        if len(anomalies) > 3:
            print(f"     ... and {len(anomalies) - 3} more")
    
    # Step 4: Summary
    print("\n[STEP 4] Workflow Summary")
    print("-"*40)
    print(f"✅ Analyzed: {len(timesheets)} timesheets")
    print(f"✅ Found: {sum(len(a) for a in anomalies_by_employee.values())} total anomalies")
    print(f"✅ Would notify: {len(anomalies_by_employee)} employees")
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nTo actually send emails:")
    print("1. Ensure valid Gmail credentials in .env")
    print("2. Uncomment the actual email sending code")
    print("3. Run the workflow again")


if __name__ == "__main__":
    asyncio.run(demo_full_workflow())
