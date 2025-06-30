#!/usr/bin/env python3

import logging
from flask import render_template, flash
from werkzeug.utils import secure_filename
from app.services import XCTSKService

logger = logging.getLogger(__name__)


def render_task_viewer(
    task_code=None,
    task_data=None,
    error_message=None,
    message=None,
    show_upload=False,
    is_upload=False,
):
    """
    Centralized function to render task_viewer.html with consistent parameters.

    Args:
        task_code: The task code to display
        task_data: The processed task data
        error_message: Error message to display
        message: Success message to display
        show_upload: Whether to show upload form
        is_upload: Whether this is from an upload operation

    Returns:
        Rendered template response
    """
    return render_template(
        "task_viewer.html",
        task_code=task_code,
        task_data=task_data,
        error_message=error_message,
        message=message,
        show_upload=show_upload,
        is_upload=is_upload,
    )


def validate_xctsk_file(file):
    """
    Validate uploaded XCTSK file.

    Args:
        file: Flask file object from request.files

    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or file.filename == "":
        return False, "No file selected"

    if not file.filename.lower().endswith(".xctsk"):
        return False, "Please upload a valid .xctsk file"

    return True, None


def process_xctsk_task(task_code, xctsk_service=None):
    """
    Process XCTSK task with consistent error handling.

    Args:
        task_code: The task code to process
        xctsk_service: Optional XCTSKService instance (will create if None)

    Returns:
        tuple: (success, template_response)
    """
    if not xctsk_service:
        xctsk_service = XCTSKService()

    try:
        success, message, task_data, status_code = xctsk_service.load_and_process_task(
            task_code
        )

        if not success:
            if status_code == 404:
                logger.warning(f"Task not found: {task_code}")
                return False, render_task_viewer(
                    task_code=task_code, error_message=message
                )
            else:
                logger.error(f"Failed to load task {task_code}: {message}")
                return False, render_task_viewer(
                    task_code=task_code, error_message=f"Failed to load task: {message}"
                )

        # Success case
        return True, render_task_viewer(
            task_code=task_code, task_data=task_data, message=message
        )

    except Exception as e:
        logger.error(f"Unexpected error loading task {task_code}: {str(e)}")
        return False, render_task_viewer(
            task_code=task_code,
            error_message="An unexpected error occurred while loading the task.",
        )


def process_uploaded_xctsk_file(file_content, filename, xctsk_service=None):
    """
    Process uploaded XCTSK file content.

    Args:
        file_content: The file content as string
        filename: Original filename
        xctsk_service: Optional XCTSKService instance (will create if None)

    Returns:
        tuple: (success, template_response)
    """
    if not xctsk_service:
        xctsk_service = XCTSKService()

    try:
        success, message, task_data = xctsk_service.process_task_data(file_content)

        if not success:
            flash(f"Error processing XCTSK file: {message}", "danger")
            return False, render_task_viewer(show_upload=True)

        # Generate display name from filename
        secure_name = secure_filename(filename)
        task_display_name = secure_name.replace(".xctsk", "")

        # Success case
        return True, render_task_viewer(
            task_code=task_display_name,
            task_data=task_data,
            message=f"Successfully loaded XCTSK file: {secure_name}",
            is_upload=True,
        )

    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        flash(f"Error processing file: {str(e)}", "danger")
        return False, render_task_viewer(show_upload=True)


def handle_file_upload_errors(error_message):
    """
    Handle file upload errors with consistent flash messaging.

    Args:
        error_message: The error message to flash

    Returns:
        Template response with upload form
    """
    flash(error_message, "danger")
    return render_task_viewer(show_upload=True)
