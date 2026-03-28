# -*- coding: utf-8 -*-
"""Tests for config manager and format manager behavior."""

from src.core.format_manager import FormatManager
from src.utils.config_manager import ConfigManager


def test_config_manager_creates_dirs_and_persists_data(tmp_path):
    config_dir = tmp_path / "config"
    manager = ConfigManager(str(config_dir))

    assert (config_dir / "templates").exists()

    api_config = {"api_url": "https://example.com", "api_key": "k", "model": "m"}
    app_config = {"save_path": "/tmp/output", "theme": "light"}
    template = {"rules": {"正文": {"font": "宋体", "size": "小四"}}}

    assert manager.save_api_config(api_config) is True
    assert manager.save_app_config(app_config) is True
    assert manager.save_template("测试模板", template) is True

    reloaded = ConfigManager(str(config_dir))
    assert reloaded.get_api_config()["model"] == "m"
    assert reloaded.get_app_config()["theme"] == "light"
    assert reloaded.get_template("测试模板")["name"] == "测试模板"
    assert reloaded.delete_template("测试模板") is True
    assert reloaded.delete_template("不存在模板") is False


def test_format_manager_save_load_delete_and_validate_template(tmp_path):
    templates_dir = tmp_path / "templates"
    manager = FormatManager(str(templates_dir))

    template = {
        "name": "论文模板",
        "description": "测试模板",
        "rules": {
            "正文": {"font": "宋体", "size": "小四", "bold": False, "alignment": "justify"}
        },
    }

    assert manager.save_template("论文模板", template) is True
    assert "论文模板" in manager.load_templates()

    valid, msg = manager.validate_template(template)
    assert valid is True
    assert msg == ""

    invalid_template = {"name": "坏模板", "rules": {"正文": {"size": "小四"}}}
    valid, msg = manager.validate_template(invalid_template)
    assert valid is False
    assert "font" in msg

    assert manager.delete_template("论文模板") is True


def test_format_manager_converts_docx_params(tmp_path):
    manager = FormatManager(str(tmp_path / "templates"))
    params = manager.format_to_docx_params(
        {
            "font": "黑体",
            "size": "小四",
            "bold": True,
            "italic": False,
            "underline": True,
            "line_spacing": 1.5,
            "alignment": "center",
            "first_line_indent": 21,
        }
    )

    assert params["font_name"] == "黑体"
    assert "font_size" in params
    assert params["bold"] is True
    assert params["underline"] is True
    assert params["alignment"] == "center"
    assert params["first_line_indent"] == 21
