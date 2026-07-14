# Closet

A personal wardrobe management app built with Streamlit. Snap a photo of each item you own, and Closet handles the rest — tracking what's clean, suggesting outfits based on color theory and formality, and reminding you what needs a wash.

## Features

- **Add Item** — Upload a photo of a clothing item; Closet automatically detects its dominant color and lets you tag category, sub-type, formality, pattern, and season.
- **Closet Grid** — Browse your full inventory with filters by category and season, plus at-a-glance color, formality, and cleanliness status.
- **Suggestions** — Pick a context (office, university, friend hangout, trip) and season, and get outfits ranked by a color-and-formality match score.
- **AI Suggestion** — A zero-input version of Suggestions: reads the time of day, current weather, and calendar context to auto-pick a season and recommend today's outfit.
- **Wash Alerts** — See which items need washing and get warned when low item counts in a category start limiting your outfit options.
- **Reserve Event** — Lock specific items to a date range (e.g. a big event) so they're excluded from suggestions and everyday wear until then.
- **Shopping** — Checks a few Pakistani retailers for items that would fill gaps in your wardrobe (missing colors/types), or search manually.
- **Home dashboard** — Today's top outfit pick, quick stats (item count, items needing wash, reservations), recent activity, and upcoming reservations.

## Tech stack

- **Frontend**: [Streamlit](https://streamlit.io/) (multi-page app)
- **Database**: SQLite (file-based, auto-created on first run)
- **Weather**: [Open-Meteo](https://open-meteo.com/) API (no key required), defaults to Lahore, PK coordinates
- **Styling**: Custom design system in `utils/styling.py` — light, editorial theme (gold accents, Inter font)

## Project structure

```
closet/
├── app.py                      # Home dashboard
├── pages/
│   ├── 1_Add_Item.py           # Upload + tag a new item
│   ├── 2_Closet_Grid.py        # Browse/filter inventory
│   ├── 3_Suggest_Outfit.py     # Context-based outfit suggestions
│   ├── 4_Wash_Alerts.py        # Laundry tracking
│   ├── 5_Reserve_Event.py      # Reserve items for upcoming events
│   ├── 6_AI_Suggestion.py      # Context-aware "just tell me what to wear"
│   └── 7_Shopping.py           # Wardrobe gap-filling shopping search
├── services/
│   ├── color_extractor.py      # Dominant color detection from uploaded photos
│   ├── color_theory.py         # Color matching/compatibility rules
│   ├── matching_engine.py      # Outfit scoring and generation
│   ├── laundry_tracker.py      # Wear counts, dirty-item tracking
│   ├── event_reservation.py    # Reserve/cancel item holds for events
│   ├── weather.py              # Open-Meteo current weather fetch
│   ├── smart_context.py        # Time/weather → context inference for AI Suggestion
│   └── shopping_scraper.py     # Retailer search + gap detection
├── db/
│   ├── database.py             # SQLite connection + schema init/migration
│   └── queries.py              # All DB read/write queries
├── models/
│   └── schemas.py              # Dataclasses + fixed choice lists (categories, formality, etc.)
├── utils/
│   ├── styling.py               # Design system: theme, colors, reusable UI components
│   └── image_utils.py           # Image saving/handling helpers
└── data/
    ├── closet.db                # SQLite database (auto-created)
    └── images/                  # Uploaded clothing photos
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**

   ```bash
   streamlit run app.py
   ```

3. Open the URL Streamlit prints (usually `http://localhost:8501`).

No API keys or environment variables are required — the weather service uses Open-Meteo's free, keyless API, and the database is a local SQLite file created automatically on first run.

## How outfit matching works

Each item is tagged with a category, sub-type, formality level, pattern (neutral/printed), season, and dominant color. The matching engine combines:

- **Color compatibility** — via rules in `color_theory.py`
- **Formality alignment** — items are only paired with others of a compatible formality tier
- **Season fit** — `all-season` items match anything; season-specific items only show up when that season (or a colder-climate trip) is selected
- **Wear/cleanliness state** — dirty or reserved items are excluded from suggestions

Each candidate outfit gets a match score, and the highest-scoring combination is surfaced first.

## Notes

- Weather defaults to Lahore, PK coordinates (`services/weather.py`) — update `LAHORE_LAT`/`LAHORE_LON` if you're elsewhere.
- Uploaded images are stored locally in `data/images/`.
