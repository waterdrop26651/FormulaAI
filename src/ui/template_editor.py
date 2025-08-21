# -*- coding: utf-8 -*-
"""
TemplateEdit器Dialog模块
负责创建和管理TemplateEdit器Dialog，用于EditFormattingTemplate。
"""

import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFormLayout, QComboBox,
                           QMessageBox, QGroupBox, QDialogButtonBox, QTextEdit,
                           QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
                           QHeaderView, QSpinBox, QDoubleSpinBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.logger import app_logger
from ..utils.config_manager import config_manager
from ..utils.font_manager import FontManager
from ..core.format_manager import FormatManager

class FontSelectionDialog(QDialog):
    """
    FontSelectionDialog，用于SelectionSystemCenterAvailable的Font
    """
    def __init__(self, parent=None, current_font="宋体"):
        super().__init__(parent)
        self.setWindowTitle("SelectionFont")
        self.setMinimumWidth(400)
        self.setMinimumHeight(350)  # Increase height to accommodate new controls
        self.setModal(True)
        
        self.selected_font = current_font
        self.font_manager = FontManager()
        self.user_input_name = ""  # User-defined font name input
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """
        初始化User界面
        """
        layout = QVBoxLayout(self)
        
        # CreateFontList
        self.font_list = QComboBox()
        self.font_list.setEditable(True)  # Allow user input
        
        # GetFontList及其Visible名称
        all_fonts = self.font_manager.get_all_fonts()
        
        # CreateVisible名称到System名称的Mapping（用于SelectionTimeConversion回System名称）
        self.display_to_system_mapping = {}
        
        # Get所HasFont的Visible名称
        display_fonts = []
        for font in all_fonts:
            display_name = self.font_manager.get_font_display_name(font)
            if display_name not in display_fonts:
                display_fonts.append(display_name)
                self.display_to_system_mapping[display_name] = font
        
        # 将FontMinute为CenterDocumentFont和非CenterDocumentFont
        chinese_fonts = []
        other_fonts = []
        
        # 判断YesNo为CenterDocumentFont名称
        for font in display_fonts:
            # 判断Font名称YesNoContainsCenterDocumentCharacter符
            if any('One' <= char <= '鿿' for char in font):
                chinese_fonts.append(font)
            else:
                other_fonts.append(font)
        
        # RespectivelySort
        chinese_fonts.sort()
        other_fonts.sort()
        
        # 合并List，CenterDocumentFontInPrevious
        sorted_fonts = chinese_fonts + other_fonts
        
        # Add到Down拉List
        for font in sorted_fonts:
            self.font_list.addItem(font)
        
        # SetWhenPreviousFont的Visible名称
        display_font = self.font_manager.get_font_display_name(self.selected_font)
        index = self.font_list.findText(display_font)
        if index >= 0:
            self.font_list.setCurrentIndex(index)
        else:
            # If找不到Visible名称，尝试原始Font名称
            index = self.font_list.findText(self.selected_font)
            if index >= 0:
                self.font_list.setCurrentIndex(index)
            else:
                self.font_list.setEditText(self.selected_font)
        
        # AddCustomFont名称Input fields
        custom_group = QGroupBox("CustomFont名称")
        custom_layout = QVBoxLayout()
        
        # Add说明DocumentCharacter
        custom_layout.addWidget(QLabel("If需要Use特定Font名称（如微Soft雅Black），可InDown方Input"))
        
        # Custom名称Input fields
        self.custom_name_input = QLineEdit()
        self.custom_name_input.setPlaceholderText("InputCustomFont名称（可选）")
        custom_layout.addWidget(self.custom_name_input)
        
        custom_group.setLayout(custom_layout)
        
        # FontPreview
        self.preview_label = QLabel("FontPreview: CenterDocumentABC123")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(100)
        self.update_preview(self.selected_font)
        
        # Connect signals
        self.font_list.currentTextChanged.connect(self.update_preview)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add到Layout
        layout.addWidget(QLabel("SelectionFont:"))
        layout.addWidget(self.font_list)
        layout.addWidget(custom_group)  # AddCustomFont组
        layout.addWidget(QLabel("Preview:"))
        layout.addWidget(self.preview_label)
        layout.addWidget(button_box)
        
    def update_preview(self, font_name):
        """
        更NewFontPreview
        """
        try:
            preview_font = QFont(font_name, 14)  # Use14PoundSize便于Preview
            self.preview_label.setFont(preview_font)
            self.selected_font = font_name
        except Exception as e:
            app_logger.error(f"SettingsPreviewFontFailed: {str(e)}")
    
    def accept(self):
        """
        DialogAcceptTime的Process
        """
        # SaveWhenPreviousSelection的Font
        self.selected_font = self.font_list.currentText()
        
        # SaveUserInput的CustomFont名称
        self.user_input_name = self.custom_name_input.text().strip()
        
        # 调用父Class的acceptMethod
        super().accept()
    
    def get_user_input(self):
        """
        获取UserInput的CustomFont名称
        
        Returns:
            str: UserInput的CustomFont名称，If没HasInputRuleReturnSpaceString
        """
        return self.user_input_name
        
    def get_selected_font(self):
        """
        获取Selection的Font
        
        Returns:
            str: SystemAvailable的Font名称
        """
        # GetUserSelection的Visible名称
        display_name = self.selected_font
        
        # IfVisible名称InMappingCenter，Return对应的System名称
        if display_name in self.display_to_system_mapping:
            system_name = self.display_to_system_mapping[display_name]
            if self.font_manager.is_font_available(system_name):
                return system_name
        
        # IfVisible名称Available，直接Return
        if self.font_manager.is_font_available(display_name):
            return display_name
        
        # If都不Available，ReturnNext备Font
        return self.font_manager.get_available_font(display_name)


class TemplateEditorDialog(QDialog):
    """TemplateEdit器Dialog，用于EditFormattingTemplate"""
    
    def __init__(self, parent=None, template_name="", template=None):
        """
        初始化TemplateEdit器Dialog
        
        Args:
            parent: 父Window
            template_name: Template name
            template: TemplateContent
        """
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("FormattingTemplateEdit器")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setModal(True)
        
        # 初始化MemberVariable
        self.format_manager = FormatManager()
        self.font_manager = FontManager()  # 初始化Font管理器
        self.is_new_template = not template_name or not template
        self.template_name = template_name if not self.is_new_template else ""
        self.template = template if not self.is_new_template else self.format_manager.create_default_template()
        
        # Initialize UI
        self.init_ui()
        
        # LoadTemplateData
        self.load_template()
    
    def init_ui(self):
        """
        初始化User界面
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # BasicInformation区域
        info_group = QGroupBox("BasicInformation")
        info_layout = QFormLayout(info_group)
        
        # Template name
        self.name_label = QLabel("Template name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请InputTemplate name")
        info_layout.addRow(self.name_label, self.name_edit)
        
        # Template描述
        self.desc_label = QLabel("Template描述:")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("请InputTemplate描述")
        info_layout.addRow(self.desc_label, self.desc_edit)
        
        # AddBasicInformation组
        main_layout.addWidget(info_group)
        
        # RuleEdit区域
        rules_group = QGroupBox("FormattingRule")
        rules_layout = QVBoxLayout(rules_group)
        
        # CreateTable格
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels(["ElementType", "Font", "CharacterNumber", "粗体", "LineBetween距", "对齐方式"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # SetTable格单元格Edit方式
        self.rules_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        # Add/DeleteButtons
        buttons_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton("AddRule")
        self.add_rule_btn.clicked.connect(self.add_rule)
        self.remove_rule_btn = QPushButton("DeleteRule")
        self.remove_rule_btn.clicked.connect(self.remove_rule)
        buttons_layout.addWidget(self.add_rule_btn)
        buttons_layout.addWidget(self.remove_rule_btn)
        
        rules_layout.addWidget(self.rules_table)
        rules_layout.addLayout(buttons_layout)
        
        # AddRuleEdit组
        main_layout.addWidget(rules_group)
        
        # Preview区域
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        # AddPreview组
        main_layout.addWidget(preview_group)
        
        # Buttons区域
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | 
                                     QDialogButtonBox.StandardButton.Cancel)
        # 将ButtonsDocumentBook改为CenterDocument
        save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if save_button:
            save_button.setText("保存")
            # Set保存Buttons为Bright色
            save_button.setStyleSheet("""
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            """)
        if cancel_button:
            cancel_button.setText("Cancel")
            # SetCancelButtons为Gray色
            cancel_button.setStyleSheet("""
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            """)
            
        button_box.accepted.connect(self.save_template)
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
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
            QTableWidget {
                border: 1px solid #BBDEFB;
                gridline-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #E3F2FD;
                padding: 4px;
                border: 1px solid #BBDEFB;
                font-weight: bold;
            }
        """)
    
    def load_template(self):
        """
        加载TemplateData到UI
        """
        # SetBasicInformation
        self.name_edit.setText(self.template.get("name", ""))
        self.desc_edit.setText(self.template.get("description", ""))
        
        # LoadRule
        rules = self.template.get("rules", {})
        self.rules_table.setRowCount(len(rules))
        
        for i, (element_type, rule) in enumerate(rules.items()):
            # ElementType
            type_item = QTableWidgetItem(element_type)
            self.rules_table.setItem(i, 0, type_item)
            
            # Font - ValidateFontYesNoAvailable
            font_name = rule.get("font", "宋体")
            available_font = self.font_manager.get_available_font(font_name)
            
            # CheckYesNoHas保存的Visible名称
            if "font_display_name" in rule:
                display_name = rule["font_display_name"]
            else:
                # GetFont的Visible名称（优先UseCenterDocument名称）
                display_name = self.font_manager.get_font_display_name(available_font)
            
            font_item = QTableWidgetItem(display_name)
            self.rules_table.setItem(i, 1, font_item)
            
            # CharacterNumber
            size_item = QTableWidgetItem(rule.get("size", "五Number"))
            self.rules_table.setItem(i, 2, size_item)
            
            # 粗体
            bold_item = QTableWidgetItem("Yes" if rule.get("bold", False) else "No")
            self.rules_table.setItem(i, 3, bold_item)
            
            # LineBetween距
            spacing_item = QTableWidgetItem(str(rule.get("line_spacing", 1.5)))
            self.rules_table.setItem(i, 4, spacing_item)
            
            # 对齐方式
            alignment = rule.get("alignment", "left")
            alignment_display = {
                "left": "Left对齐",
                "center": "居Center",
                "right": "Right对齐",
                "justify": "两端对齐"
            }.get(alignment, "Left对齐")
            alignment_item = QTableWidgetItem(alignment_display)
            self.rules_table.setItem(i, 5, alignment_item)
        
        # UpdatePreview
        self.update_preview()
    
    def update_preview(self):
        """
        更NewPreviewContent
        """
        # 构建PreviewDocumentBook
        preview = f"Template name: {self.name_edit.text()}\n"
        preview += f"Template描述: {self.desc_edit.text()}\n\n"
        preview += "FormattingRule:\n"
        
        # AddRuleContent并ApplicationFontPreview
        self.preview_text.clear()
        self.preview_text.append(f"Template name: {self.name_edit.text()}")
        self.preview_text.append(f"Template描述: {self.desc_edit.text()}\n")
        self.preview_text.append("FormattingRule:")
        
        # CreateFont管理器Instance
        font_manager = FontManager()
        
        for row in range(self.rules_table.rowCount()):
            element_type = self.rules_table.item(row, 0).text()
            font_display_name = self.rules_table.item(row, 1).text()  # 这已经YesVisible名称
            size = self.rules_table.item(row, 2).text()
            bold = self.rules_table.item(row, 3).text()
            spacing = self.rules_table.item(row, 4).text()
            alignment = self.rules_table.item(row, 5).text()
            
            # Create带Format的PreviewDocumentBook
            rule_text = f"- {element_type}: {font_display_name} {size} {bold} Line距{spacing} {alignment}"
            
            # ApplicationFontPreview
            cursor = self.preview_text.textCursor()
            format = cursor.charFormat()
            
            # GetSystemFont名称（用于实际Application）
            system_font_name = font_display_name
            
            # IfInMappingCenterHas对应的SystemFont名称，UseSystemFont名称
            if font_display_name in font_manager.font_mapping:
                system_font_name = font_manager.font_mapping[font_display_name]
            
            # 确保FontAvailable
            if not font_manager.is_font_available(system_font_name):
                system_font_name = font_manager.get_available_font(system_font_name)
            
            # SetFont
            preview_font = QFont(system_font_name)
            
            # Set粗体
            preview_font.setBold(bold == "Yes")
            
            # ApplicationFont
            format.setFont(preview_font)
            self.preview_text.append("")
            self.preview_text.setCurrentCharFormat(format)
            self.preview_text.insertPlainText(rule_text)
            
            # Set对齐方式（仅用于Preview效果）
            block_format = self.preview_text.textCursor().blockFormat()
            if alignment == "Left对齐":
                block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            elif alignment == "居Center":
                block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif alignment == "Right对齐":
                block_format.setAlignment(Qt.AlignmentFlag.AlignRight)
            elif alignment == "两端对齐":
                block_format.setAlignment(Qt.AlignmentFlag.AlignJustify)
            
            # Application对齐方式到WhenPreviousParagraph
            cursor = self.preview_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.setBlockFormat(block_format)
    
    def add_rule(self):
        """
        AddNewRule
        """
        # GetWhenPreviousLine数
        row_count = self.rules_table.rowCount()
        self.rules_table.setRowCount(row_count + 1)
        
        # SetDefaultValue
        self.rules_table.setItem(row_count, 0, QTableWidgetItem("Custom"))
        self.rules_table.setItem(row_count, 1, QTableWidgetItem("宋体"))
        self.rules_table.setItem(row_count, 2, QTableWidgetItem("五Number"))
        self.rules_table.setItem(row_count, 3, QTableWidgetItem("No"))
        self.rules_table.setItem(row_count, 4, QTableWidgetItem("1.5"))
        self.rules_table.setItem(row_count, 5, QTableWidgetItem("Left对齐"))
        
        # UpdatePreview
        self.update_preview()
    
    def remove_rule(self):
        """
        DeleteSelected的Rule
        """
        # GetSelected的Line
        selected_rows = set()
        for item in self.rules_table.selectedItems():
            selected_rows.add(item.row())
        
        # If没HasSelectedLine，提示User
        if not selected_rows:
            QMessageBox.warning(self, "未Selection", "请先Selection要Delete的Rule！")
            return
        
        # ConfirmDelete
        reply = QMessageBox.question(
            self,
            "ConfirmDelete",
            f"确定要DeleteSelected的 {len(selected_rows)} ItemRule吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从Next往PreviousDelete，避免Index变化
            for row in sorted(selected_rows, reverse=True):
                self.rules_table.removeRow(row)
            
            # UpdatePreview
            self.update_preview()
    
    def save_template(self):
        """
        保存Template
        """
        # GetBasicInformation
        name = self.name_edit.text().strip()
        description = self.desc_edit.text().strip()
        
        # Validate名称
        if not name:
            QMessageBox.warning(self, "InputError", "Template name不能为Space！")
            return
        
        # 构建RuleDictionary
        rules = {}
        for row in range(self.rules_table.rowCount()):
            element_type = self.rules_table.item(row, 0).text().strip()
            font = self.rules_table.item(row, 1).text().strip()
            size = self.rules_table.item(row, 2).text().strip()
            bold = self.rules_table.item(row, 3).text().strip() == "Yes"
            
            # ParseLineBetween距
            try:
                spacing = float(self.rules_table.item(row, 4).text().strip())
            except ValueError:
                spacing = 1.5
                QMessageBox.warning(self, "InputError", f"Rule '{element_type}' 的LineBetween距FormatInvalid，已设为DefaultValue1.5。")
            
            # Get对齐方式
            alignment_display = self.rules_table.item(row, 5).text().strip()
            alignment_map = {
                "Left对齐": "left",
                "居Center": "center",
                "Right对齐": "right",
                "两端对齐": "justify"
            }
            alignment = alignment_map.get(alignment_display, "left")
            
            # AddDebugLog，Confirm对齐方式Information
            app_logger.debug(f"保存Rule '{element_type}' 的对齐方式: {alignment_display} -> {alignment}")
            
            # UseUserSelection的Font名称，不进LineAutomaticMapping
            system_font = font
            
            # 不再ValidateFontYesNoAvailable，直接UseUserSelection的Font
            # BecauseWordDocument可以NormalVisible即使System没Has该Font
            # Down面的代Yard被注释掉，不再VisibleFont不Available的提示
            # if not self.font_manager.is_font_available(system_font):
            #     available_font = self.font_manager.get_available_font(system_font)
            #     reply = QMessageBox.question(
            #         self,
            #         "Font不Available",
            #         f"Font '{font}' InSystemCenter不Available，YesNoUse '{self.font_manager.get_font_display_name(available_font)}' 替代？",
            #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            #         QMessageBox.StandardButton.Yes
            #     )
            #     
            #     if reply == QMessageBox.StandardButton.Yes:
            #         system_font = available_font
            #         # UpdateTable格Center的Font（Visible名称）
            #         display_name = self.font_manager.get_font_display_name(available_font)
            #         self.rules_table.item(row, 1).setText(display_name)
            
            # Add到RuleDictionary
            rules[element_type] = {
                "font": system_font,  # UseSystemFont名称而不YesVisible名称
                "size": size,
                "bold": bold,
                "line_spacing": spacing,
                "alignment": alignment,  # 确保对齐方式Information被保存
                "font_display_name": font  # SaveVisible名称，便于Next续Visible
            }
            
            # AddDebugLog，ConfirmRuleContent
            app_logger.debug(f"Rule '{element_type}' Content: {rules[element_type]}")
        
        # 构建Template
        template = {
            "name": name,
            "description": description,
            "rules": rules
        }
        
        # ValidateTemplate
        is_valid, error_msg = self.format_manager.validate_template(template)
        if not is_valid:
            QMessageBox.warning(self, "TemplateInvalid", f"TemplateValidateFailed: {error_msg}")
            return
        
        # SaveTemplate
        if self.is_new_template:
            # CheckYesNo已Exists同名Template
            if name in self.format_manager.get_template_names():
                reply = QMessageBox.question(
                    self,
                    "Template已Exists",
                    f"已Exists名为 '{name}' 的Template，YesNo覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
        
        # SaveTemplate
        success = self.format_manager.save_template(name, template)
        
        if success:
            app_logger.info(f"Template '{name}' 已保存")
            QMessageBox.information(self, "保存Success", f"Template '{name}' 已保存！")
            # SaveWhenPreviousTemplate name，以便主Window可以获取
            self.template_name = name
            super().accept()
        else:
            app_logger.error(f"保存Template '{name}' Failed")
            QMessageBox.critical(self, "保存Failed", f"Template '{name}' 保存Failed！")
    
    def get_template_name(self):
        """
        获取WhenPreviousTemplate name
        
        Returns:
            str: Template name
        """
        return self.template_name
    
    def on_cell_double_clicked(self, row, column):
        """
        单元格双击EventProcess
        
        Args:
            row: LineIndex
            column: ColumnIndex
        """
        # 根据ColumnType提供Different的Edit方式
        if column == 1:  # FontColumn
            self.edit_font(row, column)
        elif column == 2:  # CharacterNumberColumn
            self.edit_size(row, column)
        elif column == 3:  # 粗体Column
            self.edit_bold(row, column)
        elif column == 4:  # LineBetween距Column
            self.edit_spacing(row, column)
        elif column == 5:  # 对齐方式Column
            self.edit_alignment(row, column)
    
    def edit_font(self, row, column):
        """
        EditFont
        
        Args:
            row: LineIndex
            column: ColumnIndex
        """
        current_font = self.rules_table.item(row, column).text()
        dialog = FontSelectionDialog(self, current_font)
        
        if dialog.exec():
            # GetSystemAvailable的Font名称
            system_font = dialog.get_selected_font()
            
            # GetFont的Visible名称（CenterDocument名称）
            font_manager = FontManager()
            display_name = font_manager.get_font_display_name(system_font)
            
            # IfUserInput了Custom名称，UseUserInput的名称
            user_input = dialog.get_user_input()
            if user_input:
                display_name = user_input
                
                # 不再Automatic创建FontMapping，直接UseUserInput的名称
                # font_manager.add_font_mapping(display_name, system_font)
            
            # InTable格CenterVisibleFont名称
            self.rules_table.setItem(row, column, QTableWidgetItem(display_name))
            
            # UpdatePreview
            self.update_preview()
    
    def edit_size(self, row, column):
        """
        EditCharacterNumber
        
        Args:
            row: LineIndex
            column: ColumnIndex
        """
        current_size = self.rules_table.item(row, column).text()
        
        # CreateCharacterNumberSelectionDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("SelectionCharacterNumber")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        
        # CreateCharacterNumberDown拉List
        size_combo = QComboBox()
        size_combo.setEditable(True)
        
        # Add常用CharacterNumber
        standard_sizes = ["Small二", "三Number", "Small三", "四Number", "Small四", "五Number", "Small五", "六Number"]
        for size in standard_sizes:
            size_combo.addItem(size)
        
        # SetWhenPreviousCharacterNumber
        index = size_combo.findText(current_size)
        if index >= 0:
            size_combo.setCurrentIndex(index)
        else:
            size_combo.setEditText(current_size)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Add到Layout
        layout.addWidget(QLabel("SelectionCharacterNumber:"))
        layout.addWidget(size_combo)
        layout.addWidget(button_box)
        
        if dialog.exec():
            selected_size = size_combo.currentText()
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_size))
            self.update_preview()
    
    def edit_bold(self, row, column):
        """
        Edit粗体Settings
        
        Args:
            row: LineIndex
            column: ColumnIndex
        """
        current_bold = self.rules_table.item(row, column).text()
        new_bold = "No" if current_bold == "Yes" else "Yes"
        self.rules_table.setItem(row, column, QTableWidgetItem(new_bold))
        self.update_preview()
    
    def edit_spacing(self, row, column):
        """
        EditLineBetween距
        
        Args:
            row: LineIndex
            column: ColumnIndex
        """
        current_spacing = self.rules_table.item(row, column).text()
        
        # CreateLineBetween距EditDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("SettingsLineBetween距")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        
        # CreateLineBetween距Input fields
        spacing_spin = QDoubleSpinBox()
        spacing_spin.setRange(0.5, 3.0)
        spacing_spin.setSingleStep(0.1)
        spacing_spin.setDecimals(1)
        
        try:
            spacing_spin.setValue(float(current_spacing))
        except ValueError:
            spacing_spin.setValue(1.5)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Add到Layout
        layout.addWidget(QLabel("SettingsLineBetween距:"))
        layout.addWidget(spacing_spin)
        layout.addWidget(button_box)
        
        if dialog.exec():
            # GetValue并Format为OneBitDecimal，避免Float精Degree问题
            value = spacing_spin.value()
            selected_spacing = f"{value:.1f}"
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_spacing))
            self.update_preview()
            
    def edit_alignment(self, row, column):
        """
        Edit对齐方式
        
        Args:
            row: LineIndex
            column: ColumnIndex
        """
        current_alignment = self.rules_table.item(row, column).text()
        
        # Create对齐方式EditDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings对齐方式")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        
        # Create对齐方式Dropdown
        alignment_combo = QComboBox()
        alignment_options = ["Left对齐", "居Center", "Right对齐", "两端对齐"]
        for option in alignment_options:
            alignment_combo.addItem(option)
        
        # SetWhenPrevious对齐方式
        index = alignment_combo.findText(current_alignment)
        if index >= 0:
            alignment_combo.setCurrentIndex(index)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Add到Layout
        layout.addWidget(QLabel("Selection对齐方式:"))
        layout.addWidget(alignment_combo)
        layout.addWidget(button_box)
        
        if dialog.exec():
            selected_alignment = alignment_combo.currentText()
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_alignment))
            self.update_preview()
    
    def closeEvent(self, event):
        """
        WindowShutdownEvent
        """
        # 询问YesNo保存更改
        reply = QMessageBox.question(
            self,
            "ConfirmShutdown",
            "YesNo保存更改？",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Save:
            self.save_template()
            event.accept()
        elif reply == QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()
