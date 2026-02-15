# Ardoa Wine Bar - Study Guide Website

## What This Is
An interactive educational website for Ardoa Wine Bar staff to learn about wines, beers, food pairings, and wine regions. Features quizzes, flashcards, printable study cards, and a comprehensive FAQ.

## Tech Stack
- **Single-file architecture**: Everything lives in `index.html` (~6,300 lines)
- **No frameworks, no build tools, no dependencies** - pure vanilla HTML/CSS/JS
- **External fonts only**: Google Fonts (Cinzel + Crimson Text)
- **Static hosting**: Can be deployed anywhere that serves files

## File Structure
```
/Ardoa
├── CLAUDE.md        (this file)
└── index.html       (entire website - HTML, CSS, and JS embedded)
```

## index.html Layout
- **Lines 1-2730**: CSS (`<style>` block) - gothic theme, responsive breakpoints, card styles
- **Lines 2730-3990**: HTML structure - header, sticky nav, 10 content sections
- **Lines 3990-6270**: JavaScript (`<script>` block) - data arrays, rendering functions, quiz logic

## Content Sections (10 tabs)
1. Wine List (24 wines in Enomatic system)
2. Beer Selection (8 craft beers)
3. Food Menu (cheeses, charcuterie, flatbreads, tapas, pates, desserts)
4. Wine Quiz (randomized multiple-choice)
5. Online Flashcards (flip-card study mode with wine/beer/food decks)
6. Quick Reference Tables
7. Wine Regions of the World (6 countries)
8. Enomatic System Info
9. Printable Study Cards
10. Wine FAQ (50+ questions by difficulty/category)

## Architecture Pattern
- **Data-driven rendering**: All content stored in JS arrays/objects, rendered to DOM by functions
- **Section-based navigation**: One section visible at a time, toggled via sticky nav buttons
- **Card-based UI**: Consistent card patterns across wines, beers, food, FAQs

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
- No build step - edit index.html directly and refresh browser
- All data (wines, beers, food, FAQs) is inline in the JS section
- To add a new wine/beer/food item, add to the corresponding JS array and the render function handles the rest
- Quiz questions are auto-generated from wine data
