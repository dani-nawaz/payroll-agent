"""Generate sample timesheet data for testing."""

import pandas as pd
from datetime import datetime, timedelta
import random


def generate_sample_timesheets():
    """Generate sample timesheet data with some anomalies."""
    
    employees = [
        {"id": "EMP001", "name": "John Smith", "email": "john.smith@example.com"},
        {"id": "EMP002", "name": "Jane Doe", "email": "jane.doe@example.com"},
        {"id": "EMP003", "name": "Bob Johnson", "email": "bob.johnson@example.com"},
        {"id": "EMP004", "name": "Alice Williams", "email": "alice.williams@example.com"},
        {"id": "EMP005", "name": "Charlie Brown", "email": "charlie.brown@example.com"},
    ]
    
    projects = ["Project Alpha", "Project Beta", "Project Gamma", "Maintenance", None]
    
    data = []
    start_date = datetime.now() - timedelta(days=14)
    
    for employee in employees:
        for day_offset in range(14):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends for most employees
            if current_date.weekday() >= 5 and employee["id"] != "EMP003":
                continue
            
            # Generate hours with some anomalies
            if employee["id"] == "EMP001" and day_offset in [3, 7]:
                # John has missing hours on some days
                hours = random.uniform(3, 6)
            elif employee["id"] == "EMP002" and day_offset == 10:
                # Jane didn't log hours one day
                continue
            elif employee["id"] == "EMP003" and day_offset in [5, 6]:
                # Bob worked excessive hours on weekend
                hours = random.uniform(12, 16)
            elif employee["id"] == "EMP004" and day_offset in [2, 8]:
                # Alice has incomplete hours
                hours = random.uniform(4, 7)
            else:
                # Normal hours
                hours = random.uniform(7.5, 9)
            
            data.append({
                "employee_id": employee["id"],
                "employee_name": employee["name"],
                "employee_email": employee["email"],
                "date": current_date.strftime("%Y-%m-%d"),
                "hours_worked": round(hours, 1),
                "project": random.choice(projects),
                "status": "pending",
                "notes": None
            })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv("data/timesheets.csv", index=False)
    
    print(f"[OK] Generated {len(data)} timesheet entries")
    print(f"[OK] Saved to data/timesheets.csv")
    
    # Print summary
    print("\nSample anomalies created:")
    print("- EMP001 (John Smith): Missing hours on 2 days")
    print("- EMP002 (Jane Doe): Missing entry for 1 day")
    print("- EMP003 (Bob Johnson): Excessive weekend hours")
    print("- EMP004 (Alice Williams): Incomplete hours on 2 days")
    
    return df


if __name__ == "__main__":
    df = generate_sample_timesheets()
    print(f"\nDataFrame shape: {df.shape}")
    print("\nFirst few entries:")
    print(df.head())
