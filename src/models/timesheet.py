"""Timesheet data models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class TimesheetEntry(BaseModel):
    """Model representing a single timesheet entry."""
    
    employee_id: str = Field(..., description="Unique employee identifier")
    employee_name: str = Field(..., description="Employee full name")
    employee_email: EmailStr = Field(..., description="Employee email address")
    date: datetime = Field(..., description="Date of the timesheet entry")
    hours_worked: float = Field(..., ge=0, le=24, description="Hours worked on this date")
    project: Optional[str] = Field(None, description="Project or department")
    status: str = Field("pending", description="Timesheet status: pending, approved, rejected")
    notes: Optional[str] = Field(None, description="Additional notes or comments")


class TimesheetAnomaly(BaseModel):
    """Model representing an anomaly in timesheet data."""
    
    employee_id: str
    employee_name: str
    employee_email: EmailStr
    date: datetime
    expected_hours: float
    actual_hours: float
    anomaly_type: str  # "missing_hours", "excessive_hours", "missing_entry"
    description: str
    severity: str = Field("medium", description="Severity: low, medium, high")


class EmployeeTimesheetSummary(BaseModel):
    """Summary of an employee's timesheet for a period."""
    
    employee_id: str
    employee_name: str
    employee_email: EmailStr
    period_start: datetime
    period_end: datetime
    total_hours: float
    total_days: int
    average_hours_per_day: float
    anomalies: List[TimesheetAnomaly] = Field(default_factory=list)
    status: str = "pending"
