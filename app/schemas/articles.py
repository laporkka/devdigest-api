from pydantic import BaseModel
from datetime import datetime


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    source: str
    score: int
    created_at: datetime

    model_config = {"from_attributes": True}