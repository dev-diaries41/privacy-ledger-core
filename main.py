import os
import asyncio

from dotenv import load_dotenv

from privacy_ledger.data.event_store import EventStore
from privacy_ledger.data.helpers import generate_events

load_dotenv()

POSTGRES_URI = os.environ.get("POSTGRES_URI")

db = EventStore(dsn=POSTGRES_URI, embed_dim=768)

async def main():
    count = await db.count()
    print(f"Initial count: {count}")

    # events = await db.get()
    # print(events)
    
    events = generate_events(2)
    await db.add(events)

    count = await db.count()
    print(f"Updated count: {count}")

asyncio.run(main())