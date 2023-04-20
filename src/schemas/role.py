from pydantic import BaseModel, Field


class RoleSchemaBase(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    description: str | None = Field(min_length=2, max_length=100)


class RoleSchemaCreate(RoleSchemaBase):
    pass


class RoleSchemaUpdate(RoleSchemaBase):
    name: str | None = Field(min_length=2, max_length=20)


class RoleUserSchema(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        orm_mode = True


class RoleSchema(RoleUserSchema):
    users: list["UserSchema"] | None = Field(
        include={"__all__": {"id", "username", "email", "fio"}}
    )

    class Config:
        orm_mode = True


from .user import UserSchema

RoleSchema.update_forward_refs()
