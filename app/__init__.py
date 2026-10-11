"""Flask app factory for xctsk-viewer.

Initializes the Flask application, configures file upload settings,
and registers route blueprints.
"""

import os

from flask import Flask


def create_app():
    """Create and configure the Flask app instance."""
    app = Flask(__name__)
    # `or`, not a .get() default: an empty FLASK_SECRET_KEY (e.g. the blank
    # line in .env.example) must fall back too, or flash() raises.
    app.config["SECRET_KEY"] = (
        os.environ.get("FLASK_SECRET_KEY") or "your-secret-key-change-in-production"
    )

    # File upload configuration
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    app.config["UPLOAD_EXTENSIONS"] = [".xctsk"]

    # Register routes
    from app.routes import airspace, api, main, static_routes

    app.register_blueprint(main.bp)
    app.register_blueprint(static_routes.static_bp)
    app.register_blueprint(api.api_bp)
    app.register_blueprint(airspace.airspace_bp)

    return app
