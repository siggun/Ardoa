# Ardoa Wine Bar - Study Guide Website

## What This Is
An interactive educational website for Ardoa Wine Bar staff to learn about wines, beers, food pairings, and wine regions. Features quizzes, flashcards, printable study cards, a comprehensive FAQ, a time clock, opening checklist, kitchen timers, and more.

## Tech Stack
- **Single-file architecture**: Everything lives in `index.html` (~9,500 lines)
- **No frameworks, no build tools, no dependencies** - pure vanilla HTML/CSS/JS
- **External fonts only**: Google Fonts (Cinzel + Crimson Text)
- **Static hosting**: Can be deployed anywhere that serves files

## File Structure
```
/Ardoa
├── CLAUDE.md        (this file - AI assistant instructions)
├── README.md        (human-facing project overview)
├── .gitignore       (ignores OS/editor junk files)
└── index.html       (entire website - HTML, CSS, and JS embedded)
```

## index.html Layout
- **Lines 1-4789**: CSS (`<style>` block) - gothic theme, responsive breakpoints, card styles
- **Lines 4790-5973**: HTML structure - header, sticky nav, 16 content sections
- **Lines 5974-9526**: JavaScript (`<script>` block) - data arrays, rendering functions, quiz logic, time clock, timers

## Content Sections (16 tabs, in nav order)
1. **Wine List** (`#techsheets`) - 24 wines in the Enomatic system with tasting notes and pairings
2. **Quick Reference** (`#quickref`) - At-a-glance tables for wines, beers, food
3. **Time Clock** (`#timeclock`) - Staff clock in/out with manual entry and delete
4. **Opening Checklist** (`#checklist`) - Pre-shift checklist for opening procedures
5. **Timers** (`#timers`) - Kitchen/service countdown timers
6. **Beer List** (`#beerlist`) - 8 craft beers with descriptions
7. **Food Menu** (`#food`) - Cheeses, charcuterie, flatbreads, tapas, pates, desserts
8. **Wine Quiz** (`#flashcards`) - Randomized multiple-choice questions
9. **Online Flashcards** (`#onlineflashcards`) - Flip-card study mode (wine/beer/food decks)
10. **Wine Regions** (`#wineregions`) - Educational content on 6 major wine-producing countries
11. **Enomatic System** (`#enomatic`) - How to operate the wine dispensing system
12. **Print Cards** (`#printcards`) - Printable physical study materials
13. **Wine FAQ** (`#faq`) - 50+ questions organized by difficulty and category
14. **Pronunciations** (`#pronunciations`) - Phonetic guides for wine/producer names
15. **Food Pairings** (`#foodpairings`) - Wine-to-food pairing matrix
16. **Wine Varietals** (`#varietals`) - Grape variety profiles from the wine list

## Architecture Pattern
- **Data-driven rendering**: All content stored in JS arrays/objects, rendered to DOM by functions
- **Section-based navigation**: One section visible at a time, toggled via sticky nav links
- **Card-based UI**: Consistent card patterns across wines, beers, food, FAQs
- **URL deep linking**: Sections are addressable via `#hash` in the URL (e.g. `index.html#faq`)

## iOS Safari Compatibility (Critical)
Significant engineering went into making this work on iOS Safari. Key constraints:

- **forceRepaint() helper**: Must be called after every `innerHTML` update - iOS Safari's compositor doesn't always repaint dynamically inserted content
- **No rgba() backgrounds on cards**: Use opaque hex colors only - rgba + position:relative creates invisible compositing layers on iOS
- **No ::before/::after pseudo-elements on cards**: These create extra compositing layers that iOS fails to paint
- **No backdrop-filter on sticky nav**: Conflicts with `position: sticky` on iOS Safari
- **No CSS animations on cards**: Opacity transitions cause rendering bugs on iOS

If making visual changes, always test on an actual iOS device or Safari. These bugs don't reproduce in Chrome DevTools mobile emulation.

## Design Theme
Gothic/wine aesthetic with these key colors:
- `--midnight: #0a0a0f` (background)
- `--deep-purple: #1a1025`
- `--wine-blood: #4a0e1a`
- `--aged-burgundy: #6b1c2e`
- `--pale-gold: #c4a875` (accent/text)
- `--bone: #e8e4dc` (light text)

## Responsive Breakpoints
- Desktop: default
- Tablet: 768px
- Mobile: 480px
- Small mobile: 320px

## Development Notes
- No build step - edit `index.html` directly and refresh browser
- All data (wines, beers, food, FAQs) is inline in the JS section (~line 5974+)
- To add a new wine/beer/food item, add to the corresponding JS array; the render function handles the rest
- Quiz questions are auto-generated from wine data
- Time Clock data is stored in `localStorage` (key: `ardoaTimeEntries`)
- Opening Checklist state is stored in `localStorage` (key: `ardoaChecklist`)
