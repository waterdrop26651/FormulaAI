# -*- coding: utf-8 -*-
"""
文档管理面板

职责：
1. 文档选择和验证
2. 文档信息显示
3. 文档结构分析结果展示
4. 保存位置设置

设计原则：
- 单一职责：只管文档相关操作
- 无特殊情况：统一的错误处理
- 简洁明了：最多2层缩进
"""

import os
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
        QLabel, QPushButton, QFileDialog, QTextEdit,
        QGridLayout, QMessageBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QFont
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    raise ImportError("PyQt6 is required but not properly installed")

from ...utils.logger import app_logger
from ...utils.config_manager import config_manager
from ...utils.file_utils import is_valid_docx
from ...core.structure_analyzer import StructureAnalyzer


class DocumentPanel(QWidget):
    """
    文档管理面板
    
    信号：
    - document_selected: 文档选择完成
    - formatting_requested: 请求开始排版
    """
    
    # 信号定义
    document_selected = pyqtSignal(str)  # 文档路径
    formatting_requested = pyqtSignal()  # 排版请求
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self._selected_document: Optional[str] = None
        self._save_directory: Optional[str] = None
        
        # 核心组件
        self.structure_analyzer = StructureAnalyzer()
        self.app_config = config_manager.get_app_config()
        
        # 初始化UI
        self._init_ui()
        self._load_config()
        
        app_logger.info("文档面板初始化完成")
    
    def _init_ui(self):
        """
        初始化用户界面
        
        布局（简化版）：
        ┌─文档选择─────────┐
        │ 文件路径         │
        │ [浏览] [分析]    │
        ├─保存设置─────────┤
        │ 保存位置         │
        └─操作按钮─────────┘
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 文档选择区
        doc_group = self._create_document_selection_group()
        layout.addWidget(doc_group)
        
        # 保存设置区
        save_group = self._create_save_settings_group()
        layout.addWidget(save_group)
        
        # 操作按钮区
        action_group = self._create_action_buttons_group()
        layout.addWidget(action_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _create_document_selection_group(self) -> QGroupBox:
        """创建文档选择组"""
        group = QGroupBox("文档选择")
        layout = QGridLayout(group)
        
        # 文档路径标签
        self.doc_path_label = QLabel("请选择Word文档:")
        self.doc_path_value = QLabel("未选择文件")
        self.doc_path_value.setStyleSheet("color: gray; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        
        # 按钮
        self.browse_btn = QPushButton("浏览...")
        
        # 连接信号
        self.browse_btn.clicked.connect(self._select_document)
        
        # 布局
        layout.addWidget(self.doc_path_label, 0, 0)
        layout.addWidget(self.doc_path_value, 0, 1)
        layout.addWidget(self.browse_btn, 0, 2)
        
        return group
    

    
    def _create_save_settings_group(self) -> QGroupBox:
        """创建保存设置组"""
        group = QGroupBox("保存设置")
        layout = QGridLayout(group)
        
        # 保存路径
        self.save_path_label = QLabel("保存位置:")
        self.save_path_value = QLabel("与源文件相同目录")
        self.save_path_value.setStyleSheet("color: gray; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        self.save_browse_btn = QPushButton("浏览...")
        
        # 连接信号
        self.save_browse_btn.clicked.connect(self._select_save_directory)
        
        layout.addWidget(self.save_path_label, 0, 0)
        layout.addWidget(self.save_path_value, 0, 1)
        layout.addWidget(self.save_browse_btn, 0, 2)
        
        return group
    
    def _create_action_buttons_group(self) -> QGroupBox:
        """创建操作按钮组"""
        group = QGroupBox("操作")
        layout = QHBoxLayout(group)
        
        # 开始排版按钮
        self.format_btn = QPushButton("开始排版")
        self.format_btn.setEnabled(False)
        self.format_btn.setMinimumHeight(40)
        self.format_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0D8AEE;
            }
            QPushButton:disabled {
                background-color: #B3E5FC;
                color: #E1F5FE;
            }
        """)
        
        # 连接信号
        self.format_btn.clicked.connect(self._request_formatting)
        
        layout.addStretch()
        layout.addWidget(self.format_btn)
        layout.addStretch()
        
        return group
    
    def _load_config(self):
        """加载配置"""
        # 加载保存路径配置
        save_path = self.app_config.get("save_path", "")
        if save_path and os.path.exists(save_path):
            self._save_directory = save_path
            self.save_path_value.setText(save_path)
            self.save_path_value.setStyleSheet("color: black; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
    
    def _select_document(self):
        """选择文档"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择Word文档",
            "",
            "Word文档 (*.docx)"
        )
        
        if not file_path:
            return
        
        # 验证文档
        if not is_valid_docx(file_path):
            QMessageBox.warning(self, "无效文档", "所选文件不是有效的Word文档！")
            return
        
        # 更新状态
        self._selected_document = file_path
        self.doc_path_value.setText(os.path.basename(file_path))
        self.doc_path_value.setStyleSheet("color: black; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        self.doc_path_value.setToolTip(file_path)
        
        # 启用按钮
        self.format_btn.setEnabled(True)
        
        # 发射信号
        self.document_selected.emit(file_path)
        
        app_logger.info(f"文档已选择: {file_path}")
    

    
    def _select_save_directory(self):
        """选择保存目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择保存位置",
            self._save_directory or ""
        )
        
        if directory:
            self._save_directory = directory
            self.save_path_value.setText(directory)
            self.save_path_value.setStyleSheet("color: black; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
            
            # 保存配置
            self.app_config["save_path"] = directory
            config_manager.save_app_config(self.app_config)
            
            app_logger.info(f"保存位置已设置: {directory}")
    
    def _request_formatting(self):
        """请求开始排版"""
        if not self._selected_document:
            QMessageBox.warning(self, "提示", "请先选择文档！")
            return
        
        # 发射排版请求信号
        self.formatting_requested.emit()
    
    # 公共接口方法
    def get_selected_document(self) -> Optional[str]:
        """获取选择的文档路径"""
        return self._selected_document
    
    def get_save_directory(self) -> Optional[str]:
        """获取保存目录"""
        return self._save_directory
    
    def set_formatting_enabled(self, enabled: bool):
        """设置排版按钮状态"""
        self.format_btn.setEnabled(enabled and self._selected_document is not None)