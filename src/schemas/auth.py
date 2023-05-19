from pydantic import BaseModel, Field


class AuthSchemaIn(BaseModel):
    username: str = Field(min_length=2, max_length=20)
    password: str = Field(min_length=8, max_length=32)


class AuthSchemaOut(BaseModel):
    access_token: str
    refresh_token: str


class RefreshAccessToken(BaseModel):
    access_token: str
