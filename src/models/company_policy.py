"""Company policy models for dynamic reason validation."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class ValidReason(BaseModel):
    """Model for valid reasons that can be used for missing hours."""
    reason_type: str  # "sick", "personal", "work_from_home", "leave", "other"
    keywords: List[str]
    description: str
    requires_approval: bool = False
    max_days_per_month: Optional[int] = None
    requires_documentation: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class CompanyPolicy(BaseModel):
    """Model for company policies and rules."""
    policy_id: str
    policy_name: str
    description: str
    valid_reasons: List[ValidReason]
    min_hours_per_day: float = 8.0
    max_hours_per_day: float = 12.0
    max_followup_attempts: int = 3
    auto_approval_threshold: int = 2  # days per month
    requires_manager_approval: bool = True
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class PolicyRepository:
    """Repository for managing company policies."""
    
    def __init__(self):
        # Initialize with default policies
        self.policies: Dict[str, CompanyPolicy] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize with default company policies."""
        default_reasons = [
            ValidReason(
                reason_type="sick",
                keywords=["sick", "ill", "illness", "not feeling well", "under the weather", "fever", "cold", "flu"],
                description="Sick leave for health-related absences",
                requires_approval=False,
                max_days_per_month=5,
                requires_documentation=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ValidReason(
                reason_type="personal",
                keywords=["personal", "family", "emergency", "appointment", "doctor", "dentist", "family emergency"],
                description="Personal emergency or family-related absences",
                requires_approval=True,
                max_days_per_month=3,
                requires_documentation=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ValidReason(
                reason_type="work_from_home",
                keywords=["work from home", "remote", "wfh", "home office", "working remotely", "telecommute"],
                description="Work from home arrangements",
                requires_approval=True,
                max_days_per_month=None,  # No limit
                requires_documentation=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ValidReason(
                reason_type="leave",
                keywords=["leave", "vacation", "pto", "time off", "holiday", "annual leave"],
                description="Approved leave or vacation time",
                requires_approval=True,
                max_days_per_month=None,  # Based on available leave
                requires_documentation=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ValidReason(
                reason_type="other",
                keywords=["other", "miscellaneous", "unforeseen", "special circumstances"],
                description="Other valid business reasons",
                requires_approval=True,
                max_days_per_month=2,
                requires_documentation=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        default_policy = CompanyPolicy(
            policy_id="default",
            policy_name="Default Company Policy",
            description="Default policy for timesheet management",
            valid_reasons=default_reasons,
            min_hours_per_day=8.0,
            max_hours_per_day=12.0,
            max_followup_attempts=3,
            auto_approval_threshold=2,
            requires_manager_approval=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.policies["default"] = default_policy
    
    def get_policy(self, policy_id: str = "default") -> Optional[CompanyPolicy]:
        """Get a company policy by ID."""
        return self.policies.get(policy_id)
    
    def get_valid_reasons(self, policy_id: str = "default") -> List[ValidReason]:
        """Get valid reasons for a policy."""
        policy = self.get_policy(policy_id)
        if policy:
            return [reason for reason in policy.valid_reasons if reason.is_active]
        return []
    
    def add_valid_reason(self, policy_id: str, reason: ValidReason) -> bool:
        """Add a new valid reason to a policy."""
        policy = self.get_policy(policy_id)
        if policy:
            policy.valid_reasons.append(reason)
            policy.updated_at = datetime.now()
            return True
        return False
    
    def update_valid_reason(self, policy_id: str, reason_type: str, updated_reason: ValidReason) -> bool:
        """Update an existing valid reason."""
        policy = self.get_policy(policy_id)
        if policy:
            for i, reason in enumerate(policy.valid_reasons):
                if reason.reason_type == reason_type:
                    policy.valid_reasons[i] = updated_reason
                    policy.updated_at = datetime.now()
                    return True
        return False
    
    def deactivate_reason(self, policy_id: str, reason_type: str) -> bool:
        """Deactivate a valid reason."""
        policy = self.get_policy(policy_id)
        if policy:
            for reason in policy.valid_reasons:
                if reason.reason_type == reason_type:
                    reason.is_active = False
                    reason.updated_at = datetime.now()
                    policy.updated_at = datetime.now()
                    return True
        return False
