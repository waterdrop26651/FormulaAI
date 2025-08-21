# -*- coding: utf-8 -*-
"""
DocumentBookParseDialog

用于InputFormat要求DocumentBook并生成Template的Dialog
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
    DocumentBookParseDialog，用于InputFormat要求DocumentBook并生成Template
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("从DocumentBookParse生成Template")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        """SettingsUser界面"""
        layout = QVBoxLayout(self)
        
        # Template nameInput
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Template name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请InputTemplate name")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Template描述Input
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Template描述:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("请InputTemplate描述（可选）")
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        # DocumentBookContentInput
        layout.addWidget(QLabel("Format要求DocumentBook:"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "请InputFormat要求DocumentBook，例如：\n"
            "标题UseBlack体Small二NumberCharacter，居Center对齐\n"
            "正DocumentUse宋体Small四NumberCharacter，Left对齐，Line距1.5倍\n"
            "OneLevel标题UseBlack体三NumberCharacter，Left对齐\n"
            "二Level标题UseBlack体Small三NumberCharacter，Left对齐"
        )
        layout.addWidget(self.text_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_text_content(self):
        """获取Input的DocumentBookContent"""
        return self.text_input.toPlainText()
        
    def get_template_name(self):
        """获取Template name"""
        return self.name_input.text().strip()
        
    def get_template_description(self):
        """获取Template描述"""
        return self.desc_input.text().strip() or "从DocumentBookParse生成的Template"