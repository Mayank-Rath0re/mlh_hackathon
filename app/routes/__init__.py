def register_routes(app):
    """Register all route blueprints with the Flask app."""
    
    # Register the HTML views
    from app.routes.views import views_bp
    app.register_blueprint(views_bp)

    # Register the URL shortening logic (This was missing!)
    from app.routes.urls import urls_bp
    app.register_blueprint(urls_bp)