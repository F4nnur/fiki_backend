from pydantic import BaseModel, Field, validator
from datetime import datetime


class CommentSchemaBase(BaseModel):
    text: str = Field(min_length=1, max_length=360)


class CommentSchemaCreate(CommentSchemaBase):
    user_id: int = Field(ge=1)
    summary_id: int = Field(ge=1)


class CommentSchemaUpdate(CommentSchemaBase):
    pass


class CommentSchema(BaseModel):
    id: int
    text: str
    created_at: str
    updated_at: str
    user: "UserSchema" = Field(include={"id", "username", "email", "fio", "role"})
    summary: "SummarySchema" = Field(exclude={"user", "comments"})

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


from .user import UserSchema
from .summary import SummarySchema

CommentSchema.update_forward_refs()
