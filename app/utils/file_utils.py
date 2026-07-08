"""File utilities for handling file uploads and paths in the xctsk-viewer app."""

import os

from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """Check if uploaded file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def get_secure_filepath(filename, upload_folder):
    """Get secure filepath for uploaded file."""
    filename = secure_filename(filename)
    return os.path.join(upload_folder, filename)


def cleanup_temp_file(filepath):
    """Clean up temporary file safely."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not remove temp file {filepath}: {e}")


def get_default_airspace_path():
    """Get path to default airspace file."""
    return os.path.join(os.path.dirname(__file__), "..", "examples", "Switzerland.txt")
