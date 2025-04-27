# backend application for the ask-rag application
# this will expose following endpoints:
# 1. /ingest
# 2. /ask

import uvicorn
from app.api.endpoints import router
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# Include the router
app.include_router(router)

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
