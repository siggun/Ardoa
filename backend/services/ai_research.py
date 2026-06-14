import json
import os
import re

import anthropic

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a wine research assistant for Ardoa Wine Bar in Charleston, SC.
Given a wine name, find the REAL, SPECIFIC wine being referenced and return accurate information about it.

CRITICAL ACCURACY RULES:
- Do NOT guess or hallucinate. If the producer name is specific and real (e.g. "Grape Abduction"), look up that exact producer — do not substitute a similar-sounding one or assume a region.
- The producer's actual country and region MUST be correct. "Grape Abduction" is a Slovenian producer making orange wines — not Californian. Always ground the country/region in the real producer's location.
- If you are not confident about a specific field (e.g. exact vintage ABV), say so with a reasonable range rather than inventing a precise figure.
- Producer names, regions, and countries are the most hallucination-prone fields — double-check these against what you know about the real producer before writing.

Write everything the way a great wine bar server would describe the wine to a guest at the
table — specific, vivid, and useful, never generic wine-speak.

Return ONLY valid JSON — no markdown, no explanation. The JSON must have exactly these fields:
{
  "identification": "State plainly which single real wine you identified and the key evidence, e.g. 'Torre Mora \\'Cauru\\' Etna Rosso DOC 2023 — a red from Nerello Mascalese. Matched on producer + appellation; \\'Cauru\\' is the cuvée name, not a grape.' This is for staff to sanity-check your pick.",
  "confidence": "high, medium, or low — how sure you are this is the exact wine. Use low if the clues are sparse or conflicting.",
  "name": "Full wine name as it should appear on the wine list",
  "vintage": "Year as a string, e.g. '2022', or 'NV' if non-vintage",
  "type": "One of: red, white, rose, orange, sparkling",
  "grape": "Grape variety or blend, e.g. '100% Cabernet Sauvignon'",
  "grape_detail": "2-3 sentences on the grape variety's character and why it matters here",
  "region": "Actual sub-region and region of this specific producer, e.g. 'Vipava Valley, Slovenia'",
  "appellation": "Official appellation/AOC/DOC/PDO/AVA if one exists, or empty string",
  "country": "Actual country of origin of this specific producer",
  "winemaker": "Producer name and a brief 1-sentence note about who they are and their philosophy",
  "body": "Style and body in one line: light/medium/full-bodied, dry/off-dry/sweet, still/sparkling. e.g. 'Full-bodied, dry, still red'",
  "aromatics": "The nose — what it smells like: fruit, floral, herbal, earthy, oak, spice. 1-2 sentences, specific.",
  "palate": "The palate — what it actually tastes like and how it echoes or differs from the nose. 1-2 sentences.",
  "structure": "The technical backbone: acidity (crisp/bright vs round), tannin (for reds — grippy/soft/smooth), and alcohol/weight. 1-2 sentences.",
  "finish": "How long flavors linger and how it leaves the mouth (clean, lingering, warming). 1 sentence.",
  "winemaking": "Notable winemaking details when relevant: oak aging, fermentation method, skin contact, organic/biodynamic. Keep it tight; empty string if nothing stands out.",
  "story": "A hook a server can use — something memorable about the producer, the region's character, or why this wine is special. 2-3 sentences that turn the description into a recommendation.",
  "alcohol": "ABV as string, e.g. '13.5%'",
  "pronunciation": "Phonetic pronunciation if the name is non-English, e.g. 'ehr-KOH-leh bar-BEHR-ah', or empty string",
  "tech_sheet_url": "Direct URL to the producer's tech sheet or winery website if known, otherwise empty string"
}

Accuracy over completeness: a blank field is better than a wrong one. Keep each field focused —
a server should be able to glance at any one line and use it immediately."""


def _build_user_message(wine_name, producer, region, varietal, vintage):
    lines = ["Identify the single real wine that best matches ALL of these clues taken together:"]
    lines.append("")
    if wine_name:
        lines.append(f"- Wine name / bottling: {wine_name}")
    if producer:
        lines.append(f"- Producer / winery: {producer}")
    if region:
        lines.append(f"- Region or appellation: {region}")
    if varietal:
        lines.append(f"- Grape / varietal (as entered by staff): {varietal}")
    if vintage:
        lines.append(f"- Vintage: {vintage}")
    lines.append("")
    lines.append(
        "How to weight these clues:\n"
        "- PRODUCER and REGION/APPELLATION are strong anchors — the wine you return "
        "MUST come from this producer and be consistent with this region/country. "
        "Do not substitute a different producer or relocate them.\n"
        "- The WINE NAME and VARIETAL fields are hints that staff may have entered "
        "imprecisely. A word placed in the varietal box is often NOT a grape — it may "
        "be the cuvée name, the bottling/proprietary name, or the appellation. If the "
        "entered 'varietal' is not a real grape, or doesn't grow in this region, treat "
        "it as the wine's name/cuvée and infer the ACTUAL grape from the real wine.\n"
        "- Reconcile everything to one specific bottling. If the clues genuinely "
        "conflict (e.g. a grape that cannot exist in that appellation), trust the "
        "producer + region, flag it in 'identification', and set confidence to low.\n"
        "Use the 'identification' and 'confidence' fields to report exactly what you "
        "landed on so staff can catch a wrong match."
    )
    return "\n".join(lines)


async def research_wine(
    wine_name: str,
    producer: str = "",
    region: str = "",
    varietal: str = "",
    vintage: str = "",
) -> dict:
    user_message = _build_user_message(wine_name, producer, region, varietal, vintage)
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude added them
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)
