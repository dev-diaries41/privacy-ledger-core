import os

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from privacy_ledger.event_store import EventStore
from privacy_ledger.schema.api import SearchEventsRequest, SearchEventsResponse, AddEventsRequest, AddEventsResponse, CountEventsRequest, CountEventsResponse

from api.routes import Routes

load_dotenv()

POSTGRES_HOST=os.environ.get("POSTGRES_HOST")
POSTGRES_USER=os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB=os.environ.get("POSTGRES_DB")

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_methods=["POST", "OPTIONS", "GET", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

db = EventStore(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB, embed_dim=768)


@app.post(Routes.ADD_EVENT_ENDPOINT) 
async def add_events(req: AddEventsRequest):
    if len(req.events) == 0:
        raise HTTPException(status_code=400, detail="No events provided")
    await db.add(req.events)
    return AddEventsResponse(added=len(req.events))

@app.post(Routes.SEARCH_EVENTS_ENDPOINT)
async def search_events(req: SearchEventsRequest):
    events = await db.get(filter=req.filter, limit=req.limit, offset=req.offset, order_by=req.order_by, ascending=req.ascending)
    return JSONResponse(SearchEventsResponse(events=events).model_dump())


@app.post(Routes.COUNT_EVENTS_ENDPOINT)
async def count_prompts(req: CountEventsRequest):
    count = await db.count(filter=req)
    return JSONResponse(CountEventsResponse(count=count).model_dump())
