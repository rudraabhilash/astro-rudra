# 🧠 Design
# Input: {planet_name: sign_name}
# Output: (overlap_start_IST, overlap_end_IST) or None
# Timezone: New Delhi (IST)
# Zodiac: Sidereal (Lahiri)

# planetary_overlap.py

import swisseph as swe
from datetime import datetime, timedelta
import pytz

# =========================
# CONFIGURATION
# =========================

swe.set_sid_mode(swe.SIDM_LAHIRI)

IST = pytz.timezone("Asia/Kolkata")
UTC = pytz.UTC

SIGN_SIZE = 30.0  # degrees per sign

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Ketu": swe.MEAN_NODE,  # handled specially
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_INDEX = {name: i for i, name in enumerate(SIGNS)}

# =========================
# CORE HELPERS
# =========================

def julian_day(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600
    )


def planet_longitude(dt_utc: datetime, planet: str) -> float:
    jd = julian_day(dt_utc)

    if planet == "Ketu":
        lonlat, flags = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
        lon, lat, distance, speed_lon, speed_lat, speed_distance = lonlat
        return (lon + 180) % 360

    lon, _ = swe.calc_ut(jd, PLANETS[planet], swe.FLG_SIDEREAL)
    return lon % 360


def sign_of_longitude(lon: float) -> int:
    return int(lon // SIGN_SIZE)


# =========================
# FIND ENTRY / EXIT WINDOW
# =========================

def find_sign_window(
    planet: str,
    target_sign: str,
    start_dt_utc: datetime,
    end_dt_utc: datetime,
    step_minutes: int
):
    print(f"Finding window for {planet} in {target_sign} from {start_dt_utc} to {end_dt_utc}")
    target_idx = SIGN_INDEX[target_sign]

    t = start_dt_utc
    prev_sign = sign_of_longitude(planet_longitude(t, planet))
    # print(f'Initial prev_sign: {prev_sign}')
    entry = exit_ = None

    while t <= end_dt_utc:
        lon = planet_longitude(t, planet)
        current_sign = sign_of_longitude(lon)
        print(f'current_sign: {current_sign}')

        # Entry
        if entry is None and current_sign == target_idx and prev_sign != target_idx:
            entry = t

        # Exit
        if entry is not None and current_sign != target_idx and prev_sign == target_idx:
            exit_ = t
            break

        prev_sign = current_sign
        t += timedelta(minutes=step_minutes)

    if entry and exit_:
        return (
            entry.astimezone(IST),
            exit_.astimezone(IST)
        )

    # Debugging output
    print(f"Entry: {entry}, Exit: {exit_}")
    print(f"Could not find complete window for {planet} in {target_sign}")
    return None


# =========================
# MAIN OVERLAP FUNCTION
# =========================

def compute_overlap(
    planet_sign_map: dict,
    year: int,
    search_padding_days: int = 60
):
    """
    planet_sign_map example:
    {
        "Mercury": "Aquarius",
        "Sun": "Aquarius",
        "Moon": "Pisces",
        "Mars": "Sagittarius",
        ...
    }
    """

    start_utc = datetime(year, 1, 1, tzinfo=UTC) - timedelta(days=search_padding_days)
    end_utc = datetime(year, 12, 31, tzinfo=UTC) + timedelta(days=search_padding_days)

    windows = {}

    for planet, sign in planet_sign_map.items():
        step = 2 if planet == "Moon" else 10  # Moon needs higher resolution

        window = find_sign_window(
            planet,
            sign,
            start_utc,
            end_utc,
            step_minutes=step
        )

        if not window:
            print(f"No window found for {planet} in sign {sign}")
            return None

        windows[planet] = window

    overlap_start = max(w[0] for w in windows.values())
    overlap_end = min(w[1] for w in windows.values())

    if overlap_start < overlap_end:
        return overlap_start, overlap_end

    return None
