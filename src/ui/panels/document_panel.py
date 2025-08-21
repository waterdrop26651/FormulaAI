# -*- coding: utf-8 -*-
"""
Document Management Panel

Responsibilities:
1. Document selection and validation
2. Document information display
3. Document structure analysis results display
4. Save location settings

Design Principles:
- Single responsibility: Only handles document-related operations
- No special cases: Unified error handling
- Simple and clear: Maximum 2 levels of indentation
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
    Document Management Panel
    
    Signals:
    - document_selected: Document selection completed
    - formatting_requested: Request to start formatting
    """
    
    # Signal definitions
    document_selected = pyqtSignal(str)  # Document path
    formatting_requested = pyqtSignal()  # Formatting request
    
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
        
        app_logger.info("Document panel initialization completed")
    
    def _init_ui(self):
        """
        Initialize user interface
        
        Layout (simplified):
        ┌─Document Selection──┐
        │ File path           │
        │ [Browse] [Analyze]  │
        ├─Save Settings──────┤
        │ Save location       │
        └─Action Buttons─────┘
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
        """Create document selection group"""
        group = QGroupBox("Document Selection")
        layout = QGridLayout(group)
        
        # Document path labels
        self.doc_path_label = QLabel("Select Word Document:")
        self.doc_path_value = QLabel("No file selected")
        self.doc_path_value.setStyleSheet("color: gray; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        
        # Buttons
        self.browse_btn = QPushButton("Browse...")
        
        # 连接信号
        self.browse_btn.clicked.connect(self._select_document)
        
        # 布局
        layout.addWidget(self.doc_path_label, 0, 0)
        layout.addWidget(self.doc_path_value, 0, 1)
        layout.addWidget(self.browse_btn, 0, 2)
        
        return group
    

    
    def _create_save_settings_group(self) -> QGroupBox:
        """Create save settings group"""
        group = QGroupBox("Save Settings")
        layout = QGridLayout(group)
        
        # Save path
        self.save_path_label = QLabel("Save Location:")
        self.save_path_value = QLabel("Same directory as source file")
        self.save_path_value.setStyleSheet("color: gray; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        self.save_browse_btn = QPushButton("Browse...")
        
        # 连接信号
        self.save_browse_btn.clicked.connect(self._select_save_directory)
        
        layout.addWidget(self.save_path_label, 0, 0)
        layout.addWidget(self.save_path_value, 0, 1)
        layout.addWidget(self.save_browse_btn, 0, 2)
        
        return group
    
    def _create_action_buttons_group(self) -> QGroupBox:
        """Create action buttons group"""
        group = QGroupBox("Actions")
        layout = QHBoxLayout(group)
        
        # Start formatting button
        self.format_btn = QPushButton("Start Formatting")
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
        """Select document"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Word Document",
            "",
            "Word Documents (*.docx)"
        )
        
        if not file_path:
            return
        
        # Validate document
        if not is_valid_docx(file_path):
            QMessageBox.warning(self, "Invalid Document", "The selected file is not a valid Word document!")
            return
        
        # Update status
        self._selected_document = file_path
        self.doc_path_value.setText(os.path.basename(file_path))
        self.doc_path_value.setStyleSheet("color: black; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        self.doc_path_value.setToolTip(file_path)
        
        # Enable buttons
        self.format_btn.setEnabled(True)
        
        # Emit signal
        self.document_selected.emit(file_path)
        
        app_logger.info(f"Document selected: {file_path}")
    

    
    def _select_save_directory(self):
        """Select save directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Save Location",
            self._save_directory or ""
        )
        
        if directory:
            self._save_directory = directory
            self.save_path_value.setText(directory)
            self.save_path_value.setStyleSheet("color: black; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
            
            # Save configuration
            self.app_config["save_path"] = directory
            config_manager.save_app_config(self.app_config)
            
            app_logger.info(f"Save location set: {directory}")
    
    def _request_formatting(self):
        """Request to start formatting"""
        if not self._selected_document:
            QMessageBox.warning(self, "Notice", "Please select a document first!")
            return
        
        # Emit formatting request signal
        self.formatting_requested.emit()
    
    # Public interface methods
    def get_selected_document(self) -> Optional[str]:
        """Get selected document path"""
        return self._selected_document
    
    def get_save_directory(self) -> Optional[str]:
        """Get save directory"""
        return self._save_directory
    
    def set_formatting_enabled(self, enabled: bool):
        """Set formatting button state"""
        self.format_btn.setEnabled(enabled and self._selected_document is not None)