# Copyright (C) 2026 ANe5s
# SPDX-License-Identifier: GPL-3.0-or-later

"""Krea 2 Turbo resolution selector.

This node deliberately does not reuse ComfyUI's generic megapixel resolver.
It uses the supplied Krea 2 Turbo 1K buckets as the verification table,
scales the mathematical aspect-ratio family, rounds to the 32px Krea
resolution bucket grid, and caps the long edge at the official 2048px Turbo
ceiling.
"""

from __future__ import annotations


KREA2_TURBO_ASPECT_RATIOS = (
    "1:1",
    "4:3",
    "3:2",
    "16:9",
    "2.35:1",
    "4:5",
    "2:3",
    "9:16",
)

# Keep these 1K anchors exactly aligned with the Krea 2 Turbo table supplied
# by the user. All official table dimensions are 32px multiples. In
# particular, 1K (4:3) is 1184x896, not the generic ComfyUI 1184x880 result
# produced by its 16px independent-axis rounding.
KREA2_TURBO_1K_ANCHORS = {
    "1:1": (1024, 1024),
    "4:3": (1184, 896),
    "3:2": (1248, 832),
    "16:9": (1376, 768),
    "2.35:1": (1568, 672),
    "4:5": (928, 1152),
    "2:3": (832, 1248),
    "9:16": (768, 1376),
}

KREA2_TURBO_ASPECT_VALUES = {
    "1:1": (1.0, 1.0),
    "4:3": (4.0, 3.0),
    "3:2": (3.0, 2.0),
    "16:9": (16.0, 9.0),
    "2.35:1": (2.35, 1.0),
    "4:5": (4.0, 5.0),
    "2:3": (2.0, 3.0),
    "9:16": (9.0, 16.0),
}

KREA2_TURBO_MAX_EDGE = 2048
KREA2_TURBO_GRID = 32
KREA2_TURBO_MIN_MEGAPIXELS = 1.0
KREA2_TURBO_MAX_MEGAPIXELS = 4.0
KREA2_TURBO_MEGAPIXEL_STEP = 0.1


def _nearest_grid(value: float, grid: int = KREA2_TURBO_GRID) -> int:
    """Round a positive dimension to the nearest Krea bucket-grid multiple."""

    return max(grid, int(value / grid + 0.5) * grid)


def get_krea2_turbo_resolution(
    aspect_ratio: str,
    megapixels: float = KREA2_TURBO_MIN_MEGAPIXELS,
) -> tuple[int, int]:
    """Map a target MP value onto the Krea 2 Turbo resolution family.

    At 1.0 MP the result is checked against and returned as the exact supplied
    1K anchor. Above 1.0 MP the mathematical aspect ratio is scaled by target
    area, then both dimensions are rounded to the 32px Krea bucket grid. The
    scale is capped before rounding so no dimension can exceed the 2048px
    Turbo limit.
    """

    key = str(aspect_ratio)
    if key not in KREA2_TURBO_1K_ANCHORS:
        raise ValueError(f"Unsupported Krea 2 Turbo aspect ratio: {aspect_ratio!r}")

    target_mp = float(megapixels)
    if not (
        KREA2_TURBO_MIN_MEGAPIXELS
        <= target_mp
        <= KREA2_TURBO_MAX_MEGAPIXELS
    ):
        raise ValueError(
            "Krea 2 Turbo megapixels must be between "
            f"{KREA2_TURBO_MIN_MEGAPIXELS} and "
            f"{KREA2_TURBO_MAX_MEGAPIXELS}"
        )

    base_width, base_height = KREA2_TURBO_1K_ANCHORS[key]
    if abs(target_mp - KREA2_TURBO_MIN_MEGAPIXELS) < 1e-9:
        return base_width, base_height

    ratio_width, ratio_height = KREA2_TURBO_ASPECT_VALUES[key]
    target_pixels = target_mp * 1024 * 1024
    scale = (target_pixels / (ratio_width * ratio_height)) ** 0.5
    scale = min(
        scale,
        KREA2_TURBO_MAX_EDGE / max(ratio_width, ratio_height),
    )

    width = min(
        KREA2_TURBO_MAX_EDGE,
        _nearest_grid(ratio_width * scale),
    )
    height = min(
        KREA2_TURBO_MAX_EDGE,
        _nearest_grid(ratio_height * scale),
    )
    return width, height


class Krea2TurboResolutionSelector:
    """Select an MP-adjustable Krea 2 Turbo resolution."""

    CATEGORY = "ANe5s节点/Krea2"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("Width", "Height")
    FUNCTION = "select"
    DESCRIPTION = (
        "Map a target megapixel value onto a Krea 2 Turbo aspect-ratio family. "
        "The supplied 1K buckets are preserved, output is aligned to the 32px "
        "Krea bucket grid, and no dimension can exceed 2048 pixels. "
        "The selected resolution is shown in the node preview."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (
                    list(KREA2_TURBO_ASPECT_RATIOS),
                    {
                        "default": "1:1",
                        "tooltip": "Krea 2 Turbo fixed aspect-ratio bucket.",
                    },
                ),
                "megapixels": (
                    "FLOAT",
                    {
                        "default": KREA2_TURBO_MIN_MEGAPIXELS,
                        "min": KREA2_TURBO_MIN_MEGAPIXELS,
                        "max": KREA2_TURBO_MAX_MEGAPIXELS,
                        "step": KREA2_TURBO_MEGAPIXEL_STEP,
                        "tooltip": (
                            "Target Krea MP. 1.0 returns the supplied 1K anchor; "
                            "higher values scale toward the 2048px ceiling using the "
                            "32px Krea bucket grid."
                        ),
                    },
                ),
            }
        }

    def select(self, aspect_ratio: str, megapixels: float):
        width, height = get_krea2_turbo_resolution(
            aspect_ratio,
            megapixels,
        )
        return width, height


__all__ = [
    "KREA2_TURBO_ASPECT_RATIOS",
    "KREA2_TURBO_1K_ANCHORS",
    "KREA2_TURBO_ASPECT_VALUES",
    "KREA2_TURBO_GRID",
    "KREA2_TURBO_MAX_EDGE",
    "KREA2_TURBO_MAX_MEGAPIXELS",
    "KREA2_TURBO_MIN_MEGAPIXELS",
    "Krea2TurboResolutionSelector",
    "get_krea2_turbo_resolution",
]
