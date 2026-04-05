from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    return render_template("index.html")

# NEW ROUTE: Serve the stats page
@views_bp.route("/stats/<short_code>")
def stats_page(short_code):
    return render_template("stats.html")

@views_bp.route("/health")
def health_check():
    # Returns a 200 OK with a JSON payload
    return jsonify({"status": "ok"}), 200