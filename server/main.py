from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_database
from routers import story, job, redis
from graphql_api.router import router as graphql_router

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(
    title="Auction System",
    description="A secure, real-time auction system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(graphql_router, prefix="/graphql", tags=["graphql"])
app.include_router(job.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(redis.router, prefix="/api/v1/redis", tags=["redis"])
app.include_router(story.router, prefix="/api/v1/stories", tags=["stories"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Auction System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
