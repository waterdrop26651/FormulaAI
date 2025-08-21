# -*- coding: utf-8 -*-
"""
主Window模块 V2 - 重构Edition
采用Linus "好品味"原Rule：消除Special情况，简化Data结构

Core理念：
1. Each组Item只做OneItem事并做好
2. 消除超过3Layer缩进的Complex逻辑
3. 用最Simple的方式解决问题
"""

import os
import sys
from typing import Optional, Dict, Any

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
        QSplitter, QApplication
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QFont
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    raise ImportError("PyQt6 is required but not properly installed")

from .panels.document_panel import DocumentPanel
from .panels.template_panel import TemplatePanel
from .panels.status_panel import StatusPanel
from ..utils.logger import app_logger
from ..utils.config_manager import config_manager


class MainWindowV2(QMainWindow):
    """
    主Window V2 - 重构Edition
    
    架构原Rule：
    - 双PanelLayout：Document管理 + TemplateSettings
    - Status管理器：单OneData源
    - Event驱动：PanelBetweenThroughSignal通信
    - 模块化：EachPanelCompletelyIndependent
    """
    
    # Signal definitions
    document_selected = pyqtSignal(str)  # Document selection signal
    template_changed = pyqtSignal(str)   # Template change signal
    formatting_started = pyqtSignal()    # Start formatting signal
    
    def __init__(self):
        super().__init__()
        
        # Application configuration
        self.app_config = config_manager.get_app_config()
        
        # Initialize panels
        self.document_panel: Optional[DocumentPanel] = None
        self.template_panel: Optional[TemplatePanel] = None
        self.status_panel: Optional[StatusPanel] = None
        
        # Initialize UI
        self._init_ui()
        self._connect_signals()
        self._apply_styles()
        
        # Set window properties
        self.setWindowTitle("FormulaAI - AI-Powered Document Formatting Tool")
        self.resize(1000, 700)
        
        app_logger.info("主WindowV2初始化Complete")
    
    def _init_ui(self):
        """
        初始化User界面
        
        Layout结构：
        ┌─────────────────────────────────────┐
        │  [DocumentPanel]  │  [TemplatePanel]        │
        │             │                   │
        │             │                   │
        ├─────────────────────────────────────┤
        │           [StatusPanel]              │
        └─────────────────────────────────────┘
        """
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create horizontal splitter (document panel | template panel)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create panels
        self.document_panel = DocumentPanel()
        self.template_panel = TemplatePanel()
        self.status_panel = StatusPanel()
        
        # Add panels to splitter
        splitter.addWidget(self.document_panel)
        splitter.addWidget(self.template_panel)
        
        # Set splitter ratio (document panel:template panel = 1:1)
        splitter.setSizes([500, 500])
        
        # Add to main layout
        main_layout.addWidget(splitter, 1)  # Stretch factor 1
        main_layout.addWidget(self.status_panel)  # Fixed height
    
    def _connect_signals(self):
        """
        JoinSignal和槽
        
        Event流：
        DocumentPanel → 主Window → TemplatePanel
        TemplatePanel → 主Window → DocumentPanel
        """
        if self.document_panel:
            self.document_panel.document_selected.connect(self._on_document_selected)
            self.document_panel.formatting_requested.connect(self._on_formatting_requested)
        
        if self.template_panel:
            self.template_panel.template_changed.connect(self._on_template_changed)
        
        if self.status_panel:
            self.status_panel.stop_requested.connect(self._on_stop_requested)
    
    def _apply_styles(self):
        """
        ApplicationStyle
        
        设计原Rule：
        - 简洁现代
        - Layer次Clear
        - 专业Tool感
        - StrongSystemShallow色主题，不受SystemDark色模式影响
        """
        # Set全局Font (Skip font settings to avoid compatibility issues)
        # app = QApplication.instance()
        # if app and hasattr(app, 'setFont'):
        #     font = QFont("Microsoft YaHei", 10)
        #     app.setFont(font)
        
        # Force light theme style, override system dark mode
        self.setStyleSheet("""
            /* 主WindowStrongSystemShallow色背景 */
            QMainWindow {
                background-color: #ffffff;
                color: #333333;
            }
            
            /* Minute割器Style */
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
            
            /* StrongSystem所HasQWidgetUseShallow色主题 */
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            
            /* Group框Style */
            QGroupBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #BBDEFB;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #1976D2;
            }
            
            /* Text boxStyle */
            QTextEdit, QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
            
            /* DropdownStyle */
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
            }
            
            /* ButtonsStyle */
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D8AEE;
            }
            QPushButton:pressed {
                background-color: #0A6EBD;
            }
            QPushButton:disabled {
                background-color: #B3E5FC;
                color: #E1F5FE;
            }
            
            /* LabelsStyle */
            QLabel {
                background-color: transparent;
                color: #333333;
            }
            
            /* ProgressItemStyle */
            QProgressBar {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
            }
        """)
    
    # Event handling methods
    def _on_document_selected(self, file_path: str):
        """
        ProcessDocumentSelectionEvent
        
        Args:
            file_path: Selection的Document path
        """
        app_logger.info(f"Document已Selection: {file_path}")
        
        # 通知TemplatePanelDocument已Selection
        if self.template_panel:
            self.template_panel.on_document_ready(file_path)
        
        # Emit signal
        self.document_selected.emit(file_path)
    
    def _on_template_changed(self, template_name: str):
        """
        ProcessTemplate变更Event
        
        Args:
            template_name: Template name
        """
        app_logger.info(f"Template已变更: {template_name}")
        
        # Save最NextUse的Template
        self.app_config["last_template"] = template_name
        config_manager.save_app_config(self.app_config)
        
        # Emit signal
        self.template_changed.emit(template_name)
    
    def _on_formatting_requested(self):
        """
        ProcessFormattingRequestEvent
        """
        app_logger.info("StartFormattingProcess")
        
        # GetWhenPreviousDocument和Template
        if not self.document_panel or not self.template_panel:
            return
        
        doc_path = self.document_panel.get_selected_document()
        template_name = self.template_panel.get_selected_template()
        
        if not doc_path or not template_name:
            app_logger.warning("Document或Template未Selection")
            return
        
        # Update status panel
        if self.status_panel:
            self.status_panel.start_formatting()
        
        # Emit signal
        self.formatting_started.emit()
        
        # TODO: StartupFormatting工作线程
        self._start_formatting_worker(doc_path, template_name)
    
    def _on_stop_requested(self):
        """
        ProcessStopRequestEvent
        
        StopWhenPrevious的FormattingProcess
        """
        app_logger.info("UserRequestStopProcess")
        
        # StopFormatting工作线程
        if hasattr(self, 'formatting_worker') and self.formatting_worker:
            try:
                self.formatting_worker.stop()
                self.formatting_worker.wait(3000)  # Wait up to 3 seconds
                if self.formatting_worker.isRunning():
                    self.formatting_worker.terminate()
                self.formatting_worker = None
                app_logger.info("Formatting工作线程已Stop")
            except Exception as e:
                app_logger.error(f"StopFormatting工作线程Failed: {e}")
        
        # Update status panel
        if self.status_panel:
            self.status_panel.stop_formatting()
    
    def _start_formatting_worker(self, doc_path: str, template_name: str):
        """
        StartupFormatting工作线程
        
        Args:
            doc_path: Document path
            template_name: Template name
        """
        try:
            # Import necessary modules
            from ..core.doc_processor import DocProcessor
            from ..core.ai_connector import AIConnector
            from ..core.format_manager import FormatManager
            from ..core.structure_analyzer import StructureAnalyzer
            from ..utils.config_manager import config_manager
            
            # CreateCore组ItemInstance
            doc_processor = DocProcessor()
            api_config = config_manager.get_api_config()
            ai_connector = AIConnector(api_config)
            format_manager = FormatManager()
            structure_analyzer = StructureAnalyzer()
            
            # ValidateAPIConfiguration
            valid, error_msg = ai_connector.validate_config()
            if not valid:
                if self.status_panel:
                    self.status_panel._update_log(f"APIConfigurationError: {error_msg}", "ERROR")
                return
            
            # Get保存Path
            save_path = None
            if self.document_panel:
                save_path = self.document_panel.get_save_directory()
                if save_path:
                    app_logger.info(f"UseCustom保存Path: {save_path}")
                else:
                    app_logger.info("未Settings保存Path，将保存到原FileDirectory")
            
            # Create并Startup工作线程
            from .main_window import FormattingWorker
            self.formatting_worker = FormattingWorker(
                doc_processor,
                ai_connector,
                format_manager,
                structure_analyzer,
                doc_path,
                template_name,
                save_path
            )
            
            # Connect signals
            self.formatting_worker.progress_updated.connect(
                lambda progress: self.status_panel.update_progress(progress) if self.status_panel else None
            )
            self.formatting_worker.log_message.connect(
                lambda msg: self.status_panel._update_log(msg) if self.status_panel else None
            )
            self.formatting_worker.task_completed.connect(self._on_formatting_completed)
            
            # Start thread
            self.formatting_worker.start()
            app_logger.info(f"StartupFormatting: {doc_path} -> {template_name}")
            
        except Exception as e:
            app_logger.error(f"StartupFormatting工作线程Failed: {e}")
            if self.status_panel:
                self.status_panel.update_log(f"StartupFormattingFailed: {str(e)}", "ERROR")
    
    def _on_formatting_completed(self, success: bool, result: str):
        """
        FormattingComplete回调
        
        Args:
            success: YesNoSuccess
            result: ResultInformation（SuccessTime为输出File path，FailedTime为ErrorInformation）
        """
        if success:
            if self.status_panel:
                self.status_panel._update_log(f"FormattingComplete！File已保存: {result}", "INFO")
            app_logger.info(f"FormattingComplete: {result}")
        else:
            if self.status_panel:
                self.status_panel._update_log(f"FormattingFailed: {result}", "ERROR")
            app_logger.error(f"FormattingFailed: {result}")
        
        # Clean up worker thread
        if hasattr(self, 'formatting_worker'):
            self.formatting_worker = None
    
    # Public interface methods
    def get_document_panel(self) -> Optional[DocumentPanel]:
        """获取DocumentPanel"""
        return self.document_panel
    
    def get_template_panel(self) -> Optional[TemplatePanel]:
        """获取TemplatePanel"""
        return self.template_panel
    
    def get_status_panel(self) -> Optional[StatusPanel]:
        """获取StatusPanel"""
        return self.status_panel
    
    def closeEvent(self, event):
        """
        WindowShutdownEvent
        """
        app_logger.info("主WindowShutdown")
        event.accept()