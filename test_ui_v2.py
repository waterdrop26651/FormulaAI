#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新UI架构

用于测试重构后的双面板布局和模块化设计
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
except ImportError:
    print("错误: 未安装PyQt6")
    print("请运行: pip install PyQt6")
    sys.exit(1)

from src.ui.main_window_v2 import MainWindowV2
from src.utils.logger import app_logger


def main():
    """
    主函数 - 启动新UI测试
    """
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("FormulaAI V2")
    app.setApplicationVersion("2.0.0")
    
    # 设置应用程序属性 (PyQt6中已自动启用高DPI支持)
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)  # PyQt6中已移除
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)     # PyQt6中已移除
    
    try:
        # 创建主窗口
        window = MainWindowV2()
        window.show()
        
        app_logger.info("FormulaAI V2 启动成功")
        app_logger.info("新架构特点:")
        app_logger.info("- 双面板布局: 文档管理 + 模板设置")
        app_logger.info("- 模块化设计: 每个面板独立")
        app_logger.info("- 消除复杂度: 无超过3层缩进")
        app_logger.info("- 事件驱动: 面板间通过信号通信")
        
        # 运行应用程序
        return app.exec()
        
    except Exception as e:
        app_logger.error(f"启动失败: {e}")
        print(f"启动失败: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)