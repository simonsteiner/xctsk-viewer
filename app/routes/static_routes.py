"""Static file routes for serving icons and manifest files."""

import os

import requests
from flask import Blueprint, Response, send_from_directory

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


@static_bp.route("/stats.js")
def stats_js():
    """Proxy the Umami tracking script."""
    try:
        response = requests.get("https://cloud.umami.is/script.js", timeout=10)
        response.raise_for_status()

        return Response(
            response.text,
            mimetype="application/javascript",
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Content-Type": "application/javascript",
            },
        )
    except requests.RequestException:
        # Return empty script if proxy fails
        return Response(
            "// Umami tracking script unavailable", mimetype="application/javascript"
        )
