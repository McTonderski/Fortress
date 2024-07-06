import pytest
from fastapi.testclient import TestClient
from docker_fortress.__main__ import app

client = TestClient(app, backend="asyncio")

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Docker container controller!"}

# def test_start_container():
#     response = client.post("/containers/start/your_container_id")
#     assert response.status_code == 200
#     assert "Container your_container_id started successfully." in response.json()["message"]

# Add similar tests for other endpoints
