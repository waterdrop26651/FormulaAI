# -*- coding: utf-8 -*-
"""Tests for text template parsing and normalization."""

from src.core.text_template_parser import TextTemplateParser


class FakeAIConnector:
    """Simple stub for TextTemplateParser tests."""

    def __init__(self, response, success=True):
        self.response = response
        self.success = success
        self.last_prompt = None

    def send_request(self, prompt):
        self.last_prompt = prompt
        return self.success, self.response


def _chat_response(content):
    return {"choices": [{"message": {"content": content}}]}


def test_parse_text_to_template_normalizes_alignment_and_size():
    response = _chat_response(
        """
```json
{
  "标题": {"font": "黑体", "size": "小二", "bold": true, "alignment": "居中", "line_spacing": 1.5},
  "正文": {"font": "宋体", "size": "未知字号", "bold": false, "alignment": "两端对齐", "line_spacing": "1.25"}
}
```
"""
    )
    connector = FakeAIConnector(response=response)
    parser = TextTemplateParser(connector)

    success, template = parser.parse_text_to_template(
        "标题使用黑体小二，正文两端对齐。",
        template_name="测试模板",
        template_description="解析测试",
    )

    assert success is True
    assert "标题使用黑体小二" in connector.last_prompt
    assert template["name"] == "测试模板"
    assert template["description"] == "解析测试"
    assert template["rules"]["标题"]["alignment"] == "center"
    assert template["rules"]["正文"]["alignment"] == "justify"
    assert template["rules"]["正文"]["size"] == "五号"
    assert template["rules"]["正文"]["line_spacing"] == 1.25


def test_parse_text_to_template_returns_error_when_ai_request_fails():
    connector = FakeAIConnector(response="timeout", success=False)
    parser = TextTemplateParser(connector)

    success, message = parser.parse_text_to_template("任意输入")

    assert success is False
    assert "AI解析失败" in message


def test_normalize_rules_skips_non_dict_and_uses_defaults():
    parser = TextTemplateParser(FakeAIConnector(response={}))
    rules = {
        "正文": {"font": "宋体", "alignment": "left"},
        "无效项": "not-a-dict",
    }

    normalized = parser._normalize_rules(rules)

    assert "无效项" not in normalized
    assert normalized["正文"]["font"] == "宋体"
    assert normalized["正文"]["size"] == "五号"
    assert normalized["正文"]["bold"] is False
    assert normalized["正文"]["alignment"] == "left"
