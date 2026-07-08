"""API routes for airspace data (OpenAir) in the xctsk-viewer app."""

import logging
import tempfile
import traceback

from flask import Blueprint, Response, jsonify, request

from app.services.airspace_service import get_airspace_service
from app.utils.file_utils import (
    allowed_file,
    cleanup_temp_file,
    get_secure_filepath,
)

airspace_bp = Blueprint("airspace", __name__)

logger = logging.getLogger(__name__)

# OpenAir airspace files may use any of these extensions
ALLOWED_AIRSPACE_EXTENSIONS = {"txt", "air", "openair"}


def _error(message: str, status: int = 500, trace: bool = False) -> Response:
    """Build a standardized JSON error response."""
    body = {"error": message}
    if trace:
        body["stacktrace"] = traceback.format_exc()
    return Response(
        jsonify(body).get_data(as_text=False),
        status=status,
        mimetype="application/json",
    )


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
        return _error(str(e), trace=True)


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
        return _error(str(e), trace=True)


@airspace_bp.route("/api/airspaces/upload", methods=["POST"])
def upload_airspaces() -> Response:
    """Load a user-supplied OpenAir file as the active airspace dataset.

    Expects a multipart form with a ``file`` field (.txt/.air/.openair). The
    file replaces the cached dataset served by ``GET /api/airspaces``.

    Returns:
        Response: JSON with ``filename`` and ``count`` on success, or an error
        message with status 400 (bad request/file) or 500 (parse failure).
    """
    if "file" not in request.files:
        return _error("No file provided.", status=400)

    file = request.files["file"]
    if not file.filename:
        return _error("No file selected.", status=400)

    if not allowed_file(file.filename, ALLOWED_AIRSPACE_EXTENSIONS):
        return _error(
            "Invalid file type. Please upload a .txt, .air or .openair file.",
            status=400,
        )

    filepath = get_secure_filepath(file.filename, tempfile.gettempdir())
    try:
        file.save(filepath)
        service = get_airspace_service()
        success, error_msg = service.load_from_uploaded_file(filepath, file.filename)
        if not success:
            return _error(f"Error parsing file: {error_msg}", status=400)

        airspaces, _ = service.get_cached_data()
        return jsonify(
            {
                "filename": service.get_current_filename(),
                "count": len(airspaces or []),
            }
        )
    except Exception as e:
        logger.error(f"Error uploading airspace file: {e}")
        return _error(str(e), trace=True)
    finally:
        cleanup_temp_file(filepath)


@airspace_bp.route("/api/airspaces/reset", methods=["POST"])
def reset_airspaces() -> Response:
    """Reset the active airspace dataset back to the bundled default.

    Returns:
        Response: JSON with the default ``filename`` and airspace ``count``,
        or an error message with status 500.
    """
    try:
        service = get_airspace_service()
        service.reset_to_default()
        airspaces, _ = service.get_cached_data()
        return jsonify(
            {
                "filename": service.get_current_filename(),
                "count": len(airspaces or []),
            }
        )
    except Exception as e:
        logger.error(f"Error resetting airspace data: {e}")
        return _error(str(e), trace=True)
