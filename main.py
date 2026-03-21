import os
import asyncio

from dotenv import load_dotenv

from privacy_ledger.event_store import EventStore
from privacy_ledger.data import generate_events

load_dotenv()

POSTGRES_URI = os.environ.get("POSTGRES_URI")

db = EventStore(POSTGRES_URI, 768)

async def main():
    # events = generate_events(2)
    count = await db.count()
    print(f"Initial count: {count}")

    events = await db.get()
    print(events)
    

    # await db.add(events)

    # count = await db.count()
    # print(f"Updated count: {count}")

asyncio.run(main())