# backend application for the ask-rag application
# this will expose following endpoints:
# 1. /ingest
# 2. /ask
# 3. /authenticate # optional

from fastapi import FastAPI
from app.api.endpoints import router


app = FastAPI()

# Include the router
app.include_router(router)