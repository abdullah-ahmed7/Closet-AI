import streamlit as st
from db import queries
from models.schemas import CATEGORIES, SUB_TYPES
from services.shopping_scraper import search_products, find_wardrobe_gaps
from utils.styling import (
    apply_theme, sidebar_nav, eyebrow, section_heading, pill_badge,
    TEXT_SECONDARY, ACCENT, BORDER,
)

st.set_page_config(page_title="Shopping - Closet", page_icon="🛍️", layout="wide")
apply_theme()

all_items = queries.get_all_items()
sidebar_nav(total_count=len(all_items), dirty_count=len([i for i in all_items if i["is_dirty"]]))

eyebrow("Fill The Gaps")
st.markdown("# Shopping")
st.caption(
    "Closet checks a few popular Pakistani retailers for the color and type you're missing - "
    "no need to browse each site yourself."
)
st.markdown("")


def _render_results(results, empty_note="No parseable results right now - use the link to search directly."):
    """Shared results grid used by both the gap suggestions and manual search."""
    for site_result in results:
        with st.container(border=True):
            top = st.columns([3, 1])
            with top[0]:
                st.markdown(f"**{site_result['site']}**")
            with top[1]:
                st.link_button("Open site search ↗", site_result["search_url"], use_container_width=True)

            products = site_result["products"]
            if not products:
                st.caption(empty_note)
                continue

            cols = st.columns(len(products))
            for col, product in zip(cols, products):
                with col:
                    if product.get("image"):
                        st.image(product["image"], use_container_width=True)
                    st.markdown(
                        f'<div style="font-size:13px;font-weight:600;margin-top:4px;">'
                        f'{product["title"][:60]}</div>',
                        unsafe_allow_html=True,
                    )
                    if product.get("price"):
                        st.markdown(
                            f'<div style="font-size:13px;color:{ACCENT};">Rs. {product["price"]}</div>',
                            unsafe_allow_html=True,
                        )
                    st.link_button("View", product["url"], use_container_width=True)
section_heading(
    "Closet noticed you're missing a few basics",
    "Common type + color combos most wardrobes need, that yours doesn't have yet.",
)
gaps = find_wardrobe_gaps(all_items)
if not gaps:
    st.info("Nice - your closet already covers all the common basics Closet checks for.")
else:
    gap_labels = [f"{g['color'].title()} {g['sub_type']}" for g in gaps]
    picked_gap_idx = st.selectbox(
        "Missing basics", range(len(gaps)),
        format_func=lambda i: gap_labels[i],
        label_visibility="collapsed",
    )
    picked_gap = gaps[picked_gap_idx]
    st.markdown(pill_badge(f"{picked_gap['color'].title()} {picked_gap['sub_type']}"), unsafe_allow_html=True)

    if st.button("Shop for this", type="primary", key="shop_gap"):
        with st.spinner("Checking retailers..."):
            results = search_products(picked_gap["sub_type"], picked_gap["color"], category=picked_gap["category"])
        st.session_state["shopping_results"] = results
        st.session_state["shopping_results_label"] = f"{picked_gap['color'].title()} {picked_gap['sub_type']}"
st.markdown("")
st.markdown("---")
section_heading("Or search for something specific", "Just the type and color - Closet does the rest.")
with st.container(border=True):
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        category = st.selectbox("Category", CATEGORIES, key="shop_category")
    with c2:
        sub_type = st.selectbox("Type", SUB_TYPES.get(category, []), key="shop_subtype")
    with c3:
        color = st.text_input("Color", placeholder="e.g. black, navy, maroon", key="shop_color")
    if st.button("Search Retailers", type="primary", key="shop_manual"):
        if not color.strip():
            st.warning("Enter a color to search for - e.g. \"black\" or \"navy\".")
        else:
            with st.spinner("Checking retailers..."):
                results = search_products(sub_type, color.strip(), category=category)
            st.session_state["shopping_results"] = results
            st.session_state["shopping_results_label"] = f"{color.title()} {sub_type}"
st.markdown("")
if "shopping_results" in st.session_state:
    section_heading(f"Results for \"{st.session_state.get('shopping_results_label', '')}\"")
    _render_results(st.session_state["shopping_results"])
st.markdown("")
st.caption(
    "Closet checks each retailer's own search for a live match. Some sites load their product "
    "grids with JavaScript and won't return parseable results here - in that case, use the "
    "\"Open site search\" link to look it up directly on that site."
)