from pydantic import BaseModel, validator, Field, EmailStr
from datetime import datetime


class UserSchemaBase(BaseModel):
    username: str = Field(min_length=2, max_length=20)
    email: EmailStr | None = None
    fio: str | None = Field(min_length=5, max_length=50)


class UserSchemaCreate(UserSchemaBase):
    password: str = Field(min_length=8, max_length=32)
    role_id: int | None = Field(ge=1)


class UserSchemaUpdate(UserSchemaBase):
    username: str | None = Field(min_length=2, max_length=20)
    password: str | None = Field(min_length=8, max_length=32)


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    fio: str | None = None
    created_at: str
    updated_at: str
    role: "RoleUserSchema" = Field(exclude={"id", "users"})
    summaries: list["SummarySchema"] | None = Field(
        exclude={"__all__": {"user", "comments"}}
    )
    comments: list["CommentSchema"] | None = Field(
        exclude={"__all__": {"user", "summary"}}
    )

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


class UserParentSchema(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    fio: str | None = None
    created_at: str
    updated_at: str
    role: "RoleUserSchema" = Field(exclude={"users"})

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


from .role import RoleUserSchema
from .summary import SummarySchema
from .comment import CommentSchema

UserSchema.update_forward_refs()
UserParentSchema.update_forward_refs()
