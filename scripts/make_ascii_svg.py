import sys
from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
COLS = 100
ROWS = 53
FONT_W = 7      # approx monospace char width in px at chosen font-size
FONT_H = 13     # approx monospace line height in px
FILL_COLOR = "#c9d1d9"   # light gray, monochrome

def image_to_ascii_rows(image_path, cols=COLS, rows=ROWS):
    img = Image.open(image_path).convert("L")
    img = img.resize((cols, rows))
    pixels = list(img.getdata())

    ascii_rows = []
    ramp_len = len(RAMP)
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0=black, 255=white
            # Map brightness (0-255) to ramp index (dense->sparse as brightness rises)
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))
    return ascii_rows

def escape_xml(s):
    return (s.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;"))

def build_svg(ascii_rows, out_path="avi-ascii.svg"):
    width = COLS * FONT_W
    height = ROWS * FONT_H

    svg_parts = []
    svg_parts.append(f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
                      f'font-family="monospace" font-size="{FONT_H - 2}">')
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="none"/>')
    svg_parts.append(f'<style>')
    svg_parts.append(f'text {{ fill: {FILL_COLOR}; white-space: pre; }}')
    for r in range(ROWS):
        delay = r * 0.05
        svg_parts.append(f'''
        .row{r} {{
            clip-path: inset(0 100% 0 0);
            animation: wipe{r} 0.4s steps(30) forwards;
            animation-delay: {delay:.2f}s;
        }}
        @keyframes wipe{r} {{
            to {{ clip-path: inset(0 0 0 0); }}
        }}
        ''')
    svg_parts.append('</style>')

    for r, row in enumerate(ascii_rows):
        y = (r + 1) * FONT_H
        escaped = escape_xml(row)
        svg_parts.append(
            f'<text class="row{r}" x="0" y="{y}" xml:space="preserve">{escaped}</text>'
        )

    svg_parts.append('</svg>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"Saved {out_path}")

if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    rows = image_to_ascii_rows(input_path)
    build_svg(rows)