# -*- coding: utf-8 -*-
"""
UI模块单元测试
使用pytest-qt框架测试Qt界面组件
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMainWindowV2:
    """主窗口V2测试类"""

    def test_window_initialization(self, qtbot):
        """测试窗口初始化"""
        from src.ui.main_window_v2 import MainWindowV2

        window = MainWindowV2()
        qtbot.addWidget(window)

        # 验证窗口标题
        assert window.windowTitle() == "FormulaAI - AI智能文档排版工具"

        # 验证窗口大小
        assert window.width() == 1000
        assert window.height() == 700

    def test_panels_created(self, qtbot):
        """测试面板创建"""
        from src.ui.main_window_v2 import MainWindowV2

        window = MainWindowV2()
        qtbot.addWidget(window)

        # 验证面板存在
        assert window.document_panel is not None
        assert window.template_panel is not None
        assert window.status_panel is not None

    def test_signals_defined(self, qtbot):
        """测试信号定义"""
        from src.ui.main_window_v2 import MainWindowV2

        window = MainWindowV2()
        qtbot.addWidget(window)

        # 验证信号存在
        assert hasattr(window, 'document_selected')
        assert hasattr(window, 'template_changed')
        assert hasattr(window, 'formatting_started')


class TestDocumentPanel:
    """文档面板测试类"""

    def test_panel_initialization(self, qtbot):
        """测试面板初始化"""
        from src.ui.panels.document_panel import DocumentPanel

        panel = DocumentPanel()
        qtbot.addWidget(panel)

        # 验证初始状态
        assert panel.get_selected_document() is None
        assert panel.get_save_directory() is None

    def test_signals_defined(self, qtbot):
        """测试信号定义"""
        from src.ui.panels.document_panel import DocumentPanel

        panel = DocumentPanel()
        qtbot.addWidget(panel)

        # 验证信号存在
        assert hasattr(panel, 'document_selected')
        assert hasattr(panel, 'formatting_requested')


class TestTemplatePanel:
    """模板面板测试类"""

    def test_panel_initialization(self, qtbot):
        """测试面板初始化"""
        from src.ui.panels.template_panel import TemplatePanel

        panel = TemplatePanel()
        qtbot.addWidget(panel)

        # 验证初始状态
        assert panel.get_selected_template() is None

    def test_set_template_enabled(self, qtbot):
        """测试模板启用状态设置"""
        from src.ui.panels.template_panel import TemplatePanel

        panel = TemplatePanel()
        qtbot.addWidget(panel)

        # 测试启用
        panel.set_template_enabled(True)
        assert panel.template_combo.isEnabled() == True

        # 测试禁用
        panel.set_template_enabled(False)
        assert panel.template_combo.isEnabled() == False

    def test_get_header_footer_config(self, qtbot):
        """测试获取页眉页脚配置"""
        from src.ui.panels.template_panel import TemplatePanel

        panel = TemplatePanel()
        qtbot.addWidget(panel)

        # 初始时应为None
        config = panel.get_header_footer_config()
        assert config is None


class TestStatusPanel:
    """状态面板测试类"""

    def test_panel_initialization(self, qtbot):
        """测试面板初始化"""
        from src.ui.panels.status_panel import StatusPanel

        panel = StatusPanel()
        qtbot.addWidget(panel)

        # 验证初始状态
        assert hasattr(panel, 'stop_requested')

    def test_start_formatting(self, qtbot):
        """测试开始排版"""
        from src.ui.panels.status_panel import StatusPanel

        panel = StatusPanel()
        qtbot.addWidget(panel)

        # 调用开始排版方法
        panel.start_formatting()

    def test_stop_formatting(self, qtbot):
        """测试停止排版"""
        from src.ui.panels.status_panel import StatusPanel

        panel = StatusPanel()
        qtbot.addWidget(panel)

        # 调用停止排版方法
        panel.stop_formatting()


class TestStructureAnalyzer:
    """结构分析器测试类"""

    def test_chinese_punctuation_detection(self):
        """测试中文标点检测"""
        from src.core.structure_analyzer import StructureAnalyzer

        analyzer = StructureAnalyzer()

        # 测试带中文标点的段落不应被识别为标题
        paragraphs = ["这是标题。", "这是另一个标题，还有内容"]
        features = analyzer.analyze_text_features(paragraphs)

        # 验证分析结果
        assert 'paragraph_lengths' in features

    def test_title_detection(self):
        """测试标题检测"""
        from src.core.structure_analyzer import StructureAnalyzer

        analyzer = StructureAnalyzer()

        # 测试简单文档结构
        paragraphs = ["论文标题", "摘要内容", "正文内容"]
        features = analyzer.analyze_text_features(paragraphs)

        # 第一段短且无标点，应被识别为潜在标题
        assert 0 in features['potential_titles']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
