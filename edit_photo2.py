from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

print("Loading image...")
img_path = "/home/admin/.openclaw/media/inbound/290f424b-ede8-410b-8ee3-37f6ba15ed4b.jpg"
img = Image.open(img_path).convert('RGB')
w, h = img.size
print(f"Size: {w}x{h}")

arr = np.array(img, dtype=np.float32)

# ============================================================
# 1. Remove ink bottle
# ============================================================
# Bottle at roughly: x=1280-1750, y=3150-4500 (plus red cap y=3050-3150)
bx1, by1 = int(w*0.165), int(h*0.61)
bx2, by2 = int(w*0.235), int(h*0.87)
cap_top = int(h*0.595)

# Create binary mask
mask = np.zeros((h, w), dtype=bool)
mask[cap_top:by2, bx1:bx2] = True
# Expand mask a bit
mask[max(0,cap_top-10):min(h,by2+10), max(0,bx1-10):min(w,bx2+10)] = True

print("Inpainting bottle area...")
# For each masked pixel, sample from surrounding valid pixels
# Use a faster approach: compute once from nearby valid pixels
arr_result = arr.copy()

# Process row by row, for each masked pixel use average of valid neighbors in a window
window = 15
for y in range(cap_top - window, by2 + window):
    for x in range(bx1 - window, bx2 + window):
        if not (0 <= y < h and 0 <= x < w and mask[y, x]):
            continue
        # Collect valid neighbors
        ylo, yhi = max(0, y-window), min(h, y+window+1)
        xlo, xhi = max(0, x-window), min(w, x+window+1)
        valid_mask = ~mask[ylo:yhi, xlo:xhi]
        if valid_mask.any():
            vals = arr[ylo:yhi, xlo:xhi][valid_mask]
            # Weighted by distance (inverse)
            yy, xx = np.ogrid[ylo:yhi, xlo:xhi]
            d = np.sqrt((yy-y)**2 + (xx-x)**2)
            d = np.maximum(d, 0.5)
            wts = 1.0 / d
            wts_valid = wts[ylo:yhi, xlo:xhi][valid_mask]
            wts_valid = wts_valid / wts_valid.sum()
            arr_result[y, x] = (wts_valid[:, None] * vals).sum(axis=0)

# Smooth the filled region
print("Smoothing filled area...")
filled_region = mask.astype(np.float32)
from scipy.ndimage import gaussian_filter
smoothed = gaussian_filter(arr_result, sigma=3)
blend = np.clip(filled_region[:, :, None] * 0.4, 0, 1)
arr_result = arr_result * (1 - blend) + smoothed * blend

# ============================================================
# 2. Face enhancement - make skin smooth and radiant
# ============================================================
print("Enhancing face...")
# Face area: roughly x=2700-4100, y=350-1400
fx1, fy1 = int(w*0.35), int(h*0.07)
fx2, fy2 = int(w*0.53), int(h*0.27)

face = arr_result[fy1:fy2, fx1:fx2].copy()
face_uint8 = np.clip(face, 0, 255).astype(np.uint8)
face_pil = Image.fromarray(face_uint8)

# Bilateral-like smoothing for skin (preserve edges)
# Use a combination of gaussian blur and edge detection to smooth skin areas
face_blur1 = np.array(face_pil.filter(ImageFilter.GaussianBlur(radius=2)), dtype=np.float32)
face_blur2 = np.array(face_pil.filter(ImageFilter.GaussianBlur(radius=5)), dtype=np.float32)

# Detect edges to preserve them
gray = face_uint8.astype(np.float32).mean(axis=2)
from scipy.ndimage import sobel
sx = sobel(gray.astype(np.float64))
sy = sobel(gray.astype(np.float64), axes=1)
edges = np.sqrt(sx**2 + sy**2)
edge_mask = (edges > 30).astype(np.float32)

# Blend: smooth areas get more blur, edge areas keep detail
smooth_face = face.astype(np.float32) * 0.5 + face_blur1 * 0.3 + face_blur2 * 0.2
# Preserve edges
edge_preserved = smooth_face * (1 - edge_mask[:,:,None]*0.6) + face.astype(np.float32) * edge_mask[:,:,None]*0.6

# Add glow/radiance - slight brightness boost on midtones
glow = np.array([1.04, 1.02, 0.98], dtype=np.float32)  # warm glow
face_enhanced = np.clip(edge_preserved * glow, 0, 255).astype(np.float32)

# Add slight saturation boost for healthy skin
from PIL import ImageEnhance
face_pil2 = Image.fromarray(np.clip(face_enhanced, 0, 255).astype(np.uint8))
face_pil2 = ImageEnhance.Color(face_pil2).enhance(1.05)
face_pil2 = ImageEnhance.Brightness(face_pil2).enhance(1.03)
face_enhanced = np.array(face_pil2, dtype=np.float32)

arr_result[fy1:fy2, fx1:fx2] = face_enhanced

# ============================================================
# 3. Save
# ============================================================
print("Saving...")
result = Image.fromarray(np.clip(arr_result, 0, 255).astype(np.uint8))
# Slight overall sharpness
result = result.filter(ImageFilter.UnsharpMask(radius=0.5, percent=5, threshold=2))

output = "/home/admin/.openclaw/workspace/edited_photo.jpg"
result.save(output, 'JPEG', quality=95, subsampling='4:4:4')
print(f"Saved! {output}")
