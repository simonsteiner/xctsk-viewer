from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key-change-in-production"

    # File upload configuration
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    app.config["UPLOAD_EXTENSIONS"] = [".xctsk"]

    # Register routes
    from app.routes import main, static_routes

    app.register_blueprint(main.bp)
    app.register_blueprint(static_routes.static_bp)

    return app
