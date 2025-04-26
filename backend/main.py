# backend application for the ask-rag application
# this will expose following endpoints:
# 1. /ingest
# 2. /ask

from app.api.endpoints import router
from fastapi import FastAPI

app = FastAPI()

# Include the router
app.include_router(router)
