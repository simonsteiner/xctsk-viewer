"""WSGI entry point for Gunicorn.

This file is used by Gunicorn to run the Flask application in production.
It creates an application instance using the `create_app` function from the app module.
"""

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
