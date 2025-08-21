#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件保存逻辑
"""

import sys
import os
sys.path.insert(0, '/Users/Waterdrop/FormulaAI')
sys.path.insert(0, '/Users/Waterdrop/FormulaAI/src')

from src.core.doc_processor import DocProcessor
from src.utils.logger import app_logger

def test_file_save():
    """测试文件保存功能"""
    print("开始测试文件保存逻辑...")
    
    # 创建文档处理器
    doc_processor = DocProcessor()
    
    # 测试文档路径
    test_doc = "/Users/Waterdrop/Nutstore Files/我的坚果云/多模态大模型安全研究_.docx"
    
    if not os.path.exists(test_doc):
        print(f"测试文档不存在: {test_doc}")
        return False
    
    # 读取文档
    print(f"读取测试文档: {test_doc}")
    if not doc_processor.read_document(test_doc):
        print("读取文档失败")
        return False
    
    print("文档读取成功")
    
    # 创建简单的格式化指令
    formatting_instructions = {
        "elements": [
            {
                "type": "标题",
                "content": "测试标题",
                "format": {
                    "font": "黑体",
                    "size": "小二",
                    "bold": True,
                    "line_spacing": 1.0,
                    "alignment": "center"
                }
            },
            {
                "type": "正文",
                "content": "测试正文内容",
                "format": {
                    "font": "宋体",
                    "size": "小四",
                    "bold": False,
                    "line_spacing": 1.5,
                    "alignment": "left"
                }
            }
        ]
    }
    
    print("开始应用格式化指令...")
    
    # 应用格式化
    success = doc_processor.apply_formatting(formatting_instructions)
    
    if success:
        output_file = doc_processor.get_output_file()
        print(f"格式化成功！输出文件: {output_file}")
        
        # 检查文件是否真的存在
        if os.path.exists(output_file):
            print(f"✅ 文件保存成功: {output_file}")
            print(f"文件大小: {os.path.getsize(output_file)} 字节")
            return True
        else:
            print(f"❌ 文件保存失败: 文件不存在 {output_file}")
            return False
    else:
        print("❌ 格式化失败")
        return False

if __name__ == "__main__":
    test_file_save()