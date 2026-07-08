"""API routes for airspace data (OpenAir) in the xctsk-viewer app."""

import logging
import traceback

from flask import Blueprint, Response, jsonify

from app.services.airspace_service import get_airspace_service

airspace_bp = Blueprint("airspace", __name__)

logger = logging.getLogger(__name__)


@airspace_bp.route("/api/airspaces", methods=["GET"])
def get_airspaces() -> Response:
    """Return the cached airspace data as a GeoJSON FeatureCollection.

    Returns:
        Response: JSON GeoJSON FeatureCollection, or an error message with
        status 500 if the airspace data could not be loaded.
    """
    try:
        service = get_airspace_service()
        _, geojson = service.get_cached_data()
        return jsonify(geojson)
    except Exception as e:
        logger.error(f"Error loading airspace data: {e}")
        return Response(
            jsonify({"error": str(e), "stacktrace": traceback.format_exc()}).get_data(
                as_text=False
            ),
            status=500,
            mimetype="application/json",
        )


@airspace_bp.route("/api/airspaces/stats", methods=["GET"])
def get_airspace_stats() -> Response:
    """Return airspace statistics (total count and per-class counts).

    Returns:
        Response: JSON object with ``total_airspaces`` and ``classes``, plus the
        current source filename, or an error message with status 500.
    """
    try:
        service = get_airspace_service()
        stats = service.get_airspace_stats()
        stats["filename"] = service.get_current_filename()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error computing airspace stats: {e}")
        return Response(
            jsonify({"error": str(e), "stacktrace": traceback.format_exc()}).get_data(
                as_text=False
            ),
            status=500,
            mimetype="application/json",
        )
