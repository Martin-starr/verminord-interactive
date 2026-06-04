#!/usr/bin/env python3
"""
test_sync.py -- Offline test for sync_sheet.py using mock sheet data.
No Google credentials required.
"""

import sys
import json
from datetime import date, timedelta
from pathlib import Path

# Ensure scripts/ is importable
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from sync_sheet import (
    parse_rows,
    parse_date,
    build_system_name_map,
    resolve_system_by_name,
    build_data_json,
    load_config,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAILURES = []


def check(label, condition, detail=""):
    if not condition:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" -- {detail}"
        FAILURES.append(msg)
        print(msg)
    else:
        print(f"  ok: {label}")


# ---------------------------------------------------------------------------
# Build mock rows matching the active sheet format:
#   [timestamp, system_name, logger, temp, ph, moisture, feed, comment]
# ---------------------------------------------------------------------------

SYSTEM_NAMES = [
    "CFT1", "CFT2", "CFT3",
    "Wedge 1", "Wedge 2",
    "Breeder Bin",
    "Forkompost 1", "Forkompost 2", "Forkompost 3",
]

# Realistic value ranges per system group
PROD_DEFAULTS = {"temp": 21.0, "ph": 7.2, "moisture": 72.0}
PRECOMP_DEFAULTS = {"temp": 62.0, "ph": 7.0, "moisture": 58.0}


def make_row(dt, system, logger, temp, ph, moisture, feed="", comment=""):
    """Return a row list matching Google Sheets format (all strings)."""
    return [
        dt.strftime("%d/%m/%Y"),
        system,
        logger,
        str(temp),
        str(ph),
        str(moisture),
        feed,
        comment,
    ]


def generate_mock_rows():
    """Generate ~10 days of data for each of the 9 systems."""
    rows = []
    today = date(2026, 6, 4)
    loggers = ["Mats", "Elin", "Jo"]

    for day_offset in range(10):
        dt = today - timedelta(days=9 - day_offset)
        for i, name in enumerate(SYSTEM_NAMES):
            is_precomp = name.startswith("Forkompost")
            defaults = PRECOMP_DEFAULTS if is_precomp else PROD_DEFAULTS

            # Add slight daily variation
            temp = round(defaults["temp"] + (day_offset % 3) - 1, 1)
            ph = round(defaults["ph"] + (day_offset % 4) * 0.1, 1)
            moisture = round(defaults["moisture"] + (day_offset % 5) - 2, 1)
            logger = loggers[day_offset % len(loggers)]
            feed = "Matavfall 5L" if day_offset % 3 == 0 else ""
            comment = "Alt OK" if day_offset % 5 == 0 else ""

            rows.append(make_row(dt, name, logger, temp, ph, moisture, feed, comment))

    return rows


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_parse_date():
    print("\n--- parse_date ---")
    check("dd/mm/yyyy", parse_date("04/06/2026") == date(2026, 6, 4))
    check("yyyy-mm-dd", parse_date("2026-06-04") == date(2026, 6, 4))
    check("dd.mm.yyyy", parse_date("04.06.2026") == date(2026, 6, 4))
    check("with time", parse_date("04/06/2026 14:30") == date(2026, 6, 4))
    check("bad string", parse_date("not-a-date") is None)


def test_name_map():
    print("\n--- build_system_name_map / resolve_system_by_name ---")
    config = load_config()
    name_map = build_system_name_map(config["systems"])

    check("CFT1 resolves", resolve_system_by_name("CFT1", name_map) == "cft1")
    check("cft1 lowercase", resolve_system_by_name("cft1", name_map) == "cft1")
    check("Wedge 1", resolve_system_by_name("Wedge 1", name_map) == "wedge1")
    check("Breeder Bin", resolve_system_by_name("Breeder Bin", name_map) == "breeder")
    check("Forkompost 1", resolve_system_by_name("Forkompost 1", name_map) == "forkompost1")
    check("alias BB", resolve_system_by_name("BB", name_map) == "breeder")
    check("alias FK1", resolve_system_by_name("FK1", name_map) == "forkompost1")
    check("unknown returns None", resolve_system_by_name("NoSuchSystem", name_map) is None)


def test_parse_rows():
    print("\n--- parse_rows ---")
    config = load_config()
    mock = generate_mock_rows()
    records = parse_rows(mock, config["columns"])

    check("non-empty", len(records) > 0, f"got {len(records)}")
    expected = 10 * 9  # 10 days x 9 systems
    check(f"record count == {expected}", len(records) == expected, f"got {len(records)}")

    # Spot check first record
    r0 = records[0]
    check("has date", isinstance(r0["date"], date))
    check("has system_name", isinstance(r0["system_name"], str) and len(r0["system_name"]) > 0)
    check("has temp", r0["temp"] is not None)
    check("has ph", r0["ph"] is not None)
    check("has moisture", r0["moisture"] is not None)

    return records


def test_build_data_json(records):
    print("\n--- build_data_json ---")
    config = load_config()
    today = date(2026, 6, 4)
    data = build_data_json(records, config, today)

    RANGE_KEYS = {"7D", "21D", "3M", "6M", "YTD", "ALL"}

    # --- SYSTEMS ---
    systems = data["SYSTEMS"]
    check("9 systems", len(systems) == 9, f"got {len(systems)}")

    system_ids = {s["id"] for s in systems}
    expected_ids = {"cft1", "cft2", "cft3", "wedge1", "wedge2", "breeder",
                    "forkompost1", "forkompost2", "forkompost3"}
    check("all system ids present", system_ids == expected_ids,
          f"missing={expected_ids - system_ids}, extra={system_ids - expected_ids}")

    for s in systems:
        sid = s["id"]

        # tempSeries / fuktSeries / phSeries each have 6 range keys
        for series_name in ("tempSeries", "fuktSeries", "phSeries"):
            keys = set(s[series_name].keys())
            check(f"{sid}.{series_name} has 6 keys", keys == RANGE_KEYS,
                  f"got {keys}")

        # status is valid
        check(f"{sid}.status valid", s["status"] in ("ok", "watch", "under"),
              f"got {s['status']}")

        # Forkompost extras
        if s["group"] == "precompost":
            check(f"{sid} has dailyLow", "dailyLow" in s)
            check(f"{sid} has streak", "streak" in s)
            check(f"{sid} has threshold", "threshold" in s)
            check(f"{sid} has required", "required" in s)

    # --- KPIS ---
    kpis = data["KPIS"]
    required_kpi_fields = ["avvik", "hygienisering", "aktive", "populasjon",
                           "hosting", "oppgaver", "omsetning",
                           "omsetningMaal", "omsetningDager"]
    for field in required_kpi_fields:
        check(f"KPIS.{field} exists", field in kpis, f"missing from KPIS")

    check("hygienisering.total == 3",
          kpis["hygienisering"]["total"] == 3,
          f"got {kpis['hygienisering']['total']}")

    # --- RANGES ---
    check("RANGES has 6 entries", len(data["RANGES"]) == 6,
          f"got {len(data['RANGES'])}")

    # --- Other top-level keys ---
    for key in ("REGULATORY", "WEEK", "MILESTONES", "MOTIVATION"):
        check(f"top-level '{key}' present", key in data)

    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("sync_sheet.py offline test")
    print("=" * 60)

    test_parse_date()
    test_name_map()
    records = test_parse_rows()
    data = test_build_data_json(records)

    print("\n" + "=" * 60)
    if FAILURES:
        print(f"RESULT: FAIL  ({len(FAILURES)} failure(s))")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("RESULT: PASS  (all checks passed)")
        sys.exit(0)


if __name__ == "__main__":
    main()
