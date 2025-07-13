import os

from flask import Blueprint, send_from_directory

static_bp = Blueprint("static_routes", __name__)


def _serve_static_file(filename, mimetype):
    """Helper function to serve static files."""
    return send_from_directory(
        os.path.join(static_bp.root_path, "..", "static"), filename, mimetype=mimetype
    )


# Favicon and icon routes
@static_bp.route("/favicon.ico")
def favicon():
    return _serve_static_file("favicon.ico", "image/vnd.microsoft.icon")


@static_bp.route("/android-chrome-192x192.png")
def android_chrome_192():
    return _serve_static_file("android-chrome-192x192.png", "image/png")


@static_bp.route("/android-chrome-512x512.png")
def android_chrome_512():
    return _serve_static_file("android-chrome-512x512.png", "image/png")


@static_bp.route("/apple-touch-icon.png")
def apple_touch_icon():
    return _serve_static_file("apple-touch-icon.png", "image/png")


@static_bp.route("/favicon-16x16.png")
def favicon_16():
    return _serve_static_file("favicon-16x16.png", "image/png")


@static_bp.route("/favicon-32x32.png")
def favicon_32():
    return _serve_static_file("favicon-32x32.png", "image/png")


@static_bp.route("/site.webmanifest")
def site_webmanifest():
    return _serve_static_file("site.webmanifest", "application/manifest+json")
