# -*- coding: utf-8 -*-
"""
UIPanel模块

Contains所HasUIPanel组Item：
- DocumentPanel: Document管理Panel
- TemplatePanel: TemplateSettingsPanel  
- StatusPanel: StatusVisiblePanel
"""

from .document_panel import DocumentPanel
from .template_panel import TemplatePanel
from .status_panel import StatusPanel

__all__ = ['DocumentPanel', 'TemplatePanel', 'StatusPanel']