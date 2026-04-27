from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import asyncio

from database import engine, SessionLocal
import models
from routers import products, emission_factors, inventory, calculations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed demo data after server is already listening
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _seed)
    yield


def _seed():
    from seed_data import run_seed
    run_seed(engine, SessionLocal, models)


app = FastAPI(
    title="PCF Bilanzierung",
    description="Product Carbon Footprint Bilanzierung nach GHG Protocol / ISO 14067",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(emission_factors.router)
app.include_router(inventory.router)
app.include_router(calculations.router)

# Serve frontend static files
# Docker (root Dockerfile): frontend copied to /app/frontend
# Docker Compose: frontend volume-mounted at /frontend
# Local dev: ../frontend relative to backend/
_base = os.path.dirname(os.path.abspath(__file__))
for _candidate in [
    os.path.join(_base, "frontend"),
    os.path.join(_base, "..", "frontend"),
    "/frontend",
]:
    if os.path.isdir(_candidate):
        frontend_path = os.path.abspath(_candidate)
        break
else:
    frontend_path = None

if frontend_path and os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{page}.html")
    def serve_page(page: str):
        file_path = os.path.join(frontend_path, f"{page}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}
