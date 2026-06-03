# Ardoa Wine Bar - Staff Study Guide

An interactive training website for Ardoa Wine Bar staff. Covers wines, beers, food, pairings, wine regions, and daily operations tools — backed by a FastAPI + PostgreSQL API with an admin interface for managing content.

## Features

### Study & Training
- **Wine List** - Wines in the Enomatic system with tasting notes, pairings, and tech sheets
- **Beer List** - Craft beers with descriptions
- **Food Menu** - Cheeses, charcuterie, flatbreads, tapas, pates, and desserts
- **Wine Quiz** - Randomized multiple-choice questions to test knowledge
- **Online Flashcards** - Interactive flip-card study mode for wines, beers, and food
- **Wine Regions** - Educational content covering 6 major wine-producing countries
- **Wine Varietals** - Grape variety profiles from the wine list
- **Pronunciations** - Phonetic guides for wine and producer names
- **Food Pairings** - Wine-to-food pairing matrix
- **Wine FAQ** - 50+ questions organized by difficulty and category
- **Enomatic System** - How to operate the wine dispensing system
- **Print Cards** - Printable physical study materials

### Daily Operations
- **Quick Reference** - At-a-glance tables for wines, beers, and food
- **Time Clock** - Staff clock in/out with manual entry and delete (saved in browser)
- **Opening Checklist** - Pre-shift checklist for opening procedures
- **Timers** - Kitchen/service countdown timers

### Admin (`/admin.html`)
- Add, edit, archive, and delete wines, beers, and food items
- **AI Wine Research** — type a wine name and Claude fills in tasting notes, region, pairings, ABV, and more automatically
- Password-protected (HTTP Basic Auth)

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript (`index.html`) — no frameworks, no build tools
- **Backend**: Python + FastAPI served on Railway
- **Database**: PostgreSQL (Railway add-on)
- **AI**: Anthropic Claude API for wine research
- **Fonts**: Google Fonts (Cinzel + Crimson Text)

## File Structure

```
/
├── index.html          # Public staff training site
├── admin.html          # Admin content management interface
├── backend/
│   ├── main.py         # FastAPI app entry point
│   ├── models.py       # SQLModel DB models (Wine, Beer, FoodItem)
│   ├── database.py     # DB engine and session
│   ├── auth.py         # HTTP Basic Auth
│   ├── routers/        # API route handlers (wines, beers, food)
│   ├── services/       # AI research service (Anthropic SDK)
│   ├── seed.py         # One-time DB seed script
│   ├── seed_data.py    # Original wine/beer/food data as Python
│   └── requirements.txt
├── Procfile            # Railway process definition
└── railway.toml        # Railway deploy config
```

## API Endpoints

Public (no auth):
- `GET /api/wines` — active wines with food pairings
- `GET /api/wines/archived` — archived wines
- `GET /api/beers` — all beers
- `GET /api/food` — all food grouped by category
- `GET /api/health` — health check

Admin (HTTP Basic Auth required):
- `POST/PUT/DELETE /api/wines/{id}` — wine CRUD
- `PATCH /api/wines/{id}/archive` — archive a wine
- `PATCH /api/wines/{id}/restore` — restore archived wine
- `POST /api/wines/research` — AI research: `{"name": "wine name"}` → prefilled wine object
- Same CRUD pattern for `/api/beers` and `/api/food/item/{id}`

## Local Development

```bash
pip install -r backend/requirements.txt

# Run with SQLite (no Postgres needed locally)
DATABASE_URL=sqlite:///./dev.db ADMIN_PASSWORD=secret ANTHROPIC_API_KEY=sk-... \
  uvicorn backend.main:app --reload

# Seed the database with existing wine/beer/food data
DATABASE_URL=sqlite:///./dev.db python -m backend.seed
```

Open `http://localhost:8000` for the public site, `http://localhost:8000/admin.html` for the admin.

## Railway Deployment

1. Connect this repo to a Railway project
2. Add the **PostgreSQL** plugin — `DATABASE_URL` is injected automatically
3. Set environment variables in the Railway dashboard:
   - `ADMIN_PASSWORD` — password for the admin interface
   - `ANTHROPIC_API_KEY` — your Claude API key
   - `ALLOWED_ORIGINS` — comma-separated allowed origins (e.g. `https://your-app.up.railway.app`)
4. After the first deploy, run the seed job once:
   ```
   python -m backend.seed
   ```

## Browser Support

Tested and optimized for:
- Chrome / Edge (desktop and mobile)
- Firefox
- Safari (desktop and iOS) — significant effort went into iOS Safari compatibility

> **Note for iOS users:** If the site shows a blank page in a third-party browser app, open it in Safari directly.

## License

Private — Ardoa Wine Bar internal training materials.
