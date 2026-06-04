#!/usr/bin/env python3
"""Generate data.json from the actual Verminord sheet data (read via Google Drive API)."""

import json
from datetime import date, timedelta
from collections import defaultdict
import re

TODAY = date(2026, 6, 4)

# ── Current values from the Active Sheet (Dashboard tab) ───────────────────

CURRENT = {
    "cft1":        {"updated": "03.06 18:26", "temp": 22, "ph": 7.5, "fukt": 73, "for": 10},
    "cft2":        {"updated": "03.06 18:22", "temp": 24, "ph": 7.5, "fukt": 76, "for": 10},
    "cft3":        {"updated": "03.06 00:16", "temp": 22, "ph": 7.0, "fukt": 75, "for": 2},
    "wedge1":      {"updated": "03.06 18:10", "temp": 23, "ph": 7.5, "fukt": 63, "for": 0},
    "wedge2":      {"updated": "03.06 18:12", "temp": 21, "ph": 7.5, "fukt": 62, "for": 0},
    "breeder":     {"updated": "03.06 18:22", "temp": 23, "ph": 7.5, "fukt": 73, "for": 10},
    "forkompost1": {"updated": "03.06 00:50", "temp": 33, "ph": 7.5, "fukt": 77, "for": 0},
    "forkompost2": {"updated": "—",           "temp": None, "ph": None, "fukt": None, "for": 0},
    "forkompost3": {"updated": "—",           "temp": None, "ph": None, "fukt": None, "for": 0},
}

SYSTEMS_CFG = [
    {"id": "cft1",        "name": "CFT1",         "group": "prod",       "targets": {"temp": [15, 25], "fukt": [60, 85], "ph": [6.0, 8.0]}},
    {"id": "cft2",        "name": "CFT2",         "group": "prod",       "targets": {"temp": [15, 25], "fukt": [60, 85], "ph": [6.0, 8.0]}},
    {"id": "cft3",        "name": "CFT3",         "group": "prod",       "targets": {"temp": [15, 25], "fukt": [60, 85], "ph": [6.0, 8.0]}},
    {"id": "wedge1",      "name": "Wedge 1",      "group": "prod",       "targets": {"temp": [15, 25], "fukt": [60, 85], "ph": [6.0, 8.0]}},
    {"id": "wedge2",      "name": "Wedge 2",      "group": "prod",       "targets": {"temp": [15, 25], "fukt": [60, 85], "ph": [6.0, 8.0]}},
    {"id": "breeder",     "name": "Breeder Bin",   "group": "prod",       "targets": {"temp": [15, 25], "fukt": [60, 85], "ph": [6.0, 8.0]}},
    {"id": "forkompost1", "name": "Forkompost 1",  "group": "precompost", "targets": {"temp": [55, 80], "fukt": [50, 70], "ph": [6.0, 8.5]}, "threshold": 55, "required": 5},
    {"id": "forkompost2", "name": "Forkompost 2",  "group": "precompost", "targets": {"temp": [55, 80], "fukt": [50, 70], "ph": [6.0, 8.5]}, "threshold": 55, "required": 5},
    {"id": "forkompost3", "name": "Forkompost 3",  "group": "precompost", "targets": {"temp": [55, 80], "fukt": [50, 70], "ph": [6.0, 8.5]}, "threshold": 55, "required": 5},
]

RANGES = [
    {"key": "7D",  "label": "7 DGR",  "n": 7},
    {"key": "21D", "label": "21 DGR", "n": 21},
    {"key": "3M",  "label": "3 MND",  "n": 90},
    {"key": "6M",  "label": "6 MND",  "n": 180},
    {"key": "YTD", "label": "I ÅR",   "n": (TODAY - date(2026, 1, 1)).days},
    {"key": "ALL", "label": "ALT",    "n": (TODAY - date(2025, 7, 7)).days},
]

# ── Historical data from Master Log ────────────────────────────────────────
# Parsed from the Worm Production and Pre-Compost tabs

def pf(s):
    if not s or s == '-':
        return None
    s = s.replace(',', '.').strip()
    try:
        return float(s)
    except:
        return None

def pd(s):
    s = s.strip()
    if s.startswith('??'):
        return None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            parts = s.split('/')
            if len(parts) == 3:
                d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                return date(y, m, d)
        except:
            pass
    return None

# WORM PRODUCTION: Epoch-based mapping
# Jul–Oct 2025: Bin 1→wedge1, Bin 2→wedge2
# Nov 2025–Jan 2026: Bin 1→cft1, Bin 2→cft2
# Feb 2026+: Bin 1→cft1, Bin 2→cft2, BB→breeder
# Active sheet entries use system names directly

PROD_RAW = """07/07/2025,1,62,13,7
07/07/2025,2,64,13,7.5
08/07/2025,1,65,15,6.5
08/07/2025,2,64,14,7
09/07/2025,1,61,15,6
09/07/2025,2,62,16,6.3
10/07/2025,1,64,15,6.5
10/07/2025,2,65,16,6.5
11/07/2025,1,66,18,7
11/07/2025,2,65,16,7.5
12/07/2025,1,61,19,7.5
12/07/2025,2,62,20,7.5
13/07/2025,1,65,20,7.5
13/07/2025,2,63,20,8
14/07/2025,1,75,20,7
14/07/2025,2,69,19,7.5
15/07/2025,1,78,20,7.5
15/07/2025,2,75,18,7.5
16/07/2025,1,81,20,6.5
16/07/2025,2,74,20,7
17/07/2025,1,67,21,6.5
17/07/2025,2,65,21,7
18/07/2025,1,65,20,7
18/07/2025,2,64,21,7.5
19/07/2025,1,59,20,7.5
19/07/2025,2,60,20,7.5
20/07/2025,1,64,20,7
20/07/2025,2,62,19,7.5
21/07/2025,1,71,19,7
21/07/2025,2,70,19,7
22/07/2025,1,65,17,8
22/07/2025,2,68,18,7
23/07/2025,1,69,19,8
23/07/2025,2,61,19,7.5
24/07/2025,1,65,20,7
24/07/2025,2,70,19,6.5
25/07/2025,1,60,19,6.5
25/07/2025,2,67,19,6.5
26/07/2025,1,64,18,6
26/07/2025,2,62,19,6
27/07/2025,1,72,18,5
27/07/2025,2,61,17,6
28/07/2025,1,57,19,6
28/07/2025,2,62,18,6
21/08/2025,1,65,20,6
21/08/2025,2,62,19,6
22/08/2025,1,69,19,6
22/08/2025,2,65,19,6
24/08/2025,1,61,20,6.5
24/08/2025,2,54,19,6.5
25/08/2025,1,65,19,7
25/08/2025,2,61,19,6.5
26/08/2025,1,69,20,7.5
26/08/2025,2,65,18,6
27/08/2025,1,75,19,7
27/08/2025,2,71,19,6.5
28/08/2025,1,71,20,6.3
28/08/2025,2,69,19,6
29/08/2025,1,65,20,7
29/08/2025,2,61,19,6
30/08/2025,1,66,19,6.5
30/08/2025,2,65,18,7.5
31/08/2025,1,61,19,7
31/08/2025,2,54,18,7.5
24/09/2025,1,65,20,7
25/09/2025,1,70,20,6.5
25/09/2025,2,78,17,6
26/09/2025,1,60,19,6.3
26/09/2025,2,67,19,6.5
27/09/2025,2,62,19,6
28/09/2025,1,72,14,5
28/09/2025,2,61,17,6
29/09/2025,1,52,19,6
29/09/2025,2,65,18,8
01/10/2025,1,57,20,5.5
01/10/2025,2,71,19,7.5
02/10/2025,1,61,20,7.8
02/10/2025,2,77,19,6.5
03/10/2025,1,60,20,7
03/10/2025,2,75,19,7
03/10/2025,2,58,18,6.5
07/10/2025,2,86,14,5
09/10/2025,2,60,17,6
09/11/2025,1,61,16,6.5
09/11/2025,2,64,16,6
20/11/2025,1,59,16,7
20/11/2025,2,66,17,6
24/11/2025,1,58,16,7
24/11/2025,2,53,16,6.5
26/11/2025,1,55,14,7.5
26/11/2025,2,55,17,7
28/11/2025,1,55,16,6.5
28/11/2025,2,65,16,7.5
29/11/2025,1,56,16,7.5
30/11/2025,1,61,17,7
01/12/2025,1,65,19,7.5
01/12/2025,2,65,17,7.5
04/12/2025,1,55,14,7.5
04/12/2025,2,50,14,7.6
06/12/2025,1,58,19,6.5
07/12/2025,1,62,13,7
07/12/2025,2,64,13,7
08/12/2025,1,65,15,7.5
08/12/2025,2,64,14,7
09/12/2025,1,61,15,6
09/12/2025,2,62,16,6.3
10/12/2025,1,64,16,6.5
10/12/2025,2,65,16,6.5
11/12/2025,1,66,17,7
11/12/2025,2,65,16,7.5
12/12/2025,1,61,19,7.5
12/12/2025,2,62,20,7.5
13/12/2025,1,65,20,7.5
13/12/2025,2,63,20,8
14/12/2025,1,75,20,7
14/12/2025,2,69,20,7.5
15/12/2025,1,78,20,7.5
15/12/2025,2,75,19,7.5
16/12/2025,1,81,20,6.5
16/12/2025,2,74,20,7
17/12/2025,1,67,21,6.5
17/12/2025,2,65,21,7
18/12/2025,1,65,20,7
18/12/2025,2,64,21,7.5
19/12/2025,1,62,20,7.5
19/12/2025,2,64,20,7
20/12/2025,1,63,19,7.5
20/12/2025,2,64,19,6.5
24/12/2025,1,75,20,6.5
24/12/2025,2,62,19,6.5
01/01/2026,1,62,19,7
01/01/2026,2,65,19,7
04/01/2026,1,63,18,7.5
04/01/2026,2,65,18,7.5
25/02/2026,1,73,13,7
25/02/2026,2,75,15,7
28/02/2026,1,76,17,7
28/02/2026,2,76,15,6
02/03/2026,1,77,19,6
02/03/2026,2,80,19,6.2
03/03/2026,1,75,16,7.5
03/03/2026,2,75,17,7
05/03/2026,1,75,14,7.5
05/03/2026,2,74,15,7
07/03/2026,1,76,14,7
07/03/2026,2,76,14,7
12/03/2026,1,77,16,6.5
12/03/2026,2,76,15,6
13/03/2026,1,78,18,6
13/03/2026,2,76,15,6
14/03/2026,1,80,18,6.5
14/03/2026,2,76,17,6
16/03/2026,1,70,17,7
16/03/2026,2,74,17,7
18/03/2026,1,76,17,7.5
18/03/2026,2,76,16,7.5
20/03/2026,1,74,17,7.5
20/03/2026,2,76,17,7.5
22/03/2026,1,75,18,7.5
22/03/2026,2,76,18,7.5
24/03/2026,1,80,17,6.5
24/03/2026,2,63,18,7
03/04/2026,1,83,19,6.5
03/04/2026,2,83,12,6.5
08/04/2026,1,77,17,6
08/04/2026,2,72,15,6
09/04/2026,1,82,19,6
09/04/2026,2,74,18,6
11/04/2026,1,64,18,7.5
11/04/2026,2,75,18,7.5
12/04/2026,1,75,19,7.5
12/04/2026,2,74,18,7.5
15/04/2026,1,78,16,7.5
15/04/2026,2,72,17,7.5
16/04/2026,1,64,22,7.5
18/04/2026,BB,65,24,7.5
19/04/2026,1,60,22,7.5
29/04/2026,2,64,21,7
04/05/2026,1,75,20.5,7.5
04/05/2026,2,80,19.4,7.5
05/05/2026,1,84,18,7.5
05/05/2026,2,74,26.6,7.5
11/05/2026,2,78,28,7.5
13/05/2026,1,60,19.4,7.5
13/05/2026,2,70,23.3,7.5
15/05/2026,1,68,20.3,7.5
15/05/2026,2,72,20.4,7.2
18/05/2026,1,74,20.8,7.5
18/05/2026,2,74,21.8,7.5
20/05/2026,1,74,25,7.5
20/05/2026,2,78,28,7.5
21/05/2026,BB,74,18,7
24/05/2026,1,83,24,7.3
24/05/2026,2,68,19,7.3
26/05/2026,1,65,16.8,7.4
26/05/2026,2,60,20.6,7.3
29/05/2026,1,63,21,7.2
29/05/2026,2,68,22,7.5
06/06/2026,1,64,19,7.5"""

# Active sheet recent entries (system names used directly)
ACTIVE_PROD = """03/06/2026,CFT1,22,6.5,71
03/06/2026,CFT3,22,7,75
03/06/2026,CFT1,21,7,65
03/06/2026,CFT1,22,7.5,71
03/06/2026,CFT1,22,6.6,71
03/06/2026,CFT1,22,7,75
03/06/2026,Wedge 1,23,7.5,63
03/06/2026,Wedge 2,21,7.5,62
03/06/2026,Breeder Bin,20,7,67
03/06/2026,Breeder Bin,23,7.5,73
03/06/2026,CFT2,24,7.5,76
03/06/2026,CFT1,22,7.5,73
16/04/2026,Wedge 1,22,7.5,71
16/04/2026,Wedge 1,25,7,71"""

# PRE-COMPOST data
PRECOMP_RAW = """09/07/2025,1,60,21,6.8
10/07/2025,1,65,23,6
11/07/2025,1,61,21,6.5
12/07/2025,1,69,34,7.5
13/07/2025,1,75,41,6.5
14/07/2025,1,65,56,6.5
15/07/2025,1,78,64,7
16/07/2025,1,71,67,7.5
17/07/2025,1,69,61,6.5
18/07/2025,1,65,57,6
19/07/2025,1,55,48,6.5
20/07/2025,1,61,41,7
22/07/2025,1,65,40,7.5
23/07/2025,1,68,36,7
25/07/2025,1,65,34,7
27/07/2025,1,61,36,7.8
17/08/2025,1,59,20,7
17/08/2025,2,71,26,6
18/08/2025,1,69,30,6.5
18/08/2025,2,65,35,7
19/08/2025,1,61,45,7.5
19/08/2025,2,75,39,7.5
21/08/2025,1,71,57,7
21/08/2025,2,69,54,6.8
22/08/2025,1,65,67,6.5
22/08/2025,2,72,60,6.5
24/08/2025,1,68,64,6
24/08/2025,2,71,62,5.5
26/08/2025,1,78,66,6
26/08/2025,2,72,65,5.5
29/08/2025,1,75,54,7.5
29/08/2025,2,65,61,7
30/08/2025,1,69,51,7.5
30/08/2025,2,71,65,7
02/09/2025,1,61,43,7
02/09/2025,2,72,53,6.8
04/09/2025,1,63,38,6.5
04/09/2025,2,67,47,7
05/09/2025,1,61,33,7.5
05/09/2025,2,60,35,6.5
08/09/2025,1,63,31,7
08/09/2025,2,64,31,7
10/09/2025,1,64,24,7.5
10/09/2025,2,65,29,7.5
11/09/2025,2,63,24,7.5
12/09/2025,1,74,21,6
12/09/2025,2,64,22,6.5
13/09/2025,1,68,22,6.6
13/09/2025,2,64,23,6
14/09/2025,1,58,21,7.5
14/09/2025,2,63,23,7
15/09/2025,1,66,22,7
15/09/2025,2,63,24,7
16/09/2025,1,60,25,7
16/09/2025,2,63,22,7
17/09/2025,1,65,26,6.5
17/09/2025,2,71,26,6
18/09/2025,1,67,26,7
18/09/2025,2,76,25,6.5
19/09/2025,1,71,25,6.5
19/09/2025,2,74,27,6.5
20/09/2025,1,78,25,8
20/09/2025,2,77,25,7.5
21/09/2025,1,58,25,7
21/09/2025,2,65,24,6.5
22/09/2025,1,59,20,7.5
22/09/2025,2,69,36,6.5
23/09/2025,1,71,33,6.5
23/09/2025,2,75,38,6.3
24/09/2025,1,69,46,6
24/09/2025,2,62,52,5.5
25/09/2025,1,66,55,6
25/09/2025,2,67,54,5.5
26/09/2025,1,60,56,6
26/09/2025,2,69,64,6
27/09/2025,1,85,61,6
27/09/2025,2,81,65,6.5
28/09/2025,1,64,35,6
28/09/2025,2,86,35,6.5
29/09/2025,1,64,49,6
29/09/2025,2,86,55,6
30/09/2025,1,64,46,6
30/09/2025,2,85,49,5.5
01/10/2025,1,71,42,6.5
01/10/2025,2,75,49,6
02/10/2025,1,68,29,5.8
02/10/2025,2,67,39,6
03/10/2025,1,79,31,5.5
03/10/2025,2,65,38,6
22/11/2025,2,61,38,6.5
22/11/2025,4,60,35,6
26/11/2025,2,56,24,6
26/11/2025,4,62,29,6
15/01/2026,1,55,30,8.5
15/01/2026,2,60,25.6,9
25/02/2026,1,65,30,8
26/02/2026,2,61,31,6.5
27/02/2026,1,73,22,6
28/02/2026,1,65,29,7
01/03/2026,1,85,45,6.5
04/03/2026,1,80,63,6.5
06/03/2026,1,73,16,7
11/03/2026,1,74,31,6.5
13/03/2026,1,74,24,7.4
14/03/2026,1,79,24,7.4
14/03/2026,2,72,19,8
19/03/2026,1,69,19,7
19/03/2026,2,68,17,6
20/03/2026,1,70,16,7
20/03/2026,2,70,17,7.5
21/03/2026,2,80,34,6.5
22/03/2026,2,69,38,6.5
23/03/2026,1,81,17,7.5
23/03/2026,2,75,40,7.1
24/03/2026,1,66,17,7.5
24/03/2026,2,76,,6.8
25/03/2026,2,68,46,6.5
26/03/2026,1,70,59,6.5
28/03/2026,1,75,56,6.5
30/03/2026,1,76,17,6
30/03/2026,2,76,17,7
02/04/2026,1,77,19,6
02/04/2026,2,82,19,6.7
03/04/2026,1,83,19,6.5
03/04/2026,2,80,13,7.5
06/04/2026,1,73,17,8
06/04/2026,2,82,18,7
08/04/2026,1,75,13,6.9
08/04/2026,2,74,17,7.2
09/04/2026,1,64,17,7.2
11/04/2026,2,75,18,7.5
12/04/2026,1,75,19,7.5
12/04/2026,2,74,18,7.5
15/04/2026,1,78,16,7.5
15/04/2026,2,72,17,7.5
01/04/2026,1,67,16,7.6
01/04/2026,2,75,43,5.5
02/04/2026,1,47,36,6.6
02/04/2026,2,68,14,7
03/04/2026,1,79,28,7.2
03/04/2026,2,64,12,7
07/04/2026,1,71,16,7.2
07/04/2026,2,62,8,7.5
09/04/2026,1,62,10,7.5
09/04/2026,2,56,8,7
13/04/2026,1,64,9,7.4
13/04/2026,2,62,8,7.3
16/04/2026,1,62,10,7.5
16/04/2026,2,64,10,7.2
20/04/2026,1,69,10,7.5
20/04/2026,2,67,10,7.5
24/04/2026,1,65,10,7.5
24/04/2026,2,65,10,7.3
27/04/2026,1,70,9,7.5
27/04/2026,2,62,9,7.5
16/04/2026,1,64,22,7.5
16/04/2026,2,66,24,7
17/04/2026,1,64,26,7.5
17/04/2026,2,74,25,7
20/04/2026,1,79,24,7.5
20/04/2026,2,74,25,7.5
21/04/2026,1,61,21,7.5
21/04/2026,2,68,25,7
23/04/2026,1,61,25,7
23/04/2026,2,65,24,7.5
24/04/2026,1,64,21,7.5
24/04/2026,2,78,18,7
25/04/2026,1,74,19,7.5
25/04/2026,2,64,18,7.5
27/04/2026,1,74,16.3,7.5
27/04/2026,2,70,17.3,7.5
30/04/2026,1,70,20,7
30/04/2026,2,74,22,7
03/06/2026,1,77,33,7.5"""

# Active forkompost log
ACTIVE_FK = """03/06/2026,Forkompost 1,33,7.5,77"""

# ── Parse + map ────────────────────────────────────────────────────────────

def map_prod_system(d, bin_str):
    """Map worm production record to system ID."""
    name_map = {
        'CFT1': 'cft1', 'CFT2': 'cft2', 'CFT3': 'cft3',
        'Wedge 1': 'wedge1', 'Wedge 2': 'wedge2',
        'Breeder Bin': 'breeder', 'BB': 'breeder',
        'CPT 1': 'cft1', 'CPT 2': 'cft2',
        'CFT 1': 'cft1', 'CFT 2': 'cft2',
    }
    if bin_str in name_map:
        return name_map[bin_str]
    try:
        b = int(float(bin_str))
    except:
        return None
    if d < date(2025, 11, 1):
        return 'wedge1' if b == 1 else 'wedge2'
    else:
        return {1: 'cft1', 2: 'cft2', 3: 'cft3', 4: 'wedge1', 5: 'wedge2', 6: 'breeder'}.get(b)

def map_precomp_system(d, bin_str):
    try:
        b = int(float(bin_str))
    except:
        if 'Forkompost 1' in bin_str: return 'forkompost1'
        if 'Forkompost 2' in bin_str: return 'forkompost2'
        if 'Forkompost 3' in bin_str: return 'forkompost3'
        return None
    return {1: 'forkompost1', 2: 'forkompost2', 3: 'forkompost3', 4: 'forkompost2'}.get(b)

by_system = defaultdict(list)

for line in PROD_RAW.strip().split('\n'):
    parts = line.split(',')
    d = pd(parts[0])
    if not d:
        continue
    sid = map_prod_system(d, parts[1].strip())
    if not sid:
        continue
    m, t, p = pf(parts[2]), pf(parts[3]), pf(parts[4]) if len(parts) > 4 else None
    by_system[sid].append({'date': d, 'temp': t, 'moisture': m, 'ph': p})

for line in ACTIVE_PROD.strip().split('\n'):
    parts = line.split(',')
    d = pd(parts[0])
    if not d:
        continue
    sid = map_prod_system(d, parts[1].strip())
    if not sid:
        continue
    t, p, m = pf(parts[2]), pf(parts[3]), pf(parts[4]) if len(parts) > 4 else None
    by_system[sid].append({'date': d, 'temp': t, 'moisture': m, 'ph': p})

for line in PRECOMP_RAW.strip().split('\n'):
    parts = line.split(',')
    d = pd(parts[0])
    if not d:
        continue
    sid = map_precomp_system(d, parts[1].strip())
    if not sid:
        continue
    m, t, p = pf(parts[2]), pf(parts[3]), pf(parts[4]) if len(parts) > 4 else None
    by_system[sid].append({'date': d, 'temp': t, 'moisture': m, 'ph': p})

for line in ACTIVE_FK.strip().split('\n'):
    parts = line.split(',')
    d = pd(parts[0])
    if not d:
        continue
    sid = map_precomp_system(d, parts[1].strip())
    if not sid:
        continue
    t, p, m = pf(parts[2]), pf(parts[3]), pf(parts[4]) if len(parts) > 4 else None
    by_system[sid].append({'date': d, 'temp': t, 'moisture': m, 'ph': p})

# ── Build time series ──────────────────────────────────────────────────────

def build_series(records, field, ranges, today):
    pairs = sorted([(r['date'], r[field]) for r in records if r[field] is not None])
    if not pairs:
        return {r['key']: [] for r in ranges}
    series = {}
    for rng in ranges:
        cutoff = today - timedelta(days=rng['n'])
        window = [(d, v) for d, v in pairs if d >= cutoff]
        day_map = {}
        for d, v in window:
            day_map[d] = v
        if not day_map:
            series[rng['key']] = []
            continue
        vals = [round(day_map[k], 1) for k in sorted(day_map)]
        series[rng['key']] = vals
    return series

def daily_low(records, n, today):
    cutoff = today - timedelta(days=n)
    pairs = [(r['date'], r['temp']) for r in records if r['temp'] is not None and r['date'] >= cutoff]
    day_mins = {}
    for d, v in pairs:
        if d not in day_mins or v < day_mins[d]:
            day_mins[d] = v
    return [round(day_mins[k], 1) for k in sorted(day_mins)]

def compute_streak(dl, threshold):
    streak = 0
    for v in reversed(dl):
        if v >= threshold:
            streak += 1
        else:
            break
    return streak

# ── Build output ───────────────────────────────────────────────────────────

systems = []
avvik = 0
aktive = 0
within = 0
hyg_met = 0
hyg_total = 0
yesterday = TODAY - timedelta(days=1)

for scfg in SYSTEMS_CFG:
    sid = scfg['id']
    cur = CURRENT[sid]
    recs = sorted(by_system.get(sid, []), key=lambda r: r['date'])

    temp_s = build_series(recs, 'temp', RANGES, TODAY)
    fukt_s = build_series(recs, 'moisture', RANGES, TODAY)
    ph_s   = build_series(recs, 'ph', RANGES, TODAY)

    obj = {
        'id': sid,
        'name': scfg['name'],
        'group': scfg['group'],
        'updated': cur['updated'],
        'temp': cur['temp'],
        'ph': cur['ph'],
        'fukt': cur['fukt'],
        'for': cur['for'],
        'targets': scfg['targets'],
        'tempSeries': temp_s,
        'fuktSeries': fukt_s,
        'phSeries': ph_s,
    }

    has_recent = any(r['date'] >= yesterday for r in recs)
    if has_recent:
        aktive += 1

    streak = None
    if scfg['group'] == 'precompost':
        threshold = scfg.get('threshold', 55)
        required = scfg.get('required', 5)
        dl = daily_low(recs, 10, TODAY)
        streak = compute_streak(dl, threshold)
        obj['threshold'] = threshold
        obj['required'] = required
        obj['dailyLow'] = dl
        obj['streak'] = streak
        hyg_total += 1
        if streak >= required:
            hyg_met += 1

    # Status
    if scfg['group'] == 'precompost':
        if cur['temp'] is None:
            status = 'watch'
        elif streak is not None and streak < scfg.get('required', 5):
            status = 'under'
        elif cur['temp'] < scfg.get('threshold', 55):
            status = 'under'
        else:
            status = 'ok'
    else:
        targets = scfg['targets']
        status = 'ok'
        for metric, bounds in targets.items():
            field = 'fukt' if metric == 'fukt' else metric
            val = cur.get(field)
            if val is not None and (val < bounds[0] or val > bounds[1]):
                status = 'watch'
                break

    obj['status'] = status
    if status == 'under':
        avvik += 1
    if status == 'ok':
        within += 1

    systems.append(obj)

total = len(SYSTEMS_CFG)
health = round(100 * within / total) if total else 0

# Regulatory
regulatory = []
for s in systems:
    if s['group'] != 'precompost':
        continue
    ok = s.get('streak', 0) >= s.get('required', 5)
    if s['temp'] is None:
        regulatory.append({
            'id': len(regulatory) + 1,
            'label': f"§19 Hygienisering — {s['name']}",
            'state': 'Ingen data',
            'tone': 'muted',
            'detail': 'Ingen logg ennå',
        })
    elif ok:
        regulatory.append({
            'id': len(regulatory) + 1,
            'label': f"§19 Hygienisering — {s['name']}",
            'state': 'OK',
            'tone': 'green',
            'detail': f"Streak {s['streak']} dager ≥ {s['threshold']} °C",
        })
    else:
        regulatory.append({
            'id': len(regulatory) + 1,
            'label': f"§19 Hygienisering — {s['name']}",
            'state': 'Avvik',
            'tone': 'bad',
            'detail': f"Streak {s.get('streak', 0)}/{s['required']} dager over {s['threshold']} °C",
        })

data = {
    'RANGES': [{'key': r['key'], 'label': r['label'], 'n': r['n']} for r in RANGES],
    'SYSTEMS': systems,
    'KPIS': {
        'avvik': avvik,
        'hygienisering': {'met': hyg_met, 'total': hyg_total},
        'aktive': aktive,
        'populasjon': 15936,
        'hosting': health,
        'oppgaver': 9,
        'omsetning': 47200,
        'omsetningMaal': 100000,
        'omsetningDager': 9,
    },
    'REMINDERS': [
        {'id': 1, 'tag': 'AKUTT', 'tone': 'gold', 'title': 'Forkompost 1 under 55 °C', 'meta': 'Siste: 33 °C — streak nullstilt', 'sub': 'Sjekk isolasjon og vending'},
    ],
    'PROJECTS': [
        {'id': 1, 'name': 'Utvidet CFT-kapasitet', 'status': 'I gang', 'progress': 60, 'value': '↑ 40 % kapasitet', 'due': '4 dgr', 'tone': 'gold'},
        {'id': 2, 'name': 'Klasse I-sertifisering', 'status': 'Bestått', 'progress': 100, 'value': 'ALS-rapport klar', 'due': '—', 'tone': 'green'},
    ],
    'REGULATORY': regulatory,
    'WEEK': {
        'number': TODAY.isocalendar()[1],
        'title': 'Ukens fokus',
        'goal': 'Rette opp Forkompost 1, forberede neste batch',
        'tasks': [
            {'t': 'Vend FK1, sjekk isolasjon', 'who': 'Habiba', 'tone': 'gold'},
            {'t': 'Logg alle systemer daglig', 'who': 'Martin', 'tone': 'teal'},
            {'t': 'Oppdater foto-indeks', 'who': 'Martin', 'tone': 'muted'},
        ],
        'metric': {'label': 'Omsetning mot 100 000-mål', 'value': 47200, 'target': 100000},
    },
    'MILESTONES': [
        {'title': '15 936 i populasjon', 'detail': 'Ny rekord for anlegget', 'tone': 'green', 'icon': '▲'},
        {'title': 'Klasse I oppnådd', 'detail': 'ALS Lab NO2604972', 'tone': 'green', 'icon': '✓'},
    ],
    'MOTIVATION': [
        {'tag': 'UKENS MÅL', 'text': '350 / 500 poser solgt · 16 dager igjen — stå på!'},
    ],
    'fmt': {},
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print(f"Wrote data.json")
print(f"Systems: {len(systems)}")
for s in systems:
    n = len(by_system.get(s['id'], []))
    print(f"  {s['name']:15s}  status={s['status']:6s}  temp={s['temp']}  records={n}")
print(f"KPIs: avvik={avvik}, aktive={aktive}, health={health}%")
print(f"Hygienisering: {hyg_met}/{hyg_total}")
