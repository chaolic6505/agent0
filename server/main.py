from fastapi import FastAPI
from routers import story, job
from db.database import create_tables
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings

create_tables()

app = FastAPI(
    title="StoryTeller",
    description="A storyteller app",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_origins=settings.ALLOW_ORIGINS,
)

app.include_router(job.router, prefix=settings.API_PREFIX)
app.include_router(story.router, prefix=settings.API_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
