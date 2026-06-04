#!/usr/bin/env python3
"""
sync_sheet.py — Les Google Sheet, bygg data.json for Verminord Storskjerm.

Bruk:
  GOOGLE_SHEET_ID=xxx python scripts/sync_sheet.py
  # eller med config.json som har sheet_id satt

Miljøvariabler:
  GOOGLE_SHEET_ID        — Sheet-ID (overstyrer config.json)
  GOOGLE_CREDENTIALS_JSON — Innhold av service-account-nøkkel (JSON-streng)
  GOOGLE_CREDENTIALS_FILE — Sti til service-account-nøkkelfil
  VN_OUTPUT              — Sti til output (standard: data.json i repo-rot)
"""

import json
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config():
    with open(SCRIPT_DIR / "config.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Google Sheets reader
# ---------------------------------------------------------------------------

def get_sheets_service():
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_file = os.environ.get("GOOGLE_CREDENTIALS_FILE")

    if creds_json:
        import json as _json
        info = _json.loads(creds_json)
        creds = Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
    elif creds_file:
        creds = Credentials.from_service_account_file(
            creds_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
    else:
        raise RuntimeError(
            "Sett GOOGLE_CREDENTIALS_JSON eller GOOGLE_CREDENTIALS_FILE"
        )

    return build("sheets", "v4", credentials=creds)


def fetch_tab(service, sheet_id, tab_name):
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"'{tab_name}'")
        .execute()
    )
    return result.get("values", [])


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_date(s):
    """Parse dd/mm/yyyy or yyyy-mm-dd."""
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_float(s):
    if not s:
        return None
    s = s.strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def is_section_header(row):
    """Detect section-header rows like 'WEDGE PRODUCTION: Jul–Oct 2025'."""
    if not row:
        return True
    first = str(row[0]).strip().upper()
    return (
        not first
        or first.startswith("DATE")
        or "PRODUCTION" in first
        or "COMPOST" in first
        or first.startswith("BIN")
        or first.startswith("---")
    )


def parse_rows(raw_rows, col_map):
    """Parse sheet rows into structured records."""
    records = []
    for row in raw_rows:
        if len(row) <= max(col_map.values()):
            row += [""] * (max(col_map.values()) + 1 - len(row))

        if is_section_header(row):
            continue

        d = parse_date(str(row[col_map["date"]]))
        if d is None:
            continue

        bin_val = str(row[col_map["bin"]]).strip()
        try:
            bin_num = int(float(bin_val))
        except (ValueError, TypeError):
            continue

        records.append({
            "date": d,
            "bin": bin_num,
            "temp": parse_float(str(row[col_map["temp"]])),
            "moisture": parse_float(str(row[col_map["moisture"]])),
            "ph": parse_float(str(row[col_map["ph"]])),
            "feed": str(row[col_map["feed"]]).strip() if col_map["feed"] < len(row) else "",
            "comment": str(row[col_map["comment"]]).strip() if col_map["comment"] < len(row) else "",
        })

    return records


# ---------------------------------------------------------------------------
# Epoch → System mapping
# ---------------------------------------------------------------------------

def resolve_system(record_date, bin_num, tab_key, epoch_map):
    """Find the system ID for a given date + bin + tab using the epoch map."""
    for ep in epoch_map:
        if ep["tab"] != tab_key:
            continue
        if ep["bin"] != bin_num:
            continue

        start = date.fromisoformat(ep["start"])
        end = date.fromisoformat(ep["end"]) if ep.get("end") else date(2099, 12, 31)

        if start <= record_date <= end:
            return ep["system"]
    return None


# ---------------------------------------------------------------------------
# Time series builder
# ---------------------------------------------------------------------------

def build_series(dated_values, ranges_cfg, today):
    """Build {rangeKey: [values]} from a list of (date, value) pairs."""
    dated_values.sort(key=lambda x: x[0])

    ytd_start = date(today.year, 1, 1)
    all_start = dated_values[0][0] if dated_values else today

    series = {}
    for r in ranges_cfg:
        key = r["key"]
        n = r["n"]

        if n == "ytd":
            cutoff = ytd_start
        elif n == "all":
            cutoff = all_start
        else:
            cutoff = today - timedelta(days=n)

        window = [(d, v) for d, v in dated_values if d >= cutoff]

        day_map = {}
        for d, v in window:
            if v is not None:
                day_map[d] = v

        if not day_map:
            series[key] = []
            continue

        first = min(day_map)
        last = max(day_map)
        result = []
        current = first
        last_known = None
        while current <= last:
            if current in day_map:
                last_known = day_map[current]
            if last_known is not None:
                result.append(round(last_known, 1))
            current += timedelta(days=1)

        series[key] = result

    return series


def daily_low_temps(dated_temps, n_days, today):
    """Lowest temp per day for the last n_days (for §19 dailyLow)."""
    cutoff = today - timedelta(days=n_days)
    day_mins = {}
    for d, v in dated_temps:
        if v is None or d < cutoff:
            continue
        if d not in day_mins or v < day_mins[d]:
            day_mins[d] = v

    result = []
    current = cutoff + timedelta(days=1)
    while current <= today:
        if current in day_mins:
            result.append(round(day_mins[current], 1))
        current += timedelta(days=1)

    return result


# ---------------------------------------------------------------------------
# KPI computation (§5)
# ---------------------------------------------------------------------------

def compute_streak(daily_low, threshold):
    """Sammenhengende døgn (bakfra) der laveste temp >= threshold."""
    streak = 0
    for v in reversed(daily_low):
        if v >= threshold:
            streak += 1
        else:
            break
    return streak


def compute_status(system, latest, streak=None):
    """ok / watch / under."""
    targets = system["targets"]

    if system["group"] == "precompost":
        threshold = system.get("threshold", 55)
        required = system.get("required", 5)
        if streak is not None and streak < required:
            return "under"
        if latest.get("temp") is not None and latest["temp"] < threshold:
            return "under"

    for metric, (lo, hi) in targets.items():
        field = "moisture" if metric == "fukt" else metric
        val = latest.get(field)
        if val is not None and (val < lo or val > hi):
            return "watch"

    return "ok"


def fmt_updated(d):
    """Format date as dd.mm HH:MM (use 00:00 since sheet has no time)."""
    return d.strftime("%d.%m") + " 00:00"


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build_data_json(prod_records, precomp_records, config, today):
    systems_cfg = {s["id"]: s for s in config["systems"]}
    epoch_map = config["epoch_map"]
    ranges_cfg = config["ranges"]

    # Group records by system
    by_system = {s["id"]: [] for s in config["systems"]}

    for rec in prod_records:
        sid = resolve_system(rec["date"], rec["bin"], "production", epoch_map)
        if sid and sid in by_system:
            by_system[sid].append(rec)

    for rec in precomp_records:
        sid = resolve_system(rec["date"], rec["bin"], "precompost", epoch_map)
        if sid and sid in by_system:
            by_system[sid].append(rec)

    # Build each system object
    systems = []
    yesterday = today - timedelta(days=1)
    avvik = 0
    aktive = 0
    within_targets = 0
    hygiene_met = 0
    hygiene_total = 0
    total_pop = 0

    for scfg in config["systems"]:
        sid = scfg["id"]
        recs = sorted(by_system[sid], key=lambda r: r["date"])

        if not recs:
            sys_obj = {
                "id": sid,
                "name": scfg["name"],
                "group": scfg["group"],
                "status": "watch",
                "updated": "—",
                "temp": None, "ph": None, "fukt": None, "for": 0,
                "targets": scfg["targets"],
                "tempSeries": {r["key"]: [] for r in ranges_cfg},
                "fuktSeries": {r["key"]: [] for r in ranges_cfg},
                "phSeries":   {r["key"]: [] for r in ranges_cfg},
            }
            if scfg["group"] == "precompost":
                sys_obj["threshold"] = scfg.get("threshold", 55)
                sys_obj["required"] = scfg.get("required", 5)
                sys_obj["dailyLow"] = []
                sys_obj["streak"] = 0
                hygiene_total += 1
            systems.append(sys_obj)
            continue

        latest = recs[-1]
        latest_temp = latest["temp"]
        latest_moist = latest["moisture"]
        latest_ph = latest["ph"]

        # Check if active (logged in last 24h)
        if latest["date"] >= yesterday:
            aktive += 1

        # Time series
        temp_pairs = [(r["date"], r["temp"]) for r in recs if r["temp"] is not None]
        moist_pairs = [(r["date"], r["moisture"]) for r in recs if r["moisture"] is not None]
        ph_pairs = [(r["date"], r["ph"]) for r in recs if r["ph"] is not None]

        temp_series = build_series(temp_pairs, ranges_cfg, today)
        fukt_series = build_series(moist_pairs, ranges_cfg, today)
        ph_series = build_series(ph_pairs, ranges_cfg, today)

        sys_obj = {
            "id": sid,
            "name": scfg["name"],
            "group": scfg["group"],
            "updated": fmt_updated(latest["date"]),
            "temp": round(latest_temp, 1) if latest_temp else None,
            "ph": round(latest_ph, 1) if latest_ph else None,
            "fukt": round(latest_moist, 1) if latest_moist else None,
            "for": 0,
            "targets": scfg["targets"],
            "tempSeries": temp_series,
            "fuktSeries": fukt_series,
            "phSeries": ph_series,
        }

        streak = None
        if scfg["group"] == "precompost":
            threshold = scfg.get("threshold", 55)
            required = scfg.get("required", 5)
            dl = daily_low_temps(temp_pairs, 10, today)
            streak = compute_streak(dl, threshold)
            sys_obj["threshold"] = threshold
            sys_obj["required"] = required
            sys_obj["dailyLow"] = dl
            sys_obj["streak"] = streak
            hygiene_total += 1
            if streak >= required:
                hygiene_met += 1

        status = compute_status(scfg, {
            "temp": latest_temp,
            "moisture": latest_moist,
            "ph": latest_ph,
        }, streak)
        sys_obj["status"] = status

        if status == "under":
            avvik += 1
        if status == "ok":
            within_targets += 1

        systems.append(sys_obj)

    total_systems = len(config["systems"])
    health = round(100 * within_targets / total_systems) if total_systems else 0

    data = {
        "RANGES": [{"key": r["key"], "label": r["label"], "n": r["n"] if isinstance(r["n"], int) else total_systems} for r in ranges_cfg],
        "SYSTEMS": systems,
        "KPIS": {
            "avvik": avvik,
            "hygienisering": {"met": hygiene_met, "total": hygiene_total},
            "aktive": aktive,
            "populasjon": total_pop,
            "hosting": health,
            "oppgaver": 0,
            "omsetning": 0,
            "omsetningMaal": 100000,
            "omsetningDager": 0,
        },
        "REMINDERS": [],
        "PROJECTS": [],
        "REGULATORY": build_regulatory(systems, config),
        "WEEK": {
            "number": today.isocalendar()[1],
            "title": "Ukens fokus",
            "goal": "",
            "tasks": [],
            "metric": {"label": "Omsetning mot 100 000-mål", "value": 0, "target": 100000},
        },
        "MILESTONES": [],
        "MOTIVATION": [],
        "fmt": {},
    }

    return data


def build_regulatory(systems, config):
    """Build REGULATORY entries from system statuses."""
    items = []
    for sys_obj in systems:
        if sys_obj["group"] == "precompost":
            streak = sys_obj.get("streak", 0)
            required = sys_obj.get("required", 5)
            if streak < required:
                items.append({
                    "id": len(items) + 1,
                    "label": f"§19 Hygienisering — {sys_obj['name']}",
                    "state": "Avvik",
                    "tone": "bad",
                    "detail": f"Streak {streak}/{required} dager over {sys_obj.get('threshold', 55)} °C",
                })
            else:
                items.append({
                    "id": len(items) + 1,
                    "label": f"§19 Hygienisering — {sys_obj['name']}",
                    "state": "OK",
                    "tone": "green",
                    "detail": f"Streak {streak} dager ≥ {sys_obj.get('threshold', 55)} °C",
                })
    return items


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    config = load_config()

    sheet_id = os.environ.get("GOOGLE_SHEET_ID") or config.get("sheet_id")
    if not sheet_id or sheet_id == "FILL_IN_YOUR_GOOGLE_SHEET_ID":
        print("FEIL: Sett GOOGLE_SHEET_ID (env) eller sheet_id i config.json")
        sys.exit(1)

    today = date.today()
    col_map = config["columns"]

    print(f"Synkroniserer fra sheet {sheet_id} ...")
    service = get_sheets_service()

    prod_rows = fetch_tab(service, sheet_id, config["tabs"]["production"])
    print(f"  Worm Production: {len(prod_rows)} rader")

    precomp_rows = fetch_tab(service, sheet_id, config["tabs"]["precompost"])
    print(f"  Pre-Compost: {len(precomp_rows)} rader")

    prod_records = parse_rows(prod_rows, col_map)
    precomp_records = parse_rows(precomp_rows, col_map)
    print(f"  Parsed: {len(prod_records)} produksjon, {len(precomp_records)} forkompost")

    data = build_data_json(prod_records, precomp_records, config, today)

    output = Path(os.environ.get("VN_OUTPUT", REPO_ROOT / "data.json"))
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Skrev {output} ({output.stat().st_size} bytes)")
    print(f"  Systemer: {len(data['SYSTEMS'])}, aktive: {data['KPIS']['aktive']}, avvik: {data['KPIS']['avvik']}")


if __name__ == "__main__":
    main()
