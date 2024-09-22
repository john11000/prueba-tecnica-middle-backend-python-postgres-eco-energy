import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.features.allocation.infrastructure import adapter
from src.core.settings import settings
from src.features.allocation.api.api import api_router

app = FastAPI(
    title="API",
    description="API",
    version="0.1.0",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

adapter.start_mappers()

if __name__ == "__main__":
    uvicorn.run(app, port=8000, proxy_headers=True, log_level="debug")
