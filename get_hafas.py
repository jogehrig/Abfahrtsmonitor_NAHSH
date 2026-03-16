# get_hafas.py
from datetime import datetime, timedelta
from pyhafas.client import HafasClient
from my_profiles.nahsh import NahSHProfile

def get_bus_departure_info():
    """
    Fetch bus departures for dashboard.

    Returns a dictionary with:
    - current_time: str, current HH:MM
    - leibniz_departures: list of next 10 valid buses from Leibnizstrasse with arrival at Uni-Hochhaus
    - x60_departures: list of next 10 Bus X60 to Fachhochschule with arrival at Seefischmarkt (>=29 min after departure)
    - other_departures: list of next 10 departures from Leibnizstrasse not in DEST_LINE_MAP
      and not going to 'Kiel Universität'
    """
    # Station IDs
    STATION_LEIBNIZSTRASSE = "9049148"
    STATION_UNI_HOCHHAUS = "9049283"
    STATION_SEEFISCHMARKT = "9049245"

    # Destination + valid lines map
    DEST_LINE_MAP = {
        "Wik": ["Bus 6"],
        "Suchsdorf": ["Bus 81"],
        "Russee": ["Bus 62", "Bus N62"],
        "Hassee": ["Bus 50"],
        "Mettenhof": ["Bus 61"],
        "Fachhochschule": ["Bus X60"],
        "Kiel Rankestraße": ["Bus 6"],
        "Kiel Hbf": ["Bus 81", "Bus N62", "Bus X60"],
    }

    client = HafasClient(NahSHProfile())
    now = datetime.now()

    # Fetch all departures from Leibnizstrasse
    departures = client.departures(STATION_LEIBNIZSTRASSE, now)

    # Next 10 valid departures from Leibnizstrasse
    valid_buses = [
        d for d in departures
        if DEST_LINE_MAP.get(d.direction) and d.name in DEST_LINE_MAP[d.direction]
    ][:10]

    deps_uni = client.departures(STATION_UNI_HOCHHAUS, now)
    leibniz_info = []
    for d in valid_buses:
        arrival_bus = next(
            (u for u in deps_uni
             if u.name == d.name
             and u.direction == d.direction
             and u.dateTime > d.dateTime),
            None
        )

        leibniz_info.append({
            "line": d.name,
            "destination": d.direction,
            "departure": d.dateTime.strftime("%H:%M"),
            "delay": f"+{d.delay} min" if d.delay else "on time",
            "cancelled": d.cancelled,
            "arrival_uni": arrival_bus.dateTime.strftime("%H:%M") if arrival_bus else None
        })

    # Next 10 Bus X60 to Fachhochschule with arrival >= 29 minutes after departure
    x60_raw = [
        d for d in departures
        if d.name == "Bus X60" and d.direction == "Fachhochschule"
    ][:10]

    deps_seefisch = client.departures(STATION_SEEFISCHMARKT, now)
    x60_info = []

    for d in x60_raw:
        min_arrival_time = d.dateTime + timedelta(minutes=29)

        arrival_bus = next(
            (s for s in deps_seefisch
             if s.name == d.name
             and s.direction == d.direction
             and s.dateTime >= min_arrival_time),
            None
        )

        x60_info.append({
            "departure": d.dateTime.strftime("%H:%M"),
            "delay": f"+{d.delay} min" if d.delay else "on time",
            "cancelled": d.cancelled,
            "arrival_seefisch": arrival_bus.dateTime.strftime("%H:%M") if arrival_bus else None
        })

    # Next 10 other departures excluding:
    #      - ones in DEST_LINE_MAP
    #      - any with direction "Kiel Universität"
    other_buses = [
        d for d in departures
        if not (DEST_LINE_MAP.get(d.direction) and d.name in DEST_LINE_MAP[d.direction])
        and "Universit" not in d.direction
    ][:10]

    other_info = [{
        "line": d.name,
        "destination": d.direction,
        "departure": d.dateTime.strftime("%H:%M"),
        "delay": f"+{d.delay} min" if d.delay else "on time",
        "cancelled": d.cancelled
    } for d in other_buses]

    # Return all data
    return {
        "current_time": now.strftime("%H:%M"),
        "leibniz_departures": leibniz_info,
        "x60_departures": x60_info,
        "other_departures": other_info
    }
