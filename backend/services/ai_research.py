import json
import os
import re

import anthropic

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a wine expert assistant for Ardoa Wine Bar in Charleston, SC.
Given a wine name, return a JSON object with accurate, engaging descriptions suitable for
wine-by-the-glass staff training and guest-facing materials.

Return ONLY valid JSON — no markdown, no explanation. The JSON must have exactly these fields:
{
  "name": "Full wine name as it should appear on the wine list",
  "vintage": "Year as a string, e.g. '2022'",
  "type": "One of: red, white, rose, orange, sparkling",
  "grape": "Grape variety or blend, e.g. '100% Cabernet Sauvignon'",
  "grape_detail": "2-3 sentence description of the grape variety's character and origin",
  "region": "Sub-region and region, e.g. 'Napa Valley, California'",
  "appellation": "Official appellation/AOC/DOC, e.g. 'Napa Valley AVA'",
  "country": "Country of origin",
  "winemaker": "Producer name and brief 1-sentence note about them",
  "tasting": "Tasting note: aromas and flavors in 2-3 sentences, specific and evocative",
  "food": "Brief food pairing summary, e.g. 'Grilled lamb, aged cheeses, mushroom dishes'",
  "food_pairings": [
    {"item": "Specific food item", "why": "1-sentence explanation of why it pairs well"},
    {"item": "Second food item", "why": "1-sentence explanation"},
    {"item": "Third food item", "why": "1-sentence explanation"}
  ],
  "alcohol": "ABV as string, e.g. '13.5%'",
  "serving": "Serving temperature recommendation, e.g. 'Room temperature (65-68°F / 18-20°C)'",
  "notes": "Educational paragraph (3-5 sentences) about the wine's history, style, or what makes it special",
  "pronunciation": "Phonetic pronunciation if the name is non-English, e.g. 'ehr-KOH-leh bar-BEHR-ah'",
  "pronunciation_guide_only": false
}

Be accurate. If you're unsure of a specific vintage detail, use reasonable estimates for the region and style.
Keep tasting notes vivid and specific — no generic wine-speak."""


async def research_wine(wine_name: str) -> dict:
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Research this wine: {wine_name}"}],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude added them
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)
