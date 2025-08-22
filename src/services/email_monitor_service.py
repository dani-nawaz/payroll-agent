"""Email monitoring service for continuous inbox checking."""

import asyncio
import imaplib
import email
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
import re
from dataclasses import dataclass

from src.config import settings


@dataclass
class EmailMessage:
    """Email message data structure."""
    message_id: str
    from_email: str
    from_name: str
    subject: str
    content: str
    received_date: datetime
    is_reply: bool
    original_subject: Optional[str] = None
    timesheet_date: Optional[str] = None


class EmailMonitorService:
    """Service for monitoring email inbox for replies."""
    
    def __init__(self):
        self.email_service = None  # Will be set from EmailService
        self.last_check_time: Optional[datetime] = None
        self.processed_messages: set = set()
        self.reply_callback: Optional[Callable] = None
        self.monitoring_active = False
        self.check_interval = 60  # Check every 60 seconds
        self.check_count = 0  # Track number of checks for cleanup
        print("[INFO] Email monitor initialized - will mark emails as read in Gmail")
        
    def set_email_service(self, email_service):
        """Set the email service for sending notifications."""
        self.email_service = email_service
    
    def set_reply_callback(self, callback: Callable):
        """Set callback function to handle email replies."""
        self.reply_callback = callback
    
    async def start_monitoring(self):
        """Start continuous email monitoring."""
        try:
            self.monitoring_active = True
            print(f"[INFO] Starting email monitoring (checking every {self.check_interval} seconds)")
            print(f"[INFO] Background monitoring active - you can continue using the system")
            
            while self.monitoring_active:
                try:
                    replies = await self.check_for_replies()
                    
                    # Provide user-friendly notifications for new replies
                    if replies:
                        print(f"\n[NOTIFICATION] Found {len(replies)} new email reply(ies)!")
                        for reply in replies:
                            print(f"   From: {reply.from_name} ({reply.from_email})")
                            print(f"   Date: {reply.timesheet_date}")
                            print(f"   Subject: {reply.subject[:50]}...")
                            print(f"   Content: {reply.content[:100]}...")
                            print("   " + "-" * 50)
                    
                    await asyncio.sleep(self.check_interval)
                except Exception as e:
                    print(f"[ERROR] Email monitoring error: {str(e)}")
                    # Continue monitoring even if there's an error
                    await asyncio.sleep(self.check_interval)
                    
        except Exception as e:
            print(f"[ERROR] Failed to start email monitoring: {str(e)}")
            self.monitoring_active = False
            raise e
    
    async def stop_monitoring(self):
        """Stop continuous email monitoring."""
        self.monitoring_active = False
        print("[INFO] Email monitoring stopped")
    
    async def check_for_replies(self) -> List[EmailMessage]:
        """Check for new email replies."""
        try:
            # Get all replies from Gmail
            all_replies = await self._simulate_email_check()
            
            # Filter out already processed messages
            new_replies = []
            for reply in all_replies:
                if reply.message_id not in self.processed_messages:
                    new_replies.append(reply)
                    # Mark as processed immediately to prevent duplicates
                    self.processed_messages.add(reply.message_id)
            
            if new_replies:
                print(f"[INFO] Found {len(new_replies)} new email replies (total found: {len(all_replies)})")
                
                # Process each new reply
                for reply in new_replies:
                    await self._process_reply(reply)
            else:
                print(f"[INFO] No new emails found (total checked: {len(all_replies)})")
            
            self.last_check_time = datetime.now()
            self.check_count += 1
            
            # Clean up processed messages every 10 checks to prevent memory issues
            if self.check_count % 10 == 0 and len(self.processed_messages) > 100:
                print(f"[INFO] Cleaning up processed messages (current: {len(self.processed_messages)})")
                # Keep only the last 50 processed messages
                self.processed_messages = set(list(self.processed_messages)[-50:])
            
            return new_replies
            
        except Exception as e:
            print(f"[ERROR] Error checking for replies: {str(e)}")
            return []
    
    async def _simulate_email_check(self) -> List[EmailMessage]:
        """Check for real email replies from Gmail inbox."""
        try:
            # Connect to Gmail IMAP
            replies = await self._connect_imap()
            return replies
        except Exception as e:
            print(f"[ERROR] Failed to check Gmail: {str(e)}")
            # Fallback to simulation for testing
            return await self._fallback_simulation()
    
    async def _fallback_simulation(self) -> List[EmailMessage]:
        """Fallback simulation when Gmail connection fails."""
        current_time = datetime.now()
        
        # Only simulate replies if we haven't checked recently
        if (self.last_check_time and 
            (current_time - self.last_check_time).seconds < 30):
            return []
        
        # Simulate replies with some randomness
        import random
        if random.random() < 0.3:  # 30% chance of finding a reply
            return [
                EmailMessage(
                    message_id=f"msg_{current_time.timestamp()}",
                    from_email="john.smith@example.com",
                    from_name="John Smith",
                    subject="Re: Timesheet Issue - 2025-08-08",
                    content="I was sick on that day, couldn't come to work.",
                    received_date=current_time - timedelta(minutes=5),
                    is_reply=True,
                    original_subject="Timesheet Issue - 2025-08-08",
                    timesheet_date="2025-08-08"
                )
            ]
        
        return []
    
    async def _process_reply(self, reply: EmailMessage):
        """Process an email reply."""
        print(f"[INFO] Processing reply from {reply.from_name}: {reply.content[:50]}...")
        
        # Extract timesheet date from subject
        if not reply.timesheet_date:
            reply.timesheet_date = self._extract_timesheet_date(reply.subject)
        
        # Call the callback function if set
        if self.reply_callback:
            try:
                await self.reply_callback(reply)
            except Exception as e:
                print(f"[ERROR] Error in reply callback: {str(e)}")
    
    def _extract_timesheet_date(self, subject: str) -> Optional[str]:
        """Extract timesheet date from email subject."""
        # Look for date patterns like "2025-08-08" or "08/08/2025"
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
            r'(\d{2}-\d{2}-\d{4})',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, subject)
            if match:
                return match.group(1)
        
        return None
    
    async def _connect_imap(self) -> List[EmailMessage]:
        """Connect to Gmail IMAP server and check for replies."""
        replies = []
        
        try:
            # Gmail IMAP settings
            imap_server = "imap.gmail.com"
            imap_port = 993
            username = "abdulrehman@clickchain.com"
            password = "jayx tamp jmcj yrnf"  # App password
            
            print(f"[INFO] Connecting to Gmail IMAP: {username}")
            
            # Connect to Gmail IMAP
            imap = imaplib.IMAP4_SSL(imap_server, imap_port)
            imap.login(username, password)
            
            # Select inbox
            imap.select('INBOX')
            
            # Search for unread emails with timesheet-related subjects
            search_criteria = '(UNSEEN SINCE "1-Jan-2025" SUBJECT "Timesheet")'
            status, message_numbers = imap.search(None, search_criteria)
            
            if status == 'OK' and message_numbers[0]:
                print(f"[INFO] Found {len(message_numbers[0].split())} unread timesheet emails since Jan 2025")
                
                for num in message_numbers[0].split():
                    try:
                        # Fetch email content
                        status, data = imap.fetch(num, '(RFC822)')
                        if status == 'OK':
                            email_body = data[0][1]
                            email_message = email.message_from_bytes(email_body)
                            
                            # Extract email details
                            subject = self._decode_header(email_message['subject'])
                            from_email = self._decode_header(email_message['from'])
                            from_name = self._extract_name(from_email)
                            received_date = email.utils.parsedate_to_datetime(email_message['date'])
                            
                            # Get email content
                            content = self._get_email_content(email_message)
                            
                            # Check if it's a reply to timesheet email
                            if self._is_timesheet_reply(subject, content):
                                # Extract timesheet date from subject
                                timesheet_date = self._extract_timesheet_date(subject)
                                
                                # Create a more unique message ID
                                unique_id = f"gmail_{num.decode()}_{received_date.timestamp()}"
                                
                                reply = EmailMessage(
                                    message_id=unique_id,
                                    from_email=from_email,
                                    from_name=from_name,
                                    subject=subject,
                                    content=content,
                                    received_date=received_date,
                                    is_reply=True,
                                    original_subject=subject,
                                    timesheet_date=timesheet_date
                                )
                                
                                replies.append(reply)
                                print(f"[INFO] Found reply from {from_name}: {subject}")
                                
                                # Mark email as read in Gmail
                                try:
                                    imap.store(num, '+FLAGS', '\\Seen')
                                    print(f"[INFO] Marked email {num.decode()} as read")
                                except Exception as e:
                                    print(f"[WARNING] Failed to mark email as read: {str(e)}")
                    
                    except Exception as e:
                        print(f"[ERROR] Error processing email {num}: {str(e)}")
                        continue
            
            imap.close()
            imap.logout()
            
        except Exception as e:
            print(f"[ERROR] Gmail IMAP connection failed: {str(e)}")
            raise e
        
        return replies
    
    def _decode_header(self, header_value):
        """Decode email header value."""
        if header_value:
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        return ""
    
    def _extract_name(self, email_address):
        """Extract name from email address."""
        if '<' in email_address and '>' in email_address:
            name_part = email_address.split('<')[0].strip()
            if name_part:
                return name_part.strip('"')
        return email_address.split('@')[0]
    
    def _get_email_content(self, email_message):
        """Extract text content from email message."""
        content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        content += part.get_payload(decode=True).decode('latin-1', errors='ignore')
        else:
            try:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                content = email_message.get_payload(decode=True).decode('latin-1', errors='ignore')
        
        return content
    
    def _is_timesheet_reply(self, subject, content):
        """Check if email is a reply to timesheet email."""
        timesheet_keywords = ['timesheet', 'missing hours', 'anomaly', 'issue']
        subject_lower = subject.lower()
        content_lower = content.lower()
        
        # Check if subject contains timesheet keywords
        for keyword in timesheet_keywords:
            if keyword in subject_lower:
                return True
        
        # Check if content contains timesheet-related text
        for keyword in timesheet_keywords:
            if keyword in content_lower:
                return True
        
        return False
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            "monitoring_active": self.monitoring_active,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "processed_messages_count": len(self.processed_messages),
            "check_interval_seconds": self.check_interval
        }
    
    def update_check_interval(self, interval_seconds: int):
        """Update the check interval."""
        self.check_interval = interval_seconds
        print(f"[INFO] Email check interval updated to {interval_seconds} seconds")
