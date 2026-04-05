from flask import Blueprint, request, jsonify, redirect
import string
import random
import json
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from app.models.url import Url
from app.models.event import Event

urls_bp = Blueprint("urls", __name__)

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@urls_bp.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.json
    if not data or "original_url" not in data:
        return jsonify({"error": "original_url is required"}), 400
    
    original = data["original_url"]
    user_id = data.get("user_id") 
    title = data.get("title", "Untitled")

    code = generate_short_code()
    while Url.select().where(Url.short_code == code).exists():
        code = generate_short_code()

    now = datetime.now()
    
    # 1. Create the URL
    url = Url.create(
        original_url=original, 
        short_code=code, 
        user_id=user_id,
        title=title,
        created_at=now,
        updated_at=now
    )
    
    # 2. Log the creation event
    event_details = json.dumps({"short_code": code, "original_url": original})
    Event.create(
        url=url,
        user_id=user_id,
        event_type="created",
        timestamp=now,
        details=event_details
    )

    return jsonify(model_to_dict(url)), 201

@urls_bp.route("/api/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    try:
        url = Url.get(Url.short_code == short_code)
        
        # Get all events for this URL, ordered by newest first
        events = Event.select().where(Event.url == url).order_by(Event.timestamp.desc())
        
        click_events = []
        for e in events:
            if e.event_type == "clicked":
                # Parse the JSON string stored in the details column
                details = json.loads(e.details) if e.details else {}
                click_events.append({
                    "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "ip_address": details.get("ip_address", "Unknown"),
                    "user_agent": details.get("user_agent", "Unknown")
                })
        
        return jsonify({
            "short_code": url.short_code,
            "original_url": url.original_url,
            "title": url.title,
            "created_at": url.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "total_clicks": len(click_events),
            "recent_clicks": click_events[:15] # Send the last 15 clicks to the UI
        }), 200
        
    except Url.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404

@urls_bp.route("/<short_code>", methods=["GET"])
def redirect_url(short_code):
    try:
        # Check if URL exists AND is active
        url = Url.get((Url.short_code == short_code) & (Url.is_active == True))
        
        # Log the click event as a JSON string in the details column
        click_details = json.dumps({
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent')
        })
        
        Event.create(
            url=url, 
            event_type="clicked",
            timestamp=datetime.now(),
            details=click_details
        )

        return redirect(url.original_url)
    except Url.DoesNotExist:
        return jsonify({"error": "URL not found or inactive"}), 404