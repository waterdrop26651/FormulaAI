# -*- coding: utf-8 -*-
"""
页眉页脚配置模块
定义页眉页脚的配置数据结构
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class HeaderFooterConfig:
    """页眉页脚配置类"""
    
    # 基础设置
    enable_header: bool = False
    enable_footer: bool = False
    
    # 页眉配置
    header_content: str = ""
    header_alignment: str = "center"  # left, center, right, justify
    header_font: str = "宋体"
    header_font_size: int = 10
    header_bold: bool = False
    header_italic: bool = False
    
    # 页脚配置
    footer_content: str = ""
    footer_alignment: str = "center"
    footer_font: str = "宋体"
    footer_font_size: int = 9
    footer_bold: bool = False
    footer_italic: bool = False
    
    # 高级设置
    different_first_page: bool = False
    different_odd_even: bool = False
    
    # 首页页眉页脚
    first_page_header_content: str = ""
    first_page_footer_content: str = ""
    
    # 偶数页页眉页脚
    even_page_header_content: str = ""
    even_page_footer_content: str = ""
    
    # 页码设置
    include_page_number: bool = False
    page_number_position: str = "footer_center"  # header_left, header_center, header_right, footer_left, footer_center, footer_right
    page_number_format: str = "第 {page} 页"  # {page} 为页码占位符
    
    # 制表符布局（三栏）
    use_three_column_layout: bool = False
    header_left_content: str = ""
    header_center_content: str = ""
    header_right_content: str = ""
    footer_left_content: str = ""
    footer_center_content: str = ""
    footer_right_content: str = ""
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于序列化"""
        return {
            'enable_header': self.enable_header,
            'enable_footer': self.enable_footer,
            'header_content': self.header_content,
            'header_alignment': self.header_alignment,
            'header_font': self.header_font,
            'header_font_size': self.header_font_size,
            'header_bold': self.header_bold,
            'header_italic': self.header_italic,
            'footer_content': self.footer_content,
            'footer_alignment': self.footer_alignment,
            'footer_font': self.footer_font,
            'footer_font_size': self.footer_font_size,
            'footer_bold': self.footer_bold,
            'footer_italic': self.footer_italic,
            'different_first_page': self.different_first_page,
            'different_odd_even': self.different_odd_even,
            'first_page_header_content': self.first_page_header_content,
            'first_page_footer_content': self.first_page_footer_content,
            'even_page_header_content': self.even_page_header_content,
            'even_page_footer_content': self.even_page_footer_content,
            'include_page_number': self.include_page_number,
            'page_number_position': self.page_number_position,
            'page_number_format': self.page_number_format,
            'use_three_column_layout': self.use_three_column_layout,
            'header_left_content': self.header_left_content,
            'header_center_content': self.header_center_content,
            'header_right_content': self.header_right_content,
            'footer_left_content': self.footer_left_content,
            'footer_center_content': self.footer_center_content,
            'footer_right_content': self.footer_right_content
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HeaderFooterConfig':
        """从字典创建配置对象，用于反序列化"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def validate(self) -> tuple[bool, str]:
        """验证配置的有效性"""
        # 检查对齐方式
        valid_alignments = ['left', 'center', 'right', 'justify']
        if self.header_alignment not in valid_alignments:
            return False, f"页眉对齐方式无效: {self.header_alignment}"
        if self.footer_alignment not in valid_alignments:
            return False, f"页脚对齐方式无效: {self.footer_alignment}"
        
        # 检查字体大小
        if not (6 <= self.header_font_size <= 72):
            return False, f"页眉字体大小超出范围: {self.header_font_size}"
        if not (6 <= self.footer_font_size <= 72):
            return False, f"页脚字体大小超出范围: {self.footer_font_size}"
        
        # 检查页码位置
        valid_positions = [
            'header_left', 'header_center', 'header_right',
            'footer_left', 'footer_center', 'footer_right'
        ]
        if self.page_number_position not in valid_positions:
            return False, f"页码位置无效: {self.page_number_position}"
        
        # 检查页码格式
        if self.include_page_number and '{page}' not in self.page_number_format:
            return False, "页码格式必须包含 {page} 占位符"
        
        return True, "配置验证通过"
    
    def get_effective_header_content(self) -> str:
        """获取有效的页眉内容（考虑三栏布局）"""
        if self.use_three_column_layout:
            return f"{self.header_left_content}\t{self.header_center_content}\t{self.header_right_content}"
        return self.header_content
    
    def get_effective_footer_content(self) -> str:
        """获取有效的页脚内容（考虑三栏布局）"""
        if self.use_three_column_layout:
            return f"{self.footer_left_content}\t{self.footer_center_content}\t{self.footer_right_content}"
        return self.footer_content