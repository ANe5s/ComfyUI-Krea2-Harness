// Copyright (C) 2026 ANe5s
// SPDX-License-Identifier: GPL-3.0-or-later

const { app } = window.comfyAPI.app;

const NODE_ID = "Krea2TurboResolutionSelector";
const GRID = 32;
const MAX_EDGE = 2048;
const MP_BASE = 1024 * 1024;

const ASPECTS = {
  "1:1": [1, 1],
  "4:3": [4, 3],
  "3:2": [3, 2],
  "16:9": [16, 9],
  "2.35:1": [2.35, 1],
  "4:5": [4, 5],
  "2:3": [2, 3],
  "9:16": [9, 16],
};

const ANCHORS_1K = {
  "1:1": [1024, 1024],
  "4:3": [1184, 896],
  "3:2": [1248, 832],
  "16:9": [1376, 768],
  "2.35:1": [1568, 672],
  "4:5": [928, 1152],
  "2:3": [832, 1248],
  "9:16": [768, 1376],
};

function nearestGrid(value) {
  return Math.max(GRID, Math.floor(value / GRID + 0.5) * GRID);
}

function resolutionFor(aspect, megapixels) {
  const anchor = ANCHORS_1K[aspect] || ANCHORS_1K["1:1"];
  const target = Number(megapixels);
  if (!Number.isFinite(target) || Math.abs(target - 1) < 1e-9) {
    return anchor;
  }

  const ratio = ASPECTS[aspect] || ASPECTS["1:1"];
  const targetPixels = target * MP_BASE;
  const scale = Math.min(
    Math.sqrt(targetPixels / (ratio[0] * ratio[1])),
    MAX_EDGE / Math.max(ratio[0], ratio[1]),
  );
  return [
    Math.min(MAX_EDGE, nearestGrid(ratio[0] * scale)),
    Math.min(MAX_EDGE, nearestGrid(ratio[1] * scale)),
  ];
}

function currentValue(node, name, fallback) {
  const widget = node.widgets?.find((candidate) => candidate.name === name);
  return widget?.value ?? fallback;
}

function installPreview(node) {
  if (node.__krea2ResolutionPreviewInstalled) return;
  node.__krea2ResolutionPreviewInstalled = true;

  const preview = document.createElement("div");
  preview.className = "krea2-resolution-preview";
  preview.style.cssText = [
    "box-sizing: border-box",
    "width: 100%",
    "height: 24px",
    "padding: 3px 8px",
    "border-radius: 4px",
    "background: rgba(255, 255, 255, 0.08)",
    "color: var(--descrip-text, #d0d0d0)",
    "font: 12px/18px sans-serif",
    "text-align: center",
    "white-space: nowrap",
    "user-select: none",
    "pointer-events: none",
  ].join(";");

  let previewWidget;
  if (typeof node.addDOMWidget === "function") {
    previewWidget = node.addDOMWidget(
      "krea2_resolution_preview",
      "krea2_resolution_preview",
      preview,
      { serialize: false, hideOnZoom: false, margin: 0 },
    );
  } else {
    previewWidget = node.addWidget(
      "text",
      "krea2_resolution_preview",
      "",
      undefined,
      { serialize: false },
    );
    previewWidget.disabled = true;
  }

  const update = () => {
    const aspect = String(currentValue(node, "aspect_ratio", "1:1"));
    const megapixels = Number(currentValue(node, "megapixels", 1.0));
    const [width, height] = resolutionFor(aspect, megapixels);
    const actualMp = (width * height) / MP_BASE;
    const label = `${width} × ${height}    ${actualMp.toFixed(2)} MP`;
    if (previewWidget?.type === "krea2_resolution_preview") {
      preview.textContent = label;
    } else if (previewWidget) {
      previewWidget.value = label;
    }
    node.graph?.setDirtyCanvas(true, true);
  };

  for (const name of ["aspect_ratio", "megapixels"]) {
    const widget = node.widgets?.find((candidate) => candidate.name === name);
    if (!widget) continue;
    const original = widget.callback;
    widget.callback = function (...args) {
      const result = original?.apply(this, args);
      update();
      return result;
    };
  }

  const originalConfigure = node.onConfigure;
  node.onConfigure = function (...args) {
    const result = originalConfigure?.apply(this, args);
    setTimeout(update, 0);
    return result;
  };

  node.__krea2ResolutionPreview = { preview, previewWidget, update };
  update();
}

app.registerExtension({
  name: "KreaHarness.Krea2ResolutionSelector",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== NODE_ID) return;

    const originalCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function (...args) {
      const result = originalCreated?.apply(this, args);
      installPreview(this);
      return result;
    };
  },
});
