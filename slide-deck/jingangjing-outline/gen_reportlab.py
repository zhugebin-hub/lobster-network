#!/usr/bin/env python3
"""Generate slide PNGs using reportlab with proper CJK font support."""
import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import Paragraph, SimpleDocTemplate, BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Ellipse, Line, Polygon
from reportlab.graphics import renderPM
from PIL import Image

SLIDE_DIR = "/home/admin/.openclaw/workspace/slide-deck/jingangjing-outline"
W, H = 1280, 720

# Colors
BG = HexColor("#FAF8F0")
INK = HexColor("#2D2D2D")
GRAY = HexColor("#5D5D5D")
LIGHT = HexColor("#9D9D9D")
GOLD = HexColor("#D4A84B")
CORAL = HexColor("#F4A261")
SAGE = HexColor("#87A96B")
SKY = HexColor("#7EC8E3")
ROSE = HexColor("#E8A0A0")

# Register CJK font
CJK_FONT = "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc"
pdfmetrics.registerFont(TTFont("CJK", CJK_FONT))

def gen_slide(filename, draw_func):
    """Generate a slide by calling draw_func on a PIL Image."""
    img = Image.new("RGB", (W, H), "#FAF8F0")
    draw_func(img)
    img.save(os.path.join(SLIDE_DIR, filename))
    print(f"  {filename}")

def main():
    print("Generating slides with reportlab + PIL...")

    # Slide 1: Cover
    def draw_cover(img):
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        # Mountain bg
        import math
        pts = []
        for x in range(0, W+20, 20):
            y = H-60+int(40*math.sin(x*0.008)+25*math.sin(x*0.015+1)+15*math.cos(x*0.02))
            pts.append((x, y))
        pts.extend([(W,H),(0,H)])
        d.polygon(pts, fill="#2D2D2D0A")
        # Title
        d.text((200, 200), "金刚般若波罗蜜经", font=TTFont("CJK", CJK_FONT).font, fill=INK)

    # Actually let me just test if reportlab TTFont works
    from reportlab.pdfbase.ttfonts import TTFont
    font = TTFont("CJK", CJK_FONT)
    print(f"Font registered: {font.fontName}")

    # Let me try a completely different approach - use reportlab to generate PDF, then convert to PNG
    print("Trying reportlab PDF approach...")

if __name__ == "__main__":
    main()
