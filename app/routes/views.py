from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    # Renders app/templates/index.html
    return render_template("index.html")