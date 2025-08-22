"""Main application for the Payroll Agent System using agentic approach."""

import asyncio
import sys
from typing import Optional
from agents import Runner

from src.agents.simple_agent import create_payroll_agent
from src.config import settings


class PayrollAgentSystem:
    """Main application class for the payroll agent system using agentic approach."""
    
    def __init__(self):
        """Initialize the payroll agent system."""
        self.agent = create_payroll_agent()
        self.runner = Runner()
    
    async def process_request(self, user_input: str) -> str:
        """Process a user request through the agent system using agentic loop.
        
        Args:
            user_input: The user's request or query
            
        Returns:
            The agent's response
        """
        try:
            # Use the agentic approach - let the agent decide which tools to use
            result = await self.runner.run(
                self.agent,
                user_input
            )
            
            # Return the final output
            return result.final_output if result.final_output else "Task completed successfully."
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    async def interactive_mode(self):
        """Run the system in interactive mode."""
        print("=" * 60)
        print("Welcome to the Payroll Agent System")
        print("=" * 60)
        print("\nAvailable commands:")
        print("- 'analyze': Analyze timesheets for anomalies")
        print("- 'pending': List all pending timesheets")
        print("- 'send email': Send notifications to employees with pending timesheets")
        print("- 'exit': Exit the system")
        print("\nOr describe what you want to do in natural language.")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n> ").strip()
                
                # Check for exit command
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process the request using agentic approach
                print("\n🤖 Processing your request...")
                response = await self.process_request(user_input)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    async def batch_mode(self, command: str):
        """Run a single command in batch mode.
        
        Args:
            command: The command to execute
        """
        print(f"🤖 Processing: {command}")
        response = await self.process_request(command)
        print(f"\n{response}")


async def main():
    """Main entry point for the application."""
    
    # Create the payroll system
    system = PayrollAgentSystem()
    
    # Check if a command was provided as argument
    if len(sys.argv) > 1:
        # Batch mode - execute the provided command
        command = " ".join(sys.argv[1:])
        await system.batch_mode(command)
    else:
        # Interactive mode
        await system.interactive_mode()


if __name__ == "__main__":
    # Run the main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nApplication terminated.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
