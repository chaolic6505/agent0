from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict

class StoryOptionsSchema(BaseModel):
    text: str
    node_id: Optional[int] = None


class StoryNodeBase(BaseModel):
    content: str
    is_ending: bool = False
    is_winning_ending: bool = False

class CompleteStoryNodeResponse(StoryNodeBase):
    id: int
    options: List[StoryOptionsSchema]

    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    title: str
    session_id: str

    class Config:
        from_attributes = True

class CreateStoryRequest(BaseModel):
    theme: str


class CompleteStoryResponse(BaseModel):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: List[CompleteStoryNodeResponse]

    class Config:
        from_attributes = True
