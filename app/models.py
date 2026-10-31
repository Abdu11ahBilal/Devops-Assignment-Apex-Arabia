from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)  # "   " becomes "" and fails min_length

    title: str = Field(min_length=1, max_length=200)


class Task(BaseModel):
    id: int
    title: str
    done: bool
    created_at: datetime
