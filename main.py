import os
import asyncio

from dotenv import load_dotenv

from privacy_ledger.data.event_store import EventStore
from privacy_ledger.data.helpers import generate_events

load_dotenv()

POSTGRES_URI = os.environ.get("POSTGRES_URI")
POSTGRES_HOST=os.environ.get("POSTGRES_HOST")
POSTGRES_USER=os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB=os.environ.get("POSTGRES_DB")

store = EventStore(database=POSTGRES_DB, embed_dim=768)

async def main():
    count = await store.count()
    print(f"Initial count: {count}")

    # events = await db.get()
    # print(events)
    
    # events = generate_events(2)
    # await store.add(events)

    # count = await store.count()
    # print(f"Updated count: {count}")

    print(f"Overview: {await store.get_events_overview()}")

asyncio.run(main())