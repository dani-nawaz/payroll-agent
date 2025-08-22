"""Base repository interface following SOLID principles."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generic, TypeVar
from datetime import datetime

from src.models.timesheet import TimesheetEntry, EmployeeTimesheetSummary

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for data access."""
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Retrieve all records."""
        pass
    
    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[T]:
        """Retrieve a record by ID."""
        pass
    
    @abstractmethod
    async def create(self, record: T) -> T:
        """Create a new record."""
        pass
    
    @abstractmethod
    async def update(self, record_id: str, record: T) -> Optional[T]:
        """Update an existing record."""
        pass
    
    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """Delete a record by ID."""
        pass


class TimesheetRepository(ABC):
    """Abstract repository for timesheet operations."""
    
    @abstractmethod
    async def get_timesheets_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[TimesheetEntry]:
        """Get timesheets within a date range."""
        pass
    
    @abstractmethod
    async def get_employee_timesheets(
        self, 
        employee_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TimesheetEntry]:
        """Get timesheets for a specific employee."""
        pass
    
    @abstractmethod
    async def get_pending_timesheets(self) -> List[TimesheetEntry]:
        """Get all pending timesheets."""
        pass
    
    @abstractmethod
    async def update_timesheet_status(
        self, 
        employee_id: str, 
        date: datetime, 
        status: str
    ) -> bool:
        """Update the status of a timesheet entry."""
        pass
    
    @abstractmethod
    async def get_employee_summary(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[EmployeeTimesheetSummary]:
        """Get summary of employee timesheets for a period."""
        pass
