from pydantic import BaseModel


class TagsResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}