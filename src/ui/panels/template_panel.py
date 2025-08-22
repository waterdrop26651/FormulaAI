# -*- coding: utf-8 -*-
"""
模板设置面板

职责：
1. 模板选择和管理
2. 快速参数调节
3. 高级模板编辑入口
4. API配置管理

设计原则：
- 单一职责：只管模板相关操作
- 渐进式披露：常用功能突出，高级功能收纳
- 简洁操作：最多2层缩进
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
from ..dialogs.header_footer_dialog import HeaderFooterDialog
from ...core.header_footer_config import HeaderFooterConfig


class TemplatePanel(QWidget):
    """
    模板设置面板
    
    信号：
    - template_changed: 模板变更
    """
    
    # 信号定义
    template_changed = pyqtSignal(str)  # 模板名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self._current_template: Optional[str] = None
        self._document_ready: bool = False
        
        # 核心组件
        self.format_manager = FormatManager()
        self.app_config = config_manager.get_app_config()
        
        # 页眉页脚配置
        self.header_footer_config: Optional[HeaderFooterConfig] = None
        
        # 初始化UI
        self._init_ui()
        self._load_templates()
        self._load_config()
        
        app_logger.info("模板面板初始化完成")
    
    def _init_ui(self):
        """
        初始化用户界面
        
        布局：
        ┌─模板选择─────────┐
        │ 模板下拉框       │
        ├─快速调节─────────┤
        │ 字体、字号等     │
        ├─高级设置─────────┤
        │ 编辑器入口       │
        ├─模板管理─────────┤
        │ 导入导出等       │
        └─API配置──────────┘
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 模板选择区
        template_group = self._create_template_selection_group()
        layout.addWidget(template_group)
        
        # 模板内容预览区
        preview_group = self._create_template_preview_group()
        layout.addWidget(preview_group)
        
        # 模板管理区（仅保留导入功能）
        management_group = self._create_template_management_group()
        layout.addWidget(management_group)
        
        # API配置区
        api_group = self._create_api_config_group()
        layout.addWidget(api_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _create_template_selection_group(self) -> QGroupBox:
        """创建模板选择组"""
        group = QGroupBox("模板选择")
        layout = QVBoxLayout(group)
        
        # 模板下拉框
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        
        layout.addWidget(QLabel("选择排版模板:"))
        layout.addWidget(self.template_combo)
        
        return group
    
    def _create_template_preview_group(self) -> QGroupBox:
        """创建模板内容预览组"""
        group = QGroupBox("模板内容预览")
        layout = QVBoxLayout(group)
        
        # 模板内容显示区
        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(200)
        self.template_preview.setPlaceholderText("选择模板后将显示模板的详细配置信息")
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
        """创建模板管理组"""
        group = QGroupBox("模板管理")
        layout = QVBoxLayout(group)
        
        # 导入按钮
        self.import_btn = QPushButton("导入模板")
        self.import_btn.clicked.connect(self._import_template)
        
        # 页眉页脚配置按钮
        self.header_footer_btn = QPushButton("Header & Footer Settings")
        self.header_footer_btn.clicked.connect(self._show_header_footer_dialog)
        self.header_footer_btn.setToolTip("Configure document header and footer")
        
        layout.addWidget(self.import_btn)
        layout.addWidget(self.header_footer_btn)
        
        return group
    
    def _create_api_config_group(self) -> QGroupBox:
        """创建API配置组"""
        group = QGroupBox("API配置")
        layout = QVBoxLayout(group)
        
        # API配置按钮
        self.api_config_btn = QPushButton("API配置")
        self.api_config_btn.clicked.connect(self._open_api_config)
        
        layout.addWidget(self.api_config_btn)
        
        return group
    
    def _load_templates(self):
        """加载模板列表"""
        self.template_combo.clear()
        
        try:
            template_names = self.format_manager.get_template_names()
            for name in template_names:
                self.template_combo.addItem(name)
            
            app_logger.info(f"已加载 {len(template_names)} 个模板")
            
        except Exception as e:
            app_logger.error(f"加载模板失败: {e}")
    
    def _load_config(self):
        """加载配置"""
        # 设置默认模板
        default_template = self.app_config.get("last_template", "默认模板")
        index = self.template_combo.findText(default_template)
        if index >= 0:
            self.template_combo.setCurrentIndex(index)
        elif self.template_combo.count() > 0:
            self.template_combo.setCurrentIndex(0)
    
    def _on_template_changed(self, template_name: str):
        """模板变更事件"""
        if not template_name:
            return
        
        self._current_template = template_name
        
        # 更新模板内容预览
        self._update_template_preview(template_name)
        
        # 发射信号
        self.template_changed.emit(template_name)
        
        app_logger.info(f"模板已切换: {template_name}")
    
    def _update_template_preview(self, template_name: str):
        """更新模板内容预览"""
        try:
            # 获取模板数据
            template_data = self.format_manager.get_template(template_name)
            
            if template_data:
                # 格式化显示模板内容
                preview_text = self._format_template_content(template_data)
                self.template_preview.setText(preview_text)
            else:
                self.template_preview.setText(f"无法加载模板 '{template_name}' 的内容")
                
        except Exception as e:
            app_logger.error(f"更新模板预览失败: {e}")
            self.template_preview.setText(f"加载模板内容时发生错误: {str(e)}")
    
    def _format_template_content(self, template_data: dict) -> str:
        """格式化模板内容为可读文本"""
        try:
            content_lines = []
            
            # 模板基本信息
            content_lines.append(f"模板名称: {template_data.get('name', '未知')}")
            content_lines.append(f"模板描述: {template_data.get('description', '无描述')}")
            content_lines.append("")
            
            # 排版规则
            elements = template_data.get('elements', {})
            if elements:
                content_lines.append("排版规则:")
                content_lines.append("=" * 40)
                
                for element_name, element_config in elements.items():
                    content_lines.append(f"\n【{element_name}】")
                    
                    if isinstance(element_config, dict):
                        for key, value in element_config.items():
                            if key == 'font':
                                content_lines.append(f"  字体: {value}")
                            elif key == 'size':
                                content_lines.append(f"  字号: {value}")
                            elif key == 'bold':
                                content_lines.append(f"  粗体: {'是' if value else '否'}")
                            elif key == 'alignment':
                                alignment_map = {
                                    'center': '居中',
                                    'left': '左对齐',
                                    'right': '右对齐',
                                    'justify': '两端对齐'
                                }
                                content_lines.append(f"  对齐: {alignment_map.get(value, value)}")
                            elif key == 'line_spacing':
                                content_lines.append(f"  行距: {value}倍")
                            else:
                                content_lines.append(f"  {key}: {value}")
                    else:
                        content_lines.append(f"  配置: {element_config}")
            else:
                content_lines.append("该模板暂无排版规则配置")
            
            return "\n".join(content_lines)
            
        except Exception as e:
            app_logger.error(f"格式化模板内容失败: {e}")
            return f"格式化模板内容时发生错误: {str(e)}"
    

    
    def _import_template(self):
        """导入模板"""
        from ..dialogs.text_parsing_dialog import TextParsingDialog
        from ...core.text_template_parser import TextTemplateParser
        from ...core.ai_connector import AIConnector
        
        try:
            # 创建文本解析对话框
            dialog = TextParsingDialog(self)
            if dialog.exec():
                template_name = dialog.get_template_name()
                template_desc = dialog.get_template_description()
                text_content = dialog.get_text_content()
                
                if not template_name:
                    QMessageBox.warning(self, "提示", "请输入模板名称！")
                    return
                
                if not text_content.strip():
                    QMessageBox.warning(self, "提示", "请输入格式要求文本！")
                    return
                
                # 显示进度对话框
                from PyQt6.QtWidgets import QProgressDialog
                from PyQt6.QtCore import Qt
                
                progress = QProgressDialog("正在使用AI解析格式要求，请稍候...", "取消", 0, 0, self)
                progress.setWindowTitle("生成模板")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setCancelButton(None)  # 禁用取消按钮
                progress.show()
                
                # 处理事件循环，确保对话框显示
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()
                
                # 使用AI解析文本生成模板
                from ...utils.config_manager import config_manager
                api_config = config_manager.get_api_config()
                ai_connector = AIConnector(api_config)
                parser = TextTemplateParser(ai_connector)
                
                success, result = parser.parse_text_to_template(text_content)
                progress.close()
                
                if success:
                    # 保存生成的模板
                    template_data = {
                        "name": template_name,
                        "description": template_desc,
                        "elements": result
                    }
                    
                    # 保存到模板文件
                    import os
                    import json
                    template_file = os.path.join("config/templates", f"{template_name}.json")
                    
                    with open(template_file, 'w', encoding='utf-8') as f:
                        json.dump(template_data, f, ensure_ascii=False, indent=2)
                    
                    # 重新加载模板列表
                    self._load_templates()
                    
                    # 选择新创建的模板
                    index = self.template_combo.findText(template_name)
                    if index >= 0:
                        self.template_combo.setCurrentIndex(index)
                    
                    QMessageBox.information(self, "成功", f"模板 '{template_name}' 已成功生成并保存！")
                    app_logger.info(f"成功生成模板: {template_name}")
                else:
                    QMessageBox.warning(self, "错误", f"生成模板失败: {result}")
                    app_logger.error(f"生成模板失败: {result}")
                    
        except Exception as e:
            app_logger.error(f"导入模板失败: {e}")
            QMessageBox.warning(self, "错误", f"导入模板失败: {str(e)}")
    

    
    def _open_api_config(self):
        """打开API配置"""
        try:
            dialog = ApiConfigDialog(self)
            if dialog.exec():
                app_logger.info("API配置已更新")
                
        except Exception as e:
            app_logger.error(f"打开API配置失败: {e}")
            QMessageBox.warning(self, "错误", f"打开API配置失败: {str(e)}")
    
    def _show_header_footer_dialog(self):
        """显示页眉页脚配置对话框"""
        try:
            dialog = HeaderFooterDialog(self, self.header_footer_config)
            if dialog.exec():
                self.header_footer_config = dialog.config
                app_logger.info("Header/footer configuration updated")
                QMessageBox.information(self, "Success", "Header and footer configuration saved")
                
        except Exception as e:
            app_logger.error(f"Failed to open header/footer configuration: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open header/footer configuration: {str(e)}")
    
    # 公共接口方法
    def get_selected_template(self) -> Optional[str]:
        """获取选择的模板名称"""
        return self._current_template
    
    def get_header_footer_config(self) -> Optional[HeaderFooterConfig]:
        """获取页眉页脚配置"""
        return self.header_footer_config
    
    def on_document_ready(self, file_path: str):
        """文档准备就绪事件"""
        self._document_ready = True
        app_logger.info(f"模板面板收到文档就绪通知: {file_path}")
        
        # TODO: 根据文档特征推荐合适的模板
    
    def set_template_enabled(self, enabled: bool):
        """设置模板相关控件状态"""
        self.template_combo.setEnabled(enabled)
        self.apply_btn.setEnabled(enabled)
        self.edit_template_btn.setEnabled(enabled)