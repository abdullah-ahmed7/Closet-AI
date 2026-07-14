import datetime
import streamlit as st
from db.database import init_db
from db import queries
from services.matching_engine import suggest_outfits
from services.laundry_tracker import record_wear
from services.weather import get_current_weather
from utils.styling import (
    apply_theme, sidebar_nav, score_ring, pill_badge, safe_image,
    eyebrow, section_heading, SUCCESS, ERROR,
)

st.set_page_config(page_title="Closet", page_icon="👕", layout="wide")
init_db()
apply_theme()

USER_NAME = "Abdullah"
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="clock_refresh")
except ImportError:
    pass
now = datetime.datetime.now()
hour = now.hour
greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
weather = get_current_weather()

all_items = queries.get_all_items()
dirty_items = [i for i in all_items if i["is_dirty"]]
reserved_ids = queries.get_active_reserved_item_ids()
events = queries.get_all_reserved_events()
available_items = [i for i in all_items if not i["is_dirty"] and i["id"] not in reserved_ids]
top_outfits = suggest_outfits(available_items, context=None, top_n=1) if available_items else []
best_outfit = top_outfits[0] if top_outfits else None
sidebar_nav(total_count=len(all_items), dirty_count=len(dirty_items))
hcol1, hcol2 = st.columns([3, 1])
with hcol1:
    eyebrow("Your Wardrobe, Curated")
    st.markdown(f"# {greeting}, {USER_NAME}")
    st.caption("Here's your top outfit for today." if best_outfit else "Add a few items to get your first outfit pick.")
with hcol2:
    with st.container(border=True):
        if weather:
            st.markdown(f"##### {weather['icon']} {round(weather['temp_c'])}°C")
            st.caption(f"{weather['condition']} · Lahore, PK · {now.strftime('%I:%M %p')}")
        else:
            st.markdown(f"##### {now.strftime('%I:%M %p')}")
            st.caption("Weather unavailable right now")
st.markdown("")

section_heading("Today's Recommendation", "The single best outfit your closet can put together right now.")
with st.container(border=True):
    if not best_outfit:
        st.info(
            "Not enough clean, unreserved items for a full outfit yet. "
            "Add more in **Add Item**, or free some up in **Wash Alerts**."
        )
    else:
        cols = st.columns([1, 1, 1, 1.1])
        with cols[0]:
            safe_image(best_outfit["top"]["image_path"], caption=best_outfit["top"]["sub_type"].title(), use_container_width=True)
        with cols[1]:
            safe_image(best_outfit["bottom"]["image_path"], caption=best_outfit["bottom"]["sub_type"].title(), use_container_width=True)
        with cols[2]:
            if best_outfit["shoes"]:
                safe_image(best_outfit["shoes"]["image_path"], caption=best_outfit["shoes"]["sub_type"].title(), use_container_width=True)
            else:
                st.caption("No shoes matched")
        with cols[3]:
            st.markdown(score_ring(best_outfit["score"], size=76), unsafe_allow_html=True)
            st.caption("Match Score")
        if st.button("Wear This Outfit", type="primary", key="wear_today"):
            worn_items = [best_outfit["top"], best_outfit["bottom"]]
            if best_outfit["shoes"]:
                worn_items.append(best_outfit["shoes"])
            if best_outfit["accessory"]:
                worn_items.append(best_outfit["accessory"])
            for item in worn_items:
                record_wear(item["id"], category=item["category"])
            queries.log_outfit_worn([item["id"] for item in worn_items], "daily")
            st.success("Logged! Shirts & pants need a wash - shoes hold up longer, accessories don't need one at all.")
            st.rerun()
st.markdown("")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Items in Closet", len(all_items))
col2.metric("Need Washing", len(dirty_items))
col3.metric("Reserved Right Now", len(reserved_ids))
col4.metric("Best Match Score", int(best_outfit["score"]) if best_outfit else "—")
st.markdown("")
left, right = st.columns([1.4, 1])
with left:
    section_heading("Quick Actions")
    a, b, c, d, e = st.columns(5)
    with a:
        st.page_link("pages/1_Add_Item.py", label="Add Item", use_container_width=True)
    with b:
        st.page_link("pages/6_AI_Suggestion.py", label="AI Suggestion", use_container_width=True)
    with c:
        st.page_link("pages/3_Suggest_Outfit.py", label="Suggestions", use_container_width=True)
    with d:
        st.page_link("pages/4_Wash_Alerts.py", label="Wash Alerts", use_container_width=True)
    with e:
        st.page_link("pages/5_Reserve_Event.py", label="Reserve Event", use_container_width=True)
    st.markdown("")
    section_heading("Recent Activity")
    recent = sorted(
        (i for i in all_items if i.get("last_worn_date")),
        key=lambda i: i["last_worn_date"],
        reverse=True,
    )[:4]
    if not recent:
        st.info("No activity yet - wear an outfit above to see it show up here.")
    else:
        for item in recent:
            with st.container(border=True):
                rcols = st.columns([0.18, 0.62, 0.2])
                with rcols[0]:
                    safe_image(item["image_path"], use_container_width=True)
                with rcols[1]:
                    st.markdown(f"**{item['sub_type'].title()}** worn")
                    st.caption(item["last_worn_date"])
                with rcols[2]:
                    if item["is_dirty"]:
                        st.markdown(pill_badge("Needs Wash", color=ERROR), unsafe_allow_html=True)
                    else:
                        st.markdown(pill_badge("Clean", color=SUCCESS), unsafe_allow_html=True)
with right:
    section_heading("Upcoming Reservations")
    if not events:
        st.info("No events reserved yet.")
    else:
        for event in events[:3]:
            with st.container(border=True):
                st.markdown(f"**{event['event_name']}**")
                st.caption(f"{event['start_date']} → {event['end_date']}")
st.markdown("---")
st.caption(
    "Add clothing photos in **Add Item**, then let **Suggestions** build outfits "
    "using color theory and formality matching - tailored to office, university, "
    "friend hangouts, or trips."
)