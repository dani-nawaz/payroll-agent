"""CSV implementation of the timesheet repository."""

import pandas as pd
from typing import List, Optional
from datetime import datetime
import os
from pathlib import Path

from src.repositories.base import TimesheetRepository
from src.models.timesheet import TimesheetEntry, EmployeeTimesheetSummary, TimesheetAnomaly
from src.config import settings


class CSVTimesheetRepository(TimesheetRepository):
    """CSV-based implementation of the timesheet repository."""
    
    def __init__(self, csv_path: Optional[str] = None):
        """Initialize the CSV repository.
        
        Args:
            csv_path: Path to the CSV file. If None, uses default from settings.
        """
        self.csv_path = csv_path or settings.app.csv_data_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the CSV file and directory exist."""
        path = Path(self.csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            # Create empty CSV with headers
            df = pd.DataFrame(columns=[
                'employee_id', 'employee_name', 'employee_email',
                'date', 'hours_worked', 'project', 'status', 'notes'
            ])
            df.to_csv(self.csv_path, index=False)
    
    async def _load_data(self) -> pd.DataFrame:
        """Load data from CSV file."""
        try:
            df = pd.read_csv(self.csv_path)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    async def _save_data(self, df: pd.DataFrame):
        """Save data to CSV file."""
        df.to_csv(self.csv_path, index=False)
    
    def _df_to_timesheet_entry(self, row: pd.Series) -> TimesheetEntry:
        """Convert a DataFrame row to TimesheetEntry."""
        # Handle NaN values properly
        project = row.get('project')
        if pd.isna(project):
            project = None
        
        notes = row.get('notes')
        if pd.isna(notes):
            notes = None
        
        return TimesheetEntry(
            employee_id=str(row['employee_id']),
            employee_name=row['employee_name'],
            employee_email=row['employee_email'],
            date=pd.to_datetime(row['date']),
            hours_worked=float(row['hours_worked']),
            project=project,
            status=row.get('status', 'pending'),
            notes=notes
        )
    
    async def get_timesheets_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[TimesheetEntry]:
        """Get timesheets within a date range."""
        df = await self._load_data()
        if df.empty:
            return []
        
        # Filter by date range
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df.loc[mask]
        
        return [
            self._df_to_timesheet_entry(row)
            for _, row in filtered_df.iterrows()
        ]
    
    async def get_employee_timesheets(
        self, 
        employee_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TimesheetEntry]:
        """Get timesheets for a specific employee."""
        df = await self._load_data()
        if df.empty:
            return []
        
        # Filter by employee
        filtered_df = df[df['employee_id'] == employee_id]
        
        # Apply date filters if provided
        if start_date:
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        if end_date:
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
        
        return [
            self._df_to_timesheet_entry(row)
            for _, row in filtered_df.iterrows()
        ]
    
    async def get_pending_timesheets(self) -> List[TimesheetEntry]:
        """Get all pending timesheets."""
        df = await self._load_data()
        if df.empty:
            return []
        
        pending_df = df[df['status'] == 'pending']
        
        return [
            self._df_to_timesheet_entry(row)
            for _, row in pending_df.iterrows()
        ]
    
    async def update_timesheet_status(
        self, 
        employee_id: str, 
        date: datetime, 
        status: str
    ) -> bool:
        """Update the status of a timesheet entry."""
        df = await self._load_data()
        if df.empty:
            return False
        
        # Find the matching row
        mask = (df['employee_id'] == employee_id) & (df['date'] == date)
        if mask.any():
            df.loc[mask, 'status'] = status
            await self._save_data(df)
            return True
        
        return False
    
    async def get_employee_summary(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[EmployeeTimesheetSummary]:
        """Get summary of employee timesheets for a period."""
        timesheets = await self.get_employee_timesheets(
            employee_id, start_date, end_date
        )
        
        if not timesheets:
            return None
        
        # Calculate summary statistics
        total_hours = sum(ts.hours_worked for ts in timesheets)
        total_days = len(set(ts.date.date() for ts in timesheets))
        avg_hours = total_hours / total_days if total_days > 0 else 0
        
        # Find anomalies
        anomalies = []
        for ts in timesheets:
            if ts.hours_worked < settings.app.anomaly_threshold_hours:
                anomalies.append(TimesheetAnomaly(
                    employee_id=ts.employee_id,
                    employee_name=ts.employee_name,
                    employee_email=ts.employee_email,
                    date=ts.date,
                    expected_hours=settings.app.anomaly_threshold_hours,
                    actual_hours=ts.hours_worked,
                    anomaly_type="missing_hours",
                    description=f"Only {ts.hours_worked} hours logged, expected at least {settings.app.anomaly_threshold_hours}",
                    severity="medium" if ts.hours_worked > 4 else "high"
                ))
        
        # Get the first timesheet for employee info
        first_ts = timesheets[0]
        
        return EmployeeTimesheetSummary(
            employee_id=employee_id,
            employee_name=first_ts.employee_name,
            employee_email=first_ts.employee_email,
            period_start=start_date,
            period_end=end_date,
            total_hours=total_hours,
            total_days=total_days,
            average_hours_per_day=avg_hours,
            anomalies=anomalies,
            status="pending"
        )
    
    async def create_timesheet(self, entry: TimesheetEntry) -> TimesheetEntry:
        """Create a new timesheet entry."""
        df = await self._load_data()
        
        new_row = pd.DataFrame([{
            'employee_id': entry.employee_id,
            'employee_name': entry.employee_name,
            'employee_email': entry.employee_email,
            'date': entry.date,
            'hours_worked': entry.hours_worked,
            'project': entry.project,
            'status': entry.status,
            'notes': entry.notes
        }])
        
        df = pd.concat([df, new_row], ignore_index=True)
        await self._save_data(df)
        
        return entry
