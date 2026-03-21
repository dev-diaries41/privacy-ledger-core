from datetime import date
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

from privacy_ledger.enums import ImpactType, Topic, Severity, Scope, Platform

class PrivacyEvent(BaseModel):
    id: str
    title: str
    date: date
    topic: Topic
    actors: List[str]
    impact_types: List[ImpactType]
    severity: Severity
    scope: Scope
    summary: str
    impact_description: str
    source: HttpUrl
    tags: Optional[List[str]] = None
    platforms: Optional[List[Platform]] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

class Filter(BaseModel):
    topic: Optional[str] = None
    actors: Optional[List[str]] = None
    impact_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    platforms: Optional[List[Platform]] = None
    severity: Optional[int] = None
    scope: Optional[str] = None
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    updated_after: Optional[date] = None
    updated_before: Optional[date] = None