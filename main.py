import os
import asyncio
import argparse
from dotenv import load_dotenv

from privacy_ledger.data.event_store import EventStore
from privacy_ledger.data.helpers import load_events_from_file

load_dotenv()

POSTGRES_DB = os.environ.get("POSTGRES_DB")

store = EventStore(database=POSTGRES_DB, embed_dim=768)


async def cmd_count(args):
    count = await store.count()
    print(f"Count: {count}")


async def cmd_add(args):
    events = load_events_from_file(args.file)
    initial = await store.count()
    print(f"Initial count: {initial}")

    await store.add(events)

    updated = await store.count()
    print(f"Updated count: {updated}")


async def main():
    parser = argparse.ArgumentParser(description="EventStore CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_count = subparsers.add_parser("count", help="Count events")
    parser_count.set_defaults(func=cmd_count)

    parser_add = subparsers.add_parser("add", help="Add events from file")
    parser_add.add_argument("file", help="Path to JSON file with events")
    parser_add.set_defaults(func=cmd_add)

    args = parser.parse_args()
    await args.func(args)


if __name__ == "__main__":
    asyncio.run(main())