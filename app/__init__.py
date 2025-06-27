from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key-change-in-production"

    # Register routes
    from app.routes import main

    app.register_blueprint(main.bp)

    return app
