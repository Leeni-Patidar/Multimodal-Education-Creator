from pydantic import BaseModel


class GenerateRequest(BaseModel):
    topic: str
    level: str = "basic"
    style: str = "diagram"
    image_prompt: str | None = None
    image_count: int = 5
