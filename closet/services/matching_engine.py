from services.color_theory import multi_color_match_score, formality_compatible
from db.queries import get_item_colors

CONTEXT_FORMALITY_MAP = {
    "office": ["semi-formal", "business", "formal"],
    "university": ["casual", "semi-formal", "business"],
    "friend": ["casual", "semi-formal"],
    "trip": ["casual", "semi-formal"],
}
MAX_COMBO_OPTIONS = 3

def _filter_by_context(items, context):
    allowed = CONTEXT_FORMALITY_MAP.get(context, ["casual", "semi-formal", "business", "formal"])
    return [item for item in items if item["formality"] in allowed]

def _filter_by_season(items, season):
    if not season or season == "all-season":
        return items
    return [i for i in items if i.get("season", "all-season") in (season, "all-season")]

def _ranked_matches(candidates_pool, pant_or_shirt_formality, reference_colors):
    matches = []
    for candidate in candidates_pool:
        if not formality_compatible(candidate["formality"], pant_or_shirt_formality):
            continue
        score = multi_color_match_score(get_item_colors(candidate), reference_colors)
        matches.append({"item": candidate, "score": round(score, 1)})
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches[:MAX_COMBO_OPTIONS]

def suggest_outfits(all_items, context, season=None, top_n=None):
    seasonal_items = _filter_by_season(all_items, season)
    context_items = _filter_by_context(seasonal_items, context)
    shirts = [i for i in context_items if i["category"] == "shirt"]
    pants = [i for i in context_items if i["category"] == "pant"]
    shoes_list = [i for i in context_items if i["category"] == "shoes"]
    accessories = [i for i in context_items if i["category"] == "accessory"]
    candidates = []
    for shirt in shirts:
        for pant in pants:
            if not formality_compatible(shirt["formality"], pant["formality"]):
                continue
            shirt_colors = get_item_colors(shirt)
            pant_colors = get_item_colors(pant)
            base_score = multi_color_match_score(shirt_colors, pant_colors)
            shoe_options = _ranked_matches(shoes_list, pant["formality"], pant_colors)
            accessory_options = _ranked_matches(accessories, pant["formality"], shirt_colors)
            shoe_bonus = shoe_options[0]["score"] if shoe_options else 0
            acc_bonus = accessory_options[0]["score"] if accessory_options else 0
            total_score = base_score * 0.6 + shoe_bonus * 0.25 + acc_bonus * 0.15
            candidates.append({
                "top": shirt,
                "bottom": pant,
                "shoes": shoe_options[0]["item"] if shoe_options else None,
                "accessory": accessory_options[0]["item"] if accessory_options else None,
                "shoe_options": shoe_options,
                "accessory_options": accessory_options,
                "score": round(total_score, 1),
            })
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates if top_n is None else candidates[:top_n]