import streamlit as st
from db import queries
from services.matching_engine import suggest_outfits
from services.laundry_tracker import record_wear
from models.schemas import CONTEXTS, SEASONS
from utils.styling import (
    apply_theme, sidebar_nav, score_ring, eyebrow, section_heading,
    DISPLAY_FONT, TEXT_SECONDARY,
)

st.set_page_config(page_title="Suggestions - Closet", page_icon="✨", layout="wide")
apply_theme()

_all_items_for_nav = queries.get_all_items()
sidebar_nav(total_count=len(_all_items_for_nav), dirty_count=len([i for i in _all_items_for_nav if i["is_dirty"]]))

eyebrow("Styled For You")
st.markdown("# Suggestions")
st.caption("Pick where you're headed - get outfits ranked by color and formality match.")
st.markdown("")

context = st.radio("Where are you headed?", CONTEXTS, horizontal=True, label_visibility="collapsed")

season_labels = {
    "all-season": "All-Season (default)",
    "summer": "Summer",
    "winter": "Winter / Heading somewhere colder up north",
    "spring/fall": "Spring / Fall",
}
season_choice = st.selectbox(
    "Season / Climate",
    SEASONS,
    format_func=lambda s: season_labels.get(s, s),
    help="Pick 'Winter' if you're traveling to a colder, northern area (e.g. Murree, "
         "Islamabad, Gilgit) so warmer pieces get prioritized alongside your all-season basics.",
)

all_items = queries.get_all_items()
reserved_ids = queries.get_active_reserved_item_ids()

available_items = [
    item for item in all_items
    if not item["is_dirty"] and item["id"] not in reserved_ids
]

st.markdown("")

if not available_items:
    st.warning("No clean, available items to suggest from. Check **Wash Alerts** or add more items.")
else:
    outfits = suggest_outfits(available_items, context, season=season_choice)

    if not outfits:
        st.warning(
            f"Couldn't find a full shirt+pant combo for '{context}'"
            f"{'' if season_choice == 'all-season' else f' in {season_choice} pieces'}. "
            f"Try adding more items in that formality/season range."
        )
    else:
        section_heading(f"{len(outfits)} Outfit Option(s) for {context.title()}")

        for i, outfit in enumerate(outfits):
            with st.container(border=True):
                cols = st.columns([0.6, 1, 1, 1, 1, 1.3])

                with cols[0]:
                    st.markdown(
                        f'<div style="width:30px;height:30px;border-radius:50%;background:#F1EFEA;'
                        f'display:flex;align-items:center;justify-content:center;font-weight:700;'
                        f'font-family:{DISPLAY_FONT};color:{TEXT_SECONDARY};margin-top:18px;">{i + 1}</div>',
                        unsafe_allow_html=True,
                    )
                with cols[1]:
                    st.image(outfit["top"]["image_path"], caption=outfit["top"]["sub_type"], use_container_width=True)
                with cols[2]:
                    st.image(outfit["bottom"]["image_path"], caption=outfit["bottom"]["sub_type"], use_container_width=True)
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
                            key=f"shoe_pick_{i}", label_visibility="collapsed",
                        )
                        picked_shoe = shoe_options[picked_shoe_idx]["item"]
                        st.image(picked_shoe["image_path"], caption=picked_shoe["sub_type"], use_container_width=True)
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
                            key=f"acc_pick_{i}", label_visibility="collapsed",
                        )
                        picked_acc = acc_options[picked_acc_idx]["item"]
                        st.image(picked_acc["image_path"], caption=picked_acc["sub_type"], use_container_width=True)
                    else:
                        picked_acc = None
                        st.caption("No accessory")
                with cols[5]:
                    st.markdown(score_ring(outfit["score"]), unsafe_allow_html=True)
                    st.caption("Match Score")

                if st.button("Wear This Outfit", key=f"wear_{i}", type="primary"):
                    worn_items = [outfit["top"], outfit["bottom"]]
                    if picked_shoe:
                        worn_items.append(picked_shoe)
                    if picked_acc:
                        worn_items.append(picked_acc)

                    for item in worn_items:
                        record_wear(item["id"], category=item["category"])
                    queries.log_outfit_worn([item["id"] for item in worn_items], context)

                    st.success("Logged! Shirts & pants need a wash - shoes hold up longer, accessories don't need one at all.")
                    st.rerun()
