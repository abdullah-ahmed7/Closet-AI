import datetime
EVENING_HOUR = 17  
SUNDAY = 6         

def get_smart_context(now=None, weather=None):
    now = now or datetime.datetime.now()
    is_sunday = now.weekday() == SUNDAY
    is_evening = now.hour >= EVENING_HOUR
    allowed = {"casual", "business", "formal"}
    excluded_subtypes = set()
    reasons = []
    if is_sunday:
        allowed -= {"business", "formal"}
        reasons.append("It's Sunday, so office wear is skipped.")
    if is_evening:
        allowed &= {"casual"}
        reasons.append("It's after 5 PM, so leaning casual for the evening.")
    if weather and weather.get("is_rainy"):
        excluded_subtypes.add("sandals")
        reasons.append(f"{weather['condition']} outside, so steering clear of open shoes.")
    if not allowed:
        allowed = {"casual"}
    if not reasons:
        reasons.append("Nothing special about right now, so showing your best all-round match.")
    return {
        "allowed_formalities": allowed,
        "excluded_subtypes": excluded_subtypes,
        "reasons": reasons,
    }