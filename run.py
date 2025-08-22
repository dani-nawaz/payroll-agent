"""Simple runner script for the payroll agent system."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
    print("Please set it in your .env file or environment")
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        print("Continuing without API key (some features may not work)")

# Import after environment is set up
from main import main

if __name__ == "__main__":
    print("Starting Payroll Agent System...")
    asyncio.run(main())
