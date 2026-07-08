"""Airspace service for managing airspace data in the xctsk-viewer Flask app."""

import os

from openair import parse_file

from app.model.openair_types import convert_raw_airspace
from app.utils.file_utils import get_default_airspace_path
from app.utils.geojson_converter import convert_airspace_to_geojson


class AirspaceService:
    """Service for managing airspace data."""

    def __init__(self, verbose=False):
        """Initialize the AirspaceService with optional verbosity."""
        self.verbose = verbose
        self._cached_airspaces = None
        self._cached_geojson = None
        self._current_filename = None

    def load_airspace_data(self, filepath=None):
        """Load and process airspace data from a file."""
        # Use provided filepath or default Switzerland file
        if filepath is None:
            filepath = get_default_airspace_path()

        # Only reload if filepath changed or no data cached, and the file exists
        if (
            self._cached_airspaces is None or self._current_filename != filepath
        ) and os.path.exists(filepath):
            try:
                if self.verbose:
                    print(f"Loading airspace data from: {filepath}")

                # Use the openair library to parse the file (returns raw dictionary data)
                raw_airspaces = parse_file(filepath)

                # Convert raw data to typed Airspace objects
                self._cached_airspaces = [
                    convert_raw_airspace(raw_data) for raw_data in raw_airspaces
                ]
                self._current_filename = filepath

                # Convert to GeoJSON for web display
                self._cached_geojson = convert_airspace_to_geojson(
                    self._cached_airspaces, verbose=self.verbose
                )

                if self.verbose:
                    print(
                        f"Loaded {len(self._cached_airspaces)} airspaces from {os.path.basename(filepath)}"
                    )
                    print(
                        f"Generated {len(self._cached_geojson['features'])} GeoJSON features"
                    )

                    # Debug: Print first airspace structure
                    if self._cached_airspaces:
                        self._print_debug_info()

            except Exception as e:
                print(f"Error loading airspace data: {e}")
                import traceback

                traceback.print_exc()
                self._cached_airspaces = []
                self._cached_geojson = {"type": "FeatureCollection", "features": []}
                self._current_filename = None

        elif not os.path.exists(filepath):
            print(f"File does not exist: {filepath}")
            # If the cached file doesn't exist, reset to default
            if filepath != get_default_airspace_path():
                return self.load_airspace_data()  # Recursive call with default file

        return self._cached_airspaces, self._cached_geojson

    def load_from_uploaded_file(self, filepath, original_filename):
        """Load airspace data from an uploaded file."""
        try:
            if self.verbose:
                print(f"Loading airspace data from uploaded file: {filepath}")
            raw_airspaces = parse_file(filepath)

            # Convert raw data to typed Airspace objects
            self._cached_airspaces = [
                convert_raw_airspace(raw_data) for raw_data in raw_airspaces
            ]

            # Convert to GeoJSON for web display
            self._cached_geojson = convert_airspace_to_geojson(
                self._cached_airspaces, verbose=self.verbose
            )

            # Set current filename to the original filename for display
            self._current_filename = original_filename

            if self.verbose:
                print(
                    f"Loaded {len(self._cached_airspaces)} airspaces from {original_filename}"
                )
                print(
                    f"Generated {len(self._cached_geojson['features'])} GeoJSON features"
                )

            return True, None

        except Exception as e:
            print(f"Error parsing uploaded file: {e}")
            import traceback

            traceback.print_exc()
            return False, str(e)

    def reset_to_default(self):
        """Reset to default airspace data."""
        self._cached_airspaces = None
        self._cached_geojson = None
        self._current_filename = None

    def get_cached_data(self):
        """Get currently cached airspace and GeoJSON data."""
        if self._cached_airspaces is not None and self._cached_geojson is not None:
            return self._cached_airspaces, self._cached_geojson
        else:
            return self.load_airspace_data()

    def get_current_filename(self):
        """Get the current filename being displayed."""
        return (
            os.path.basename(self._current_filename)
            if self._current_filename
            else os.path.basename(get_default_airspace_path())
        )

    def get_airspace_stats(self):
        """Get airspace statistics."""
        airspaces, _ = self.get_cached_data()

        # Count airspaces by class using typed objects
        class_counts: dict[str, int] = {}
        for airspace in airspaces:
            airspace_class = airspace.airspace_class
            class_counts[airspace_class] = class_counts.get(airspace_class, 0) + 1

        return {"total_airspaces": len(airspaces), "classes": class_counts}

    def _print_debug_info(self):
        """Print debug information about the first airspace."""
        print("First airspace structure:")
        assert self._cached_airspaces is not None
        first_airspace = self._cached_airspaces[0]
        print(f"Name: {first_airspace.name}")
        print(f"Class: {first_airspace.airspace_class}")
        print(f"Lower: {first_airspace.lower_bound.to_text()}")
        print(f"Upper: {first_airspace.upper_bound.to_text()}")
        print(f"Geometry type: {type(first_airspace.geom).__name__}")


# Global service instance
airspace_service = None


def get_airspace_service():
    """Get the global airspace service instance."""
    global airspace_service
    if airspace_service is None:
        from flask import current_app

        verbose = current_app.config.get("VERBOSE", False)
        airspace_service = AirspaceService(verbose=verbose)
    return airspace_service
