import os
import textwrap

WIDTH = 560
LINE_HEIGHT = 24
PADDING_TOP = 60
FONT_SIZE = 15
TITLE_BAR_H = 40
CHAR_W = 9.1  # approx monospace char width at FONT_SIZE=15

FIELDS = [
    ("Now",         "Research Intern @ ELITE Research Lab (NLP/CV/Medical Imaging)"),
    ("Prev",        "Content Writer @ EduMox"),
    ("Edu",         "B.Sc. CSE, Port City International University ('2024)"),
    ("Stack",       "Python, TensorFlow, PyTorch, OpenCV, ReactJS"),
    ("Research",    "5 papers+ | 2 in IEEE Xplore | 1 Q3 journal (under review)"),
    ("Highlights",  "98% deepfake detection acc. | 96.3% breast cancer diagnosis acc."),
    ("Talks",       "IEEE ICCIT 2025 & ICECTE 2026 conference presenter"),
]
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLE_COLOR = "#58a6ff"
KEY_COLOR = "#7ee787"
VAL_COLOR = "#c9d1d9"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]
LEFT_PAD = 20
RIGHT_PAD = 20

def escape_xml(s):
    return (s.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;"))

def wrap_value(key, value):
    """Wrap value text to fit width, indenting continuation lines under the value start."""
    key_prefix_len = len(key) + 2  # "key: "
    avail_px = WIDTH - LEFT_PAD - RIGHT_PAD
    max_chars_first = max(10, int(avail_px / CHAR_W) - key_prefix_len)
    max_chars_cont = max(10, int(avail_px / CHAR_W))
    wrapped = textwrap.wrap(value, width=max_chars_first) if len(value) > max_chars_first else [value]
    if len(wrapped) > 1:
        # re-wrap more evenly using continuation width for lines after the first
        wrapped = [wrapped[0]] + textwrap.wrap(value[len(wrapped[0]):].strip(), width=max_chars_cont)
    return wrapped

def build_svg(out_path="info-card.svg"):
    static = os.environ.get("STATIC") == "1"

    # Pre-wrap all fields to compute total line count / height
    wrapped_fields = [(k, wrap_value(k, v)) for k, v in FIELDS]
    total_lines = sum(len(lines) for _, lines in wrapped_fields)
    height = PADDING_TOP + total_lines * LINE_HEIGHT + 20

    svg = []
    svg.append(f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
                f'font-family="monospace" font-size="{FONT_SIZE}">')

    svg.append(f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="8" '
                f'fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>')

    svg.append(f'<rect x="0" y="0" width="{WIDTH}" height="{TITLE_BAR_H}" rx="8" fill="{BG_COLOR}"/>')
    for i, color in enumerate(DOT_COLORS):
        cx = LEFT_PAD + i * 20
        svg.append(f'<circle cx="{cx}" cy="{TITLE_BAR_H/2}" r="6" fill="{color}"/>')
    svg.append(f'<text x="{WIDTH/2}" y="{TITLE_BAR_H/2 + 5}" text-anchor="middle" '
                f'fill="{TITLE_COLOR}">neofetch</text>')

    svg.append('<style>')
    if not static:
        svg.append('.line { opacity: 0; animation: fadeIn 0.4s ease forwards; }')
        idx = 0
        for _, lines in wrapped_fields:
            for _ in lines:
                delay = 0.3 + idx * 0.15
                svg.append(f'.line{idx} {{ animation-delay: {delay:.2f}s; }}')
                idx += 1
        svg.append('@keyframes fadeIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }')
    svg.append('</style>')

    y = PADDING_TOP
    idx = 0
    for key, lines in wrapped_fields:
        for li, line in enumerate(lines):
            cls = "" if static else f'class="line line{idx}"'
            if li == 0:
                svg.append(f'<text {cls} x="{LEFT_PAD}" y="{y}">'
                            f'<tspan fill="{KEY_COLOR}">{escape_xml(key)}</tspan>'
                            f'<tspan fill="{VAL_COLOR}">: {escape_xml(line)}</tspan>'
                            f'</text>')
            else:
                svg.append(f'<text {cls} x="{LEFT_PAD}" y="{y}">'
                            f'<tspan fill="{VAL_COLOR}">{escape_xml(line)}</tspan>'
                            f'</text>')
            y += LINE_HEIGHT
            idx += 1

    svg.append('</svg>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved {out_path}")

if __name__ == "__main__":
    build_svg()