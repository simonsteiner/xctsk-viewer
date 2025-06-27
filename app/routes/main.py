from flask import (
    Blueprint,
    render_template,
    abort,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename
from app.services import XCTSKService
import logging
import os
import tempfile

bp = Blueprint("main", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    return show_task_view()


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/xctsk/view")
def show_task_view():
    """Handle task code form submission or show empty form."""
    task_code = request.args.get("taskCode", "").strip()

    if not task_code:
        # Show empty form
        return render_template("task_viewer.html", task_code=None, task_data=None)

    # Redirect to the task-specific route
    return load_task(task_code)


@bp.route("/xctsk/view/<task_code>")
def load_task(task_code):
    """Load and display an XCTSK task by task code."""
    if not task_code or not task_code.strip():
        return render_template(
            "task_viewer.html",
            task_code=task_code,
            task_data=None,
            error_message="Invalid task code provided.",
        )

    # Initialize the XCTSK service
    xctsk_service = XCTSKService()

    try:
        # Load and process the task
        success, message, task_data, status_code = xctsk_service.load_and_process_task(
            task_code
        )

        if not success:
            if status_code == 404:
                logger.warning(f"Task not found: {task_code}")
                # Return the template with task_data=None to show the error message
                return render_template(
                    "task_viewer.html",
                    task_code=task_code,
                    task_data=None,
                    error_message=message,
                )
            else:
                logger.error(f"Failed to load task {task_code}: {message}")
                return render_template(
                    "task_viewer.html",
                    task_code=task_code,
                    task_data=None,
                    error_message=f"Failed to load task: {message}",
                )

        # Render the task template with the processed data
        return render_template(
            "task_viewer.html",
            task_code=task_code,
            task_data=task_data,
            message=message,
        )

    except Exception as e:
        logger.error(f"Unexpected error loading task {task_code}: {str(e)}")
        return render_template(
            "task_viewer.html",
            task_code=task_code,
            task_data=None,
            error_message="An unexpected error occurred while loading the task.",
        )


@bp.route("/xctsk/upload", methods=["GET", "POST"])
def upload_task():
    """Handle XCTSK file upload."""
    if request.method == "GET":
        return render_template(
            "task_viewer.html", task_code=None, task_data=None, show_upload=True
        )

    # Handle POST - file upload
    if "xctsk_file" not in request.files:
        flash("No file selected", "danger")
        return render_template(
            "task_viewer.html", task_code=None, task_data=None, show_upload=True
        )

    file = request.files["xctsk_file"]

    if file.filename == "":
        flash("No file selected", "danger")
        return render_template(
            "task_viewer.html", task_code=None, task_data=None, show_upload=True
        )

    if not file.filename.lower().endswith(".xctsk"):
        flash("Please upload a valid .xctsk file", "danger")
        return render_template(
            "task_viewer.html", task_code=None, task_data=None, show_upload=True
        )

    try:
        # Read file content
        file_content = file.read().decode("utf-8")

        # Initialize the XCTSK service
        xctsk_service = XCTSKService()

        # Process the uploaded file content
        success, message, task_data = xctsk_service.process_task_data(file_content)

        if not success:
            flash(f"Error processing XCTSK file: {message}", "danger")
            return render_template(
                "task_viewer.html", task_code=None, task_data=None, show_upload=True
            )

        # Generate a display name from filename
        filename = secure_filename(file.filename)
        task_display_name = filename.replace(".xctsk", "")

        # Render the task template with the processed data
        return render_template(
            "task_viewer.html",
            task_code=task_display_name,
            task_data=task_data,
            message=f"Successfully loaded XCTSK file: {filename}",
            is_upload=True,
        )

    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        flash(f"Error processing file: {str(e)}", "danger")
        return render_template(
            "task_viewer.html", task_code=None, task_data=None, show_upload=True
        )
