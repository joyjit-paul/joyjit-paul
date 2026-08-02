import json
from datetime import datetime, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

CELL = 12
GAP = 3
LEFT_PAD = 30
TOP_PAD = 40
LEGEND_H = 30
FOOTER_H = 30

def load_data(path="data/contributions.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def level_for(day, max_count):
    if day["count"] == 0:
        return 0
    # Map count into 5 buckets using the existing GitHub-style level if present, else derive it
    lvl = day.get("level")
    if lvl is not None and 0 <= lvl <= 4:
        return lvl + 1  # shift so 0 stays "no contrib", 1-5 are intensity buckets
    if max_count == 0:
        return 1
    ratio = day["count"] / max_count
    if ratio > 0.75:
        return 5
    elif ratio > 0.5:
        return 4
    elif ratio > 0.25:
        return 3
    else:
        return 1

def build_svg(data, out_path="contrib-heatmap.svg"):
    days = data["days"]
    stats = data["stats"]

    if not days:
        raise SystemExit("No contribution data to render.")

    # Group days into weeks (columns), aligned by weekday like GitHub's calendar
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    # Back up to the most recent Sunday on/before first_date so columns align
    offset = (first_date.weekday() + 1) % 7  # weekday(): Mon=0..Sun=6 -> convert to Sun=0
    start_date = first_date - timedelta(days=offset)

    day_map = {d["date"]: d for d in days}
    max_count = max((d["count"] for d in days), default=0)

    weeks = []
    cursor = start_date
    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d")
    while cursor <= last_date:
        week = []
        for i in range(7):
            date_str = cursor.strftime("%Y-%m-%d")
            d = day_map.get(date_str, {"date": date_str, "count": 0, "level": 0})
            week.append(d)
            cursor += timedelta(days=1)
        weeks.append(week)

    num_weeks = len(weeks)
    width = LEFT_PAD + num_weeks * (CELL + GAP) + 20
    height = TOP_PAD + 7 * (CELL + GAP) + LEGEND_H + FOOTER_H

    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
                f'font-family="monospace" font-size="12">')
    svg.append(f'<rect width="{width}" height="{height}" fill="none"/>')

    svg.append('<style>')
    svg.append('''
    .cell {
        opacity: 0;
        animation: slideIn 0.3s ease forwards;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translate(-6px, -6px); }
        to { opacity: 1; transform: translate(0, 0); }
    }
    ''')
    svg.append('</style>')

    # Draw cells, staggered diagonally (delay based on week + day index)
    idx = 0
    for w, week in enumerate(weeks):
        for dow, day in enumerate(week):
            x = LEFT_PAD + w * (CELL + GAP)
            y = TOP_PAD + dow * (CELL + GAP)
            lvl = level_for(day, max_count)
            color = PALETTE[lvl]
            delay = (w + dow) * 0.008
            svg.append(f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                        f'fill="{color}" style="animation-delay:{delay:.3f}s">'
                        f'<title>{day["date"]}: {day["count"]} contributions</title>'
                        f'</rect>')
            idx += 1

    # Legend: Less -> More
    legend_y = TOP_PAD + 7 * (CELL + GAP) + 20
    svg.append(f'<text x="{LEFT_PAD}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = LEFT_PAD + 45
    for lvl in range(6):
        svg.append(f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" rx="2" '
                    f'fill="{PALETTE[lvl]}"/>')
        lx += CELL + GAP
    svg.append(f'<text x="{lx + 5}" y="{legend_y}" fill="#8b949e">More</text>')

    # Footer stats
    footer_y = legend_y + 25
    footer_text = (f'{stats["total"]:,} contributions in the last year · '
                    f'current streak {stats["current_streak"]} · '
                    f'longest streak {stats["longest_streak"]}')
    svg.append(f'<text x="{LEFT_PAD}" y="{footer_y}" fill="#c9d1d9">{footer_text}</text>')

    svg.append('</svg>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved {out_path}")

if __name__ == "__main__":
    data = load_data()
    build_svg(data)