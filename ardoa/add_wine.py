#!/usr/bin/env python3
"""
add_wine.py — Research a wine using Claude + Tavily and output a JS entry
ready to paste into the wines[] array in index.html.

Setup:
    pip install -r requirements.txt
    cp .env.example .env
    # Edit .env and add your API keys

Usage:
    python add_wine.py
"""

import os
import sys
from pathlib import Path

# Load .env if present (optional — plain env vars work too)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

try:
    from anthropic import Anthropic
    from tavily import TavilyClient
except ImportError:
    print("Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)


# ── Canonical wine schema example — keeps Claude on-format ───────────────────

SCHEMA_EXAMPLE = """{
    name: "Ercole Barbera del Monferrato",
    vintage: "2024",
    type: "red",
    grape: "100% Barbera",
    grapeDetail: "Barbera is Piedmont's workhorse grape - high acidity, low tannins, makes it incredibly food-friendly",
    region: "Monferrato, Piedmont",
    appellation: "Barbera del Monferrato DOC",
    country: "Italy",
    winemaker: "Ercole Wines - Named after Ercole (Hercules), referencing the strength and character of Piedmontese wines. This project focuses on bringing authentic Piedmontese varieties to a wider audience, working with local growers who practice sustainable viticulture in the rolling hills of Monferrato. The winery emphasizes minimal intervention and respecting traditional winemaking methods passed down through generations.",
    tasting: "Bright cherry (morello), raspberry, dried herbs, hints of almond and black pepper. Medium body with high acidity, low tannins, and a refreshing, tangy finish.",
    alcohol: "13%",
    serving: "Slightly chilled (55-60°F / 13-15°C)",
    notes: "Barbera is Piedmont's most-planted grape (ahead of Nebbiolo), covering over 50% of the region's vineyards. Its naturally high acidity and low tannins make it incredibly food-friendly. Fun fact: Barbera was once considered a peasant grape but has risen to prominence thanks to modern winemaking. The Monferrato DOC was established in 1994 and sits between the famous Langhe and Asti zones."
}"""


def ask(label, required=True):
    """Prompt user for input, re-prompting if required and blank."""
    while True:
        val = input(label).strip()
        if val or not required:
            return val
        print("  (required)")


def format_results(results, max_chars=1500):
    """Format Tavily search results into a readable block for the prompt."""
    lines = []
    for r in results.get("results", []):
        lines.append(f"SOURCE: {r.get('url', 'unknown')}")
        lines.append(f"TITLE:  {r.get('title', '')}")
        content = r.get("content", "").strip()
        if len(content) > max_chars:
            content = content[:max_chars] + "…"
        lines.append(f"TEXT:   {content}")
        lines.append("")
    return "\n".join(lines) if lines else "(no results)"


def main():
    print("\n=== Ardoa Wine Research ===\n")

    # ── API key checks ────────────────────────────────────────────────────────

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    tavily_key    = os.environ.get("TAVILY_API_KEY")

    if not anthropic_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        print("  → Add it to .env  or  run: export ANTHROPIC_API_KEY=sk-ant-...")
        print("  → Get a key at: https://console.anthropic.com")
        sys.exit(1)

    if not tavily_key:
        print("Error: TAVILY_API_KEY not set.")
        print("  → Add it to .env  or  run: export TAVILY_API_KEY=tvly-...")
        print("  → Get a free key at: https://tavily.com")
        sys.exit(1)

    # ── Gather wine details ───────────────────────────────────────────────────

    print("Enter wine details (* = required):\n")
    producer    = ask("Producer *: ")
    wine_name   = ask("Wine name  (if separate from producer, else Enter): ", required=False)
    grape       = ask("Grape variety/varieties *: ")
    vintage     = ask("Vintage year *: ")
    region      = ask("Region *: ")
    country     = ask("Country *: ")
    wine_type   = ask("Type  (red / white / rosé / sparkling / orange) *: ")
    appellation = ask("Appellation  (DOC, AVA, etc. — optional): ", required=False)
    alcohol_pct = ask("Alcohol %  (optional, skip if unknown): ", required=False)
    extra       = ask("Any extra context to include  (optional): ", required=False)

    display_name = f"{producer} {wine_name}".strip() if wine_name else producer
    search_base  = f"{producer} {wine_name or ''} {vintage}".strip()

    print(f"\nResearching {display_name} {vintage}...\n")

    # ── Web research — three targeted searches ────────────────────────────────

    tavily = TavilyClient(api_key=tavily_key)

    print("  [1/3] Producer tech sheet and winery notes...")
    tech = tavily.search(
        query=f"{search_base} tech sheet winery",
        search_depth="advanced",
        max_results=5,
    )

    print("  [2/3] Vintage-specific reviews and tasting notes...")
    reviews = tavily.search(
        query=f"{search_base} tasting notes review",
        search_depth="advanced",
        max_results=5,
        # Prioritise reputable, vintage-tagged sources
        include_domains=[
            "winemag.com", "wineenthusiast.com", "wine-searcher.com",
            "vivino.com", "cellartracker.com", "jancisrobinson.com",
            "decanter.com",
        ],
    )

    print("  [3/3] Producer background and story...")
    producer_info = tavily.search(
        query=f"{producer} winery about history",
        search_depth="basic",
        max_results=3,
    )

    # Pull out PDF tech sheet URL if one was found
    tech_sheet_pdf = next(
        (r["url"] for r in tech.get("results", []) if r.get("url", "").endswith(".pdf")),
        None,
    )

    research = (
        f"=== PRODUCER TECH SHEET / WINERY NOTES ===\n{format_results(tech)}\n\n"
        f"=== VINTAGE-SPECIFIC REVIEWS ===\n{format_results(reviews)}\n\n"
        f"=== PRODUCER BACKGROUND ===\n{format_results(producer_info)}"
    )
    if tech_sheet_pdf:
        research += f"\n\nTECH SHEET PDF FOUND: {tech_sheet_pdf}"

    # ── Claude synthesis ──────────────────────────────────────────────────────

    print("\nGenerating wine entry with Claude...\n")

    system_prompt = f"""You are a sommelier writing staff reference entries for Ardoa Wine Bar.

Output ONLY a single raw JavaScript object literal.
- No const / let / var declaration
- No markdown code fences
- No explanation or surrounding text
- Start with {{ and end with }}

Use this exact schema and writing style:
{SCHEMA_EXAMPLE}

Field rules:

name        → "[Producer] [Wine name]" as one string
type        → exactly one of: red | white | rosé | sparkling | orange
grape       → "100% VarietyName" or "X% Variety, Y% Variety"
grapeDetail → one specific, educational sentence about the grape(s) — not marketing copy
region      → sub-region or general area, e.g. "Monferrato, Piedmont" or "Finger Lakes"
appellation → formal designation: DOC, DOCG, AVA, AOC, DO, etc.
country     → full country name
winemaker   → "[Producer name] - " then 2-3 sentences on story, philosophy, location. Present tense.
tasting     → exactly two sentences:
              (1) aromas and flavors — be specific, name the fruit and secondary notes
              (2) structure — body, acidity, tannins, finish
alcohol     → e.g. "13.5%" — OMIT THIS FIELD ENTIRELY if not confirmed in the research. Never guess.
serving     → use the correct style for the wine type:
              Light reds / chillable reds: "Slightly chilled (55-60°F / 13-15°C)"
              Full reds: "Room temperature (60-65°F / 16-18°C)"
              Whites / Rosé: "Well chilled (45-50°F / 7-10°C)"
              Sparkling: "Well chilled (40-45°F / 4-7°C)"
notes       → 3-4 sentences: grape history, regional context, producer achievements, a memorable
              fun fact a staff member could repeat to a guest. Use "Fun fact:" if there is a good one.
pronunciation → ONLY include if the name is genuinely tricky for English speakers.
              Format: "Word: phonetic · Word2: phonetic"
              Omit entirely for names that are straightforward.

VINTAGE ACCURACY — CRITICAL:
The target vintage is {vintage}. The research may contain reviews for multiple vintages of this wine.
Wines change significantly year to year. Only use tasting notes and critic scores that explicitly
state they cover the {vintage} vintage. If a review does not specify a vintage, discard it entirely.
The producer's own tech sheet for {vintage} is the primary source. Critic notes from verified
publications (Wine Enthusiast, Decanter, Jancis Robinson) are secondary, {vintage} vintage only.

All string values must use double quotes."""

    user_prompt = f"""Create a wine entry for:

Producer:    {producer}
Wine name:   {wine_name or "(same as producer)"}
Grape:       {grape}
Vintage:     {vintage}
Region:      {region}
Country:     {country}
Type:        {wine_type}
Appellation: {appellation or "(find in research)"}
Alcohol:     {alcohol_pct or "(find in research — omit the field entirely if not confirmed)"}
Extra notes: {extra or "none"}

Research findings:

{research}"""

    client   = Anthropic(api_key=anthropic_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    output = response.content[0].text.strip()

    # ── Output ────────────────────────────────────────────────────────────────

    print("=" * 64)
    print("Paste this into the wines[] array in index.html:")
    print("=" * 64)
    print()
    print(output)
    print()
    print("=" * 64)

    if tech_sheet_pdf:
        print(f"Tech sheet PDF: {tech_sheet_pdf}")

    cost = (response.usage.input_tokens * 3 + response.usage.output_tokens * 15) / 1_000_000
    print(f"Tokens — in: {response.usage.input_tokens}  out: {response.usage.output_tokens}  (~${cost:.4f})\n")


if __name__ == "__main__":
    main()
