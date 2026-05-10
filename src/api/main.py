from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import scan, proposals, trades, account
from src.db.database import engine, Base
from src.db import models

app = FastAPI(title="Trading AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Database siap")

@app.get("/health")
def health():
    return {"status": "ok"}

# URUTAN PENTING: specific route dulu, wildcard belakangan
app.include_router(scan.router)       # POST /scan
app.include_router(account.router)    # /account/*
app.include_router(proposals.router)  # GET /proposals, POST /{id}/accept|reject
app.include_router(trades.router)     # GET /, POST /{id}/close