# -*- coding: utf-8 -*-
"""
UI面板模块

包含所有UI面板组件：
- DocumentPanel: 文档管理面板
- TemplatePanel: 模板设置面板  
- StatusPanel: 状态显示面板
"""

from .document_panel import DocumentPanel
from .template_panel import TemplatePanel
from .status_panel import StatusPanel

__all__ = ['DocumentPanel', 'TemplatePanel', 'StatusPanel']