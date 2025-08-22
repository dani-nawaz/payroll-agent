#!/usr/bin/env python3
"""Send test email to trigger monitoring."""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.email_service import EmailService


async def send_test_email():
    """Send a test email to trigger monitoring."""
    print("📧 Sending Test Email")
    print("=" * 40)
    
    try:
        # Create email service
        email_service = EmailService()
        
        # Test email details
        to_email = "abdulrehman@clickchain.com"
        subject = "Re: Timesheet Issue - 2025-08-22"
        body = """
Dear Payroll Team,

I was sick with the flu on 2025-08-22 and couldn't come to work. 
I had a fever and was bedridden for the entire day.

Please let me know if you need any additional information.

Best regards,
John Smith
        """
        
        print(f"📤 Sending test email to: {to_email}")
        print(f"📝 Subject: {subject}")
        print(f"📄 Content: {body[:100]}...")
        
        # Send email
        success = await email_service.send_email(to_email, subject, body)
        
        if success:
            print("✅ Test email sent successfully!")
            print("💡 The background monitor should detect this email in the next 60 seconds")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")


if __name__ == "__main__":
    asyncio.run(send_test_email())
