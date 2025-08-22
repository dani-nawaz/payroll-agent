"""Test script to demonstrate the payroll agent system."""

import asyncio
import os
from datetime import datetime

# Set a test OpenAI API key if not present (for demonstration)
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Note: OPENAI_API_KEY not set. Some features may not work.")
    print("For full functionality, please set your OpenAI API key in the .env file")

from src.repositories.csv_repository import CSVTimesheetRepository
from src.services.email_service import EmailService
from src.models.timesheet import TimesheetEntry


async def test_repository():
    """Test the repository functions."""
    print("\n" + "="*60)
    print("Testing Repository Functions")
    print("="*60)
    
    repo = CSVTimesheetRepository()
    
    # Test getting pending timesheets
    print("\n1. Getting pending timesheets...")
    pending = await repo.get_pending_timesheets()
    print(f"   Found {len(pending)} pending timesheets")
    
    if pending:
        # Show first few entries
        for ts in pending[:3]:
            print(f"   - {ts.employee_name}: {ts.date.strftime('%Y-%m-%d')} - {ts.hours_worked} hours")
    
    # Test getting employee summary
    print("\n2. Getting employee summary...")
    if pending:
        employee_id = pending[0].employee_id
        summary = await repo.get_employee_summary(
            employee_id,
            datetime(2024, 1, 1),
            datetime.now()
        )
        
        if summary:
            print(f"   Employee: {summary.employee_name}")
            print(f"   Total Hours: {summary.total_hours:.1f}")
            print(f"   Anomalies: {len(summary.anomalies)}")


async def test_anomaly_detection():
    """Test anomaly detection."""
    print("\n" + "="*60)
    print("Testing Anomaly Detection")
    print("="*60)
    
    from src.agents.tools import analyze_timesheets
    
    print("\nAnalyzing timesheets for anomalies...")
    anomalies = await analyze_timesheets()
    
    print(f"Found anomalies for {len(anomalies)} employees:")
    for email, employee_anomalies in anomalies.items():
        print(f"\n  {email}:")
        for anomaly in employee_anomalies[:2]:  # Show first 2 anomalies
            print(f"    - {anomaly.date.strftime('%Y-%m-%d')}: {anomaly.description}")


async def test_email_service():
    """Test email service (without actually sending)."""
    print("\n" + "="*60)
    print("Testing Email Service")
    print("="*60)
    
    email_service = EmailService()
    
    print("\n[OK] Email service initialized")
    print(f"  From: {email_service.from_email}")
    print(f"  SMTP: {email_service.config.smtp_server}:{email_service.config.smtp_port}")
    
    print("\n[WARNING] Note: Actual email sending is disabled in test mode")
    print("  To enable emails, run the main application with valid credentials")


async def test_data_generation():
    """Test data generation."""
    print("\n" + "="*60)
    print("Testing Data Generation")
    print("="*60)
    
    import subprocess
    import sys
    
    print("\nGenerating sample timesheet data...")
    result = subprocess.run(
        [sys.executable, "data/generate_sample_data.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("[OK] Sample data generated successfully")
        print(result.stdout)
    else:
        print("[ERROR] Failed to generate sample data")
        print(result.stderr)


async def main():
    """Run all tests."""
    print("="*60)
    print("Payroll Agent System - Test Suite")
    print("="*60)
    
    try:
        # Generate sample data first
        await test_data_generation()
        
        # Test repository
        await test_repository()
        
        # Test anomaly detection
        await test_anomaly_detection()
        
        # Test email service
        await test_email_service()
        
        print("\n" + "="*60)
        print("[OK] All tests completed successfully!")
        print("="*60)
        print("\nTo run the full system:")
        print("  python run.py")
        print("\nOr with a specific command:")
        print("  python run.py \"analyze timesheets and send notifications\"")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
