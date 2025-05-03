import re
from datetime import datetime

def parse_target_command(text):
    pattern = (
        r"target\s+(\S+).*?"
        r"RA=([^\s]+).*?"
        r"Dec=([^\s]+).*?"
        r"(?:date_from=(\d{4}-\d{2}-\d{2}))?.*?"
        r"(?:date_to=(\d{4}-\d{2}-\d{2}))?"
    )

    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None

    target, ra_str, dec_str, date_from, date_to = match.groups()

    # Detect non-decimal input (e.g. colon-separated or HMS/DMS)
    if re.search(r"[:hdms]", ra_str, re.IGNORECASE) or re.search(r"[:hdms]", dec_str, re.IGNORECASE):
        raise ValueError("RA and Dec must be given in decimal degrees (e.g. RA=123.45 Dec=-23.5)")

    try:
        ra = float(ra_str)
        dec = float(dec_str)
    except ValueError:
        raise ValueError("RA and Dec must be valid decimal numbers")

    plot_requested = bool(re.search(r"plot\s*=\s*(true|yes|1)|\bplot\b", text, re.IGNORECASE))

    return {
        "target_name": target,
        "ra": ra,
        "dec": dec,
        "date_from": date_from or "2024-01-01",
        "date_to": date_to or datetime.utcnow().strftime("%Y-%m-%d"),
        "plot": plot_requested
    }