import os
from PIL import Image, ImageDraw

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw.ellipse([2, 2, 62, 62], fill="#89b4fa")

draw.rounded_rectangle([14, 12, 50, 52], radius=4, fill="#1e1e2e")

draw.rectangle([18, 16, 46, 22], fill="#89b4fa")
draw.text((21, 14), "=", fill="#1e1e2e")

draw.rectangle([18, 26, 30, 32], fill="#313244")
draw.rectangle([34, 26, 46, 32], fill="#313244")
draw.rectangle([18, 36, 30, 42], fill="#313244")
draw.rectangle([34, 36, 46, 42], fill="#313244")

draw.text((21, 24), "7", fill="#cdd6f4")
draw.text((35, 24), "8", fill="#cdd6f4")
draw.text((21, 34), "4", fill="#cdd6f4")
draw.text((35, 34), "5", fill="#cdd6f4")

path = os.path.join(os.path.dirname(__file__), "icon.png")
img.save(path)
print(f"icon.png erstellt: {path}")
