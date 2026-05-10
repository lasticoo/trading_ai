from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import scan, proposals, trades, account
from src.db.database import engine, Base
from src.db import models  # WAJIB agar SQLAlchemy register table

app = FastAPI(title="Trading AI API")

# =========================
# CORS (FE → BE)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nanti bisa dikunci
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# INIT DATABASE
# =========================
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# =========================
# ROUTES (TANPA PREFIX TAMBAHAN)
# =========================
app.include_router(scan.router)       # POST /scan
app.include_router(proposals.router)  # GET /proposals, POST /{id}/accept|reject
app.include_router(trades.router)     # GET / (active trades), POST /{trade_id}/close
app.include_router(account.router)    # /account/*
