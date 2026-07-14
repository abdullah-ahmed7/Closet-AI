import streamlit as st
from db import queries
from services.laundry_tracker import get_items_needing_wash, get_low_combination_warning, record_wash
from utils.styling import apply_theme, sidebar_nav, pill_badge, eyebrow, section_heading, ERROR

st.set_page_config(page_title="Wash Alerts - Closet", page_icon="🧺", layout="wide")
apply_theme()

dirty_items = get_items_needing_wash()
all_items = queries.get_all_items()
sidebar_nav(total_count=len(all_items), dirty_count=len(dirty_items))

eyebrow("Laundry Day")
st.markdown("# Wash Alerts")
st.markdown("")

warnings = get_low_combination_warning(all_items)
for w in warnings:
    st.warning(w)

if not dirty_items:
    st.success("Nothing needs washing right now. You're good!")
else:
    section_heading(f"{len(dirty_items)} item(s) need a wash")
    cols = st.columns(4)
    for idx, item in enumerate(dirty_items):
        with cols[idx % 4]:
            with st.container(border=True):
                st.image(item["image_path"], use_container_width=True)
                st.markdown(f"**{item['sub_type'].title()}**")
                st.markdown(pill_badge(f"worn {item['wear_count']}x", color=ERROR), unsafe_allow_html=True)
                st.markdown("")
                if st.button("Mark as Washed", key=f"wash_{item['id']}", type="primary"):
                    record_wash(item["id"])
                    st.rerun()

st.markdown("---")
st.caption("💡 Tip: shirts & pants are flagged after every wear, shoes after about 5 wears, and accessories never need washing.")
