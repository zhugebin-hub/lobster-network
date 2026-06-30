from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter, binary_dilation
import time

t0 = time.time()

# Load as uint8 to save memory
img_path = "/home/admin/.openclaw/media/inbound/290f424b-ede8-410b-8ee3-37f6ba15ed4b.jpg"
img = Image.open(img_path).convert('RGB')
w, h = img.size
arr = np.array(img, dtype=np.uint8)
print(f"Loaded: {w}x{h}, mem: {arr.nbytes/1e6:.0f}MB")

# ============================================================
# 1. Remove ink bottle
# ============================================================
bx1, by1 = int(w*0.165), int(h*0.61)
bx2, by2 = int(w*0.235), int(h*0.87)
cap_top = int(h*0.595)

# Create mask
mask = np.zeros((h, w), dtype=bool)
mask[cap_top:by2, bx1:bx2] = True
mask = binary_dilation(mask, iterations=12)

# Strategy: fill with border color + gradient, then smooth
# Find border pixels
from scipy.ndimage import distance_transform_edt
outer = binary_dilation(mask, iterations=20)
border = outer & ~mask

border_pixels = arr[border]
border_mean = border_pixels.mean(axis=0).astype(np.uint8)
print(f"Border mean: {border_mean}")

# Create fill array (only for masked region to save memory)
arr_result = arr.copy()

# Compute normalized distance within mask
dist = distance_transform_edt(~mask)
max_d = dist[mask].max() if mask.any() else 1

# Fill masked area
y_coords, x_coords = np.where(mask)
for i in range(len(y_coords)):
    y, x = y_coords[i], x_coords[i]
    # Simple gradient: slightly darker toward bottom
    t = (y - by1) / max(by2 - by1, 1)
    factor = 1.0 - t * 0.08
    for c in range(3):
        arr_result[y, x, c] = np.clip(int(border_mean[c] * factor), 0, 255)

print(f"Filled {len(y_coords)} pixels")

# Smooth the filled area with gaussian blur (applied to whole image for blending)
# Use a moderate sigma for smooth blending
print("Smoothing...")
# Only smooth the bottle region - create a masked version
smoothed = gaussian_filter(arr_result.astype(np.float16), sigma=6).astype(np.uint8)

# Blend: in the mask area, use 60% smoothed + 40% original fill
mask_3d = mask[:, :, np.newaxis]
arr_result = np.where(mask_3d,
    (arr_result.astype(np.float16) * 0.4 + smoothed.astype(np.float16) * 0.6).astype(np.uint8),
    arr_result)

# Second blend pass for softer edges
smoothed2 = gaussian_filter(arr_result.astype(np.float16), sigma=10).astype(np.uint8)
arr_result = np.where(mask_3d,
    (arr_result.astype(np.float16) * 0.5 + smoothed2.astype(np.float16) * 0.5).astype(np.uint8),
    arr_result)

# Clean up intermediate arrays
del smoothed, smoothed2, border_pixels

# ============================================================
# 2. Face enhancement
# ============================================================
print("Enhancing face...")
fx1, fy1 = int(w*0.35), int(h*0.07)
fx2, fy2 = int(w*0.53), int(h*0.27)

# Extract face region
face = arr_result[fy1:fy2, fx1:fx2].copy()

# Convert to PIL for filtering
face_pil = Image.fromarray(face)

# Create blurred versions
blur_s = np.array(face_pil.filter(ImageFilter.GaussianBlur(radius=2)), dtype=np.uint8)
blur_m = np.array(face_pil.filter(ImageFilter.GaussianBlur(radius=6)), dtype=np.uint8)
blur_l = np.array(face_pil.filter(ImageFilter.GaussianBlur(radius=12)), dtype=np.uint8)

# Edge detection for preservation
gray = face.astype(np.float16).mean(axis=2)
sx = np.zeros_like(gray)
sy = np.zeros_like(gray)
sx[1:-1] = (gray[2:,1:-1] - gray[:-2,1:-1]) / 2
sy[1:-1] = (gray[1:-1,2:] - gray[1:-1,:-2]) / 2
edge_mag = np.sqrt(sx**2 + sy**2)
edge_mask = np.clip(edge_mag / 40.0, 0, 1)
edge_3d = edge_mask[:, :, np.newaxis]

# Smooth blend
face_smooth = (face.astype(np.float16) * 0.3 +
               blur_s.astype(np.float16) * 0.35 +
               blur_m.astype(np.float16) * 0.2 +
               blur_l.astype(np.float16) * 0.15).astype(np.uint8)

# Preserve edges
face_final = (face_smooth.astype(np.float16) * (1 - edge_3d * 0.7) +
              face.astype(np.float16) * edge_3d * 0.7).astype(np.uint8)

# Warm glow + brightness
warm = np.array([1.05, 1.02, 0.97], dtype=np.float16)
face_final = np.clip(face_final.astype(np.float16) * warm * 1.04, 0, 255).astype(np.uint8)

# Put back
arr_result[fy1:fy2, fx1:fx2] = face_final

del face, face_pil, blur_s, blur_m, blur_l, face_smooth, face_final

# ============================================================
# 3. Save
# ============================================================
print("Saving...")
result = Image.fromarray(arr_result)
result = result.filter(ImageFilter.UnsharpMask(radius=0.5, percent=6, threshold=2))

output = "/home/admin/.openclaw/workspace/edited_photo.jpg"
result.save(output, 'JPEG', quality=95, subsampling='4:4:4')
print(f"Done! {time.time()-t0:.1f}s -> {output}")
