# -*- coding: utf-8 -*-
"""
字体管理模块
负责获取系统字体、验证字体可用性和提供字体映射功能。
"""

import json
import os
import platform
import subprocess

try:
    from PyQt6.QtGui import QFont, QFontDatabase
    PYQT_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    QFont = None
    QFontDatabase = None
    PYQT_AVAILABLE = False

from ..utils.logger import app_logger


class FontManager:
    """字体管理器，负责获取和验证系统字体"""

    _instance = None

    _SYSTEM_TO_DISPLAY_MAPPING = {
        # macOS
        "PingFang SC": "苹方",
        "PingFang TC": "苹方",
        "Songti SC": "宋体",
        "Songti TC": "宋体",
        "Heiti SC": "黑体",
        "Heiti TC": "黑体",
        "Kaiti SC": "楷体",
        "Kaiti TC": "楷体",
        "Yuanti SC": "圆体",
        "Yuanti TC": "圆体",
        "STSong": "华文宋体",
        "STHeiti": "华文黑体",
        "STKaiti": "华文楷体",
        "STFangsong": "华文仿宋",
        "Hiragino Sans GB": "冬青黑体",
        "Lantinghei SC": "兰亭黑",
        "Wawati SC": "娃娃体",
        "Xingkai SC": "行楷",
        "Baoli SC": "报隆体",
        "Libian SC": "隶变体",
        "Weibei SC": "魏碧体",
        "Yuppy SC": "雅痛体",
        "Yuppy TC": "雅痛体",
        # Windows
        "SimSun": "宋体",
        "SimHei": "黑体",
        "KaiTi": "楷体",
        "FangSong": "仿宋",
        "Microsoft YaHei": "微软雅黑",
        "Microsoft YaHei UI": "微软雅黑",
        "YouYuan": "幼圆",
        "LiSu": "隶书",
        "FZYaoTi": "方正姚体",
        "FZShuTi": "方正舒体",
        "DengXian": "等线",
        "DengXian Light": "等线 Light",
        # Common Latin
        "Arial": "Arial",
        "Times New Roman": "Times New Roman",
        "Courier New": "Courier New",
        "Verdana": "Verdana",
        "Tahoma": "Tahoma",
        "Calibri": "Calibri",
        "Helvetica": "Helvetica",
        "Helvetica Neue": "Helvetica Neue",
    }

    _COMMON_FONT_ALIASES = {
        "宋体": "SimSun",
        "黑体": "SimHei",
        "楷体": "KaiTi",
        "仿宋": "FangSong",
        "微软雅黑": "Microsoft YaHei",
        "微软雅黑 UI": "Microsoft YaHei UI",
        "华文宋体": "STSong",
        "华文黑体": "STHeiti",
        "华文楷体": "STKaiti",
        "华文仿宋": "STFangsong",
        "幼圆": "YouYuan",
        "隶书": "LiSu",
        "方正姚体": "FZYaoTi",
        "方正舒体": "FZShuTi",
        "思源黑体": "Source Han Sans CN",
        "思源宋体": "Source Han Serif CN",
        "苹方": "PingFang SC",
        "苹方-简": "PingFang SC",
        "冬青黑体": "Hiragino Sans GB",
        "兰亭黑": "Lantinghei SC",
        "翩翩体": "Pianpian",
        "娃娃体": "Wawati SC",
        "行楷": "Xingkai SC",
        "圆体": "Yuanti SC",
        "华文细黑": "STXihei",
        "华文中宋": "STZhongsong",
        "等线": "DengXian",
        "等线 Light": "DengXian Light",
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
        "英文": "Arial",
    }

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化字体管理器"""
        if self._initialized:
            return

        self._initialized = True
        self.system_fonts = []
        self.chinese_fonts = []
        self.font_mapping = {}
        self.reverse_mapping = {}
        self.display_name_mapping = {}
        self.system_to_display_mapping = {}
        self.display_to_system_mapping = {}
        self.font_availability_cache = {}
        self.en_to_cn_mapping = {}
        self._pyqt_font_probe_enabled = PYQT_AVAILABLE and (
            os.getenv("FORMULAAI_ENABLE_PYQT_FONTS", "").strip().lower() in {"1", "true", "yes", "on"}
        )

        self.load_system_fonts()
        self.load_font_mapping()

        app_logger.info(
            f"字体管理器初始化完成，共加载 {len(self.system_fonts)} 个系统字体，"
            f"pyqt_probe={'on' if self._pyqt_font_probe_enabled else 'off'}"
        )

    def _infer_display_name(self, font_name):
        """根据英文系统字体名称推断中文显示名称。"""
        if "Song" in font_name or "SimSun" in font_name:
            return "宋体"
        if "Hei" in font_name or "SimHei" in font_name:
            return "黑体"
        if "Kai" in font_name or "KaiTi" in font_name:
            return "楷体"
        if "Fang" in font_name or "FangSong" in font_name:
            return "仿宋"
        if "Yuan" in font_name:
            return "圆体"
        if "Ming" in font_name:
            return "明体"
        return None

    def _discover_fonts_via_system_tools(self):
        """使用系统命令发现字体，避免依赖GUI运行时。"""
        fonts = []
        system = platform.system()
        app_logger.debug(f"当前操作系统: {system}")

        if system in {"Linux", "Darwin"}:
            try:
                result = subprocess.run(
                    ["fc-list", ":", "family"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        for font in line.split(","):
                            name = font.strip()
                            if name and name not in fonts:
                                fonts.append(name)
            except Exception as e:
                app_logger.debug(f"fc-list获取字体失败: {str(e)}")

        if system == "Darwin":
            try:
                result = subprocess.run(
                    ["system_profiler", "SPFontsDataType"],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    check=False,
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "Full Name:" in line:
                            name = line.split("Full Name:")[1].strip()
                            if name and name not in fonts:
                                fonts.append(name)
            except Exception as e:
                app_logger.debug(f"system_profiler获取字体失败: {str(e)}")

        return fonts

    def _discover_fonts_via_pyqt(self):
        """可选：使用PyQt字体数据库进行补充探测。"""
        if not PYQT_AVAILABLE or QFontDatabase is None:
            return []
        try:
            return [f for f in QFontDatabase.families() if f and not f.startswith("@")]
        except Exception as e:
            app_logger.debug(f"QFontDatabase探测失败: {str(e)}")
            return []

    def load_system_fonts(self):
        """加载系统所有可用字体"""
        try:
            self.system_fonts = []
            self.chinese_fonts = []
            self.system_to_display_mapping = dict(self._SYSTEM_TO_DISPLAY_MAPPING)
            self.display_to_system_mapping = {
                display_name: system_name
                for system_name, display_name in self.system_to_display_mapping.items()
            }

            discovered_fonts = self._discover_fonts_via_system_tools()
            app_logger.debug(f"系统命令发现字体数量: {len(discovered_fonts)}")

            # 默认不开启Qt字体探测，避免在headless场景触发Qt abort
            if self._pyqt_font_probe_enabled:
                for font in self._discover_fonts_via_pyqt():
                    if font not in discovered_fonts:
                        discovered_fonts.append(font)
                app_logger.debug(f"启用PyQt补充字体探测，合并后数量: {len(discovered_fonts)}")
            elif PYQT_AVAILABLE:
                app_logger.debug("检测到PyQt6，但未启用QFontDatabase探测（FORMULAAI_ENABLE_PYQT_FONTS!=1）")

            self.system_fonts = [font for font in discovered_fonts if font and not font.startswith("@")]

            for font_name in self.system_fonts:
                if any(0x4E00 <= ord(char) <= 0x9FFF for char in font_name):
                    if font_name not in self.chinese_fonts:
                        self.chinese_fonts.append(font_name)

                if font_name not in self.system_to_display_mapping:
                    inferred_name = self._infer_display_name(font_name)
                    if inferred_name:
                        self.system_to_display_mapping[font_name] = inferred_name
                        self.display_to_system_mapping[inferred_name] = font_name
                        if inferred_name not in self.chinese_fonts:
                            self.chinese_fonts.append(inferred_name)

            self.en_to_cn_mapping = {}
            for cn_name, en_name in self._COMMON_FONT_ALIASES.items():
                if en_name in self.en_to_cn_mapping:
                    if len(cn_name) < len(self.en_to_cn_mapping[en_name]) or cn_name in {"宋体", "黑体", "楷体", "仿宋", "微软雅黑"}:
                        self.en_to_cn_mapping[en_name] = cn_name
                else:
                    self.en_to_cn_mapping[en_name] = cn_name

                if cn_name not in self.system_fonts and en_name in self.system_fonts:
                    self.system_fonts.append(cn_name)
                elif en_name not in self.system_fonts and cn_name in self.system_fonts:
                    self.system_fonts.append(en_name)

            if len(self.system_fonts) < 10:
                for font in [
                    "Arial", "Times New Roman", "Courier New",
                    "SimSun", "SimHei", "Microsoft YaHei",
                    "宋体", "黑体", "微软雅黑",
                ]:
                    if font not in self.system_fonts:
                        self.system_fonts.append(font)

            chinese_keywords = [
                "宋", "黑", "楷", "仿", "微软", "华文",
                "SimSun", "SimHei", "KaiTi", "FangSong", "Microsoft YaHei",
            ]
            for font in self.system_fonts:
                if any(keyword in font for keyword in chinese_keywords) and font not in self.chinese_fonts:
                    self.chinese_fonts.append(font)

            app_logger.debug(f"加载系统字体成功，共 {len(self.system_fonts)} 个字体")
            app_logger.debug(f"识别中文字体 {len(self.chinese_fonts)} 个")
            return self.system_fonts
        except Exception as e:
            app_logger.error(f"加载系统字体失败: {str(e)}")
            fallback_fonts = [
                "Arial", "Times New Roman", "Courier New",
                "SimSun", "SimHei", "Microsoft YaHei",
                "宋体", "黑体", "微软雅黑",
            ]
            self.system_fonts = fallback_fonts[:]
            self.chinese_fonts = [f for f in fallback_fonts if any(k in f for k in ["宋", "黑", "微", "Sim", "YaHei"])]
            return self.system_fonts

    def load_font_mapping(self):
        """加载字体映射配置"""
        self.font_mapping = {
            "宋体": "SimSun",
            "黑体": "SimHei",
            "楷体": "KaiTi",
            "仿宋": "FangSong",
            "微软雅黑": "Microsoft YaHei",
            "微软雅黑 UI": "Microsoft YaHei UI",
            "等线": "DengXian",
            "等线 Light": "DengXian Light",
            "幼圆": "YouYuan",
            "隶书": "LiSu",
            "华文宋体": "STSong",
            "华文黑体": "STHeiti",
            "华文楷体": "STKaiti",
            "华文仿宋": "STFangsong",
            "苹方": "PingFang SC",
            "苹方-简": "PingFang SC",
            "苹方-繁": "PingFang TC",
            "宋体-简": "Songti SC",
            "宋体-繁": "Songti TC",
            "黑体-简": "Heiti SC",
            "黑体-繁": "Heiti TC",
            "楷体-简": "Kaiti SC",
            "楷体-繁": "Kaiti TC",
            "冬青黑体": "Hiragino Sans GB",
            "兰亭黑": "Lantinghei SC",
            "华文细黑": "STXihei",
            "Times New Roman": "Times New Roman",
            "Arial": "Arial",
            "Calibri": "Calibri",
            "Cambria": "Cambria",
            "Courier New": "Courier New",
            "Tahoma": "Tahoma",
            "Verdana": "Verdana",
            "Georgia": "Georgia",
            "思源黑体": "Source Han Sans CN",
            "思源宋体": "Source Han Serif CN",
            "方正书宋": "FZShuSong",
            "方正黑体": "FZHei",
            "方正楷体": "FZKai",
            "方正仿宋": "FZFangSong",
            "阿里巴巴普惠体": "Alibaba PuHuiTi",
            "阿里巴巴方圆体": "Alimama FangYuanTi VF",
        }

        self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}

        for cn_name, en_name in self.font_mapping.items():
            if en_name not in self.en_to_cn_mapping:
                self.en_to_cn_mapping[en_name] = cn_name

        try:
            mapping_file = os.path.join("config", "font_mapping.json")
            if os.path.exists(mapping_file):
                with open(mapping_file, "r", encoding="utf-8") as f:
                    additional_mapping = json.load(f)
                self.font_mapping.update(additional_mapping)
                self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}
                app_logger.info("从配置文件加载了额外的字体映射")
        except Exception as e:
            app_logger.error(f"加载字体映射配置失败: {str(e)}")

    def get_font_for_document(self, font_name):
        """
        获取用于文档的字体名称，完全尊重用户选择的字体名称
        """
        if self.is_font_available(font_name):
            app_logger.debug(f"字体 '{font_name}' 直接可用")
            return font_name

        if font_name in self.font_mapping:
            mapped_font = self.font_mapping[font_name]
            if self.is_font_available(mapped_font):
                app_logger.debug(f"字体 '{font_name}' 映射为 '{mapped_font}'")
                return mapped_font

        app_logger.info(f"尊重用户选择，保留原始字体名称: '{font_name}'")
        return font_name

    def is_font_available(self, font_name):
        """
        检查字体是否可用，使用缓存机制提高性能
        """
        if font_name in self.font_availability_cache:
            return self.font_availability_cache[font_name]

        result = False
        try:
            if font_name in self.system_fonts:
                result = True
            elif font_name in self.font_mapping and self.font_mapping[font_name] in self.system_fonts:
                result = True
            elif any(font_name.lower() == system_font.lower() for system_font in self.system_fonts):
                result = True
            elif font_name in ["宋体", "黑体", "楷体", "仿宋", "微软雅黑"]:
                result = True

            self.font_availability_cache[font_name] = result
        except Exception as e:
            app_logger.error(f"检查字体可用性时发生异常: {font_name}, 错误: {str(e)}")
            self.font_availability_cache[font_name] = True
            return True

        return result

    def get_available_font(self, font_name, fallback="SimSun"):
        """
        获取可用字体，如果指定字体不可用则返回后备字体
        """
        if self.is_font_available(font_name):
            app_logger.debug(f"字体 '{font_name}' 直接可用")
            return font_name

        common_fonts = {
            "宋体": ["Songti SC", "Songti TC", "SimSun", "STSong"],
            "黑体": ["Heiti SC", "Heiti TC", "SimHei", "STHeiti"],
            "楷体": ["Kaiti SC", "Kaiti TC", "KaiTi", "STKaiti"],
            "仿宋": ["Fangsong", "STFangsong", "FangSong"],
            "微软雅黑": ["Microsoft YaHei", "Microsoft YaHei UI", "PingFang SC", "苹方-简"],
        }

        for common_font, aliases in common_fonts.items():
            if font_name == common_font:
                for alias in aliases:
                    if self.is_font_available(alias):
                        app_logger.info(f"字体 '{font_name}' 使用别名 '{alias}' 替代")
                        return alias

        if font_name in self.en_to_cn_mapping:
            cn_name = self.en_to_cn_mapping[font_name]
            if self.is_font_available(cn_name):
                app_logger.debug(f"使用中文字体名称 '{cn_name}' 替代英文名称 '{font_name}'")
                return cn_name

        mapped_font = self.font_mapping.get(font_name)
        if mapped_font and self.is_font_available(mapped_font):
            app_logger.debug(f"使用映射的英文字体名称 '{mapped_font}' 替代中文名称 '{font_name}'")
            return mapped_font

        if self._pyqt_font_probe_enabled and QFont is not None:
            try:
                test_font = QFont(font_name)
                actual_family = test_font.family()
                if actual_family not in {"Arial", "System", ".AppleSystemUIFont"}:
                    app_logger.info(f"字体 '{font_name}' 被Qt映射到系统字体 '{actual_family}'")
                    return actual_family
            except Exception as e:
                app_logger.debug(f"测试字体 '{font_name}' 时出错: {str(e)}")

        if self.is_font_available(fallback):
            app_logger.warning(f"字体 '{font_name}' 不可用，使用后备字体 '{fallback}'")
            return fallback

        app_logger.warning(f"字体 '{font_name}' 和后备字体 '{fallback}' 均不可用，使用系统默认字体")
        return self.system_fonts[0] if self.system_fonts else "Arial"

    def get_font_display_name(self, font_name):
        """
        获取字体的显示名称（优先返回本地化显示名称）
        """
        if font_name in self.system_to_display_mapping:
            return self.system_to_display_mapping[font_name]

        for system_name, display_name in self.system_to_display_mapping.items():
            if font_name.lower() == system_name.lower():
                return display_name

        if font_name in self.font_mapping:
            return font_name

        if font_name in self.en_to_cn_mapping:
            return self.en_to_cn_mapping[font_name]

        if font_name in self.reverse_mapping:
            return self.reverse_mapping[font_name]

        return font_name

    def get_all_fonts(self):
        """获取所有系统字体"""
        return self.system_fonts

    def get_chinese_fonts(self):
        """获取所有中文字体"""
        return self.chinese_fonts

    def get_font_mapping(self):
        """获取字体映射表"""
        return self.font_mapping

    def add_font_mapping(self, display_name, system_name):
        """
        添加新的字体映射
        """
        if not self.is_font_available(system_name):
            app_logger.warning(f"添加字体映射失败: 系统字体 {system_name} 不可用")
            alternative_font = self.get_available_font(system_name)
            if alternative_font != system_name:
                system_name = alternative_font
                app_logger.info(f"使用替代字体: {alternative_font}")
            else:
                return False

        self.font_mapping[display_name] = system_name
        self.reverse_mapping[system_name] = display_name
        self.system_to_display_mapping[system_name] = display_name

        try:
            os.makedirs("config", exist_ok=True)
            mapping_file = os.path.join("config", "font_mapping.json")
            existing_mapping = {}
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, "r", encoding="utf-8") as f:
                        existing_mapping = json.load(f)
                except Exception as e:
                    app_logger.warning(f"读取现有字体映射文件失败: {str(e)}")

            existing_mapping[display_name] = system_name
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(existing_mapping, f, ensure_ascii=False, indent=4)

            app_logger.info(f"添加字体映射: {display_name} -> {system_name}")
            return True
        except Exception as e:
            app_logger.error(f"保存字体映射失败: {str(e)}")
            return False
