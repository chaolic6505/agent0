import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks



from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob

from schemas.job import StoryJobResponse
from schemas.story import CompleteStoryResponse, CreateStoryRequest, CompleteStoryNodeResponse

from core.story_generator import StoryGenerator

router = APIRouter(
    prefix="/story",
    tags=["stories"]
)


def get_session_id(session_id: str = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        generate_story_task,
        job_id,
        request.theme,
        session_id
    )

    return job

def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal()

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        if not job:
            return

        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()

        except Exception as e:
            job.error = str(e)
            job.status = "failed"
            job.completed_at = datetime.now()
            db.commit()
            raise e
    finally:
        db.close()



@router.get("/{story_id}/complete", response_model=StoryJobResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")


    complete_story = build_complete_story(story_id, db)

    return complete_story


def build_complete_story(story_id: int, db: Session = Depends(get_db)):
    pass


