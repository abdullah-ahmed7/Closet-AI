from db import queries

def reserve_items_for_event(event_name, start_date, end_date, item_ids):
    queries.add_reserved_event(event_name, start_date, end_date, item_ids)

def get_currently_reserved_ids():
    return queries.get_active_reserved_item_ids()

def get_upcoming_events():
    return queries.get_all_reserved_events()

def cancel_reservation(event_id):
    queries.delete_reserved_event(event_id)