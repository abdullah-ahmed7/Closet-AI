from db import queries

DEFAULT_WASH_THRESHOLD = 1 
SHOE_WASH_THRESHOLD = 5    
NO_WASH_CATEGORIES = {"accessory"}

def record_wear(item_id, category=None, wash_after_n_wears=None):
    needs_wash = category not in NO_WASH_CATEGORIES
    if wash_after_n_wears is None:
        wash_after_n_wears = SHOE_WASH_THRESHOLD if category == "shoes" else DEFAULT_WASH_THRESHOLD
    queries.mark_item_worn(item_id, wash_after_n_wears, needs_wash=needs_wash)

def record_wash(item_id):
    queries.mark_item_washed(item_id)

def get_items_needing_wash():
    all_items = queries.get_all_items()
    return [item for item in all_items if item["is_dirty"]]

def get_low_combination_warning(all_items, min_clean_per_category=1):
    warnings = []
    categories = set(item["category"] for item in all_items)
    for cat in categories:
        clean_count = len([i for i in all_items if i["category"] == cat and not i["is_dirty"]])
        if clean_count < min_clean_per_category:
            warnings.append(f"You're low on clean {cat}s ({clean_count} left) - wash some soon!")
    return warnings