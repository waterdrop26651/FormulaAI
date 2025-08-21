# -*- coding: utf-8 -*-
"""
状态面板

职责：
1. 显示处理进度
2. 显示日志信息
3. 提供停止控制
4. 显示状态信息

设计原则：
- 信息清晰：进度和日志分离显示
- 操作简单：一键停止
- 状态明确：当前操作状态一目了然
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
    状态面板
    
    信号：
    - stop_requested: 请求停止处理
    """
    
    # 信号定义
    stop_requested = pyqtSignal()  # 停止请求
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self._is_processing: bool = False
        self._current_progress: int = 0
        
        # 初始化UI
        self._init_ui()
        
        # 设置日志处理器
        app_logger.add_ui_handler(self._update_log)
        
        app_logger.info("状态面板初始化完成")
    
    def _init_ui(self):
        """
        初始化用户界面
        
        布局：
        ┌─进度显示─────────────────────────────┐
        │ 进度条 [████████░░] 80% [停止]    │
        ├─日志显示─────────────────────────────┤
        │ 处理日志信息...                    │
        │ 文档分析完成                       │
        │ 开始应用模板...                    │
        └───────────────────────────────────┘
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)
        
        # 进度显示区
        progress_group = self._create_progress_group()
        layout.addWidget(progress_group)
        
        # 日志显示区
        log_group = self._create_log_group()
        layout.addWidget(log_group)
    
    def _create_progress_group(self) -> QGroupBox:
        """创建进度显示组"""
        group = QGroupBox("处理进度")
        layout = QHBoxLayout(group)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setMinimumWidth(80)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        # 停止按钮
        self.stop_btn = QPushButton("停止")
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
        
        # 连接信号
        self.stop_btn.clicked.connect(self._request_stop)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar, 1)  # 拉伸因子为1
        layout.addWidget(self.stop_btn)
        
        return group
    
    def _create_log_group(self) -> QGroupBox:
        """创建日志显示组"""
        group = QGroupBox("处理日志")
        layout = QVBoxLayout(group)
        
        # 日志文本框
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
        更新日志显示
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        if self.log_text:
            # 添加时间戳
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            # 添加到日志
            self.log_text.append(formatted_message)
            
            # 自动滚动到底部
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _request_stop(self):
        """请求停止处理"""
        if self._is_processing:
            self.stop_requested.emit()
            app_logger.info("用户请求停止处理")
    
    # 公共接口方法
    def start_formatting(self):
        """开始排版处理"""
        self._is_processing = True
        self.status_label.setText("处理中...")
        self.progress_bar.setValue(0)
        self.stop_btn.setEnabled(True)
        
        # 清空日志
        self.log_text.clear()
        
        app_logger.info("开始排版处理")
    
    def stop_formatting(self):
        """停止排版处理"""
        self._is_processing = False
        self.status_label.setText("已停止")
        self.stop_btn.setEnabled(False)
        
        app_logger.info("排版处理已停止")
    
    def complete_formatting(self, success: bool = True):
        """完成排版处理"""
        self._is_processing = False
        self.stop_btn.setEnabled(False)
        
        if success:
            self.status_label.setText("完成")
            self.progress_bar.setValue(100)
            app_logger.info("排版处理完成")
        else:
            self.status_label.setText("失败")
            app_logger.error("排版处理失败")
    
    def update_progress(self, value: int, message: str = ""):
        """
        更新进度
        
        Args:
            value: 进度值 (0-100)
            message: 进度消息
        """
        self._current_progress = value
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
            app_logger.info(f"进度更新: {value}% - {message}")
    
    def is_processing(self) -> bool:
        """是否正在处理"""
        return self._is_processing
    
    def get_current_progress(self) -> int:
        """获取当前进度"""
        return self._current_progress
    
    def clear_log(self):
        """清空日志"""
        if self.log_text:
            self.log_text.clear()
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """
        添加日志消息
        
        Args:
            message: 消息内容
            level: 日志级别 (INFO, WARNING, ERROR)
        """
        # 根据级别设置颜色
        color_map = {
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = color_map.get(level, "black")
        
        # 添加带颜色的消息
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.log_text:
            self.log_text.append(
                f'<span style="color: {color}">[{timestamp}] [{level}] {message}</span>'
            )
            
            # 自动滚动到底部
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())