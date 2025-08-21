# -*- coding: utf-8 -*-
"""
文本解析对话框

用于输入格式要求文本并生成模板的对话框
"""

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
        QLineEdit, QTextEdit, QDialogButtonBox
    )
    from PyQt6.QtCore import Qt
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    raise ImportError("PyQt6 is required but not properly installed")


class TextParsingDialog(QDialog):
    """
    文本解析对话框，用于输入格式要求文本并生成模板
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("从文本解析生成模板")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 模板名称输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("模板名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入模板名称")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 模板描述输入
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("模板描述:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("请输入模板描述（可选）")
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        # 文本内容输入
        layout.addWidget(QLabel("格式要求文本:"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "请输入格式要求文本，例如：\n"
            "标题使用黑体小二号字，居中对齐\n"
            "正文使用宋体小四号字，左对齐，行距1.5倍\n"
            "一级标题使用黑体三号字，左对齐\n"
            "二级标题使用黑体小三号字，左对齐"
        )
        layout.addWidget(self.text_input)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_text_content(self):
        """获取输入的文本内容"""
        return self.text_input.toPlainText()
        
    def get_template_name(self):
        """获取模板名称"""
        return self.name_input.text().strip()
        
    def get_template_description(self):
        """获取模板描述"""
        return self.desc_input.text().strip() or "从文本解析生成的模板"