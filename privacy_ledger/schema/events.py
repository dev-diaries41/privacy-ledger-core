from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl, Field

from privacy_ledger.enums import ImpactType, Topic, Severity, Scope, Platform

class Event(BaseModel):
    id: str
    title: str
    date: date
    topic: Topic
    actors: List[str]
    impact_types: List[ImpactType]
    platforms: List[Platform]
    severity: Severity
    scope: Scope
    summary: str # description of event + impact  
    source: HttpUrl
    tags: Optional[List[str]] = None
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)

class EventFilter(BaseModel):
    topics: Optional[List[str]] = None
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
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class EventsOverview(BaseModel):
    total_events: int
    top_actor_counts: Dict[str, int]
    platform_counts: Dict[str, int]
    scope_counts: Dict[str, int]
    impact_type_counts: Dict[str, int]
    topic_counts: Dict[str, int]