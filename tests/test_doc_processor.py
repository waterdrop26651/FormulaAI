# -*- coding: utf-8 -*-
"""Tests for DocProcessor formatting reports."""

from pathlib import Path

from docx import Document

from src.core.doc_processor import DocProcessor
from src.core.header_footer_config import HeaderFooterConfig


def _make_input_docx(path: Path):
    document = Document()
    document.add_paragraph("原始标题")
    document.save(path)


def test_apply_formatting_returns_structured_render_report(tmp_path):
    input_path = tmp_path / "input.docx"
    _make_input_docx(input_path)

    processor = DocProcessor()
    assert processor.read_document(str(input_path)) is True

    report = processor.apply_formatting(
        {
            "elements": [
                {
                    "type": "标题",
                    "content": "论文标题",
                    "format": {
                        "font": "黑体",
                        "size": "小二",
                        "bold": True,
                        "line_spacing": 1.0,
                        "alignment": "center",
                    },
                },
                {
                    "type": "正文",
                    "content": "这是正文。",
                    "format": {
                        "font": "宋体",
                        "size": "小四",
                        "bold": False,
                        "line_spacing": 1.5,
                        "alignment": "justify",
                    },
                },
            ]
        },
        custom_save_path=str(tmp_path),
        header_footer_config=HeaderFooterConfig(),
    )

    assert report["success"] is True
    assert report["total_elements"] == 2
    assert report["processed_elements"] == 2
    assert report["failed_elements"] == []
    assert report["output_file"]
    assert Path(report["output_file"]).exists()
    assert report["header_footer"]["attempted"] is True
    assert report["header_footer"]["success"] is True
