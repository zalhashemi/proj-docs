import os

import sentry_sdk
from fastapi import FastAPI

from app.routers import orders

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

app = FastAPI(title="Ledgerline API", version="0.9.2")
app.include_router(orders.router)


@app.get("/health")
def health():
    return {"status": "ok"}
