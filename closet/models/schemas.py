"""
Simple dataclasses representing the core entities in Closet.
These are plain data holders - DB logic lives in db/queries.py.
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ClothingItem:
    category: str              # shirt, pant, shoes, accessory
    sub_type: str               # polo, formal shirt, jeans, sneakers, belt, etc.
    formality: str               # casual, semi-formal, business, formal
    dominant_color_hex: str
    dominant_color_name: str
    image_path: str
    id: Optional[int] = None
    wear_count: int = 0
    last_worn_date: Optional[str] = None
    is_dirty: bool = False
    pattern: str = "neutral"     # neutral (solid/plain) or printed - shirts only, matters for formality
    season: str = "all-season"   # all-season, summer, winter, spring/fall


@dataclass
class Outfit:
    top: ClothingItem
    bottom: ClothingItem
    shoes: Optional[ClothingItem] = None
    accessories: List[ClothingItem] = field(default_factory=list)
    match_score: float = 0.0
    context: str = ""           # office, friend, university, trip


@dataclass
class ReservedEvent:
    event_name: str
    start_date: str
    end_date: str
    reserved_item_ids: List[int]
    id: Optional[int] = None


# Fixed choice lists - used to populate Streamlit dropdowns consistently
CATEGORIES = ["shirt", "pant", "shoes", "accessory"]

# "semi-formal" sits between casual and business - a big part of what university
# students actually wear (smart-casual blazers, non-plain button-downs, chinos
# with a collared shirt, etc.), so it gets its own tier rather than being folded
# into "business".
FORMALITY_LEVELS = ["casual", "semi-formal", "business", "formal"]

CONTEXTS = ["office", "friend", "university", "trip"]

SUB_TYPES = {
    "shirt": ["polo", "formal shirt", "t-shirt", "casual shirt", "kurta"],
    "pant": ["jeans", "formal trousers", "chinos", "shalwar"],
    "shoes": ["sneakers", "formal shoes", "loafers", "sandals"],
    "accessory": ["belt", "watch", "tie", "cap", "sunglasses"],
}

# Pattern only really matters for shirts/tops - a printed shirt (florals,
# graphics, big logos) reads as casual no matter what formality label gets
# picked, so Add Item restricts the formality choices when this is "printed".
PATTERNS = ["neutral", "printed"]

# Season / climate suitability. "all-season" items match no matter what the
# person picks in the Suggestions pages; the others only show up when that
# specific season (or a trip to a colder/northern region) is selected.
SEASONS = ["all-season", "summer", "winter", "spring/fall"]
