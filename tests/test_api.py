from datetime import datetime
from app.models.user import User

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_shorten_and_redirect(client):
    # 1. Test creating a short URL
    post_res = client.post("/shorten", json={"original_url": "https://mlh.io"})
    assert post_res.status_code == 201
    
    data = post_res.json
    assert "short_code" in data
    short_code = data["short_code"]

    # 2. Test the redirect
    get_res = client.get(f"/{short_code}")
    assert get_res.status_code == 302 # 302 is the HTTP code for Redirect
    assert get_res.location == "https://mlh.io"


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_ui_pages_render(client):
    """Ensure the HTML templates load successfully"""
    # Test main page
    response = client.get("/")
    assert response.status_code == 200
    assert b"Command Center" in response.data

def test_shorten_error_handling(client):
    """Ensure the API rejects bad payloads"""
    # Missing original_url
    response = client.post("/shorten", json={"user_id": 1, "title": "Bad Link"})
    assert response.status_code == 400
    assert "original_url is required" in response.json["error"]

def test_analytics_tracking(client):
    """Ensure clicks are logged and the stats API returns them"""
    
    # 0. Seed a dummy user into the empty test database
    User.create(
        id=1, 
        username="testuser", 
        email="testuser@acme.dev", 
        created_at=datetime.now()
    )

    # 1. Create a link
    create_res = client.post("/shorten", json={"original_url": "https://github.com", "user_id": 1})
    
    # Verify the creation was successful before proceeding
    assert create_res.status_code == 201
    short_code = create_res.json["short_code"]

    # 2. Click the link (triggering the Event logger)
    client.get(f"/{short_code}")
    
    # 3. Check the stats API to ensure the click was recorded
    stats_res = client.get(f"/api/stats/{short_code}")
    assert stats_res.status_code == 200
    assert stats_res.json["total_clicks"] == 1
    assert stats_res.json["original_url"] == "https://github.com"