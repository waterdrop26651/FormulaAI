# -*- coding: utf-8 -*-
"""Shared helpers for runtime template normalization."""

ALIGNMENT_ALIASES = {
    "left": "left",
    "center": "center",
    "right": "right",
    "justify": "justify",
    "justified": "justify",
    "leftalign": "left",
    "centeralign": "center",
    "rightalign": "right",
    "justifiedalign": "justify",
    "左对齐": "left",
    "左": "left",
    "居中": "center",
    "居中对齐": "center",
    "右对齐": "right",
    "右": "right",
    "两端对齐": "justify",
    "两端": "justify",
}


def normalize_alignment(value):
    """Normalize alignment values to left/center/right/justify."""
    raw = str(value or "").strip()
    key = raw.lower().replace(" ", "")

    if key in ALIGNMENT_ALIASES:
        return ALIGNMENT_ALIASES[key]

    if "居中" in raw:
        return "center"
    if "右" in raw:
        return "right"
    if "两端" in raw:
        return "justify"
    return "left"


def normalize_template_rules(rules):
    """Normalize template rules while skipping invalid entries."""
    if not isinstance(rules, dict):
        return {}

    normalized = {}
    for element_type, rule in rules.items():
        if not isinstance(rule, dict):
            continue
        normalized_rule = dict(rule)
        normalized_rule["alignment"] = normalize_alignment(rule.get("alignment", "left"))
        normalized[element_type] = normalized_rule
    return normalized
