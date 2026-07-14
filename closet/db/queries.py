import json
from datetime import date, timedelta
from db.database import get_connection

def add_clothing_item(image_path, category, sub_type, formality, colors,
                       pattern="neutral", season="all-season"):
    """
    colors: list of dicts from color_extractor.extract_colors(), e.g.
            [{"hex":"#..","rgb":(r,g,b),"name":"navy","weight":0.6}, ...]
    The first (largest-weight) color is also stored separately as
    dominant_color/color_name for quick access and backward compatibility.

    pattern: "neutral" (solid/plain) or "printed" - mainly meaningful for
             shirts; printed items are capped below "formal" by the Add Item
             page before this is ever called.
    season: "all-season", "summer", "winter", or "spring/fall".
    """
    primary = colors[0]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clothing_items
            (image_path, category, sub_type, formality, dominant_color, color_name, colors, pattern, season)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        image_path, category, sub_type, formality,
        primary["hex"], primary["name"], json.dumps(colors), pattern, season,
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def get_all_items(category=None, exclude_dirty=False, exclude_reserved_ids=None, season=None):
    """
    season: if given and not "all-season", only returns items whose own
            season matches (plus items marked "all-season", which always
            qualify) - e.g. season="winter" surfaces warmer pieces for a
            trip to a colder, northern area while still allowing all-season
            basics to fill in the rest of the outfit.
    """
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM clothing_items WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if exclude_dirty:
        query += " AND is_dirty = 0"
    if exclude_reserved_ids:
        placeholders = ",".join("?" * len(exclude_reserved_ids))
        query += f" AND id NOT IN ({placeholders})"
        params.extend(exclude_reserved_ids)
    if season and season != "all-season":
        query += " AND (season = ? OR season = 'all-season' OR season IS NULL)"
        params.append(season)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_item_by_id(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clothing_items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_item_colors(item):
    """
    Returns the full list of colors for an item, parsed from the 'colors'
    JSON column. Falls back to a single-color list built from
    dominant_color/color_name for rows saved before multi-color support existed.
    """
    if item.get("colors"):
        try:
            colors = json.loads(item["colors"])
            for c in colors:
                c["rgb"] = tuple(c["rgb"])
            return colors
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    # Legacy fallback
    hex_code = item["dominant_color"].lstrip("#")
    rgb = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
    return [{"hex": item["dominant_color"], "rgb": rgb, "name": item["color_name"], "weight": 1.0}]

def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clothing_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def mark_item_worn(item_id, wash_after_n_wears=1, needs_wash=True):
    """Increments wear count and updates last worn date. Only flags the item
    dirty if needs_wash is True - accessories like belts/watches don't need
    washing, so they should never end up in the Wash Alerts list."""
    conn = get_connection()
    cur = conn.cursor()
    if needs_wash:
        cur.execute("""
            UPDATE clothing_items
            SET wear_count = wear_count + 1,
                last_worn_date = date('now'),
                is_dirty = CASE WHEN wear_count + 1 >= ? THEN 1 ELSE is_dirty END
            WHERE id = ?
        """, (wash_after_n_wears, item_id))
    else:
        cur.execute("""
            UPDATE clothing_items
            SET wear_count = wear_count + 1,
                last_worn_date = date('now')
            WHERE id = ?
        """, (item_id,))
    conn.commit()
    conn.close()

def mark_item_washed(item_id):
    """Resets wear count and clears the dirty flag."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clothing_items
        SET wear_count = 0, is_dirty = 0
        WHERE id = ?
    """, (item_id,))
    conn.commit()
    conn.close()

def get_dirty_items():
    return get_all_items(exclude_dirty=False)  # filtered in Python by caller if needed

def log_outfit_worn(item_ids, context):
    conn = get_connection()
    cur = conn.cursor()
    ids_str = ",".join(str(i) for i in item_ids)
    cur.execute("""
        INSERT INTO outfit_log (item_ids, context) VALUES (?, ?)
    """, (ids_str, context))
    conn.commit()
    conn.close()

def add_reserved_event(event_name, start_date, end_date, item_ids):
    conn = get_connection()
    cur = conn.cursor()
    ids_str = ",".join(str(i) for i in item_ids)
    cur.execute("""
        INSERT INTO reserved_events (event_name, start_date, end_date, reserved_item_ids)
        VALUES (?, ?, ?, ?)
    """, (event_name, start_date, end_date, ids_str))
    conn.commit()
    conn.close()

def get_active_reserved_item_ids(on_date=None):
    """Returns a set of item IDs currently locked by an active event (today by default)."""
    if on_date is None:
        on_date = date.today().isoformat()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT reserved_item_ids FROM reserved_events
        WHERE start_date <= ? AND end_date >= ?
    """, (on_date, on_date))
    rows = cur.fetchall()
    conn.close()

    reserved_ids = set()
    for row in rows:
        ids = row["reserved_item_ids"].split(",")
        reserved_ids.update(int(i) for i in ids if i)
    return reserved_ids

def get_all_reserved_events():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reserved_events ORDER BY start_date")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_reserved_event(event_id):
    """Cancels a reservation, freeing its items back into the suggestion pool immediately."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reserved_events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()