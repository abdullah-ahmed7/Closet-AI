import colorsys
NEUTRAL_NAMES = {
    "black", "white", "gray", "light gray", "charcoal",
    "beige", "cream", "khaki", "navy",
}

def rgb_to_hue(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v

def is_neutral(color_name, saturation=None):
    if color_name in NEUTRAL_NAMES:
        return True
    if saturation is not None and saturation < 0.15:
        return True
    return False

def color_match_score(rgb_a, name_a, rgb_b, name_b):
    hue_a, sat_a, _ = rgb_to_hue(rgb_a)
    hue_b, sat_b, _ = rgb_to_hue(rgb_b)
    if is_neutral(name_a, sat_a) or is_neutral(name_b, sat_b):
        return 90  
    diff = abs(hue_a - hue_b)
    diff = min(diff, 360 - diff)  
    if diff <= 40:
        return 85 
    if 150 <= diff <= 210:
        return 80  
    if 40 < diff < 150:
        return 45 
    return 55  

def formality_compatible(formality_a, formality_b):
    if formality_a == formality_b:
        return True
    pair = {formality_a, formality_b}
    if pair == {"business", "formal"}:
        return True
    if pair == {"semi-formal", "business"}:
        return True
    if pair == {"semi-formal", "casual"}:
        return True
    return False

def multi_color_match_score(colors_a, colors_b):
    best = 0
    for ca in colors_a:
        for cb in colors_b:
            score = color_match_score(ca["rgb"], ca["name"], cb["rgb"], cb["name"])
            if score > best:
                best = score
    return best