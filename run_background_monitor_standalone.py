#!/usr/bin/env python3
"""Standalone Background Monitor - Runs in separate terminal window."""

import asyncio
import sys
import os
import subprocess
import platform
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.background_monitor_agent import BackgroundMonitorAgent


def run_in_separate_terminal():
    """Run the background monitor in a separate terminal window."""
    script_path = Path(__file__).absolute()
    
    if platform.system() == "Windows":
        # Windows - use start command to open new terminal
        cmd = f'start "Background Monitor" cmd /k "python {script_path} --monitor"'
        subprocess.run(cmd, shell=True)
    elif platform.system() == "Darwin":  # macOS
        # macOS - use Terminal.app
        cmd = f'osascript -e \'tell app "Terminal" to do script "cd {project_root} && python {script_path} --monitor"\'' 
        subprocess.run(cmd, shell=True)
    else:  # Linux
        # Linux - try different terminal emulators
        terminals = [
            f'gnome-terminal -- bash -c "cd {project_root} && python {script_path} --monitor; exec bash"',
            f'konsole -e bash -c "cd {project_root} && python {script_path} --monitor; exec bash"',
            f'xterm -e bash -c "cd {project_root} && python {script_path} --monitor; exec bash"'
        ]
        
        for terminal_cmd in terminals:
            try:
                subprocess.run(terminal_cmd, shell=True)
                break
            except:
                continue


async def run_monitor():
    """Run the background monitor."""
    print("Background Monitor Agent - Separate Terminal")
    print("=" * 60)
    print("Monitoring: abdulrehman@clickchain.com")
    print("Check Interval: 60 seconds")
    print("Log File: logs/background_monitor.log")
    print("=" * 60)
    print("Press Ctrl+C to stop the monitor")
    print("=" * 60)
    
    monitor = BackgroundMonitorAgent()
    
    try:
        await monitor.start_background_monitoring()
    except KeyboardInterrupt:
        print("\n[INFO] Received interrupt, shutting down...")
        monitor.stop_monitoring()
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        monitor.stop_monitoring()


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Run the monitor
        asyncio.run(run_monitor())
    else:
        # Start in separate terminal
        print("[INFO] Starting Background Monitor in separate terminal...")
        run_in_separate_terminal()
        print("[INFO] Background monitor started in separate terminal window")
        print("[INFO] Check the new terminal window for monitoring logs")


if __name__ == "__main__":
    main()
