from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import time

start = time.time()

# Load image
img_path = "/home/admin/.openclaw/media/inbound/290f424b-ede8-410b-8ee3-37f6ba15ed4b.jpg"
img = Image.open(img_path).convert('RGB')
w, h = img.size
print(f"Image: {w}x{h}")

# Convert to numpy array for processing
arr = np.array(img, dtype=np.float32)

# ============================================================
# 1. Remove ink bottle (lower-left area)
# ============================================================
# Bottle position (original image ~7728x5152):
# x: ~1270-1800, y: ~3150-4500 (including red cap area)
bx1, by1 = int(w * 0.165), int(h * 0.61)
bx2, by2 = int(w * 0.235), int(h * 0.87)
# Red cap top area
cap_y1 = int(h * 0.595)

# Create mask for bottle region
mask = np.zeros((h, w), dtype=np.bool_)
mask[by1:by2, bx1:bx2] = True
mask[cap_y1:by1, bx1:bx2] = True  # cap area too

# Expand mask slightly to catch edges
from scipy.ndimage import binary_dilation
mask = binary_dilation(mask, iterations=8)

# Inpaint: for each masked pixel, fill with median of surrounding unmasked pixels
print("Inpainting bottle area...")
arr_work = arr.copy()

# Multi-pass from outer edge inward
for radius in [8, 5, 3, 2, 1]:
    print(f"  Pass radius={radius}")
    for y in range(by1 - 20, by2 + 20):
        for x in range(bx1 - 20, bx2 + 20):
            if 0 <= y < h and 0 <= x < w and mask[y, x]:
                # Get surrounding unmasked pixels
                y0, y1p = max(0, y - radius), min(h, y + radius + 1)
                x0, x1p = max(0, x - radius), min(w, x + radius + 1)
                
                region = arr_work[y0:y1p, x0:x1p]
                m_region = mask[y0:y1p, x0:x1p]
                
                valid = region[~m_region]
                if len(valid) > 0:
                    # Use weighted average (closer pixels weighted more)
                    dy, dx = np.ogrid[y0:y1p, x0:x1p]
                    dist = np.sqrt((dy - y)**2 + (dx - x)**2)
                    dist = np.maximum(dist, 0.1)
                    weights = 1.0 / dist
                    weights[m_region] = 0
                    
                    total_w = weights[y0:y1p, x0:x1p][~m_region].sum()
                    if total_w > 0:
                        for c in range(3):
                            val = (weights[y0:y1p, x0:x1p][~m_region] * valid[:, c]).sum() / total_w
                            arr_work[y, x, c] = val

# Smooth the filled area to blend better
from scipy.ndimage import uniform_filter
# Apply slight smoothing only to bottle area
smoothed = uniform_filter(arr_work, size=5)
mask_float = mask.astype(np.float32)[:, :, np.newaxis]
arr_work = arr_work * (1 - mask_float * 0.3) + smoothed * mask_float * 0.3

# ============================================================
# 2. Face enhancement
# ============================================================
# Face area (original ~7728x5152):
# x: ~2700-4000, y: ~350-1400
fx1, fy1 = int(w * 0.35), int(h * 0.07)
fx2, fy2 = int(w * 0.52), int(h * 0.27)

print("Enhancing face...")

# Convert face area to PIL for selective enhancement
face_arr = arr_work[fy1:fy2, fx1:fx2].copy()
face_img = Image.fromarray(face_arr.astype(np.uint8))

# 1. Slight brightness increase for glow
face_img = ImageEnhance.Brightness(face_img).enhance(1.06)

# 2. Slight contrast increase for definition
face_img = ImageEnhance.Contrast(face_img).enhance(1.08)

# 3. Skin smoothing: bilateral-like effect using gaussian blur + overlay
face_arr_np = np.array(face_img, dtype=np.float32)
# Create a smoothed version
face_smooth = np.array(face_img.filter(ImageFilter.GaussianBlur(radius=3)), dtype=np.float32)
# Blend: mostly original, slight smoothing for skin areas (avoiding eyes, glasses, mouth)
# Simple approach: blend 20% smoothed into original for overall softness
face_arr_np = face_arr_np * 0.82 + face_smooth * 0.18

# 4. Add subtle warmth/glow (slight yellow-warm tint for healthy skin)
warmth = np.array([1.02, 1.0, 0.97], dtype=np.float32)  # slightly more red/yellow
face_arr_np = face_arr_np * warmth
face_arr_np = np.clip(face_arr_np, 0, 255).astype(np.uint8)

# Put enhanced face back
arr_work[fy1:fy2, fx1:fx2] = face_arr_np.astype(np.float32)

# ============================================================
# 3. Overall subtle polish
# ============================================================
print("Final polish...")
result_img = Image.fromarray(np.clip(arr_work, 0, 255).astype(np.uint8))

# Slight overall sharpening (unsharp mask equivalent)
result_img = result_img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=8, threshold=3))

# ============================================================
# Save
# ============================================================
output_path = "/home/admin/.openclaw/workspace/edited_photo.jpg"
result_img.save(output_path, 'JPEG', quality=95, subsampling='4:4:4')
print(f"Saved to {output_path}")
print(f"Time: {time.time() - start:.1f}s")
