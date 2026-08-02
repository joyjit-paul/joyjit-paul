import json

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 12
GAP = 3

def build_svg(out_path="stats-footer.svg"):
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    stats = data["stats"]

    width = 860
    height = 60

    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
                f'font-family="monospace" font-size="13">')
    svg.append(f'<rect width="{width}" height="{height}" fill="none"/>')

    # Legend: Less -> More
    ly = 20
    svg.append(f'<text x="0" y="{ly+5}" fill="#8b949e">Less</text>')
    lx = 40
    for lvl in range(6):
        svg.append(f'<rect x="{lx}" y="{ly-9}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[lvl]}"/>')
        lx += CELL + GAP
    svg.append(f'<text x="{lx+5}" y="{ly+5}" fill="#8b949e">More</text>')

    # Stats line
    footer_text = (f'{stats["total"]:,} contributions in the last year &#183; '
                    f'current streak {stats["current_streak"]} &#183; '
                    f'longest streak {stats["longest_streak"]}')
    svg.append(f'<text x="0" y="{ly+35}" fill="#c9d1d9">{footer_text}</text>')

    svg.append('</svg>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved {out_path}")

if __name__ == "__main__":
    build_svg()