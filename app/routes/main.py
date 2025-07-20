"""Main application routes for the XCTSK viewer.

This module handles the main routes for viewing and uploading XCTSK tasks,
including rendering the task viewer, handling file uploads, and displaying
task-specific views.
"""

import logging

from flask import Blueprint, render_template, request

from app.utils import (
    handle_file_upload_errors,
    process_uploaded_xctsk_file,
    process_xctsk_task,
    render_task_viewer,
    validate_xctsk_file,
)

bp = Blueprint("main", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """Handle the root route and render the main task viewer page."""
    return show_task_view()


@bp.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html")


@bp.route("/xctsk/view")
def show_task_view():
    """Handle task code form submission or show empty form."""
    task_code = request.args.get("taskCode", "").strip()

    if not task_code:
        # Show empty form
        return render_task_viewer()

    # Redirect to the task-specific route
    return load_task(task_code)


@bp.route("/xctsk/view/<task_code>")
def load_task(task_code):
    """Load and display an XCTSK task by task code."""
    if not task_code or not task_code.strip():
        return render_task_viewer(
            task_code=task_code, error_message="Invalid task code provided."
        )

    # Process the task using utility function
    success, response = process_xctsk_task(task_code)
    return response


@bp.route("/xctsk/upload", methods=["GET", "POST"])
def upload_task():
    """Handle XCTSK file upload."""
    if request.method == "GET":
        return render_task_viewer(show_upload=True)

    # Handle POST - file upload
    if "xctsk_file" not in request.files:
        return handle_file_upload_errors("No file selected")

    file = request.files["xctsk_file"]

    # Validate the file
    is_valid, error_message = validate_xctsk_file(file)
    if not is_valid:
        return handle_file_upload_errors(error_message)

    try:
        # Read file content
        file_content = file.read().decode("utf-8")

        # Process the uploaded file using utility function
        success, response = process_uploaded_xctsk_file(file_content, file.filename)
        return response

    except Exception as e:
        logger.error(f"Error reading uploaded file: {str(e)}")
        return handle_file_upload_errors(f"Error reading file: {str(e)}")
