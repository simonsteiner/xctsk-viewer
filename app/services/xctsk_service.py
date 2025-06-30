"""
Service for handling XCTSK file operations including download and processing.
"""

from typing import Dict, Optional, Tuple, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import qrcode
import base64
from io import BytesIO

# Import pyxctsk functions
from app.lib.pyxctsk import parse_task, calculate_task_distances, generate_task_geojson


class XCTSKService:
    """Service for downloading and processing XCTSK files."""

    BASE_URL = "https://tools.xcontest.org"

    def __init__(self, timeout: int = 30, retry_count: int = 3):
        """Initialize the service with HTTP session configuration."""
        self.timeout = timeout
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=retry_count,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def download_task_data(
        self, task_code: str, version: int = 1
    ) -> Tuple[bool, str, Optional[str], Optional[int]]:
        """
        Download task data from XContest API.

        Args:
            task_code: The task code to download
            version: API version (1 or 2)
            Returns: Tuple of (success, message, task_data_string, status_code)
        """
        endpoint = (
            f"/api/xctsk/load/{task_code}"
            if version == 1
            else f"/api/xctsk/loadV2/{task_code}"
        )

        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}", timeout=self.timeout
            )

            if response.status_code == 200:
                # Return the raw text content, not parsed JSON
                # because parse_task expects a JSON string
                task_data_text = response.text
                return (
                    True,
                    f"Successfully downloaded task {task_code}",
                    task_data_text,
                    200,
                )
            elif response.status_code == 404:
                return (
                    False,
                    f"Task '<strong>{task_code}</strong>' not found. Please check the task code spelling and try again.",
                    None,
                    404,
                )
            else:
                return (
                    False,
                    f"Download failed with status {response.status_code}: {response.text}",
                    None,
                    response.status_code,
                )

        except requests.RequestException as e:
            return False, f"Network error downloading task {task_code}: {e}", None, None

    def process_task_data(self, task_data: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Process XCTSK task data using pyxctsk functions.

        Args:
            task_data: Raw task data string from XContest API

        Returns:
            Tuple of (success, message, processed_data)
        """
        try:
            # Parse the task
            task = parse_task(task_data)

            # Calculate distances - this returns all the turnpoint details we need
            distances = calculate_task_distances(task)

            # Generate GeoJSON
            geojson = generate_task_geojson(task)

            # Build task info using data from pyxctsk calculations
            task_info = {
                "task": task,
                "distances": distances,
                "geojson": geojson,
                "turnpoints": self._format_turnpoints_for_display(task, distances),
                "metadata": self._extract_task_metadata(task, distances),
            }

            # Generate QR code for the task
            qr_code_data = self.generate_qr_code(task)
            if qr_code_data:
                task_info["qr_code"] = qr_code_data

            return True, "Task processed successfully", task_info

        except Exception as e:
            return False, f"Error processing task data: {str(e)}", None

    def _format_utc_time(self, time_str: Optional[str]) -> Optional[str]:
        """
        Format a UTC time string (e.g., "09:30:00Z" or '"09:30:00Z"') as 'HH:MM (UTC)'.
        Returns None if input is None or invalid.
        """
        if not time_str:
            return None
        # Remove quotes if present
        if time_str.startswith('"') and time_str.endswith('"'):
            time_str = time_str[1:-1]
        try:
            parts = time_str.split(":")
            if len(parts) < 2:
                return None
            hour = int(parts[0])
            minute = int(parts[1])
            return f"{hour:02d}:{minute:02d} (UTC)"
        except Exception:
            return None

    def _extract_task_metadata(self, task, distances: Dict) -> Dict[str, Any]:
        """Extract task metadata from task object and distance calculations."""
        return {
            "task_distance_center": distances.get("center_distance_km", 0) * 1000,
            "task_distance_optimized": distances.get("optimized_distance_km", 0) * 1000,
            "earth_model": task.earth_model.value if task.earth_model else "Unknown",
            "task_type": task.task_type.value if task.task_type else "Unknown",
            "takeoff_open": self._format_utc_time(
                task.takeoff.time_open.to_json_string()
                if task.takeoff and task.takeoff.time_open
                else None
            ),
            "takeoff_close": self._format_utc_time(
                task.takeoff.time_close.to_json_string()
                if task.takeoff and task.takeoff.time_close
                else None
            ),
            "sss_time": self._format_utc_time(
                task.sss.time_gates[0].to_json_string()
                if task.sss and task.sss.time_gates
                else None
            ),
            "sss_type": (task.sss.type.value if task.sss and task.sss.type else None),
            "goal_deadline": self._format_utc_time(
                task.goal.deadline.to_json_string()
                if task.goal and task.goal.deadline
                else None
            ),
            "goal_type": (
                task.goal.type.value if task.goal and task.goal.type else "Unknown"
            ),
        }

    def _format_turnpoints_for_display(self, task, distances: Dict) -> List[Dict]:
        """Format turnpoints for display using data from distance calculations."""
        turnpoints = []

        if not task.turnpoints or not distances.get("turnpoints"):
            return turnpoints

        for i, tp_detail in enumerate(distances["turnpoints"]):
            # Get the corresponding task turnpoint
            tp = task.turnpoints[i] if i < len(task.turnpoints) else None

            # Determine display type and styling
            tp_type, table_class = self._determine_turnpoint_display_type(
                tp, i, len(distances["turnpoints"])
            )

            turnpoint_info = {
                "index": i + 1,
                "name": tp_detail.get("name", ""),
                "description": tp.waypoint.description if tp and tp.waypoint else "",
                "radius": tp_detail.get("radius", 0),
                "cumulative_distance_center": tp_detail.get("cumulative_center_km", 0),
                "cumulative_distance_optimized": tp_detail.get(
                    "cumulative_optimized_km", 0
                ),
                "type": tp_type,
                "table_class": table_class,
            }

            turnpoints.append(turnpoint_info)

        return turnpoints

    def _determine_turnpoint_display_type(
        self, tp, index: int, total_count: int
    ) -> Tuple[str, str]:
        """Determine the display type and CSS class for a turnpoint."""
        if tp and tp.type:
            tp_type_value = tp.type.value if hasattr(tp.type, "value") else str(tp.type)
            if tp_type_value == "TAKEOFF":
                return "Takeoff", ""
            elif tp_type_value == "SSS":
                return "SSS", "table-primary"
            elif tp_type_value == "ESS":
                return "ESS", "table-primary"
            else:
                return tp_type_value, ""

        # Fallback to position-based determination
        if index == 0:
            return "Takeoff", ""
        elif index == total_count - 1:
            return "Goal", "table-danger"
        else:
            return "Turnpoint", ""

    def load_and_process_task(
        self, task_code: str
    ) -> Tuple[bool, str, Optional[Dict], Optional[int]]:
        """
        Download and process a task in one operation.

        Args:
            task_code: The task code to load and process

        Returns:
            Tuple of (success, message, processed_task_data, status_code)
        """
        # Download task data
        success, message, task_data, status_code = self.download_task_data(task_code)
        if not success:
            return success, message, None, status_code

        # Process task data
        process_success, process_message, processed_data = self.process_task_data(
            task_data
        )
        return process_success, process_message, processed_data, status_code

    def generate_qr_code(self, task) -> Optional[str]:
        """
        Generate a QR code for the task in XCTSK format.

        Args:
            task: The task object to generate QR code for

        Returns:
            Base64 encoded PNG image data or None if generation fails
        """
        try:
            # Convert task to QR code format
            qr_task = task.to_qr_code_task()
            qr_string = qr_task.to_string()

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(qr_string)
            qr.make(fit=True)

            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64 string
            buffer = BytesIO()
            qr_image.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return img_str

        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
