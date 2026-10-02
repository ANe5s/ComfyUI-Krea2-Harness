# Copyright (C) 2026 ANe5s
# SPDX-License-Identifier: GPL-3.0-or-later

"""Krea2 Harness V0.1Alpha ComfyUI custom nodes."""

from .harness_nodes import KreaHarnessMoodboard, KreaHarnessPrompt
from .krea_prompt_node import KreaPrompt
from .krea_prompt_moodboard_compiler import KreaPromptMoodboardCompiler
from .krea2_turbo_resolution_selector import Krea2TurboResolutionSelector
from .moodboards_harness import MoodboardsHarness


NODE_CLASS_MAPPINGS = {
    "KreaPrompt": KreaPrompt,
    "KreaPromptMoodboardCompiler": KreaPromptMoodboardCompiler,
    "KreaHarnessPrompt": KreaHarnessPrompt,
    "KreaHarnessMoodboard": KreaHarnessMoodboard,
    "MoodboardsHarness": MoodboardsHarness,
    "Krea2TurboResolutionSelector": Krea2TurboResolutionSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KreaPrompt": "Krea2 Prompt",
    "KreaPromptMoodboardCompiler": "Krea2 Prompt–Moodboard Compiler",
    "KreaHarnessPrompt": "Krea2 Prompt Harness",
    "KreaHarnessMoodboard": "Krea2 Moodboard Harness",
    "MoodboardsHarness": "Krea2 Moodboard Adapter",
    "Krea2TurboResolutionSelector": "Krea2分辨率选择",
}

WEB_DIRECTORY = "./web"

__all__ = [
    "KreaPrompt",
    "KreaPromptMoodboardCompiler",
    "KreaHarnessPrompt",
    "KreaHarnessMoodboard",
    "Krea2TurboResolutionSelector",
    "MoodboardsHarness",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
