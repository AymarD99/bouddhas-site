#!/usr/bin/env python3
"""Génère un placeholder JPG thématique local (fallback tant que Pollinations est en rate-limit).
Usage: python3 scripts/gen_placeholder.py <slug> <title> <category>
Produit images/blog/<slug>.jpg (1200x700, fond dégradé or/noir + texte)."""
import sys, os
from PIL import Image, ImageDraw, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{SITE}/images/blog/{sys.argv[1]}.jpg"
title = sys.argv[2] if len(sys.argv)>2 else sys.argv[1]
cat = sys.argv[3] if len(sys.argv)>3 else "Bouddhas"

W,H = 1200,700
img = Image.new("RGB",(W,H),(26,26,44))
draw = ImageDraw.Draw(img)
# Dégradé or en bas
for y in range(H):
    t = y/H
    r = int(26 + t*(201-26))
    g = int(26 + t*(169-26))
    b = int(44 + t*(110-44))
    draw.line([(0,y),(W,y)],fill=(r,g,b))
# Bandeau sombre haut
draw.rectangle([0,0,W,90],fill=(15,15,26))
# Texte catégorie
try:
    f_cat = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",36)
    f_tit = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",58)
except:
    f_cat = f_tit = ImageFont.load_default()
draw.text((W//2,45),cat.upper(),fill=(201,169,110),font=f_cat,anchor="mm")
# Titre (centré, retour à la ligne si long)
words = title.split()
lines=[]; cur=""
for w in words:
    if len(cur+" "+w)<32: cur=(cur+" "+w).strip()
    else: lines.append(cur); cur=w
if cur: lines.append(cur)
y=H//2-30*(len(lines)//2)
for line in lines:
    draw.text((W//2,y),line,fill=(255,255,255),font=f_tit,anchor="mm")
    y+=70
# Logo
draw.text((W//2,H-70),"Bouddhas.fr",fill=(201,169,110),font=f_cat,anchor="mm")
img.save(OUT,"JPEG",quality=85)
print(f"✅ Placeholder: {OUT} ({os.path.getsize(OUT)} bytes)")
