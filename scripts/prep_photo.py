import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove
from io import BytesIO

def prep_photo(input_path, output_path="source-prepped.png"):
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)

    img = Image.open(BytesIO(output_bytes)).convert("RGBA")

    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img).convert("RGB")

    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output_path)
    print(f"Saved prepped photo to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <input-photo>")
        sys.exit(1)
    prep_photo(sys.argv[1])