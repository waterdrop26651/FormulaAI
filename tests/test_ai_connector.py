# -*- coding: utf-8 -*-
"""Tests for AIConnector methods that do not require network."""

from src.core.ai_connector import AIConnector


def _response_with_content(content):
    return {"choices": [{"message": {"content": content}}]}


def test_generate_prompt_contains_document_and_rules():
    connector = AIConnector({"api_url": "https://example.com", "api_key": "key", "model": "demo"})
    prompt = connector.generate_prompt(
        ["论文标题", "这是正文。"],
        {"正文": {"font": "宋体", "size": "小四", "alignment": "justify"}},
    )

    assert "论文标题" in prompt
    assert "宋体" in prompt
    assert "JSON格式" in prompt


def test_parse_response_extracts_wrapped_json():
    connector = AIConnector({"api_url": "https://example.com", "api_key": "key", "model": "demo"})
    content = """
以下是排版结果：
{
  "elements": [
    {
      "type": "正文",
      "content": "测试内容",
      "format": {"font": "宋体", "size": "小四", "bold": false, "line_spacing": 1.5, "alignment": "left"}
    }
  ]
}
"""
    success, result = connector.parse_response(_response_with_content(content))

    assert success is True
    assert isinstance(result, dict)
    assert result["elements"][0]["type"] == "正文"


def test_parse_response_reports_error_for_template_shape():
    connector = AIConnector({"api_url": "https://example.com", "api_key": "key", "model": "demo"})
    template_like_content = '{"name":"模板","description":"desc","rules":{"正文":{"font":"宋体"}}}'

    success, message = connector.parse_response(_response_with_content(template_like_content))

    assert success is False
    assert "elements" in message


def test_parse_response_repairs_trailing_comma_and_normalizes_alignment():
    connector = AIConnector({"api_url": "https://example.com", "api_key": "key", "model": "demo"})
    malformed = """
{
  "elements": [
    {
      "type": "正文",
      "content": "测试内容",
      "format": {"font": "宋体", "size": "小四", "bold": false, "line_spacing": 1.5, "alignment": "两端对齐",}
    }
  ]
}
"""
    success, result = connector.parse_response(_response_with_content(malformed))

    assert success is True
    assert result["elements"][0]["format"]["alignment"] == "justify"


def test_validate_config_rejects_blank_values_without_request():
    connector = AIConnector({"api_url": "", "api_key": "", "model": ""})

    success, message = connector.validate_config()

    assert success is False
    assert "API URL不能为空" in message
