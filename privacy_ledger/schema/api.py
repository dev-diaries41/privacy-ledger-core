from pydantic import BaseModel
from typing import List, Optional, Literal

from privacy_ledger.schema.events import PrivacyEvent, Filter

class EventsPayload(BaseModel):
    events: List[PrivacyEvent]

class AddEventsRequest(EventsPayload):
    pass

class AddEventsResponse(BaseModel):
    added: int
 
class SearchEventsRequest(BaseModel):
    filter: Filter
    offset: Optional[int] = 0
    limit: Optional[int] = 25
    order_by: Literal["created_at", "updated_at", "date", "id"] = "created_at"
    ascending: bool = True

class SearchEventsResponse(EventsPayload):
    pass

class CountEventsRequest(Filter):
    pass

class CountEventsResponse(BaseModel):
    count: int
 