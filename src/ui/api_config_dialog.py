# -*- coding: utf-8 -*-
"""
APIConfigurationDialog模块
负责创建和管理APIConfigurationDialog，用于SettingsAI API的相关Parameters。
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFormLayout, QComboBox,
                           QMessageBox, QGroupBox, QDialogButtonBox)
from PyQt6.QtCore import Qt

from ..utils.logger import app_logger
from ..utils.config_manager import config_manager
from ..core.ai_connector import AIConnector

class ApiConfigDialog(QDialog):
    """APIConfigurationDialog，用于SettingsAI API的相关Parameters"""
    
    def __init__(self, parent=None):
        """
        初始化APIConfigurationDialog
        
        Args:
            parent: 父Window
        """
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("ModelConfiguration")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        # LoadWhenPreviousConfiguration
        self.api_config = config_manager.get_api_config()
        
        # Initialize UI
        self.init_ui()
        
        # LoadConfiguration到UI
        self.load_config()
    
    def init_ui(self):
        """
        初始化User界面
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # APIConfiguration组
        api_group = QGroupBox("APIConfiguration")
        form_layout = QFormLayout(api_group)
        
        # API URL
        self.api_url_label = QLabel("API URL:")
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("例如: https://api.deepseek.com/chat/completions")
        form_layout.addRow(self.api_url_label, self.api_url_edit)
        
        # API Key
        self.api_key_label = QLabel("API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Input您的API密钥")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Password mode
        form_layout.addRow(self.api_key_label, self.api_key_edit)
        
        # ModelSelection
        self.model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["deepseek-chat", "deepseek-coder", "gpt-3.5-turbo", "gpt-4", "custom"])
        self.model_combo.setEditable(True)  # Allow custom input
        form_layout.addRow(self.model_label, self.model_combo)
        
        # 最Next更NewTime
        self.last_updated_label = QLabel("最Next更New:")
        self.last_updated_value = QLabel("未Settings")
        form_layout.addRow(self.last_updated_label, self.last_updated_value)
        
        # AddAPIConfiguration组
        main_layout.addWidget(api_group)
        
        # TestJoinButtons
        self.test_btn = QPushButton("TestJoin")
        self.test_btn.clicked.connect(self.test_connection)
        main_layout.addWidget(self.test_btn)
        
        # Buttons区域
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # SetStyle
        self.set_style()
    
    def set_style(self):
        """
        SettingsDialogStyle
        """
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BBDEFB;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #1976D2;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #0D8AEE;
            }
            QPushButton:pressed {
                background-color: #0A6EBD;
            }
            QLineEdit, QComboBox {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
        """)
    
    def load_config(self):
        """
        从ConfigurationCenter加载Data到UI
        """
        # SetAPI URL
        self.api_url_edit.setText(self.api_config.get("api_url", ""))
        
        # SetAPI Key
        self.api_key_edit.setText(self.api_config.get("api_key", ""))
        
        # SetModel
        model = self.api_config.get("model", "deepseek-chat")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        else:
            self.model_combo.setEditText(model)
        
        # Set最Next更NewTime
        last_updated = self.api_config.get("last_updated", "")
        if last_updated:
            self.last_updated_value.setText(last_updated)
    
    def accept(self):
        """
        保存Configuration并ShutdownDialog
        """
        # GetInputValue
        api_url = self.api_url_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        model = self.model_combo.currentText().strip()
        
        # ValidateInput
        if not api_url:
            QMessageBox.warning(self, "InputError", "API URL不能为Space！")
            return
        
        if not api_key:
            QMessageBox.warning(self, "InputError", "API Key不能为Space！")
            return
        
        if not model:
            QMessageBox.warning(self, "InputError", "Model名称不能为Space！")
            return
        
        # UpdateConfiguration
        self.api_config["api_url"] = api_url
        self.api_config["api_key"] = api_key
        self.api_config["model"] = model
        self.api_config["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # SaveConfiguration
        config_manager.save_api_config(self.api_config)
        app_logger.info("APIConfiguration已更New")
        
        # ShutdownDialog
        super().accept()
    
    def test_connection(self):
        """
        TestAPIJoin
        """
        # GetWhenPreviousInput的Configuration
        api_url = self.api_url_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        model = self.model_combo.currentText().strip()
        
        # ValidateInput
        if not api_url or not api_key or not model:
            QMessageBox.warning(self, "InputError", "请填写所HasAPIConfigurationInformation！")
            return
        
        # CreateTemporaryConfiguration
        temp_config = {
            "api_url": api_url,
            "api_key": api_key,
            "model": model
        }
        
        # CreateAIJoin器并Test
        ai_connector = AIConnector(temp_config)
        
        # Visible等待Message
        self.test_btn.setEnabled(False)
        self.test_btn.setText("TestCenter...")
        app_logger.info("正InTestAPIJoin...")
        
        # ValidateConfiguration
        is_valid, message = ai_connector.validate_config()
        
        # ResumeButtonsStatus
        self.test_btn.setEnabled(True)
        self.test_btn.setText("TestJoin")
        
        # VisibleResult
        if is_valid:
            QMessageBox.information(self, "JoinSuccess", "APIJoinTestSuccess！")
            app_logger.info("APIJoinTestSuccess")
        else:
            QMessageBox.critical(self, "JoinFailed", f"APIJoinTestFailed！\nError: {message}")
            app_logger.error(f"APIJoinTestFailed: {message}")
