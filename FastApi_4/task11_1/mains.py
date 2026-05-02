import pytest
from fastapi.testclient import TestClient
from main import app, db

client = TestClient(app)


def setup_function():
    """Очищает БД перед каждым тестом"""
    db.clear()


def test_create_user_success():
    response = client.post("/users", json={"username": "alice", "age": 25})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["age"] == 25
    assert "id" in data
    assert data["id"] == 1


def test_create_user_missing_age():
    response = client.post("/users", json={"username": "bob"})
    assert response.status_code == 422


def test_create_user_missing_username():
    response = client.post("/users", json={"age": 30})
    assert response.status_code == 422


def test_create_user_empty_username():
    response = client.post("/users", json={"username": "", "age": 30})
    assert response.status_code == 422


def test_get_user_success():
    client.post("/users", json={"username": "charlie", "age": 35})
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "charlie"
    assert data["age"] == 35
    assert data["id"] == 1


def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_success():
    client.post("/users", json={"username": "david", "age": 40})
    response = client.delete("/users/1")
    assert response.status_code == 204


def test_delete_user_not_found():
    response = client.delete("/users/999")
    assert response.status_code == 404


def test_delete_twice():
    client.post("/users", json={"username": "eve", "age": 45})
    response1 = client.delete("/users/1")
    response2 = client.delete("/users/1")
    assert response1.status_code == 204
    assert response2.status_code == 404


def test_get_after_delete():
    client.post("/users", json={"username": "frank", "age": 50})
    client.delete("/users/1")
    response = client.get("/users/1")
    assert response.status_code == 404


def test_create_multiple_users():
    client.post("/users", json={"username": "user1", "age": 20})
    client.post("/users", json={"username": "user2", "age": 30})
    client.post("/users", json={"username": "user3", "age": 40})

    response1 = client.get("/users/1")
    response2 = client.get("/users/2")
    response3 = client.get("/users/3")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    assert response1.json()["username"] == "user1"
    assert response2.json()["username"] == "user2"
    assert response3.json()["username"] == "user3"