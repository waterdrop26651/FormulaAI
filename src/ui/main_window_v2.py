# -*- coding: utf-8 -*-
"""
主窗口模块 V2 - 重构版
采用Linus "好品味"原则：消除特殊情况，简化数据结构

核心理念：
1. 每个组件只做一件事并做好
2. 消除超过3层缩进的复杂逻辑
3. 用最简单的方式解决问题
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
from .dialogs.header_footer_dialog import HeaderFooterDialog
from ..core.header_footer_config import HeaderFooterConfig
from ..utils.logger import app_logger
from ..utils.config_manager import config_manager


class MainWindowV2(QMainWindow):
    """
    主窗口 V2 - 重构版
    
    架构原则：
    - 双面板布局：文档管理 + 模板设置
    - 状态管理器：单一数据源
    - 事件驱动：面板间通过信号通信
    - 模块化：每个面板完全独立
    """
    
    # 信号定义
    document_selected = pyqtSignal(str)  # 文档选择信号
    template_changed = pyqtSignal(str)   # 模板变更信号
    formatting_started = pyqtSignal()    # 开始排版信号
    
    def __init__(self):
        super().__init__()
        
        # 应用配置
        self.app_config = config_manager.get_app_config()
        
        # 初始化面板
        self.document_panel: Optional[DocumentPanel] = None
        self.template_panel: Optional[TemplatePanel] = None
        self.status_panel: Optional[StatusPanel] = None
        
        # 页眉页脚配置
        self.header_footer_config: Optional[HeaderFooterConfig] = None
        
        # 初始化UI
        self._init_ui()
        self._connect_signals()
        self._apply_styles()
        
        # 设置窗口属性
        self.setWindowTitle("FormulaAI - AI智能文档排版工具")
        self.resize(1000, 700)
        
        app_logger.info("主窗口V2初始化完成")
    
    def _init_ui(self):
        """
        初始化用户界面
        
        布局结构：
        ┌─────────────────────────────────────┐
        │  [文档面板]  │  [模板面板]        │
        │             │                   │
        │             │                   │
        ├─────────────────────────────────────┤
        │           [状态面板]              │
        └─────────────────────────────────────┘
        """
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建水平分割器（文档面板 | 模板面板）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建面板
        self.document_panel = DocumentPanel()
        self.template_panel = TemplatePanel()
        self.status_panel = StatusPanel()
        
        # 添加面板到分割器
        splitter.addWidget(self.document_panel)
        splitter.addWidget(self.template_panel)
        
        # 设置分割器比例（文档面板:模板面板 = 1:1）
        splitter.setSizes([500, 500])
        
        # 添加到主布局
        main_layout.addWidget(splitter, 1)  # 拉伸因子为1
        main_layout.addWidget(self.status_panel)  # 固定高度
    
    def _connect_signals(self):
        """
        连接信号和槽
        
        事件流：
        文档面板 → 主窗口 → 模板面板
        模板面板 → 主窗口 → 文档面板
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
        应用样式
        
        设计原则：
        - 简洁现代
        - 层次清晰
        - 专业工具感
        - 强制浅色主题，不受系统暗色模式影响
        """
        # 设置全局字体 (跳过字体设置以避免兼容性问题)
        # app = QApplication.instance()
        # if app and hasattr(app, 'setFont'):
        #     font = QFont("Microsoft YaHei", 10)
        #     app.setFont(font)
        
        # 强制浅色主题样式，覆盖系统暗色模式
        self.setStyleSheet("""
            /* 主窗口强制浅色背景 */
            QMainWindow {
                background-color: #ffffff;
                color: #333333;
            }
            
            /* 分割器样式 */
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
            
            /* 强制所有QWidget使用浅色主题 */
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            
            /* 分组框样式 */
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
            
            /* 文本框样式 */
            QTextEdit, QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
            
            /* 下拉框样式 */
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
            
            /* 按钮样式 */
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
            
            /* 标签样式 */
            QLabel {
                background-color: transparent;
                color: #333333;
            }
            
            /* 进度条样式 */
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
    
    # 事件处理方法
    def _on_document_selected(self, file_path: str):
        """
        处理文档选择事件
        
        Args:
            file_path: 选择的文档路径
        """
        app_logger.info(f"文档已选择: {file_path}")
        
        # 通知模板面板文档已选择
        if self.template_panel:
            self.template_panel.on_document_ready(file_path)
        
        # 发射信号
        self.document_selected.emit(file_path)
    
    def _on_template_changed(self, template_name: str):
        """
        处理模板变更事件
        
        Args:
            template_name: 模板名称
        """
        app_logger.info(f"模板已变更: {template_name}")
        
        # 保存最后使用的模板
        self.app_config["last_template"] = template_name
        config_manager.save_app_config(self.app_config)
        
        # 发射信号
        self.template_changed.emit(template_name)
    
    def _on_formatting_requested(self):
        """
        处理排版请求事件
        """
        app_logger.info("开始排版处理")
        
        # 获取当前文档和模板
        if not self.document_panel or not self.template_panel:
            return
        
        doc_path = self.document_panel.get_selected_document()
        template_name = self.template_panel.get_selected_template()
        
        if not doc_path or not template_name:
            app_logger.warning("文档或模板未选择")
            return
        
        # 获取页眉页脚配置
        header_footer_config = self.template_panel.get_header_footer_config()
        if header_footer_config:
            app_logger.info("检测到页眉页脚配置，将应用到文档")
        
        # 更新状态面板
        if self.status_panel:
            self.status_panel.start_formatting()
        
        # 发射信号
        self.formatting_started.emit()
        
        # 启动排版工作线程
        self._start_formatting_worker(doc_path, template_name, header_footer_config)
    
    def _on_stop_requested(self):
        """
        处理停止请求事件
        
        停止当前的排版处理
        """
        app_logger.info("用户请求停止处理")
        
        # 停止排版工作线程
        if hasattr(self, 'formatting_worker') and self.formatting_worker:
            try:
                self.formatting_worker.stop()
                self.formatting_worker.wait(3000)  # 等待最多3秒
                if self.formatting_worker.isRunning():
                    self.formatting_worker.terminate()
                self.formatting_worker = None
                app_logger.info("排版工作线程已停止")
            except Exception as e:
                app_logger.error(f"停止排版工作线程失败: {e}")
        
        # 更新状态面板
        if self.status_panel:
            self.status_panel.stop_formatting()
    
    def _start_formatting_worker(self, doc_path: str, template_name: str, header_footer_config=None):
        """
        启动排版工作线程
        
        Args:
            doc_path: 文档路径
            template_name: 模板名称
            header_footer_config: 页眉页脚配置
        """
        try:
            # 导入必要的模块
            from ..core.doc_processor import DocProcessor
            from ..core.ai_connector import AIConnector
            from ..core.format_manager import FormatManager
            from ..core.structure_analyzer import StructureAnalyzer
            from ..utils.config_manager import config_manager
            
            # 创建核心组件实例
            doc_processor = DocProcessor()
            api_config = config_manager.get_api_config()
            ai_connector = AIConnector(api_config)
            format_manager = FormatManager()
            structure_analyzer = StructureAnalyzer()
            
            # 验证API配置
            valid, error_msg = ai_connector.validate_config()
            if not valid:
                if self.status_panel:
                    self.status_panel._update_log(f"API配置错误: {error_msg}", "ERROR")
                return
            
            # 获取保存路径
            save_path = None
            if self.document_panel:
                save_path = self.document_panel.get_save_directory()
                if save_path:
                    app_logger.info(f"使用自定义保存路径: {save_path}")
                else:
                    app_logger.info("未设置保存路径，将保存到原文件目录")
            
            # 创建并启动工作线程
            from .main_window import FormattingWorker
            self.formatting_worker = FormattingWorker(
                doc_processor,
                ai_connector,
                format_manager,
                structure_analyzer,
                doc_path,
                template_name,
                save_path,
                header_footer_config
            )
            
            # 连接信号
            self.formatting_worker.progress_updated.connect(
                lambda progress: self.status_panel.update_progress(progress) if self.status_panel else None
            )
            self.formatting_worker.log_message.connect(
                lambda msg: self.status_panel._update_log(msg) if self.status_panel else None
            )
            self.formatting_worker.task_completed.connect(self._on_formatting_completed)
            
            # 启动线程
            self.formatting_worker.start()
            app_logger.info(f"启动排版: {doc_path} -> {template_name}")
            
        except Exception as e:
            app_logger.error(f"启动排版工作线程失败: {e}")
            if self.status_panel:
                self.status_panel.update_log(f"启动排版失败: {str(e)}", "ERROR")
    
    def _on_formatting_completed(self, success: bool, result: str):
        """
        排版完成回调
        
        Args:
            success: 是否成功
            result: 结果信息（成功时为输出文件路径，失败时为错误信息）
        """
        if success:
            if self.status_panel:
                self.status_panel._update_log(f"排版完成！文件已保存: {result}", "INFO")
            app_logger.info(f"排版完成: {result}")
        else:
            if self.status_panel:
                self.status_panel._update_log(f"排版失败: {result}", "ERROR")
            app_logger.error(f"排版失败: {result}")
        
        # 清理工作线程
        if hasattr(self, 'formatting_worker'):
            self.formatting_worker = None
    
    # 公共接口方法
    def get_document_panel(self) -> Optional[DocumentPanel]:
        """获取文档面板"""
        return self.document_panel
    
    def get_template_panel(self) -> Optional[TemplatePanel]:
        """获取模板面板"""
        return self.template_panel
    
    def get_status_panel(self) -> Optional[StatusPanel]:
        """获取状态面板"""
        return self.status_panel
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        app_logger.info("主窗口关闭")
        event.accept()