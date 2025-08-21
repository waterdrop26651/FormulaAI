# -*- coding: utf-8 -*-
"""
Configuration管理模块
负责管理ApplicationProgram的ConfigurationInformation，包括APIConfiguration、ApplicationConfiguration和FormattingTemplate。
"""

import os
import json
import json5
from datetime import datetime
from .logger import app_logger

class ConfigManager:
    """Configuration管理器Class，负责加载、保存和管理ApplicationConfiguration"""
    
    def __init__(self, config_dir="config"):
        """
        初始化Configuration管理器
        
        Args:
            config_dir: ConfigurationFileDirectory
        """
        self.config_dir = config_dir
        self.templates_dir = os.path.join(config_dir, "templates")
        self.api_config_file = os.path.join(config_dir, "api_config.json")
        self.app_config_file = os.path.join(config_dir, "app_config.json")
        
        # Ensure config directory exists
        self._ensure_dirs_exist()
        
        # LoadConfiguration
        self.api_config = self._load_config(self.api_config_file)
        self.app_config = self._load_config(self.app_config_file)
        self.templates = self._load_templates()
        
        app_logger.info("Configuration管理器初始化Complete")
    
    def _ensure_dirs_exist(self):
        """确保ConfigurationDirectoryExists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            app_logger.info(f"创建ConfigurationDirectory: {self.config_dir}")
        
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            app_logger.info(f"创建TemplateDirectory: {self.templates_dir}")
    
    def _load_config(self, config_file):
        """加载ConfigurationFile"""
        if not os.path.exists(config_file):
            app_logger.warning(f"ConfigurationFile不Exists: {config_file}，将创建DefaultConfiguration")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json5.loads(f.read())
                app_logger.debug(f"加载ConfigurationFile: {config_file}")
                return config
        except Exception as e:
            app_logger.error(f"加载ConfigurationFileFailed: {config_file}, Error: {str(e)}")
            return {}
    
    def _save_config(self, config, config_file):
        """保存Configuration到File"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                app_logger.debug(f"保存ConfigurationFile: {config_file}")
                return True
        except Exception as e:
            app_logger.error(f"保存ConfigurationFileFailed: {config_file}, Error: {str(e)}")
            return False
    
    def _load_templates(self):
        """加载所HasFormattingTemplate"""
        templates = {}
        
        if not os.path.exists(self.templates_dir):
            app_logger.warning(f"TemplateDirectory不Exists: {self.templates_dir}")
            return templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = json5.loads(f.read())
                        template_name = template.get('name', os.path.splitext(filename)[0])
                        templates[template_name] = template
                        app_logger.debug(f"加载Template: {template_name}")
                except Exception as e:
                    app_logger.error(f"加载TemplateFailed: {template_path}, Error: {str(e)}")
        
        return templates
    
    def get_api_config(self):
        """获取APIConfiguration"""
        return self.api_config
    
    def save_api_config(self, api_config):
        """保存APIConfiguration"""
        api_config['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.api_config = api_config
        return self._save_config(api_config, self.api_config_file)
    
    def get_app_config(self):
        """获取ApplicationConfiguration"""
        return self.app_config
    
    def save_app_config(self, app_config):
        """保存ApplicationConfiguration"""
        self.app_config = app_config
        return self._save_config(app_config, self.app_config_file)
    
    def get_templates(self):
        """获取所HasFormattingTemplate"""
        return self.templates
    
    def get_template(self, template_name):
        """获取指定名称的FormattingTemplate"""
        return self.templates.get(template_name)
    
    def save_template(self, template_name, template_content):
        """保存FormattingTemplate"""
        # 确保TemplateHasnameField
        if 'name' not in template_content:
            template_content['name'] = template_name
        
        # UpdateInner存Center的Template
        self.templates[template_name] = template_content
        
        # Save到File
        template_file = os.path.join(self.templates_dir, f"{template_name}.json")
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_content, f, ensure_ascii=False, indent=4)
                app_logger.info(f"保存Template: {template_name}")
                return True
        except Exception as e:
            app_logger.error(f"保存TemplateFailed: {template_name}, Error: {str(e)}")
            return False
    
    def delete_template(self, template_name):
        """DeleteFormattingTemplate"""
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

# Create全局Configuration管理器Instance
config_manager = ConfigManager()
