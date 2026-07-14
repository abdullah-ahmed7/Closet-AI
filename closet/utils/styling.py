"""
Shared visual styling for Closet - injected CSS plus small HTML component
generators (score rings, pill badges, color swatches, section headings) so
every page shares one premium, editorial-fashion design system.

This file owns 100% of the presentation layer. No data/business logic lives
here - pages still call db/services exactly as before, they just render the
results through these helpers.
"""
import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens - single source of truth for the whole app
# ---------------------------------------------------------------------------
BG = "#F8F8F6"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#111111"
TEXT_SECONDARY = "#6B7280"
ACCENT = "#C8A46B"
ACCENT_SOFT = "#E4D3B4"
ACCENT_DARK = "#A9824F"
BORDER = "#E7E5E0"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
ERROR = "#DC2626"

# legacy aliases so any old call sites (or future copy/paste) still resolve
SURFACE = CARD_BG
CARD_BORDER = BORDER

DISPLAY_FONT = "'Outfit', sans-serif"
BODY_FONT = "'Inter', sans-serif"


def apply_theme():
    """Injects shared CSS. Call once near the top of every page."""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: {BODY_FONT} !important;
        }}

        .stApp {{
            background-color: {BG} !important;
        }}

        /* ---------- Hide default Streamlit chrome ----------
           IMPORTANT: the "reopen sidebar" arrow lives INSIDE stToolbar
           (data-testid="stExpandSidebarButton"), so stToolbar itself must
           stay visible - we only hide the specific buttons we don't want
           (hamburger menu, deploy button) rather than the whole toolbar. */
        footer {{ visibility: hidden; height: 0; }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            visibility: visible !important;
        }}
        div[data-testid="stDecoration"] {{ display: none; }}
        div[data-testid="stStatusWidget"] {{ display: none; }}
        button[data-testid="stMainMenuButton"] {{ display: none; }}
        div[data-testid="stAppDeployButton"] {{ display: none; }}
        div[data-testid="stExpandSidebarButton"] {{
            visibility: visible !important;
            display: flex !important;
        }}

        .block-container {{
            padding-top: 1.4rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1180px;
        }}

        /* ---------- Typography ---------- */
        h1, h2, h3, h4, h5 {{
            font-family: {DISPLAY_FONT} !important;
            color: {TEXT_PRIMARY} !important;
            letter-spacing: -0.02em;
            font-weight: 600 !important;
        }}
        h1 {{ font-size: 46px !important; line-height: 1.08 !important; }}
        h2 {{ font-size: 28px !important; }}
        h3 {{ font-size: 21px !important; }}

        p, span, label, li {{ color: {TEXT_PRIMARY}; }}
        [data-testid="stCaptionContainer"], .stCaption {{
            color: {TEXT_SECONDARY} !important;
            font-size: 13px !important;
        }}
        ::selection {{ background: {ACCENT_SOFT}; }}

        /* ---------- Animations ---------- */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stImage"] {{
            animation: fadeInUp 0.35s ease both;
        }}

        /* ---------- Cards (st.container(border=True)) ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 22px !important;
            border: 1px solid {BORDER} !important;
            background-color: {CARD_BG} !important;
            padding: 6px;
            box-shadow: 0 1px 2px rgba(17,17,17,0.04);
            transition: box-shadow 0.25s ease, transform 0.25s ease;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            box-shadow: 0 16px 32px rgba(17,17,17,0.08);
            transform: translateY(-2px);
        }}

        /* ---------- Buttons ---------- */
        div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {{
            border-radius: 999px !important;
            font-family: {DISPLAY_FONT} !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            letter-spacing: 0.02em;
            padding: 0.55rem 1.5rem !important;
            border: 1px solid {TEXT_PRIMARY} !important;
            background-color: transparent !important;
            color: {TEXT_PRIMARY} !important;
            transition: all 0.2s ease;
        }}
        div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
            background-color: {TEXT_PRIMARY} !important;
            color: #fff !important;
            transform: translateY(-1px);
        }}
        div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {{
            background-color: {ACCENT} !important;
            border: 1px solid {ACCENT} !important;
            color: #fff !important;
        }}
        div.stButton > button[kind="primary"]:hover {{
            background-color: {ACCENT_DARK} !important;
            border-color: {ACCENT_DARK} !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(200,164,107,0.35);
        }}

        /* ---------- Images ---------- */
        div[data-testid="stImage"] {{
            overflow: hidden;
            border-radius: 16px !important;
        }}
        div[data-testid="stImage"] img {{
            border-radius: 16px !important;
            transition: transform 0.4s ease;
        }}
        div[data-testid="stImage"]:hover img {{
            transform: scale(1.04);
        }}

        /* ---------- Inputs ---------- */
        div[data-baseweb="select"] > div,
        .stTextInput input, .stNumberInput input, .stDateInput input, textarea {{
            border-radius: 12px !important;
            border: 1px solid {BORDER} !important;
            background-color: {CARD_BG} !important;
            font-family: {BODY_FONT} !important;
        }}
        div[data-baseweb="select"]:focus-within > div, .stTextInput input:focus {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 1px {ACCENT} !important;
        }}

        /* Radio group -> pill tabs (used for context / occasion pickers) */
        div[role="radiogroup"] {{ gap: 8px; }}
        div[role="radiogroup"] label {{
            border: 1px solid {BORDER};
            border-radius: 999px;
            padding: 6px 16px !important;
            transition: all 0.2s ease;
        }}
        div[role="radiogroup"] label:hover {{ border-color: {ACCENT}; }}

        /* File uploader -> soft drag & drop card */
        section[data-testid="stFileUploaderDropzone"] {{
            border-radius: 20px !important;
            border: 1.5px dashed {ACCENT_SOFT} !important;
            background-color: #FDFCFA !important;
        }}
        section[data-testid="stFileUploaderDropzone"] button {{
            border-radius: 999px !important;
        }}

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background-color: {CARD_BG} !important;
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] .block-container {{ padding-top: 2.2rem; }}

        div[data-testid="stSidebarNav"] {{ display: none; }}

        div[data-testid="stPageLink"] {{
            border-radius: 12px !important;
            padding: 7px 10px !important;
            margin-bottom: 3px;
            transition: background-color 0.2s ease;
        }}
        div[data-testid="stPageLink"]:hover {{ background-color: #FAF6EF !important; }}
        div[data-testid="stPageLink"] p {{
            font-family: {DISPLAY_FONT} !important;
            font-size: 14px !important;
            font-weight: 500;
            letter-spacing: 0.01em;
        }}

        .closet-logo {{
            font-family: {DISPLAY_FONT};
            font-size: 21px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {TEXT_PRIMARY};
            padding: 4px 4px 0 4px;
        }}
        .closet-logo-rule {{
            height: 2px;
            width: 32px;
            background: {ACCENT};
            margin: 8px 4px 18px 4px;
        }}

        /* ---------- Metrics ---------- */
        div[data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 1px 2px rgba(17,17,17,0.04);
            transition: box-shadow 0.25s ease;
        }}
        div[data-testid="stMetric"]:hover {{ box-shadow: 0 10px 22px rgba(17,17,17,0.07); }}
        div[data-testid="stMetricValue"] {{
            font-family: {DISPLAY_FONT} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        div[data-testid="stMetricLabel"] {{ color: {TEXT_SECONDARY} !important; }}

        /* ---------- Alerts ---------- */
        div[data-testid="stAlert"] {{
            border-radius: 14px !important;
            font-family: {BODY_FONT} !important;
            border: 1px solid {BORDER} !important;
        }}

        /* ---------- Misc ---------- */
        hr {{ border-color: {BORDER} !important; }}
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Editorial text helpers
# ---------------------------------------------------------------------------
def eyebrow(text):
    """Small uppercase gold kicker label, used above hero/section titles."""
    st.markdown(
        f'<div style="font-family:{DISPLAY_FONT};font-size:12px;font-weight:600;'
        f'letter-spacing:0.14em;text-transform:uppercase;color:{ACCENT_DARK};'
        f'margin-bottom:6px;">{text}</div>',
        unsafe_allow_html=True,
    )


def section_heading(title, subtitle=None):
    """Consistent section header used to open each page block."""
    html = (
        f'<div style="margin:6px 0 2px 0;font-family:{DISPLAY_FONT};font-size:24px;'
        f'font-weight:600;letter-spacing:-0.01em;color:{TEXT_PRIMARY};">{title}</div>'
    )
    if subtitle:
        html += (
            f'<div style="font-size:13.5px;color:{TEXT_SECONDARY};'
            f'margin:2px 0 16px 0;">{subtitle}</div>'
        )
    else:
        html += '<div style="margin-bottom:10px;"></div>'
    st.markdown(html, unsafe_allow_html=True)


def divider(width=44):
    st.markdown(
        f'<div style="height:2px;width:{width}px;background:{ACCENT};margin:10px 0 20px 0;"></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
def score_ring(score, size=64):
    """Circular match-score badge - gold conic-gradient ring, score centered."""
    pct = max(0, min(100, score))
    return f"""
    <div style="position:relative;width:{size}px;height:{size}px;border-radius:50%;
                background:conic-gradient({ACCENT} {pct * 3.6}deg, {BORDER} 0deg);
                display:flex;align-items:center;justify-content:center;flex-shrink:0;">
      <div style="width:{size - 10}px;height:{size - 10}px;border-radius:50%;
                  background:{CARD_BG};display:flex;align-items:center;justify-content:center;">
        <span style="font-family:{DISPLAY_FONT};font-size:{size * 0.27}px;font-weight:700;
                     color:{TEXT_PRIMARY};">{int(pct)}</span>
      </div>
    </div>
    """


def pill_badge(text, color=ACCENT, text_color="#fff"):
    """Small rounded uppercase pill label, e.g. for formality/category/status tags."""
    return (
        f'<span style="display:inline-block;padding:4px 12px;border-radius:999px;'
        f'background-color:{color};color:{text_color};font-family:{DISPLAY_FONT};'
        f'font-size:11px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;'
        f'margin-right:6px;">{text}</span>'
    )


def color_swatch_row(colors, swatch_size=22):
    """Renders a row of small color swatches (for multi-color items) with names."""
    html = '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">'
    for c in colors:
        html += (
            f'<div style="display:flex;align-items:center;gap:6px;">'
            f'<div style="width:{swatch_size}px;height:{swatch_size}px;border-radius:7px;'
            f'background-color:{c["hex"]};border:1px solid {BORDER};"></div>'
            f'<span style="font-size:12px;color:{TEXT_SECONDARY};">{c["name"]}</span>'
            f'</div>'
        )
    html += "</div>"
    return html


def sidebar_nav(total_count=None, dirty_count=None):
    """
    Renders the branded 'Closet' wordmark, icon nav links, and (if counts are
    passed) the Closet Health ring at the bottom of the sidebar.
    Call once per page, right after apply_theme().
    """
    import streamlit as st

    with st.sidebar:
        st.markdown('<div class="closet-logo">Closet</div>', unsafe_allow_html=True)
        st.markdown('<div class="closet-logo-rule"></div>', unsafe_allow_html=True)

        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/1_Add_Item.py", label="Add Item", icon="➕")
        st.page_link("pages/6_AI_Suggestion.py", label="AI Suggestion", icon="🤖")
        st.page_link("pages/3_Suggest_Outfit.py", label="Suggestions", icon="✨")
        wash_label = f"Wash Alerts ({dirty_count})" if dirty_count else "Wash Alerts"
        st.page_link("pages/4_Wash_Alerts.py", label=wash_label, icon="🧺")
        st.page_link("pages/5_Reserve_Event.py", label="Reserve Event", icon="📅")
        st.page_link("pages/2_Closet_Grid.py", label="Closet Grid", icon="🗂️")
        st.page_link("pages/7_Shopping.py", label="Shopping", icon="🛍️")

        if total_count is not None:
            st.markdown("---")
            st.markdown(
                f'<div style="font-family:{DISPLAY_FONT};font-size:12px;font-weight:600;'
                f'letter-spacing:0.08em;text-transform:uppercase;color:{TEXT_SECONDARY};'
                f'margin-bottom:10px;">Closet Health</div>',
                unsafe_allow_html=True,
            )
            clean_pct = 100 if total_count == 0 else round(100 * (total_count - (dirty_count or 0)) / total_count)
            label = "Good" if clean_pct >= 60 else "Fair" if clean_pct >= 40 else "Low"
            note = "You're all set" if clean_pct >= 60 else "Do a wash run soon"
            c1, c2 = st.columns([1, 1.4])
            with c1:
                st.markdown(score_ring(clean_pct, size=54), unsafe_allow_html=True)
            with c2:
                st.markdown(f"**{label}**")
                st.caption(note)


def safe_image(path, **kwargs):
    """
    Wraps st.image() so a missing/moved file (deleted photo, path copied
    from another machine, etc.) shows a small placeholder instead of
    crashing the whole page.
    """
    import os
    import streamlit as st

    try:
        if path and os.path.exists(path):
            st.image(path, **kwargs)
        else:
            st.caption("🖼️ Image not found")
    except Exception:
        st.caption("🖼️ Couldn't load image")


STATUS_COLORS = {
    "clean": SUCCESS,
    "dirty": ERROR,
    "reserved": WARNING,
}
