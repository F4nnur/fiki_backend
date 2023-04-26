from pydantic import BaseModel, validator, Field
from datetime import datetime


class SummarySchemaBase(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    description: str | None = Field(min_length=10, max_length=1000)


class SummarySchemaCreate(SummarySchemaBase):
    user_id: int = Field(ge=1)


class SummarySchemaUpdate(SummarySchemaBase):
    title: str | None = Field(min_length=2, max_length=50)


class SummarySchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    created_at: str
    updated_at: str
    user: "UserParentSchema" = Field(
        exclude={"summaries", "comments", "created_at", "updated_at", "role"}
    )
    comments: list["CommentSchema"] | None = Field(exclude={"__all__": {"summary"}})

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


class SummaryParentSchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    created_at: str
    updated_at: str
    user: "UserParentSchema" = Field(
        exclude={"summaries", "comments", "created_at", "updated_at"}
    )

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


class SummaryUserSchema(SummarySchema):
    class Config:
        fields = {"user": {"exclude": True}, "comments": {"exclude": True}}
        orm_mode = True


from .user import UserParentSchema
from .comment import CommentSchema

SummarySchema.update_forward_refs()
SummaryParentSchema.update_forward_refs()
SummaryUserSchema.update_forward_refs()
