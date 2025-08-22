"""Demo script to showcase the Payroll Agent System."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("[WARNING] OPENAI_API_KEY not set. Some features may not work.")
    print("For full functionality, please set your OpenAI API key in the .env file")
    print("You can continue with limited functionality for testing.\n")

from main import PayrollAgentSystem

async def demo():
    """Run a demo of the payroll agent system."""
    print("="*60)
    print("Payroll Agent System - Demo")
    print("="*60)
    
    # Initialize the system
    system = PayrollAgentSystem()
    print("[OK] System initialized")
    
    # Demo commands
    demo_commands = [
        "List all pending timesheets",
        "Analyze timesheets and find anomalies",
        "Show me employees with missing hours"
    ]
    
    print("\nDemo Commands:")
    for i, cmd in enumerate(demo_commands, 1):
        print(f"{i}. {cmd}")
    
    # If no API key, show what would happen
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[INFO] Running in demo mode without OpenAI API key")
        print("The system would process these commands through the AI agent.")
        print("\nTo see actual results:")
        print("1. Add your OpenAI API key to the .env file")
        print("2. Run: python demo.py")
    else:
        # Process a sample command
        print("\n[INFO] Processing sample command...")
        command = "Analyze timesheets and find anomalies"
        print(f"Command: {command}")
        
        try:
            response = await system.process_request(command)
            print(f"\nResponse: {response}")
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            print("Please ensure your OpenAI API key is valid.")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(demo())
