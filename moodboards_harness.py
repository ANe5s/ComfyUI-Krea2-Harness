# Copyright (C) 2026 ANe5s
# SPDX-License-Identifier: GPL-3.0-or-later

"""Compatibility adapter for the GitHub-baseline Krea moodboard browser.

The baseline Visual Browser remains responsible for resolving a card and
producing its upstream outputs.  ``Moodboards Harness`` exposes the two
downstream values needed by the production workflow.  The old local
Moodboards build carried one user-owned field, ``prompt_guidance``, in its
metadata; the GitHub baseline does not.  To preserve the proven downstream
Stage 2 input, this standalone adapter deterministically recovers that field
from the baseline ``positive`` output.  It does not import, copy, or register
any Moodboards source code.
"""

from __future__ import annotations

import json
import re


HARNESS_CATEGORY = "ANe5s Nodes/Krea2"

_STYLE_GUIDANCE_LABEL_PATTERN = (
    r"palette|lighting|medium\s+and\s+texture|composition|contrast|"
    r"atmosphere|era\s+or\s+movement"
)
_STYLE_GUIDANCE_SECTION_RE = re.compile(
    rf"\b(?P<label>{_STYLE_GUIDANCE_LABEL_PATTERN})\s*:\s*"
    rf"(?P<body>.*?)(?=\s+(?:{_STYLE_GUIDANCE_LABEL_PATTERN})\s*:|$)",
    flags=re.IGNORECASE,
)
_OPTICAL_GUIDANCE_RE = re.compile(
    r"\b(?:fisheye|wide[- ]angle|forced\s+perspective|distortion|barrel|"
    r"refraction|refract|chromatic\s+aberration|double\s+exposure|"
    r"motion\s+blur|long\s+exposure|panning|halation|scanline|"
    r"lens\s+warp|optical)\b",
    flags=re.IGNORECASE,
)
_OPTICAL_TREATMENT_REPLACEMENTS = {
    "fisheye": "localized fisheye distortion on existing subject geometry",
    "wide-angle": "localized wide-angle optical treatment on existing subject geometry",
    "forced perspective": "localized perspective warp on existing subject geometry",
    "distortion": "localized distortion on existing subject geometry",
    "barrel": "localized barrel distortion on existing subject geometry",
    "refraction": "localized refraction on existing light and subject edges",
    "refract": "localized refraction on existing light and subject edges",
    "chromatic aberration": "localized chromatic aberration on existing edges",
    "double exposure": "localized double-exposure treatment on the requested subject",
    "motion blur": "localized motion blur on the requested subject",
    "long exposure": "localized long-exposure light diffusion",
    "panning": "localized panning motion blur on the requested subject",
    "halation": "localized halation around existing highlights",
    "scanline": "localized scanline treatment over the requested subject",
    "lens warp": "localized lens warp on existing subject geometry",
    "optical": "localized optical treatment on the requested subject",
}

# ``abstract_style_prose`` in the user-owned local Moodboards delta is
# intentionally lossy for one current card: it rewrites this exact phrase in
# the rendered positive.  The GitHub-baseline positive therefore cannot carry
# the original wording back by itself.  Keep the inverse correction narrowly
# scoped to the confirmed card instead of bundling the Moodboards catalog in
# this independent plugin.
_LEGACY_PROMPT_GUIDANCE_REPAIRS: dict[str, tuple[tuple[str, str], ...]] = {
    "cinematic gothic noir": (
        (
            "high-contrast silhouette treatment within expansive backgrounds",
            "isolated forms or silhouettes within expansive backgrounds",
        ),
    ),
}


def _localized_optical_treatments(body: str) -> list[str]:
    treatments: list[str] = []
    seen: set[str] = set()
    for optical_match in _OPTICAL_GUIDANCE_RE.finditer(str(body or "")):
        token = " ".join(optical_match.group(0).split()).casefold()
        treatment = _OPTICAL_TREATMENT_REPLACEMENTS.get(token)
        if treatment and treatment not in seen:
            seen.add(treatment)
            treatments.append(treatment)
    return treatments


def _extract_style_only_positive(candidate_prompt: str, *, title: str = "") -> str:
    """Mirror the local Visual Browser's style-only extraction contract.

    The title is removed before the section parser runs.  This is the small
    but important compatibility fix for titles such as ``... Atmosphere``:
    the word is part of the card title, not an ``Atmosphere:`` section.
    """

    text = str(candidate_prompt or "").strip()
    if not re.search(
        r"\bStyle-only\s+Krea\s+moodboard\s+guidance\s*:",
        text,
        flags=re.IGNORECASE,
    ):
        return text
    text = re.sub(
        r"\s+Style\s+keywords\s*:.*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    title_text = str(title or "").strip()
    if title_text:
        title_prefix = f"{title_text}:"
        title_start = text.find(title_prefix)
        if title_start >= 0:
            text = text[title_start + len(title_prefix) :].lstrip()

    sections: list[str] = []
    for match in _STYLE_GUIDANCE_SECTION_RE.finditer(text):
        label = " ".join(match.group("label").split())
        body = " ".join(match.group("body").split()).strip(" ;:.")
        if not body:
            continue
        if label.casefold() == "composition":
            optical_treatments = _localized_optical_treatments(body)
            if optical_treatments:
                sections.append("Optical treatment: " + ", ".join(optical_treatments))
            continue
        sections.append(f"{label}: {body}")
    if not sections:
        return text
    return ". ".join(sections).strip(" .") + "."


def _extract_prompt_guidance(candidate_prompt: str, *, title: str = "") -> str:
    """Recover the raw user-owned guidance from a baseline positive output.

    The baseline node already emits the official guidance in its positive
    string.  The local customized node additionally stored that same raw
    guidance in metadata as ``prompt_guidance``.  Keep this extraction narrow:
    remove only the wrapper, card title, and keyword tail, while retaining the
    guidance text itself apart from surrounding whitespace.
    """

    text = str(candidate_prompt or "")
    marker = re.search(
        r"Style-only\s+Krea\s+moodboard\s+guidance\s*:",
        text,
        flags=re.IGNORECASE,
    )
    if marker is None:
        return ""
    body = text[marker.end():].strip()
    title_text = str(title or "").strip()
    if title_text:
        title_match = re.search(
            rf"{re.escape(title_text)}\s*:\s*",
            body,
            flags=re.IGNORECASE,
        )
        if title_match is not None:
            body = body[title_match.end():].strip()
    body = re.split(
        r"\s+Style\s+keywords\s*:",
        body,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    return body


def _restore_legacy_prompt_guidance(value: str, *, title: str = "") -> str:
    """Undo only confirmed lossy rewrites from the user-owned local delta."""

    repairs = _LEGACY_PROMPT_GUIDANCE_REPAIRS.get(
        str(title or "").strip().casefold(),
        (),
    )
    restored = str(value or "")
    for rendered, original in repairs:
        restored = restored.replace(rendered, original)
    return restored


def _metadata_with_prompt_guidance(
    metadata_json: str,
    *,
    prompt_guidance: str,
) -> str:
    """Add only the missing legacy compatibility field to valid metadata."""

    raw = str(metadata_json or "")
    guidance = str(prompt_guidance or "").strip()
    if not guidance:
        return raw
    try:
        payload = json.loads(raw or "{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return raw
    if not isinstance(payload, dict):
        return raw
    existing = str(payload.get("prompt_guidance") or "").strip()
    if existing:
        return raw
    payload["prompt_guidance"] = guidance
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


class MoodboardsHarness:
    """Bridge baseline outputs to the old local Stage 2 metadata contract."""

    CATEGORY = HARNESS_CATEGORY
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = (
        "Metadata JSON",
        "Style-only Positive",
    )
    OUTPUT_TOOLTIPS = (
        "Metadata JSON restored to the legacy Krea2 Harness contract.",
        "Style-only positive extracted from the selected moodboard.",
    )
    FUNCTION = "adapt"
    DESCRIPTION = (
        "Adapt GitHub-baseline Krea Moodboard Visual Browser outputs to the legacy metadata and style-only-positive contract."
    )

    @classmethod
    def INPUT_TYPES(cls):
        def string_input(display_name: str, tooltip: str):
            return (
                "STRING",
                {
                    "forceInput": True,
                    "display_name": display_name,
                    "tooltip": tooltip,
                },
            )

        return {
            "required": {
                "positive": string_input(
                    "Positive",
                    "Positive output from the GitHub-baseline Krea Moodboard Visual Browser.",
                ),
                "title": string_input("Title", "Selected moodboard title."),
                "uuid": string_input("UUID", "Selected moodboard UUID."),
                "metadata_json": string_input(
                    "Metadata JSON",
                    "Metadata JSON output from the GitHub-baseline moodboard browser.",
                ),
            }
        }

    def adapt(
        self,
        positive: str,
        title: str,
        uuid: str,
        metadata_json: str,
    ):
        prompt_guidance = _restore_legacy_prompt_guidance(
            _extract_prompt_guidance(positive, title=title),
            title=title,
        )
        compatible_metadata_json = _metadata_with_prompt_guidance(
            metadata_json,
            prompt_guidance=prompt_guidance,
        )
        style_only_positive = _extract_style_only_positive(positive, title=title)
        return (
            compatible_metadata_json,
            style_only_positive,
        )


__all__ = ["MoodboardsHarness"]
