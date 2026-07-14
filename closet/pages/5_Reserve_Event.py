import datetime
import streamlit as st
from db import queries
from services.event_reservation import reserve_items_for_event, get_upcoming_events, cancel_reservation
from utils.styling import apply_theme, sidebar_nav, eyebrow, section_heading

st.set_page_config(page_title="Reserve Event - Closet", page_icon="📅", layout="wide")
apply_theme()

_all_items_for_nav = queries.get_all_items()
sidebar_nav(total_count=len(_all_items_for_nav), dirty_count=len([i for i in _all_items_for_nav if i["is_dirty"]]))

eyebrow("Plan Ahead")
st.markdown("# Reserve Items for an Event")
st.caption("Lock specific items away so they don't get suggested (or accidentally worn) before your event.")
st.markdown("")

with st.container(border=True):
    with st.form("reserve_form"):
        event_name = st.text_input("Event name", placeholder="e.g. Cousin's formal dinner")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", value=datetime.date.today())
        with col2:
            end_date = st.date_input("End date", value=datetime.date.today())

        all_items = queries.get_all_items()
        item_options = {f"#{i['id']} - {i['sub_type']} ({i['color_name']})": i["id"] for i in all_items}
        selected_labels = st.multiselect("Items to reserve", list(item_options.keys()))

        submitted = st.form_submit_button("Reserve", type="primary")

        if submitted:
            if not event_name or not selected_labels:
                st.error("Please provide an event name and select at least one item.")
            elif end_date < start_date:
                st.error("End date must be after start date.")
            else:
                item_ids = [item_options[label] for label in selected_labels]
                reserve_items_for_event(event_name, start_date.isoformat(), end_date.isoformat(), item_ids)
                st.success(f"Reserved {len(item_ids)} item(s) for '{event_name}'.")
                st.rerun()

st.markdown("")
section_heading("Upcoming / Active Reservations")

events = get_upcoming_events()
if not events:
    st.info("No reservations yet.")
else:
    for event in events:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{event['event_name']}**")
                st.caption(f"{event['start_date']} → {event['end_date']}")
                st.caption(f"Item IDs reserved: {event['reserved_item_ids']}")
            with col2:
                if st.button("Cancel", key=f"cancel_{event['id']}"):
                    cancel_reservation(event["id"])
                    st.success("Reservation cancelled - items are unlocked.")
                    st.rerun()
