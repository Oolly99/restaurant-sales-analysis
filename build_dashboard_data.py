"""Generate the reviewed dashboard snapshot from the two source CSVs."""

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = "https://mavenanalytics.io/data-playground/restaurant-orders"
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar")


def read_csv(name):
    with (ROOT / "data" / "raw" / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def stats(rows):
    return {
        "sales": round(sum(row["cents"] for row in rows) / 100, 2),
        "orders": len({row["order"] for row in rows}),
        "items": len(rows),
    }


def write_snapshot(path):
    orders = read_csv("order_details.csv")
    menu = {row["menu_item_id"]: row for row in read_csv("menu_items.csv")}
    rows = []
    for row in orders:
        item = menu.get(row["item_id"])
        if item:
            date = datetime.strptime(row["order_date"] + " " + row["order_time"], "%m/%d/%y %I:%M:%S %p")
            rows.append({
                "month": MONTHS[date.month - 1], "weekday": WEEKDAYS[date.weekday()],
                "hour": date.hour, "order": row["order_id"], "item": item["item_name"],
                "category": item["category"], "cents": int(Decimal(item["price"]) * 100),
            })

    queries = {key: {"rows": [], "source": {"name": "Maven Analytics Restaurant Orders",
        "type": "file", "files": ["order_details.csv", "menu_items.csv"], "url": SOURCE,
        "description": "Fictional restaurant, January–March 2023. Join by item ID. Omit order lines without a matched menu item. Sales sum menu prices, and orders count distinct IDs within the filter."},
        "methods": [{"language": "text", "code": "Run build_dashboard_data.py with the two source CSVs."}]}
        for key in ("totals", "monthly", "categories", "weekday", "hourly", "items", "pairs")}

    categories = sorted({row["category"] for row in rows})
    facets = {"month": ["All", *MONTHS], "category": ["All", *categories]}
    for selected_month in facets["month"]:
        for selected_category in facets["category"]:
            scope = f"{selected_month}|{selected_category}"
            scoped = [row for row in rows if selected_month in ("All", row["month"])
                      and selected_category in ("All", row["category"])]
            current = stats(scoped)
            current["average"] = round(current["sales"] / current["orders"], 2) if current["orders"] else None
            queries["totals"]["rows"].append({"scope": scope, **current})
            for query, field, labels in (
                ("monthly", "month", MONTHS if selected_month == "All" else [selected_month]),
                ("categories", "category", categories if selected_category == "All" else [selected_category]),
                ("weekday", "weekday", WEEKDAYS),
                ("hourly", "hour", range(10, 24)),
                ("items", "item", sorted({row["item"] for row in scoped})),
            ):
                values = [{"scope": scope, "name": str(label), **stats([row for row in scoped if row[field] == label])} for label in labels]
                if query == "items":
                    values = sorted(values, key=lambda row: (-row["sales"], row["name"]))[:8]
                queries[query]["rows"].extend(values)
            baskets = defaultdict(set)
            for row in scoped:
                baskets[row["order"]].add(row["item"])
            counts = Counter(pair for items in baskets.values() for pair in combinations(sorted(items), 2))
            ranked = sorted(counts.items(), key=lambda entry: (-entry[1], entry[0]))[:5]
            queries["pairs"]["rows"].extend({"scope": scope, "name": " + ".join(pair), "orders": count} for pair, count in ranked)

    assert len(orders) == 12234 and len(menu) == 32 and len(rows) == 12097
    assert queries["totals"]["rows"][0] == {
        "scope": "All|All", "sales": 159217.90, "orders": 5343, "items": 12097, "average": 29.80,
    }
    path.write_text(json.dumps({"surface": "dashboard", "title": "Restaurant sales & menu performance",
        "buildStatus": "complete", "queries": queries, "facets": facets}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    write_snapshot(Path(sys.argv[1]))
