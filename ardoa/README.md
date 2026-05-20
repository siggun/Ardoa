# Ardoa Wine Bar - Staff Study Guide

An interactive training website for Ardoa Wine Bar staff. Covers wines, beers, food, pairings, wine regions, and daily operations tools — all in a single HTML file with no dependencies.

## Features

### Study & Training
- **Wine List** - 24 wines in the Enomatic system with tasting notes, pairings, and tech sheets
- **Beer List** - 8 craft beers with descriptions
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

## Tech Stack

- Pure vanilla HTML, CSS, and JavaScript (~9,500 lines)
- No frameworks, no build tools, no dependencies
- Single-file architecture (`index.html`)
- External fonts: Google Fonts (Cinzel + Crimson Text)

## Getting Started

Open `index.html` in a web browser. No build step or server required.

For local development with a live server:

```bash
# Python 3
python -m http.server 8000

# Node.js (npx)
npx serve .
```

Then open `http://localhost:8000` in your browser.

## Deployment

Deploy to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- Any web server that serves static files

## Browser Support

Tested and optimized for:
- Chrome / Edge (desktop and mobile)
- Firefox
- Safari (desktop and iOS) — significant effort went into iOS Safari compatibility

> **Note for iOS users:** If the site shows a blank page in a third-party browser app, open it in Safari directly.

## Development

All content lives in `index.html`. No build step — edit and refresh.

- **CSS**: lines 1–4789
- **HTML**: lines 4790–5973
- **JavaScript / data**: lines 5974–9526

To add a wine, beer, or food item: find the corresponding JS array in the script section and add an entry. The render functions handle the rest.

Time Clock and Opening Checklist state persist via `localStorage`.

## License

Private — Ardoa Wine Bar internal training materials.
