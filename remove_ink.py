from PIL import Image, ImageFilter
import os

# Load the image
img_path = "/home/admin/.openclaw/media/inbound/290f424b-ede8-410b-8ee3-37f6ba15ed4b.jpg"
img = Image.open(img_path)
w, h = img.size

# The ink bottle is roughly in the lower-left area
# Approximate coordinates (x, y) based on visual inspection:
# x: 15% - 25% of width, y: 60% - 95% of height
# Let me define a rough mask area and use a simple inpainting approach

# Convert to numpy-like operations using PIL
pixels = img.load()

# Define the bottle region (approximate based on visual inspection)
# Bottle is at roughly: left ~18%, top ~62%, right ~24%, bottom ~93%
bottle_x1 = int(w * 0.18)
bottle_y1 = int(h * 0.62)
bottle_x2 = int(w * 0.24)
bottle_y2 = int(h * 0.93)

# Create a copy for modification
img_mod = img.copy()
pixels_mod = img_mod.load()

# Simple inpainting: for each pixel in the bottle area, use average of nearby non-bottle pixels
# We'll do multiple passes

# First, identify non-bottle pixels around the area
def get_surrounding_avg(x, y, img, pixels, mask_func, radius=20):
    r_sum, g_sum, b_sum = 0, 0, 0
    count = 0
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < img.width and 0 <= ny < img.height:
                if not mask_func(nx, ny):
                    r, g, b = pixels[nx, ny][:3]
                    r_sum += r
                    g_sum += g
                    b_sum += b
                    count += 1
    if count == 0:
        return None
    return (r_sum // count, g_sum // count, b_sum // count)

def is_bottle(x, y):
    return bottle_x1 <= x <= bottle_x2 and bottle_y1 <= y <= bottle_y2

# Multi-pass inpainting from edges inward
for pass_num in range(5):
    for y in range(bottle_y1 - 10, bottle_y2 + 10):
        for x in range(bottle_x1 - 10, bottle_x2 + 10):
            if is_bottle(x, y):
                avg = get_surrounding_avg(x, y, img_mod, pixels_mod, is_bottle, radius=15 + pass_num * 5)
                if avg:
                    pixels_mod[x, y] = avg

# Apply a slight blur to smooth transitions in the filled area
# Create a mask for the bottle area + small border
mask_img = Image.new('L', img.size, 0)
from PIL import ImageDraw
draw = ImageDraw.Draw(mask_img)
margin = 10
draw.rectangle([bottle_x1 - margin, bottle_y1 - margin, bottle_x2 + margin, bottle_y2 + margin], fill=255)

# Save the result
output_path = "/home/admin/.openclaw/workspace/edited_photo.jpg"
img_mod.save(output_path, 'JPEG', quality=95)
print(f"Saved to {output_path}")
print(f"Image size: {w}x{h}")
print(f"Bottle area: ({bottle_x1}, {bottle_y1}) to ({bottle_x2}, {bottle_y2})")
