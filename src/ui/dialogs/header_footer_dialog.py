# -*- coding: utf-8 -*-
"""
页眉页脚配置对话框
提供用户友好的页眉页脚设置界面
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QFormLayout, QCheckBox, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QMessageBox, QLabel, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ...core.header_footer_config import HeaderFooterConfig
from ...utils.logger import app_logger

class HeaderFooterDialog(QDialog):
    """页眉页脚配置对话框"""
    
    def __init__(self, parent=None, config: HeaderFooterConfig = None):
        super().__init__(parent)
        self.setWindowTitle("Header & Footer Settings")
        self.setModal(True)
        self.resize(650, 600)
        
        # 初始化配置
        self.config = config if config else HeaderFooterConfig()
        
        # 设置UI
        self.setup_ui()
        
        # 加载配置到UI
        self.load_config_to_ui()
        
        # 连接信号
        self.connect_signals()
        
        app_logger.debug("页眉页脚配置对话框初始化完成")
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 基础设置选项卡
        basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(basic_tab, "Basic Settings")
        
        # 高级设置选项卡
        advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, "Advanced Settings")
        
        # 页码设置选项卡
        page_number_tab = self.create_page_number_tab()
        self.tab_widget.addTab(page_number_tab, "Page Numbers")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setToolTip("Preview header and footer effects")
        button_layout.addWidget(self.preview_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setToolTip("Reset all settings")
        button_layout.addWidget(self.reset_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_basic_tab(self):
        """Create basic settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 页眉设置组
        header_group = QGroupBox("Header Settings")
        header_layout = QFormLayout(header_group)
        
        self.enable_header_cb = QCheckBox("Enable Header")
        header_layout.addRow(self.enable_header_cb)
        
        self.header_content_edit = QLineEdit()
        self.header_content_edit.setPlaceholderText("Enter header content")
        header_layout.addRow("Header Content:", self.header_content_edit)
        
        self.header_alignment_combo = QComboBox()
        self.header_alignment_combo.addItems(["Left Align", "Center", "Right Align", "Justify"])
        self.header_alignment_combo.setCurrentText("Center")
        header_layout.addRow("Alignment:", self.header_alignment_combo)
        
        # 页眉字体设置
        header_font_layout = QHBoxLayout()
        
        self.header_font_combo = QComboBox()
        self.header_font_combo.addItems(["SimSun", "SimHei", "KaiTi", "FangSong", "Microsoft YaHei", "Times New Roman", "Arial"])
        self.header_font_combo.setCurrentText("Times New Roman")
        header_font_layout.addWidget(QLabel("Font:"))
        header_font_layout.addWidget(self.header_font_combo)
        
        self.header_font_size_spin = QSpinBox()
        self.header_font_size_spin.setRange(6, 72)
        self.header_font_size_spin.setValue(10)
        self.header_font_size_spin.setSuffix(" pt")
        header_font_layout.addWidget(QLabel("Size:"))
        header_font_layout.addWidget(self.header_font_size_spin)
        
        self.header_bold_cb = QCheckBox("Bold")
        header_font_layout.addWidget(self.header_bold_cb)
        
        self.header_italic_cb = QCheckBox("Italic")
        header_font_layout.addWidget(self.header_italic_cb)
        
        header_font_layout.addStretch()
        header_layout.addRow("Font Settings:", header_font_layout)
        
        layout.addWidget(header_group)
        
        # 页脚设置组
        footer_group = QGroupBox("Footer Settings")
        footer_layout = QFormLayout(footer_group)
        
        self.enable_footer_cb = QCheckBox("Enable Footer")
        footer_layout.addRow(self.enable_footer_cb)
        
        self.footer_content_edit = QLineEdit()
        self.footer_content_edit.setPlaceholderText("Enter footer content")
        footer_layout.addRow("Footer Content:", self.footer_content_edit)
        
        self.footer_alignment_combo = QComboBox()
        self.footer_alignment_combo.addItems(["Left Align", "Center", "Right Align", "Justify"])
        self.footer_alignment_combo.setCurrentText("Center")
        footer_layout.addRow("Alignment:", self.footer_alignment_combo)
        
        # 页脚字体设置
        footer_font_layout = QHBoxLayout()
        
        self.footer_font_combo = QComboBox()
        self.footer_font_combo.addItems(["SimSun", "SimHei", "KaiTi", "FangSong", "Microsoft YaHei", "Times New Roman", "Arial"])
        self.footer_font_combo.setCurrentText("Times New Roman")
        footer_font_layout.addWidget(QLabel("Font:"))
        footer_font_layout.addWidget(self.footer_font_combo)
        
        self.footer_font_size_spin = QSpinBox()
        self.footer_font_size_spin.setRange(6, 72)
        self.footer_font_size_spin.setValue(9)
        self.footer_font_size_spin.setSuffix(" pt")
        footer_font_layout.addWidget(QLabel("Size:"))
        footer_font_layout.addWidget(self.footer_font_size_spin)
        
        self.footer_bold_cb = QCheckBox("Bold")
        footer_font_layout.addWidget(self.footer_bold_cb)
        
        self.footer_italic_cb = QCheckBox("Italic")
        footer_font_layout.addWidget(self.footer_italic_cb)
        
        footer_font_layout.addStretch()
        footer_layout.addRow("Font Settings:", footer_font_layout)
        
        layout.addWidget(footer_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 高级选项组
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.different_first_page_cb = QCheckBox("Different first page header/footer")
        self.different_first_page_cb.setToolTip("Use different header and footer for the first page")
        advanced_layout.addWidget(self.different_first_page_cb)
        
        self.different_odd_even_cb = QCheckBox("Different odd/even page headers/footers")
        self.different_odd_even_cb.setToolTip("Use different headers and footers for odd and even pages")
        advanced_layout.addWidget(self.different_odd_even_cb)
        
        self.three_column_layout_cb = QCheckBox("Use three-column layout (Left-Center-Right)")
        self.three_column_layout_cb.setToolTip("Divide header and footer into left, center, and right columns")
        advanced_layout.addWidget(self.three_column_layout_cb)
        
        layout.addWidget(advanced_group)
        
        # 首页设置组
        self.first_page_group = QGroupBox("First Page Settings")
        self.first_page_group.setEnabled(False)
        first_page_layout = QFormLayout(self.first_page_group)
        
        self.first_page_header_edit = QLineEdit()
        self.first_page_header_edit.setPlaceholderText("First page header content")
        first_page_layout.addRow("First Page Header:", self.first_page_header_edit)
        
        self.first_page_footer_edit = QLineEdit()
        self.first_page_footer_edit.setPlaceholderText("First page footer content")
        first_page_layout.addRow("First Page Footer:", self.first_page_footer_edit)
        
        layout.addWidget(self.first_page_group)
        
        # 偶数页设置组
        self.even_page_group = QGroupBox("Even Page Settings")
        self.even_page_group.setEnabled(False)
        even_page_layout = QFormLayout(self.even_page_group)
        
        self.even_page_header_edit = QLineEdit()
        self.even_page_header_edit.setPlaceholderText("Even page header content")
        even_page_layout.addRow("Even Page Header:", self.even_page_header_edit)
        
        self.even_page_footer_edit = QLineEdit()
        self.even_page_footer_edit.setPlaceholderText("Even page footer content")
        even_page_layout.addRow("Even Page Footer:", self.even_page_footer_edit)
        
        layout.addWidget(self.even_page_group)
        
        # 三栏布局设置组
        self.three_column_group = QGroupBox("Three-Column Layout Settings")
        self.three_column_group.setEnabled(False)
        three_column_layout = QFormLayout(self.three_column_group)
        
        # 页眉三栏
        self.header_left_edit = QLineEdit()
        self.header_left_edit.setPlaceholderText("Header left content")
        three_column_layout.addRow("Header Left:", self.header_left_edit)
        
        self.header_center_edit = QLineEdit()
        self.header_center_edit.setPlaceholderText("Header center content")
        three_column_layout.addRow("Header Center:", self.header_center_edit)
        
        self.header_right_edit = QLineEdit()
        self.header_right_edit.setPlaceholderText("Header right content")
        three_column_layout.addRow("Header Right:", self.header_right_edit)
        
        # 页脚三栏
        self.footer_left_edit = QLineEdit()
        self.footer_left_edit.setPlaceholderText("Footer left content")
        three_column_layout.addRow("Footer Left:", self.footer_left_edit)
        
        self.footer_center_edit = QLineEdit()
        self.footer_center_edit.setPlaceholderText("Footer center content")
        three_column_layout.addRow("Footer Center:", self.footer_center_edit)
        
        self.footer_right_edit = QLineEdit()
        self.footer_right_edit.setPlaceholderText("Footer right content")
        three_column_layout.addRow("Footer Right:", self.footer_right_edit)
        
        layout.addWidget(self.three_column_group)
        
        layout.addStretch()
        return widget
    
    def create_page_number_tab(self):
        """Create page number settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 页码设置组
        page_number_group = QGroupBox("Page Number Settings")
        page_number_layout = QFormLayout(page_number_group)
        
        self.include_page_number_cb = QCheckBox("Include Page Numbers")
        page_number_layout.addRow(self.include_page_number_cb)
        
        self.page_number_position_combo = QComboBox()
        self.page_number_position_combo.addItems([
            "Header Left", "Header Center", "Header Right",
            "Footer Left", "Footer Center", "Footer Right"
        ])
        self.page_number_position_combo.setCurrentText("Footer Center")
        page_number_layout.addRow("Page Number Position:", self.page_number_position_combo)
        
        self.page_number_format_edit = QLineEdit()
        self.page_number_format_edit.setText("Page {page}")
        self.page_number_format_edit.setPlaceholderText("Use {page} as page number placeholder")
        page_number_layout.addRow("Page Number Format:", self.page_number_format_edit)
        
        layout.addWidget(page_number_group)
        
        # 预览区域
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Header and footer preview will be displayed here...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        return widget
    
    def connect_signals(self):
        """连接信号"""
        # 按钮信号
        self.ok_btn.clicked.connect(self.accept_config)
        self.cancel_btn.clicked.connect(self.reject)
        self.preview_btn.clicked.connect(self.preview_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        # 复选框信号
        self.different_first_page_cb.toggled.connect(self.first_page_group.setEnabled)
        self.different_odd_even_cb.toggled.connect(self.even_page_group.setEnabled)
        self.three_column_layout_cb.toggled.connect(self.three_column_group.setEnabled)
        
        # 内容变化信号（用于实时预览）
        self.header_content_edit.textChanged.connect(self.update_preview)
        self.footer_content_edit.textChanged.connect(self.update_preview)
        self.page_number_format_edit.textChanged.connect(self.update_preview)
        self.include_page_number_cb.toggled.connect(self.update_preview)
    
    def load_config_to_ui(self):
        """从配置加载到UI"""
        # 基础设置
        self.enable_header_cb.setChecked(self.config.enable_header)
        self.enable_footer_cb.setChecked(self.config.enable_footer)
        
        self.header_content_edit.setText(self.config.header_content)
        self.footer_content_edit.setText(self.config.footer_content)
        
        # 对齐方式
        alignment_map = {"left": "左对齐", "center": "居中", "right": "右对齐", "justify": "两端对齐"}
        self.header_alignment_combo.setCurrentText(alignment_map.get(self.config.header_alignment, "居中"))
        self.footer_alignment_combo.setCurrentText(alignment_map.get(self.config.footer_alignment, "居中"))
        
        # 字体设置
        self.header_font_combo.setCurrentText(self.config.header_font)
        self.footer_font_combo.setCurrentText(self.config.footer_font)
        self.header_font_size_spin.setValue(self.config.header_font_size)
        self.footer_font_size_spin.setValue(self.config.footer_font_size)
        self.header_bold_cb.setChecked(self.config.header_bold)
        self.footer_bold_cb.setChecked(self.config.footer_bold)
        self.header_italic_cb.setChecked(self.config.header_italic)
        self.footer_italic_cb.setChecked(self.config.footer_italic)
        
        # 高级设置
        self.different_first_page_cb.setChecked(self.config.different_first_page)
        self.different_odd_even_cb.setChecked(self.config.different_odd_even)
        self.three_column_layout_cb.setChecked(self.config.use_three_column_layout)
        
        # 首页设置
        self.first_page_header_edit.setText(self.config.first_page_header_content)
        self.first_page_footer_edit.setText(self.config.first_page_footer_content)
        
        # 偶数页设置
        self.even_page_header_edit.setText(self.config.even_page_header_content)
        self.even_page_footer_edit.setText(self.config.even_page_footer_content)
        
        # 三栏布局
        self.header_left_edit.setText(self.config.header_left_content)
        self.header_center_edit.setText(self.config.header_center_content)
        self.header_right_edit.setText(self.config.header_right_content)
        self.footer_left_edit.setText(self.config.footer_left_content)
        self.footer_center_edit.setText(self.config.footer_center_content)
        self.footer_right_edit.setText(self.config.footer_right_content)
        
        # 页码设置
        self.include_page_number_cb.setChecked(self.config.include_page_number)
        
        position_map = {
            "header_left": "页眉左侧", "header_center": "页眉中间", "header_right": "页眉右侧",
            "footer_left": "页脚左侧", "footer_center": "页脚中间", "footer_right": "页脚右侧"
        }
        self.page_number_position_combo.setCurrentText(position_map.get(self.config.page_number_position, "页脚中间"))
        self.page_number_format_edit.setText(self.config.page_number_format)
        
        # 更新预览
        self.update_preview()
    
    def get_config(self) -> HeaderFooterConfig:
        """从UI获取配置"""
        config = HeaderFooterConfig()
        
        # 基础设置
        config.enable_header = self.enable_header_cb.isChecked()
        config.enable_footer = self.enable_footer_cb.isChecked()
        
        config.header_content = self.header_content_edit.text()
        config.footer_content = self.footer_content_edit.text()
        
        # 对齐方式
        alignment_map = {"左对齐": "left", "居中": "center", "右对齐": "right", "两端对齐": "justify"}
        config.header_alignment = alignment_map.get(self.header_alignment_combo.currentText(), "center")
        config.footer_alignment = alignment_map.get(self.footer_alignment_combo.currentText(), "center")
        
        # 字体设置
        config.header_font = self.header_font_combo.currentText()
        config.footer_font = self.footer_font_combo.currentText()
        config.header_font_size = self.header_font_size_spin.value()
        config.footer_font_size = self.footer_font_size_spin.value()
        config.header_bold = self.header_bold_cb.isChecked()
        config.footer_bold = self.footer_bold_cb.isChecked()
        config.header_italic = self.header_italic_cb.isChecked()
        config.footer_italic = self.footer_italic_cb.isChecked()
        
        # 高级设置
        config.different_first_page = self.different_first_page_cb.isChecked()
        config.different_odd_even = self.different_odd_even_cb.isChecked()
        config.use_three_column_layout = self.three_column_layout_cb.isChecked()
        
        # 首页设置
        config.first_page_header_content = self.first_page_header_edit.text()
        config.first_page_footer_content = self.first_page_footer_edit.text()
        
        # 偶数页设置
        config.even_page_header_content = self.even_page_header_edit.text()
        config.even_page_footer_content = self.even_page_footer_edit.text()
        
        # 三栏布局
        config.header_left_content = self.header_left_edit.text()
        config.header_center_content = self.header_center_edit.text()
        config.header_right_content = self.header_right_edit.text()
        config.footer_left_content = self.footer_left_edit.text()
        config.footer_center_content = self.footer_center_edit.text()
        config.footer_right_content = self.footer_right_edit.text()
        
        # 页码设置
        config.include_page_number = self.include_page_number_cb.isChecked()
        
        position_map = {
            "页眉左侧": "header_left", "页眉中间": "header_center", "页眉右侧": "header_right",
            "页脚左侧": "footer_left", "页脚中间": "footer_center", "页脚右侧": "footer_right"
        }
        config.page_number_position = position_map.get(self.page_number_position_combo.currentText(), "footer_center")
        config.page_number_format = self.page_number_format_edit.text()
        
        return config
    
    def accept_config(self):
        """确认配置"""
        try:
            config = self.get_config()
            
            # 验证配置
            is_valid, error_msg = config.validate()
            if not is_valid:
                QMessageBox.warning(self, "配置错误", error_msg)
                return
            
            self.config = config
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
            app_logger.error(f"保存页眉页脚配置失败: {str(e)}")
    
    def preview_settings(self):
        """预览设置"""
        try:
            config = self.get_config()
            
            # 验证配置
            is_valid, error_msg = config.validate()
            if not is_valid:
                QMessageBox.warning(self, "配置错误", error_msg)
                return
            
            # 生成预览文本
            preview_text = self.generate_preview_text(config)
            self.preview_text.setPlainText(preview_text)
            
            # 切换到页码设置选项卡显示预览
            self.tab_widget.setCurrentIndex(2)
            
        except Exception as e:
            QMessageBox.warning(self, "预览失败", f"生成预览失败: {str(e)}")
    
    def generate_preview_text(self, config: HeaderFooterConfig) -> str:
        """生成预览文本"""
        lines = []
        lines.append("=== 页眉页脚预览 ===")
        lines.append("")
        
        # 页眉预览
        if config.enable_header:
            header_content = config.get_effective_header_content()
            if header_content.strip():
                lines.append(f"页眉: {header_content}")
                lines.append(f"  字体: {config.header_font} {config.header_font_size}pt")
                lines.append(f"  对齐: {config.header_alignment}")
                if config.header_bold or config.header_italic:
                    style = []
                    if config.header_bold:
                        style.append("粗体")
                    if config.header_italic:
                        style.append("斜体")
                    lines.append(f"  样式: {', '.join(style)}")
                lines.append("")
        
        # 页脚预览
        if config.enable_footer:
            footer_content = config.get_effective_footer_content()
            if footer_content.strip():
                lines.append(f"页脚: {footer_content}")
                lines.append(f"  字体: {config.footer_font} {config.footer_font_size}pt")
                lines.append(f"  对齐: {config.footer_alignment}")
                if config.footer_bold or config.footer_italic:
                    style = []
                    if config.footer_bold:
                        style.append("粗体")
                    if config.footer_italic:
                        style.append("斜体")
                    lines.append(f"  样式: {', '.join(style)}")
                lines.append("")
        
        # 页码预览
        if config.include_page_number:
            lines.append(f"页码: {config.page_number_format}")
            lines.append(f"  位置: {config.page_number_position}")
            lines.append("")
        
        # 高级设置预览
        if config.different_first_page:
            lines.append("✓ 首页页眉页脚不同")
        if config.different_odd_even:
            lines.append("✓ 奇偶页页眉页脚不同")
        if config.use_three_column_layout:
            lines.append("✓ 使用三栏布局")
        
        return "\n".join(lines)
    
    def update_preview(self):
        """更新预览"""
        try:
            config = self.get_config()
            preview_text = self.generate_preview_text(config)
            self.preview_text.setPlainText(preview_text)
        except Exception:
            # 忽略预览更新错误
            pass
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置吗？这将清除当前的所有配置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = HeaderFooterConfig()
            self.load_config_to_ui()
            app_logger.debug("页眉页脚设置已重置")