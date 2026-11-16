import os
import asyncio
import redis.asyncio as aredis
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import engine, get_db, SessionLocal, Base
from .models import Click

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def listen_for_clicks():
    r = aredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe("clicks")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        db = SessionLocal()
        db.add(Click(code=message["data"]))
        db.commit()
        db.close()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_for_clicks())

@app.get("/stats/{code}")
def get_stats(code: str, db: Session = Depends(get_db)):
    total = db.query(func.count(Click.id)).filter(Click.code == code).scalar()
    return {"code": code, "total_clicks": total}

@app.get("/health")
def health():
    return {"status": "ok"}