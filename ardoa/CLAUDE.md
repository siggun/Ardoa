# Ardoa Wine Bar - Study Guide Website

## What This Is
An interactive reference website for Ardoa Wine Bar staff covering wines, beers, food, and wine regions. Light-themed, mobile-friendly, single-file site.

## Tech Stack
- **Single-file architecture**: Everything lives in `index.html` (~4,100 lines)
- **No frameworks, no build tools, no dependencies** - pure vanilla HTML/CSS/JS
- **External fonts only**: Google Fonts (Cinzel + Crimson Text + VT323)
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
- **Lines 8-1789**: CSS (`<style>` block) - light theme, responsive breakpoints, card styles, dark theme overrides, cyberpunk theme
- **Lines 1791-2535**: HTML structure - header, sticky nav, 6 sections
- **Lines 2536-4119**: JavaScript (`<script>` block) - data arrays and rendering functions

## Content Sections (6 nav tabs, in nav order)
1. **Wine List** (`#techsheets`) - Current wines in the Enomatic system with tasting notes and pairings
2. **Beer List** (`#beerlist`) - Craft beers with descriptions and filter by type
3. **Food Menu** (`#food`) - Cheeses, charcuterie, flatbreads, tapas, pates, desserts
4. **Wine Regions** (`#wineregions`) - Educational content on major wine-producing countries
5. **Pronunciations** (`#pronunciations`) - Phonetic guides auto-generated from wine/beer data
6. **Wine Archive** (`#winearchive`) - Previously featured wines, no longer on the list

## JS Data Arrays (all inline in the script block)
- `wines` - current wine list
- `archivedWines` - retired wines
- `beers` - beer list
- `cheeses`, `charcuterie`, `flatbreads`, `tapas`, `pates`, `desserts` - food menu categories

## Architecture Pattern
- **Data-driven rendering**: All content stored in JS arrays/objects, rendered to DOM by render functions
- **Section-based navigation**: One section visible at a time, toggled via sticky nav links
- **Card-based UI**: Consistent card patterns across wines, beers, food
- **URL deep linking**: Sections addressable via `#hash` (e.g. `index.html#beerlist`)

## Theming
- **Light theme (default)**: Clean white/warm off-white, burgundy accents — matches ardoawinebar.com
- **Dark theme**: Toggled via moon/sun button in the header, persisted in `localStorage` (`ardoa-theme`). Enables fog and vine overlay layers.
- Key light-theme CSS variables: `--wine-blood: #4a1a28`, `--aged-burgundy: #6b2d3e`, `--pale-gold: #4a1a28`, `--bone: #2c2c2c`
- Legacy CSS variable aliases (`--burgundy`, `--gold`, `--cream`, `--charcoal`) still used in Wine Regions styles — do not remove them

## iOS Safari Compatibility (Critical)
Significant engineering went into making this work on iOS Safari. Key constraints:

- **forceRepaint() helper**: Must be called after every `innerHTML` update - iOS Safari's compositor doesn't always repaint dynamically inserted content
- **No rgba() backgrounds on cards**: Use opaque hex colors only - rgba + position:relative creates invisible compositing layers on iOS
- **No ::before/::after pseudo-elements on cards**: These create extra compositing layers that iOS fails to paint
- **No backdrop-filter on sticky nav**: Conflicts with `position: sticky` on iOS Safari
- **No CSS animations on cards**: Opacity transitions cause rendering bugs on iOS

If making visual changes, always test on an actual iOS device or Safari. These bugs don't reproduce in Chrome DevTools mobile emulation.

## Responsive Breakpoints
- Desktop: default
- Tablet: 768px
- Mobile: 480px
- Small mobile: 320px

## Development Notes
- No build step - edit `index.html` directly and refresh browser
- To add a wine: append to the `wines` array; the render function handles the rest
- To archive a wine: move it from `wines` to `archivedWines`
