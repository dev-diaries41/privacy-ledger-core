import random
from datetime import date, timedelta
from typing import List
from uuid import uuid4

from privacy_ledger.schema.events import PrivacyEvent, Topic, Severity, Scope, ImpactType

def generate_events(n: int) -> List[PrivacyEvent]:
    dummy_actors = ["Acme Corp", "Gov Agency", "Privacy Org", "Unknown Entity"]
    dummy_sources = [
        "https://example.com/news",
        "https://example.com/research",
        "https://example.com/report"
    ]
    events = []
    for i in range(n):
        event = PrivacyEvent(
            id=str(uuid4()),
            title=f"Dummy Privacy Event {i+1}",
            date=date.today() - timedelta(days=random.randint(0, 365)),
            topic=random.choice(list(Topic)),
            actors=random.sample(dummy_actors, k=random.randint(1, 2)),
            impact_types=random.sample(list(ImpactType), k=random.randint(1, 3)),
            severity=random.choice(list(Severity)),
            scope=random.choice(list(Scope)),
            summary="This is a short summary of the privacy event.",
            impact_description="This is a detailed explanation of the privacy impact.",
            source=random.choice(dummy_sources),
            tags=["dummy", "test"],
            created_at=date.today(),
            updated_at=date.today(),
        )
        events.append(event)

    return events