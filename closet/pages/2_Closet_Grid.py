import streamlit as st
from db import queries
from models.schemas import CATEGORIES, SEASONS
from utils.styling import (
    apply_theme, sidebar_nav, color_swatch_row, pill_badge, eyebrow,
    TEXT_SECONDARY, ERROR, ACCENT_DARK,
)

st.set_page_config(page_title="Closet Grid - Closet", page_icon="🗂️", layout="wide")
apply_theme()

_all_items = queries.get_all_items()
sidebar_nav(total_count=len(_all_items), dirty_count=len([i for i in _all_items if i["is_dirty"]]))

eyebrow("Full Inventory")
st.markdown("# Your Closet")
st.caption("Every piece you own, at a glance - type, color, formality, pattern, and season all in one place.")
st.markdown("")

fcol1, fcol2 = st.columns(2)
with fcol1:
    filter_category = st.selectbox("Filter by category", ["all"] + CATEGORIES)
with fcol2:
    filter_season = st.selectbox("Filter by season", ["all"] + SEASONS)

category_arg = None if filter_category == "all" else filter_category
season_arg = None if filter_season == "all" else filter_season

reserved_ids = queries.get_active_reserved_item_ids()
items = queries.get_all_items(
    category=category_arg,
    exclude_reserved_ids=list(reserved_ids) if reserved_ids else None,
    season=season_arg,
)

if reserved_ids:
    st.caption(f"🔒 {len(reserved_ids)} item(s) hidden - currently reserved for an event. See **Reserve Event** page.")

st.markdown("")

if not items:
    st.info("No items yet. Go add some in **Add Item**!")
else:
    cols = st.columns(4)
    for idx, item in enumerate(items):
        with cols[idx % 4]:
            with st.container(border=True):
                st.image(item["image_path"], use_container_width=True)
                st.markdown(f"**{item['sub_type'].title()}**")
                st.markdown(
                    f'<div style="font-size:12px;letter-spacing:0.06em;text-transform:uppercase;'
                    f'color:{TEXT_SECONDARY};margin-bottom:8px;">{item["category"].title()}</div>',
                    unsafe_allow_html=True,
                )

                colors = queries.get_item_colors(item)
                st.markdown(color_swatch_row(colors, swatch_size=16), unsafe_allow_html=True)
                st.markdown("")

                badges_html = pill_badge(item["formality"], color="#F1EFEA", text_color="#111111")
                if item.get("pattern") == "printed":
                    badges_html += pill_badge("printed", color="#F1EFEA", text_color="#111111")
                season = item.get("season") or "all-season"
                if season != "all-season":
                    badges_html += pill_badge(season, color=ACCENT_DARK)
                if item["is_dirty"]:
                    badges_html += pill_badge("needs wash", color=ERROR)
                st.markdown(badges_html, unsafe_allow_html=True)

                st.caption(f"Worn {item['wear_count']}x")

                if st.button("Delete", key=f"del_{item['id']}"):
                    queries.delete_item(item["id"])
                    st.rerun()
