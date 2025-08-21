# -*- coding: utf-8 -*-
"""
FormattingRule管理模块
负责管理和ApplicationFormattingRule，包括加载预设Template、保存CustomTemplate等。
"""

import os
import json
import json5
from docx.shared import Pt
from ..utils.logger import app_logger

class FormatManager:
    """FormattingRule管理器，负责管理和ApplicationFormattingRule"""
    
    def __init__(self, templates_dir="config/templates"):
        """
        初始化FormattingRule管理器
        
        Args:
            templates_dir: TemplateDirectoryPath
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self.current_template = None
        self.current_template_name = ""
        
        # FontSizeMappingTable
        self.font_size_mapping = {
            "初Number": Pt(42),
            "Small初": Pt(36),
            "OneNumber": Pt(26),
            "SmallOne": Pt(24),
            "二Number": Pt(22),
            "Small二": Pt(18),
            "三Number": Pt(16),
            "Small三": Pt(15),
            "四Number": Pt(14),
            "Small四": Pt(12),
            "五Number": Pt(10.5),
            "Small五": Pt(9),
            "六Number": Pt(7.5),
            "Small六": Pt(6.5),
            "七Number": Pt(5.5),
            "八Number": Pt(5)
        }
        
        # LoadTemplate
        self.load_templates()
        
        app_logger.info(f"FormattingRule管理器初始化Complete，加载了 {len(self.templates)} 个Template")
    
    def load_templates(self):
        """
        加载所Has预设Template
        
        Returns:
            dict: TemplateDictionary，键为Template name，Value为TemplateContent
        """
        self.templates = {}
        
        if not os.path.exists(self.templates_dir):
            app_logger.warning(f"TemplateDirectory不Exists: {self.templates_dir}")
            return self.templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = json5.loads(f.read())
                        template_name = template.get('name', os.path.splitext(filename)[0])
                        self.templates[template_name] = template
                        app_logger.debug(f"加载Template: {template_name}")
                except Exception as e:
                    app_logger.error(f"加载TemplateFailed: {template_path}, Error: {str(e)}")
        
        return self.templates
    
    def get_templates(self):
        """
        获取所HasTemplate
        
        Returns:
            dict: TemplateDictionary
        """
        return self.templates
    
    def get_template_names(self):
        """
        获取所HasTemplate name
        
        Returns:
            list: Template nameList
        """
        return list(self.templates.keys())
    
    def get_template(self, template_name):
        """
        获取指定名称的Template
        
        Args:
            template_name: Template name
            
        Returns:
            dict: TemplateContent，IfTemplate不ExistsRuleReturnNone
        """
        return self.templates.get(template_name)
    
    def set_current_template(self, template_name):
        """
        SettingsWhenPreviousUse的Template
        
        Args:
            template_name: Template name
            
        Returns:
            bool: YesNoSuccessSettings
        """
        if template_name not in self.templates:
            app_logger.warning(f"Template不Exists: {template_name}")
            return False
        
        self.current_template = self.templates[template_name]
        self.current_template_name = template_name
        app_logger.info(f"SettingsWhenPreviousTemplate: {template_name}")
        return True
    
    def get_current_template(self):
        """
        获取WhenPreviousTemplate
        
        Returns:
            dict: WhenPreviousTemplateContent
        """
        return self.current_template
    
    def save_template(self, template_name, template_content):
        """
        保存Template
        
        Args:
            template_name: Template name
            template_content: TemplateContent
            
        Returns:
            bool: YesNoSuccess保存
        """
        # 确保TemplateHasnameField
        if 'name' not in template_content:
            template_content['name'] = template_name
        
        # UpdateInner存Center的Template
        self.templates[template_name] = template_content
        
        # Save到File
        # Record保存PathInformation，方便Debug
        template_file = os.path.join(self.templates_dir, f"{template_name}.json")
        app_logger.debug(f"Template保存Path: {template_file}")
        
        try:
            # 确保TemplateDirectoryExists
            if not os.path.exists(self.templates_dir):
                os.makedirs(self.templates_dir)
                app_logger.debug(f"创建TemplateDirectory: {self.templates_dir}")
            
            # 先Delete同名TemplateFile（IfExists）
            if os.path.exists(template_file):
                os.remove(template_file)
                app_logger.debug(f"Delete原TemplateFile: {template_file}")
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_content, f, ensure_ascii=False, indent=4)
                app_logger.info(f"保存Template: {template_name}")
                
                # ValidateFileYesNo写入Success
                if os.path.exists(template_file):
                    app_logger.debug(f"TemplateFile写入Success: {template_file}")
                else:
                    app_logger.error(f"TemplateFile写入Failed: {template_file}")
                    
                return True
        except Exception as e:
            app_logger.error(f"保存TemplateFailed: {template_name}, Error: {str(e)}")
            return False
    
    def delete_template(self, template_name):
        """
        DeleteTemplate
        
        Args:
            template_name: Template name
            
        Returns:
            bool: YesNoSuccessDelete
        """
        if template_name not in self.templates:
            app_logger.warning(f"Template不Exists: {template_name}")
            return False
        
        # 从Inner存CenterDelete
        del self.templates[template_name]
        
        # 从FileSystemCenterDelete
        template_file = os.path.join(self.templates_dir, f"{template_name}.json")
        if os.path.exists(template_file):
            try:
                os.remove(template_file)
                app_logger.info(f"DeleteTemplate: {template_name}")
                return True
            except Exception as e:
                app_logger.error(f"DeleteTemplateFileFailed: {template_name}, Error: {str(e)}")
                return False
        return True
    
    def create_default_template(self):
        """
        创建DefaultTemplate
        
        Returns:
            dict: DefaultTemplateContent
        """
        default_template = {
            "name": "DefaultTemplate",
            "description": "BasicFormattingTemplate，适用于One般Document",
            "rules": {
                "标题": {
                    "font": "Black体",
                    "size": "Small二",
                    "bold": True,
                    "line_spacing": 1.0
                },
                "OneLevel标题": {
                    "font": "Black体",
                    "size": "五Number",
                    "bold": True,
                    "line_spacing": 1.5
                },
                "二Level标题": {
                    "font": "宋体",
                    "size": "五Number",
                    "bold": True,
                    "line_spacing": 1.5
                },
                "正Document": {
                    "font": "宋体",
                    "size": "五Number",
                    "bold": False,
                    "line_spacing": 19
                }
            }
        }
        return default_template
    
    def format_to_docx_params(self, format_instruction):
        """
        将Format指令Conversion为docxParameters
        
        Args:
            format_instruction: Format指令
            
        Returns:
            dict: docxParameters
        """
        docx_params = {}
        
        # Font名称
        if 'font' in format_instruction:
            docx_params['font_name'] = format_instruction['font']
        
        # FontSize
        if 'size' in format_instruction:
            size = format_instruction['size']
            if isinstance(size, str):
                docx_params['font_size'] = self.font_size_mapping.get(size, Pt(10.5))  # Default五NumberFont
            else:
                docx_params['font_size'] = Pt(size)
        
        # 粗体
        if 'bold' in format_instruction:
            docx_params['bold'] = format_instruction['bold']
        
        # 斜体
        if 'italic' in format_instruction:
            docx_params['italic'] = format_instruction['italic']
        
        # Down划线
        if 'underline' in format_instruction:
            docx_params['underline'] = format_instruction['underline']
        
        # LineBetween距
        if 'line_spacing' in format_instruction:
            docx_params['line_spacing'] = format_instruction['line_spacing']
        
        # 对齐方式
        if 'alignment' in format_instruction:
            docx_params['alignment'] = format_instruction['alignment']
        
        # 首Line缩进
        if 'first_line_indent' in format_instruction:
            docx_params['first_line_indent'] = format_instruction['first_line_indent']
        
        return docx_params
    
    def validate_template(self, template):
        """
        ValidateTemplateFormatYesNo正确
        
        Args:
            template: TemplateContent
            
        Returns:
            (bool, str): YesNoValid及ErrorInformation
        """
        # Check必要Field
        if 'name' not in template:
            return False, "Template缺少nameField"
        
        if 'rules' not in template:
            return False, "Template缺少rulesField"
        
        rules = template['rules']
        if not isinstance(rules, dict):
            return False, "rulesField必须YesDictionaryType"
        
        # CheckEachRule
        for element_type, format_rule in rules.items():
            if not isinstance(format_rule, dict):
                return False, f"Rule '{element_type}' 必须YesDictionaryType"
            
            # Check必要的FormatField
            if 'font' not in format_rule:
                return False, f"Rule '{element_type}' 缺少fontField"
            
            if 'size' not in format_rule:
                return False, f"Rule '{element_type}' 缺少sizeField"
        
        return True, ""
    
    def get_template_as_text(self, template_name):
        """
        获取Template的DocumentBookTable示，用于Visible
        
        Args:
            template_name: Template name
            
        Returns:
            str: Template的DocumentBookTable示
        """
        template = self.get_template(template_name)
        if not template:
            return ""
        
        text = f"{template.get('name', template_name)}\n"
        if 'description' in template:
            text += f"{template['description']}\n"
        
        text += "\nFormatRule:\n"
        
        for element_type, format_rule in template.get('rules', {}).items():
            text += f"{element_type}: "
            format_parts = []
            
            if 'font' in format_rule:
                format_parts.append(f"{format_rule['font']}")
            
            if 'size' in format_rule:
                format_parts.append(f"{format_rule['size']}")
            
            if format_rule.get('bold', False):
                format_parts.append("粗体")
            
            if 'line_spacing' in format_rule:
                format_parts.append(f"Line距 {format_rule['line_spacing']}")
            
            # Add对齐方式Visible
            if 'alignment' in format_rule:
                alignment = format_rule['alignment']
                alignment_display = {
                    "left": "Left对齐",
                    "center": "居Center",
                    "right": "Right对齐",
                    "justify": "两端对齐"
                }.get(alignment, "Left对齐")
                format_parts.append(f"{alignment_display}")
            
            text += ", ".join(format_parts) + "\n"
        
        return text
