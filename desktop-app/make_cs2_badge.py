"""
Generates ultra-crisp, high-fidelity CS2 Command Center badge icons.
Outputs app.png and app.ico with multi-resolution layers (256, 128, 64, 48, 32, 16).
"""
import math
from PIL import Image, ImageDraw, ImageFont

def create_cs2_icon():
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 1. Outer tactical glow / shadow
    for offset in range(6, 0, -1):
        alpha = int(25 * (7 - offset) / 6)
        d.rounded_rectangle(
            (24 - offset, 24 - offset, size - 24 + offset, size - 24 + offset),
            radius=110,
            fill=(249, 115, 22, alpha)
        )

    # 2. Outer dark tactical shield base
    d.rounded_rectangle(
        (24, 24, size - 24, size - 24),
        radius=100,
        fill="#0b0e14",
        outline="#1e293b",
        width=4
    )

    # 3. Inner tactical carbon frame
    d.rounded_rectangle(
        (40, 40, size - 40, size - 40),
        radius=84,
        fill="#121824",
        outline="#ea580c",
        width=8
    )

    # 4. Subtle tactical crosshair / sniper reticle lines
    cx, cy = size // 2, size // 2
    reticle_col = (234, 88, 12, 60)
    # Circle reticle
    d.ellipse((cx - 160, cy - 160, cx + 160, cy + 160), outline=reticle_col, width=3)
    d.ellipse((cx - 210, cy - 210, cx + 210, cy + 210), outline=(56, 189, 248, 40), width=2)
    # Crosshair tick marks
    d.line((cx - 220, cy, cx - 170, cy), fill=reticle_col, width=4)
    d.line((cx + 170, cy, cx + 220, cy), fill=reticle_col, width=4)
    d.line((cx, cy - 220, cx, cy - 170), fill=reticle_col, width=4)
    d.line((cx, cy + 170, cx, cy + 220), fill=reticle_col, width=4)

    # 5. Corner tactical hash marks (CS:GO / CS2 UI aesthetic)
    d.polygon([(65, 75), (85, 55), (95, 55), (65, 85)], fill="#f97316")
    d.polygon([(size - 65, 75), (size - 85, 55), (size - 95, 55), (size - 65, 85)], fill="#f97316")
    d.polygon([(65, size - 75), (85, size - 55), (95, size - 55), (65, size - 85)], fill="#f97316")
    d.polygon([(size - 65, size - 75), (size - 85, size - 55), (size - 95, size - 55), (size - 65, size - 85)], fill="#f97316")

    # 6. High-impact CS 2 Center Typography
    # Try loading bold Windows system font
    font_bold = None
    font_sub = None
    for fpath in ["C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]:
        try:
            font_bold = ImageFont.truetype(fpath, 175)
            font_sub = ImageFont.truetype(fpath, 42)
            break
        except Exception:
            pass

    if not font_bold:
        font_bold = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw "CS" in white with dark drop shadow
    # Text positions
    # Drop shadow
    d.text((82, 122), "CS", font=font_bold, fill="#000000")
    d.text((78, 118), "CS", font=font_bold, fill="#ffffff")

    # Draw "2" in vibrant electric CS2 orange
    d.text((314, 122), "2", font=font_bold, fill="#7c2d12")
    d.text((310, 118), "2", font=font_bold, fill="#ff7a00")

    # 7. Subtitle badge: "COMMAND CENTER"
    badge_y = 350
    d.rounded_rectangle((75, badge_y, size - 75, badge_y + 64), radius=14, fill="#0f172a", outline="#ea580c", width=3)

    # Subtitle text
    bbox = d.textbbox((0, 0), "COMMAND CENTER", font=font_sub)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    d.text((tx, badge_y + 11), "COMMAND CENTER", font=font_sub, fill="#f8fafc")

    # Small top tactical status bar
    d.rounded_rectangle((180, 52, size - 180, 62), radius=4, fill="#22c55e")

    # Save 512x512 PNG
    img.save("app.png", format="PNG")
    print("Saved app.png (512x512)")

    # Save Multi-resolution ICO
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save("app.ico", format="ICO", sizes=icon_sizes)
    print("Saved app.ico with layers:", icon_sizes)

if __name__ == "__main__":
    create_cs2_icon()
