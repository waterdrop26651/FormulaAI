# -*- coding: utf-8 -*-
"""
StatusPanel

职责：
1. VisibleProcessProgress
2. VisibleLogInformation
3. 提供Stop控System
4. VisibleStatusInformation

设计原Rule：
- InformationClear：Progress和LogMinute离Visible
- OperationSimple：One键Stop
- Status明确：WhenPreviousOperationStatusOne目了然
"""

from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
        QLabel, QPushButton, QProgressBar, QTextEdit
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    raise ImportError("PyQt6 is required but not properly installed")

from ...utils.logger import app_logger


class StatusPanel(QWidget):
    """
    StatusPanel
    
    Signal：
    - stop_requested: RequestStopProcess
    """
    
    # Signal definitions
    stop_requested = pyqtSignal()  # Stop request
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State variables
        self._is_processing: bool = False
        self._current_progress: int = 0
        
        # Initialize UI
        self._init_ui()
        
        # SetLogProcess器
        app_logger.add_ui_handler(self._update_log)
        
        app_logger.info("StatusPanel初始化Complete")
    
    def _init_ui(self):
        """
        初始化User界面
        
        Layout：
        ┌─ProgressVisible─────────────────────────────┐
        │ ProgressItem [████████░░] 80% [Stop]    │
        ├─LogVisible─────────────────────────────┤
        │ ProcessLogInformation...                    │
        │ DocumentAnalyzeComplete                       │
        │ StartApplicationTemplate...                    │
        └───────────────────────────────────┘
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        # Progress display area
        progress_group = self._create_progress_group()
        layout.addWidget(progress_group)
        
        # Log display area
        log_group = self._create_log_group()
        layout.addWidget(log_group)
    
    def _create_progress_group(self) -> QGroupBox:
        """创建ProgressVisible组"""
        group = QGroupBox("ProcessProgress")
        layout = QHBoxLayout(group)
        
        # Status label
        self.status_label = QLabel("就绪")
        self.status_label.setMinimumWidth(80)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumWidth(80)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #ffcdd2;
                color: #ffebee;
            }
        """)
        
        # Connect signals
        self.stop_btn.clicked.connect(self._request_stop)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar, 1)  # Stretch factor 1
        layout.addWidget(self.stop_btn)
        
        return group
    
    def _create_log_group(self) -> QGroupBox:
        """创建LogVisible组"""
        group = QGroupBox("ProcessLog")
        layout = QVBoxLayout(group)
        
        # Log text box
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        return group
    
    def _update_log(self, message: str, level: str = "INFO"):
        """
        更NewLogVisible
        
        Args:
            message: LogMessage
            level: LogLevel别
        """
        if self.log_text:
            # Add timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            # Add to log
            self.log_text.append(formatted_message)
            
            # Auto scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _request_stop(self):
        """RequestStopProcess"""
        if self._is_processing:
            self.stop_requested.emit()
            app_logger.info("UserRequestStopProcess")
    
    # Public interface methods
    def start_formatting(self):
        """StartFormattingProcess"""
        self._is_processing = True
        self.status_label.setText("ProcessCenter...")
        self.progress_bar.setValue(0)
        self.stop_btn.setEnabled(True)
        
        # Clear log
        self.log_text.clear()
        
        app_logger.info("StartFormattingProcess")
    
    def stop_formatting(self):
        """StopFormattingProcess"""
        self._is_processing = False
        self.status_label.setText("已Stop")
        self.stop_btn.setEnabled(False)
        
        app_logger.info("FormattingProcess已Stop")
    
    def complete_formatting(self, success: bool = True):
        """CompleteFormattingProcess"""
        self._is_processing = False
        self.stop_btn.setEnabled(False)
        
        if success:
            self.status_label.setText("Complete")
            self.progress_bar.setValue(100)
            app_logger.info("FormattingProcessComplete")
        else:
            self.status_label.setText("Failed")
            app_logger.error("FormattingProcessFailed")
    
    def update_progress(self, value: int, message: str = ""):
        """
        更NewProgress
        
        Args:
            value: ProgressValue (0-100)
            message: ProgressMessage
        """
        self._current_progress = value
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
            app_logger.info(f"Progress更New: {value}% - {message}")
    
    def is_processing(self) -> bool:
        """YesNo正InProcess"""
        return self._is_processing
    
    def get_current_progress(self) -> int:
        """获取WhenPreviousProgress"""
        return self._current_progress
    
    def clear_log(self):
        """清SpaceLog"""
        if self.log_text:
            self.log_text.clear()
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """
        AddLogMessage
        
        Args:
            message: MessageContent
            level: LogLevel别 (INFO, WARNING, ERROR)
        """
        # Set color based on level
        color_map = {
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = color_map.get(level, "black")
        
        # Add colored message
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.log_text:
            self.log_text.append(
                f'<span style="color: {color}">[{timestamp}] [{level}] {message}</span>'
            )
            
            # Auto scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())