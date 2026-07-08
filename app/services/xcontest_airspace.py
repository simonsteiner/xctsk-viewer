"""Fetch airspace data from the public airspace.xcontest.org API.

The site's OpenAir *export* endpoint requires a logged-in account, but the
public ``/api/v6`` API (used by the map itself) serves the same airspace data
as JSON without authentication. This module resolves the "COMP CH" channel to
its current file(s) and adapts the JSON into the raw-dict shape consumed by
:func:`app.model.openair_types.convert_raw_airspace`, so the data flows through
the same pipeline as an uploaded OpenAir file.
"""

from typing import Any, Dict, List, Tuple

import requests

BASE_URL = "https://airspace.xcontest.org"
COMP_CH_CHANNEL = "COMP CH"
REQUEST_TIMEOUT = 15  # seconds

# xcontest airspace class -> our colour-scheme class (others pass through)
_CLASS_MAP = {"R": "Restricted", "P": "Prohibited"}


def _get_json(path: str) -> Any:
    """GET ``path`` from the xcontest API and return the parsed JSON."""
    resp = requests.get(f"{BASE_URL}{path}", timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def resolve_comp_ch_files() -> List[Tuple[int, str]]:
    """Return ``(oaid, name)`` for every file in the COMP CH channel.

    Returns:
        A list of (oaid, name) tuples. Empty if the channel has no files.
    """
    files = _get_json("/api/v6/files")
    return [
        (f["oaid"], f.get("name", ""))
        for f in files
        if f.get("channame") == COMP_CH_CHANNEL
    ]


def _map_class(airclass: str | None) -> str:
    """Map an xcontest airspace class to our colour-scheme class."""
    return _CLASS_MAP.get(airclass or "", airclass or "")


def _map_altitude(limit: Dict[str, Any] | None) -> Dict[str, Any]:
    """Map an xcontest ``{hfeet, htype}`` limit to a raw altitude dict."""
    if not limit:
        return {"type": "Gnd"}
    htype = (limit.get("htype") or "").upper()
    hfeet = limit.get("hfeet")
    if htype == "FL":
        return {
            "type": "FlightLevel",
            "val": int(round(hfeet / 100)) if hfeet is not None else None,
        }
    if htype == "AGL":
        return {"type": "FeetAgl", "val": hfeet}
    if htype in ("AMSL", "AGL/AMSL"):
        return {"type": "FeetAmsl", "val": hfeet}
    if htype in ("GND", "") and hfeet in (0, None):
        return {"type": "Gnd"}
    return {"type": "FeetAmsl", "val": hfeet}


def _adapt_airspace(airspace: Dict[str, Any]) -> Dict[str, Any]:
    """Adapt one xcontest airspace dict to the openair-rs-py raw-dict shape."""
    polygon = airspace.get("polygon") or []
    return {
        "name": airspace.get("name", ""),
        "class": _map_class(airspace.get("airclass")),
        "lowerBound": _map_altitude(airspace.get("lowerLimit")),
        "upperBound": _map_altitude(airspace.get("upperLimit")),
        "geom": {
            "type": "Polygon",
            "segments": [
                {"type": "Point", "lat": point[0], "lng": point[1]}
                for point in polygon
                if len(point) >= 2
            ],
        },
    }


def fetch_comp_ch() -> Tuple[List[Dict[str, Any]], str]:
    """Fetch the current COMP CH airspaces from xcontest.

    Returns:
        A tuple of (raw_airspaces, label) where ``raw_airspaces`` is a list of
        dicts ready for :func:`convert_raw_airspace` and ``label`` names the
        source (e.g. ``"COMP CH: <competition name>"``).

    Raises:
        requests.RequestException: on network/HTTP failure.
        ValueError: if the COMP CH channel currently has no files.
    """
    files = resolve_comp_ch_files()
    if not files:
        raise ValueError("No files available in the COMP CH channel.")

    raw_airspaces: List[Dict[str, Any]] = []
    names: List[str] = []
    for oaid, name in files:
        data = _get_json(f"/api/v6/data/{oaid}")
        raw_airspaces.extend(_adapt_airspace(a) for a in data.get("airspaces", []))
        names.append(data.get("name") or name)

    label = f"{COMP_CH_CHANNEL}: {', '.join(n for n in names if n)}".rstrip(": ")
    return raw_airspaces, label
