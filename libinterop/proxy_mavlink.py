
from pymavlink import mavutil
def mavlink_latlon(degrees):
    """Converts a MAVLink packet lat/lon degree format to decimal degrees."""
    return float(degrees) / 1e7


def mavlink_alt(dist):
    """Converts a MAVLink packet millimeter format to decimal feet."""
    return dist * 0.00328084


def mavlink_heading(heading):
    """Converts a MAVLink packet heading format to decimal degrees."""
    return heading / 100.0
