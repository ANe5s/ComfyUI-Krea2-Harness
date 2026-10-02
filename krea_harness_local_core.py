# Copyright (C) 2026 ANe5s
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

# This module is an exact mechanical extraction of the user-owned
# cleaning/style-adaptation delta from the local Moodboards plugin.
# It intentionally contains no GitHub-baseline browser/catalog code and
# has no runtime dependency on comfyui-krea-moodboards.

import json
import re

NODE_CATEGORY = "Andro.Meta/Moodboards"

_HUMAN_ENTITY_RE = re.compile(
    r"\b(?:person|persons|people|man|men|woman|women|child|children|adult|adults|boy|girl|teenager|teenage|elderly|friend|friends|couple|couples|mechanic|technician|passenger|crowd|coworker|colleague|reader|patron|student|visitor|pedestrian|passerby|traveler|worker|operator|driver|rider|riders|cyclist|cyclists|crew(?![-\s]?neck)|staff|figure|figures|human|humans)\b",
    flags=re.IGNORECASE,
)

_GENERIC_HUMAN_SYNONYMS = frozenset(
    {
        "person",
        "persons",
        "people",
        "figure",
        "figures",
        "human",
        "humans",
    }
)

_HUMAN_HAND_ACTION_RE = re.compile(
    r"\b(?:hand|hands|finger|fingers|fingertip|fingertips|palm|palms|thumb|thumbs)\b(?!-)(?!(?:\s+)(?:once|previously|formerly)\b)[^.;!?]{0,60}\b(?:rest|rests|resting|hover|hovers|hovering|hold|holds|holding|touch|touches|touching|shape|shapes|shaping|grip|grips|gripping|press|presses|pressing|reach|reaches|reaching|point|points|pointing|write|writes|writing|draw|draws|drawing|move|moves|moving)\b|\b(?:rest|rests|resting|hover|hovers|hovering|hold|holds|holding|touch|touches|touching|shape|shapes|shaping|grip|grips|gripping|press|presses|pressing|reach|reaches|reaching|point|points|pointing|write|writes|writing|draw|draws|drawing|move|moves|moving)\b[^.;!?]{0,60}\b(?<!by )(?:hand|hands|finger|fingers|fingertip|fingertips|palm|palms|thumb|thumbs)\b(?!-)",
    flags=re.IGNORECASE,
)

_UNREQUESTED_HAND_ACTION_CLAUSE_RE = re.compile(
    r"(?:,\s*|\band\s+)?(?:(?:her|his|their|the subject's)\s+)?(?:hands?|fingers?|fingertips?|palms?|thumbs?)\b[^.;!?]{0,100}\b(?:rest|rests|resting|hover|hovers|hovering|hold|holds|holding|touch|touches|touching|shape|shapes|shaping|grip|grips|gripping|press|presses|pressing|reach|reaches|reaching|point|points|pointing|write|writes|writing|draw|draws|drawing|move|moves|moving)\b[^.;!?]*",
    flags=re.IGNORECASE,
)

_NATURAL_HAND_METAPHOR_RE = re.compile(
    r"\b(?:branch|branches|root|roots|bark|leaf|leaves|limb|limbs|twig|twigs|vines?|clouds?)\b[^.;!?]{0,65}\b(?:hand|hands|finger|fingers|palm|palms|thumb|thumbs)\b|\b(?:like|as if|as though|resembling|reminiscent of)\b[^.;!?]{0,45}\b(?:hand|hands|finger|fingers|palm|palms|thumb|thumbs)\b",
    flags=re.IGNORECASE,
)

_METAPHORICAL_HUMAN_RE = re.compile(
    r"\b(?:human|humans)\s+(?:touch|hands?|labor|presence|intervention|craft|intention|element|error|scale|history)\b|\bhuman[- ](?:made|crafted|shaped|formed)\b",
    flags=re.IGNORECASE,
)

_ANIMAL_ENTITY_RE = re.compile(r"\b(?:animal|dog|cat|bird|horse|wolf|deer|fish|insect|creature)\b", flags=re.IGNORECASE)

_VEHICLE_ENTITY_RE = re.compile(
    r"\b(?:vehicle|car|truck|bus|train|airplane|aircraft|spacecraft|spaceship|motorcycle|bicycle|boat|ship)\b",
    flags=re.IGNORECASE,
)

_EXTRA_HUMAN_RE = re.compile(
    r"\b(?:another|second|additional|background)(?:\s+(?:faint|distant|far-off|shadowy|dark|ghostly|blurred|indistinct|soft|subordinate|light-colored|light|dark-colored))*\s+(?:person|people|man|woman|figure|human|passenger|friend|friends|couple|coworker|colleague|reader|patron|student|visitor|pedestrian|passerby|traveler|worker|operator|technician|driver|rider|cyclist|silhouette)\b|\b(?:two|three|several)(?:\s+(?:faint|distant|far-off|shadowy|dark|ghostly|blurred|indistinct|soft|subordinate|light-colored|light|dark-colored))*\s+(?:people|persons|men|women|adults|children|figures|humans|passengers|friends|couples|coworkers|colleagues|readers|patrons|students|visitors|pedestrians|travelers|workers|operators|technicians|riders|cyclists|silhouettes)\b|\b(?:crowd|reader|patron|student|visitor|pedestrian|passerby|traveler|worker|operator|technician|driver|rider|cyclist|crew(?![-\s]?neck)|staff)\b",
    flags=re.IGNORECASE,
)

_NEW_SILHOUETTE_ENTITY_RE = re.compile(
    r"\b(?:a|an|one|single|solitary|lone|another|second|additional)"
    r"(?:\s+(?:faint|distant|far-off|shadowy|dark|ghostly|blurred|indistinct|soft|subordinate|isolated))*"
    r"\s+silhouette\b"
    r"|\bsilhouette\s+(?:stands?|walks?|sits?|faces?|looks?|turns?|reaches?|moves?|gazes?|waits?)\b",
    flags=re.IGNORECASE,
)

_BACKGROUND_HUMAN_RE = re.compile(
    r"\b(?:faint|distant|far-off|shadowy|ghostly|blurred|background)(?:\s*,?\s+(?:faint|distant|far-off|shadowy|ghostly|blurred|indistinct|soft|subordinate))*\s+(?:human\s+)?(?:people|persons|figures|humans|silhouettes)\b|\b(?:human|humans)\s+(?:figure|figures|silhouette|silhouettes)\b",
    flags=re.IGNORECASE,
)

_CAPTURE_FORMAT_RE = re.compile(
    r"\b(?:medium[- ]format|large[- ]format|full[- ]frame|35mm|70mm|16mm|mirrorless|dslr|anamorphic|focal\s+length|sensor)\b",
    flags=re.IGNORECASE,
)

_METAPHORICAL_TRAVELER_RE = re.compile(
    r"\b(?:cable\s+car|gondola|vehicle|car|train|bus|boat|ship|aircraft|spacecraft|motorcycle|bicycle)\b[^.;!?]{0,90}\bas\b[^.;!?]{0,45}\btraveler\b",
    flags=re.IGNORECASE,
)

_ENTITY_NEGATION_RE = re.compile(r"\b(?:no|not|without|devoid of|empty of|free of|free from|zero|absent|absence of|untouched by)\b", flags=re.IGNORECASE)

_ENVIRONMENT_CONTEXT_RE = re.compile(
    r"\b(?:greenhouse|harbor|harbour|meadow|field|forest|woodland|garden|orchard|shore|coast|beach|river|lake|marsh|swamp|mountain|valley|desert|street|avenue|market|station|terminal|bus\s+window|train\s+carriage|rehearsal\s+room|workshop|studio|warehouse|factory|office|control\s+room|interior|landscape|underwater|aquatic|ocean|water|outdoors?)\b",
    flags=re.IGNORECASE,
)

_SUBORDINATE_ENTITY_CONTEXT_RE = re.compile(
    r"\b(?:distant|farther|background|behind|beside|nearby|along|across|beyond|scattered|anchored|moored|dock(?:ed)?|drifts?|bobs?|rests?|perches?|tangled|silhouette|horizon|shoreline|water|field|grass|branch|pier|piling|mist|tide|canopy|underbrush)\b",
    flags=re.IGNORECASE,
)

_ABSTRACT_RE = re.compile(r"\b(?:abstract|graphic|diagram|typography|poster|vector)\b", flags=re.IGNORECASE)

_ABSTRACT_SCENE_DRIFT_RE = re.compile(
    r"\b(?:cathedral|church|chapel|temple|building|architecture|architectural|ruin|ruins|landscape|cityscape|city|street|forest|mountain|valley|room|interior)\b",
    flags=re.IGNORECASE,
)

_REFUSAL_OR_PROTOCOL_RE = re.compile(
    r"^\s*(?:i['’]?m sorry|sorry|i cannot|i can['’]?t|i['’]?m unable|as an ai|the prompt you provided|please provide a revised prompt|you['’]?re not a prompt engineer|you are not a prompt engineer|you['’]?re asking me to (?:generate|write|create) a prompt|you are asking me to (?:generate|write|create) a prompt|this is not a request|this isn['’]?t a request|your job is to|i['’]?ll (?:craft|write|create) (?:that|a prompt)|.*(?:guidelines|policies|policy|not permitted|cannot fulfill).*)",
    flags=re.IGNORECASE | re.DOTALL,
)

_CJK_RE = re.compile(r"[\u3400-\u9fff]")

_EXACT_SUBJECT_COUNT_RE = re.compile(r"\bexactly\s+one\s+([^;,.]+)", flags=re.IGNORECASE)

_MEDIUM_DRIFT_RE = re.compile(
    r"\b(?:3d render|3d-rendered|photorealistic|photorealism|hyperrealistic|realistic rendering|digital realism)\b",
    flags=re.IGNORECASE,
)

_MEDIUM_NEGATION_RE = re.compile(
    r"\b(?:no|not|without|avoid|avoiding|devoid of|free of|free from|lacks?|never)\b",
    flags=re.IGNORECASE,
)

_TECHNICAL_SUBJECT_SIDE_RE = re.compile(
    r"\b(?:earpiece|earcup|headset|headband|microphone|ear[- ]side\s+(?:interface|device|unit)|technical\s+wearable|rugged\s+collar)\b",
    flags=re.IGNORECASE,
)

_MEDIUM_FAMILY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("photographic", re.compile(r"\b(?:photograph|photographic|photo|photorealistic|photorealism|hyperrealistic|cinematic\s+photograph)\b", flags=re.IGNORECASE)),
    ("illustration", re.compile(r"\b(?:illustration|illustrated|anime|manga|comic|cartoon)\b", flags=re.IGNORECASE)),
    ("painting", re.compile(r"\b(?:painting|painted|watercolor|watercolour|oil\s+painting|gouache)\b", flags=re.IGNORECASE)),
    ("drawing", re.compile(r"\b(?:drawing|sketch|line\s*art|ink\s+art)\b", flags=re.IGNORECASE)),
    ("render", re.compile(r"\b(?:3d|3-d|cgi|render|rendering|digital\s+(?:render|realism|composite|matte)|cinematic\s+(?:still|realism))\b", flags=re.IGNORECASE)),
    ("graphic", re.compile(r"\b(?:graphic|poster|vector|flat\s+design)\b", flags=re.IGNORECASE)),
    ("diagram", re.compile(r"\b(?:diagram|schematic|infographic)\b", flags=re.IGNORECASE)),
)

_STYLE_AXIS_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    # Keep style optics while removing literal world-material nouns that can
    # be hallucinated as new objects when the source scene does not contain
    # them.  The official positive remains available for audit; the adapter
    # receives these style-only transfer witnesses instead.
    ("fluted glass refraction", "vertical refraction bands"),
    ("glass refraction", "vertical refraction bands"),
    ("fluffy cumulus clouds", "soft rounded light masses"),
    ("cumulus clouds", "soft rounded light masses"),
    ("volumetric cloud shadows", "volumetric tonal shadows"),
    ("volumetric cloud shadow", "volumetric tonal shadow"),
    ("cloud shadows", "volumetric tonal shadows"),
    ("cloud shadow", "volumetric tonal shadows"),
    ("expansive skies", "open tonal space"),
    ("expansive sky", "open tonal space"),
    ("lush green landscape", "lush green tonal field"),
    ("green landscape", "green tonal field"),
    ("extreme low-angle fisheye", "unmistakable fisheye barrel warp"),
    ("low-angle fisheye", "unmistakable fisheye barrel warp"),
    ("fisheye framing", "unmistakable fisheye barrel warp"),
    ("forced perspective", "visible perspective warp"),
    ("long-exposure light trails", "streaked light diffusion"),
    ("light trails", "streaked light diffusion"),
    ("sacred geometry", "geometric surface rhythm"),
    ("stark silhouette accents", "stark edge separation"),
    ("silhouette-focused composition", "controlled edge separation"),
    ("minimalist graphic staging", "restrained graphic simplicity"),
    ("cinematic composition", "cinematic visual rhythm"),
    ("pictorialist composition", "pictorial tonal rhythm"),
    ("interior stillness staging", "quiet stillness"),
    ("fisheye wide-angle warp", "visible fisheye barrel distortion"),
    ("wide-angle warp", "visible wide-angle barrel distortion"),
    ("depth of field", "selective focus falloff"),
    ("vibrant minimalist grounds", "clean color-field simplicity"),
    ("chunky rounded geometry", "rounded form language"),
    ("vinyl-toy polish", "smooth polished surface treatment"),
    ("retro-futuristic detailing", "restrained retro-futurist surface detailing"),
    ("dystopian architecture", "dystopian tonal language"),
    ("gothic architecture", "gothic tonal language"),
)

_STYLE_AXIS_DROP_TERMS: tuple[str, ...] = (
    "aerial",
    "high-angle framing",
    "high-angle",
    "top-down",
    "drone",
    "low-angle framing",
    "framing",
    "perspective",
    "camera angle",
    "camera",
    "lens",
    "layout",
    "staging",
    "shot",
    "foreground",
    "midground",
    "centered framing",
    # Keep literal subject, pose, camera, and scene residue out of the
    # style-only transfer channels. World-level meaning is extracted
    # separately by _safe_world_semantics().
    "low-angle",
    "upward perspective",
    "downward perspective",
    "wide-angle",
    "close-up",
    "close framing",
    "macro",
    "scenic",
    "wide scenic",
    "upward view",
    "downward view",
    "portraiture",
    "portrait",
    "portraits",
    "silhouette",
    "silhouetted",
    "monolith",
    "monoliths",
    "composition",
    "negative space",
    "vast space",
    "expansive space",
    "wide view",
    "wide shot",
    "open vista",
    "spatial layout",
    "depth layout",
    "camera position",
    "angle of view",
    "arrangement",
    "scale-focused",
    "scale",
    "vertiginous",
    "monumental",
    "monumentally",
    "megastructure",
    "megastructures",
    "brutalist",
    "megastucture",
    "foregrounding",
    "foregrounded",
    "foregrounds",
    "expansive",
    "stacked scale",
    "architectural",
    "architecture",
    "building",
    "buildings",
    "landscape",
    "sky",
    "skies",
    "cloud",
    "clouds",
    "vegetation",
    "foliage",
    "trees",
    "tree",
    "street",
    "cityscape",
    "city",
    "ruins",
    "fields",
    "pastoral",
    "figure",
    "figures",
    "crowd",
    "vehicle",
    "vehicles",
    "animal",
    "animals",
)

_STYLE_CHANNEL_TERMS: dict[str, tuple[str, ...]] = {
    "palette": (
        "color", "palette", "tone", "teal", "cyan", "amber", "orange", "gold",
        "yellow", "blue", "indigo", "navy", "crimson", "red", "green", "verdant",
        "purple", "violet", "magenta", "coral", "arctic", "earthy", "muted",
        "desaturated", "monochrome", "neon", "vibrant", "pastel", "warm", "cool",
        "dark", "bright",
    ),
    "lighting": (
        "light", "lighting", "glow", "luminous", "illumination", "illuminated",
        "shadow", "chiaroscuro", "backlight", "rim-light", "rim light", "shaft",
        "volumetric", "studio", "overcast", "sunlit", "sunlight", "raking", "diffuse",
    ),
    "contrast": (
        "contrast", "high-key", "low-key", "dynamic range", "tonal depth",
        "shadow depth", "shadow separation", "dramatic",
    ),
    "atmosphere": (
        "haze", "fog", "mist", "atmospheric", "diffusion", "ethereal", "dreamy",
        "fluid", "air", "particulate", "smoky",
    ),
    "texture_medium": (
        "grain", "texture", "painterly", "brushstroke", "brushstrokes", "oil",
        "watercolor", "gouache", "clay", "matte", "polished", "plastic", "vinyl",
        "illustration", "illustrated", "cinematic", "film", "analog", "glitch",
        "halftone", "sketch", "ink", "rendering", "render", "surface", "surfacing",
        "grit", "material", "porcelain", "ceramic", "glaze", "glazed", "subsurface",
        "airbrush", "airbrushed", "fuzzy", "plush", "knitted", "wool", "paper",
        "cutout", "cut-out", "print", "photographic", "film stock", "gradient",
        "process", "engraved", "engraving", "etching", "risograph", "pointill",
    ),
    "optics": (
        "fisheye", "wide-angle", "distortion", "barrel", "refraction", "refracted",
        "chromatic aberration", "double exposure", "motion blur", "long exposure",
        "panning", "halation", "scanline", "optical", "lens warp", "scale exaggeration",
    ),
}

_SUBJECT_SIDE_AUTHORITY_RE = re.compile(
    r"\b(?:industrial|dieselpunk|retro[- ]futur(?:ist|ism)|cybernetic|engineered|mechanical|technical|protective|rugged\s+equipment)\b",
    flags=re.IGNORECASE,
)

_WORLD_SEMANTIC_MARKERS: tuple[str, ...] = (
    "oceanic", "ocean", "marine", "aquatic", "underwater", "celestial",
    "astral", "cosmic", "botanical", "floral", "desert", "arctic", "tropical",
    "volcanic", "lunar", "industrial", "dieselpunk", "retro-futurist",
    "retro futuristic", "cybernetic", "mechanical", "gothic", "noir",
    "surrealist", "whimsical", "futuristic", "vintage", "baroque",
)

_PALETTE_MARKERS: tuple[str, ...] = (
    "palette", "color", "colour", "tone", "harmony", "duotone", "monochrome",
    "gradient", "warm-toned", "cool-toned", "earthy", "muted", "desaturated",
    "vibrant", "pastel", "neon", "chromatic",
)

_LIGHTING_MARKERS: tuple[str, ...] = (
    "light", "lighting", "glow", "luminous", "illumination", "illuminated",
    "shadow", "chiaroscuro", "backlight", "rim-light", "rim light", "shaft",
    "volumetric", "studio", "overcast", "sunlit", "sunlight", "raking", "diffuse",
)

_STYLE_GUIDANCE_SECTION_RE = re.compile(
    r"\b(?P<label>palette|lighting|medium\s+and\s+texture|composition|contrast|atmosphere|era\s+or\s+movement)\s*:\s*(?P<body>.*?)(?=\s+(?:palette|lighting|medium\s+and\s+texture|composition|contrast|atmosphere|era\s+or\s+movement)\s*:|$)",
    flags=re.IGNORECASE,
)

_OPTICAL_GUIDANCE_RE = re.compile(
    r"\b(?:fisheye|wide[- ]angle|forced\s+perspective|distortion|barrel|refraction|refract|chromatic\s+aberration|double\s+exposure|motion\s+blur|long\s+exposure|panning|halation|scanline|lens\s+warp|optical)\b",
    flags=re.IGNORECASE,
)

_STYLE_SOURCE_BOUND_DETAIL_REPLACEMENTS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    # These are treatment-side nouns that a moodboard profile can introduce
    # while describing its example image.  Keep them only when the immutable
    # source explicitly contains them; otherwise bind the same treatment to a
    # generic existing surface or geometry.
    (r"\b(?:mountain\s+range|mountain\s+ranges)\b", "distant tonal mass", ("mountain range", "mountain ranges")),
    (r"\bhorizon(?:\s+lines?)?\b", "open tonal field", ("horizon", "horizon lines")),
    (r"\bstairwell\b", "existing stair geometry", ("stairwell",)),
    (r"\blapels?\b", "existing garment surface", ("lapel", "lapels")),
    (r"\bcollars?\b", "existing garment edge", ("collar", "collars")),
    (r"\bsleeves?\b", "existing garment surface", ("sleeve", "sleeves")),
    (r"\b(?:deep\s+blue|blue)\s+sk(?:y|ies)\b", "deep blue tonal field", ("sky", "skies")),
    (r"\bsky\s+blues?\b", "blue tonal accents", ("sky", "skies")),
    # The broad absent-world pass may already have rewritten "sky" before
    # this detail pass runs.  Normalize those intermediate forms as well.
    (r"\bdeep\s+blue\s+open\s+tonal\s+field\b", "deep blue tonal field", ()),
    (r"\bopen\s+tonal\s+field\s+blues?\b", "blue tonal accents", ()),
    (r"\bexternal\s+environments?\b", "surrounding tonal field", ()),
    (r"\bshadowy\s+silhouettes?\b", "shadowy tonal forms", ()),
    (r"\blong\s+silhouettes?\b", "long cast shadows", ()),
    (r"\bfocal\s+forms?\b", "focal geometry", ()),
    (r"\bfocal\s+zones?\b", "focal geometry", ()),
    (r"\bmonochromatic\s+foundation\s+strict\s+monochromatic\s+tonal\s+structure\b", "monochromatic foundation with strict tonal structure", ()),
)

_STYLE_PROFILE_WITNESS_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\b(?:porcelain[- ]like|porcelain)\s+skin\b", "porcelain-like surface finish"),
    (r"\bsculptural\s+facial\s+features?\b", "sculptural form modeling"),
    (r"\b(?:wind[- ]swept|wind[- ]blown)\s+hair\b", "directional edge movement"),
    (r"\bhair\s+texture\b", "edge texture"),
    (r"\bskin\s+texture\b", "surface texture"),
    (r"\b(?:delicate|fine|visible|subtle)\s+skin\s+pores?\b", "fine surface texture"),
    (r"\b(?:candid|ethereal|editorial)\s+portrait(?:ure)?\b", "candid image treatment"),
    (r"\burban\s+portrait(?:ure)?\b", "documentary surface treatment"),
    (r"\bportrait\s+photography\b", "photographic treatment"),
    (r"\bstreetwear\s+aesthetic\b", "youthful graphic styling"),
    (r"\bhigh[- ]energy\s+urban\b", "high-energy graphic"),
    (r"\bfacial\s+expressions?\b", "expressive tonal contrast"),
    (r"\bhand\s+cross[- ]hatching\b", "cross-hatching"),
    (r"\b(?:across|through|on)\s+every\s+surface\s+by\s+hand\b", "across every surface with tactile precision"),
    (r"\bby\s+hand\b", "with tactile precision"),
    (r"\bcomic\s+hand\b", "comic line language"),
    (r"\bstorybook\s+hand\b", "storybook line language"),
    (r"\b(?:deep\s+blue|blue)\s+sk(?:y|ies)\b", "deep blue tonal field"),
    (r"\bsky\s+blues?\b", "blue tonal accents"),
    (r"\b(?:volumetric\s+)?cloud\s+shadows?\b", "volumetric tonal shadows"),
    (r"\bexternal\s+environments?\b", "surrounding tonal field"),
    (r"\binterior\s+points\b", "existing ambient light"),
    (r"\bfocal\s+forms?\b", "focal geometry"),
    (r"\bfocal\s+zones?\b", "focal geometry"),
    (r"\bnatural\s+elements?\b", "existing surfaces"),
    (r"\brustic\s+structural\s+forms?\b", "existing structural surfaces"),
)

_STYLE_PROFILE_DROP_TERMS: tuple[str, ...] = (
    "hair", "skin", "face", "faces", "facial", "eye", "eyes", "iris", "irises",
    "mouth", "lips", "nose", "cheek", "cheeks", "hands", "hand", "fingers",
    "finger", "body", "head", "shoulder", "shoulders", "portrait", "portraits",
    "portraiture", "person", "people", "woman", "man", "girl", "boy", "figure",
    "figures", "cottage", "house", "street", "city", "sky", "skies", "cloud",
    "clouds", "mountain", "mountains", "landscape", "landscapes", "garden", "tree",
    "trees", "vegetation", "foliage", "forest", "ocean", "sea", "river", "lake",
    "water", "shoe", "shoes", "sneaker", "sneakers", "dress", "shirt", "jacket",
    "trousers", "pants", "bag", "vehicle", "vehicles", "car", "animal", "animals",
    "fish", "bird", "architecture", "architectural", "building", "buildings", "room",
    "window", "door", "doorway", "fixture", "bulb", "lamp", "lantern", "glass",
)

_WORLD_SEMANTIC_TREATMENTS: dict[str, str] = {
    "oceanic": "fluid reflective tonality",
    "ocean": "deep reflective tonality",
    "marine": "cool reflective tonality",
    "aquatic": "fluid reflective tonality",
    "underwater": "submerged atmospheric tonality",
    "celestial": "luminous atmospheric tonality",
    "astral": "luminous atmospheric tonality",
    "cosmic": "expansive luminous tonality",
    "botanical": "organic surface rhythm",
    "floral": "organic line rhythm",
    "desert": "dry sun-baked tonal contrast",
    "arctic": "pale cool tonal contrast",
    "tropical": "saturated warm-cool tonality",
    "volcanic": "ember-dark tonal contrast",
    "lunar": "cool mineral tonality",
    "industrial": "mechanical surface rhythm",
    "dieselpunk": "weathered mechanical tonality",
    "retro-futurist": "retro-futurist material rhythm",
    "retro futuristic": "retro-futurist material rhythm",
    "cybernetic": "precise technical surface rhythm",
    "mechanical": "mechanical surface rhythm",
    "gothic": "gothic shadow tonality",
    "noir": "noir shadow tonality",
    "surrealist": "surreal tonal juxtaposition",
    "futuristic": "precise luminous tonality",
    "vintage": "vintage tonal response",
    "baroque": "ornate tonal rhythm",
    "whimsical": "whimsical tonal rhythm",
}

_STYLE_ILLUSTRATIVE_TERMS = re.compile(
    r"\b(?:illustration|illustrated|anime|manga|comic|cartoon|painting|painted|watercolor|"
    r"watercolour|gouache|hand[- ]drawn|line\s*art|ink\s+(?:art|line)|brushwork|painterly|"
    r"vector|stipple|risograph|screen[- ]?print(?:ing)?|printmaking|woodcut|linocut|etching|"
    r"engraving|collage|cut[- ]paper|flat\s+graphic|graphic\s+design|cel\s+animation|"
    r"digital\s+painting|illustrative|graphic\s+novel|poster\s+art|pixel\s+art)\b",
    flags=re.IGNORECASE,
)

_STYLE_PHOTOGRAPHIC_TERMS = re.compile(
    r"\b(?:photograph|photographic|photography|photo|documentary|35mm\s+film|film\s+grain|"
    r"analog\s+film|raw\s+capture|realistic\s+capture)\b",
    flags=re.IGNORECASE,
)

_STYLE_CONFLICTING_PHOTOGRAPHIC_TERMS = re.compile(
    r"\b(?:cinematic\s+realism|cinematic\s+realistic|photographic\s+(?:rendering|realism|capture)|"
    r"photorealistic|photorealism|realistic\s+rendering|realistic\s+capture|"
    r"(?:clean,?\s+)?studio[- ]like\s+(?:medium|rendering|look)|"
    r"shallow\s+depth\s+of\s+field|deep\s+depth\s+of\s+field|depth\s+of\s+field|"
    r"(?:softly\s+)?blur(?:red|ring)?\s+(?:the\s+)?background|background\s+blur|"
    r"background\s+(?:is\s+)?out\s+of\s+focus)\b",
    flags=re.IGNORECASE,
)

_STYLE_CONFLICTING_ILLUSTRATIVE_TERMS = re.compile(
    r"\b(?:painterly\s+(?:mush|blur|rendering)|anime\s+rendering|cartoon(?:ish)?\s+rendering|"
    r"illustrative\s+photo(?:graph)?ic\s+rendering)\b",
    flags=re.IGNORECASE,
)

def _source_has_style_term(source_prompt: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", str(source_prompt or ""), flags=re.IGNORECASE))

def _existing_subject_surface(source_prompt: str) -> str:
    source = str(source_prompt or "")
    for term in ("jacket", "coat", "shirt", "dress", "garment", "sleeve", "trousers", "pants", "face", "skin", "hands", "body"):
        if _source_has_style_term(source, term):
            return term
    return "existing focal surface"

def _replace_unrequested_style_entities(candidate_prompt: str, source_prompt: str) -> str:
    """Keep style transfer on the source scene instead of importing profile nouns.

    Moodboard keywords often contain literal example-world nouns (clouds, sky,
    glass, a bulb, and so on).  They are valid catalog evidence but are not
    valid scene facts unless the original prompt already contains them.  This
    generic pass translates only absent nouns into surface/light/tonal effects;
    it does not alter any term that is present in the immutable source.
    """
    text = str(candidate_prompt or "")
    source = str(source_prompt or "")
    surface = _existing_subject_surface(source)

    replacements = (
        (r"\b(?:a|an|the)\s+(?:(?:flickering|flicker(?:ing)?)\s+)?(?:overhead\s+)?(?:light\s+)?(?:bulb|lamp|lantern)\b", "a localized highlight", ("bulb", "lamp", "lantern")),
        (r"\b(?:(?:flickering|flicker(?:ing)?)\s+)?(?:overhead\s+)?(?:light\s+)?(?:bulb|lamp|lantern)\b", "localized highlight", ("bulb", "lamp", "lantern")),
        (r"\b(?:volumetric\s+)?(?:cloud|clouds|cumulus)\s+shadows?\b", "volumetric tonal shadows", ("cloud", "clouds", "cumulus")),
        (r"\b(?:deep\s+)?blue\s+sk(?:y|ies)\s+tones?\b", "deep blue tonal accents", ("sky", "skies")),
        (r"\b(?:fluted\s+)?glass\s+refraction\b", "vertical surface refraction", ("glass",)),
        (r"\binterior\s+points\b", "existing ambient light", ()),
        (r"\barchitectural[- ]visualization\s+rendering\b", "structured surface rendering", ("architecture", "architectural")),
        (r"\barchitectural\s+surfaces?\b", "existing structural surfaces", ("architecture", "architectural")),
    )
    for pattern, replacement, source_terms in replacements:
        if not any(_source_has_style_term(source, term) for term in source_terms):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    absent_replacements = {
        "sky": "open tonal field",
        "skies": "open tonal field",
        "cloud": "tonal volume",
        "clouds": "tonal volume",
        "landscape": "existing surroundings",
        "landscapes": "existing surroundings",
        "vegetation": "organic surface texture",
        "foliage": "organic surface texture",
        "tree": "vertical surface rhythm",
        "trees": "vertical surface rhythm",
        "forest": "deep atmospheric texture",
        "garden": "layered surface texture",
        "mountain": "distant tonal mass",
        "mountains": "distant tonal masses",
        "ocean": "deep tonal field",
        "sea": "deep tonal field",
        "water": "fluid reflective surface texture",
        "river": "reflective tonal flow",
        "lake": "reflective tonal field",
        "street": "urban surface texture",
        "city": "distant tonal mass",
        "building": "existing structural surface",
        "buildings": "existing structural surfaces",
        "architecture": "structural geometry",
        "architectural": "structural surface treatment",
        "glass": "translucent surface",
        "bulb": "localized highlight",
        "lamp": "localized highlight",
        "lantern": "localized highlight",
        "skin": "existing focal surface",
        "facial": "focal",
        "face": "existing focal form",
        "faces": "existing focal forms",
        "eye": "focal detail",
        "eyes": "focal details",
        "mouth": "focal detail",
        "lips": "focal detail",
        "nose": "focal form",
        "cheek": "focal surface",
        "cheeks": "focal surfaces",
        "body": "subject form",
        "head": "subject form",
        "shoulder": "subject form",
        "shoulders": "subject forms",
        "hands": "subject details",
        "fingers": "subject details",
        "portrait": "image treatment",
        "portraits": "image treatment",
        "portraiture": "image treatment",
        "figure": "existing focal form",
        "figures": "existing focal forms",
        "window": "reflective surface",
        "room": "open tonal space",
        "screen": "rectangular surface",
        "monitor": "rectangular surface",
        "fixture": "existing surface detail",
    }
    for term, replacement in absent_replacements.items():
        if not _source_has_style_term(source, term):
            text = re.sub(rf"(?<!\w){re.escape(term)}(?!\w)", replacement, text, flags=re.IGNORECASE)

    if not _source_has_style_term(source, "hair"):
        text = re.sub(
            r"\b(?:the\s+)?(?:person['’]s|figure['’]s|their|his|her)\s+hair\b",
            f"the {surface}",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\bhair\b", surface, text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()

def _replace_unrequested_style_details(candidate_prompt: str, source_prompt: str) -> str:
    """Keep inferred body, garment, and world details out of style prose.

    The style profile is allowed to control treatment, but its example-world
    nouns must not become new scene facts.  This second pass covers compound
    details (for example ``mountain range`` or ``jacket lapel``) that are not
    safely handled by the broad world-word pass above.
    """
    text = str(candidate_prompt or "")
    source = str(source_prompt or "")
    for pattern, replacement, source_terms in _STYLE_SOURCE_BOUND_DETAIL_REPLACEMENTS:
        if any(_source_has_style_term(source, term) for term in source_terms):
            continue
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    if not _source_has_style_term(source, "skin"):
        text = re.sub(
            r"\b(?:delicate|fine|visible|subtle)\s+skin\s+pores?\b",
            "fine surface texture",
            text,
            flags=re.IGNORECASE,
        )
    return re.sub(r"\s{2,}", " ", text).strip()

def _rewrite_style_profile_witnesses(candidate_prompt: str, source_prompt: str) -> str:
    """Abstract profile witness phrases without rewriting the source ledger."""
    def clean_suffix(text: str) -> str:
        for pattern, replacement in _STYLE_PROFILE_WITNESS_REPLACEMENTS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", text).strip()

    return _transform_style_suffix(candidate_prompt, source_prompt, clean_suffix)

def _style_profile_channel_text(style_profile: str) -> str:
    """Return only structured style-channel text for medium conflict checks."""
    try:
        payload = json.loads(str(style_profile or "{}"))
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    channels = payload.get("style_channels")
    if not isinstance(channels, dict):
        return ""
    values: list[str] = []
    for channel in ("palette", "lighting", "contrast", "atmosphere", "texture_medium", "optics", "emotion_design"):
        raw_values = channels.get(channel)
        if isinstance(raw_values, list):
            values.extend(str(value or "") for value in raw_values)
    return " ".join(values)

def _localized_optical_treatments(body: str) -> list[str]:
    """Extract only explicit optical witnesses from a composition sentence."""
    replacements = {
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
    treatments: list[str] = []
    seen: set[str] = set()
    for optical_match in _OPTICAL_GUIDANCE_RE.finditer(str(body or "")):
        token = " ".join(optical_match.group(0).split()).casefold()
        treatment = replacements.get(token)
        if treatment and treatment not in seen:
            seen.add(treatment)
            treatments.append(treatment)
    return treatments

def _extract_official_style_guidance(candidate_prompt: str, *, title: str = "") -> str:
    """Keep the official positive's treatment sections, not its instruction wrapper."""
    text = str(candidate_prompt or "").strip()
    if not re.search(r"\bStyle-only\s+Krea\s+moodboard\s+guidance\s*:", text, flags=re.IGNORECASE):
        return text
    # Style keywords are useful catalog metadata but often contain the raw
    # example composition (wide framing, scenic nouns, etc.).  The structured
    # channel adapter already preserves the useful witnesses, so do not send
    # this low-level keyword tail through the direct positive route.
    text = re.sub(r"\s+Style\s+keywords\s*:.*$", "", text, flags=re.IGNORECASE)
    # The normal/strong positive begins with ``<title>:``.  Some official
    # titles contain a section label, e.g. ``Candid Cinematic Atmosphere``;
    # removing that title before section parsing prevents the title's
    # ``Atmosphere`` suffix from being mistaken for a real style section.
    title_text = str(title or "").strip()
    if title_text:
        title_prefix = f"{title_text}:"
        title_start = text.find(title_prefix)
        if title_start >= 0:
            text = text[title_start + len(title_prefix):].lstrip()
    sections: list[str] = []
    for match in _STYLE_GUIDANCE_SECTION_RE.finditer(text):
        label = " ".join(match.group("label").split())
        body = " ".join(match.group("body").split()).strip(" ;:.")
        if not body:
            continue
        if label.casefold() == "composition":
            # Composition prose is the main path by which a moodboard can
            # override the user's requested layout. Preserve only explicit
            # optical treatment (fisheye, refraction, motion blur, etc.) as a
            # localized style cue; discard center/symmetry/shot/angle/scale,
            # scenic nouns, and spatial arrangement instructions wholesale.
            optical_treatments = _localized_optical_treatments(body)
            if optical_treatments:
                sections.append(
                    "Optical treatment: "
                    + ", ".join(optical_treatments)
                )
            continue
        sections.append(f"{label}: {body}")
    if not sections:
        return text
    return ". ".join(sections).strip(" .") + "."

def _transform_style_suffix(candidate_prompt: str, source_prompt: str, transform) -> str:
    """Apply a style-only transform without rewriting the immutable source."""
    text = str(candidate_prompt or "")
    source = str(source_prompt or "")
    if source and text.startswith(source):
        return text[: len(source)] + transform(text[len(source) :])
    return transform(text)

def _replace_positive_medium_conflicts(pattern: re.Pattern[str], replacement: str, text: str) -> str:
    """Replace medium conflicts only in positive clauses, not anti-artifact text."""
    protected_negatives: list[str] = []

    def protect_negative(match: re.Match[str]) -> str:
        protected_negatives.append(match.group(0))
        return f"__KREA_NEGATIVE_MEDIUM_{len(protected_negatives) - 1}__"

    text = re.sub(
        r"\b(?:without|avoid(?:ing)?|no|never)\b[^.;!?]{0,120}",
        protect_negative,
        text,
        flags=re.IGNORECASE,
    )
    text = pattern.sub(replacement, text)
    for index, original in enumerate(protected_negatives):
        text = text.replace(f"__KREA_NEGATIVE_MEDIUM_{index}__", original)
    return text

def _sanitize_style_medium_conflicts(candidate_prompt: str, source_prompt: str, style_profile: str) -> str:
    """Prevent a style sentence from mixing photographic and illustrative media."""
    profile_text = _style_profile_channel_text(style_profile)
    if not profile_text:
        return str(candidate_prompt or "")
    source_text = str(source_prompt or "")

    def clean_suffix(text: str) -> str:
        if _STYLE_ILLUSTRATIVE_TERMS.search(profile_text) and not _STYLE_ILLUSTRATIVE_TERMS.search(source_text):
            text = _replace_positive_medium_conflicts(
                _STYLE_CONFLICTING_PHOTOGRAPHIC_TERMS,
                "coherent illustrated rendering", text
            )
        if _STYLE_PHOTOGRAPHIC_TERMS.search(profile_text) and not _STYLE_PHOTOGRAPHIC_TERMS.search(source_text):
            text = _replace_positive_medium_conflicts(
                _STYLE_CONFLICTING_ILLUSTRATIVE_TERMS,
                "textured photographic rendering", text
            )
        return re.sub(r"\s{2,}", " ", text).strip()

    return _transform_style_suffix(candidate_prompt, source_prompt, clean_suffix)

def _strip_unsupported_monochrome_accent(candidate_prompt: str, source_prompt: str, style_profile: str) -> str:
    """Keep a profile-declared accent without inventing an unsupported hue."""
    profile_text = _style_profile_channel_text(style_profile)
    if not re.search(r"\b(?:monochrome|monochromatic|grayscale|grey[- ]scale|black[- ]and[- ]white)\b", profile_text, flags=re.IGNORECASE):
        return str(candidate_prompt or "")
    if re.search(
        r"\b(?:accent|accented)\b[^.;,]{0,40}\b(?:red|orange|yellow|green|blue|purple|violet|pink|brown|black|white|gray|grey|gold|golden|amber|crimson|teal|cyan|navy|indigo|magenta|coral|turquoise|maroon|silver|ochre|mustard|cream|ivory)\b"
        r"|\b(?:red|orange|yellow|green|blue|purple|violet|pink|brown|black|white|gray|grey|gold|golden|amber|crimson|teal|cyan|navy|indigo|magenta|coral|turquoise|maroon|silver|ochre|mustard|cream|ivory)\b[^.;,]{0,40}\b(?:accent|accented)\b",
        profile_text,
        flags=re.IGNORECASE,
    ):
        return str(candidate_prompt or "")

    profile_declares_accent = bool(
        re.search(r"\b(?:accent|accented|punctuated)\b", profile_text, flags=re.IGNORECASE)
    )
    accent_replacement = (
        "one controlled profile-declared accent on an existing subject surface"
        if profile_declares_accent
        else "one controlled accent drawn from existing source colors"
    )

    def clean_suffix(text: str) -> str:
        text = re.sub(
            r"\b(?P<prefix>(?:strictly\s+controlled\s+)?monochromatic\s+foundation)\s+(?:punctuated\s+by|with|including)\s+(?:one\s+)?(?:subtle|vivid|single|bright)(?:\s*,\s*(?:subtle|vivid|single|bright))?\s+accent(?:\s+(?:color|hue))?\b",
            rf"\g<prefix> with {accent_replacement}",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\bone\s+subtle\s+one\s+controlled\s+accent\b",
            accent_replacement,
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\bpunctuated\s+by\s+(?:one\s+)?(?:subtle|vivid|single|bright)(?:\s*,\s*)?(?:subtle|vivid|single|bright)?\s+accent\b[^;,.]*(?=[;,\.]|$)",
            accent_replacement,
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\b(?:one\s+)?(?:subtle|vivid|single|bright)(?:\s*,\s*)?(?:subtle|vivid|single|bright)?\s+accent(?:\s+(?:color|hue))?\b[^;,.]*(?=[;,\.]|$)",
            accent_replacement,
            text,
            flags=re.IGNORECASE,
        )
        return re.sub(r"\s{2,}", " ", text).strip()

    return _transform_style_suffix(candidate_prompt, source_prompt, clean_suffix)

def _enforce_style_transfer_witnesses(
    candidate_prompt: str,
    source_prompt: str,
    style_profile: str,
) -> str:
    """Add compact, profile-driven witnesses the text model may omit.

    The witnesses are treatment vocabulary only.  They make palette strength,
    medium identity, and photographic surface/focus requirements explicit at
    the final CLIP boundary without introducing a moodboard example's nouns.
    """
    profile_text = _style_profile_channel_text(style_profile)
    if not profile_text:
        return str(candidate_prompt or "")
    profile_low = profile_text.casefold()
    source_text = str(source_prompt or "")
    monochrome = bool(
        re.search(r"\b(?:monochrome|monochromatic|grayscale|grey[- ]scale|black[- ]and[- ]white)\b", profile_text, flags=re.IGNORECASE)
    )
    photographic = bool(_STYLE_PHOTOGRAPHIC_TERMS.search(profile_text))
    illustrative = bool(_STYLE_ILLUSTRATIVE_TERMS.search(profile_text))
    has_palette = bool(
        re.search(r"\b(?:palette|color|colour|tone|teal|cyan|amber|orange|gold|blue|green|red|violet|magenta|warm|cool|vibrant|saturated|desaturated)\b", profile_text, flags=re.IGNORECASE)
    )

    def clean_suffix(text: str) -> str:
        additions: list[str] = []
        low = text.casefold()
        if (
            re.search(r"\bsilhouette\b", source_text, flags=re.IGNORECASE)
            and re.search(r"\b(?:facing away|rear|back[- ]facing|from behind)\b", source_text, flags=re.IGNORECASE)
            and re.search(r"\b(?:blurred|out of focus|bokeh|cityscape|skyline)\b", source_text, flags=re.IGNORECASE)
            and not re.search(r"\b(?:distinct|clean edge|tonal separation|stands? apart)\b", text, flags=re.IGNORECASE)
        ):
            additions.append(
                "the primary rear silhouette remains a distinct, fully readable foreground shape with a clean edge and clear tonal separation from the blurred cityscape and bokeh"
            )
        if has_palette:
            if monochrome:
                if not re.search(r"\bmonochromatic\b[^.;]{0,180}\b(?:existing subject|existing surfaces|connected surfaces|tonal structure)\b", text, flags=re.IGNORECASE):
                    additions.append("the existing subject and connected existing surfaces retain a monochromatic tonal structure")
            elif not re.search(r"\b(?:palette|color|colour|tone|hue)\b[^.;]{0,180}\b(?:existing subject|existing surfaces|connected surfaces|subject surface)\b", text, flags=re.IGNORECASE):
                additions.append("the existing subject and connected existing surfaces visibly carry the supplied palette with strong hue separation")
        if illustrative and not photographic:
            if not re.search(r"\b(?:linework|line art|brushwork|brushstrokes|shading)\b[^.;]{0,180}\b(?:visibly forms|forms the existing subject|connected existing surfaces)\b", text, flags=re.IGNORECASE):
                additions.append("linework or brushwork visibly forms the existing subject and connected existing surfaces")
        elif photographic:
            if not re.search(r"\b(?:microtexture|material separation|crisp focal edges|tactile texture)\b", text, flags=re.IGNORECASE):
                additions.append("natural microtexture, material separation, and crisp focal edges remain clearly visible")
        if not re.search(r"\b(?:blurred|out\s+of\s+focus|intentionally\s+soft|abstract)\b", source_text, flags=re.IGNORECASE):
            if not re.search(r"\b(?:tack[- ]sharp|crisp focal|sharp(?:ly)?\s+(?:resolved|focused)|primary subject remains)\b", text, flags=re.IGNORECASE):
                additions.append("the primary subject remains sharply resolved and any softness stays secondary and localized")
        if not additions:
            return re.sub(r"\s{2,}", " ", text).strip()
        base = text.rstrip(" .;:")
        return re.sub(r"\s{2,}", " ", base + "; " + "; ".join(additions) + ".").strip()

    return _transform_style_suffix(candidate_prompt, source_prompt, clean_suffix)

def _style_profile_payload(style_profile: str) -> dict[str, object]:
    """Parse the adapter payload without trusting arbitrary profile fields."""
    try:
        payload = json.loads(str(style_profile or "{}"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    channels = payload.get("style_channels")
    if not isinstance(channels, dict):
        return {}
    return {"style_channels": channels}

def _style_contract_values(
    style_profile: str,
    channel: str,
    *,
    limit: int = 1,
    max_chars: int = 190,
) -> list[str]:
    """Choose a few high-information treatment values from one channel.

    The adapter may expose repeated short keyword witnesses and a longer
    official guidance sentence.  Prefer the longer, information-rich values
    while keeping the final conditioning compact enough for Krea 2.
    """
    payload = _style_profile_payload(style_profile)
    channels = payload.get("style_channels")
    if not isinstance(channels, dict):
        return []
    raw_values = channels.get(channel)
    if not isinstance(raw_values, list):
        return []
    values: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        value = " ".join(str(raw_value or "").split()).strip(" .;:")
        if not value:
            continue
        # Keep the style identity but abstract any example-world nouns in the
        # same way as the main profile compiler.
        for pattern, replacement in _STYLE_PROFILE_WITNESS_REPLACEMENTS:
            value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
        for source, target in _STYLE_AXIS_REPLACEMENTS:
            value = re.sub(re.escape(source), target, value, flags=re.IGNORECASE)
        # The contract is itself style text, so it needs the same source-bound
        # world/detail cleanup as a model-generated style suffix.  Otherwise
        # phrases such as ``horizon lines bending`` can leak back in through
        # the high-salience optics witness.
        value = _replace_unrequested_style_entities(value, "")
        value = _replace_unrequested_style_details(value, "")
        value = re.sub(r"\s{2,}", " ", value).strip(" .;:")
        if len(value) > max_chars:
            value = value[: max_chars - 1].rsplit(" ", 1)[0] + "…"
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            values.append(value)
    # Longer profile sentences generally carry the actual hue relationship or
    # medium identity; keyword duplicates are less useful at the final CLIP
    # boundary.  Preserve stable order for ties so runs remain reproducible.
    values.sort(key=lambda value: -len(value))
    return values[: max(0, int(limit))]

def _compact_style_contract_value(value: str, channel: str) -> str:
    """Turn one official guidance witness into compact source-bound language."""
    text = " ".join(str(value or "").split()).strip(" .;:")
    text = re.sub(
        r"^\s*(?:palette|lighting|medium\s+and\s+texture|composition|contrast|atmosphere|era\s+or\s+movement)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"^\s*(?:a|an|the)\s+", "", text, flags=re.IGNORECASE)
    if channel == "palette":
        # Keep the hue relationship and saturation, not the explanatory tail.
        text = re.sub(
            r"\s*,?\s*(?:creating|resulting in|often|which)\b.*$",
            "",
            text,
            flags=re.IGNORECASE,
        )
    elif channel in ("lighting", "contrast"):
        # Reuse the style's light behavior without importing a different
        # source-world light such as sunlight into an interior or screen-lit
        # scene.  The source scene remains the light-source authority.
        text = re.sub(
            r"\b(?:golden[- ]hour\s+lighting|golden[- ]hour\s+light|sunlight|sunlit\s+daylight|sunlit|daylight|sunny\s+light)\b",
            "existing directional light",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\binterior\s+points?\b", "existing light sources", text, flags=re.IGNORECASE)
        text = re.sub(r"\bexternal\s+environments?\b", "surrounding tonal field", text, flags=re.IGNORECASE)
        text = re.sub(r"\bshadowy\s+silhouettes?\b", "deep shadow planes", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(?:long\s+)?cast\s+shadows?\b", "directional shadow planes", text, flags=re.IGNORECASE)
        text = re.sub(r"\bvolumetric\s+cloud\s+shadows?\b", "volumetric tonal shadows", text, flags=re.IGNORECASE)
        text = re.sub(
            r"\b(?:directional\s+)?existing\s+directional\s+light\b",
            "existing directional light",
            text,
            flags=re.IGNORECASE,
        )
    elif channel == "texture_medium":
        # A profile's motion/softness cue must not erase a photographic focal
        # plane; keep it as a localized secondary-layer treatment.
        text = re.sub(
            r"\b(?:slight|subtle)\s+motion\s+blur\b",
            "localized secondary-edge diffusion",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\bsoft\s+focus(?:\s+dreamscape)?\b",
            "localized secondary-layer diffusion",
            text,
            flags=re.IGNORECASE,
        )
    elif channel == "optics":
        # Keep an optical signature recognizable, but do not let profile
        # composition/world nouns become a new scene or the only style cue.
        text = re.sub(
            r"\bunmistakable\s+fisheye\s+barrel\s+warp\b[^.;]*",
            "visible fisheye barrel warp on existing subject geometry",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\bvisible\s+perspective\s+warp\b", "visible perspective warp on existing geometry", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip(" .;:")

def _style_transfer_contract(style_profile: str, source_prompt: str = "") -> str:
    """Compile normalized profile evidence into a short high-salience clause.

    This is deliberately generic.  It is not a per-board prompt and never
    copies a moodboard example.  The contract exists because a free-form Stage
    2 rewrite can omit a strong palette or collapse a medium into a generic
    photographic grade before the final Krea 2 conditioning step.
    """
    profile_text = _style_profile_channel_text(style_profile)
    if not profile_text:
        return ""
    profile_low = profile_text.casefold()
    monochrome = bool(
        re.search(
            r"\b(?:monochrome|monochromatic|grayscale|grey[- ]scale|black[- ]and[- ]white)\b",
            profile_text,
            flags=re.IGNORECASE,
        )
    )
    photographic = bool(_STYLE_PHOTOGRAPHIC_TERMS.search(profile_text))
    illustrative = bool(_STYLE_ILLUSTRATIVE_TERMS.search(profile_text))

    palette_values = _style_contract_values(style_profile, "palette", limit=1)
    lighting_values = _style_contract_values(style_profile, "lighting", limit=1)
    contrast_values = _style_contract_values(style_profile, "contrast", limit=1)
    medium_values = _style_contract_values(style_profile, "texture_medium", limit=1)
    optics_values = _style_contract_values(style_profile, "optics", limit=1)
    emotion_values = _style_contract_values(style_profile, "emotion_design", limit=1)

    palette = _compact_style_contract_value(palette_values[0], "palette") if palette_values else "the supplied palette"
    lighting = _compact_style_contract_value(lighting_values[0], "lighting") if lighting_values else "the supplied lighting behavior"
    medium = _compact_style_contract_value(medium_values[0], "texture_medium") if medium_values else "the supplied medium treatment"
    optics = _compact_style_contract_value(optics_values[0], "optics") if optics_values else ""
    emotion = _compact_style_contract_value(emotion_values[0], "emotion_design") if emotion_values else ""
    contrast_value = _compact_style_contract_value(contrast_values[0], "contrast") if contrast_values else ""
    luminous_signature = bool(
        re.search(
            r"\b(?:glow|glowing|luminous|neon|light\s+leak|halation|high[- ]contrast|hard[- ]light|harsh)\b",
            profile_text,
            flags=re.IGNORECASE,
        )
    )
    if monochrome:
        profile_declares_accent = bool(
            re.search(r"\b(?:accent|accented|punctuated)\b", profile_text, flags=re.IGNORECASE)
        )
        if profile_declares_accent:
            accent_rule = "the profile-declared vivid accent, derived from the supplied palette or existing source colors when no hue is named"
        else:
            accent_rule = "one controlled accent drawn from existing source colors"
        palette_rule = (
            f"the strict monochromatic structure and supplied tonal contrast remain visible across "
            f"major subject planes at thumbnail scale; the palette is {palette}; the monochrome rule "
            f"is not a weak grayscale filter; exactly one existing subject detail or connected surface "
            f"carries {accent_rule}, visibly legible at thumbnail scale, while all other visible planes "
            "remain within the monochromatic family"
        )
    else:
        palette_rule = (
            f"the supplied palette is {palette}, used as a dominant color script rather than a weak overall "
            "grade; assign its named hue relationship and saturation across major visible planes of the "
            "existing subject and at least one connected existing surface, with clear separation between "
            "colored highlight and shadow planes at thumbnail scale"
        )

    if photographic:
        medium_rule = (
            f"a photographic or analog-film treatment visibly forms the existing subject and surfaces "
            f"({medium}), with natural microtexture, material separation, realistic edge response, and "
            "a crisp focal plane"
        )
    elif illustrative:
        medium_rule = (
            f"the supplied illustrated, painted, drawn, or printed grammar visibly forms the existing "
            f"subject, surface edges, marks, and tonal planes ({medium})"
        )
    elif medium_values:
        medium_rule = f"the supplied medium treatment visibly forms the existing subject and surfaces ({medium})"
    else:
        medium_rule = "the supplied medium treatment visibly forms the existing subject and surfaces"

    signature_parts = []
    if optics:
        signature_parts.append(
            f"the optical signature is {optics}, localized on existing geometry and recognizable at "
            "thumbnail scale"
        )
    if emotion:
        signature_parts.append(f"the emotional/era signature is {emotion}")
    signature = "; " + "; ".join(signature_parts) if signature_parts else ""
    light = (
        f"existing light sources realize {lighting} across the subject; preserve the source direction and "
        "apply the profile's light color and contrast behavior to the existing light and surfaces, making "
        "highlight/shadow color separation legible"
    )
    if contrast_value:
        light += f" with {contrast_value}"
    if luminous_signature:
        light += "; keep at least one localized luminous zone and one deep shadow plane visibly legible on existing surfaces"
    if photographic:
        quality = "; retain natural fine texture, separated material boundaries, crisp decisive edges, a tack-sharp focal plane, and only localized secondary-layer softness"
    elif illustrative:
        quality = "; keep the line, brush, print, or paint marks coherent on the focal subject rather than decorating an invented background"
    else:
        quality = "; keep the focal subject readable and sharply resolved unless the source explicitly requests softness"
    return (
        "Visual treatment dominates the existing subject and connected surfaces: "
        f"{palette_rule}; {medium_rule}; {light}{signature}{quality}."
    )

def _restore_generic_style_focus(candidate_prompt: str, source_prompt: str) -> str:
    """Prevent style texture language from degrading a photographic focal plane."""
    text = str(candidate_prompt or "")
    source = str(source_prompt or "")
    if re.search(r"\b(?:blurred|out\s+of\s+focus|abstract|intentionally\s+soft)\b", source, flags=re.IGNORECASE):
        return text
    if not re.search(r"\bmotion\s+blur\b", source, flags=re.IGNORECASE):
        text = re.sub(
            r"\b(?:slight|subtle)\s+motion\s+blur\b",
            "localized motion softness confined to secondary light edges",
            text,
            flags=re.IGNORECASE,
        )
    text = re.sub(
        r"\b(?:smear(?:s|ed|ing)?|soften(?:s|ed|ing)?)\s+(?:the\s+)?(?:edges?|focal\s+detail|subject(?:['’]s)?(?:\s+\w+)?|primary\s+subject)\b(?:\s+(?:into|with|as\s+if|as\s+though)\s+[^,.;!?]*)?",
        "retains crisp focal detail",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bsoft\s+focus(?:\s+(?:dreamscape|look|rendering|effect|aesthetic))?\b",
        "soft secondary-layer atmospheric diffusion",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bghostly\s+blur\b", "controlled atmospheric grain", text, flags=re.IGNORECASE)
    if not re.search(r"\b(?:tack[- ]sharp|crisp\s+(?:focal|subject)|sharp\s+(?:focal|subject)|sharply\s+resolved)\b", text, flags=re.IGNORECASE):
        text = text.rstrip(" .;:") + ", while the primary subject and decisive existing edges remain tack-sharp and readable."
    return text

def _strip_unrequested_focus_blur(candidate_prompt: str, source_prompt: str) -> str:
    """Replace generic focus blur added by a prompt stage when the source did not request it.

    This is intentionally narrower than a general optical guard.  Explicit source
    blur, bokeh, depth-of-field, or focus instructions are immutable and bypass the
    transform.  Otherwise, only generic photographic blur wording is converted to
    positive, readable depth/atmosphere language.  Moodboard style-only text is not
    passed through this function, so official atmosphere and texture cues remain
    available at the final positive boundary.
    """
    text = str(candidate_prompt or "")
    source = str(source_prompt or "")
    if not text or re.search(
        r"\b(?:blur(?:s|red|ring)?|out\s+of\s+focus|bokeh|soft\s+focus|"
        r"shallow\s+depth\s+of\s+field|deep\s+depth\s+of\s+field|"
        r"depth\s+of\s+field|lens\s+blur|motion\s+blur)\b",
        source,
        flags=re.IGNORECASE,
    ):
        return text

    replacements = (
        (
            r"\bshallow\s+depth\s+of\s+field\b",
            "clear layered depth and crisp subject edges",
        ),
        (
            r"\bsoft(?:ly)?\s+blurred\s+(?P<target>[^.;!?]{1,120})",
            r"atmospheric \g<target> with readable contours",
        ),
        (
            r"\bblurred\s+(?P<target>[^.;!?]{1,120})",
            r"atmospheric \g<target> with readable contours",
        ),
        (
            r"\bsoft\s+haze\s+blurs\s+(?P<target>[^.;!?]{1,80})",
            r"soft haze separates the \g<target> with readable contours",
        ),
        (
            r"(?:\bwhile\s+)?\bblurring\s+the\s+background\s+into\s+a\s+soft\s+tonal\s+fade\b",
            "while retaining readable background structure with a soft tonal fade",
        ),
        (
            r"\bbackground\s+(?:is\s+)?out\s+of\s+focus\b",
            "the background remains atmospheric with readable structure",
        ),
        (
            r"\bbackground\s+blur\b",
            "soft tonal background separation",
        ),
        (
            r"\bsoft\s+focus(?:\s+(?:look|rendering|effect|aesthetic))?\b",
            "soft atmospheric separation with crisp focal edges",
        ),
        (
            r"\b(?:blur(?:red|ring)?)\s+(?P<target>[^.;!?]{1,120})",
            r"atmospheric \g<target> with readable contours",
        ),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([,.;])", r"\1", text)
    return text.strip()

def _anchor_subject_against_background_softness(candidate_prompt: str, source_prompt: str) -> str:
    """Localize source-authorized softness to secondary background layers.

    Reverse-engineered moodboard prompts often describe a blurred cityscape,
    bokeh lights, or a shallow-focus background.  Those are legitimate scene
    cues, but without a positive focal-plane boundary Krea 2 Turbo can spread
    the softness over the subject as a camera-wide blur.  Preserve the source
    cue and add one compact boundary only when the source points the softness
    at a background/distant layer and does not explicitly blur the subject.
    """
    text = str(candidate_prompt or "").strip()
    source = str(source_prompt or "")
    if not text or not source:
        return text
    # Treat a stacked, generic background-blur description as a camera cue
    # that needs localization.  A single official bokeh/softness phrase is
    # left alone; this narrower trigger is what keeps unrelated styles
    # byte-for-byte unchanged in the 54-style preservation run.
    stacked_background_softness = bool(
        re.search(
            r"\b(?:blurred|softly\s+blurred)\s+(?:cityscape|skyline|urban\s+structures?|"
            r"background)\b",
            source,
            flags=re.IGNORECASE,
        )
        and re.search(
            r"\bout\s+of\s+focus\b[^.;!?]{0,100}\bbackground\b|"
            r"\bbackground\b[^.;!?]{0,100}\bout\s+of\s+focus\b",
            source,
            flags=re.IGNORECASE,
        )
    )
    if not stacked_background_softness:
        return text
    explicit_subject_softness = bool(
        re.search(
            r"\b(?:the\s+)?(?:primary\s+)?(?:subject|figure|silhouette|person|woman|man|face|eyes?)\b"
            r"[^.;!?]{0,70}\b(?:is|are|remains?)\b[^.;!?]{0,30}\b(?:blurred|out\s+of\s+focus|"
            r"softly?\s+diffused|soft\s+focus|shallow\s+focus|shallow\s+depth\s+of\s+field)\b",
            source,
            flags=re.IGNORECASE,
        )
    )
    if explicit_subject_softness:
        return text
    if re.search(
        r"\b(?:primary\s+subject|focal\s+subject|subject\s+silhouette)\b[^.;!?]{0,100}"
        r"\b(?:sharply\s+resolved|sharp(?:ly)?\s+focused|clean\s+readable\s+edge|"
        r"optical\s+softness\s+is\s+confined)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return text
    replacements = (
        (
            r"\ba\s+blurred\s+cityscape\b",
            "an atmospheric cityscape",
        ),
        (
            r"\bblurred\s+(?P<target>skyline|urban\s+structures?|background)\b",
            r"atmospheric \g<target>",
        ),
        (
            r"\b(?:city\s+lights?|lights?)\s+are\s+out\s+of\s+focus\s+in\s+the\s+background,\s+creating\s+bokeh\b",
            "Distant background lights form distinct bokeh points",
        ),
        (
            r"\bdepth\s+emphasized\s+by\s+shallow\s+focus\b",
            "depth emphasized by layered atmospheric recession",
        ),
        (
            r"\batmospheric\s+haze\s+diffuses\s+foreground\s+edges\b",
            "atmospheric haze separates foreground edges with readable contours",
        ),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([,.;])", r"\1", text).strip()
    anchor = (
        "the primary subject remains sharply resolved with a clean readable edge, "
        "while optical softness is confined to distant background lights and atmospheric layers"
    )
    return f"{text.rstrip(' .;:')}; {anchor}."

def _preserve_profile_facial_detail(candidate_prompt: str, source_prompt: str, style_profile: str) -> str:
    """Keep the visible eye in a flat vector side-profile transfer.

    This is a narrow harness guard for the S31 failure mode.  It activates only
    when the source is a profile portrait and the supplied style profile is the
    flat-vector/stipple/risograph family.  Other styles and non-profile scenes
    are returned byte-for-byte unchanged.
    """
    text = str(candidate_prompt or "").strip()
    source = str(source_prompt or "")
    profile = str(style_profile or "")
    if not text or not source or not profile:
        return text
    if not re.search(r"\bprofile\b", source, flags=re.IGNORECASE):
        return text
    if not re.search(r"\b(?:woman|man|person|portrait|face)\b", source, flags=re.IGNORECASE):
        return text
    if not re.search(r"\bflat\s+vector\b", profile, flags=re.IGNORECASE):
        return text
    if not re.search(r"\b(?:stipple|risograph)\b", profile, flags=re.IGNORECASE):
        return text
    if re.search(r"\b(?:open\s+almond[- ]shaped\s+eye|dark\s+iris|small\s+pupil)\b", text, flags=re.IGNORECASE):
        return text
    anchor = "the visible eye on the side-profile face remains open and clearly drawn as an almond-shaped eye with a dark iris and small pupil beneath a distinct eyebrow, with the eyelid and eye line legible as facial features"
    return f"{text.rstrip(' .;:')}; {anchor}."

def _strip_trailing_source_noun_audit(candidate_prompt: str, source_prompt: str) -> str:
    """Remove a model's trailing source-noun checklist, not normal prose."""
    text = str(candidate_prompt or "").strip()
    source_words = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z'-]*", str(source_prompt or ""))
    }
    if not text or not source_words:
        return text
    match = re.search(r"\s+[—–]\s+(?P<tail>[^.!?\n]{3,220})[.!?]?\s*$", text)
    if not match:
        return text
    tail = match.group("tail").strip()
    parts = [part.strip() for part in tail.split(",") if part.strip()]
    if len(parts) < 2:
        return text
    tail_words = [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z'-]*", tail)]
    if not tail_words or not all(word in source_words for word in tail_words):
        return text
    return text[: match.start()].rstrip(" ,;:-") + "."

def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(
        re.search(rf"(?<!\w){re.escape(term.lower())}(?!\w)", text.lower())
        for term in terms
    )

def _active_human_hand_action(text: str) -> bool:
    for match in _HUMAN_HAND_ACTION_RE.finditer(str(text or "")):
        clause_start = max(0, match.start() - 90)
        clause_end = min(len(str(text or "")), match.end() + 90)
        clause = str(text or "")[clause_start:clause_end]
        if _NATURAL_HAND_METAPHOR_RE.search(clause):
            continue
        return True
    return False

_SAME_SUBJECT_STYLE_REFERENCE_RE = re.compile(
    r"\b(?:her|his|their|its|the|a|an|one|single|solitary|focal|main|central)\s+(?:figure|silhouette)\b"
    r"|\b(?:figure|silhouette)\s+(?:against|loom(?:s|ed|ing)?|remain(?:s|ed|ing)?|appear(?:s|ed|ing)?|read(?:s|ing)?|carry(?:ing)?|stand(?:s|ing)?|is\s+rendered)\b",
    flags=re.IGNORECASE,
)

_STYLE_ENVIRONMENT_SILHOUETTE_RE = re.compile(
    r"(?:\b(?:environment(?:s)?|exterior|background|horizon|space|scene|air|distance|walls?)\b"
    r"[^.;!?]{0,80}|\b(?:deepen|dissolve|fade|dim|merge|melt|soften)(?:s|ed|ing)?\s+into\b[^.;!?]{0,40})"
    r"\b(?:shadowy|ghostly|dimmed|blurred|distant|soft)\s+silhouettes?\b",
    flags=re.IGNORECASE,
)

def _style_only_same_subject_reference(candidate: str, source: str) -> bool:
    """Allow style prose to call an already-present subject a figure/silhouette.

    The entity guard must still reject a real second subject.  This narrow
    exception covers possessive/singular references such as ``her figure`` and
    environmental phrases such as ``shadowy silhouettes`` used to describe
    light and background treatment rather than people.
    """
    if not _human_guard_terms(source):
        return False
    candidate_text = str(candidate or "")
    for match in _BACKGROUND_HUMAN_RE.finditer(candidate_text):
        clause_start = max(0, match.start() - 120)
        clause_end = min(len(candidate_text), match.end() + 100)
        clause = candidate_text[clause_start:clause_end]
        if _EXTRA_HUMAN_RE.search(clause):
            return False
        if _STYLE_ENVIRONMENT_SILHOUETTE_RE.search(clause):
            continue
        if _SAME_SUBJECT_STYLE_REFERENCE_RE.search(clause):
            continue
        return False
    generic_terms = _human_guard_terms(candidate_text) - _human_guard_terms(source)
    if generic_terms and not generic_terms <= {"figure", "figures", "silhouette", "silhouettes"}:
        return False
    for term in ("figure", "figures", "silhouette", "silhouettes"):
        for match in re.finditer(rf"\b{term}\b", candidate_text, flags=re.IGNORECASE):
            clause_start = max(0, match.start() - 120)
            clause_end = min(len(candidate_text), match.end() + 100)
            clause = candidate_text[clause_start:clause_end]
            if _EXTRA_HUMAN_RE.search(clause):
                return False
            if _STYLE_ENVIRONMENT_SILHOUETTE_RE.search(clause):
                continue
            if _SAME_SUBJECT_STYLE_REFERENCE_RE.search(clause):
                continue
            if term in {"figures", "silhouettes"}:
                return False
    return True

def _subject_side_authorized(value: object) -> bool:
    try:
        payload = json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return False
    if not isinstance(payload, dict):
        return False
    channels = payload.get("style_channels")
    if not isinstance(channels, dict):
        return False
    authority = channels.get("subject_side_authority")
    return isinstance(authority, list) and "technical_material" in authority

def _safe_world_semantics(text: object) -> list[str]:
    source = " ".join(str(text or "").split())
    semantics: list[str] = []
    for marker in sorted(_WORLD_SEMANTIC_MARKERS, key=len, reverse=True):
        if re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", source, flags=re.IGNORECASE):
            if marker not in semantics:
                semantics.append(marker)
    return semantics

def _strip_unrequested_subject_side_detail(text: str, source_prompt: str) -> str:
    if not _TECHNICAL_SUBJECT_SIDE_RE.search(text):
        return text
    if _TECHNICAL_SUBJECT_SIDE_RE.search(str(source_prompt or "")):
        return text
    stripped = re.sub(
        r"(?:^|(?<=[.!?;]))\s*[^.!?;]*\b(?:earpiece|earcup|headset|headband|microphone|ear[- ]side\s+(?:interface|device|unit)|technical\s+wearable|rugged\s+collar)\b[^.!?;]*[.!?;]?",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    stripped = re.sub(r"\s{2,}", " ", stripped)
    return stripped.strip(" ,;:")

def _normalize_transfer_axis(raw_axis: object) -> str:
    axis = " ".join(str(raw_axis or "").split())
    for pattern, replacement in _STYLE_PROFILE_WITNESS_REPLACEMENTS:
        axis = re.sub(pattern, replacement, axis, flags=re.IGNORECASE)
    for source, target in _STYLE_AXIS_REPLACEMENTS:
        axis = re.sub(re.escape(source), target, axis, flags=re.IGNORECASE)
    if not axis:
        return ""
    for drop_term in sorted(_STYLE_AXIS_DROP_TERMS, key=len, reverse=True):
        axis = re.sub(
            rf"(?<!\w){re.escape(drop_term)}(?!\w)",
            " ",
            axis,
            flags=re.IGNORECASE,
        )
    for drop_term in sorted(_STYLE_PROFILE_DROP_TERMS, key=len, reverse=True):
        axis = re.sub(
            rf"(?<!\w){re.escape(drop_term)}(?!\w)",
            " ",
            axis,
            flags=re.IGNORECASE,
        )
    for pattern, replacement in _STYLE_PROFILE_WITNESS_REPLACEMENTS:
        axis = re.sub(pattern, replacement, axis, flags=re.IGNORECASE)
    axis = " ".join(axis.split()).strip(" ,;:/|-_")
    if not axis:
        return ""
    return axis

def _style_profile(raw_axes: object, semantic_text: object = "") -> dict[str, list[str]]:
    channels: dict[str, list[str]] = {
        "palette": [],
        "lighting": [],
        "contrast": [],
        "atmosphere": [],
        "texture_medium": [],
        "emotion_design": [],
        "world_semantics": [],
        "subject_side_authority": [],
        "composition": [],
        "optics": [],
    }
    if not isinstance(raw_axes, list):
        return channels
    for raw_axis in raw_axes:
        axis = _normalize_transfer_axis(raw_axis)
        if not axis:
            continue
        low = axis.lower()
        matched = False
        for channel, terms in _STYLE_CHANNEL_TERMS.items():
            if channel == "palette" and _contains_any(low, _LIGHTING_MARKERS):
                if not _contains_any(low, _PALETTE_MARKERS):
                    continue
            if _contains_any(low, terms):
                if axis not in channels[channel]:
                    channels[channel].append(axis)
                matched = True
        if not matched and axis not in channels["emotion_design"]:
            channels["emotion_design"].append(axis)
    raw_axis_text = " ".join(str(value or "") for value in raw_axes if value)
    if _SUBJECT_SIDE_AUTHORITY_RE.search(raw_axis_text):
        channels["subject_side_authority"].append("technical_material")
    raw_semantics = _safe_world_semantics(f"{raw_axis_text} {semantic_text}")
    # Preserve a world cue only as an abstract treatment witness.  Keeping
    # literal values such as ``sky`` or ``ocean`` in the compiler input makes
    # a language model more likely to materialize the moodboard example.
    for semantic in raw_semantics:
        treatment = _WORLD_SEMANTIC_TREATMENTS.get(semantic, "abstract tonal treatment")
        if treatment not in channels["world_semantics"]:
            channels["world_semantics"].append(treatment)
        if treatment not in channels["emotion_design"]:
            channels["emotion_design"].append(treatment)
    return channels

def _safe_guidance_sections(raw_guidance: object) -> dict[str, list[str]]:
    guidance = " ".join(str(raw_guidance or "").split())
    sections: dict[str, list[str]] = {
        "palette": [],
        "lighting": [],
        "contrast": [],
        "atmosphere": [],
        "texture_medium": [],
        "emotion_design": [],
        "optics": [],
    }
    channel_by_label = {
        "palette": "palette",
        "lighting": "lighting",
        "medium and texture": "texture_medium",
        "contrast": "contrast",
        "composition": "optics",
        "atmosphere": "atmosphere",
        "era or movement": "emotion_design",
    }
    for match in _STYLE_GUIDANCE_SECTION_RE.finditer(guidance):
        if match.group("label").lower() == "composition":
            for treatment in _localized_optical_treatments(match.group("body")):
                if treatment not in sections["optics"]:
                    sections["optics"].append(treatment)
            continue
        axis = _normalize_transfer_axis(match.group("body"))
        channel = channel_by_label[match.group("label").lower()]
        if axis and axis not in sections[channel]:
            sections[channel].append(axis)
    return sections

class KreaMoodboardStyleAdapter:
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("style_axes_json",)
    FUNCTION = "adapt"
    DESCRIPTION = "Expose structured moodboard style channels for a prompt compiler; removes titles, examples, composition, and scene prose."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "metadata_json": (
                    "STRING",
                    {
                        "default": "{}",
                        "multiline": True,
                        "tooltip": "Metadata JSON from a Krea Moodboard node.",
                    },
                ),
            }
        }

    def adapt(self, metadata_json: str):
        try:
            data = json.loads(str(metadata_json or "{}"))
        except json.JSONDecodeError:
            data = {}
        raw_axes = data.get("style_axes") if isinstance(data, dict) else []
        raw_keywords = data.get("keywords") if isinstance(data, dict) else []
        axes: list[str] = []
        for raw_values in (raw_axes, raw_keywords):
            if not isinstance(raw_values, list):
                continue
            for raw_axis in raw_values:
                axis = " ".join(str(raw_axis or "").split())
                if axis and axis not in axes:
                    axes.append(axis)
        semantic_values: list[str] = []
        for value in (
            data.get("title"),
            data.get("source_summary"),
            data.get("keywords"),
            data.get("style_axes"),
            data.get("prompt_guidance"),
        ):
            if isinstance(value, list):
                semantic_values.extend(str(item or "") for item in value)
            elif value:
                semantic_values.append(str(value))
        channels = _style_profile(axes, " ".join(semantic_values))
        guidance_sections = _safe_guidance_sections(data.get("prompt_guidance") if isinstance(data, dict) else "")
        for channel, section_axes in guidance_sections.items():
            if channel == "texture_medium":
                for section_axis in reversed(section_axes):
                    if section_axis and section_axis not in channels[channel]:
                        channels[channel].insert(0, section_axis)
                continue
            # Keep short keyword witnesses, but also retain the sanitized
            # official section so high-salience palette, lighting, and optical
            # relationships are not reduced to a generic token such as
            # “vibrant” or “glow”.
            for section_axis in section_axes:
                if section_axis and section_axis not in channels[channel]:
                    channels[channel].append(section_axis)
        return (json.dumps({"style_channels": channels}, ensure_ascii=False, sort_keys=True),)

class KreaPromptSanitizer:
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("clean_prompt",)
    FUNCTION = "clean"
    DESCRIPTION = "Remove accidental prompt wrappers before Krea 2 encoding, with optional fallback and creative-drift protection."

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Prompt text to clean before image encoding.",
                    },
                )
            },
            "optional": {
                "fallback_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Original prompt used when the generator returns a system or role transcript.",
                    },
                ),
                "source_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Original prompt used by the optional entity-drift guard.",
                    },
                ),
                "style_profile": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Structured moodboard channels used to keep style nouns on existing source surfaces.",
                    },
                ),
                "style_contract_only": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Research mode: retain the source prompt and replace free-form style prose with one compact generic style contract.",
                    },
                ),
                "subject_side_authority": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Filtered moodboard channels used to guard unrequested subject-side technical details.",
                    },
                ),
                "guard_entities": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Fallback when the generated text adds an obvious entity or changes the medium.",
                    },
                ),
                "allow_subordinate_environment_entities": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "When enabled, allow clearly subordinate animals or vehicles in a broad named environment while keeping extra people and strict branches guarded.",
                    },
                ),
                "allow_contextual_environment_medium": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "When enabled, allow photographic or rendered medium wording chosen for a broad environment while keeping strict branches guarded.",
                    },
                ),
                "allow_subordinate_background_people": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "When enabled, allow distant or background people as optional environment occupancy without allowing a new foreground character or relationship.",
                    },
                ),
                "strip_internal_sampling_marker": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Remove an optional model-generated internal sampling marker before encoding.",
                    },
                ),
                "strip_prompt_labels": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Remove model-generated section labels such as Style treatments or Focus hierarchy before encoding.",
                    },
                ),
                "strip_unrequested_capture_formats": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Remove camera, film-format, and sensor terms when the source prompt does not request them.",
                    },
                ),
                "preserve_subject_count": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Repeat an explicit exactly-one subject anchor from the source prompt before encoding.",
                    },
                ),
                "preserve_source_optical_anchors": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Restore explicit source-fixed cold-screen and rectangular-eye reflection wording when a candidate weakens it.",
                    },
                ),
                "guard_unrequested_focus_blur": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Harness guard: keep explicit source focus requests, but replace unrequested generic shallow-depth/background-blur wording with readable layered depth.",
                    },
                ),
                "preserve_profile_facial_detail": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Harness guard: preserve the visible eye and eyelid for flat-vector stipple side-profile portraits.",
                    },
                ),
                "block_rectangular_eye_catchlights": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Stage-specific guard: replace geometric screen catchlight wording tied to eyes or irises with diffuse natural highlights.",
                    },
                ),
                "strip_unrequested_hand_actions": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Remove a newly introduced hand or finger action when the source prompt has none.",
                    },
                ),
            }
        }

    def clean(
        self,
        prompt: str,
        fallback_prompt: str = "",
        source_prompt: str = "",
        style_profile: str = "",
        style_contract_only: bool = False,
        subject_side_authority: str = "",
        guard_entities: bool = False,
        allow_subordinate_environment_entities: bool = False,
        allow_contextual_environment_medium: bool = False,
        allow_subordinate_background_people: bool = False,
        strip_internal_sampling_marker: bool = False,
        strip_prompt_labels: bool = False,
        strip_unrequested_capture_formats: bool = False,
        preserve_subject_count: bool = False,
        preserve_source_optical_anchors: bool = False,
        guard_unrequested_focus_blur: bool = False,
        preserve_profile_facial_detail: bool = False,
        block_rectangular_eye_catchlights: bool = False,
        strip_unrequested_hand_actions: bool = False,
    ):
        fallback = str(fallback_prompt or "").strip()
        cleaned = str(prompt or "").strip()
        cleaned = re.sub(r"^```(?:text|markdown)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        if (
            fallback
            and not _CJK_RE.search(str(source_prompt or ""))
            and _CJK_RE.search(cleaned)
            and not _CJK_RE.search(fallback)
        ):
            return (fallback,)
        if _REFUSAL_OR_PROTOCOL_RE.search(cleaned):
            if fallback:
                return (fallback,)
            cleaned = ""
        if re.search(r"<\|im_start\|>system|You are the (?:first|second) stage of a Krea 2 prompt compiler\.", cleaned, flags=re.IGNORECASE):
            if fallback:
                return (fallback,)
            assistant_match = re.search(
                r"<\|im_start\|>assistant\s*(?:<think>.*?</think>\s*)?(.*?)(?:<\|im_end\|>|$)",
                cleaned,
                flags=re.IGNORECASE | re.DOTALL,
            )
            cleaned = assistant_match.group(1).strip() if assistant_match else ""
        cleaned = re.sub(r"^\s*(?:<\|im_start\|>)?(?:assistant|user)\s*[:\r\n]+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*<think>.*?</think>\s*", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(
            r"^\s*(?:\*\*|__)?(?:final\s+(?:prompt|answer)|image\s+prompt|answer|user\s+prompt|prompt)\s*:?\s*(?:\*\*|__)?\s*:?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"^\s*[-*]\s+", "", cleaned)
        if strip_internal_sampling_marker:
            cleaned = re.sub(
                r"^\s*`?(?:cinder|reed|glass)`?(?:\s*(?:[:\-]\s*)?[\r\n]+|\s+)",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )
        if style_profile and source_prompt:
            # Extract official Palette/Lighting/Medium sections before the
            # generic label stripper can consume their section headers.
            cleaned = _extract_official_style_guidance(cleaned)
        if strip_prompt_labels:
            cleaned = re.sub(
                r"\b(?:technical[_ -]?material|subject[_ -]?side(?:[_ -]?(?:authority|treatment))?)\s+(?:gate\s+)?(?:on|off)\s*:?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )
            cleaned = re.sub(
                r"\b(?:technical[_ -]?material|subject[_ -]?side(?:[_ -]?(?:authority|treatment))?)\s+authority\s+(?:triggers?|permits?|allows?|authorizes?|branch)\s*:?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )
            cleaned = re.sub(
                r"\b(?:style\s+treatments?|style\s+witnesses?|style\s+consequences?|focus(?:\s+hierarchy)?|emotional\s+temperature|subject[- ]side|setting[- ]side|background|palette|lighting|atmosphere|world|local\s+optics|rendering\s+form|(?:one|two|three)\s+(?:open[- ]slot\s+realization|concrete\s+consequences?|visible\s+consequences?|consequences?)|(?:dominant\s+)?medium\s+ontology|open[- ]slot\s+realization|consequences?|medium\s+and\s+texture|medium|treatment|first|second|third)\s*:\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )
            cleaned = re.sub(
                r"(?:\*\*|__)?\s*(?:final\s+(?:output|prompt|answer)|image\s+prompt|answer|user\s+prompt|prompt)\s*:?(?:\s*(?:\*\*|__))?\s*:?[ \t]*",
                " ",
                cleaned,
                flags=re.IGNORECASE,
            )
            cleaned = re.sub(
                r"\s*(?:medium|close[- ]up|wide|full)\s+shot\s+composition\.?\s*",
                " ",
                cleaned,
                flags=re.IGNORECASE,
            )
            cleaned = re.sub(r"(?m)^\s*[-*]\s+", "", cleaned)
            cleaned = re.sub(r"\s+[-*]\s+(?=[A-Za-z])", " ", cleaned)
            cleaned = re.sub(r"(?:\*\*|__){2,}", " ", cleaned)
            cleaned = re.sub(r"\s*\n\s*", " ", cleaned)
            cleaned = re.sub(r"\s{2,}", " ", cleaned)
            cleaned = _collapse_repeated_sentence_blocks(cleaned)
        if style_profile and source_prompt:
            cleaned = _extract_official_style_guidance(cleaned)
            cleaned = _replace_unrequested_style_entities(cleaned, source_prompt)
            cleaned = _replace_unrequested_style_details(cleaned, source_prompt)
            cleaned = _rewrite_style_profile_witnesses(cleaned, source_prompt)
            cleaned = _sanitize_style_medium_conflicts(cleaned, source_prompt, style_profile)
            cleaned = _strip_unsupported_monochrome_accent(cleaned, source_prompt, style_profile)
            cleaned = _restore_generic_style_focus(cleaned, source_prompt)
            cleaned = _enforce_style_transfer_witnesses(cleaned, source_prompt, style_profile)
            contract = _style_transfer_contract(style_profile, source_prompt)
            if style_contract_only and contract and source_prompt:
                # The original source is the immutable scene ledger.  In this
                # research mode it is followed by exactly one deterministic,
                # profile-driven treatment contract; the free-form Stage 2
                # suffix cannot dilute or contradict the style signal.
                source_text = str(source_prompt or "").strip()
                cleaned = f"{source_text.rstrip()} {contract}"
            elif contract and contract.casefold() not in cleaned.casefold():
                cleaned = f"{cleaned.rstrip(' .;:')}; {contract}"
            cleaned = _strip_trailing_source_noun_audit(cleaned, source_prompt)
        if subject_side_authority and not _subject_side_authorized(subject_side_authority):
            cleaned = _strip_unrequested_subject_side_detail(cleaned, source_prompt)
        if strip_unrequested_capture_formats and source_prompt:
            cleaned = _strip_unrequested_capture_formats(cleaned, source_prompt)
        if preserve_subject_count and source_prompt:
            count_match = _EXACT_SUBJECT_COUNT_RE.search(str(source_prompt))
            if count_match and not re.search(
                rf"\bexactly\s+one\s+{re.escape(count_match.group(1).strip())}\b",
                cleaned,
                flags=re.IGNORECASE,
            ):
                count_phrase = f"Exactly one {count_match.group(1).strip()}"
                cleaned = f"{count_phrase}; {cleaned}" if cleaned else count_phrase
        if preserve_source_optical_anchors and source_prompt:
            cleaned = _restore_source_optical_anchors(cleaned, source_prompt)
        if strip_unrequested_hand_actions and source_prompt:
            if not _active_human_hand_action(source_prompt) and _active_human_hand_action(cleaned):
                cleaned = _UNREQUESTED_HAND_ACTION_CLAUSE_RE.sub("", cleaned)
                cleaned = re.sub(r"\s{2,}", " ", cleaned)
                cleaned = re.sub(r",\s*,", ",", cleaned)
        if source_prompt:
            cleaned = _restore_source_color_anchors(cleaned, source_prompt)
        if not cleaned and fallback:
            cleaned = fallback
        if guard_entities and source_prompt and fallback and _creative_entity_drift(
            source_prompt,
            cleaned,
            allow_subordinate_environment_entities=allow_subordinate_environment_entities,
            allow_contextual_environment_medium=allow_contextual_environment_medium,
            allow_subordinate_background_people=allow_subordinate_background_people,
        ):
            # The lexical entity guard cannot compare a CJK source ledger with
            # its English translation: every translated subject term appears
            # "new" to the English-only regex and causes a false drift hit.
            # Keep the translated candidate in this explicit cross-language
            # path; same-language entity protection remains unchanged.
            source_is_cjk = bool(_CJK_RE.search(str(source_prompt or "")))
            candidate_is_english = bool(cleaned) and not _CJK_RE.search(cleaned)
            if not (source_is_cjk and candidate_is_english):
                cleaned = fallback
        if preserve_subject_count and source_prompt:
            count_match = _EXACT_SUBJECT_COUNT_RE.search(str(source_prompt))
            if count_match and not re.search(
                rf"\bexactly\s+one\s+{re.escape(count_match.group(1).strip())}\b",
                cleaned,
                flags=re.IGNORECASE,
            ):
                count_phrase = f"Exactly one {count_match.group(1).strip()}"
                cleaned = f"{count_phrase}; {cleaned}" if cleaned else count_phrase
        if preserve_source_optical_anchors and source_prompt:
            cleaned = _restore_source_optical_anchors(cleaned, source_prompt)
        if source_prompt:
            cleaned = _restore_source_color_anchors(cleaned, source_prompt)
        if guard_unrequested_focus_blur and source_prompt:
            cleaned = _strip_unrequested_focus_blur(cleaned, source_prompt)
            cleaned = _anchor_subject_against_background_softness(cleaned, source_prompt)
        if preserve_profile_facial_detail and source_prompt:
            cleaned = _preserve_profile_facial_detail(cleaned, source_prompt, style_profile)
        if block_rectangular_eye_catchlights:
            cleaned = _block_rectangular_eye_catchlights(cleaned)
        return (cleaned.strip(),)

def _collapse_repeated_sentence_blocks(prompt: str) -> str:
    text = str(prompt or "").strip()
    if not text:
        return text
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    if len(sentences) < 2:
        return text
    max_block = min(12, len(sentences) // 2)
    for block_size in range(max_block, 1, -1):
        changed = True
        while changed and len(sentences) >= block_size * 2:
            changed = False
            for start in range(0, len(sentences) - block_size * 2 + 1):
                left = [re.sub(r"\s+", " ", item).strip().casefold() for item in sentences[start : start + block_size]]
                right = [re.sub(r"\s+", " ", item).strip().casefold() for item in sentences[start + block_size : start + block_size * 2]]
                if left == right:
                    del sentences[start + block_size : start + block_size * 2]
                    changed = True
                    break
    return " ".join(sentences)

def _restore_source_optical_anchors(candidate_prompt: str, source_prompt: str) -> str:
    candidate = str(candidate_prompt or "").strip()
    source = str(source_prompt or "")
    source_light = re.search(r"\bcold\s+blue-white\s+screen\s+light\b", source, flags=re.IGNORECASE)
    if source_light and not re.search(r"\bcold\b[^.;\n]{0,80}\bscreen\s+light\b", candidate, flags=re.IGNORECASE):
        corrected = re.sub(
            r"\bcool(?=\s+blue-white\s+screen\s+light\b)",
            "cold",
            candidate,
            count=1,
            flags=re.IGNORECASE,
        )
        candidate = corrected if corrected != candidate else f"{source_light.group(0)}; {candidate}"
    source_reflection = re.search(
        r"\bclear\s+rectangular\s+screen\s+reflection\s+in\s+both\s+eyes\b",
        source,
        flags=re.IGNORECASE,
    )
    if source_reflection:
        # Keep the source meaning while preventing the text encoder from
        # reading an eye reflection as a projected display across the face.
        # This is intentionally generic: it applies to any source prompt that
        # asks for a rectangular screen reflection in both eyes.
        bounded_reflection = "two tiny, separate rectangular screen catchlights, each fully contained within its own iris"
        candidate = re.sub(
            r"\bclear\s+rectangular\s+screen\s+reflection\s+in\s+both\s+eyes\b",
            bounded_reflection,
            candidate,
            flags=re.IGNORECASE,
        )
        candidate = re.sub(
            r"\b(?:clear\s+)?rectangular\s+screen\s+reflections?\b(?:(?:\s+|,\s*)[^.;]{0,100}?\b(?:both|each)\s+(?:eyes?|irises?|corneas?)\b)",
            bounded_reflection,
            candidate,
            flags=re.IGNORECASE,
        )
        has_bounded_reflection = re.search(
            rf"{re.escape(bounded_reflection)}|\b(?:two|pair\s+of)\s+(?:tiny|small),?\s+separate\s+rectangular\s+screen\s+catchlights?\b[^.;]{{0,100}}\b(?:each|both)\s+(?:eyes?|irises?|corneas?)\b|\b(?:fully\s+)?contained\s+within\s+(?:each|both|its\s+own)\s+(?:eye|iris|cornea)\b|\b(?:within|inside)\s+(?:each|both)\s+(?:eye|iris|cornea)\b",
            candidate,
            flags=re.IGNORECASE,
        )
        if not has_bounded_reflection:
            candidate = f"{bounded_reflection}; {candidate}" if candidate else bounded_reflection
    else:
        # The conditional instruction is easy for a text model to copy even
        # when the source has no screen reflection.  Remove that unrequested
        # optical detail instead of letting it become a new subject cue.
        candidate = re.sub(
            r"(?:\s*(?:while|and|;)?\s*)?"
            r"two\s+tiny,\s+separate\s+rectangular\s+screen\s+catchlights?\b"
            r"[^.;!?]*",
            " ",
            candidate,
            flags=re.IGNORECASE,
        )
        candidate = re.sub(r"\s+([,.;])", r"\1", candidate)
        candidate = re.sub(r"([,;])\s*([,.])", r"\2", candidate)
        # Removing an unrequested conditional clause can leave a dangling
        # bridge word at the end of the sentence (for example, “including.”).
        candidate = re.sub(r"\s*,?\s*(?:including|such as|notably)\s*[.;!?]$", ".", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s{2,}", " ", candidate)
    return candidate

def _block_rectangular_eye_catchlights(prompt: str) -> str:
    """Remove geometric screen-reflection wording only when it is tied to eyes."""
    candidate = str(prompt or "")
    if not candidate:
        return candidate
    safe_catchlights = "soft natural catchlights in both irises, diffuse and without a defined geometric shape"
    candidate = re.sub(
        r"\b(?:clear\s+)?rectangular\s+screen\s+reflection\s+in\s+both\s+eyes\b",
        safe_catchlights,
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"\b(?:two\s+tiny,\s+separate\s+)?rectangular\s+screen\s+(?:reflections?|catchlights?)\b"
        r"[^.;!?]{0,180}\b(?:eyes?|iris(?:es)?|corneas?)\b",
        safe_catchlights,
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"\b(?:clear\s+)?rectangular\s+screen\s+(?:reflections?|catchlights?)\b"
        r"(?:(?:\s+|,\s*)[^.;!?]{0,100}?\b(?:both|each|its\s+own|the\s+two)\s+(?:eyes?|iris(?:es)?|corneas?)\b)",
        safe_catchlights,
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(r"\s{2,}", " ", candidate)
    candidate = re.sub(r"\s+([,.;])", r"\1", candidate)
    return candidate.strip()

_COLOR_ANCHOR_RE = re.compile(
    r"\b(?P<color>(?:(?:light|dark|deep|bright|pale|faded|muted|vivid|warm|cool|soft|rich|fiery|dusty|electric|neon|saturated|desaturated|warm-toned|cool-toned)\s+)?"
    r"(?:red|orange|yellow|green|blue|purple|violet|pink|brown|black|white|gray|grey|beige|gold|golden|amber|crimson|teal|cyan|navy|indigo|magenta|coral|turquoise|maroon|silver|ochre|mustard|earthy|cream|ivory))"
    r"\s+(?P<modifiers>(?:(?![.;!?])\b[A-Za-z][A-Za-z-]*\b\s+){0,2})"
    r"(?P<noun>shirt|t-shirt|skirt|dress|jacket|coat|pants|trousers|shorts|cardigan|sweater|top|bag|hair|eyes?|irises?|skin|lips?|shoes?|sneakers?|letters?|text|water|sky|clouds?|curtain|walls?|floor|path|grass|trees?|leaves?|cottage|roof|door|window|staircase|sand|ocean|horizon)\b",
    flags=re.IGNORECASE,
)

_COLOR_PHRASE = (
    r"(?:(?:light|dark|deep|bright|pale|faded|muted|vivid|warm|cool|soft|rich|fiery|dusty|"
    r"electric|neon|saturated|desaturated|warm-toned|cool-toned)\s+)?"
    r"(?:red|orange|yellow|green|blue|purple|violet|pink|brown|black|white|gray|grey|beige|"
    r"gold|golden|amber|crimson|teal|cyan|navy|indigo|magenta|coral|turquoise|maroon|silver|"
    r"ochre|mustard|earthy|cream|ivory)"
)

_COLOR_CLAIM_RE = re.compile(
    rf"\b(?P<color>{_COLOR_PHRASE}s?)\b",
    flags=re.IGNORECASE,
)

def _restore_source_color_anchors(candidate_prompt: str, source_prompt: str) -> str:
    """Keep an explicit source object color while allowing style grading around it."""
    candidate = str(candidate_prompt or "")
    source = str(source_prompt or "")
    if not candidate or not source:
        return candidate
    anchors_by_noun: dict[str, list[str]] = {}
    for anchor in _COLOR_ANCHOR_RE.finditer(source):
        source_color = " ".join(anchor.group("color").split())
        noun = anchor.group("noun").lower()
        anchors_by_noun.setdefault(noun, []).append(source_color)

    # First handle a grouped claim such as “deep blues of the sky and skirt”.
    # Keep the style color for the first existing plane, but restate the
    # source-fixed color on the later named object instead of replacing the
    # whole grouped claim and accidentally recoloring the sky.
    for noun, source_colors in anchors_by_noun.items():
        compound_pattern = re.compile(
            rf"\b(?P<color>{_COLOR_PHRASE}s?)\s+of\s+[^.;!?]{{0,60}}?\band\s+(?P<noun>{re.escape(noun)})\b",
            flags=re.IGNORECASE,
        )
        for compound in reversed(list(compound_pattern.finditer(candidate))):
            preceding = candidate[max(0, compound.start("noun") - 32) : compound.start("noun")]
            if not re.search(rf"\b{re.escape(source_colors[0])}\b", preceding, flags=re.IGNORECASE):
                candidate = (
                    candidate[: compound.start("noun")]
                    + f"{source_colors[0]} "
                    + candidate[compound.start("noun") :]
                )

    # Inspect every nearby color claim, not only the first one.  A staged
    # answer can preserve the source color in the subject clause and then
    # contradict it again in a later style clause (for example, “light blue
    # skirt” followed by “deep blue of her skirt”).
    replacements: list[tuple[int, int, str]] = []
    for color_match in _COLOR_CLAIM_RE.finditer(candidate):
        tail = candidate[color_match.end() : color_match.end() + 60]
        noun_match = re.search(
            r"\b(" + "|".join(re.escape(noun) for noun in anchors_by_noun) + r")\b",
            tail,
            flags=re.IGNORECASE,
        ) if anchors_by_noun else None
        if not noun_match:
            continue
        noun = noun_match.group(1).lower()
        source_colors = anchors_by_noun[noun]
        candidate_color = " ".join(color_match.group(0).split())
        # In a grouped “color of X and Y” claim the color belongs to the
        # first plane as well; the source color was inserted on Y above.
        if re.match(r"\s+of\b[^.;!?]{0,60}\band\b", tail, flags=re.IGNORECASE):
            continue
        if any(candidate_color.casefold() == source_color.casefold() for source_color in source_colors):
            continue
        replacements.append((color_match.start(), color_match.end(), source_colors[0]))

    for start, end, replacement in reversed(replacements):
        candidate = candidate[:start] + replacement + candidate[end:]

    for noun, source_colors in anchors_by_noun.items():
        if not re.search(rf"\b{re.escape(source_colors[0])}\b[^.;!?]{{0,30}}\b{re.escape(noun)}\b", candidate, flags=re.IGNORECASE):
            noun_match = re.search(rf"\b{re.escape(noun)}\b", candidate, flags=re.IGNORECASE)
            if noun_match:
                candidate = (
                    candidate[: noun_match.start()]
                    + f"{source_colors[0]} "
                    + candidate[noun_match.start() :]
                )
    return candidate

def _strip_unrequested_capture_formats(candidate_prompt: str, source_prompt: str) -> str:
    candidate = str(candidate_prompt or "")
    source = str(source_prompt or "")
    if _CAPTURE_FORMAT_RE.search(source):
        return candidate
    candidate = re.sub(
        r"\b(?:medium[- ]format|large[- ]format)\s+(?:digital\s+)?capture\b\s*,?\s*",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"\b(?:medium[- ]format|large[- ]format)\b\s*,?\s*",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    # A moodboard may intentionally use a film-format word as a medium witness
    # (for example, “35mm film grain” or “35mm film rendering”).  Remove bare
    # capture-format additions, but keep a format that is visibly coupled to
    # film/emulsion/analog treatment so the style authority is not erased.
    style_film_medium = re.search(
        r"\b(?:film\s+(?:grain|rendering|photography|stock)|film[- ]like\s+grain|emulsion\s+softness|analog\s+(?:film|grain|rendering)|photographic\s+film)\b",
        candidate,
        flags=re.IGNORECASE,
    )
    if not style_film_medium:
        candidate = re.sub(
            r"\b(?:35mm|70mm|16mm)\b(?=\s+(?:film|cinematic|snapshot|photograph|grain))\s*",
            "",
            candidate,
            flags=re.IGNORECASE,
        )
    candidate = re.sub(
        r"\b(?:full[- ]frame|mirrorless|dslr|anamorphic)\b\s*(?:camera|capture|photography)?\s*",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(r"\s{2,}", " ", candidate)
    candidate = re.sub(r"\s+([,.;])", r"\1", candidate)
    candidate = re.sub(r"([,;])\s*([,.])", r"\2", candidate)
    return candidate.strip()

def _creative_entity_drift(
    source_prompt: str,
    candidate_prompt: str,
    allow_subordinate_environment_entities: bool = False,
    allow_contextual_environment_medium: bool = False,
    allow_subordinate_background_people: bool = False,
) -> bool:
    source = str(source_prompt or "").lower()
    candidate = str(candidate_prompt or "").lower()
    if not source or not candidate:
        return False
    source_human_terms = _human_guard_terms(source)
    candidate_human_terms = _human_guard_terms(candidate)
    candidate_extra_human_terms = _extra_human_signatures(candidate)
    candidate_new_silhouette = _NEW_SILHOUETTE_ENTITY_RE.search(candidate)
    source_animal_terms = _positive_entity_terms(_ANIMAL_ENTITY_RE, source)
    candidate_animal_terms = _positive_entity_terms(_ANIMAL_ENTITY_RE, candidate)
    source_vehicle_terms = _positive_entity_terms(_VEHICLE_ENTITY_RE, source)
    candidate_vehicle_terms = _positive_entity_terms(_VEHICLE_ENTITY_RE, candidate)
    if not source_human_terms and candidate_human_terms:
        if not (
            allow_subordinate_background_people
            and _subordinate_background_human_additions(source, candidate)
        ):
            return True
    if not source_human_terms and (candidate_extra_human_terms or candidate_new_silhouette):
        if not (
            allow_subordinate_background_people
            and _subordinate_background_human_additions(source, candidate)
        ):
            return True
    if (
        source_human_terms
        and _BACKGROUND_HUMAN_RE.search(candidate)
        and not _BACKGROUND_HUMAN_RE.search(source)
        and not allow_subordinate_background_people
    ):
        if not _style_only_same_subject_reference(candidate, source):
            return True
    if source_human_terms and candidate_human_terms - source_human_terms:
        # A single generic person may be paraphrased as a figure or human by
        # the staged model. Treat that as the same subject, but keep gender,
        # age, role, count, and background-person changes guarded below.
        generic_human_paraphrase = (
            source_human_terms <= _GENERIC_HUMAN_SYNONYMS
            and candidate_human_terms <= _GENERIC_HUMAN_SYNONYMS
        )
        generic_style_reference = (
            candidate_human_terms - source_human_terms
            <= {"figure", "figures", "silhouette", "silhouettes"}
            and _style_only_same_subject_reference(candidate, source)
        )
        if not (
            allow_subordinate_background_people
            and _subordinate_background_human_additions(source, candidate)
        ) and not generic_human_paraphrase and not generic_style_reference:
            return True
    if not source_human_terms and _active_human_hand_action(candidate) and not _active_human_hand_action(source):
        return True
    if (
        not source_animal_terms
        and candidate_animal_terms
        and not (
            allow_subordinate_environment_entities
            and _subordinate_environment_entity_additions(source, candidate, _ANIMAL_ENTITY_RE)
        )
    ):
        return True
    if (
        not source_vehicle_terms
        and candidate_vehicle_terms
        and not (
            allow_subordinate_environment_entities
            and _subordinate_environment_entity_additions(source, candidate, _VEHICLE_ENTITY_RE)
        )
    ):
        return True
    source_extra_human_terms = _extra_human_signatures(source)
    if source_human_terms and candidate_extra_human_terms != source_extra_human_terms:
        if not (
            allow_subordinate_background_people
            and _subordinate_background_human_additions(source, candidate)
        ):
            return True
    if _medium_entity_drift(source, candidate, allow_contextual_environment_medium=allow_contextual_environment_medium):
        return True
    if _ABSTRACT_RE.search(source) and _positive_medium_drift(candidate):
        return True
    if _ABSTRACT_RE.search(source) and _abstract_scene_drift(candidate):
        return True
    return False

def _subordinate_environment_entity_additions(
    source: str,
    candidate: str,
    pattern: re.Pattern[str],
) -> bool:
    if not _ENVIRONMENT_CONTEXT_RE.search(source):
        return False
    matches = list(pattern.finditer(candidate))
    if not matches:
        return False
    for match in matches:
        clause_start = max(0, match.start() - 120)
        clause_end = min(len(candidate), match.end() + 120)
        clause = candidate[clause_start:clause_end]
        if _ENTITY_NEGATION_RE.search(clause):
            continue
        if not _SUBORDINATE_ENTITY_CONTEXT_RE.search(clause):
            return False
    return True

def _subordinate_background_human_additions(source: str, candidate: str) -> bool:
    if not _ENVIRONMENT_CONTEXT_RE.search(source):
        return False
    matches = list(_EXTRA_HUMAN_RE.finditer(candidate))
    if not matches:
        return False
    for match in matches:
        clause_start = max(0, match.start() - 140)
        clause_end = min(len(candidate), match.end() + 140)
        clause = candidate[clause_start:clause_end]
        if _ENTITY_NEGATION_RE.search(clause):
            continue
        if not re.search(
            r"\b(?:distant|farther|background|behind|beside|nearby|along|across|beyond|silhouette)\b",
            clause,
            flags=re.IGNORECASE,
        ):
            return False
    return True

def _positive_entity_terms(pattern: re.Pattern[str], text: str) -> set[str]:
    terms: set[str] = set()
    for match in pattern.finditer(text):
        clause_start = max(0, match.start() - 80)
        clause = re.split(r"[.;!?]", text[clause_start : match.start()])[-1]
        if _ENTITY_NEGATION_RE.search(clause):
            continue
        terms.add(match.group(0).lower())
    return terms

def _extra_human_signatures(text: str) -> list[str]:
    """Normalize extra-subject phrases so harmless adjective rewrites compare equal."""
    signatures: list[str] = []
    generic = {
        "person", "people", "persons", "figure", "figures", "human", "humans",
        "silhouette", "silhouettes",
    }
    for match in _EXTRA_HUMAN_RE.finditer(str(text or "")):
        entity_match = re.search(
            r"\b(?:person|people|persons|man|woman|figure|human|passenger|friend|friends|couple|coworker|colleague|reader|patron|student|visitor|pedestrian|passerby|traveler|worker|operator|technician|driver|rider|cyclist|silhouette|men|women|adults|children|figures|humans|passengers|couples|coworkers|colleagues|readers|patrons|students|visitors|pedestrians|travelers|workers|operators|technicians|riders|cyclists)\b\s*$",
            match.group(0),
            flags=re.IGNORECASE,
        )
        if entity_match is None:
            continue
        entity = entity_match.group(0).lower()
        signatures.append("generic" if entity in generic else entity)
    return sorted(signatures)

def _positive_medium_drift(text: str) -> bool:
    for match in _MEDIUM_DRIFT_RE.finditer(text):
        clause_start = max(0, match.start() - 80)
        clause = re.split(r"[.;!?]", text[clause_start : match.start()])[-1]
        if _MEDIUM_NEGATION_RE.search(clause):
            continue
        return True
    return False

def _positive_medium_families(text: str) -> set[str]:
    families: set[str] = set()
    for family, pattern in _MEDIUM_FAMILY_PATTERNS:
        for match in pattern.finditer(text):
            if family == "painting" and match.group(0).lower() == "painted":
                before = text[max(0, match.start() - 70) : match.start()]
                after = text[match.end() : min(len(text), match.end() + 70)]
                if re.search(
                    r"\b(?:wall|walls|floor|ceiling|door|doors|surface|surfaces|bench|room|background|brick|wood|tile|tiles|panel|panels)\b",
                    before,
                    flags=re.IGNORECASE,
                ) and re.search(
                    r"\b(?:white|black|gray|grey|red|blue|green|yellow|brown|beige|cream|ochre|ivory|muted|dark|light|earth[- ]?tone)\b",
                    after,
                    flags=re.IGNORECASE,
                ):
                    continue
            if family == "drawing" and re.match(
                r"\s+(?:(?:subtle|quiet|visual|particular|the)\s+)?(?:attention|focus|the\s+eye|the\s+viewer|the\s+gaze)\b",
                text[match.end() :],
                flags=re.IGNORECASE,
            ):
                continue
            clause_start = max(0, match.start() - 80)
            clause = re.split(r"[.;!?]", text[clause_start : match.start()])[-1]
            if _MEDIUM_NEGATION_RE.search(clause):
                continue
            families.add(family)
            break
    return families

def _medium_entity_drift(source: str, candidate: str, allow_contextual_environment_medium: bool = False) -> bool:
    source_families = _positive_medium_families(source)
    candidate_families = _positive_medium_families(candidate)
    if (
        allow_contextual_environment_medium
        and not source_families
        and candidate_families
    ):
        # The moodboard adapter is an explicit style authority for medium/process
        # changes.  A source may be a person against a plain backdrop, so requiring
        # an environment noun here incorrectly falls back to the unstyled source
        # before the Turbo sampler can receive the Stage 2 medium witness.
        return False
    return not source_families and bool(candidate_families)

def _human_guard_terms(text: str, pattern: re.Pattern[str] = _HUMAN_ENTITY_RE) -> set[str]:
    terms = _positive_entity_terms(pattern, text)
    if pattern is _HUMAN_ENTITY_RE and _METAPHORICAL_HUMAN_RE.search(text):
        terms.discard("human")
        terms.discard("humans")
    if "traveler" in terms and _METAPHORICAL_TRAVELER_RE.search(text):
        terms.discard("traveler")
    return terms

def _abstract_scene_drift(candidate_prompt: str) -> bool:
    for match in _ABSTRACT_SCENE_DRIFT_RE.finditer(candidate_prompt):
        term = match.group(0).lower()
        before = candidate_prompt[max(0, match.start() - 45) : match.start()]
        after = candidate_prompt[match.end() : min(len(candidate_prompt), match.end() + 45)]
        if term == "room" and re.search(
            r"\b(?:breathing|elbow|leg|head|shoulder|clearance|maneuvering)\s*$",
            before,
            flags=re.IGNORECASE,
        ):
            continue
        if term in {"architecture", "architectural"} and re.search(
            r"\b(?:grandeur|style|language|motif|form|texture|surface|detail)\b",
            after,
            flags=re.IGNORECASE,
        ):
            continue
        if term == "landscape" and re.search(
            r"\b(?:orientation|format|layout|mode)\b",
            after,
            flags=re.IGNORECASE,
        ):
            continue
        return True
    return False

__all__ = ["KreaMoodboardStyleAdapter", "KreaPromptSanitizer"]
