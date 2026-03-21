from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class Category(str, Enum):
    LAW = "law"
    TECH = "tech"

class ActorType(str, Enum):
    COMPANY = "company"
    GOVERNMENT = "government"
    ORGANIZATION = "organization"
    UNKNOWN = "unknown"

class ImpactType(str, Enum):
    DATA_EXPOSURE = "data_exposure"
    LOSS_OF_ANONYMITY = "loss_of_anonymity"
    BEHAVIORAL_TRACKING = "behavioral_tracking"
    LEGAL_PRECEDENT = "legal_precedent"
    MASS_SURVEILLANCE = "mass_surveillance"
    CONSENT_VIOLATION = "consent_violation"
    OTHER = "other"

class Scope(str, Enum):
    LOCAL = "local"
    NATIONAL = "national"
    GLOBAL = "global"

class Severity(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PrivacyEvent(BaseModel):
    id: str
    title: str
    date: date
    category: Category
    actors: List[str]
    impact_types: List[ImpactType]
    severity: Severity
    scope: Scope
    summary: str
    impact_description: str
    source: HttpUrl
    tags: Optional[List[str]] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

class Filter(BaseModel):
    category: Optional[str] = None
    actors: Optional[List[str]] = None
    impact_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    severity: Optional[int] = None
    scope: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    updated_after: Optional[date] = None
    updated_before: Optional[date] = None