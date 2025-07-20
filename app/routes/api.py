"""API routes for XCTSK viewer (QR code, etc)."""

import logging

from flask import Blueprint, Response, jsonify
from pyxctsk import generate_qrcode_image

from app.services.xctsk_service import XCTSKService

api_bp = Blueprint("api", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@api_bp.route("/api/xctsk/<task_code>", methods=["GET"])
def api_task_data(task_code):
    """API endpoint to fetch XCTSK task data as JSON for a given task code.

    Args:
        task_code (str): The unique code identifying the XCTSK task.

    Returns:
        Response: JSON response containing the task data if found, or an error message with appropriate status code.
    """
    if not task_code or not task_code.strip():
        return jsonify({"error": "Invalid task code provided."}), 400

    try:
        service = XCTSKService()
        task_data = service.get_task_data_by_code(task_code)
        if not task_data:
            return jsonify({"error": "Task not found or invalid."}), 404
        return jsonify(task_data)
    except Exception as e:
        logger.error(f"Error fetching task data for API: {str(e)}")
        return jsonify({"error": f"Error fetching task data: {str(e)}"}), 500


@api_bp.route("/api/qrcode_image/qrcode_<task_code>.png")
def qrcode_image(task_code: str) -> Response:
    """API endpoint to generate and return a PNG QR code image for the given XCTSK task.

    Args:
        task_code (str): The unique code identifying the XCTSK task whose QR code should be generated.

    Returns:
        Response: Flask response containing the PNG image of the QR code if successful, or a JSON error message with appropriate status code if not.
    """

    def error_response(message, status=500, stacktrace=None):
        body = {"error": message}
        if stacktrace:
            body["stacktrace"] = stacktrace
        return Response(
            jsonify(body).get_data(as_text=False),
            status=status,
            mimetype="application/json",
        )

    try:
        service = XCTSKService()
        task_data = service.get_task_data_by_code(task_code)
    except Exception as e:
        import traceback

        return error_response(
            f"Error fetching task data: {str(e)}", stacktrace=traceback.format_exc()
        )

    if not task_data:
        return error_response("Task not found or invalid.", status=404)

    task_name = task_data.get("name", f"task_{task_code}")
    if "qr_code" not in task_data:
        return error_response("No qr_code found in task data")
    qr_string = task_data.get("qr_code")
    if not qr_string:
        return error_response("QR code string is empty or missing")

    try:
        img = generate_qrcode_image(qr_string, size=512)
        from io import BytesIO

        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(
            buf.getvalue(),
            mimetype="image/png",
            headers={"Content-Disposition": f"inline; filename={task_name}.png"},
        )
    except Exception as e:
        import traceback

        return error_response(
            f"Error generating QR code image: {str(e)}",
            stacktrace=traceback.format_exc(),
        )
