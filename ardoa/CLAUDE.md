# Ardoa Wine Bar — Staff Reference Site

## The Soul of This Project

This is a lean, fast, single-page reference tool built for wine bar staff. It lives on their phones in a dim, noisy bar — pulled up mid-shift when a guest asks "what are the tasting notes on that Frappato?" The answer needs to appear instantly, with no login, no loading spinner, no friction.

The philosophy is **ruthless simplicity**. Every feature that was added then stripped away — quiz games, timers, time clocks, food pairing matrices — made the site heavier and harder to maintain without making staff meaningfully better at their jobs. What remains is exactly what staff need: wine info, beer info, food descriptions, wine regions, pronunciations. That's it.

**When in doubt, do less. A focused tool used daily beats a feature-rich tool ignored.**

---

## Who Uses This and How

- **Floor staff** — on an iPhone or Android, in Safari, during a shift. They need tasting notes and wine facts fast. They are not sitting down to study; they are standing at a table with a guest waiting.
- **The manager** — on a laptop, adding or archiving wines a few times a month by running `add_wine.py`, pasting the output into `index.html`, and pushing to GitHub.
- **No customers** — this is internal training material, not a public-facing menu.

This context should inform every decision. If a change makes the site slower to load, harder to navigate on a small screen, or harder to maintain — it's the wrong change.

---

## Explicit Rules

### NEVER
- Add npm packages, build tools, or anything that requires a build step
- Split content into multiple HTML files or introduce a backend
- Use `rgba()` backgrounds on card elements — breaks iOS Safari compositing
- Use `::before` / `::after` pseudo-elements on card elements — same reason
- Use `backdrop-filter` on the sticky nav — conflicts with `position: sticky` on iOS
- Add CSS animations or opacity transitions to card elements — causes iOS rendering bugs
- Call `innerHTML` without immediately calling `forceRepaint()` after — content renders invisible on iOS
- Remove the legacy CSS variable aliases (`--burgundy`, `--gold`, `--cream`, `--charcoal`) — still in active use in Wine Regions styles
- Add the `food` or `foodPairings` fields back to wine objects — deliberately removed
- Add a feature that wasn't explicitly requested — this project is actively being simplified

### ALWAYS
- Call `forceRepaint(el)` after every `innerHTML` assignment
- Use opaque hex colors on card backgrounds
- Keep everything in `index.html` — no exceptions
- Test visual changes in actual Safari or on an iOS device — Chrome DevTools emulation does not reproduce iOS compositor bugs

---

## Why These Constraints Exist

**Single file, no build step:** Staff serve this as a GitHub Pages URL, and sometimes as a local file on a phone with no internet. Zero dependencies means zero failure modes. A React app with a broken CDN goes blank; this file cannot fail to load.

**No rgba() on cards, no pseudo-elements, no backdrop-filter:** iOS Safari's GPU compositor creates invisible layers when `position: relative` is combined with transparent backgrounds. This produced blank wine cards that looked fine in Chrome but were completely invisible on iPhones. The fix is opaque hex colors everywhere on cards — no exceptions discovered the hard way.

**forceRepaint() after innerHTML:** iOS Safari doesn't always schedule a compositor paint pass after dynamic DOM insertion. The helper toggles `display: none` then `display: block` to force a reflow and paint. Without it, sections load as blank white boxes on older iPhones.

**No food/pairing fields:** Wine entries previously included `food` and `foodPairings` fields with pairing recommendations. These were removed because (1) pairing advice belongs in staff training, not a quick-reference tool, and (2) they were opinionated in ways that confused more than helped.

---

## File Structure

```
/ardoa
├── CLAUDE.md       — AI instructions (this file)
├── README.md       — human-facing project overview
├── add_wine.py     — AI research script for generating new wine entries
└── index.html      — the entire website (~3,800 lines, HTML + CSS + JS)
```

---

## index.html Layout

| Block | Lines | Contents |
|---|---|---|
| CSS | 8–1746 | Light theme, dark theme, responsive breakpoints, card styles |
| HTML | 1748–2492 | Header, sticky nav, 6 content sections |
| JavaScript | 2493–3803 | Data arrays, render functions, navigation logic |

**Key landmarks in the JS block:**
- `const wines = [` — line ~2495 — current wine list
- `const archivedWines = [` — line ~2965 — retired wines
- `const beers = [` — line ~3003 — beer list
- `const cheeses = [` — line ~3098 — food menu data begins

*Line numbers drift as content changes. Use search to find these if they've shifted.*

---

## Content Sections (6 nav tabs, in order)

1. **Wine List** (`#techsheets`) — Current wines with tasting notes, winemaker info, serving temp
2. **Beer List** (`#beerlist`) — Craft beers with descriptions, filterable by type
3. **Food Menu** (`#food`) — Cheeses, charcuterie, flatbreads, tapas, pâtés, desserts
4. **Wine Regions** (`#wineregions`) — Educational content on major wine-producing countries
5. **Pronunciations** (`#pronunciations`) — Phonetic guides auto-generated from wine/beer data
6. **Wine Archive** (`#winearchive`) — Previously featured wines no longer on the list

---

## Wine Object Schema

Every entry in `wines` and `archivedWines` must follow this shape exactly. This is the canonical reference — use it when adding wines manually or reviewing output from `add_wine.py`.

```javascript
{
    name: "Ercole Barbera del Monferrato",
    // "[Producer] [Wine name]" as one string. If the wine has no separate name, just the producer.

    vintage: "2024",
    // Four-digit year string. Required.

    type: "red",
    // Exactly one of: red | white | rosé | sparkling | orange

    grape: "100% Barbera",
    // Percentage(s) and variety name. E.g. "60% Grenache, 40% Syrah"

    grapeDetail: "Barbera is Piedmont's workhorse grape - high acidity, low tannins, makes it incredibly food-friendly",
    // One educational sentence about the grape(s). Hook, not marketing copy.

    region: "Monferrato, Piedmont",
    // Sub-region or general area. E.g. "Finger Lakes" or "Ribeira Sacra"

    appellation: "Barbera del Monferrato DOC",
    // Formal designation: DOC, DOCG, AVA, AOC, DO, etc.

    country: "Italy",

    // pronunciation — ONLY include if the name is genuinely non-obvious to English speakers.
    // Format: "Word: phonetic · Word2: phonetic"
    // Example: "Ribeira: ree-BAY-rah · Mencía: men-SEE-ah"
    // Omit entirely for straightforward names.

    winemaker: "Ercole Wines - Named after Ercole (Hercules), referencing the strength and character of Piedmontese wines. This project focuses on bringing authentic Piedmontese varieties to a wider audience, working with local growers who practice sustainable viticulture in the rolling hills of Monferrato. The winery emphasizes minimal intervention and respecting traditional winemaking methods passed down through generations.",
    // "[Producer name] - " then 2-3 sentences: story, philosophy, location. Present tense.

    tasting: "Bright cherry (morello), raspberry, dried herbs, hints of almond and black pepper. Medium body with high acidity, low tannins, and a refreshing, tangy finish.",
    // Two sentences: (1) aromas and flavors, (2) structure — body, acidity, tannins, finish.

    alcohol: "13%",
    // Omit this field entirely if unknown. Do not guess or leave blank.

    serving: "Slightly chilled (55-60°F / 13-15°C)",
    // Temperature in both °F and °C. Pick the right style:
    // Reds: "Room temperature (60-65°F / 16-18°C)" or "Slightly chilled (55-60°F / 13-15°C)"
    // Whites/Rosé: "Well chilled (45-50°F / 7-10°C)"
    // Sparkling: "Well chilled (40-45°F / 4-7°C)"

    notes: "Barbera is Piedmont's most-planted grape (ahead of Nebbiolo), covering over 50% of the region's vineyards. Its naturally high acidity and low tannins make it incredibly food-friendly. Fun fact: Barbera was once considered a 'peasant grape' but has risen to prominence thanks to modern winemaking. The Monferrato DOC was established in 1994 and sits between the famous Langhe and Asti zones.",
    // 3-4 sentences of educational/fun facts: grape history, regional context, producer story, interesting trivia.
    // This is what staff repeat to guests. Make it memorable.
}
```

**Fields that no longer exist — do not add them back:**
- `food` — removed
- `foodPairings` — removed

---

## Writing Style Guide

The voice is **educated but approachable** — a knowledgeable sommelier talking to a curious newcomer, not writing a textbook. Staff use this to answer guest questions, so the language should be something they can actually repeat at a table.

**Tasting notes:**
- Lead with fruit and aromatics, close with structure
- Be specific: "morello cherry" not "red fruit"; "graphite minerality" not "earthy"
- Always describe the finish — it's what guests remember

**Grape detail:**
- One sentence, educational hook
- Good: "Barbera is Piedmont's workhorse grape - high acidity, low tannins, makes it incredibly food-friendly"
- Bad: "A delightful grape beloved by winemakers for generations"

**Winemaker/Producer:**
- Always starts with producer name, then " - "
- Include where they are, what they believe, what makes them notable
- 2-3 sentences, present tense

**Notes field:**
- Fun facts and history that staff can actually use in conversation
- "Fun fact:" openers work well
- Include something surprising or counterintuitive when possible
- Avoid generic statements that could apply to any wine ("this region produces excellent wines")

---

## Common Workflows

### Adding a new wine
1. Run `python add_wine.py` in the project directory and answer the prompts
2. Copy the JS object from the output
3. Open `index.html`, find the `wines` array (search for `const wines = [`)
4. Paste the new entry with a `// Position N` comment above it
5. Verify it looks correct in the browser (open `index.html` locally)
6. `git add index.html && git commit -m "Add [Wine Name] [Vintage]" && git push`
7. GitHub Pages deploys automatically within ~60 seconds

### Archiving a wine
1. Cut the wine object from the `wines` array
2. Paste it into `archivedWines` (find `const archivedWines = [`)
3. Optionally add `archivedDate: "YYYY-MM"` and `replacedBy: "New Wine Name"` fields to the object
4. Commit and push

### Editing existing content
Edit `index.html` directly. No build step — save and refresh the browser.

---

## iOS Safari Compatibility

These are not stylistic preferences. They are load-bearing rules discovered through real iOS debugging. Every one of them was added after seeing a blank or broken UI on an actual device that looked fine in Chrome.

| Forbidden pattern | What goes wrong |
|---|---|
| `rgba()` backgrounds on cards | iOS compositor creates invisible layers when combined with `position: relative` |
| `::before` / `::after` on card elements | Extra compositing layers iOS fails to paint |
| `backdrop-filter` on sticky nav | Conflicts with `position: sticky`, breaks scroll behavior |
| CSS opacity transitions on cards | Cards flash, flicker, or disappear entirely |
| `innerHTML` without `forceRepaint()` | Dynamically inserted content never gets a compositor paint pass |

The `forceRepaint(el)` helper is defined in the script block. It toggles `display: none` → `display: block` to force the iOS compositor to schedule a paint. Call it after every `innerHTML` update, no exceptions.

**These bugs do not reproduce in Chrome DevTools mobile emulation.** Always test on real Safari or a real iOS device before declaring a visual change done.

---

## Theming

- **Light theme (default):** White/warm off-white, burgundy accents — matches ardoawinebar.com
- **Dark theme:** Toggled by moon/sun button in the header, state persisted in `localStorage` key `ardoa-theme`. Enables fog and vine overlay decorations.

**Active CSS variables:**
```css
--wine-blood:    #4a1a28
--aged-burgundy: #6b2d3e
--pale-gold:     #4a1a28
--bone:          #2c2c2c
```

**Legacy aliases (do not remove — actively used in Wine Regions styles):**
`--burgundy`, `--gold`, `--cream`, `--charcoal`

---

## Responsive Breakpoints

| Breakpoint | Max-width |
|---|---|
| Tablet | 768px |
| Mobile | 480px |
| Small mobile | 320px |

---

## What "Done" Looks Like

A correct change to this project:
- Touches only `index.html` (plus `CLAUDE.md` or `add_wine.py` when relevant)
- Introduces no new external dependencies
- Adds no unrequested features
- Renders correctly in Safari on an iPhone — not just Chrome on desktop
- Keeps total file size reasonable (the site should load in under 2 seconds on a slow bar wifi connection)

A bad change:
- Adds a framework "just to make it easier"
- Splits the site into multiple files
- Adds a feature because it seemed useful, not because it was asked for
- Works in Chrome but breaks on iOS
