# -*- coding: utf-8 -*-
"""Tests for structure analyzer heuristics."""

from src.core.structure_analyzer import StructureAnalyzer


def test_analyze_text_features_detects_titles_and_special_sections():
    analyzer = StructureAnalyzer()
    paragraphs = [
        "论文标题",
        "摘要",
        "这是摘要内容。",
        "关键词：人工智能；文档排版",
        "1. 引言",
        "这是正文内容。",
        "参考文献",
    ]

    features = analyzer.analyze_text_features(paragraphs)

    assert 0 in features["potential_titles"]
    assert 4 in features["potential_subtitles"]
    assert features["special_sections"]["abstract"] in (1, 2)
    assert features["special_sections"]["keywords"] == 3
    assert features["special_sections"]["references"] == 6
    assert features["avg_length"] > 0


def test_generate_structure_hints_returns_expected_ranges():
    analyzer = StructureAnalyzer()
    paragraphs = [
        "论文标题",
        "摘要",
        "这是摘要内容。",
        "关键词：人工智能；文档排版",
        "1. 引言",
        "这是正文内容。",
        "参考文献",
    ]
    features = analyzer.analyze_text_features(paragraphs)

    hints = analyzer.generate_structure_hints(features)

    assert hints["title_index"] == 0
    assert hints["keywords_index"] == 3
    assert hints["abstract_range"] in ((1, 2), (2, 2))
    assert hints["references_range"][0] == 6


def test_validate_structure_fills_missing_fields():
    analyzer = StructureAnalyzer()
    structure = {"elements": [{"content": "正文段落"}]}

    valid, normalized = analyzer.validate_structure(structure)

    assert valid is True
    assert normalized["elements"][0]["type"] == "正文"
    assert normalized["elements"][0]["content"] == "正文段落"
    assert normalized["elements"][0]["format"]["font"] == "宋体"
