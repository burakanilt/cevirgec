import numpy as np
from PIL import Image, ImageDraw

# Create a dummy image with shadow
img = Image.new('L', (300, 200), color=200) # grayish background (shadow)
draw = ImageDraw.Draw(img)
# Draw some dark text/signature
draw.text((50, 80), "Signature", fill=50, align="center")
# Add some lighter shadow part
draw.rectangle([0,0, 100, 200], fill=150)

img.save("dummy_sig.jpg")

# Otsu extraction
arr = np.array(img)
hist, _ = np.histogram(arr.flatten(), 256, [0,256])
hist_norm = hist.astype(float) / arr.size
omega = np.cumsum(hist_norm)
mu = np.cumsum(hist_norm * np.arange(256))
mu_t = mu[-1]

with np.errstate(divide='ignore', invalid='ignore'):
    sigma_b_squared = (mu_t * omega - mu)**2 / (omega * (1 - omega))
threshold = np.nanargmax(sigma_b_squared)

print(f"Calculated Threshold: {threshold}")

rgba = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
is_sig = arr < threshold
rgba[is_sig, 0] = 0
rgba[is_sig, 1] = 0
rgba[is_sig, 2] = 0
rgba[is_sig, 3] = 255

coords = np.argwhere(is_sig)
if coords.size > 0:
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    rgba = rgba[y0:y1+1, x0:x1+1]

out = Image.fromarray(rgba, 'RGBA')
out.save("dummy_sig_transparent.png")
print("Saved transparent PNG.")
