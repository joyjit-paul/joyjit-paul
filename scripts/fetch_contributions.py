import json
import re
import sys
from datetime import datetime
import requests
from bs4 import BeautifulSoup

USERNAME = "joyjit-paul"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_contributions():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date_str = cell.get("data-date")
        level = cell.get("data-level")
        if date_str is None:
            continue
        count = 0
        # tooltip text sometimes gives the count; fall back to level-based estimate
        tooltip_id = cell.get("id")
        if tooltip_id:
            tip = soup.find("tool-tip", attrs={"for": tooltip_id})
            if tip and tip.text:
                m = re.search(r"([\d,]+)\s+contribution", tip.text)
                if m:
                    count = int(m.group(1).replace(",", ""))
        days.append({
            "date": date_str,
            "level": int(level) if level is not None else 0,
            "count": count,
        })

    days.sort(key=lambda d: d["date"])
    return days

def compute_stats(days):
    total = sum(d["count"] for d in days)
    current_streak = 0
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0
    # current streak counts back from the most recent day
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break
    best_day = max(days, key=lambda d: d["count"], default=None)
    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]
    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
    }

def main():
    days = fetch_contributions()
    stats = compute_stats(days)
    data = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved data/contributions.json — {stats['total']} contributions, "
          f"current streak {stats['current_streak']}, longest {stats['longest_streak']}")

if __name__ == "__main__":
    main()