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

Return ONLY valid JSON — no markdown, no explanation. The JSON must have exactly these fields:
{
  "name": "Full wine name as it should appear on the wine list",
  "vintage": "Year as a string, e.g. '2022', or 'NV' if non-vintage",
  "type": "One of: red, white, rose, orange, sparkling",
  "grape": "Grape variety or blend, e.g. '100% Cabernet Sauvignon'",
  "grape_detail": "2-3 sentence description of the grape variety's character and origin",
  "region": "Actual sub-region and region of this specific producer, e.g. 'Vipava Valley, Slovenia'",
  "appellation": "Official appellation/AOC/DOC/PDO if one exists, or empty string",
  "country": "Actual country of origin of this specific producer",
  "winemaker": "Producer name and brief 1-sentence note about their actual winemaking philosophy",
  "tasting": "Tasting note: aromas and flavors in 2-3 sentences, specific and evocative",
  "alcohol": "ABV as string, e.g. '13.5%'",
  "notes": "Educational paragraph (3-5 sentences) about the wine's history, style, or what makes it special",
  "pronunciation": "Phonetic pronunciation if the name is non-English, e.g. 'ehr-KOH-leh bar-BEHR-ah', or empty string",
  "pronunciation_guide_only": false,
  "tech_sheet_url": "Direct URL to the producer's tech sheet or winery website if known, otherwise empty string"
}

Keep tasting notes vivid and specific — no generic wine-speak. Accuracy over completeness: a blank field is better than a wrong one."""


def _build_user_message(wine_name, producer, region, varietal, vintage):
    lines = [f"Research this wine: {wine_name}"]
    known = []
    if producer:
        known.append(f"- Producer / winery: {producer}")
    if region:
        known.append(f"- Region or country: {region}")
    if varietal:
        known.append(f"- Grape / varietal: {varietal}")
    if vintage:
        known.append(f"- Vintage: {vintage}")
    if known:
        lines.append("")
        lines.append(
            "The following details are CONFIRMED FACTS provided by staff. Treat them "
            "as authoritative ground truth — your output MUST be consistent with them "
            "and must NOT contradict them (especially producer, region, and country):"
        )
        lines.extend(known)
        lines.append("")
        lines.append(
            "Use these facts to identify the exact wine, then fill in the remaining "
            "fields accurately. If a confirmed fact conflicts with your assumptions, "
            "the confirmed fact wins."
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
