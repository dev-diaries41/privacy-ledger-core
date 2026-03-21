from datetime import date
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

from privacy_ledger.enums import ImpactType, Topic, Severity, Scope, Platform

class PrivacyEvent(BaseModel):
    id: str
    title: str
    date: date
    topic: Topic
    actors: List[str]
    impact_types: List[ImpactType]
    platforms: List[Platform]
    severity: Severity
    scope: Scope
    summary: str
    impact_description: str
    source: HttpUrl
    tags: Optional[List[str]] = None
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)

class Filter(BaseModel):
    topic: Optional[str] = None
    actors: Optional[List[str]] = None
    impact_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    severity: Optional[int] = None
    scope: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    updated_after: Optional[date] = None
    updated_before: Optional[date] = None