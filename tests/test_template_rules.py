# -*- coding: utf-8 -*-
"""Tests for runtime template-rule normalization."""

from src.runtime.template_rules import normalize_alignment, normalize_template_rules


def test_normalize_alignment_handles_chinese_aliases():
    assert normalize_alignment("居中") == "center"
    assert normalize_alignment("两端对齐") == "justify"
    assert normalize_alignment("右对齐") == "right"
    assert normalize_alignment("") == "left"


def test_normalize_template_rules_normalizes_alignment_and_skips_invalid_rules():
    rules = {
        "正文": {"font": "宋体", "size": "小四", "alignment": "两端对齐", "bold": False},
        "标题": {"font": "黑体", "size": "小二", "alignment": "居中", "bold": True},
        "坏规则": "not-a-dict",
    }

    normalized = normalize_template_rules(rules)

    assert normalized["正文"]["alignment"] == "justify"
    assert normalized["标题"]["alignment"] == "center"
    assert "坏规则" not in normalized
