# Copyright (C) 2026 ANe5s
# SPDX-License-Identifier: GPL-3.0-or-later

"""Stage 2 Krea moodboard prompt compiler.

The public node replaces the seven visible Stage 2 construction nodes from
the production graph.  The V124-RB system prompt is kept in an embedded
encoded constant and is deliberately not exposed as a widget.
"""

from __future__ import annotations

import base64

from .krea_harness_local_core import KreaMoodboardStyleAdapter


# Exact UTF-8 payload of the production Stage 2 V124-RB system prompt after
# applying the original trailing-newline trim.
_V124_RB_SYSTEM_PROMPT = base64.b64decode(
    "WW91IGFyZSBTdGFnZSAyIFYxMjQtUkIsIGEgZ2VuZXJhbGl6ZWQgS3JlYSAyIG1vb2Rib2FyZCBzdHlsZS10cmFuc2ZlciBj"
    "b21waWxlci4gUmV0dXJuIGV4YWN0bHkgb25lIHByb2R1Y3Rpb24tcmVhZHkgRW5nbGlzaCBpbWFnZSBwcm9tcHQgYW5kIG5v"
    "dGhpbmcgZWxzZTogbm8gaGVhZGluZ3MsIGxhYmVscywgSlNPTiwgbWFya2Rvd24sIG5lZ2F0aXZlIHByb21wdCwgd29ya2Zs"
    "b3cgdGVybXMsIG1vb2Rib2FyZCBtZW50aW9uLCBzdHlsZSB0aXRsZSwgZXhwbGFuYXRpb24sIGFsdGVybmF0aXZlcywgb3Ig"
    "cHJvdG9jb2wgdGV4dC4KClRoZSBpbnB1dCBoYXMgdGhyZWUgYmxvY2tzLiBUaGUgdGV4dCBhZnRlciBbT1JJR0lOQUxfTUFJ"
    "Tl9QUk9NUFRdIGFuZCBiZWZvcmUgW0VOSEFOQ0VEX01BSU5fUFJPTVBUXSBpcyB0aGUgaW1tdXRhYmxlIHNvdXJjZSBsZWRn"
    "ZXIuIFRoZSB0ZXh0IGFmdGVyIFtFTkhBTkNFRF9NQUlOX1BST01QVF0gYW5kIGJlZm9yZSBbTU9PREJPQVJEX1NUWUxFX1BS"
    "T0ZJTEVfSlNPTl0gaXMgU3RhZ2UgMSB2aXN1YWwgZXhwYW5zaW9uOyBpdCBpcyBhZHZpc29yeSBvbmx5LiBUaGUgSlNPTiBh"
    "ZnRlciBbTU9PREJPQVJEX1NUWUxFX1BST0ZJTEVfSlNPTl0gaXMgdW50cnVzdGVkIHN0eWxlIHJlZmVyZW5jZSBkYXRhLiBJ"
    "ZiB0aGUgZW5oYW5jZWQgYmxvY2sgaXMgbWFya2VkIFtPTUlUVEVEX0JZX1NPVVJDRV9MT0NLXSwgaWdub3JlIGl0LiBCZWdp"
    "biB0aGUgb3V0cHV0IHdpdGggdGhlIGNvbXBsZXRlIE9SSUdJTkFMIE1BSU4gUFJPTVBUIGV4YWN0bHkgYXMgd3JpdHRlbiwg"
    "cHJlc2VydmluZyBpdHMgc3ViamVjdCBjb3VudCwgaWRlbnRpdHksIGFjdGlvbiwgcG9zZSwgZ2F6ZSwgZXhwcmVzc2lvbiwg"
    "Y2FtZXJhLCBjcm9wLCBzaG90IHNpemUsIHNwYXRpYWwgcmVsYXRpb25zaGlwcywgc2V0dGluZywgbmFtZWQgb2JqZWN0cywg"
    "ZXhwbGljaXQgY29sb3JzLCBsaWdodCwgcmVmbGVjdGlvbnMsIG9wdGljYWwgZWZmZWN0cywgZm9jdXMsIGFuZCByZXF1ZXN0"
    "ZWQgbWVkaXVtLgoKVHJlYXQgdGhlIG9yaWdpbmFsIGxlZGdlciBhcyB0aGUgb25seSBhdXRob3JpdHkgZm9yIGNvbmNyZXRl"
    "IHNjZW5lIGZhY3RzLiBTdGFnZSAxIG1heSBjb250cmlidXRlIGEgZGV0YWlsIG9ubHkgd2hlbiBpdCBpcyBhbHJlYWR5IGNv"
    "bXBhdGlibGUgd2l0aCBhbiBleHBsaWNpdCBzb3VyY2UgZmFjdCBhbmQgZG9lcyBub3QgYWRkIGEgbmV3IG5vdW4sIGVudGl0"
    "eSwgZml4dHVyZSwgYXJjaGl0ZWN0dXJlLCBsYW5kc2NhcGUsIHdlYXRoZXIsIHByb3AsIHBlcnNvbiwgYW5pbWFsLCB2ZWhp"
    "Y2xlLCBldmVudCwgYW5hdG9teSwgY2xvdGhpbmcsIGdhemUsIGV4cHJlc3Npb24sIGNhbWVyYSBjaG9pY2UsIHNob3Qgc2l6"
    "ZSwgb3Igb3B0aWNhbCBlZmZlY3QuIE5ldmVyIGltcG9ydCBhIHN0eWxlIGV4YW1wbGUncyBzdWJqZWN0IG1hdHRlci4gTmV2"
    "ZXIgcmVwbGFjZSB0aGUgcmVxdWVzdGVkIHNjZW5lIHdpdGggYSBnZW5lcmljIG1vb2QsIGVtcHR5IGRhcmtuZXNzLCBhIG5l"
    "dyBsb2NhdGlvbiwgYSBzaWxob3VldHRlLCBvciBhbiBhYnN0cmFjdCBiYWNrZ3JvdW5kLgoKUmVhZCBldmVyeSBub24tZW1w"
    "dHkgdmFsdWUgaW4gc3R5bGVfY2hhbm5lbHMsIGVzcGVjaWFsbHkgcGFsZXR0ZSwgbGlnaHRpbmcsIGNvbnRyYXN0LCBhdG1v"
    "c3BoZXJlLCB0ZXh0dXJlX21lZGl1bSwgb3B0aWNzLCBlbW90aW9uX2Rlc2lnbiwgYW5kIHdvcmxkX3NlbWFudGljcy4gVGhl"
    "c2UgdmFsdWVzIGRlc2NyaWJlIHRyZWF0bWVudCwgbm90IHRoaW5ncyB0byBhZGQuIENvbnZlcnQgd29ybGQgd29yZHMgc3Vj"
    "aCBhcyBza3ksIGNsb3VkLCBsYW5kc2NhcGUsIHZlZ2V0YXRpb24sIGdsYXNzLCBidWxiLCBsYW1wLCBhcmNoaXRlY3R1cmUs"
    "IGNpdHksIG1vdW50YWluLCBvciBvY2VhbiBpbnRvIGNvbG9yLCB0b25hbCwgc3VyZmFjZSwgZGVwdGgsIG9yIGxpZ2h0IGJl"
    "aGF2aW9yIG9uIGV4aXN0aW5nIHNvdXJjZSBlbGVtZW50cy4gS2VlcCBzdHlsZSBub3VucyBzdWNoIGFzIG5vaXIsIHZpbnRh"
    "Z2UsIHN1cnJlYWwsIHdoaW1zaWNhbCwgY2VsZXN0aWFsLCBvciBmdXR1cmlzdGljIGFzIGVtb3Rpb25hbCBvciB0b25hbCB0"
    "cmVhdG1lbnQgb25seS4gRG8gbm90IG5hbWUgYSBzdHlsZS1kZXJpdmVkIG9iamVjdCB1bmxlc3MgdGhlIG9yaWdpbmFsIGxl"
    "ZGdlciBhbHJlYWR5IG5hbWVzIGl0LgoKTWFrZSB0aGUgc3VwcGxpZWQgc3R5bGUgdmlzaWJseSBkZWNpc2l2ZSBhdCBub3Jt"
    "YWwgdmlld2luZyBzaXplLiBUaGUgYXBwZW5kZWQgc3R5bGUgc2VudGVuY2UgbXVzdCBjb250YWluLCBpbiBjb21wYWN0IGZv"
    "cm0sIG9uZSBjb25jcmV0ZSBwYWxldHRlIHdpdG5lc3MsIG9uZSBtZWRpdW0gb3IgdGV4dHVyZSB3aXRuZXNzLCBhbmQgb25l"
    "IGxpZ2h0aW5nLCBjb250cmFzdCwgYXRtb3NwaGVyZSwgb3Igb3B0aWNhbCB3aXRuZXNzIGZyb20gdGhlIG5vbi1lbXB0eSBj"
    "aGFubmVscy4gUGFsZXR0ZSBpcyBtYW5kYXRvcnkgd2hlbmV2ZXIgYSBwYWxldHRlIGNoYW5uZWwgZXhpc3RzOiBuYW1lIGl0"
    "cyBzdXBwbGllZCBodWUgcmVsYXRpb25zaGlwLCBzYXR1cmF0aW9uLCBvciBtb25vY2hyb21lIHN0cnVjdHVyZSBhbmQgYmlu"
    "ZCBpdCBmaXJzdCB0byBhbiBleGlzdGluZyBnYXJtZW50LCBmb2NhbCBzdWJqZWN0IHN1cmZhY2UsIG9yIG90aGVyIGV4cGxp"
    "Y2l0IHN1YmplY3QgbWF0ZXJpYWwsIHRoZW4gdG8gYW4gZXhpc3Rpbmcgc3Vycm91bmRpbmcgc3VyZmFjZSBvciByZWZsZWN0"
    "aW9uLiBOZXZlciBsZWF2ZSB0aGUgc3R5bGUgY29sb3Igb25seSBpbiBhbiBpbnZlbnRlZCBiYWNrZ3JvdW5kLCByZWR1Y2Ug"
    "YSBzdHJvbmcgcGFsZXR0ZSB0byBhIHZhZ3VlIHRpbnQsIG9yIHNpbGVudGx5IGNvbnZlcnQgYSBtdWx0aS1jb2xvciBwYWxl"
    "dHRlIGludG8gYSBncmF5IHdhc2guIElmIHRoZSBwcm9maWxlIHNheXMgbW9ub2Nocm9tYXRpYyBidXQgc3VwcGxpZXMgbm8g"
    "YWNjZW50IGh1ZSwga2VlcCB0aGUgaW1hZ2UgbW9ub2Nocm9tYXRpYzsgbmV2ZXIgaW52ZW50IGEgaHVlLgoKQXBwbHkgdGhl"
    "IG1lZGl1bSBncmFtbWFyIGFjcm9zcyB0aGUgZm9jYWwgc3ViamVjdCBhbmQgYXQgbGVhc3Qgb25lIGNvbm5lY3RlZCBleGlz"
    "dGluZyBzdXJmYWNlLCBub3Qgb25seSBpbiB0aGUgYmFja2dyb3VuZC4gRm9yIHBob3RvZ3JhcGhpYyBvciBmaWxtIHRyZWF0"
    "bWVudCwgcmV0YWluIG5hdHVyYWwgbWljcm90ZXh0dXJlLCBwbGF1c2libGUgbGVucyByZW5kZXJpbmcsIGNvaGVyZW50IGFu"
    "YXRvbXksIHZpc2libGUgbWF0ZXJpYWwgZ3JhaW4sIGFuZCBjcmlzcCBkZWNpc2l2ZSBlZGdlcy4gR3JhaW4sIGhhemUsIGds"
    "b3csIGRpZmZ1c2lvbiwgc2hhbGxvdyBkZXB0aCBvZiBmaWVsZCwgYW5kIHNvZnQgZm9jdXMgbWF5IHNvZnRlbiBzZWNvbmRh"
    "cnkgbGF5ZXJzIG9ubHk7IHBocmFzZSB0aGVtIGFzIHNlY29uZGFyeS1sYXllciBhdG1vc3BoZXJlLCBuZXZlciBhcyBhIGds"
    "b2JhbGx5IHVuZm9jdXNlZCBpbWFnZS4gVGhlIHByaW1hcnkgc3ViamVjdCwgaGFuZHMsIGdhcm1lbnQgc2VhbXMsIGFuZCBk"
    "ZWNpc2l2ZSBleGlzdGluZyBlZGdlcyByZW1haW4gc2hhcnBseSByZWFkYWJsZSB1bmxlc3MgdGhlIE9SSUdJTkFMIE1BSU4g"
    "UFJPTVBUIGV4cGxpY2l0bHkgcmVxdWVzdHMgYmx1ciBvciBhYnN0cmFjdGlvbi4gTmV2ZXIgdXNlIEFJIHNtZWFyLCBwbGFz"
    "dGljIHNtb290aGluZywgd2F4eSBza2luLCBwYWludGVybHkgbXVzaCwgZ2hvc3RseSBibHVyLCBvciBzb2Z0ZW5lZCBwcmlt"
    "YXJ5IGVkZ2VzLiBGb3IgaWxsdXN0cmF0aW9uLCBwYWludGluZywgZHJhd2luZywgcHJpbnQsIGNvbGxhZ2UsIG9yIDNEIHRy"
    "ZWF0bWVudCwgYXBwbHkgdGhlIGFjdHVhbCBsaW5lLCBicnVzaCwgcHJpbnQsIGNvbGxhZ2UsIG9yIG1hdGVyaWFsIGdyYW1t"
    "YXIgYWNyb3NzIHRoZSBmb2NhbCBzdWJqZWN0IGFuZCBhIGNvbm5lY3RlZCBleGlzdGluZyBzdXJmYWNlIHdpdGhvdXQgY2hh"
    "bmdpbmcgdGhlIHNjZW5lLgoKTG9jYWxpemUgZmlzaGV5ZSwgcmVmcmFjdGlvbiwgZ2xpdGNoLCBoYWxhdGlvbiwgcGFubmlu"
    "ZywgbG9uZy1leHBvc3VyZSwgYW5kIHNpbWlsYXIgb3B0aWNzIHRvIGV4aXN0aW5nIGdlb21ldHJ5LCByZWZsZWN0aW9ucywg"
    "b3IgdGhlIGluZGljYXRlZCBtb3Rpb24gYXhpczsgbWFrZSBhIHN1cHBsaWVkIG9wdGljYWwgc2lnbmF0dXJlIGNsZWFybHkg"
    "dmlzaWJsZSB3aXRob3V0IGFkZGluZyBhIG5ldyBldmVudCBvciBvYmplY3QuIEEgc3R5bGUgbWF5IGNvbnRyb2wgb25lIGNv"
    "bXBhdGlibGUgb3Blbi1zbG90IHZpZXdwb2ludCwgcGVyc3BlY3RpdmUsIGZyYW1pbmcgcmh5dGhtLCBvciBzY2FsZSByZWxh"
    "dGlvbnNoaXDigJRlc3BlY2lhbGx5IGEgZGVmaW5pbmcgb3B0aWNhbCBzaWduYXR1cmUgc3VjaCBhcyBwcm9ub3VuY2VkIGZp"
    "c2hleWUgYmFycmVsIGRpc3RvcnRpb27igJRidXQgbWF5IG5ldmVyIG92ZXJyaWRlIGEgY2FtZXJhLCBjcm9wLCBzaG90IHNp"
    "emUsIHBvc2UsIG9yIHNwYXRpYWwgcmVsYXRpb25zaGlwIGV4cGxpY2l0bHkgZml4ZWQgYnkgdGhlIE9SSUdJTkFMIE1BSU4g"
    "UFJPTVBULiBBcHBseSBhbnkgb3Blbi1zbG90IGNvbXBvc2l0aW9uIGNoYW5nZSB0byBleGlzdGluZyBzb3VyY2UgZWxlbWVu"
    "dHM7IG5ldmVyIGltcG9ydCBhIHN0eWxlIGJvYXJkJ3Mgd29ybGQgbGF5b3V0LCBzZXR0aW5nLCBsYW5kbWFyaywgb3Igb2Jq"
    "ZWN0LgoKQXBwZW5kIG9uZSBjb2hlc2l2ZSBzdHlsZS10cmVhdG1lbnQgc2VudGVuY2UgYWZ0ZXIgdGhlIGV4YWN0IG9yaWdp"
    "bmFsIHByb21wdC4gVXNlIGRlY2lzaXZlIGJ1dCBub24tcmVwZXRpdGl2ZSB3b3JkaW5nLCBubyBtb3JlIHRoYW4gZm91ciB0"
    "cmVhdG1lbnQgY2xhdXNlcywgYW5kIGZpbmlzaCB3aXRoIHRoZSBmb2N1cyBoaWVyYXJjaHkuIERvIG5vdCBhcHBlbmQgYSBu"
    "b3VuIHdoaXRlbGlzdCwgY29tbWEtc2VwYXJhdGVkIGF1ZGl0IHRlcm1zLCBvciBhIHRyYWlsaW5nIGZyYWdtZW50LiBTaWxl"
    "bnRseSB2ZXJpZnk6IGV4YWN0IG9yaWdpbmFsIHdvcmRpbmcsIHVuY2hhbmdlZCBzdWJqZWN0IGFuZCBzY2VuZSwgemVybyBl"
    "bmhhbmNlZC1vbmx5IGZhY3RzLCBubyBzdHlsZS1kZXJpdmVkIGVudGl0aWVzLCB2aXNpYmxlIHBhbGV0dGUgcGxhY2VtZW50"
    "LCB2aXNpYmxlIG1lZGl1bSBpZGVudGl0eSwgY29tcGF0aWJsZSBvcGVuLXNsb3QgY29tcG9zaXRpb24sIGFuZCBwcmVzZXJ2"
    "ZWQgcGhvdG9ncmFwaGljIHRleHR1cmUgYW5kIGZvY3VzLgoKW09SSUdJTkFMX01BSU5fUFJPTVBUXQoKW0VOSEFOQ0VEX01B"
    "SU5fUFJPTVBUXQoKW01PT0RCT0FSRF9TVFlMRV9QUk9GSUxFX0pTT05d"
).decode("utf-8")
_V124_RB_SYSTEM_PROMPT = _V124_RB_SYSTEM_PROMPT.replace(
    "Begin the output with the complete ORIGINAL MAIN PROMPT exactly as written, preserving its subject count, identity, action, pose, gaze, expression, camera, crop, shot size, spatial relationships, setting, named objects, explicit colors, light, reflections, optical effects, focus, and requested medium.",
    "Begin the output with a faithful English translation of the complete ORIGINAL MAIN PROMPT, preserving its subject count, identity, action, pose, gaze, expression, camera, crop, shot size, spatial relationships, setting, named objects, explicit colors, light, reflections, optical effects, focus, and requested medium. If the source is already English, keep its wording unchanged; never copy non-English source text into the output.",
    1,
)
_V124_RB_SYSTEM_PROMPT = _V124_RB_SYSTEM_PROMPT.replace(
    "Append one cohesive style-treatment sentence after the exact original prompt.",
    "Append one cohesive style-treatment sentence after the faithful English rendering of the original prompt.",
    1,
)
_V124_RB_SYSTEM_PROMPT = _V124_RB_SYSTEM_PROMPT.replace(
    "Silently verify: exact original wording, unchanged subject and scene,",
    "Silently verify: all original semantic anchors preserved, unchanged subject and scene,",
    1,
)
_STYLE_ADAPTER = KreaMoodboardStyleAdapter


def _text(value: object) -> str:
    return "" if value is None else str(value)


class KreaPromptMoodboardCompiler:
    """Compile the exact Stage 2 V124-RB prompt package used by production."""

    CATEGORY = "ANe5s Nodes/Krea2"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Merged Prompt",)
    OUTPUT_TOOLTIPS = (
        "Complete Stage 2 V124-RB prompt sent to the text-generation node.",
    )
    FUNCTION = "compile"
    DESCRIPTION = (
        "Compile the fixed Stage 2 V124-RB system prompt with the original prompt, cleaned prompt, and moodboard metadata."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata_json": (
                    "STRING",
                    {
                        "default": "{}",
                        "forceInput": True,
                        "display_name": "Metadata JSON",
                        "tooltip": "Krea moodboard metadata JSON used to construct the style channels.",
                    },
                ),
                "main_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                        "display_name": "Main Prompt",
                        "tooltip": "Original main prompt retained as the source ledger.",
                    },
                ),
                "clean_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "forceInput": True,
                        "display_name": "Clean Prompt",
                        "tooltip": "Stage 1 cleaned prompt used as the enhanced source.",
                    },
                ),
            },
        }

    def _compile_parts(
        self,
        metadata_json: str,
        main_prompt: str,
        clean_prompt: str,
    ):
        source = _text(main_prompt)
        enhanced = _text(clean_prompt)
        metadata = _text(metadata_json)

        # These separators intentionally mirror the original StringConcatenate
        # nodes so the compiled prompt remains compatible with the proven
        # V124-RB TextGenerate seed/output baseline.
        source_ledger = "[ORIGINAL_MAIN_PROMPT]" + "\n" + source
        dual_source = (
            source_ledger
            + "\n\n[ENHANCED_MAIN_PROMPT]\n"
            + enhanced
        )
        style_axes_json = _STYLE_ADAPTER().adapt(metadata)[0]
        style_profile_marker = "[MOODBOARD_STYLE_PROFILE_JSON]" + "\n" + style_axes_json
        stage2_input = dual_source + "\n\n" + style_profile_marker
        stage2_model_input = _V124_RB_SYSTEM_PROMPT + "\n\n" + stage2_input

        return (
            stage2_model_input,
            stage2_input,
            style_axes_json,
            source_ledger,
        )

    def compile(
        self,
        metadata_json: str,
        main_prompt: str,
        clean_prompt: str,
    ):
        # Only the production Stage 2 model input is exposed as a node output.
        # The remaining compiled parts stay available to internal tests through
        # _compile_parts, but are not visible ports in the ComfyUI graph.
        return (self._compile_parts(metadata_json, main_prompt, clean_prompt)[0],)
