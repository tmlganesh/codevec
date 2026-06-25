"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import router
from contextlib import asynccontextmanager
from app.database import engine, Base, SessionLocal
from app.models import Product
import seed

# Create tables and indexes on startup
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        count = db.query(Product).count()
        if count == 0:
            print("Database is empty. Automatically seeding data...")
            seed.seed()
    finally:
        db.close()
    yield

app = FastAPI(title="Product Browser API", version="1.0.0", lifespan=lifespan)

# Register API routes
app.include_router(router)


# Serve static files (HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_ui():
    """Serve the single-page HTML frontend."""
    return FileResponse("static/index.html")
