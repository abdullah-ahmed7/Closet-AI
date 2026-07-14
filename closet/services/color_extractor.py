from PIL import Image
import numpy as np
import colorsys

def _rgb_to_hsv(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v

def name_color(rgb):
    h, s, v = _rgb_to_hsv(rgb)
    if v < 0.15:
        return "black"
    if s < 0.12:
        if v > 0.90:
            return "white"
        if v > 0.65:
            return "light gray"
        if v > 0.35:
            return "gray"
        return "charcoal"
    if h < 15 or h >= 345:
        base = "red"
    elif h < 45:
        base = "orange"
    elif h < 65:
        base = "yellow"
    elif h < 90:
        base = "olive"
    elif h < 150:
        base = "green"
    elif h < 200:
        base = "teal"
    elif h < 250:
        base = "blue"
    elif h < 290:
        base = "purple"
    elif h < 330:
        base = "pink"
    else:
        base = "red"
    if v < 0.45 and base == "red":
        return "maroon"
    if v < 0.45 and base == "orange":
        return "brown"
    if v < 0.35 and base == "blue":
        return "navy"
    return base

def _kmeans(pixels, k, n_iter=15, seed=42):
    rng = np.random.default_rng(seed)
    n_samples = len(pixels)
    k = min(k, n_samples)
    centers = [pixels[rng.integers(n_samples)]]
    for _ in range(k - 1):
        dists = np.min(
            [np.sum((pixels - c) ** 2, axis=1) for c in centers], axis=0
        )
        probs = dists / dists.sum() if dists.sum() > 0 else None
        next_idx = rng.choice(n_samples, p=probs) if probs is not None else rng.integers(n_samples)
        centers.append(pixels[next_idx])
    centers = np.array(centers, dtype=float)
    labels = np.zeros(n_samples, dtype=int)
    for _ in range(n_iter):
        dists = np.array([np.sum((pixels - c) ** 2, axis=1) for c in centers])
        new_labels = np.argmin(dists, axis=0)
        if np.array_equal(new_labels, labels) and _ > 0:
            break
        labels = new_labels
        for i in range(k):
            mask = labels == i
            if mask.any():
                centers[i] = pixels[mask].mean(axis=0)
    return labels, centers

def _detect_background_rgb(arr):
    h, w, _ = arr.shape
    corners = [arr[0, 0], arr[0, w - 1], arr[h - 1, 0], arr[h - 1, w - 1]]
    return np.mean(corners, axis=0)

def extract_colors(image_source, max_colors=2, resize_to=150):
    img = Image.open(image_source).convert("RGB")
    img.thumbnail((resize_to, resize_to))
    arr = np.array(img)
    pixels = arr.reshape(-1, 3).astype(float)
    bg_rgb = _detect_background_rgb(arr)
    dist_to_bg = np.linalg.norm(pixels - bg_rgb, axis=1)
    fg_mask = dist_to_bg > 35
    foreground = pixels[fg_mask]
    if len(foreground) < 50:
        foreground = pixels
    k = min(max_colors + 2, max(2, len(foreground) // 20))
    labels, centers = _kmeans(foreground, k)
    label_ids, counts = np.unique(labels, return_counts=True)
    total = counts.sum()
    ranked = sorted(zip(label_ids, counts), key=lambda lc: -lc[1])
    results = []
    for label, count in ranked:
        weight = count / total
        if weight < 0.06:  # ignore noise clusters under 6% of foreground
            continue
        rgb = tuple(int(c) for c in centers[label])
        # Merge in near-duplicate colors already picked (e.g. two shades
        # of the same fabric under different lighting/folds)
        if any(sum(abs(a - b) for a, b in zip(rgb, r["rgb"])) < 40 for r in results):
            continue
        results.append({
            "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            "rgb": rgb,
            "name": name_color(rgb),
            "weight": round(float(weight), 2),
        })
        if len(results) >= max_colors:
            break
    if not results:
        rgb = tuple(int(c) for c in foreground.mean(axis=0))
        results.append({
            "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            "rgb": rgb,
            "name": name_color(rgb),
            "weight": 1.0,
        })
    return results

def extract_dominant_color(image_source, k=3, resize_to=100):
    colors = extract_colors(image_source, max_colors=1, resize_to=resize_to)
    return colors[0]

if __name__ == "__main__":
    test_img = Image.new("RGB", (200, 200), (212, 211, 211))
    test_path = "/tmp/test_gray.png"
    test_img.save(test_path)
    result = extract_dominant_color(test_path)
    print("Gray swatch result:", result)
    assert result["name"] in ("light gray", "gray", "white"), "Bug regression!"
    print("Bug-fix sanity check passed.")
    two_tone = Image.new("RGB", (200, 200), (255, 255, 255))
    pixels_arr = np.array(two_tone)
    pixels_arr[:, :100] = (200, 30, 30)
    pixels_arr[:, 100:] = (30, 30, 200)
    Image.fromarray(pixels_arr).save("/tmp/test_two_tone.png")
    results = extract_colors("/tmp/test_two_tone.png", max_colors=2)
    print("Two-tone result:", results)
    assert len(results) == 2, "Should detect 2 distinct colors"
    print("Multi-color sanity check passed.")