import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from main import app, db

fake = Faker()


def setup_function():
    """Очищает БД перед каждым тестом"""
    db.clear()


@pytest.mark.asyncio
async def test_create_user_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        username = fake.user_name()
        age = fake.random_int(min=18, max=100)

        response = await client.post(
            "/users",
            json={"username": username, "age": age}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == username
        assert data["age"] == age
        assert "id" in data


@pytest.mark.asyncio
async def test_get_user_success_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        username = fake.user_name()
        age = fake.random_int(min=18, max=100)

        create_response = await client.post(
            "/users",
            json={"username": username, "age": age}
        )
        user_id = create_response.json()["id"]

        response = await client.get(f"/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
        assert data["age"] == age
        assert data["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_not_found_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/users/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_success_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        username = fake.user_name()
        age = fake.random_int(min=18, max=100)

        create_response = await client.post(
            "/users",
            json={"username": username, "age": age}
        )
        user_id = create_response.json()["id"]

        delete_response = await client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 204

        get_response = await client.get(f"/users/{user_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/users/999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_twice_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        username = fake.user_name()
        age = fake.random_int(min=18, max=100)

        create_response = await client.post(
            "/users",
            json={"username": username, "age": age}
        )
        user_id = create_response.json()["id"]

        response1 = await client.delete(f"/users/{user_id}")
        response2 = await client.delete(f"/users/{user_id}")

        assert response1.status_code == 204
        assert response2.status_code == 404


@pytest.mark.asyncio
async def test_multiple_users_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        users = []
        for i in range(3):
            username = fake.user_name()
            age = fake.random_int(min=18, max=100)
            response = await client.post(
                "/users",
                json={"username": username, "age": age}
            )
            assert response.status_code == 201
            users.append(response.json())

        for i, user in enumerate(users, start=1):
            response = await client.get(f"/users/{i}")
            assert response.status_code == 200
            assert response.json()["username"] == user["username"]
            assert response.json()["age"] == user["age"]


@pytest.mark.asyncio
async def test_invalid_age_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        username = fake.user_name()
        invalid_age = -5

        response = await client.post(
            "/users",
            json={"username": username, "age": invalid_age}
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_username_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/users",
            json={"username": "", "age": 25}
        )
        assert response.status_code == 422