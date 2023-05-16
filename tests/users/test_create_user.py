import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import user, users


user_data = {"username": "Paul", "password": "paul_password"}


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """
    Trying to create user
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]
