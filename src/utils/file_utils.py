# -*- coding: utf-8 -*-
"""
FileTool模块
负责FileOperation相关的ToolFunction，如FileSelection、PathProcess等。
"""

import os
import time
import shutil
from datetime import datetime
from .logger import app_logger

def generate_output_filename(input_file, custom_save_path=None):
    """
    生成输出File名
    
    Args:
        input_file: InputFile path
        custom_save_path: Custom保存Path，If指定RuleUse该Path
        
    Returns:
        输出File path
    """
    # GetFile名和Extension
    filename, ext = os.path.splitext(os.path.basename(input_file))
    
    # Initial output filename
    output_filename = f"{filename}_已Formatting{ext}"
    
    # Use custom save path if specified
    if custom_save_path and os.path.isdir(custom_save_path):
        app_logger.debug(f"UseCustom保存Path: {custom_save_path}")
        output_dir = custom_save_path
    else:
        # Otherwise use original file directory
        output_dir = os.path.dirname(input_file)
        app_logger.debug(f"Use原FileDirectory作为保存Path: {output_dir}")
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            app_logger.debug(f"创建输出Directory: {output_dir}")
        except Exception as e:
            app_logger.error(f"创建输出DirectoryFailed: {output_dir}, Error: {str(e)}")
            # Use original file directory if directory creation fails
            output_dir = os.path.dirname(input_file)
    
    output_path = os.path.join(output_dir, output_filename)
    
    # Add timestamp if file already exists
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"{filename}_已Formatting_{timestamp}{ext}"
        output_path = os.path.join(output_dir, output_filename)
    
    app_logger.debug(f"生成输出File path: {output_path}")
    return output_path

def ensure_dir_exists(dir_path):
    """
    确保DirectoryExists，如不ExistsRule创建
    
    Args:
        dir_path: DirectoryPath
        
    Returns:
        YesNoSuccess创建或Directory已Exists
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            app_logger.debug(f"创建Directory: {dir_path}")
            return True
        except Exception as e:
            app_logger.error(f"创建DirectoryFailed: {dir_path}, Error: {str(e)}")
            return False
    return True

def is_valid_docx(file_path):
    """
    CheckYesNoYesValid的WordDocument
    
    Args:
        file_path: File path
        
    Returns:
        YesNoYesValid的WordDocument
    """
    if not os.path.exists(file_path):
        app_logger.warning(f"File不Exists: {file_path}")
        return False
    
    # Check extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.docx':
        app_logger.warning(f"非WordDocumentFormat: {file_path}")
        return False
    
    # Check file size
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            app_logger.warning(f"SpaceFile: {file_path}")
            return False
    except Exception as e:
        app_logger.error(f"Check file sizeFailed: {file_path}, Error: {str(e)}")
        return False
    
    return True

def backup_file(file_path):
    """
    BackupFile
    
    Args:
        file_path: 要Backup的File path
        
    Returns:
        BackupFile path或None(IfBackupFailed)
    """
    if not os.path.exists(file_path):
        app_logger.warning(f"要Backup的File不Exists: {file_path}")
        return None
    
    try:
        # Generate backup filename
        dir_path = os.path.dirname(file_path)
        filename, ext = os.path.splitext(os.path.basename(file_path))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{filename}_backup_{timestamp}{ext}"
        backup_path = os.path.join(dir_path, backup_filename)
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        app_logger.info(f"FileBackupSuccess: {file_path} -> {backup_path}")
        return backup_path
    except Exception as e:
        app_logger.error(f"FileBackupFailed: {file_path}, Error: {str(e)}")
        return None
