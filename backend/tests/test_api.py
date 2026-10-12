from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_sections():
    response = client.get("/sections")
    # Expect 200 OK (and list response)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_articles_query_params():
    # Test filtering parameters
    response = client.get("/articles?limit=5&q=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_trigger_scrape():
    response = client.post("/scrape")
    assert response.status_code == 202
    assert response.json()["status"] == "success"
