import pytest
from pytest_schema import exact_schema
from .schemas import login_response, refresh_access_token_response
from ..users.schemas import user
from httpx import AsyncClient


user_data = {"username": "username", "password": "password"}


@pytest.mark.asyncio
async def test_auth_not_existed_user(client: AsyncClient):
    """
    Trying to authorize not existed user
    """
    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"


@pytest.mark.asyncio
async def test_auth_existed_user(client: AsyncClient, create_user):
    """
    Trying to authorize existed user
    """
    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(login_response) == response.json()


@pytest.mark.asyncio
async def test_auth_blank_body(client: AsyncClient):
    """
    Trying to authorize user with incorrect blank data
    """
    response = await client.post("/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_not_valid_data(client: AsyncClient):
    """
    Trying to authorize user with invalid data
    """
    response = await client.post(
        "/auth/login", json={"username": "u", "password": "123"}
    )
    assert response.status_code == 422

    response = await client.post("/auth/login", json={"a": "b"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_short_username(client: AsyncClient):
    """
    Trying to authorize user with short username
    """
    response = await client.post(
        "/auth/login", json={"username": "u", "password": "password"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_short_password(client: AsyncClient):
    """
    Trying to authorize user with short password
    """
    response = await client.post(
        "/auth/login", json={"username": "username", "password": "123"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_invalid_creds(client: AsyncClient):
    """
    Trying to authorize user with invalid credentials
    """
    response = await client.post(
        "/auth/login", json={"username": "user", "password": "password"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"

    response = await client.post(
        "/auth/login", json={"username": "username", "password": "password2"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"

    response = await client.post(
        "/auth/login", json={"username": "user", "password": "password2"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"


@pytest.mark.asyncio
async def test_refresh_access_token(client: AsyncClient, create_user, authorize):
    """
    Trying to refresh access token
    """
    headers = {"Authorization": f'Bearer {authorize["refresh_token"]}'}
    response = await client.post("/auth/refresh", headers=headers)
    assert response.status_code == 200
    assert exact_schema(refresh_access_token_response) == response.json()


@pytest.mark.asyncio
async def test_refresh_access_token_unauthorized(client: AsyncClient):
    """
    Trying to refresh access token unauthorized
    """
    response = await client.post("/auth/refresh")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, create_user, authorization_header):
    """
    Trying to log out
    """
    response = await client.delete("/auth/logout")
    assert response.status_code == 401

    response = await client.delete("/auth/logout", headers=authorization_header)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, create_user, authorization_header):
    """
    Trying to get current user
    """
    response = await client.get("/users/me")
    assert response.status_code == 401

    response = await client.get("/users/me", headers=authorization_header)
    assert response.status_code == 200
    assert exact_schema(user)
