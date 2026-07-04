from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter, binary_dilation
import time

t0 = time.time()

# Load
img_path = "/home/admin/.openclaw/media/inbound/290f424b-ede8-410b-8ee3-37f6ba15ed4b.jpg"
img = Image.open(img_path).convert('RGB')
w, h = img.size
arr = np.array(img, dtype=np.float32)
print(f"Loaded: {w}x{h}")

# ============================================================
# 1. Remove ink bottle - vectorized approach
# ============================================================
bx1, by1 = int(w*0.165), int(h*0.61)
bx2, by2 = int(w*0.235), int(h*0.87)
cap_top = int(h*0.595)

# Create mask
mask = np.zeros((h, w), dtype=bool)
mask[cap_top:by2, bx1:bx2] = True

# Dilate to catch edges
mask = binary_dilation(mask, iterations=12)

# Strategy: fill bottle area with a smooth blend from the surrounding border
# Compute the average color of the immediate border around the bottle
arr_result = arr.copy()

# Create a dilated mask to find the border region
inner_mask = mask.copy()
outer_mask = binary_dilation(mask, iterations=25)
border = outer_mask & ~inner_mask

# Get border pixel colors
border_pixels = arr[border]
if len(border_pixels) > 0:
    border_mean = border_pixels.mean(axis=0)
else:
    border_mean = arr[by1-5:by1, :].mean(axis=(0,1))

print(f"Border mean color: {border_mean}")

# Fill the bottle area with border color + slight gradient
# Create distance transform from the mask boundary
from scipy.ndimage import distance_transform_edt
# distance from each masked pixel to the nearest unmasked pixel
dist = distance_transform_edt(~mask)
# Normalize to 0-1 within the bottle area
max_dist = dist[mask].max() if mask.any() else 1
dist_norm = np.zeros((h, w))
dist_norm[mask] = dist[mask] / max_dist

# Use border color as base, with slight variation based on position
fill_color = border_mean.copy()
# Add slight gradient: slightly darker at bottom (simulating floor shadow continuation)
gradient_y = np.zeros((h, w))
if mask.any():
    y_coords = np.ogrid[:h, :w][0][mask]
    gradient_y[mask] = (y_coords - by1) / (by2 - by1) * 0.1  # 10% darker at bottom

for c in range(3):
    arr_result[mask, c] = fill_color[c] * (1 - gradient_y[mask])

# Smooth the fill to blend with surroundings
print("Smoothing bottle area...")
smoothed_arr = gaussian_filter(arr_result, sigma=5)
# Blend: heavily blend the fill area with smoothed version
fill_mask_3d = mask[:, :, np.newaxis].astype(np.float32)
# For the filled area, use a mix of the filled color and smoothed version
arr_result = arr_result * (1 - fill_mask_3d * 0.7) + smoothed_arr * fill_mask_3d * 0.7

# Additional smoothing pass for better blending
smoothed2 = gaussian_filter(arr_result, sigma=8)
arr_result = arr_result * (1 - fill_mask_3d * 0.3) + smoothed2 * fill_mask_3d * 0.3

# ============================================================
# 2. Face enhancement
# ============================================================
print("Enhancing face...")
fx1, fy1 = int(w*0.35), int(h*0.07)
fx2, fy2 = int(w*0.53), int(h*0.27)

face = arr_result[fy1:fy2, fx1:fx2].copy()

# Multi-scale blur for skin smoothing
blur_s = np.array(Image.fromarray(np.clip(face,0,255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(radius=2)), dtype=np.float32)
blur_m = np.array(Image.fromarray(np.clip(face,0,255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(radius=6)), dtype=np.float32)
blur_l = np.array(Image.fromarray(np.clip(face,0,255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(radius=12)), dtype=np.float32)

# Edge detection to preserve details (glasses, eyes, mouth)
gray = face.mean(axis=2)
sx = np.zeros_like(gray)
sy = np.zeros_like(gray)
sx[1:-1] = (gray[2:,1:-1] - gray[:-2,1:-1]) / 2
sy[1:-1] = (gray[1:-1,2:] - gray[1:-1,:-2]) / 2
edge_mag = np.sqrt(sx**2 + sy**2)
edge_mask = np.clip(edge_mag / 40.0, 0, 1).astype(np.float32)
edge_mask_3d = edge_mask[:, :, np.newaxis]

# Combine: smooth version for skin, preserve edges
face_smooth = face * 0.3 + blur_s * 0.35 + blur_m * 0.2 + blur_l * 0.15
face_preserved = face_smooth * (1 - edge_mask_3d * 0.7) + face * edge_mask_3d * 0.7

# Add warm glow
warm = np.array([1.05, 1.02, 0.97])
face_glow = np.clip(face_preserved * warm, 0, 255)

# Slight brightness boost for radiance
face_glow = np.clip(face_glow * 1.04, 0, 255)

arr_result[fy1:fy2, fx1:fx2] = face_glow

# ============================================================
# 3. Subtle overall sharpening
# ============================================================
print("Sharpening...")
result = Image.fromarray(np.clip(arr_result, 0, 255).astype(np.uint8))
result = result.filter(ImageFilter.UnsharpMask(radius=0.5, percent=6, threshold=2))

# ============================================================
# 4. Save at full resolution
# ============================================================
output = "/home/admin/.openclaw/workspace/edited_photo.jpg"
result.save(output, 'JPEG', quality=95, subsampling='4:4:4')
print(f"Done! {time.time()-t0:.1f}s -> {output}")
