"""Example usage of the Payroll Agent System."""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure we have sample data
print("Setting up sample data...")
import subprocess
subprocess.run(["python", "data/generate_sample_data.py"])

from main import PayrollAgentSystem


async def example_basic_analysis():
    """Example: Basic timesheet analysis."""
    print("\n" + "="*60)
    print("Example 1: Basic Timesheet Analysis")
    print("="*60)
    
    system = PayrollAgentSystem()
    
    # Analyze timesheets
    response = await system.process_request(
        "Analyze all pending timesheets and find anomalies"
    )
    print(response)


async def example_send_notifications():
    """Example: Find anomalies and send notifications."""
    print("\n" + "="*60)
    print("Example 2: Find Anomalies and Send Notifications")
    print("="*60)
    
    system = PayrollAgentSystem()
    
    # Find and notify
    response = await system.process_request(
        "Find all timesheet anomalies and send email notifications to employees"
    )
    print(response)


async def example_specific_employee():
    """Example: Analyze specific employee."""
    print("\n" + "="*60)
    print("Example 3: Specific Employee Analysis")
    print("="*60)
    
    system = PayrollAgentSystem()
    
    # Get employee summary
    response = await system.process_request(
        "Get timesheet summary for employee EMP001 for the last 2 weeks"
    )
    print(response)


async def example_date_range():
    """Example: Analyze specific date range."""
    print("\n" + "="*60)
    print("Example 4: Date Range Analysis")
    print("="*60)
    
    system = PayrollAgentSystem()
    
    # Analyze last week
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    response = await system.process_request(
        f"Analyze timesheets from {last_week} to {today} and report anomalies"
    )
    print(response)


async def example_workflow():
    """Example: Complete workflow."""
    print("\n" + "="*60)
    print("Example 5: Complete Workflow")
    print("="*60)
    
    system = PayrollAgentSystem()
    
    # Step 1: List pending
    print("\nStep 1: Checking pending timesheets...")
    response = await system.process_request("List all pending timesheets")
    print(response)
    
    # Step 2: Analyze
    print("\nStep 2: Analyzing for anomalies...")
    response = await system.process_request(
        "Analyze timesheets and identify all employees with missing hours"
    )
    print(response)
    
    # Step 3: Notify
    print("\nStep 3: Sending notifications...")
    response = await system.process_request(
        "Send email notifications to employees with timesheet issues"
    )
    print(response)


async def main():
    """Run all examples."""
    print("="*60)
    print("Payroll Agent System - Examples")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set!")
        print("The examples will show the structure but may not fully execute.")
        print("Please set your OpenAI API key in the .env file for full functionality.\n")
        return
    
    try:
        # Run examples
        await example_basic_analysis()
        
        # Uncomment to run additional examples:
        # await example_send_notifications()
        # await example_specific_employee()
        # await example_date_range()
        # await example_workflow()
        
        print("\n" + "="*60)
        print("✓ Examples completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("Please ensure you have set up your OpenAI API key in the .env file")


if __name__ == "__main__":
    asyncio.run(main())
