import random
import json
from datetime import date, timedelta
from typing import List
from uuid import uuid4

from privacy_ledger.schema.events import (
    Event, Topic, Severity, Scope, ImpactType, Platform
)

def generate_events(n: int) -> List[Event]:
    dummy_actors = ["Acme Corp", "Gov Agency", "Privacy Org", "Unknown Entity"]
    dummy_sources = [
        "https://example.com/news",
        "https://example.com/research",
        "https://example.com/report"
    ]

    events = []
    for i in range(n):
        event = Event(
            id=str(uuid4()),
            title=f"Dummy Privacy Event {i+1}",
            date=date.today() - timedelta(days=random.randint(0, 365)),
            topic=random.choice(list(Topic)),
            actors=random.sample(dummy_actors, k=random.randint(1, 2)),
            impact_types=random.sample(list(ImpactType), k=random.randint(1, 3)),
            platforms=random.sample(list(Platform), k=random.randint(1, 2)),
            severity=random.choice(list(Severity)),
            scope=random.choice(list(Scope)),
            summary="This is a short summary of the privacy event.",
            impact_description="This is a detailed explanation of the privacy impact.",
            source=random.choice(dummy_sources),
            tags=["dummy", "test"],
        )
        events.append(event)

    return events

def load_events_from_file(path: str):
    with open(path, "r") as f:
        events = json.load(f)

    events = [Event(**e) for e in events]
    return events
