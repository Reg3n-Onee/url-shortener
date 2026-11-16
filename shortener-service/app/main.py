import os
import shortuuid
import redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, get_db, Base
from .models import Link

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

class ShortenRequest(BaseModel):
    url: str

class ShortenResponse(BaseModel):
    code: str
    short_url: str

@app.post("/shorten", response_model=ShortenResponse)
def shorten(payload: ShortenRequest, db: Session = Depends(get_db)):
    code = shortuuid.ShortUUID().random(length=6)
    db.add(Link(code=code, original_url=payload.url))
    db.commit()
    return ShortenResponse(code=code, short_url=f"/api/r/{code}")

@app.get("/r/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.code == code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    redis_client.publish("clicks", code)
    return RedirectResponse(url=link.original_url)

@app.get("/health")
def health():
    return {"status": "ok"}