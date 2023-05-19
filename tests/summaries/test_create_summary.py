import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import summary, user_summaries


summary_data = {
    "title": "First Summary",
    "description": "It's description",
    "user_id": 1,
}


@pytest.mark.asyncio
async def test_create_summary_unauthorized(client: AsyncClient, create_user):
    """
    Trying to create summary unauthorized
    """
    response = await client.post("/summaries", json=summary_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_summary_authorized(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to create summary authorized
    """
    response = await client.post(
        "/summaries", json=summary_data, headers=authorization_header
    )
    assert response.status_code == 201
    assert exact_schema(summary) == response.json()
    assert response.json().get("title") == "First Summary"

    response = await client.get("/users/1/summaries", headers=authorization_header)
    assert response.status_code == 200
    assert exact_schema(user_summaries) == response.json()


@pytest.mark.asyncio
async def test_create_couple_summaries(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to create a couple of summaries
    """
    response = await client.post(
        "/summaries", json=summary_data, headers=authorization_header
    )
    assert response.status_code == 201
    assert exact_schema(summary) == response.json()
    assert response.json().get("title") == "First Summary"

    response = await client.post(
        "/summaries",
        json={
            "title": "Second Summary",
            "description": "It's description",
            "user_id": 1,
        },
        headers=authorization_header,
    )
    assert response.status_code == 201
    assert exact_schema(summary) == response.json()
    assert response.json().get("title") == "Second Summary"

    response = await client.get("/users/1/summaries", headers=authorization_header)
    assert response.status_code == 200
    assert exact_schema(user_summaries) == response.json()
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_create_blank_body(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to send request with blank body
    """
    response = await client.post("/summaries", json={}, headers=authorization_header)
    assert response.status_code == 422
