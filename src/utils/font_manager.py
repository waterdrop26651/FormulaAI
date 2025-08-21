# -*- coding: utf-8 -*-
"""
Font管理模块
负责获取SystemFont、ValidateFontAvailable性和提供FontMappingFunction。
"""

import os
import json
import platform
from PyQt6.QtGui import QFontDatabase, QFont
from ..utils.logger import app_logger

class FontManager:
    """Font管理器，负责获取和ValidateSystemFont"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化Font管理器"""
        if self._initialized:
            return
            
        self._initialized = True
        self.system_fonts = []
        self.chinese_fonts = []
        self.font_mapping = {}
        self.reverse_mapping = {}
        self.display_name_mapping = {}  # SystemFont名称到Visible名称的Mapping
        self.system_to_display_mapping = {}  # SystemFont名称到Visible名称的Mapping
        self.display_to_system_mapping = {}  # Visible名称到SystemFont名称的Mapping
        self.font_availability_cache = {}  # FontAvailable性Cache，避免RepeatCheck
        
        # LoadFontInformation
        self.load_system_fonts()
        self.load_font_mapping()
        
        app_logger.info(f"Font管理器初始化Complete，共加载 {len(self.system_fonts)} 个SystemFont")
    
    def load_system_fonts(self):
        """加载System所HasAvailableFont"""
        try:
            # UsePyQt6StaticMethod获取FontList
            all_families = QFontDatabase.families()
            app_logger.debug(f"QFontDatabase原始FontListLength: {len(all_families)}")
            if len(all_families) < 5:  # IfFontQuantityAbnormal少，Record所HasFont
                app_logger.debug(f"所Has原始Font: {all_families}")
            
            # Filter掉以@Beginning的Font（这些UsuallyYes垂直Direction的Font变体）
            self.system_fonts = [font for font in all_families if not font.startswith('@')]
            app_logger.debug(f"FilterNext的FontListLength: {len(self.system_fonts)}")
            
            # Create直接的FontMappingTable，将SystemFont名称Mapping到CenterDocumentVisible名称
            self.system_to_display_mapping = {
                # macOSSystemFont
                'PingFang SC': '苹方',
                'PingFang TC': '苹方',
                'Songti SC': '宋体',
                'Songti TC': '宋体',
                'Heiti SC': 'Black体',
                'Heiti TC': 'Black体',
                'Kaiti SC': '楷体',
                'Kaiti TC': '楷体',
                'Yuanti SC': '圆体',
                'Yuanti TC': '圆体',
                'STSong': '华Document宋体',
                'STHeiti': '华DocumentBlack体',
                'STKaiti': '华Document楷体',
                'STFangsong': '华Document仿宋',
                'Hiragino Sans GB': '冬青Black体',
                'Lantinghei SC': '兰亭Black',
                'Wawati SC': '娃娃体',
                'Xingkai SC': 'Line楷',
                'Baoli SC': 'Newspaper隆体',
                'Libian SC': '隶变体',
                'Weibei SC': '魏碧体',
                'Yuppy SC': '雅痛体',
                'Yuppy TC': '雅痛体',
                
                # WindowsSystemFont
                'SimSun': '宋体',
                'SimHei': 'Black体',
                'KaiTi': '楷体',
                'FangSong': '仿宋',
                'Microsoft YaHei': '微Soft雅Black',
                'Microsoft YaHei UI': '微Soft雅Black',
                'YouYuan': '幼圆',
                'LiSu': '隶Book',
                'FZYaoTi': '方正姚体',
                'FZShuTi': '方正舒体',
                'DengXian': '等线',
                'DengXian Light': '等线 Light',
                
                # 常用英DocumentFont
                'Arial': 'Arial',
                'Times New Roman': 'Times New Roman',
                'Courier New': 'Courier New',
                'Verdana': 'Verdana',
                'Tahoma': 'Tahoma',
                'Calibri': 'Calibri',
                'Helvetica': 'Helvetica',
                'Helvetica Neue': 'Helvetica Neue'
            }
            
            # Create反向Mapping（Visible名称 -> System名称）
            self.display_to_system_mapping = {}
            for system_name, display_name in self.system_to_display_mapping.items():
                self.display_to_system_mapping[display_name] = system_name
                # IfYesCenterDocumentFont，Add到CenterDocumentFontList
                if any(keyword in display_name for keyword in ['宋', 'Black', '楷', '仿', '微', '华', '圆', '苹']):
                    if display_name not in self.chinese_fonts:
                        self.chinese_fonts.append(display_name)
                        app_logger.debug(f"AddCenterDocumentFont: {display_name}")
            
            # 尝试UseQFontDatabase获取更MultipleFontInformation
            try:
                for font_name in self.system_fonts:
                    # IfFont名称ContainsCenterDocumentCharacter符，Rule可能YesCenterDocumentFont
                    if any(0x4E00 <= ord(char) <= 0x9FFF for char in font_name):
                        if font_name not in self.chinese_fonts:
                            self.chinese_fonts.append(font_name)
                            app_logger.debug(f"Add含CenterDocumentCharacter符的Font: {font_name}")
                    
                    # IfFont名称ContainsCommonCenterDocumentFontKeyWord
                    if any(keyword in font_name for keyword in ['Song', 'Hei', 'Kai', 'Fang', 'Yuan', 'Ming', 'SimSun', 'SimHei', 'KaiTi', 'FangSong']):
                        # 尝试为其创建One个CenterDocumentVisible名称
                        if font_name not in self.system_to_display_mapping:
                            if 'Song' in font_name:
                                display_name = '宋体'
                            elif 'Hei' in font_name:
                                display_name = 'Black体'
                            elif 'Kai' in font_name:
                                display_name = '楷体'
                            elif 'Fang' in font_name:
                                display_name = '仿宋'
                            elif 'Yuan' in font_name:
                                display_name = '圆体'
                            elif 'Ming' in font_name:
                                display_name = '明体'
                            else:
                                continue
                                
                            # Add到Mapping
                            self.system_to_display_mapping[font_name] = display_name
                            self.display_to_system_mapping[display_name] = font_name
                            
                            # Add到CenterDocumentFontList
                            if display_name not in self.chinese_fonts:
                                self.chinese_fonts.append(display_name)
                                app_logger.debug(f"Add推断的CenterDocumentFont: {display_name}")
            except Exception as e:
                app_logger.error(f"AnalyzeFontInformationFailed: {str(e)}")
            
            # If从 QFontDatabase 获取的FontListAbnormal少，尝试其他Method
            if len(self.system_fonts) < 10:
                try:
                    system = platform.system()
                    app_logger.debug(f"WhenPreviousOperationSystem: {system}")
                    
                    # InmacOSUp尝试Usefc-list命令获取Font
                    if system == "Darwin":  # macOS
                        import subprocess
                        try:
                            # Usefc-list命令获取FontList
                            result = subprocess.run(['fc-list', ':', 'family'], capture_output=True, text=True, timeout=5)
                            output = result.stdout
                            app_logger.debug(f"fc-list命令执LineStatus: {result.returncode}")
                            
                            # Parse输出提取Font名称
                            fonts_from_system = []
                            for line in output.split('\n'):
                                if line.strip():
                                    # fc-listReturn的Font名称可能ContainsMultiple个逗NumberMinute隔的名称
                                    for font in line.split(','):
                                        font = font.strip()
                                        if font and font not in fonts_from_system:
                                            fonts_from_system.append(font)
                            
                            app_logger.debug(f"Throughfc-list获取的FontQuantity: {len(fonts_from_system)}")
                            if len(fonts_from_system) > len(self.system_fonts):
                                app_logger.debug(f"Usefc-list获取的FontList替代QFontDatabase")
                                self.system_fonts = fonts_from_system
                        except Exception as e:
                            app_logger.error(f"Usefc-list获取FontFailed: {str(e)}")
                            
                        # IfUp面的MethodFailed，尝试Usesystem_profiler
                        if len(self.system_fonts) < 10:
                            try:
                                # Usesystem_profiler获取FontList
                                result = subprocess.run(['system_profiler', 'SPFontsDataType'], capture_output=True, text=True, timeout=5)
                                output = result.stdout
                                app_logger.debug(f"system_profiler命令执LineStatus: {result.returncode}")
                                
                                # Parse输出提取Font名称
                                fonts_from_system = []
                                for line in output.split('\n'):
                                    if 'Full Name:' in line:
                                        font_name = line.split('Full Name:')[1].strip()
                                        fonts_from_system.append(font_name)
                                
                                app_logger.debug(f"Throughsystem_profiler获取的FontQuantity: {len(fonts_from_system)}")
                                if len(fonts_from_system) > len(self.system_fonts):
                                    app_logger.debug(f"Usesystem_profiler获取的FontList替代先Previous的List")
                                    self.system_fonts = fonts_from_system
                            except Exception as e:
                                app_logger.error(f"Usesystem_profiler获取FontFailed: {str(e)}")
                except Exception as e:
                    app_logger.error(f"尝试替代Method获取FontFailed: {str(e)}")
            
            # 增加CommonFont的CenterDocument名称和英Document名称Mapping
            common_fonts = {
                # CenterDocument常用Font
                "宋体": "SimSun",
                "Black体": "SimHei",
                "楷体": "KaiTi",
                "仿宋": "FangSong",
                "微Soft雅Black": "Microsoft YaHei",
                "微Soft雅Black UI": "Microsoft YaHei UI",
                "华Document宋体": "STSong",
                "华DocumentBlack体": "STHeiti",
                "华Document楷体": "STKaiti",
                "华Document仿宋": "STFangsong",
                "幼圆": "YouYuan",
                "隶Book": "LiSu",
                "方正姚体": "FZYaoTi",
                "方正舒体": "FZShuTi",
                "思源Black体": "Source Han Sans CN",
                "思源宋体": "Source Han Serif CN",
                "苹方": "PingFang SC",
                "苹方-简": "PingFang SC",
                "冬青Black体": "Hiragino Sans GB",
                "兰亭Black": "Lantinghei SC",
                "翩翩体": "Pianpian",
                "娃娃体": "Wawati SC",
                "Line楷": "Xingkai SC",
                "圆体": "Yuanti SC",
                "华Document细Black": "STXihei",
                "华DocumentCenter宋": "STZhongsong",
                "等线": "DengXian",
                "等线 Light": "DengXian Light",
                
                # 英Document常用Font
                "Arial": "Arial",
                "Arial Black": "Arial Black",
                "Arial Narrow": "Arial Narrow",
                "Times New Roman": "Times New Roman",
                "Courier New": "Courier New",
                "Verdana": "Verdana",
                "Georgia": "Georgia",
                "Tahoma": "Tahoma",
                "Calibri": "Calibri",
                "Cambria": "Cambria",
                "Consolas": "Consolas",
                "Segoe UI": "Segoe UI",
                "Helvetica": "Helvetica",
                "Helvetica Neue": "Helvetica Neue",
                "Lucida Grande": "Lucida Grande",
                "Monaco": "Monaco",
                "Menlo": "Menlo",
                "Andale Mono": "Andale Mono",
                "Comic Sans MS": "Comic Sans MS",
                "Impact": "Impact",
                "Trebuchet MS": "Trebuchet MS",
                "Palatino": "Palatino",
                "Book Antiqua": "Book Antiqua",
                "Garamond": "Garamond",
                "Century Gothic": "Century Gothic",
                "Baskerville": "Baskerville",
                "Futura": "Futura",
                "Gill Sans": "Gill Sans",
                "Optima": "Optima",
                "Avenir": "Avenir",
                "Avenir Next": "Avenir Next",
                "San Francisco": "San Francisco",
                "SF Pro": "SF Pro",
                "SF Pro Text": "SF Pro Text",
                "SF Pro Display": "SF Pro Display",
                
                # 简化名称Mapping
                "英Document": "Arial"
            }
            
            # Create英Document到CenterDocument的Mapping
            self.en_to_cn_mapping = {}
            for cn_name, en_name in common_fonts.items():
                # IfOne个英Document名称对应Multiple个CenterDocument名称，优先UseShortest的、最Common的CenterDocument名称
                if en_name in self.en_to_cn_mapping:
                    # IfWhenPreviousCenterDocument名称比已Exists的Short，OrYesCommonFont名称，RuleReplace
                    if len(cn_name) < len(self.en_to_cn_mapping[en_name]) or cn_name in ["宋体", "Black体", "楷体", "仿宋", "微Soft雅Black"]:
                        self.en_to_cn_mapping[en_name] = cn_name
                else:
                    self.en_to_cn_mapping[en_name] = cn_name
                    
            # 将CenterDocumentFont名称Add到FontListCenter
            for cn_name, en_name in common_fonts.items():
                if cn_name not in self.system_fonts and en_name in self.system_fonts:
                    self.system_fonts.append(cn_name)
                    app_logger.debug(f"AddCenterDocumentFont名称: {cn_name}")
                elif en_name not in self.system_fonts and cn_name in self.system_fonts:
                    self.system_fonts.append(en_name)
                    app_logger.debug(f"Add英DocumentFont名称: {en_name}")
            
            # 识别CenterDocumentFont（SimpleMethod：ContainsCommonCenterDocumentFontKeyWord的Font）
            chinese_keywords = ['宋', 'Black', '楷', '仿', '微Soft', '华Document', 'SimSun', 'SimHei', 'KaiTi', 'FangSong', 'Microsoft YaHei']
            
            # Record详细Information
            app_logger.debug(f"加载SystemFontSuccess，共 {len(self.system_fonts)} 个Font")
            app_logger.debug(f"识别CenterDocumentFont {len(self.chinese_fonts)} 个")
            
            # IfFontQuantity仍然Abnormal少，Record所HasFont并AddBasicFont
            if len(self.system_fonts) < 10:
                app_logger.debug(f"SystemFontListContent: {self.system_fonts}")
                app_logger.debug(f"CenterDocumentFontListContent: {self.chinese_fonts}")
                
                # AddOne些BasicFont确保ProgramAvailable
                basic_fonts = ["Arial", "Times New Roman", "Courier New", "SimSun", "SimHei", "Microsoft YaHei", "宋体", "Black体", "微Soft雅Black"]
                for font in basic_fonts:
                    if font not in self.system_fonts:
                        self.system_fonts.append(font)
                        app_logger.debug(f"AddBasicFont: {font}")
                        
                # UpdateCenterDocumentFontList
                self.chinese_fonts = [font for font in self.system_fonts 
                                    if any(keyword in font for keyword in chinese_keywords)]
            
            return self.system_fonts
        except Exception as e:
            app_logger.error(f"加载SystemFontFailed: {str(e)}")
            import traceback
            app_logger.error(f"Abnormal详情: {traceback.format_exc()}")
            # ReturnBasicFontList作为Next备
    
    def load_font_mapping(self):
        """加载FontMappingConfiguration"""
        # 扩展的FontMappingTable（CenterDocument名称到英Document名称）
        self.font_mapping = {
            # BasicCenterDocumentFont
            "宋体": "SimSun",
            "Black体": "SimHei",
            "楷体": "KaiTi",
            "仿宋": "FangSong",
            "微Soft雅Black": "Microsoft YaHei",
            "微Soft雅Black UI": "Microsoft YaHei UI",
            "等线": "DengXian",
            "等线 Light": "DengXian Light",
            "幼圆": "YouYuan",
            "隶Book": "LiSu",
            "华Document宋体": "STSong",
            "华DocumentBlack体": "STHeiti",
            "华Document楷体": "STKaiti",
            "华Document仿宋": "STFangsong",
            
            # macOSCenterDocumentFont
            "苹方": "PingFang SC",
            "苹方-简": "PingFang SC",
            "苹方-繁": "PingFang TC",
            "宋体-简": "Songti SC",
            "宋体-繁": "Songti TC",
            "Black体-简": "Heiti SC",
            "Black体-繁": "Heiti TC",
            "楷体-简": "Kaiti SC",
            "楷体-繁": "Kaiti TC",
            "冬青Black体": "Hiragino Sans GB",
            "兰亭Black": "Lantinghei SC",
            "华Document细Black": "STXihei",
            
            # 常用英DocumentFont
            "Times New Roman": "Times New Roman",
            "Arial": "Arial",
            "Calibri": "Calibri",
            "Cambria": "Cambria",
            "Courier New": "Courier New",
            "Tahoma": "Tahoma",
            "Verdana": "Verdana",
            "Georgia": "Georgia",
            
            # 其他常用Font
            "思源Black体": "Source Han Sans CN",
            "思源宋体": "Source Han Serif CN",
            "方正Book宋": "FZShuSong",
            "方正Black体": "FZHei",
            "方正楷体": "FZKai",
            "方正仿宋": "FZFangSong",
            "阿里巴巴普惠体": "Alibaba PuHuiTi",
            "阿里巴巴方圆体": "Alimama FangYuanTi VF"
        }
        
        # Create反向Mapping（英Document名称到CenterDocument名称）
        self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}
        
        # Create英Document到CenterDocument的Mapping
        self.en_to_cn_mapping = {k: k for k in self.font_mapping.values()}
        for cn, en in self.font_mapping.items():
            if cn not in self.en_to_cn_mapping:
                self.en_to_cn_mapping[en] = cn
        
        # 尝试从ConfigurationFile加载额OuterMapping
        try:
            mapping_file = os.path.join("config", "font_mapping.json")
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    additional_mapping = json.load(f)
                    self.font_mapping.update(additional_mapping)
                    # Update反向Mapping
                    self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}
                app_logger.info(f"从ConfigurationFile加载了额Outer的FontMapping")
        except Exception as e:
            app_logger.error(f"加载FontMappingConfigurationFailed: {str(e)}")
    
    def get_font_for_document(self, font_name):
        """
        获取用于Document的Font名称，Completely尊重UserSelection的Font名称
        
        Args:
            font_name: User指定的Font名称
        
        Returns:
            str: 用于WordDocument的Font名称
        """
        # 首先CheckFontYesNo直接Available
        if self.is_font_available(font_name):
            app_logger.debug(f"Font '{font_name}' 直接Available")
            return font_name
            
        # IfFont不直接Available，CheckYesNoInMappingTableCenter
        if font_name in self.font_mapping:
            mapped_font = self.font_mapping[font_name]
            # CheckMappingNext的FontYesNoAvailable
            if self.is_font_available(mapped_font):
                app_logger.debug(f"Font '{font_name}' Mapping为 '{mapped_font}'")
                return mapped_font
        
        # If不InMappingTableCenter或MappingNext的Font不Available，直接Return原始Font名称
        # 这将Completely尊重User的Selection，即使Font不Available
        app_logger.info(f"尊重UserSelection，保留原始Font名称: '{font_name}'")
        return font_name
    
    def is_font_available(self, font_name):
        """
        CheckFontYesNoAvailable，UseCache机System提High性能
        
        Args:
            font_name: 要Check的Font名称
        
        Returns:
            bool: FontYesNoAvailable
        """
        # CheckCache
        if font_name in self.font_availability_cache:
            return self.font_availability_cache[font_name]
        
        result = False
        
        try:
            # 1. 直接CheckSystemFontList
            if font_name in self.system_fonts:
                result = True
            
            # 2. ThroughMappingCheck
            elif font_name in self.font_mapping:
                mapped_font = self.font_mapping[font_name]
                if mapped_font in self.system_fonts:
                    result = True
            
            # 3. CheckFont名称的Small写Version（不区MinuteSize写）
            elif any(font_name.lower() == system_font.lower() for system_font in self.system_fonts):
                result = True
            
            # 4. SpecialProcess常用CenterDocumentFont
            elif font_name in ['宋体', 'Black体', '楷体', '仿宋', '微Soft雅Black']:
                result = True  # 这些FontInWordCenterUsually都Available
            
            # CacheResult
            self.font_availability_cache[font_name] = result
            
        except Exception as e:
            app_logger.error(f"CheckFontAvailable性Time发生Abnormal: {font_name}, Error: {str(e)}")
            result = True  # 发生AbnormalTimeDefault认为FontAvailable
            self.font_availability_cache[font_name] = result
        
        return result
    
    def get_available_font(self, font_name, fallback="SimSun"):
        """
        获取AvailableFont，If指定Font不AvailableRuleReturnNext备Font
        
        Args:
            font_name: Font名称（可能YesCenterDocument或英Document）
            fallback: Next备Font名称
            
        Returns:
            str: Available的Font名称
        """
        # 1. 直接尝试Use原始Font名称（可能YesCenterDocument名称）
        if self.is_font_available(font_name):
            app_logger.debug(f"Font '{font_name}' 直接Available")
            return font_name
        
        # 2. IfYes常用CenterDocumentFont，尝试Use别名
        common_fonts = {
            '宋体': ['Songti SC', 'Songti TC', 'SimSun', 'STSong'],
            'Black体': ['Heiti SC', 'Heiti TC', 'SimHei', 'STHeiti'],
            '楷体': ['Kaiti SC', 'Kaiti TC', 'KaiTi', 'STKaiti'],
            '仿宋': ['Fangsong', 'STFangsong', 'FangSong'],
            '微Soft雅Black': ['Microsoft YaHei', 'Microsoft YaHei UI', 'PingFang SC', '苹方-简']
        }
        
        # CheckYesNoYes常用CenterDocumentFont
        for common_font, aliases in common_fonts.items():
            if font_name == common_font:
                # 尝试所Has别名
                for alias in aliases:
                    if self.is_font_available(alias):
                        app_logger.info(f"Font '{font_name}' Use别名 '{alias}' 替代")
                        return alias
        
        # 3. If原始Font不Available，尝试查找反向Mapping（英Document到CenterDocument）
        if font_name in self.en_to_cn_mapping:
            cn_name = self.en_to_cn_mapping[font_name]
            if self.is_font_available(cn_name):
                app_logger.debug(f"UseCenterDocumentFont名称 '{cn_name}' 替代英Document名称 '{font_name}'")
                return cn_name
        
        # 4. 尝试UseCenterDocument到英Document的Mapping
        mapped_font = self.font_mapping.get(font_name)
        if mapped_font and self.is_font_available(mapped_font):
            app_logger.debug(f"UseMapping的英DocumentFont名称 '{mapped_font}' 替代CenterDocument名称 '{font_name}'")
            return mapped_font
        
        # 5. 尝试创建QFontObject，获取实际Use的Font
        try:
            test_font = QFont(font_name)
            actual_family = test_font.family()
            
            # If实际Font族不YesDefaultFont，那么可能Yes找到了替代Font
            if actual_family != "Arial" and actual_family != "System" and actual_family != ".AppleSystemUIFont":
                app_logger.info(f"Font '{font_name}' 被QtMapping到SystemFont '{actual_family}'")
                return actual_family
        except Exception as e:
            app_logger.debug(f"TestFont '{font_name}' Time出错: {str(e)}")
        
        # 6. 确保Next备FontAvailable
        if self.is_font_available(fallback):
            app_logger.warning(f"Font '{font_name}' 不Available，UseNext备Font '{fallback}'")
            return fallback
        
        # 7. IfNext备Font也不Available，UseSystem第One个AvailableFont
        app_logger.warning(f"Font '{font_name}' 和Next备Font '{fallback}' 均不Available，UseSystemDefaultFont")
        return self.system_fonts[0] if self.system_fonts else "Arial"
    
    def get_font_display_name(self, font_name):
        """
        获取Font的Visible名称（优先ReturnBook地化Visible名称）
        
        Args:
            font_name: Font名称（可能YesSystem名称或Visible名称）
            
        Returns:
            str: Font的Visible名称，与SystemFontVolumeVisibleOne致
        """
        # 1. CheckYesNoInSystemVisible名称MappingCenter
        if font_name in self.system_to_display_mapping:
            return self.system_to_display_mapping[font_name]
        
        # 2. CheckYesNoHasSystemFont的Book地化Visible名称
        for system_name, display_name in self.system_to_display_mapping.items():
            if font_name.lower() == system_name.lower():
                return display_name
        
        # 3. If已经YesCenterDocument名称，直接Return
        for cn_name in self.font_mapping.keys():
            if font_name == cn_name:
                return font_name
        
        # 4. IfYes英Document名称，尝试从英Document到CenterDocument的MappingCenter查找
        if font_name in self.en_to_cn_mapping:
            return self.en_to_cn_mapping[font_name]
        
        # 5. IfIn反向MappingCenter找到，ReturnCenterDocument名称
        if font_name in self.reverse_mapping:
            return self.reverse_mapping[font_name]
        
        # 6. If没Has对应的Book地化名称，Return原始名称
        return font_name
    
    def get_all_fonts(self):
        """获取所HasSystemFont"""
        return self.system_fonts
    
    def get_chinese_fonts(self):
        """获取所HasCenterDocumentFont"""
        return self.chinese_fonts
    
    def get_font_mapping(self):
        """获取FontMappingTable"""
        return self.font_mapping
    
    def add_font_mapping(self, display_name, system_name):
        """
        AddNew的FontMapping
        
        Args:
            display_name: Visible名称（可以YesUserCustom的名称）
            system_name: SystemFont名称
        
        Returns:
            bool: YesNoSuccessAddMapping
        """
        # CheckSystemFontYesNoAvailable
        if not self.is_font_available(system_name):
            app_logger.warning(f"AddFontMappingFailed: SystemFont {system_name} 不Available")
            # 尝试查找替代Font
            alternative_font = self.get_available_font(system_name)
            if alternative_font != system_name:
                system_name = alternative_font
                app_logger.info(f"Use替代Font: {alternative_font}")
            else:
                return False
        
        # Add到MappingCenter
        self.font_mapping[display_name] = system_name
        self.reverse_mapping[system_name] = display_name
        
        # 同TimeAdd到SystemVisible名称Mapping
        self.system_to_display_mapping[system_name] = display_name
        
        # Save到ConfigurationFile
        try:
            # Ensure config directory exists
            os.makedirs("config", exist_ok=True)
            
            mapping_file = os.path.join("config", "font_mapping.json")
            
            # 读取现HasMappingFile（IfExists）
            existing_mapping = {}
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        existing_mapping = json.load(f)
                except Exception as e:
                    app_logger.warning(f"读取现HasFontMappingFileFailed: {str(e)}")
            
            # 只Add或更NewOne个Mapping，而不Yes覆盖EntireFile
            existing_mapping[display_name] = system_name
            
            # Save更NewNext的Mapping
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(existing_mapping, f, ensure_ascii=False, indent=4)
            
            app_logger.info(f"AddFontMapping: {display_name} -> {system_name}")
            return True
        except Exception as e:
            app_logger.error(f"保存FontMappingFailed: {str(e)}")
            return False
