import pytest
from pytest_schema import exact_schema
from .schemas import user
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_user_unauthorized(client: AsyncClient, create_user):
    """
    Trying to delete user without auth
    """
    response = await client.delete("/users/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_authorized(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to delete user with auth
    """
    response = await client.delete("/users/1", headers=authorization_header)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_another_user(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to delete another user
    """
    response = await client.post(
        "/users", json={"username": "user2", "password": 12345678}
    )
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "user2"

    response = await client.delete("/users/2", headers=authorization_header)
    assert response.status_code == 405
    assert response.json().get("detail") == "Method Not Allowed"


@pytest.mark.asyncio
async def test_delete_not_existed_user(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to delete not existed user
    """
    response = await client.delete("/users/2", headers=authorization_header)
    assert response.status_code == 405
    assert response.json().get("detail") == "Method Not Allowed"
