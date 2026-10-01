#!/usr/bin/env python3
"""Create / update the CI's plain-language writer agent on Vectara (idempotent).

    python3 .github/tapeout/setup_plain_writer.py

rsp_ci_plain_writer turns the tape-out gate's structured report into short, plain-English review comments
for software developers and non-engineers. It has no tools and reads only the JSON it is given; strict
structured output, so the CI runner can place each explanation on the right line. It never decides anything:
verdicts, money, owners and quotes are copied from the gate report by the runner, not by this agent.
The API key comes from the environment (VECTARA_API_KEY / VECTARA_API_KEY_STAGING) and is never printed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vectara_api as v  # noqa: E402

KEY = "rsp_ci_plain_writer"
SCHEMA_NAME = "rsp_ci_plain_comments"

INSTRUCTIONS = """You write the plain-English text of an automated code-review bot for a computer chip's tape-out paperwork (the documents a chip team must get signed off before a factory makes the chip).

Your readers are software developers and non-technical judges. They know pull requests, CI checks and code review. They know nothing about chips.

You receive one JSON gate report from the AI review board. For every finding in it, write:
- plain_title: at most 7 words, no codes, no part names (for example "Boot flash chip gets the wrong voltage").
- what_is_wrong: one or two short sentences saying what the documents disagree about, in everyday words. Keep the key concrete numbers if they help (for example 1.8 volts vs 1.2 volts, 91% vs 95%).
- why_it_blocks: one sentence on what would go wrong in the real chip if this reached the factory (for example "Chips could fail to start up").
- analogy: one short everyday comparison that is technically fair, or null if none fits.
- caused_by_change: if the report says this problem was introduced by a recent fix or change, one short plain phrase naming that change (for example "the timing fix to the security block (ECO-B-003)"); otherwise null.
- fix_here_evidence_index: the 0-based index into that finding's evidence list of the quote that shows the line someone must actually change (the wrong value, the failing number, the missing sign-off), not the requirement it violates.
For every item in closed_since_previous write plain_title and how_fixed (one plain sentence).
Also write headline: one sentence of at most 20 words for the whole verdict.

Rules:
- Use only facts in the JSON. Never invent numbers, names, causes or consequences. If unsure, say less.
- No jargon in plain_title, what_is_wrong or why_it_blocks. If one technical word is unavoidable, explain it in a few words right after it.
- Do not mention money or schedule; the bot adds those from the report itself.
- Copy each id exactly as given.
- The AI review board recommends; people decide. Never say the AI decided or blocked anything by itself."""


def _s(desc: str | None = None) -> dict:
    return {"type": "string", **({"description": desc} if desc else {})}


def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def _null(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


def schema() -> dict:
    finding = _obj({
        "id": _s(), "plain_title": _s(), "what_is_wrong": _s(), "why_it_blocks": _s(),
        "analogy": _null({"type": "string"}), "caused_by_change": _null({"type": "string"}),
        "fix_here_evidence_index": {"type": "integer"},
    })
    closed = _obj({"id": _s(), "plain_title": _s(), "how_fixed": _s()})
    return _obj({"headline": _s(), "findings": {"type": "array", "items": finding},
                 "closed": {"type": "array", "items": closed}})


def body() -> dict:
    return {
        "key": KEY,
        "name": KEY,
        "description": "Tape-out CI bot: rewrites the gate report's findings as plain-English review comments "
                       "(no tools; reads only the JSON it is given).",
        "model": {"name": "gpt-5.5"},
        "tool_configurations": {},
        "first_step_name": "write",
        "steps": {"write": {
            "instructions": [{"type": "inline", "name": "plain_writer", "template_type": "text",
                              "template": INSTRUCTIONS}],
            "output_parser": {"type": "structured", "json_schema": {"name": SCHEMA_NAME, "strict": True,
                                                                     "schema": schema()}},
            "allowed_tools": [],
        }},
        "metadata": {"project": "rsp_respin_agent", "role": "ci_plain_writer"},
    }


if __name__ == "__main__":
    c = v.Client()
    res = c.upsert_agent(body())
    print(f"agent {res.get('key', KEY)} ready")
