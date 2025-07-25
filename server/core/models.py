from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field


class StoryOptionsLLM(BaseModel):
    text: str = Field(description="The text of the option shown to the user")
    nextNode: Dict[str, Any] = Field(description="The next node content nad its options")

class StoryNodeLLM(BaseModel):
    content: str = Field(description="The content of the node")
    isEnding: bool = Field(description="Whether the node is an ending node")
    isWinningEnding: bool = Field(description="Whether the node is a winning ending node")
    options: Optional[List[StoryOptionsLLM]] = Field(default=[], description="The options for the node")

class StoryLLMResponse(BaseModel):
    title: str = Field(description="The title of the story")
    rootNode: StoryNodeLLM = Field(description="The root node of the story")