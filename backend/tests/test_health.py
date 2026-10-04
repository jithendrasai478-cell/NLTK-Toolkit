def test_root_endpoint(client):
    """Test that root endpoint responds with basic info."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["name"] == "NLTK Toolkit API"
    assert json_data["status"] == "online"

def test_health_endpoint(client):
    """Test that /api/v1/health returns status healthy and resource info."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "healthy"
    assert json_data["data"]["api_version"] == "v1.0.0"
    assert "nltk_resources" in json_data["data"]
    assert json_data["data"]["nltk_resources"]["punkt"] is True
