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