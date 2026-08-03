from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import setting
from app.api.routes.movies import router as movies_router
from app.api.routes.series import router as series_router
from app.api.routes.live import router as live_router
from app.api.routes.auth import router as auth_router
from app.api.routes.stream import router as stream_router
from app.api.routes.favorites import router as favorites_router
from app.db.init_db import init_db

from app.core.http_client import start_http_client, stop_http_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    init_db()
    start_http_client()
    
    yield
    
    # --- SHUTDOWN ---
    await stop_http_client()


app = FastAPI(
    title=setting.app_name,
    debug=setting.debug,
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(series_router)
app.include_router(live_router)
app.include_router(stream_router)
app.include_router(favorites_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

