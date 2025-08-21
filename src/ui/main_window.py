# -*- coding: utf-8 -*-
"""
主Window模块
负责创建和管理ApplicationProgram的主Window界面。
"""

import os
import sys
import time
import subprocess
try:
    from PyQt6.QtWidgets import (  # pyright: ignore[reportMissingImports]
        QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFileDialog, QProgressBar, QTextEdit,
        QComboBox, QGroupBox, QGridLayout, QMessageBox, QSplitter,
        QDialog, QDialogButtonBox, QProgressDialog, QLineEdit
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize  # pyright: ignore[reportMissingImports]
    from PyQt6.QtGui import QFont, QIcon, QColor, QPalette  # pyright: ignore[reportMissingImports]
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    # 提供备用导入或ErrorProcess
    raise ImportError("PyQt6 is required but not properly installed")

from ..core.doc_processor import DocProcessor
from ..core.ai_connector import AIConnector
from ..core.format_manager import FormatManager
from ..core.structure_analyzer import StructureAnalyzer
from ..core.text_template_parser import TextTemplateParser
from ..utils.logger import app_logger
from ..utils.config_manager import config_manager
from ..utils.file_utils import is_valid_docx

from .api_config_dialog import ApiConfigDialog
from .template_editor import TemplateEditorDialog


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


class FormattingCompleteDialog(QDialog):
    """
    FormattingCompleteDialog，VisibleSuccessMessage并提供OpenDocumentButtons
    """
    def __init__(self, parent=None, message=""):
        super().__init__(parent)
        self.message = message
        self.setWindowTitle("FormattingComplete")
        self.setup_ui()
        
    def setup_ui(self):
        # CreateLayout
        layout = QVBoxLayout(self)
        
        # AddMessageLabels
        message_label = QLabel(f"DocumentFormatting已Complete！\nFile已保存为: {self.message}")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # CreateButtons盒子
        button_box = QDialogButtonBox()
        
        # AddStandardButtons（确定）
        self.ok_button = button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        
        # AddCustomButtons（OpenDocument）
        self.open_doc_button = QPushButton("OpenDocument")
        button_box.addButton(self.open_doc_button, QDialogButtonBox.ButtonRole.ActionRole)
        
        # Connect signals和槽
        button_box.accepted.connect(self.accept)
        self.open_doc_button.clicked.connect(self.open_document)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
    def open_document(self):
        """Open已Formatting的Document"""
        try:
            # 根据OperationSystemSelectionOpen方式
            if sys.platform == "win32":
                os.startfile(self.message)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", self.message])
            else:  # Linux
                subprocess.run(["xdg-open", self.message])
                
            app_logger.info(f"已OpenDocument: {self.message}")
        except Exception as e:
            app_logger.error(f"OpenDocumentFailed: {str(e)}")
            QMessageBox.warning(self.parent(), "OpenFailed", f"NoneLawOpenDocument！\nError: {str(e)}")


class FormattingWorker(QThread):
    """Formatting工作线程，用于Next台执LineFormatting任务"""
    
    # Signal definitions
    progress_updated = pyqtSignal(int)  # Progress更NewSignal
    log_message = pyqtSignal(str)  # LogMessageSignal
    task_completed = pyqtSignal(bool, str)  # 任务CompleteSignal，Parameters为YesNoSuccess和Message
    
    def __init__(self, doc_processor, ai_connector, format_manager, structure_analyzer, doc_path, template_name, save_path=None):
        super().__init__()
        self.doc_processor = doc_processor
        self.ai_connector = ai_connector
        self.format_manager = format_manager
        self.structure_analyzer = structure_analyzer
        self.doc_path = doc_path
        self.template_name = template_name
        self.save_path = save_path
        self.is_running = False
    
    def run(self):
        """执LineFormatting任务"""
        self.is_running = True
        success = False
        output_file = ""
        
        try:
            # UpdateProgress和Log
            self.progress_updated.emit(5)
            self.log_message.emit("Start读取Document...")
            
            # 读取Document
            if not self.doc_processor.read_document(self.doc_path):
                self.log_message.emit("读取DocumentFailed！")
                self.task_completed.emit(False, "读取DocumentFailed")
                return
            
            # GetDocumentContent
            self.progress_updated.emit(15)
            self.log_message.emit("Document读取Success，StartAnalyzeDocument结构...")
            doc_content = self.doc_processor.get_document_text()
            
            # AnalyzeDocument结构
            features = self.structure_analyzer.analyze_text_features(doc_content)
            structure_hints = self.structure_analyzer.generate_structure_hints(features)
            
            self.progress_updated.emit(25)
            self.log_message.emit(f"Document结构AnalyzeComplete，发现 {len(features.get('potential_titles', []))} 个潜In标题")
            
            # GetFormattingTemplate
            template = self.format_manager.get_template(self.template_name)
            if not template:
                self.log_message.emit(f"Template '{self.template_name}' 不Exists，UseDefaultTemplate")
                template = self.format_manager.create_default_template()
            
            # 构建AI提示Word
            self.progress_updated.emit(35)
            self.log_message.emit("正In生成AI提示Word...")
            prompt = self.ai_connector.generate_prompt(doc_content, template.get('rules', {}))
            
            # 发送Request到AI API
            self.progress_updated.emit(45)
            self.log_message.emit("正In发送Request到AI API...")
            success, response = self.ai_connector.send_request(prompt)
            
            if not success:
                self.log_message.emit(f"AI APIRequestFailed: {response}")
                self.task_completed.emit(False, "AI APIRequestFailed")
                return
            
            # ParseAIResponse
            self.progress_updated.emit(65)
            self.log_message.emit("AIResponseSuccess，正InParseResponse...")
            success, formatting_instructions = self.ai_connector.parse_response(response)
            
            if not success:
                self.log_message.emit(f"ParseAIResponseFailed: {formatting_instructions}")
                self.task_completed.emit(False, "ParseAIResponseFailed")
                return
            
            # Validate结构
            self.progress_updated.emit(75)
            self.log_message.emit("正InValidateDocument结构...")
            valid, formatting_instructions = self.structure_analyzer.validate_structure(formatting_instructions)
            
            if not valid:
                self.log_message.emit("Document结构ValidateFailed，将UsePart识别Result")
            
            # ApplicationFormatting
            self.progress_updated.emit(85)
            self.log_message.emit("正InApplicationFormattingFormat...")
            
            # UseCustom保存Path
            if self.save_path:
                self.log_message.emit(f"将UseCustom保存Path: {self.save_path}")
                if not self.doc_processor.apply_formatting(formatting_instructions, self.save_path):
                    self.log_message.emit("ApplicationFormattingFormatFailed！")
                    self.task_completed.emit(False, "ApplicationFormattingFormatFailed")
                    return
            else:
                self.log_message.emit("未指定保存Path，将保存到原FileDirectory")
                if not self.doc_processor.apply_formatting(formatting_instructions):
                    self.log_message.emit("ApplicationFormattingFormatFailed！")
                    self.task_completed.emit(False, "ApplicationFormattingFormatFailed")
                    return
            
            # Get输出File path
            output_file = self.doc_processor.get_output_file()
            
            # Complete
            self.progress_updated.emit(100)
            self.log_message.emit(f"FormattingComplete！File已保存为: {output_file}")
            success = True
            
        except Exception as e:
            self.log_message.emit(f"Formatting过程发生Error: {str(e)}")
            success = False
        
        self.is_running = False
        self.task_completed.emit(success, output_file)
    
    def stop(self):
        """StopFormatting任务"""
        if self.is_running:
            self.log_message.emit("正InStopFormatting任务...")
            self.terminate()
            self.is_running = False

class MainWindow(QMainWindow):
    """ApplicationProgram主Window"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化Core组Item
        self.doc_processor = DocProcessor()
        self.format_manager = FormatManager()
        self.structure_analyzer = StructureAnalyzer()
        
        # LoadAPIConfiguration
        api_config = config_manager.get_api_config()
        self.ai_connector = AIConnector(api_config)
        
        # 初始化DocumentBookParse器
        self.text_parser = TextTemplateParser(self.ai_connector)
        
        # LoadApplicationConfiguration
        self.app_config = config_manager.get_app_config()
        
        # Initialize UI
        self.init_ui()
        
        # 初始化工作线程
        self.formatting_worker = None
        
        # AddLogProcess器
        app_logger.add_ui_handler(self.update_log)
        
        # LoadTemplateList
        self.load_templates()
        
        # SetWindow标题和图标
        self.setWindowTitle("AI WordDocumentAutomaticFormattingTool")
        
        # Log
        app_logger.info("ApplicationProgramStartupComplete")
    
    def init_ui(self):
        """初始化User界面"""
        # SetWindowSize
        self.resize(900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create主Layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # TopFunction区
        top_section = self.create_top_section()
        main_layout.addLayout(top_section)
        
        # CenterBetweenLog区
        mid_section = self.create_mid_section()
        main_layout.addLayout(mid_section, 1)  # 1Table示拉伸因子
        
        # BottomButtons区
        bottom_section = self.create_bottom_section()
        main_layout.addLayout(bottom_section)
        
        # SetStyle
        self.set_style()
    
    def create_top_section(self):
        """创建TopFunction区"""
        top_layout = QVBoxLayout()
        
        # Document selection area
        doc_group = QGroupBox("DocumentSelection")
        doc_layout = QGridLayout()
        
        self.doc_path_label = QLabel("请SelectionWordDocument:")
        self.doc_path_value = QLabel("未SelectionFile")
        self.doc_path_value.setStyleSheet("color: gray;")
        self.select_doc_btn = QPushButton("浏览...")
        self.select_doc_btn.clicked.connect(self.select_document)
        
        doc_layout.addWidget(self.doc_path_label, 0, 0)
        doc_layout.addWidget(self.doc_path_value, 0, 1)
        doc_layout.addWidget(self.select_doc_btn, 0, 2)
        
        doc_group.setLayout(doc_layout)
        top_layout.addWidget(doc_group)
        
        # FormattingRule区
        format_group = QGroupBox("FormattingRule")
        format_layout = QGridLayout()
        
        self.template_label = QLabel("SelectionFormattingTemplate:")
        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        
        # CreateButtonsLayout
        template_buttons_layout = QHBoxLayout()
        template_buttons_layout.setSpacing(5)  # SetButtons之Between的Between距
        
        # CreateEditTemplateButtons
        self.edit_template_btn = QPushButton("EditTemplate")
        self.edit_template_btn.clicked.connect(self.edit_template)
        self.edit_template_btn.setFixedHeight(30)  # FixedButtonsHeight
        
        # CreateNew增TemplateButtons
        self.add_template_btn = QPushButton("New增Template")
        self.add_template_btn.clicked.connect(self.add_template)
        self.add_template_btn.setFixedHeight(30)  # FixedButtonsHeight，与EditButtonsOne致
        
        # Create从DocumentBookParseButtons
        self.parse_text_btn = QPushButton("从DocumentBookParse")
        self.parse_text_btn.clicked.connect(self.parse_text_template)
        self.parse_text_btn.setFixedHeight(30)  # FixedButtonsHeight
        
        # SetButtonsStyle，确保视觉One致性
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        
        self.edit_template_btn.setStyleSheet(button_style)
        self.add_template_btn.setStyleSheet(button_style)
        self.parse_text_btn.setStyleSheet(button_style)
        
        template_buttons_layout.addWidget(self.edit_template_btn)
        template_buttons_layout.addWidget(self.add_template_btn)
        template_buttons_layout.addWidget(self.parse_text_btn)
        
        self.template_content = QTextEdit()
        self.template_content.setReadOnly(True)
        self.template_content.setMaximumHeight(100)
        
        format_layout.addWidget(self.template_label, 0, 0)
        format_layout.addWidget(self.template_combo, 0, 1)
        format_layout.addLayout(template_buttons_layout, 0, 2)
        format_layout.addWidget(self.template_content, 1, 0, 1, 3)
        
        format_group.setLayout(format_layout)
        top_layout.addWidget(format_group)
        
        # SavePosition区
        save_group = QGroupBox("Save location")
        save_layout = QGridLayout()
        
        self.save_path_label = QLabel("保存FilePosition:")
        self.save_path_value = QLabel(self.app_config.get("save_path", "与源FileSameDirectory"))
        self.save_path_value.setStyleSheet("color: gray;")
        self.select_save_btn = QPushButton("浏览...")
        self.select_save_btn.clicked.connect(self.select_save_location)
        
        save_layout.addWidget(self.save_path_label, 0, 0)
        save_layout.addWidget(self.save_path_value, 0, 1)
        save_layout.addWidget(self.select_save_btn, 0, 2)
        
        save_group.setLayout(save_layout)
        top_layout.addWidget(save_group)
        
        # APIConfigurationButtons（放InRightUp角）
        api_layout = QHBoxLayout()
        api_layout.addStretch(1)
        
        self.api_config_btn = QPushButton("APIConfiguration")
        self.api_config_btn.clicked.connect(self.open_api_config)
        api_layout.addWidget(self.api_config_btn)
        
        top_layout.addLayout(api_layout)
        
        return top_layout
    
    def create_mid_section(self):
        """创建CenterBetweenLog区"""
        mid_layout = QVBoxLayout()
        
        # LogLabels
        log_label = QLabel("ProcessLog")
        log_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        mid_layout.addWidget(log_label)
        
        # Log text box
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        mid_layout.addWidget(self.log_text)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_label = QLabel("Progress:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        mid_layout.addLayout(progress_layout)
        
        return mid_layout
    
    def create_bottom_section(self):
        """创建BottomButtons区"""
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        
        # StartFormattingButtons
        self.start_btn = QPushButton("StartFormatting")
        self.start_btn.setEnabled(False)  # 初始Disabled
        self.start_btn.clicked.connect(self.start_formatting)
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setMinimumHeight(40)
        
        # StopFormattingButtons
        self.stop_btn = QPushButton("StopFormatting")
        self.stop_btn.setEnabled(False)  # 初始Disabled
        self.stop_btn.clicked.connect(self.stop_formatting)
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setMinimumHeight(40)
        
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.stop_btn)
        
        return bottom_layout
    
    def set_style(self):
        """Settings界面Style"""
        # SetFont
        app = QApplication.instance()
        font = QFont("Microsoft YaHei", 10)
        app.setFont(font)
        
        # SetButtonsStyle
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
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
        """
        
        self.start_btn.setStyleSheet(button_style)
        self.stop_btn.setStyleSheet(button_style)
        self.select_doc_btn.setStyleSheet(button_style)
        self.select_save_btn.setStyleSheet(button_style)
        self.edit_template_btn.setStyleSheet(button_style)
        self.api_config_btn.setStyleSheet(button_style)
        
        # SetGroup框Style
        group_style = """
            QGroupBox {
                border: 1px solid #BBDEFB;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                color: #1976D2;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """
        
        # SetText boxStyle
        text_style = """
            QTextEdit {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
        """
        
        self.log_text.setStyleSheet(text_style)
        self.template_content.setStyleSheet(text_style)
    
    def load_templates(self):
        """加载FormattingTemplateList"""
        self.template_combo.clear()
        
        template_names = self.format_manager.get_template_names()
        for name in template_names:
            self.template_combo.addItem(name)
        
        # SetDefaultTemplate
        default_template = self.app_config.get("last_template", "DefaultTemplate")
        index = self.template_combo.findText(default_template)
        if index >= 0:
            self.template_combo.setCurrentIndex(index)
        elif self.template_combo.count() > 0:
            self.template_combo.setCurrentIndex(0)
    
    def on_template_changed(self, index):
        """TemplateSelection变更Event"""
        if index < 0:
            return
        
        template_name = self.template_combo.currentText()
        template_text = self.format_manager.get_template_as_text(template_name)
        self.template_content.setText(template_text)
        
        # Save最NextUse的Template
        self.app_config["last_template"] = template_name
        config_manager.save_app_config(self.app_config)
    
    def select_document(self):
        """SelectionWordDocument"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "SelectionWordDocument",
            "",
            "WordDocument (*.docx)"
        )
        
        if file_path:
            # ValidateDocumentValid性
            if not is_valid_docx(file_path):
                QMessageBox.warning(self, "InvalidDocument", "所选File不YesValid的WordDocument！")
                return
            
            self.doc_path_value.setText(file_path)
            self.doc_path_value.setStyleSheet("color: black;")
            app_logger.info(f"已SelectionDocument: {file_path}")
            
            # EnabledStartButtons
            self.start_btn.setEnabled(True)
    
    def select_save_location(self):
        """SelectionSave location"""
        file_dialog = QFileDialog()
        save_dir = file_dialog.getExistingDirectory(
            self,
            "SelectionSave location",
            self.app_config.get("save_path", "")
        )
        
        if save_dir:
            self.save_path_value.setText(save_dir)
            self.save_path_value.setStyleSheet("color: black;")
            app_logger.info(f"已SettingsSave location: {save_dir}")
            
            # UpdateConfiguration
            self.app_config["save_path"] = save_dir
            config_manager.save_app_config(self.app_config)
    
    def open_api_config(self):
        """OpenAPIConfigurationDialog"""
        dialog = ApiConfigDialog(self)
        if dialog.exec():
            # UpdateAIJoin器
            api_config = config_manager.get_api_config()
            self.ai_connector = AIConnector(api_config)
            app_logger.info("APIConfiguration已更New")
    
    def edit_template(self):
        """EditFormattingTemplate"""
        template_name = self.template_combo.currentText()
        template = self.format_manager.get_template(template_name)
        
        dialog = TemplateEditorDialog(self, template_name, template)
        if dialog.exec():
            # GetNew的Template name（可能已更改）
            new_template_name = dialog.get_template_name()
            app_logger.info(f"TemplateEditComplete，准备刷New: '{new_template_name}'")
            
            # StrongSystem重New加载所HasTemplate
            self.format_manager.load_templates()  # 先重New从FileSystem加载Template
            app_logger.debug(f"已重New加载TemplateFile")
            
            # CheckTemplateYesNoSuccess加载
            loaded_template = self.format_manager.get_template(new_template_name)
            if loaded_template:
                app_logger.debug(f"Success加载Template '{new_template_name}', Rule数: {len(loaded_template.get('rules', {}))}")
                for element, rule in loaded_template.get('rules', {}).items():
                    app_logger.debug(f"Element '{element}' 的对齐方式: {rule.get('alignment', '未Settings')}")
            else:
                app_logger.error(f"NoneLaw加载Template '{new_template_name}'")
            
            # UpdateUIVisible
            self.load_templates()  # UpdateDown拉菜单
            
            if new_template_name != template_name:
                app_logger.info(f"Template name已从 '{template_name}' 更改为 '{new_template_name}'")
                # SelectedNew的Template
                index = self.template_combo.findText(new_template_name)
                if index >= 0:
                    self.template_combo.setCurrentIndex(index)
            else:
                # 即使名称没变，也需要重NewSelection以触发刷New
                index = self.template_combo.findText(new_template_name)
                if index >= 0:
                    self.template_combo.setCurrentIndex(index)
                app_logger.info(f"Template '{template_name}' 已更New")
            
            # StrongSystem刷NewTemplateContentVisible
            self.on_template_changed(self.template_combo.currentIndex())
                
    def add_template(self):
        """New增FormattingTemplate"""
        # CreateSpaceBlankTemplate
        empty_template = {
            "name": "",
            "description": "New建Template",
            "rules": {
                "标题": {
                    "font": "Black体",
                    "size": "Small二",
                    "bold": True,
                    "line_spacing": 1.5,
                    "alignment": "center"
                },
                "正Document": {
                    "font": "宋体",
                    "size": "Small四",
                    "bold": False,
                    "line_spacing": 1.5,
                    "alignment": "left"
                }
            }
        }
        
        # OpenTemplateEdit器Dialog
        dialog = TemplateEditorDialog(self, "", empty_template)
        if dialog.exec():
            # 重New加载所HasTemplate
            self.format_manager.load_templates()  # 先重New从FileSystem加载Template
            self.load_templates()  # Then更NewUIVisible
            
            # GetNewTemplate name并Selected
            new_template_name = dialog.get_template_name()
            app_logger.info(f"NewTemplate '{new_template_name}' 已创建")
    
    def parse_text_template(self):
        """从DocumentBookParse生成Template"""
        # CreateDocumentBookInputDialog
        dialog = TextParsingDialog(self)
        if dialog.exec():
            text_content = dialog.get_text_content()
            template_name = dialog.get_template_name()
            template_description = dialog.get_template_description()
            
            if not text_content.strip():
                QMessageBox.warning(self, "InputError", "请InputFormat要求DocumentBook！")
                return
            
            if not template_name.strip():
                QMessageBox.warning(self, "InputError", "请InputTemplate name！")
                return
            
            # CheckAPIConfiguration
            valid, error_msg = self.ai_connector.validate_config()
            if not valid:
                QMessageBox.warning(self, "APIConfigurationError", f"APIConfigurationInvalid，请先ConfigurationAPIInformation！\nError: {error_msg}")
                self.open_api_config()
                return
            
            # VisibleProgressDialog
            progress_dialog = QProgressDialog("正InParseDocumentBookFormat要求...", "Cancel", 0, 0, self)
            progress_dialog.setWindowTitle("ParseCenter")
            progress_dialog.setModal(True)
            progress_dialog.show()
            
            try:
                # ParseDocumentBook生成Template
                success, result = self.text_parser.parse_text_to_template(
                    text_content, template_name, template_description
                )
                
                progress_dialog.close()
                
                if success:
                    # SaveTemplate
                    save_success = self.format_manager.save_template(template_name, result)
                    
                    if save_success:
                        QMessageBox.information(self, "ParseSuccess", f"Template '{template_name}' 已Success生成并保存！")
                        
                        # 重New加载TemplateList
                        self.format_manager.load_templates()
                        self.load_templates()
                        
                        # SelectedNew创建的Template
                        index = self.template_combo.findText(template_name)
                        if index >= 0:
                            self.template_combo.setCurrentIndex(index)
                        
                        app_logger.info(f"DocumentBookParseTemplate '{template_name}' 创建Success")
                    else:
                        QMessageBox.critical(self, "保存Failed", f"TemplateParseSuccess，但保存Failed！")
                else:
                    QMessageBox.critical(self, "ParseFailed", f"DocumentBookParseFailed：{result}")
                    
            except Exception as e:
                progress_dialog.close()
                error_msg = f"Parse过程发生Error: {str(e)}"
                app_logger.error(error_msg)
                QMessageBox.critical(self, "ParseError", error_msg)
    
    def update_log(self, message, level="INFO"):
        """更NewLogVisible"""
        # 根据LogLevel别SettingsColor
        color = "black"
        if level == "ERROR":
            color = "red"
        elif level == "WARNING":
            color = "orange"
        elif level == "INFO":
            color = "blue"
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        formatted_message = f"<span style='color:{color};'>[{timestamp}] {message}</span>"
        
        # Add to logText box
        self.log_text.append(formatted_message)
        
        # 滚动到Bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_formatting(self):
        """StartFormatting"""
        # CheckDocumentYesNo已Selection
        doc_path = self.doc_path_value.text()
        if doc_path == "未SelectionFile" or not os.path.exists(doc_path):
            QMessageBox.warning(self, "Error", "请先SelectionValid的WordDocument！")
            return
        
        # CheckAPIConfiguration
        valid, error_msg = self.ai_connector.validate_config()
        if not valid:
            QMessageBox.warning(self, "APIConfigurationError", f"APIConfigurationInvalid，请先ConfigurationAPIInformation！\nError: {error_msg}")
            self.open_api_config()
            return
        
        # GetWhenPreviousTemplate
        template_name = self.template_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "Error", "请先SelectionFormattingTemplate！")
            return
        
        # Get保存Path
        save_path = self.save_path_value.text()
        if save_path == "与源FileSameDirectory":
            save_path = None
        
        # Create工作线程
        self.formatting_worker = FormattingWorker(
            self.doc_processor,
            self.ai_connector,
            self.format_manager,
            self.structure_analyzer,
            doc_path,
            template_name,
            save_path
        )
        
        # UpdateApplicationConfiguration
        if save_path and save_path != self.app_config.get("save_path", ""):
            self.app_config["save_path"] = save_path
            config_manager.save_app_config(self.app_config)
            app_logger.debug(f"已更New保存PathConfiguration: {save_path}")
        
        # Connect signals
        self.formatting_worker.progress_updated.connect(self.update_progress)
        self.formatting_worker.log_message.connect(lambda msg: self.update_log(msg, "INFO"))
        self.formatting_worker.task_completed.connect(self.on_formatting_completed)
        
        # UpdateUIStatus
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Start thread
        self.formatting_worker.start()
        app_logger.info("StartFormatting任务")
    
    def stop_formatting(self):
        """StopFormatting"""
        if self.formatting_worker and self.formatting_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "ConfirmStop",
                "确定要StopWhenPreviousFormatting任务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.formatting_worker.stop()
                app_logger.warning("Formatting任务已ManualStop")
                
                # UpdateUIStatus
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
    
    def update_progress(self, value):
        """更NewProgressItem"""
        self.progress_bar.setValue(value)
    
    def on_formatting_completed(self, success, message):
        """FormattingComplete回调"""
        # UpdateUIStatus
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            # UseCustomDialog，提供“OpenDocument”Buttons
            dialog = FormattingCompleteDialog(self, message)
            dialog.exec()
            app_logger.info(f"Formatting任务SuccessComplete，输出File: {message}")
        else:
            QMessageBox.critical(self, "FormattingFailed", f"DocumentFormattingFailed！\nError: {message}")
            app_logger.error(f"Formatting任务Failed: {message}")
    
    def closeEvent(self, event):
        """WindowShutdownEvent"""
        # Stop所Has正In运Line的任务
        if self.formatting_worker and self.formatting_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "ConfirmExit",
                "Formatting任务正In进LineCenter，确定要Exit吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.formatting_worker.stop()
                app_logger.info("ApplicationProgram正InShutdown，Formatting任务已Stop")
            else:
                event.ignore()
                return
        
        # SaveConfiguration
        config_manager.save_app_config(self.app_config)
        
        # RemoveLogProcess器
        app_logger.remove_ui_handler(self.update_log)
        
        app_logger.info("ApplicationProgramNormalShutdown")
        event.accept()
