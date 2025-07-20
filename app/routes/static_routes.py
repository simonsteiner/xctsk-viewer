"""Static file routes for serving icons and manifest files."""

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
    """Serve the favicon.ico file."""
    return _serve_static_file("favicon.ico", "image/vnd.microsoft.icon")


@static_bp.route("/android-chrome-192x192.png")
def android_chrome_192():
    """Serve the 192x192 Android Chrome icon."""
    return _serve_static_file("android-chrome-192x192.png", "image/png")


@static_bp.route("/android-chrome-512x512.png")
def android_chrome_512():
    """Serve the 512x512 Android Chrome icon."""
    return _serve_static_file("android-chrome-512x512.png", "image/png")


@static_bp.route("/apple-touch-icon.png")
def apple_touch_icon():
    """Serve the Apple touch icon."""
    return _serve_static_file("apple-touch-icon.png", "image/png")


@static_bp.route("/favicon-16x16.png")
def favicon_16():
    """Serve the 16x16 favicon PNG."""
    return _serve_static_file("favicon-16x16.png", "image/png")


@static_bp.route("/favicon-32x32.png")
def favicon_32():
    """Serve the 32x32 favicon PNG."""
    return _serve_static_file("favicon-32x32.png", "image/png")


@static_bp.route("/site.webmanifest")
def site_webmanifest():
    """Serve the site web manifest file."""
    return _serve_static_file("site.webmanifest", "application/manifest+json")
