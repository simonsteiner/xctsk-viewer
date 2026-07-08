"""Units conversion utilities."""


def feet_to_meters(feet):
    """Convert feet to meters."""
    return feet * 0.3048


def meters_to_feet(meters):
    """Convert meters to feet."""
    return meters / 0.3048


def nautical_miles_to_meters(nm):
    """Convert nautical miles to meters."""
    return nm * 1852


def meters_to_nautical_miles(meters):
    """Convert meters to nautical miles."""
    return meters / 1852


def statute_miles_to_meters(miles):
    """Convert statute miles to meters."""
    return miles * 1609.344


def meters_to_statute_miles(meters):
    """Convert meters to statute miles."""
    return meters / 1609.344


def kilometers_to_meters(km):
    """Convert kilometers to meters."""
    return km * 1000


def meters_to_kilometers(meters):
    """Convert meters to kilometers."""
    return meters / 1000
