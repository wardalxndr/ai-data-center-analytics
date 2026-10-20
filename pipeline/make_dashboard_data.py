"""Build data/dashboard_data.json for the AI DC one-pager dashboard.

Reads the raw Epoch CSVs (data/raw/*.csv, live snapshot) and computes
every number the dashboard shows. If the raw CSVs are missing they are
downloaded fresh from epoch.ai (CC-BY). The pinned snapshot (94 sites /
560 rows, ADR 0006) is noted as drift so the dashboard never lies about
which data window it shows.
Run: python pipeline/make_dashboard_data.py
"""
import csv
import datetime as dt
import io
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dashboard_data.json"
RAW = ROOT / "data" / "raw"

URLS = {
    "data_centers.csv":
        "https://epoch.ai/data/data_centers/data_centers.csv",
    "data_center_timelines.csv":
        "https://epoch.ai/data/data_center_timelines/data_center_timelines.csv",
}
PINNED = {"dc": 94, "tl": 560}

APAC_COUNTRIES = {"China", "Malaysia", "Indonesia", "Australia", "Japan",
                  "India", "Singapore", "South Korea", "Taiwan",
                  "New Zealand", "Vietnam", "Thailand", "Philippines",
                  "Hong Kong"}
NA_COUNTRIES = {"United States", "Canada", "Mexico"}
LATAM_COUNTRIES = {"Brazil", "Chile", "Argentina", "Colombia", "Peru"}


def region(country):
    if country in NA_COUNTRIES:
        return "North America"
    if country in APAC_COUNTRIES:
        return "APAC"
    if country in LATAM_COUNTRIES:
        return "LATAM"
    return "EMEA"


def clean_owner(o):
    return (o or "").split(" #")[0].strip()


def load_csv(name):
    path = RAW / name
    if not path.exists():
        before = RAW
        before.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URLS[name], path)
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def main():
    dc = load_csv("data_centers.csv")
    tl = load_csv("data_center_timelines.csv")

    snap = dt.date.today().isoformat()

    total_mw = sum(num(r["Current power (MW)"]) for r in dc)
    country_mw = defaultdict(float)
    country_n = defaultdict(int)
    owner_mw = defaultdict(float)
    rows = []
    name_region = {}
    for r in dc:
        country = (r["Country"] or "").strip()
        owner = clean_owner(r["Owner"])
        mw = num(r["Current power (MW)"])
        country_mw[country] += mw
        country_n[country] += 1
        owner_mw[owner] += mw
        rows.append({"name": (r["Name"] or "").strip(),
                     "country": country, "owner": owner, "mw": mw})
        name_region[(r["Name"] or "").strip()] = region(country)

    # MW per region per year, stacked area chart input
    region_year_mw = defaultdict(lambda: defaultdict(float))
    region_year_n = defaultdict(lambda: defaultdict(int))

    countries = sorted(([[c, country_mw[c], country_n[c]]
                         for c in country_mw]),
                       key=lambda x: -x[1])
    owners = sorted(([[o, owner_mw[o]] for o in owner_mw if o]),
                    key=lambda x: -x[1])
    us_share = country_mw.get("United States", 0) / max(total_mw, 1)

    region_mw = defaultdict(float)
    for r in rows:
        region_mw[region(r["country"])] += r["mw"]
    regions = sorted(([[k, v] for k, v in region_mw.items()]),
                     key=lambda x: -x[1])
    apac_share = region_mw.get("APAC", 0) / max(total_mw, 1)

    first_year = defaultdict(int)
    first_mw = defaultdict(float)
    apac_detail = []
    for r in rows:
        if r["country"] in APAC_COUNTRIES:
            apac_detail.append(r)

    starts = defaultdict(list)
    powered = {}
    for r in tl:
        name = r["Data center"]
        d = r["Date"][:10]
        if not d:
            continue
        starts[name].append(d)
        if num(r["Power (MW)"]) > 0 and name not in powered:
            powered[name] = d

    build_days = defaultdict(list)
    for name, dates in starts.items():
        start = min(dates)
        pw = powered.get(name)
        if pw and pw >= start:
            days = (dt.date.fromisoformat(pw) -
                    dt.date.fromisoformat(start)).days
            build_days[start[:4]].append(days)

            y = start[:4]
            base_mw = num(
                next((row["Power (MW)"] for row in tl
                      if row["Data center"] == name and row["Date"][:10] == pw),
                     "0"))
            first_mw[y] += base_mw
            first_year[y] += 1
            reg = name_region.get(name)
            if reg:
                region_year_mw[y][reg] += base_mw
                region_year_n[y][reg] += 1

    velocities = [[y, round(sum(v) / len(v))]
                  for y, v in sorted(build_days.items()) if v]
    adds = sorted([[y, round(first_mw[y]), first_year[y]]
                   for y in sorted(first_mw)
                   if int(y) <= 2025])
    region_additions = [
        [y, {k: round(v) for k, v in region_year_mw[y].items()},
         sum(region_year_n[y].values())]
        for y in sorted(region_year_mw) if int(y) <= 2025]

    avg_build = round(sum(v for vals in build_days.values()
                          for v in vals) / max(
        sum(len(v) for v in build_days.values()), 1))

    malaysia_mw = country_mw.get("Malaysia", 0)
    malaysia_n = country_n.get("Malaysia", 0)
    indonesia_mw = country_mw.get("Indonesia", 0)
    apac_mw = region_mw.get("APAC", 0)
    apac_sites = sum(1 for r in rows if r["country"] in APAC_COUNTRIES)

    payload = {
        "pinned": PINNED,
        "drift": {"dc": len(dc), "tl": len(tl)},
        "snapshot": snap,
        "kpis": {
            "sites": len(dc),
            "total_gw": round(total_mw / 1000, 1),
            "apac_sites": apac_sites,
            "apac_mw": round(apac_mw),
            "avg_build_days": avg_build,
        },
        "us_share": round(us_share, 4),
        "us_mw": round(country_mw.get("United States", 0)),
        "regions": [[k, round(v)] for k, v in regions],
        "apac_share": round(apac_share, 4),
        "countries": [[c, round(m), n] for c, m, n in countries[:10]],
        "owners": [[o, round(m)] for o, m in owners[:8]],
        "velocity": velocities,
        "additions": adds,
        "region_additions": region_additions,
        "malaysia": {"mw": round(malaysia_mw), "sites": malaysia_n},
        "indonesia": {"mw": round(indonesia_mw), "sites":
                      country_n.get("Indonesia", 0)},
        "apac_detail": sorted(apac_detail, key=lambda r: -r["mw"]),
        "countries_all": [[c, round(m), n] for c, m, n in countries],
        "sites_all": sorted(
            [{"name": r["name"], "country": r["country"],
              "owner": r["owner"] or "Unknown", "mw": round(r["mw"], 1)}
             for r in rows], key=lambda s: -s["mw"]),
    }
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"OK {OUT} ({OUT.stat().st_size // 1024} KB)")
    print(f"drift vs pinned: dc {len(dc)}/{PINNED['dc']}, "
          f"tl {len(tl)}/{PINNED['tl']}")


if __name__ == "__main__":
    main()
