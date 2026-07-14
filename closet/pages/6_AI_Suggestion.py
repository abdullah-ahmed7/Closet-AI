import datetime
import streamlit as st
from db import queries
from services.matching_engine import suggest_outfits
from services.laundry_tracker import record_wear
from services.weather import get_current_weather
from services.smart_context import get_smart_context
from utils.styling import (
    apply_theme, sidebar_nav, score_ring, pill_badge, safe_image,
    eyebrow, section_heading, DISPLAY_FONT, TEXT_SECONDARY, ACCENT,
)
st.set_page_config(page_title="AI Suggestion - Closet", page_icon="🤖", layout="wide")
apply_theme()
all_items = queries.get_all_items()
dirty_items = [i for i in all_items if i["is_dirty"]]
sidebar_nav(total_count=len(all_items), dirty_count=len(dirty_items))
eyebrow("Your Personal Stylist")
st.markdown("# Today's Outfit")
st.caption("No need to pick a context - this reads the clock, the calendar, and the sky for you.")
st.markdown("")
now = datetime.datetime.now()
weather = get_current_weather()
smart = get_smart_context(now=now, weather=weather)
auto_season = "all-season"
if weather and weather.get("temp_c") is not None:
    if weather["temp_c"] <= 15:
        auto_season = "winter"
    elif weather["temp_c"] >= 30:
        auto_season = "summer"
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.caption("Time")
        st.markdown(f"### {now.strftime('%I:%M %p')}")
        st.caption(now.strftime("%A"))
with c2:
    with st.container(border=True):
        st.caption("Weather")
        if weather:
            st.markdown(f"### {weather['icon']} {round(weather['temp_c'])}°C")
            st.caption(f"{weather['condition']} · Lahore, PK")
        else:
            st.markdown("### —")
            st.caption("Weather unavailable right now")
with c3:
    with st.container(border=True):
        st.caption("Reading Right Now")
        for reason in smart["reasons"]:
            st.markdown(
                f'<div style="font-size:14px;margin-top:4px;">'
                f'<span style="color:{ACCENT};">＋</span> {reason}</div>',
                unsafe_allow_html=True,
            )
season_labels = {
    "all-season": "Auto (from weather)",
    "summer": "Summer",
    "winter": "Winter / Heading somewhere colder up north",
    "spring/fall": "Spring / Fall",
}
season_override = st.selectbox(
    "Season / Climate override",
    ["all-season", "summer", "winter", "spring/fall"],
    format_func=lambda s: season_labels.get(s, s),
    help="Left on Auto, this follows today's temperature. Switch it manually if you're "
         "traveling somewhere colder (or warmer) than it is right now.",
)
active_season = season_override if season_override != "all-season" else auto_season
st.markdown("")
reserved_ids = queries.get_active_reserved_item_ids()
available_items = [
    item for item in all_items
    if not item["is_dirty"]
    and item["id"] not in reserved_ids
    and item["formality"] in smart["allowed_formalities"]
    and not (item["category"] == "shoes" and item["sub_type"] in smart["excluded_subtypes"])
]

if not available_items:
    st.warning(
        "No clean, available items fit right now's conditions. "
        "Try **Wash Alerts** to free some items up, or add more in **Add Item**."
    )
else:
    outfits = suggest_outfits(available_items, context=None, season=active_season)

    if not outfits:
        st.warning(
            "Couldn't find a full shirt+pant combo that fits right now's conditions. "
            "Try adding more items in that formality range."
        )
    else:
        section_heading(
            f"{len(outfits)} Outfit Option(s) for Right Now",
            "Ranked by color harmony, formality fit, and today's conditions.",
        )

        for i, outfit in enumerate(outfits):
            featured = i == 0
            with st.container(border=True):
                if featured:
                    st.markdown(
                        pill_badge("Top Pick", color=ACCENT), unsafe_allow_html=True,
                    )

                cols = st.columns([0.6, 1, 1, 1, 1, 1.3])

                with cols[0]:
                    st.markdown(
                        f'<div style="width:30px;height:30px;border-radius:50%;background:#F1EFEA;'
                        f'display:flex;align-items:center;justify-content:center;font-weight:700;'
                        f'font-family:{DISPLAY_FONT};color:{TEXT_SECONDARY};margin-top:18px;">{i + 1}</div>',
                        unsafe_allow_html=True,
                    )
                with cols[1]:
                    safe_image(outfit["top"]["image_path"], caption=outfit["top"]["sub_type"], use_container_width=True)
                with cols[2]:
                    safe_image(outfit["bottom"]["image_path"], caption=outfit["bottom"]["sub_type"], use_container_width=True)

                # Shoes & accessory are swapped within this same combo card
                # rather than generating a separate outfit per color option.
                with cols[3]:
                    shoe_options = outfit["shoe_options"]
                    if shoe_options:
                        shoe_labels = [
                            f'{o["item"]["color_name"].title()} {o["item"]["sub_type"]}' + (" (best match)" if idx == 0 else "")
                            for idx, o in enumerate(shoe_options)
                        ]
                        picked_shoe_idx = st.selectbox(
                            "Shoes", range(len(shoe_options)),
                            format_func=lambda idx: shoe_labels[idx],
                            key=f"ai_shoe_pick_{i}", label_visibility="collapsed",
                        )
                        picked_shoe = shoe_options[picked_shoe_idx]["item"]
                        safe_image(picked_shoe["image_path"], caption=picked_shoe["sub_type"], use_container_width=True)
                    else:
                        picked_shoe = None
                        st.caption("No shoes matched")
                with cols[4]:
                    acc_options = outfit["accessory_options"]
                    if acc_options:
                        acc_labels = [
                            f'{o["item"]["color_name"].title()} {o["item"]["sub_type"]}' + (" (with combo)" if idx == 0 else "")
                            for idx, o in enumerate(acc_options)
                        ]
                        picked_acc_idx = st.selectbox(
                            "Accessory", range(len(acc_options)),
                            format_func=lambda idx: acc_labels[idx],
                            key=f"ai_acc_pick_{i}", label_visibility="collapsed",
                        )
                        picked_acc = acc_options[picked_acc_idx]["item"]
                        safe_image(picked_acc["image_path"], caption=picked_acc["sub_type"], use_container_width=True)
                    else:
                        picked_acc = None
                        st.caption("No accessory")
                with cols[5]:
                    st.markdown(score_ring(outfit["score"], size=72 if featured else 64), unsafe_allow_html=True)
                    st.caption("Match Score")

                if st.button("Wear This Outfit", key=f"ai_wear_{i}", type="primary"):
                    worn_items = [outfit["top"], outfit["bottom"]]
                    if picked_shoe:
                        worn_items.append(picked_shoe)
                    if picked_acc:
                        worn_items.append(picked_acc)

                    for item in worn_items:
                        record_wear(item["id"], category=item["category"])
                    queries.log_outfit_worn([item["id"] for item in worn_items], "auto")

                    st.success("Logged! Shirts & pants need a wash - shoes hold up longer, accessories don't need one at all.")
                    st.rerun()
