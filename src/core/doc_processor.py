# -*- coding: utf-8 -*-
"""
DocumentProcess模块
负责读取、Parse和写入WordDocument，以及ApplicationFormattingFormat。
"""

import os
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Length
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING
from docx.oxml.ns import qn
from ..utils.logger import app_logger
from ..utils.file_utils import generate_output_filename, is_valid_docx, backup_file
from ..utils.font_manager import FontManager

class DocProcessor:
    """DocumentProcess器，负责读取、Parse和写入WordDocument"""
    
    def __init__(self):
        """初始化DocumentProcess器"""
        self.document = None
        self.input_file = None
        self.output_file = None
        self.paragraphs_text = []
        
        # UseFont管理器获取FontInformation
        self.font_manager = FontManager()
        
        # CharacterNumberMapping
        self.font_size_mapping = {
            "Small二": Pt(18),
            "三Number": Pt(16),
            "Small三": Pt(15),
            "四Number": Pt(14),
            "Small四": Pt(12),
            "五Number": Pt(10.5),
            "Small五": Pt(9),
            "六Number": Pt(7.5)
        }
        
        app_logger.debug(f"DocumentProcess器初始化Complete，CharacterNumberMapping: {list(self.font_size_mapping.keys())}")
    
    def read_document(self, file_path):
        """
        读取WordDocumentContent
        
        Args:
            file_path: Document path
            
        Returns:
            YesNoSuccess读取Document
        """
        if not is_valid_docx(file_path):
            app_logger.error(f"Invalid的WordDocument: {file_path}")
            return False
        
        try:
            self.document = Document(file_path)
            self.input_file = file_path
            self.paragraphs_text = [p.text for p in self.document.paragraphs]
            
            app_logger.info(f"Success读取Document: {file_path}")
            app_logger.debug(f"DocumentContains {len(self.document.paragraphs)} 个Paragraph")
            return True
        except Exception as e:
            app_logger.error(f"读取DocumentFailed: {file_path}, Error: {str(e)}")
            return False
    
    def get_document_text(self):
        """
        获取Document的纯DocumentBookContent
        
        Returns:
            Document的ParagraphDocumentBookList
        """
        if not self.document:
            app_logger.warning("尚未加载Document")
            return []
        
        return self.paragraphs_text
    
    def apply_formatting(self, formatting_instructions, custom_save_path=None):
        """
        根据Formatting指令ApplicationFormat
        
        Args:
            formatting_instructions: Formatting指令，ContainsElementType和FormatInformation
            custom_save_path: Custom保存Path，If指定RuleUse该Path
            
        Returns:
            YesNoSuccessApplicationFormat
        """
        if not self.document:
            app_logger.error("尚未加载Document，NoneLawApplicationFormat")
            return False
        
        try:
            # RecordFormat指令，方便Debug
            app_logger.debug(f"Format指令: {formatting_instructions}")
            
            # Checkformatting_instructions结构
            if not isinstance(formatting_instructions, dict):
                app_logger.error(f"Formatting指令不YesDictionaryType: {type(formatting_instructions)}")
                return False
            
            elements = formatting_instructions.get('elements', [])
            if not isinstance(elements, list):
                app_logger.error(f"ElementList不YesListType: {type(elements)}")
                return False
            
            app_logger.info(f"StartApplicationFormattingFormat，共Has {len(elements)} 个Element")
            
            # RecordCustom保存Path
            if custom_save_path:
                app_logger.info(f"UseCustom保存Path: {custom_save_path}")
            
            # Backup原始Document
            backup_path = backup_file(self.input_file)
            app_logger.info(f"FileBackupSuccess: {self.input_file} -> {backup_path}")
            
            # CreateNewDocument以ApplicationFormat
            try:
                new_doc = Document()
                app_logger.debug("Success创建NewDocument")
            except Exception as e:
                app_logger.error(f"创建NewDocumentFailed: {str(e)}")
                return False
            
            # 批ProcessElement，避免Inner存压力
            batch_size = 10  # 每批Process10个Element，进One步减少Inner存压力
            total_elements = len(elements)
            
            for batch_start in range(0, total_elements, batch_size):
                batch_end = min(batch_start + batch_size, total_elements)
                app_logger.info(f"Process批次: {batch_start+1}-{batch_end}/{total_elements}")
                
                # ProcessWhenPrevious批次的Element
                for i in range(batch_start, batch_end):
                    element = elements[i]
                    try:
                        app_logger.debug(f"Process第 {i+1}/{total_elements} 个Element")
                        self._process_element(new_doc, element)
                    except Exception as e:
                        app_logger.error(f"Process第 {i+1} 个ElementTime发生Error: {str(e)}")
                        # ContinueProcessDownOne个Element，不Center断Entire过程
                
                # 批次ProcessCompleteNext，StrongSystem垃圾回收
                import gc
                gc.collect()
                app_logger.debug(f"批次 {batch_start+1}-{batch_end} ProcessComplete，已执Line垃圾回收")
            
            # 生成输出File名
            try:
                self.output_file = generate_output_filename(self.input_file, custom_save_path)
                app_logger.debug(f"生成输出File名: {self.output_file}")
            except Exception as e:
                app_logger.error(f"生成输出File名Failed: {str(e)}")
                # Use custom save path if specified
                if custom_save_path and os.path.isdir(custom_save_path):
                    filename = os.path.basename(self.input_file).replace('.docx', '_已Formatting.docx')
                    self.output_file = os.path.join(custom_save_path, filename)
                else:
                    self.output_file = self.input_file.replace('.docx', '_已Formatting.docx')
                app_logger.debug(f"UseDefault输出File名: {self.output_file}")
            
            # SaveDocument
            try:
                # Ensure output directory exists
                output_dir = os.path.dirname(self.output_file)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    app_logger.debug(f"创建输出Directory: {output_dir}")
                
                new_doc.save(self.output_file)
                app_logger.info(f"SuccessApplicationFormattingFormat并保存到: {self.output_file}")
                return True
            except Exception as e:
                app_logger.error(f"保存DocumentFailed: {str(e)}")
                return False
        except Exception as e:
            app_logger.error(f"ApplicationFormattingFormatFailed: {str(e)}")
            import traceback
            app_logger.error(f"详细ErrorInformation: {traceback.format_exc()}")
            return False
    
    def _process_element(self, doc, element):
        """
        ProcessSingleFormattingElement
        
        Args:
            doc: 目标DocumentObject
            element: FormattingElementInformation
        """
        paragraph = None
        run = None
        
        try:
            # RecordWhenPreviousProcess的ElementInformation
            app_logger.debug(f"StartProcessElement: {element}")
            
            # CheckElement结构
            if not isinstance(element, dict):
                app_logger.error(f"Element不YesDictionaryType: {type(element)}")
                return
            
            content = element.get('content', '')
            app_logger.debug(f"ElementContent: {content[:50]}...")
            
            element_type = element.get('type', '正Document')
            app_logger.debug(f"ElementType: {element_type}")
            
            format_info = element.get('format', {})
            app_logger.debug(f"FormatInformation: {format_info}")
            
            # Checkformat_info结构
            if not isinstance(format_info, dict):
                app_logger.error(f"FormatInformation不YesDictionaryType: {type(format_info)}")
                format_info = {}
            
            # AddParagraph
            paragraph = doc.add_paragraph()
            app_logger.debug("SuccessAddParagraph")
            
            run = paragraph.add_run(content)
            app_logger.debug("SuccessAddDocumentBook运Line")
            
            # ApplicationFont
            self._apply_font(run, format_info)
            app_logger.debug("SuccessApplicationFontFormat")
            
            # ApplicationParagraphFormat
            self._apply_paragraph_format(paragraph, format_info, element_type)
            app_logger.debug("SuccessApplicationParagraphFormat")
            
            app_logger.debug(f"CompleteElementProcess: {element_type}, Content: {content[:20]}...")
            
        except Exception as e:
            app_logger.error(f"ProcessElementTime发生Abnormal: {str(e)}")
            # Record详细ErrorInformation
            import traceback
            app_logger.error(f"Abnormal详情: {traceback.format_exc()}")
            # 不抛出Abnormal，ContinueProcessDownOne个Element
        finally:
            # 清理LocalVariable，释放Inner存
            try:
                del paragraph, run
            except:
                pass
            
            # StrongSystem垃圾回收，防止Inner存泄漏
            import gc
            gc.collect()
    
    def _apply_font(self, run, format_info):
        """
        ApplicationFontFormat，增StrongInner存Safe性
        
        Args:
            run: DocumentBook运LineObject
            format_info: FormatInformation
        """
        if not run or not hasattr(run, 'font'):
            app_logger.error("Invalid的DocumentBook运LineObject")
            return
            
        try:
            # Font名称 - UseSafe的DefaultValue
            font_name = format_info.get('font', '宋体') if format_info else '宋体'
            app_logger.debug(f"原始Font名称: {font_name}")
            
            # 简化FontProcess，避免Complex的MappingOperation
            safe_fonts = {'宋体': 'SimSun', 'Black体': 'SimHei', '楷体': 'KaiTi', '仿宋': 'FangSong'}
            document_font = safe_fonts.get(font_name, font_name)
            app_logger.debug(f"用于Document的Font名称: {document_font}")
            
            # SafeSettingsFont名称
            try:
                if hasattr(run.font, 'name'):
                    run.font.name = document_font
            except Exception as e:
                app_logger.error(f"SettingsFont名称Failed: {str(e)}")
            
            # 简化CenterDocumentFontSettings，避免直接OperationXMLElement
            try:
                if hasattr(run, '_element') and hasattr(run._element, 'rPr'):
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), document_font)
                    app_logger.debug(f"SuccessSettingsCenterDocumentFont: {document_font}")
            except Exception as e:
                app_logger.debug(f"SettingsCenterDocumentFontFailed，UseDefaultSettings: {str(e)}")
                
            # FontSize - UseSafe的DefaultValue
            font_size = format_info.get('size', 'Small四') if format_info else 'Small四'
            app_logger.debug(f"原始FontSize: {font_size}")
            
            try:
                if isinstance(font_size, str) and font_size in self.font_size_mapping:
                    mapped_size = self.font_size_mapping[font_size]
                    app_logger.debug(f"MappingNext的FontSize: {mapped_size}")
                    if hasattr(run.font, 'size'):
                        run.font.size = mapped_size
            except Exception as e:
                app_logger.error(f"SettingsFontSizeFailed: {str(e)}")
            
            # SafeSettingsFontProperty
            try:
                bold = format_info.get('bold', False) if format_info else False
                if hasattr(run, 'bold'):
                    run.bold = bold
                    app_logger.debug(f"Settings粗体: {bold}")
            except Exception as e:
                app_logger.error(f"Settings粗体Failed: {str(e)}")
            
            try:
                italic = format_info.get('italic', False) if format_info else False
                if hasattr(run, 'italic'):
                    run.italic = italic
                    app_logger.debug(f"Settings斜体: {italic}")
            except Exception as e:
                app_logger.error(f"Settings斜体Failed: {str(e)}")
            
            try:
                underline = format_info.get('underline', False) if format_info else False
                if hasattr(run, 'underline'):
                    run.underline = underline
                    app_logger.debug(f"SettingsDown划线: {underline}")
            except Exception as e:
                app_logger.error(f"SettingsDown划线Failed: {str(e)}")
            
        except Exception as e:
            app_logger.error(f"ApplicationFontFormatTime发生严重Abnormal: {str(e)}")
            import traceback
            app_logger.error(f"Abnormal详情: {traceback.format_exc()}")
            # 不抛出Abnormal，UseDefaultFontSettings
    
    def _apply_paragraph_format(self, paragraph, format_info, element_type):
        """
        ApplicationParagraphFormat，增StrongInner存Safe性
        
        Args:
            paragraph: ParagraphObject
            format_info: FormatInformation
            element_type: ElementType
        """
        if not paragraph or not hasattr(paragraph, 'paragraph_format'):
            app_logger.error("Invalid的ParagraphObject")
            return
            
        try:
            # Safe获取FormatInformation
            if not format_info or not isinstance(format_info, dict):
                format_info = {}
            
            # LineBetween距 - Use更Safe的DefaultValue
            line_spacing = format_info.get('line_spacing', 1.5)
            app_logger.debug(f"SettingsLineBetween距: {line_spacing}")
            
            try:
                if isinstance(line_spacing, (int, float)) and hasattr(paragraph, 'paragraph_format'):
                    # 防止AbnormalBig的LineBetween距Value导致Program崩溃
                    if line_spacing > 3.0 or line_spacing < 0.8:
                        app_logger.warning(f"检测到AbnormalLineBetween距Value: {line_spacing}，将UseDefaultValue1.5")
                        line_spacing = 1.5
                    
                    if abs(line_spacing - 1.0) < 0.1:
                        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                        app_logger.debug("Settings单倍LineBetween距")
                    elif abs(line_spacing - 1.5) < 0.1:
                        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
                        app_logger.debug("Settings1.5倍LineBetween距")
                    elif abs(line_spacing - 2.0) < 0.1:
                        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
                        app_logger.debug("Settings双倍LineBetween距")
                    else:
                        # UseDefault1.5倍LineBetween距，避免ComplexSettings
                        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
                        app_logger.debug("UseDefault1.5倍LineBetween距")
            except Exception as e:
                app_logger.error(f"SettingsLineBetween距Failed: {str(e)}")
            
            # 对齐方式 - 简化Process
            try:
                alignment = format_info.get('alignment', 'left')
                app_logger.debug(f"Settings对齐方式: {alignment}")
                
                if hasattr(paragraph, 'alignment'):
                    if alignment == 'center':
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    elif alignment == 'right':
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                    elif alignment == 'justify':
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
                    else:  # DefaultLeft对齐
                        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            except Exception as e:
                app_logger.error(f"Settings对齐方式Failed: {str(e)}")
            
            # 首Line缩进 - 简化Process
            try:
                if hasattr(paragraph, 'paragraph_format') and hasattr(paragraph.paragraph_format, 'first_line_indent'):
                    first_line_indent = format_info.get('first_line_indent', None)
                    
                    if first_line_indent is not None and isinstance(first_line_indent, (int, float)):
                        if 0 <= first_line_indent <= 50:  # Limit缩进Range
                            paragraph.paragraph_format.first_line_indent = Pt(first_line_indent)
                            app_logger.debug(f"Settings首Line缩进: {first_line_indent}Pound")
                    elif element_type == '正Document':  # 正DocumentDefault缩进
                        paragraph.paragraph_format.first_line_indent = Pt(21)
                        app_logger.debug("Settings正DocumentDefault首Line缩进: 21Pound")
            except Exception as e:
                app_logger.error(f"Settings首Line缩进Failed: {str(e)}")
            
            # PhaseBetween距 - 简化Process，避免ComplexSettings
            try:
                if hasattr(paragraph, 'paragraph_format'):
                    # UseFixed的SafeBetween距Value
                    if hasattr(paragraph.paragraph_format, 'space_before'):
                        paragraph.paragraph_format.space_before = Pt(0)
                    if hasattr(paragraph.paragraph_format, 'space_after'):
                        paragraph.paragraph_format.space_after = Pt(0)
                    app_logger.debug("SettingsPhaseBetween距为0")
            except Exception as e:
                app_logger.error(f"SettingsPhaseBetween距Failed: {str(e)}")
                
        except Exception as e:
            app_logger.error(f"ApplicationParagraphFormatTime发生严重Abnormal: {str(e)}")
            import traceback
            app_logger.error(f"Abnormal详情: {traceback.format_exc()}")
            # 不抛出Abnormal，UseDefaultParagraphSettings
    
    def get_output_file(self):
        """
        获取输出File path
        
        Returns:
            输出File path
        """
        return self.output_file
