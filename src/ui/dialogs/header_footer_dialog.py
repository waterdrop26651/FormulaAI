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
        self.setWindowTitle("页眉页脚设置")
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
        self.tab_widget.addTab(basic_tab, "基础设置")
        
        # 高级设置选项卡
        advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, "高级设置")
        
        # 页码设置选项卡
        page_number_tab = self.create_page_number_tab()
        self.tab_widget.addTab(page_number_tab, "页码设置")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.preview_btn = QPushButton("预览")
        self.preview_btn.setToolTip("预览页眉页脚效果")
        button_layout.addWidget(self.preview_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setToolTip("重置所有设置")
        button_layout.addWidget(self.reset_btn)
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_basic_tab(self):
        """创建基础设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 页眉设置组
        header_group = QGroupBox("页眉设置")
        header_layout = QFormLayout(header_group)
        
        self.enable_header_cb = QCheckBox("启用页眉")
        header_layout.addRow(self.enable_header_cb)
        
        self.header_content_edit = QLineEdit()
        self.header_content_edit.setPlaceholderText("请输入页眉内容")
        header_layout.addRow("页眉内容:", self.header_content_edit)
        
        self.header_alignment_combo = QComboBox()
        self.header_alignment_combo.addItems(["左对齐", "居中", "右对齐", "两端对齐"])
        self.header_alignment_combo.setCurrentText("居中")
        header_layout.addRow("对齐方式:", self.header_alignment_combo)
        
        # 页眉字体设置
        header_font_layout = QHBoxLayout()
        
        self.header_font_combo = QComboBox()
        self.header_font_combo.addItems(["宋体", "黑体", "楷体", "仿宋", "微软雅黑", "Times New Roman", "Arial"])
        self.header_font_combo.setCurrentText("宋体")
        header_font_layout.addWidget(QLabel("字体:"))
        header_font_layout.addWidget(self.header_font_combo)
        
        self.header_font_size_spin = QSpinBox()
        self.header_font_size_spin.setRange(6, 72)
        self.header_font_size_spin.setValue(10)
        self.header_font_size_spin.setSuffix(" pt")
        header_font_layout.addWidget(QLabel("大小:"))
        header_font_layout.addWidget(self.header_font_size_spin)
        
        self.header_bold_cb = QCheckBox("粗体")
        header_font_layout.addWidget(self.header_bold_cb)
        
        self.header_italic_cb = QCheckBox("斜体")
        header_font_layout.addWidget(self.header_italic_cb)
        
        header_font_layout.addStretch()
        header_layout.addRow("字体设置:", header_font_layout)
        
        layout.addWidget(header_group)
        
        # 页脚设置组
        footer_group = QGroupBox("页脚设置")
        footer_layout = QFormLayout(footer_group)
        
        self.enable_footer_cb = QCheckBox("启用页脚")
        footer_layout.addRow(self.enable_footer_cb)
        
        self.footer_content_edit = QLineEdit()
        self.footer_content_edit.setPlaceholderText("请输入页脚内容")
        footer_layout.addRow("页脚内容:", self.footer_content_edit)
        
        self.footer_alignment_combo = QComboBox()
        self.footer_alignment_combo.addItems(["左对齐", "居中", "右对齐", "两端对齐"])
        self.footer_alignment_combo.setCurrentText("居中")
        footer_layout.addRow("对齐方式:", self.footer_alignment_combo)
        
        # 页脚字体设置
        footer_font_layout = QHBoxLayout()
        
        self.footer_font_combo = QComboBox()
        self.footer_font_combo.addItems(["宋体", "黑体", "楷体", "仿宋", "微软雅黑", "Times New Roman", "Arial"])
        self.footer_font_combo.setCurrentText("宋体")
        footer_font_layout.addWidget(QLabel("字体:"))
        footer_font_layout.addWidget(self.footer_font_combo)
        
        self.footer_font_size_spin = QSpinBox()
        self.footer_font_size_spin.setRange(6, 72)
        self.footer_font_size_spin.setValue(9)
        self.footer_font_size_spin.setSuffix(" pt")
        footer_font_layout.addWidget(QLabel("大小:"))
        footer_font_layout.addWidget(self.footer_font_size_spin)
        
        self.footer_bold_cb = QCheckBox("粗体")
        footer_font_layout.addWidget(self.footer_bold_cb)
        
        self.footer_italic_cb = QCheckBox("斜体")
        footer_font_layout.addWidget(self.footer_italic_cb)
        
        footer_font_layout.addStretch()
        footer_layout.addRow("字体设置:", footer_font_layout)
        
        layout.addWidget(footer_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self):
        """创建高级设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.different_first_page_cb = QCheckBox("首页页眉页脚不同")
        self.different_first_page_cb.setToolTip("首页使用不同的页眉页脚")
        advanced_layout.addWidget(self.different_first_page_cb)
        
        self.different_odd_even_cb = QCheckBox("奇偶页页眉页脚不同")
        self.different_odd_even_cb.setToolTip("奇数页和偶数页使用不同的页眉页脚")
        advanced_layout.addWidget(self.different_odd_even_cb)
        
        self.three_column_layout_cb = QCheckBox("使用三栏布局（左中右）")
        self.three_column_layout_cb.setToolTip("页眉页脚分为左中右三栏")
        advanced_layout.addWidget(self.three_column_layout_cb)
        
        layout.addWidget(advanced_group)
        
        # 首页设置组
        self.first_page_group = QGroupBox("首页设置")
        self.first_page_group.setEnabled(False)
        first_page_layout = QFormLayout(self.first_page_group)
        
        self.first_page_header_edit = QLineEdit()
        self.first_page_header_edit.setPlaceholderText("首页页眉内容")
        first_page_layout.addRow("首页页眉:", self.first_page_header_edit)
        
        self.first_page_footer_edit = QLineEdit()
        self.first_page_footer_edit.setPlaceholderText("首页页脚内容")
        first_page_layout.addRow("首页页脚:", self.first_page_footer_edit)
        
        layout.addWidget(self.first_page_group)
        
        # 偶数页设置组
        self.even_page_group = QGroupBox("偶数页设置")
        self.even_page_group.setEnabled(False)
        even_page_layout = QFormLayout(self.even_page_group)
        
        self.even_page_header_edit = QLineEdit()
        self.even_page_header_edit.setPlaceholderText("偶数页页眉内容")
        even_page_layout.addRow("偶数页页眉:", self.even_page_header_edit)
        
        self.even_page_footer_edit = QLineEdit()
        self.even_page_footer_edit.setPlaceholderText("偶数页页脚内容")
        even_page_layout.addRow("偶数页页脚:", self.even_page_footer_edit)
        
        layout.addWidget(self.even_page_group)
        
        # 三栏布局设置组
        self.three_column_group = QGroupBox("三栏布局设置")
        self.three_column_group.setEnabled(False)
        three_column_layout = QFormLayout(self.three_column_group)
        
        # 页眉三栏
        self.header_left_edit = QLineEdit()
        self.header_left_edit.setPlaceholderText("页眉左侧内容")
        three_column_layout.addRow("页眉左侧:", self.header_left_edit)
        
        self.header_center_edit = QLineEdit()
        self.header_center_edit.setPlaceholderText("页眉中间内容")
        three_column_layout.addRow("页眉中间:", self.header_center_edit)
        
        self.header_right_edit = QLineEdit()
        self.header_right_edit.setPlaceholderText("页眉右侧内容")
        three_column_layout.addRow("页眉右侧:", self.header_right_edit)
        
        # 页脚三栏
        self.footer_left_edit = QLineEdit()
        self.footer_left_edit.setPlaceholderText("页脚左侧内容")
        three_column_layout.addRow("页脚左侧:", self.footer_left_edit)
        
        self.footer_center_edit = QLineEdit()
        self.footer_center_edit.setPlaceholderText("页脚中间内容")
        three_column_layout.addRow("页脚中间:", self.footer_center_edit)
        
        self.footer_right_edit = QLineEdit()
        self.footer_right_edit.setPlaceholderText("页脚右侧内容")
        three_column_layout.addRow("页脚右侧:", self.footer_right_edit)
        
        layout.addWidget(self.three_column_group)
        
        layout.addStretch()
        return widget
    
    def create_page_number_tab(self):
        """创建页码设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 页码设置组
        page_number_group = QGroupBox("页码设置")
        page_number_layout = QFormLayout(page_number_group)
        
        self.include_page_number_cb = QCheckBox("包含页码")
        page_number_layout.addRow(self.include_page_number_cb)
        
        self.page_number_position_combo = QComboBox()
        self.page_number_position_combo.addItems([
            "页眉左侧", "页眉中间", "页眉右侧",
            "页脚左侧", "页脚中间", "页脚右侧"
        ])
        self.page_number_position_combo.setCurrentText("页脚中间")
        page_number_layout.addRow("页码位置:", self.page_number_position_combo)
        
        self.page_number_format_edit = QLineEdit()
        self.page_number_format_edit.setText("第 {page} 页")
        self.page_number_format_edit.setPlaceholderText("使用 {page} 作为页码占位符")
        page_number_layout.addRow("页码格式:", self.page_number_format_edit)
        
        layout.addWidget(page_number_group)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("页眉页脚预览将在这里显示...")
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