"""OpenAir types and data structures for the Airspace Viewer application."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class AltitudeType(Enum):
    """Enumeration of altitude reference types used in OpenAir airspace definitions."""

    GND = "Gnd"
    FEET_AMSL = "FeetAmsl"
    FEET_AGL = "FeetAgl"
    FLIGHT_LEVEL = "FlightLevel"
    UNLIMITED = "Unlimited"
    OTHER = "Other"


@dataclass
class Altitude:
    """Represents an altitude value and its reference type.

    Attributes:
        type (AltitudeType): The reference type of the altitude (e.g., GND, FEET_AMSL).
        val (Union[int, float, str, None]): The altitude value, which may be feet, flight level, or other.
    """

    type: AltitudeType
    val: Union[int, float, str, None] = None

    def to_text(self) -> str:
        """Convert the altitude to a human-readable string.

        Returns:
            str: The altitude as a formatted string, e.g., '1200 m AMSL', 'FL 75', 'GND', etc.
        """
        from app.utils.units import feet_to_meters

        if self.type == AltitudeType.GND:
            return "GND"
        elif self.type == AltitudeType.FEET_AMSL:
            val = self.val
            if val is None or val == "":
                meters = 0
            else:
                try:
                    if isinstance(val, (int, float)):
                        meters = int(feet_to_meters(val))
                    else:
                        meters = int(feet_to_meters(float(val)))
                except (TypeError, ValueError):
                    meters = 0
            return f"{meters} m AMSL"
        elif self.type == AltitudeType.FEET_AGL:
            val = self.val
            if val is None or val == "":
                meters = 0
            else:
                try:
                    if isinstance(val, (int, float)):
                        meters = int(feet_to_meters(val))
                    else:
                        meters = int(feet_to_meters(float(val)))
                except (TypeError, ValueError):
                    meters = 0
            return f"{meters} m AGL"
        elif self.type == AltitudeType.FLIGHT_LEVEL:
            return f"FL {self.val}"
        elif self.type == AltitudeType.UNLIMITED:
            return "Unlimited"
        elif self.type == AltitudeType.OTHER:
            return f"?({self.val})"
        else:
            return str(self.val) if self.val else "Unknown"


@dataclass
class Point:
    """Represents a geographical point (latitude, longitude).

    Attributes:
        type (str): The geometry type, always 'Point'.
        lat (float): Latitude in decimal degrees.
        lng (float): Longitude in decimal degrees.
    """

    type: str = "Point"
    lat: float = 0.0
    lng: float = 0.0


@dataclass
class Arc:
    """Represents an arc segment defined by center, start, end, and direction.

    Attributes:
        type (str): The geometry type, always 'Arc'.
        center (Optional[Point]): The center point of the arc.
        start (Optional[Point]): The start point of the arc.
        end (Optional[Point]): The end point of the arc.
        direction (str): Arc direction, 'CW' (clockwise) or 'CCW' (counterclockwise).
    """

    type: str = "Arc"
    center: Optional[Point] = None
    start: Optional[Point] = None
    end: Optional[Point] = None
    direction: str = "CW"  # CW or CCW


@dataclass
class ArcSegment:
    """Represents an arc segment defined by center, radius, angles, and direction.

    Attributes:
        type (str): The geometry type, always 'ArcSegment'.
        center (Optional[Point]): The center point of the arc.
        radius (float): The radius of the arc.
        start_angle (float): The starting angle in degrees.
        end_angle (float): The ending angle in degrees.
        direction (str): Arc direction, 'CW' or 'CCW'.
    """

    type: str = "ArcSegment"
    center: Optional[Point] = None
    radius: float = 0.0
    start_angle: float = 0.0
    end_angle: float = 0.0
    direction: str = "CW"


# Union type for polygon segments
PolygonSegment = Union[Point, Arc, ArcSegment]


@dataclass
class PolygonGeometry:
    """Represents a polygon geometry composed of segments (points/arcs).

    Attributes:
        type (str): The geometry type, always 'Polygon'.
        segments (Optional[List[PolygonSegment]]): List of polygon segments (Point, Arc, ArcSegment).
    """

    type: str = "Polygon"
    segments: Optional[List[PolygonSegment]] = None

    def __post_init__(self):
        """Initializes segments to an empty list if not provided."""
        if self.segments is None:
            self.segments = []


@dataclass
class CircleGeometry:
    """Represents a circle geometry defined by center and radius.

    Attributes:
        type (str): The geometry type, always 'Circle'.
        centerpoint (Optional[List[float]]): Center point as [lat, lng].
        radius (float): Radius in nautical miles.
    """

    type: str = "Circle"
    centerpoint: Optional[List[float]] = None  # [lat, lng]
    radius: float = 0.0  # in nautical miles

    def __post_init__(self):
        """Initializes centerpoint to [0.0, 0.0] if not provided."""
        if self.centerpoint is None:
            self.centerpoint = [0.0, 0.0]


# Union type for geometries
AirspaceGeometry = Union[PolygonGeometry, CircleGeometry]


@dataclass
class Airspace:
    """Represents an airspace with name, class, bounds, and geometry.

    Attributes:
        name (str): The name of the airspace.
        class_ (str): The airspace class (e.g., 'C', 'D').
        lower_bound (Optional[Altitude]): The lower altitude bound.
        upper_bound (Optional[Altitude]): The upper altitude bound.
        geom (Optional[AirspaceGeometry]): The geometry of the airspace.
    """

    name: str = ""
    class_: str = ""  # Using class_ to avoid Python keyword conflict
    lower_bound: Optional[Altitude] = None
    upper_bound: Optional[Altitude] = None
    geom: Optional[AirspaceGeometry] = None

    def __post_init__(self):
        """Initializes lower and upper bounds to defaults if not provided."""
        if self.lower_bound is None:
            self.lower_bound = Altitude(AltitudeType.GND)
        if self.upper_bound is None:
            self.upper_bound = Altitude(AltitudeType.UNLIMITED)

    @property
    def airspace_class(self) -> str:
        """Returns the airspace class.

        Returns:
            str: The airspace class (e.g., 'C', 'D').
        """
        return self.class_

    def set_airspace_class(self, value: str):
        """Sets the airspace class.

        Args:
            value (str): The airspace class to set (e.g., 'C', 'D').
        """
        self.class_ = value


def convert_raw_airspace(raw_data: Dict[str, Any]) -> Airspace:
    """Converts a raw dictionary to an Airspace object.

    Args:
        raw_data (Dict[str, Any]): The raw airspace data as a dictionary.

    Returns:
        Airspace: The constructed Airspace object.
    """

    def parse_altitude(alt_data) -> Altitude:
        """Parses altitude data from a dictionary.

        Args:
            alt_data (Any): The altitude data, typically a dict with 'type' and 'val'.

        Returns:
            Altitude: The constructed Altitude object.
        """
        if isinstance(alt_data, dict):
            alt_type_str = alt_data.get("type", "Gnd")
            try:
                alt_type = AltitudeType(alt_type_str)
            except ValueError:
                alt_type = AltitudeType.OTHER
            return Altitude(type=alt_type, val=alt_data.get("val"))
        return Altitude(AltitudeType.GND)

    def parse_geometry(geom_data) -> AirspaceGeometry:
        """Parses geometry data from a dictionary.

        Args:
            geom_data (Any): The geometry data, typically a dict with 'type' and segment info.

        Returns:
            AirspaceGeometry: The constructed geometry object (PolygonGeometry or CircleGeometry).
        """
        if not isinstance(geom_data, dict):
            return PolygonGeometry()

        geom_type = geom_data.get("type", "Polygon")

        if geom_type == "Circle":
            return CircleGeometry(
                type=geom_type,
                centerpoint=geom_data.get("centerpoint", [0.0, 0.0]),
                radius=geom_data.get("radius", 0.0),
            )
        else:  # Polygon
            segments: List[PolygonSegment] = []
            for seg_data in geom_data.get("segments", []):
                if isinstance(seg_data, dict):
                    seg_type = seg_data.get("type", "Point")
                    if seg_type == "Point":
                        segments.append(
                            Point(
                                type=seg_type,
                                lat=seg_data.get("lat", 0.0),
                                lng=seg_data.get("lng", 0.0),
                            )
                        )
                    # Add Arc and ArcSegment parsing as needed

            return PolygonGeometry(
                type=geom_type, segments=segments if segments else None
            )

    return Airspace(
        name=raw_data.get("name", ""),
        class_=raw_data.get("class", ""),
        lower_bound=parse_altitude(raw_data.get("lowerBound", {})),
        upper_bound=parse_altitude(raw_data.get("upperBound", {})),
        geom=parse_geometry(raw_data.get("geom", {})),
    )
