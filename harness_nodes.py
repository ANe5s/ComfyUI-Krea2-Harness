# Copyright (C) 2026 ANe5s
# SPDX-License-Identifier: GPL-3.0-or-later

"""Public, standalone Krea2 Harness sanitizer nodes.

The exact user-owned sanitizer core lives inside this plugin.  This module
only exposes the two fixed Krea2 Harness production boundaries and deliberately
does not import, move, or register any Moodboards node.
"""

from __future__ import annotations

import json
import re

from .krea_harness_local_core import KreaPromptSanitizer


HARNESS_CATEGORY = "ANe5s Nodes/Krea2"
HARNESS_NAME = "Krea2 Harness"
HARNESS_RELEASE = "V0.1Alpha"
HARNESS_STAGE1 = "V0.1.257"
HARNESS_STAGE2 = "V0.1.124"
HARNESS_STAGE2_IMPLEMENTATION = "V124-RB"


_STYLE_ONLY_LABEL_PATTERN = (
    r"palette|lighting|medium\s+and\s+texture|composition|contrast|"
    r"atmosphere|era\s+or\s+movement|optical\s+treatment"
)
_STYLE_ONLY_SECTION_RE = re.compile(
    rf"(?:^|[.!?]\s+|\n+)"
    rf"(?P<label>{_STYLE_ONLY_LABEL_PATTERN})\s*:\s*"
    rf"(?P<body>.*?)"
    rf"(?=(?:[.!?]\s+|\n+)(?:{_STYLE_ONLY_LABEL_PATTERN})\s*:|$)",
    flags=re.IGNORECASE,
)
_STYLE_ONLY_FIRST_LABEL_RE = re.compile(
    rf"\b(?P<label>{_STYLE_ONLY_LABEL_PATTERN})\s*:",
    flags=re.IGNORECASE,
)
_STYLE_ONLY_CANONICAL_LABELS = {
    "palette": "Palette",
    "lighting": "Lighting",
    "medium and texture": "Medium and texture",
    "composition": "Composition",
    "contrast": "Contrast",
    "atmosphere": "Atmosphere",
    "era or movement": "Era or movement",
    "optical treatment": "Optical treatment",
}
_STYLE_ONLY_PARENTHESES_LABELS = frozenset(
    {"lighting", "atmosphere", "era or movement", "contrast"}
)
_STYLE_ONLY_INNER_LIGHTING_COLON_RE = re.compile(
    r"(?P<phrase>\b(?:No\s+(?:naturalistic|optical)\s+lighting|"
    r"Contrast\s+functions\s+as\s+lighting))\s*:\s*",
    flags=re.IGNORECASE,
)
_STYLE_ONLY_SPLIT_LIGHTING_RE = re.compile(
    r"(?P<header>\bLighting\s*:\s*)"
    r"(?P<phrase>No\s+(?:naturalistic|optical)|Contrast\s+functions\s+as)"
    r"\s*\.\s*lighting\s*:\s*",
    flags=re.IGNORECASE,
)


def _style_profile_prompt_guidance(style_profile: str) -> str:
    """Read raw prompt_guidance without treating compiled channels as prose."""

    try:
        payload = json.loads(str(style_profile or "{}"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return ""
    if not isinstance(payload, dict):
        return ""
    candidates = [payload.get("prompt_guidance")]
    qwen_guidance = payload.get("qwen_guidance")
    if isinstance(qwen_guidance, dict):
        candidates.append(qwen_guidance.get("prompt_guidance"))
    nested_profile = payload.get("style_profile")
    if isinstance(nested_profile, dict):
        candidates.append(nested_profile.get("prompt_guidance"))
    for candidate in candidates:
        text = str(candidate or "").strip()
        if text:
            return text
    return ""


def _metadata_json_for_legacy_sanitizer(metadata_json: str) -> str:
    """Keep the legacy sanitizer value byte-for-byte stable during renaming.

    The existing production workflows already pass the Visual Browser /
    Moodboards Harness metadata value through the old ``style_profile``
    socket.  This interface migration must not silently introduce a new
    style-channel compilation step, because that would change the final
    prompt.  The metadata-to-style-profile adapter remains an upstream
    workflow concern; this node preserves the exact legacy value here.
    """

    return str(metadata_json or "").strip()


def _repair_style_only_lighting_colons(value: str) -> str:
    """Repair only the known inner Lighting pseudo-header delimiters.

    The first substitution handles the raw official guidance.  The second
    handles the equivalent malformed text already emitted by the legacy
    upstream extractor, e.g. ``Lighting: No naturalistic. lighting: ...``.
    The real section delimiter ``Lighting:`` is never changed.
    """

    text = str(value or "")
    text = _STYLE_ONLY_INNER_LIGHTING_COLON_RE.sub(
        lambda match: f"{match.group('phrase')}, ",
        text,
    )
    return _STYLE_ONLY_SPLIT_LIGHTING_RE.sub(
        lambda match: (
            f"{match.group('header')}{match.group('phrase')} lighting, "
        ),
        text,
    )


def _style_only_source(value: str) -> str:
    """Trim the non-style tail and repair delimiters before section parsing."""

    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(
        r"\s+Style\s+keywords\s*:.*$",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()
    return _repair_style_only_lighting_colons(text)


def _parse_style_only_sections(value: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Parse style sections only at real sentence/newline boundaries."""

    text = _style_only_source(value)
    if not text:
        return "", []
    first_label = _STYLE_ONLY_FIRST_LABEL_RE.search(text)
    if first_label is None:
        return text, []

    scoped = text[first_label.start():]
    sections: list[tuple[str, str, str]] = []
    for match in _STYLE_ONLY_SECTION_RE.finditer(scoped):
        key = " ".join(match.group("label").split()).casefold()
        label = _STYLE_ONLY_CANONICAL_LABELS.get(key)
        body = re.sub(r"\s+", " ", match.group("body")).strip()
        body = body.rstrip(".!?\u3002\uff01\uff1f").rstrip()
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1].strip()
        if label and body:
            sections.append((key, label, body))
    return text, sections


def _raw_lighting_body(style_profile: str) -> str:
    """Return the repaired raw Lighting body when metadata provides it."""

    raw_guidance = _style_profile_prompt_guidance(style_profile)
    if not raw_guidance:
        return ""
    repaired = _repair_style_only_lighting_colons(raw_guidance)
    _, sections = _parse_style_only_sections(repaired)
    for key, _label, body in sections:
        if key == "lighting":
            return body
    return ""


def _format_style_only_positive(value: str, style_profile: str = "") -> str:
    """Normalize appended moodboard sections to Label: (description)."""

    text, parsed_sections = _parse_style_only_sections(value)
    if not parsed_sections:
        return text
    authoritative_lighting = _raw_lighting_body(style_profile)
    has_authoritative_lighting = bool(
        authoritative_lighting
        and _STYLE_ONLY_INNER_LIGHTING_COLON_RE.search(
            _style_profile_prompt_guidance(style_profile)
        )
    )
    sections: list[str] = []
    lighting_rendered = False
    for key, label, body in parsed_sections:
        if key == "lighting" and has_authoritative_lighting:
            if lighting_rendered:
                continue
            body = authoritative_lighting
            lighting_rendered = True
        rendered_body = (
            f"({body})" if key in _STYLE_ONLY_PARENTHESES_LABELS else body
        )
        sections.append(f"{label}: {rendered_body}.")
    return " ".join(sections) if sections else text


class KreaHarnessPrompt:
    """Stage 1 V257 Prompt Sanitizer with focus/profile guards off."""

    CATEGORY = HARNESS_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Clean Prompt",)
    OUTPUT_TOOLTIPS = ("Sanitized Stage 1 prompt.",)
    FUNCTION = "clean"
    DESCRIPTION = (
        "Clean the Stage 1 V257 generated prompt with focus and profile guards fixed off."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "forceInput": True,
                        "display_name": "Prompt",
                        "tooltip": "Stage 1 V257 generated prompt.",
                    },
                ),
                "original_main_prompt": (
                    "STRING",
                    {
                        "forceInput": True,
                        "display_name": "Original Main Prompt",
                        "tooltip": "Original main prompt used for both fallback and source-ledger roles.",
                    },
                ),
            },
        }

    def clean(
        self,
        prompt: str,
        original_main_prompt: str,
    ):
        original = str(original_main_prompt or "")
        return KreaPromptSanitizer().clean(
            prompt=prompt,
            fallback_prompt=original,
            source_prompt=original,
            style_profile="",
            style_contract_only=False,
            subject_side_authority="",
            guard_entities=True,
            allow_subordinate_environment_entities=False,
            allow_contextual_environment_medium=True,
            allow_subordinate_background_people=False,
            strip_internal_sampling_marker=False,
            strip_prompt_labels=True,
            strip_unrequested_capture_formats=True,
            preserve_subject_count=False,
            preserve_source_optical_anchors=True,
            guard_unrequested_focus_blur=False,
            preserve_profile_facial_detail=False,
            block_rectangular_eye_catchlights=False,
            strip_unrequested_hand_actions=True,
        )


class KreaHarnessMoodboard:
    """Final V124-RB Prompt Sanitizer under the requested public node name."""

    CATEGORY = HARNESS_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Clean Prompt",)
    OUTPUT_TOOLTIPS = ("Sanitized final Stage 2 prompt.",)
    FUNCTION = "clean"
    DESCRIPTION = (
        "Clean the final Stage 2 V124-RB prompt and optionally append the style-only moodboard positive."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "forceInput": True,
                        "display_name": "Prompt",
                        "tooltip": "Stage 2 V124-RB generated prompt.",
                    },
                ),
            },
            "optional": {
                "fallback_prompt": (
                    "STRING",
                    {
                        "forceInput": True,
                        "display_name": "Fallback Prompt",
                        "tooltip": "Fallback prompt used when Stage 2 returns a protocol or refusal transcript.",
                    },
                ),
                "original_main_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "forceInput": True,
                        "display_name": "Original Main Prompt",
                        "tooltip": "Original main prompt used by the focus and profile guards.",
                    },
                ),
                "metadata_json": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "forceInput": True,
                        "display_name": "Metadata JSON",
                        "tooltip": "Moodboard metadata passed through with the legacy style-profile semantics.",
                    },
                ),
                "style_only_positive": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "forceInput": True,
                        "display_name": "Style-only Positive",
                        "tooltip": "Optional style-only moodboard positive appended after final prompt sanitization.",
                    },
                ),
            },
        }

    def clean(
        self,
        prompt: str,
        fallback_prompt: str = "",
        original_main_prompt: str = "",
        metadata_json: str = "",
        style_only_positive: str = "",
    ):
        raw_metadata_json = _metadata_json_for_legacy_sanitizer(metadata_json)
        style_profile = raw_metadata_json
        sanitized = KreaPromptSanitizer().clean(
            prompt=prompt,
            fallback_prompt=fallback_prompt,
            source_prompt=original_main_prompt,
            style_profile=style_profile,
            style_contract_only=False,
            subject_side_authority="",
            guard_entities=True,
            allow_subordinate_environment_entities=False,
            allow_contextual_environment_medium=True,
            allow_subordinate_background_people=False,
            strip_internal_sampling_marker=False,
            strip_prompt_labels=True,
            strip_unrequested_capture_formats=True,
            preserve_subject_count=True,
            preserve_source_optical_anchors=True,
            guard_unrequested_focus_blur=True,
            preserve_profile_facial_detail=True,
            block_rectangular_eye_catchlights=False,
            strip_unrequested_hand_actions=True,
        )
        if not str(style_only_positive or "").strip():
            return sanitized
        formatted_style = _format_style_only_positive(
            style_only_positive,
            style_profile=raw_metadata_json,
        )
        return (sanitized[0] + "\n\n" + formatted_style,)
