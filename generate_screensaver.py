#!/usr/bin/env python3
"""
Genera el screensaver Admira para Stream Deck XL
- Canvas completo: 768x384 (8 cols x 4 rows x 96px)
- Exporta también los 32 recortes individuales (96x96) para cada botón
"""

from PIL import Image, ImageDraw, ImageFont
import os, math

# ─── Dimensiones Stream Deck XL ───────────────────────────────────────────────
COLS, ROWS = 8, 4
BTN = 96
W, H = COLS * BTN, ROWS * BTN   # 768 x 384

# ─── Paleta Admira ─────────────────────────────────────────────────────────────
BG       = (8,  12,  24)        # azul muy oscuro
GOLD     = (212, 175, 55)       # dorado
GOLD2    = (255, 215, 80)       # dorado claro (glow)
WHITE    = (240, 240, 255)
DIM      = (30,  40,  70)       # azul oscuro para bordes suaves

# ─── Canvas ────────────────────────────────────────────────────────────────────
img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Fondo degradado vertical (arriba oscuro → abajo ligeramente más claro)
for y in range(H):
    t = y / H
    r = int(BG[0] + (20  - BG[0]) * t)
    g = int(BG[1] + (28  - BG[1]) * t)
    b = int(BG[2] + (55  - BG[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Grid de puntos sutiles (estética tech)
for gx in range(0, W, 24):
    for gy in range(0, H, 24):
        draw.ellipse([gx-1, gy-1, gx+1, gy+1], fill=(30, 45, 90))

# Línea horizontal dorada delgada (un tercio desde arriba)
y_line = H // 3
draw.line([(40, y_line), (W-40, y_line)], fill=GOLD, width=1)

# Línea horizontal dorada delgada (dos tercios)
y_line2 = H * 2 // 3
draw.line([(40, y_line2), (W-40, y_line2)], fill=GOLD, width=1)

# ─── Tipografía ────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    """Intenta cargar una fuente del sistema, fallback a default."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SF Pro Display.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Geneva.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

font_title  = load_font(72, bold=True)
font_sub    = load_font(22)
font_tagline = load_font(16)

# ─── Texto principal: "ADMIRA" ─────────────────────────────────────────────────
title = "ADMIRA"
bbox  = draw.textbbox((0, 0), title, font=font_title)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (W - tw) // 2
ty = (H - th) // 2 - 20

# Glow doble (sombra expandida)
for offset in range(6, 0, -1):
    alpha = max(20, 80 - offset * 12)
    glow_color = (GOLD2[0], GOLD2[1], GOLD2[2])
    draw.text((tx - offset, ty), title, font=font_title, fill=glow_color)
    draw.text((tx + offset, ty), title, font=font_title, fill=glow_color)
    draw.text((tx, ty - offset), title, font=font_title, fill=glow_color)
    draw.text((tx, ty + offset), title, font=font_title, fill=glow_color)

# Texto principal dorado
draw.text((tx, ty), title, font=font_title, fill=GOLD)

# ─── Subtítulo: "NEXT" pequeño a la derecha del título ────────────────────────
sub = "NEXT"
bbox_s = draw.textbbox((0, 0), sub, font=font_sub)
sw = bbox_s[2] - bbox_s[0]
# justo debajo del título, alineado a la derecha de él
draw.text((tx + tw - sw, ty + th + 4), sub, font=font_sub, fill=WHITE)

# ─── Tagline ───────────────────────────────────────────────────────────────────
tag = "MacBookAirBlanco  ·  Stream Deck XL"
bbox_t = draw.textbbox((0, 0), tag, font=font_tagline)
tw_t = bbox_t[2] - bbox_t[0]
draw.text(((W - tw_t) // 2, H - 28), tag, font=font_tagline, fill=(80, 100, 150))

# ─── Marco exterior sutil ──────────────────────────────────────────────────────
draw.rectangle([2, 2, W-3, H-3], outline=(30, 50, 90), width=2)

# ─── Exportar canvas completo ──────────────────────────────────────────────────
out_dir = os.path.dirname(os.path.abspath(__file__))
full_path = os.path.join(out_dir, "screensaver_admira_full.png")
img.save(full_path)
print(f"Canvas completo: {full_path}")

# ─── Exportar 32 recortes individuales (96x96) ────────────────────────────────
slices_dir = os.path.join(out_dir, "screensaver_slices")
os.makedirs(slices_dir, exist_ok=True)

for row in range(ROWS):
    for col in range(COLS):
        x0 = col * BTN
        y0 = row * BTN
        slice_img = img.crop((x0, y0, x0 + BTN, y0 + BTN))
        fname = f"{col},{row}.png"
        slice_img.save(os.path.join(slices_dir, fname))

print(f"32 recortes en: {slices_dir}/")
print("Listo.")
