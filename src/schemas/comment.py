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
    user: "UserParentSchema" = Field(
        exclude={"summaries", "comments", "created_at", "updated_at", "role"}
    )
    summary: "SummaryParentSchema" = Field(
        exclude={"user", "comments", "created_at", "updated_at"}
    )

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


class CommentUserSchema(CommentSchema):
    class Config:
        fields = {"user": {"exclude": True}}
        orm_mode = True


from .user import UserParentSchema
from .summary import SummaryParentSchema

CommentSchema.update_forward_refs()
CommentUserSchema.update_forward_refs()
