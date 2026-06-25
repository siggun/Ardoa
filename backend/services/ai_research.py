import json
import os
import re

import anthropic

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Server-side web tools let Claude actually look up the producer and find/verify
# the real tech sheet URL instead of recalling a plausible-looking one from
# memory (which produces dead links like "briccocarlina.it").
WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 3},
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 2, "max_content_tokens": 8000},
]

# Cache-control on the system prompt so the large instruction block is only
# billed as input tokens on the first call; subsequent calls within the cache
# window (~5 min) pay the cheaper cached rate.
SYSTEM_PROMPT = [{"type": "text", "text": """You are a wine research assistant for Ardoa Wine Bar in Charleston, SC.
Given clues about a wine, find the REAL, SPECIFIC wine being referenced and return accurate information about it.

You have web_search and web_fetch tools. USE THEM:
- Search for the producer + wine to confirm which exact bottling this is, its grape, region, and vintage details.
- Find the producer's official website, then locate the actual tech sheet / fact sheet for THIS wine (often a PDF). Open it with web_fetch to confirm it is the right wine and the link works before reporting it.
- Prefer the producer's own site or their US importer's site for the tech sheet. Do NOT invent or guess a URL — only report a tech_sheet_url you actually found and verified via search/fetch. If you cannot find a real, working tech sheet, return an empty string for tech_sheet_url. A blank link is far better than a broken or wrong one.

CRITICAL ACCURACY RULES:
- Do NOT guess or hallucinate. Ground the producer's actual country and region in what the web results show, not in a similar-sounding name.
- If you are not confident about a specific field (e.g. exact vintage ABV), give a reasonable range rather than inventing a precise figure.
- Producer names, regions, countries, and the tech sheet URL are the most error-prone fields — verify these against the web before writing them.

Write everything the way a great wine bar server would describe the wine to a guest at the
table — specific, vivid, and useful, never generic wine-speak.

When you are done researching, output ONLY the final JSON object — no markdown, no explanation, no prose around it. The JSON must have exactly these fields:
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
  "tech_sheet_url": "Direct URL to a REAL, VERIFIED tech sheet or producer page for this exact wine, or empty string if you couldn't confirm one"
}

Accuracy over completeness: a blank field is better than a wrong one. Keep each field focused —
a server should be able to glance at any one line and use it immediately.""", "cache_control": {"type": "ephemeral"}}]


def _build_user_message(wine_name, producer, region, varietal, vintage):
    lines = [
        "A bar staff member read the following off a wine bottle and typed it into "
        "a form. They may have put things in the wrong fields, misspelled names, or "
        "confused the producer with the wine name. Treat ALL of these as rough clues "
        "— not guaranteed facts — and use web search to identify the single real wine "
        "that best fits the overall picture."
    ]
    lines.append("")
    if wine_name:
        lines.append(f"- 'Wine name' field: {wine_name}")
    if producer:
        lines.append(f"- 'Producer' field: {producer}")
    if region:
        lines.append(f"- 'Region' field: {region}")
    if varietal:
        lines.append(f"- 'Varietal/grape' field: {varietal}")
    if vintage:
        lines.append(f"- 'Vintage' field: {vintage}")
    lines.append("")
    lines.append(
        "How to interpret these clues:\n"
        "- Any value could be in the wrong field. A word in 'Producer' might actually "
        "be the wine's label name, and vice versa. A word in 'Varietal' might be a "
        "cuvée name, appellation, or brand — not a grape.\n"
        "- Use the COMBINATION of all clues to triangulate the most likely wine. "
        "Search the web for the words together and see what comes up — that's often "
        "more reliable than trusting any single field.\n"
        "- The VINTAGE and COUNTRY/REGION are usually the most reliably entered "
        "fields since they're hard to confuse.\n"
        "- If you identify the wine but some clues don't fit perfectly (e.g. a word "
        "that turned out to be the label name, not the producer), explain it in "
        "'identification' so staff can verify.\n"
        "- Set confidence to 'low' if the clues are sparse or contradictory.\n"
        "Search the web to confirm the wine and find its real tech sheet URL."
    )
    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    """Pull the JSON object out of the model's final text, tolerating prose or
    code fences around it."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost {...} span in the text.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start:end + 1])
    raise ValueError("No JSON object found in research response")


def _shorten_url(url: str, limit: int = 60) -> str:
    url = re.sub(r"^https?://(www\.)?", "", url)
    return url if len(url) <= limit else url[: limit - 1] + "…"


async def research_wine_stream(
    wine_name: str,
    producer: str = "",
    region: str = "",
    varietal: str = "",
    vintage: str = "",
):
    """Async generator yielding progress events while Claude researches the wine.

    Yields dicts of {"type": "status", "message": ...} as the model searches and
    reads pages, then a final {"type": "result", "data": {...}} with the parsed
    wine fields.
    """
    user_message = _build_user_message(wine_name, producer, region, varietal, vintage)
    messages = [{"role": "user", "content": user_message}]

    final_message = None
    for _ in range(6):
        # Track partial tool-input JSON per content block so we can surface the
        # actual search query / fetched URL once the block finishes.
        partial = {}
        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=WEB_TOOLS,
            messages=messages,
        ) as stream:
            async for event in stream:
                etype = getattr(event, "type", None)
                if etype == "content_block_start":
                    block = event.content_block
                    btype = getattr(block, "type", None)
                    if btype == "server_tool_use":
                        partial[event.index] = {"name": getattr(block, "name", ""), "json": ""}
                        if block.name == "web_search":
                            yield {"type": "status", "message": "🔍 Searching the web…"}
                        elif block.name == "web_fetch":
                            yield {"type": "status", "message": "📄 Reading a page…"}
                    elif btype == "text":
                        yield {"type": "status", "message": "✍️ Writing up the tasting notes…"}
                elif etype == "content_block_delta":
                    delta = event.delta
                    if getattr(delta, "type", None) == "input_json_delta" and event.index in partial:
                        partial[event.index]["json"] += delta.partial_json
                elif etype == "content_block_stop":
                    p = partial.pop(event.index, None)
                    if p:
                        try:
                            inp = json.loads(p["json"] or "{}")
                        except json.JSONDecodeError:
                            inp = {}
                        if p["name"] == "web_search" and inp.get("query"):
                            yield {"type": "status", "message": "🔍 Searched: " + inp["query"]}
                        elif p["name"] == "web_fetch" and inp.get("url"):
                            yield {"type": "status", "message": "📄 Read: " + _shorten_url(inp["url"])}
            final_message = await stream.get_final_message()

        if final_message.stop_reason == "pause_turn":
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": final_message.content},
            ]
            continue
        break

    text = "".join(
        block.text for block in final_message.content if getattr(block, "type", None) == "text"
    )
    yield {"type": "result", "data": _extract_json(text)}
