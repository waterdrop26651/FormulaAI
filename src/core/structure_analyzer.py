# -*- coding: utf-8 -*-
"""
Document结构Analyze器模块
负责Analyze未FormattingDocument的结构，并生成结构提示。
"""

import re
from ..utils.logger import app_logger

class StructureAnalyzer:
    """Document结构Analyze器，负责Analyze未FormattingDocument的结构"""
    
    def __init__(self):
        """初始化Document结构Analyze器"""
        # 标题KeyWordList
        self.title_keywords = [
            "标题", "题目", "标题：", "题目：", "title", "subject"
        ]
        
        # 摘要KeyWordList
        self.abstract_keywords = [
            "摘要", "摘 要", "摘要：", "abstract", "summary"
        ]
        
        # KeyWordKeyWordList
        self.keywords_keywords = [
            "KeyWord", "KeyWord：", "关 键 Word", "keywords", "key words"
        ]
        
        # 参考Document献KeyWordList
        self.references_keywords = [
            "参考Document献", "参考Document献：", "引用Document献", "references", "bibliography"
        ]
        
        # 数Character标题模式
        self.numeric_title_patterns = [
            r'^\d+\.\s+.+',  # 1. 标题
            r'^\d+\.\d+\.\s+.+',  # 1.1. 标题
            r'^\d+\.\d+\.\d+\.\s+.+',  # 1.1.1. 标题
            r'^[\u4e00-\u9fa5]+\s*[\u3001\uff0c\uff1a]\s*.+',  # One、标题
            r'^\(\d+\)\s+.+',  # (1) 标题
            r'^[A-Z]\.\s+.+',  # A. 标题
            r'^[a-z]\.\s+.+'   # a. 标题
        ]
    
    def analyze_text_features(self, paragraphs):
        """
        AnalyzeDocumentBook特征
        
        Args:
            paragraphs: ParagraphList
            
        Returns:
            dict: DocumentBook特征Information
        """
        if not paragraphs:
            app_logger.warning("没HasParagraphContent可Analyze")
            return {}
        
        features = {
            'paragraph_lengths': [],  # ParagraphLengthList
            'potential_titles': [],   # 潜In的标题ParagraphIndex
            'potential_subtitles': [], # 潜In的Small标题ParagraphIndex
            'special_sections': {},   # SpecialPart，如摘要、KeyWord等
            'avg_length': 0,          # AverageParagraphLength
            'max_length': 0,          # LargestParagraphLength
            'min_length': float('inf')  # SmallestParagraphLength
        }
        
        # 计算ParagraphLengthStatisticsInformation
        total_length = 0
        for i, para in enumerate(paragraphs):
            if not para.strip():  # SkipSpaceParagraph
                continue
                
            length = len(para)
            features['paragraph_lengths'].append(length)
            total_length += length
            
            features['max_length'] = max(features['max_length'], length)
            features['min_length'] = min(features['min_length'], length)
            
            # 检测潜In的标题
            if self._is_potential_title(para, i, len(paragraphs)):
                features['potential_titles'].append(i)
            
            # 检测潜In的Small标题
            elif self._is_potential_subtitle(para, i, len(paragraphs)):
                features['potential_subtitles'].append(i)
            
            # 检测SpecialPart
            self._detect_special_sections(para, i, features)
        
        # 计算AverageLength
        if features['paragraph_lengths']:
            features['avg_length'] = total_length / len(features['paragraph_lengths'])
        
        app_logger.debug(f"CompleteDocumentBook特征Analyze，发现 {len(features['potential_titles'])} 个潜In标题")
        return features
    
    def _is_potential_title(self, paragraph, index, total_paragraphs):
        """
        判断ParagraphYesNo可能Yes标题
        
        Args:
            paragraph: ParagraphDocumentBook
            index: ParagraphIndex
            total_paragraphs: 总Paragraph数
            
        Returns:
            bool: YesNo可能Yes标题
        """
        # Paragraph过Long不太可能Yes标题
        if len(paragraph) > 50:
            return False
        
        # 第OnePhaseUsuallyYes标题的可能性很Big
        if index == 0 and len(paragraph) < 30:
            return True
        
        # Contains标题KeyWord
        for keyword in self.title_keywords:
            if keyword in paragraph.lower():
                return True
        
        # 没Has标Point符Number的ShortParagraph可能Yes标题
        if len(paragraph) < 20 and not any(p in paragraph for p in '.!?;,uff0cuff01uff1fuff1bu3002'):
            return True
        
        return False
    
    def _is_potential_subtitle(self, paragraph, index, total_paragraphs):
        """
        判断ParagraphYesNo可能YesSmall标题
        
        Args:
            paragraph: ParagraphDocumentBook
            index: ParagraphIndex
            total_paragraphs: 总Paragraph数
            
        Returns:
            bool: YesNo可能YesSmall标题
        """
        # CheckYesNo符CompositeCharacter标题模式
        for pattern in self.numeric_title_patterns:
            if re.match(pattern, paragraph):
                return True
        
        # ShortParagraph且DownOnePhase不为Space
        if len(paragraph) < 30 and index < total_paragraphs - 1:
            # 没Has标Point符Number的ShortParagraph可能YesSmall标题
            if not any(p in paragraph for p in '.!?;,uff0cuff01uff1fuff1bu3002'):
                return True
        
        return False
    
    def _detect_special_sections(self, paragraph, index, features):
        """
        检测SpecialPart，如摘要、KeyWord等
        
        Args:
            paragraph: ParagraphDocumentBook
            index: ParagraphIndex
            features: 特征Dictionary，将被Modify
        """
        para_lower = paragraph.lower()
        
        # 检测摘要
        for keyword in self.abstract_keywords:
            if keyword in para_lower:
                features['special_sections']['abstract'] = index
                return
        
        # 检测KeyWord
        for keyword in self.keywords_keywords:
            if keyword in para_lower:
                features['special_sections']['keywords'] = index
                return
        
        # 检测参考Document献
        for keyword in self.references_keywords:
            if keyword in para_lower:
                features['special_sections']['references'] = index
                return
    
    def generate_structure_hints(self, features):
        """
        生成结构提示
        
        Args:
            features: DocumentBook特征Information
            
        Returns:
            dict: 结构提示Information
        """
        hints = {
            'title_index': None,
            'abstract_range': None,
            'keywords_index': None,
            'references_range': None,
            'section_titles': [],
            'subsection_titles': []
        }
        
        # Set标题Index
        if features.get('potential_titles'):
            hints['title_index'] = features['potential_titles'][0]
        
        # SetSpecialPartRange
        if 'abstract' in features.get('special_sections', {}):
            abstract_start = features['special_sections']['abstract']
            abstract_end = abstract_start
            
            # 尝试确定摘要结束Position
            for i in range(abstract_start + 1, len(features.get('paragraph_lengths', []))):
                if i in features.get('potential_titles', []) or i in features.get('potential_subtitles', []):
                    abstract_end = i - 1
                    break
                if 'keywords' in features.get('special_sections', {}) and i == features['special_sections']['keywords']:
                    abstract_end = i - 1
                    break
            
            hints['abstract_range'] = (abstract_start, abstract_end)
        
        # SetKeyWordIndex
        if 'keywords' in features.get('special_sections', {}):
            hints['keywords_index'] = features['special_sections']['keywords']
        
        # Set参考Document献Range
        if 'references' in features.get('special_sections', {}):
            references_start = features['special_sections']['references']
            hints['references_range'] = (references_start, len(features.get('paragraph_lengths', [])) - 1)
        
        # SetParagraph标题
        hints['section_titles'] = features.get('potential_titles', [])[1:] if features.get('potential_titles') else []
        hints['subsection_titles'] = features.get('potential_subtitles', [])
        
        app_logger.debug(f"生成结构提示Complete")
        return hints
    
    def validate_structure(self, structure):
        """
        Validate结构合理性
        
        Args:
            structure: AIReturn的Document结构
            
        Returns:
            (bool, dict): YesNoValid及修正Next的结构
        """
        if not structure or 'elements' not in structure:
            app_logger.error("结构Invalid，缺少elementsField")
            return False, structure
        
        elements = structure['elements']
        if not elements:
            app_logger.error("结构Invalid，elements为Space")
            return False, structure
        
        # Check必要Field
        for i, element in enumerate(elements):
            if 'type' not in element:
                app_logger.warning(f"第{i+1}个Element缺少typeField，AddDefaultValue'正Document'")
                element['type'] = '正Document'
            
            if 'content' not in element:
                app_logger.warning(f"第{i+1}个Element缺少contentField，AddSpaceString")
                element['content'] = ''
            
            if 'format' not in element:
                app_logger.warning(f"第{i+1}个Element缺少formatField，AddDefaultFormat")
                element['format'] = {
                    'font': '宋体',
                    'size': '五Number',
                    'line_spacing': 1.5
                }
        
        app_logger.info(f"结构ValidateComplete，共{len(elements)}个Element")
        return True, structure
