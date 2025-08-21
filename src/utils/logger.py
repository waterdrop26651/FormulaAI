# -*- coding: utf-8 -*-
"""
LogTool模块
负责RecordApplicationProgram的LogInformation，并提供LogVisible和管理Function。
"""

import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    """Log管理器Class。管理Log的创建、Format和输出。"""
    
    def __init__(self, name="AIPoliDoc", log_dir="logs"):
        """
        初始化Log管理器。
        
        Args:
            name: Log器名称
            log_dir: LogFile存放Directory
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.log_dir = log_dir
        self.log_file = None
        self.ui_handlers = []
        
        # CreateLogDirectory
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # CreateLogFile
        self._setup_file_handler()
        
        # Create控System台Process器
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """SettingsFileLogProcess器"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"aipolidoc_{timestamp}.log")
        
        file_handler = RotatingFileHandler(
            self.log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Settings控System台LogProcess器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Modified to debug level to show more logs
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def add_ui_handler(self, callback):
        """
        AddUILogProcess器，用于将LogInformation发送到UIVisible。
        
        Args:
            callback: 接收LogInformation的回调Function
        """
        class UIHandler(logging.Handler):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
            
            def emit(self, record):
                log_entry = self.format(record)
                self.callback(log_entry, record.levelname)
        
        handler = UIHandler(callback)
        handler.setLevel(logging.DEBUG)  # Modified to debug level to show more logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.ui_handlers.append(handler)
    
    def remove_ui_handler(self, callback):
        """RemoveUILogProcess器"""
        for handler in self.ui_handlers:
            if handler.callback == callback:
                self.logger.removeHandler(handler)
                self.ui_handlers.remove(handler)
                break
    
    def debug(self, message):
        """RecordDebugLevel别Log"""
        self.logger.debug(message)
    
    def info(self, message):
        """RecordInformationLevel别Log"""
        self.logger.info(message)
    
    def warning(self, message):
        """RecordWarningLevel别Log"""
        self.logger.warning(message)
    
    def error(self, message):
        """RecordErrorLevel别Log"""
        self.logger.error(message)
    
    def critical(self, message):
        """Record严重ErrorLevel别Log"""
        self.logger.critical(message)

# Create全局LogInstance
app_logger = Logger()
