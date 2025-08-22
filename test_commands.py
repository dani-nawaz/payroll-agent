"""Test script to demonstrate the agentic payroll system."""

import asyncio
from main import PayrollAgentSystem


async def test_system():
    """Test various commands in the payroll system using agentic approach."""
    print("="*60)
    print("Testing Payroll Agent System - Agentic Approach")
    print("="*60)
    
    # Initialize system
    system = PayrollAgentSystem()
    print("\n[OK] System initialized with agentic approach")
    
    # Test commands
    test_cases = [
        ("analyze", "Analyze timesheets for anomalies"),
        ("list pending", "List pending timesheets"),
        ("send email", "Send notifications to employees with pending timesheets"),
        ("What can you help me with?", "General inquiry")
    ]
    
    for command, description in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {description}")
        print(f"Command: {command}")
        print("-"*60)
        
        try:
            result = await system.process_request(command)
            # Show first 500 chars of result
            if len(result) > 500:
                print(result[:500] + "...")
            else:
                print(result)
        except Exception as e:
            print(f"[ERROR] {str(e)}")
    
    print("\n" + "="*60)
    print("[OK] All tests completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_system())
