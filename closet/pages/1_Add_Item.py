import streamlit as st
from services.color_extractor import extract_colors
from utils.image_utils import save_uploaded_image
from db import queries
from models.schemas import CATEGORIES, FORMALITY_LEVELS, SUB_TYPES, PATTERNS, SEASONS
from utils.styling import apply_theme, sidebar_nav, eyebrow, section_heading, BORDER, TEXT_SECONDARY
PRINTED_EXCLUDED_FORMALITY = {"formal"}

st.set_page_config(page_title="Add Item - Closet", page_icon="➕", layout="wide")
apply_theme()

_all_items = queries.get_all_items()
sidebar_nav(total_count=len(_all_items), dirty_count=len([i for i in _all_items if i["is_dirty"]]))

eyebrow("Grow Your Wardrobe")
st.markdown("# Add a Clothing Item")
st.caption("Upload a photo and Closet will detect its color palette automatically.")
st.markdown("")

uploaded_file = st.file_uploader("Upload a photo of the item", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns([1, 1.5])

    with col1:
        with st.container(border=True):
            st.markdown(
                f'<div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;'
                f'color:{TEXT_SECONDARY};margin-bottom:8px;">Preview</div>',
                unsafe_allow_html=True,
            )
            st.image(uploaded_file, use_container_width=True)

    with col2:
        with st.container(border=True):
            section_heading("Item Details")
            category = st.selectbox("Category", CATEGORIES)
            sub_type = st.selectbox("Sub-type", SUB_TYPES.get(category, []))
            pattern = "neutral"
            if category == "shirt":
                pattern = st.selectbox(
                    "Pattern",
                    PATTERNS,
                    help="Printed shirts (florals, graphics, big logos) aren't considered formal wear.",
                )

            formality_choices = FORMALITY_LEVELS
            if pattern == "printed":
                formality_choices = [f for f in FORMALITY_LEVELS if f not in PRINTED_EXCLUDED_FORMALITY]
                st.caption("Printed shirts aren't considered formal, so that option is hidden below.")
            formality = st.selectbox("Formality", formality_choices)

            season = st.selectbox(
                "Season / Climate",
                SEASONS,
                help="Pick a specific season if this item is only right for warmer or colder weather. "
                     "'all-season' items always show up regardless of season filters in Suggestions.",
            )
            uploaded_file.seek(0)
            detected_colors = extract_colors(uploaded_file, max_colors=2)
            st.markdown(
                f'<div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;'
                f'color:{TEXT_SECONDARY};margin:14px 0 8px 0;">Detected Color(s)</div>',
                unsafe_allow_html=True,
            )
            swatch_cols = st.columns(len(detected_colors) + 2)
            for i, c in enumerate(detected_colors):
                with swatch_cols[i]:
                    st.markdown(
                        f'<div style="width:44px;height:44px;border-radius:10px;'
                        f'background-color:{c["hex"]};border:1px solid {BORDER};'
                        f'box-shadow:0 1px 3px rgba(17,17,17,0.08);"></div>'
                        f'<div style="font-size:12px;margin-top:6px;color:{TEXT_SECONDARY};">{c["name"]}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown("")
            if st.button("Save Item", type="primary"):
                uploaded_file.seek(0)
                saved_path = save_uploaded_image(uploaded_file)
                item_id = queries.add_clothing_item(
                    image_path=saved_path,
                    category=category,
                    sub_type=sub_type,
                    formality=formality,
                    colors=detected_colors,
                    pattern=pattern,
                    season=season,
                )
                st.success(f"Saved! Item #{item_id} added to your closet.")