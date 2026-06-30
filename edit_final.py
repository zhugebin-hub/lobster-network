from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import time

t0 = time.time()

img_path = "/home/admin/.openclaw/media/inbound/290f424b-ede8-410b-8ee3-37f6ba15ed4b.jpg"
img = Image.open(img_path).convert('RGB')
w, h = img.size
print(f"Loaded: {w}x{h}")

result = img.copy()

# ============================================================
# 1. Remove ink bottle - process only the bottle region
# ============================================================
bx1, by1 = int(w*0.160), int(h*0.59)
bx2, by2 = int(w*0.245), int(h*0.90)

# Add margin for sampling
margin = 30
sample_x1 = max(0, bx1 - margin)
sample_y1 = max(0, by1 - margin)
sample_x2 = min(w, bx2 + margin)
sample_y2 = min(h, by2 + margin)

# Crop just the area we need
bottle_area = img.crop((sample_x1, sample_y1, sample_x2, sample_y2))
ba_w, ba_h = bottle_area.size
ba_arr = np.array(bottle_area, dtype=np.uint8)

# Mask: bottle is in the center-right portion of this crop
# Relative to crop: bottle starts at x=(bx1-sample_x1), y=(by1-sample_y1)
rbx1 = bx1 - sample_x1
rby1 = by1 - sample_y1
rbx2 = bx2 - sample_x1
rby2 = by2 - sample_y1

print(f"Bottle crop: {ba_w}x{ba_h}, bottle rect: ({rbx1},{rby1})-({rbx2},{rby2})")

# Create mask for bottle area in the cropped image
mask = np.zeros((ba_h, ba_w), dtype=bool)
mask[rby1:rby2, rbx1:rbx2] = True

# Get border color from pixels just outside the bottle
top_border = ba_arr[rby1-5:rby1, rbx1:rbx2] if rby1 > 5 else ba_arr[rby1, rbx1:rbx2]
bottom_border = ba_arr[rby2:rby2+5, rbx1:rbx2] if rby2+5 < ba_h else ba_arr[rby2, rbx1:rbx2]
left_border = ba_arr[rby1:rby2, max(0,rbx1-5):rbx1]
right_border = ba_arr[rby1:rby2, rbx2:min(ba_w,rbx2+5)]

all_border = np.vstack([
    top_border.reshape(-1, 3),
    bottom_border.reshape(-1, 3),
    left_border.reshape(-1, 3),
    right_border.reshape(-1, 3)
])
border_mean = all_border.mean(axis=0).astype(np.uint8)
print(f"Border color: {border_mean}")

# Fill bottle area with border color + slight gradient
for y in range(rby1, rby2):
    for x in range(rbx1, rbx2):
        t = (y - rby1) / max(rby2 - rby1, 1)
        factor = 1.0 - t * 0.06
        for c in range(3):
            ba_arr[y, x, c] = int(border_mean[c] * factor)

# Smooth the filled area
from scipy.ndimage import gaussian_filter
ba_float = ba_arr.astype(np.float32)
ba_smoothed = gaussian_filter(ba_float, sigma=5).astype(np.uint8)
mask_3d = mask[:, :, np.newaxis]
ba_arr = np.where(mask_3d,
    (ba_arr.astype(np.float32) * 0.35 + ba_smoothed.astype(np.float32) * 0.65).astype(np.uint8),
    ba_arr)

# Second smoother pass for edges
ba_smoothed2 = gaussian_filter(ba_arr.astype(np.float32), sigma=8).astype(np.uint8)
ba_arr = np.where(mask_3d,
    (ba_arr.astype(np.float32) * 0.5 + ba_smoothed2.astype(np.float32) * 0.5).astype(np.uint8),
    ba_arr)

# Paste back
bottle_result = Image.fromarray(ba_arr)
result.paste(bottle_result, (sample_x1, sample_y1))

del ba_arr, ba_smoothed, ba_smoothed2, bottle_result

# ============================================================
# 2. Face enhancement - process only face region
# ============================================================
print("Enhancing face...")
fx1, fy1 = int(w*0.35), int(h*0.07)
fx2, fy2 = int(w*0.53), int(h*0.27)

face = result.crop((fx1, fy1, fx2, fy2))
face_arr = np.array(face, dtype=np.uint8)

# Blur versions
face_s = np.array(face.filter(ImageFilter.GaussianBlur(radius=2)), dtype=np.uint8)
face_m = np.array(face.filter(ImageFilter.GaussianBlur(radius=6)), dtype=np.uint8)
face_l = np.array(face.filter(ImageFilter.GaussianBlur(radius=12)), dtype=np.uint8)

# Edge detection
gray = face_arr.astype(np.float32).mean(axis=2)
sx = np.zeros_like(gray)
sy = np.zeros_like(gray)
sx[1:-1, 1:-1] = (gray[2:,1:-1] - gray[:-2,1:-1]) / 2
sy[1:-1, 1:-1] = (gray[1:-1,2:] - gray[1:-1,:-2]) / 2
edge = np.sqrt(sx**2 + sy**2)
edge_m = np.clip(edge / 40.0, 0, 1)[:, :, np.newaxis]

# Smooth skin, preserve edges
smooth = (face_arr.astype(np.float32)*0.3 + face_s.astype(np.float32)*0.35 +
          face_m.astype(np.float32)*0.2 + face_l.astype(np.float32)*0.15).astype(np.uint8)
face_final = (smooth.astype(np.float32)*(1-edge_m*0.7) +
              face_arr.astype(np.float32)*edge_m*0.7).astype(np.uint8)

# Warm glow
warm = np.array([1.05, 1.02, 0.97], dtype=np.float32)
face_final = np.clip(face_final.astype(np.float32) * warm * 1.04, 0, 255).astype(np.uint8)

# Paste back
result.paste(Image.fromarray(face_final), (fx1, fy1))

del face_arr, face_s, face_m, face_l, smooth, face_final

# ============================================================
# 3. Save
# ============================================================
print("Saving...")
result = result.filter(ImageFilter.UnsharpMask(radius=0.5, percent=6, threshold=2))
output = "/home/admin/.openclaw/workspace/edited_photo.jpg"
result.save(output, 'JPEG', quality=95, subsampling='4:4:4')
print(f"Done! {time.time()-t0:.1f}s")
