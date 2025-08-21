# -*- coding: utf-8 -*-
"""
TemplateSettingsPanel

职责：
1. TemplateSelection和管理
2. Fast速Parameters调Section
3. HighLevelTemplateEdit入口
4. APIConfiguration管理

设计原Rule：
- 单One职责：只管Template相关Operation
- 渐进式披露：常用Function突出，HighLevelFunction收纳
- 简洁Operation：最Multiple2Layer缩进
"""

import os
from typing import Optional, Dict, Any

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
        QLabel, QPushButton, QComboBox, QSpinBox,
        QDoubleSpinBox, QGridLayout, QMessageBox, QTextEdit
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QFont
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    raise ImportError("PyQt6 is required but not properly installed")

from ...utils.logger import app_logger
from ...utils.config_manager import config_manager
from ...core.format_manager import FormatManager
from ..api_config_dialog import ApiConfigDialog


class TemplatePanel(QWidget):
    """
    TemplateSettingsPanel
    
    Signal：
    - template_changed: Template变更
    """
    
    # Signal definitions
    template_changed = pyqtSignal(str)  # Template name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State variables
        self._current_template: Optional[str] = None
        self._document_ready: bool = False
        
        # Core components
        self.format_manager = FormatManager()
        self.app_config = config_manager.get_app_config()
        
        # Initialize UI
        self._init_ui()
        self._load_templates()
        self._load_config()
        
        app_logger.info("TemplatePanel初始化Complete")
    
    def _init_ui(self):
        """
        初始化User界面
        
        Layout：
        ┌─TemplateSelection─────────┐
        │ TemplateDropdown       │
        ├─Fast速调Section─────────┤
        │ Font、CharacterNumber等     │
        ├─HighLevelSettings─────────┤
        │ Edit器入口       │
        ├─Template管理─────────┤
        │ 导入导出等       │
        └─APIConfiguration──────────┘
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Template selection area
        template_group = self._create_template_selection_group()
        layout.addWidget(template_group)
        
        # Template content preview area
        preview_group = self._create_template_preview_group()
        layout.addWidget(preview_group)
        
        # Template management area（仅保留导入Function）
        management_group = self._create_template_management_group()
        layout.addWidget(management_group)
        
        # API configuration area
        api_group = self._create_api_config_group()
        layout.addWidget(api_group)
        
        # Add flexible space
        layout.addStretch()
    
    def _create_template_selection_group(self) -> QGroupBox:
        """创建TemplateSelection组"""
        group = QGroupBox("TemplateSelection")
        layout = QVBoxLayout(group)
        
        # TemplateDropdown
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        
        layout.addWidget(QLabel("SelectionFormattingTemplate:"))
        layout.addWidget(self.template_combo)
        
        return group
    
    def _create_template_preview_group(self) -> QGroupBox:
        """创建TemplateContentPreview组"""
        group = QGroupBox("TemplateContentPreview")
        layout = QVBoxLayout(group)
        
        # TemplateContentVisible区
        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(200)
        self.template_preview.setPlaceholderText("SelectionTemplateNext将VisibleTemplate的详细ConfigurationInformation")
        self.template_preview.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.template_preview)
        
        return group
    
    def _create_template_management_group(self) -> QGroupBox:
        """创建Template管理组（仅保留导入Function）"""
        group = QGroupBox("Template管理")
        layout = QVBoxLayout(group)
        
        # 导入Buttons
        self.import_btn = QPushButton("导入Template")
        self.import_btn.clicked.connect(self._import_template)
        
        layout.addWidget(self.import_btn)
        
        return group
    
    def _create_api_config_group(self) -> QGroupBox:
        """创建APIConfiguration组"""
        group = QGroupBox("APIConfiguration")
        layout = QVBoxLayout(group)
        
        # APIConfigurationButtons
        self.api_config_btn = QPushButton("APIConfiguration")
        self.api_config_btn.clicked.connect(self._open_api_config)
        
        layout.addWidget(self.api_config_btn)
        
        return group
    
    def _load_templates(self):
        """加载TemplateList"""
        self.template_combo.clear()
        
        try:
            template_names = self.format_manager.get_template_names()
            for name in template_names:
                self.template_combo.addItem(name)
            
            app_logger.info(f"已加载 {len(template_names)} 个Template")
            
        except Exception as e:
            app_logger.error(f"加载TemplateFailed: {e}")
    
    def _load_config(self):
        """加载Configuration"""
        # SetDefaultTemplate
        default_template = self.app_config.get("last_template", "DefaultTemplate")
        index = self.template_combo.findText(default_template)
        if index >= 0:
            self.template_combo.setCurrentIndex(index)
        elif self.template_combo.count() > 0:
            self.template_combo.setCurrentIndex(0)
    
    def _on_template_changed(self, template_name: str):
        """Template变更Event"""
        if not template_name:
            return
        
        self._current_template = template_name
        
        # UpdateTemplateContentPreview
        self._update_template_preview(template_name)
        
        # Emit signal
        self.template_changed.emit(template_name)
        
        app_logger.info(f"Template已切换: {template_name}")
    
    def _update_template_preview(self, template_name: str):
        """更NewTemplateContentPreview"""
        try:
            # GetTemplateData
            template_data = self.format_manager.get_template(template_name)
            
            if template_data:
                # FormatVisibleTemplateContent
                preview_text = self._format_template_content(template_data)
                self.template_preview.setText(preview_text)
            else:
                self.template_preview.setText(f"NoneLaw加载Template '{template_name}' 的Content")
                
        except Exception as e:
            app_logger.error(f"更NewTemplatePreviewFailed: {e}")
            self.template_preview.setText(f"加载TemplateContentTime发生Error: {str(e)}")
    
    def _format_template_content(self, template_data: dict) -> str:
        """FormatTemplateContent为可读DocumentBook"""
        try:
            content_lines = []
            
            # TemplateBasicInformation
            content_lines.append(f"Template name: {template_data.get('name', '未知')}")
            content_lines.append(f"Template描述: {template_data.get('description', 'None描述')}")
            content_lines.append("")
            
            # FormattingRule
            elements = template_data.get('elements', {})
            if elements:
                content_lines.append("FormattingRule:")
                content_lines.append("=" * 40)
                
                for element_name, element_config in elements.items():
                    content_lines.append(f"\n【{element_name}】")
                    
                    if isinstance(element_config, dict):
                        for key, value in element_config.items():
                            if key == 'font':
                                content_lines.append(f"  Font: {value}")
                            elif key == 'size':
                                content_lines.append(f"  CharacterNumber: {value}")
                            elif key == 'bold':
                                content_lines.append(f"  粗体: {'Yes' if value else 'No'}")
                            elif key == 'alignment':
                                alignment_map = {
                                    'center': '居Center',
                                    'left': 'Left对齐',
                                    'right': 'Right对齐',
                                    'justify': '两端对齐'
                                }
                                content_lines.append(f"  对齐: {alignment_map.get(value, value)}")
                            elif key == 'line_spacing':
                                content_lines.append(f"  Line距: {value}倍")
                            else:
                                content_lines.append(f"  {key}: {value}")
                    else:
                        content_lines.append(f"  Configuration: {element_config}")
            else:
                content_lines.append("该Template暂NoneFormattingRuleConfiguration")
            
            return "\n".join(content_lines)
            
        except Exception as e:
            app_logger.error(f"FormatTemplateContentFailed: {e}")
            return f"FormatTemplateContentTime发生Error: {str(e)}"
    

    
    def _import_template(self):
        """导入Template"""
        from ..dialogs.text_parsing_dialog import TextParsingDialog
        from ...core.text_template_parser import TextTemplateParser
        from ...core.ai_connector import AIConnector
        
        try:
            # CreateDocumentBookParseDialog
            dialog = TextParsingDialog(self)
            if dialog.exec():
                template_name = dialog.get_template_name()
                template_desc = dialog.get_template_description()
                text_content = dialog.get_text_content()
                
                if not template_name:
                    QMessageBox.warning(self, "提示", "请InputTemplate name！")
                    return
                
                if not text_content.strip():
                    QMessageBox.warning(self, "提示", "请InputFormat要求DocumentBook！")
                    return
                
                # VisibleProgressDialog
                from PyQt6.QtWidgets import QProgressDialog
                from PyQt6.QtCore import Qt
                
                progress = QProgressDialog("正InUseAIParseFormat要求，请稍候...", "Cancel", 0, 0, self)
                progress.setWindowTitle("生成Template")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setCancelButton(None)  # Disable cancel button
                progress.show()
                
                # ProcessEvent循环，确保DialogVisible
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()
                
                # UseAIParseDocumentBook生成Template
                from ...utils.config_manager import config_manager
                api_config = config_manager.get_api_config()
                ai_connector = AIConnector(api_config)
                parser = TextTemplateParser(ai_connector)
                
                success, result = parser.parse_text_to_template(text_content)
                progress.close()
                
                if success:
                    # Save生成的Template
                    template_data = {
                        "name": template_name,
                        "description": template_desc,
                        "elements": result
                    }
                    
                    # Save到TemplateFile
                    import os
                    import json
                    template_file = os.path.join("config/templates", f"{template_name}.json")
                    
                    with open(template_file, 'w', encoding='utf-8') as f:
                        json.dump(template_data, f, ensure_ascii=False, indent=2)
                    
                    # 重New加载TemplateList
                    self._load_templates()
                    
                    # SelectionNew创建的Template
                    index = self.template_combo.findText(template_name)
                    if index >= 0:
                        self.template_combo.setCurrentIndex(index)
                    
                    QMessageBox.information(self, "Success", f"Template '{template_name}' 已Success生成并保存！")
                    app_logger.info(f"Success生成Template: {template_name}")
                else:
                    QMessageBox.warning(self, "Error", f"生成TemplateFailed: {result}")
                    app_logger.error(f"生成TemplateFailed: {result}")
                    
        except Exception as e:
            app_logger.error(f"导入TemplateFailed: {e}")
            QMessageBox.warning(self, "Error", f"导入TemplateFailed: {str(e)}")
    

    
    def _open_api_config(self):
        """OpenAPIConfiguration"""
        try:
            dialog = ApiConfigDialog(self)
            if dialog.exec():
                app_logger.info("APIConfiguration已更New")
                
        except Exception as e:
            app_logger.error(f"OpenAPIConfigurationFailed: {e}")
            QMessageBox.warning(self, "Error", f"OpenAPIConfigurationFailed: {str(e)}")
    
    # Public interface methods
    def get_selected_template(self) -> Optional[str]:
        """获取Selection的Template name"""
        return self._current_template
    
    def on_document_ready(self, file_path: str):
        """Document准备就绪Event"""
        self._document_ready = True
        app_logger.info(f"TemplatePanel收到Document就绪通知: {file_path}")
        
        # TODO: 根据Document特征推荐合适的Template
    
    def set_template_enabled(self, enabled: bool):
        """SettingsTemplate相关控ItemStatus"""
        self.template_combo.setEnabled(enabled)
        self.apply_btn.setEnabled(enabled)
        self.edit_template_btn.setEnabled(enabled)