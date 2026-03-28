#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FormulaAI Web - AI智能文档排版工具 (Web版)

基于Streamlit构建的Web GUI，复用核心模块。
支持：文档排版、模板管理、页眉页脚配置、API配置持久化
"""

import streamlit as st
import tempfile
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from src.core.ai_connector import AIConnector
from src.core.format_manager import FormatManager
from src.core.doc_processor import DocProcessor
from src.core.structure_analyzer import StructureAnalyzer
from src.core.header_footer_config import HeaderFooterConfig
from src.core.text_template_parser import TextTemplateParser
from src.utils.config_manager import ConfigManager
from src.utils.logger import app_logger


# ========================
# 页面配置
# ========================
st.set_page_config(
    page_title="FormulaAI Web",
    page_icon="/static/icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# 样式设置
# ========================
st.markdown("""
<style>
    /* 主色调 */
    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --bg-color: #f8fafc;
        --card-bg: #ffffff;
        --border-color: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }

    /* 隐藏默认页眉 */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* 主容器样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 页面标题 */
    .main-header {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--primary-color);
    }

    /* 卡片样式 */
    .card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* 按钮美化 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .stButton>button[kind="primary"] {
        background: var(--primary-color);
        border-color: var(--primary-color);
    }

    .stButton>button[kind="primary"]:hover {
        background: var(--primary-hover);
        border-color: var(--primary-hover);
    }

    /* 输入框美化 */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border-color: var(--border-color);
    }

    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }

    /* 选择框美化 */
    .stSelectbox>div>div>select {
        border-radius: 8px;
    }

    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        border-right: 1px solid #dbe3f0;
    }

    section[data-testid="stSidebar"] .stRadio>label {
        color: #0f172a;
        font-weight: 600;
        font-size: 0.875rem;
    }

    section[data-testid="stSidebar"] .stRadio>div {
        gap: 0.25rem;
    }

    section[data-testid="stSidebar"] .stRadio>div>label {
        color: #334155;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.125rem 0;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    section[data-testid="stSidebar"] .stRadio>div>label:hover {
        background: rgba(37, 99, 235, 0.08);
        color: #0f172a;
    }

    section[data-testid="stSidebar"] .stRadio>div>label[data-checked="true"] {
        background: var(--primary-color);
        color: #ffffff;
    }

    section[data-testid="stSidebar"] .stRadio>div>label[data-checked="true"]:hover {
        background: var(--primary-hover);
    }

    /* 侧边栏标题 */
    section[data-testid="stSidebar"] h1 {
        color: #0f172a;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: #475569;
        font-size: 0.875rem;
    }

    /* 分隔线 */
    section[data-testid="stSidebar"] hr {
        background: rgba(148,163,184,0.35);
        margin: 1rem 0;
    }

    /* 成功/警告/错误提示美化 */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #6ee7b7;
        border-radius: 8px;
        color: #065f46;
    }

    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fcd34d;
        border-radius: 8px;
        color: #92400e;
    }

    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #fca5a5;
        border-radius: 8px;
        color: #991b1b;
    }

    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #93c5fd;
        border-radius: 8px;
        color: #1e40af;
    }

    /* 文件上传区域美化 */
    .stFileUploader {
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.2s ease;
    }

    .stFileUploader:hover {
        border-color: var(--primary-color);
        background: rgba(37, 99, 235, 0.02);
    }

    /* Expander美化 */
    .streamlit-expanderHeader {
        background: var(--bg-color);
        border-radius: 8px;
        font-weight: 500;
    }

    /* 表格样式 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* 进度条美化 */
    .stProgress > div > div > div {
        background: var(--primary-color);
    }

    /* 下载按钮特殊样式 */
    .stDownloadButton>button {
        background: var(--success-color);
        border-color: var(--success-color);
    }

    .stDownloadButton>button:hover {
        background: #047857;
        border-color: #047857;
    }

    /* 副标题样式 */
    h3 {
        color: var(--text-primary);
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* 链接样式 */
    a {
        color: var(--primary-color);
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    /* 模板卡片 */
    .template-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }

    .template-card:hover {
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }

    /* JSON显示美化 */
    .stJson {
        border-radius: 8px;
        background: var(--bg-color);
        padding: 1rem;
    }

    /* 状态指示器 */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-ok {
        background: #d1fae5;
        color: #065f46;
    }

    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }

    /* 页脚样式 */
    .footer {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }

    /* 响应式优化 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.5rem;
        }
        .card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ========================
# 会话状态初始化
# ========================
def init_session_state():
    """初始化会话状态"""
    if 'language' not in st.session_state:
        st.session_state.language = "zh"

    # API配置
    if 'api_url' not in st.session_state:
        st.session_state.api_url = ""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'model' not in st.session_state:
        st.session_state.model = "deepseek-chat"

    # 文档处理
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'output_bytes' not in st.session_state:
        st.session_state.output_bytes = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []

    # 模板管理
    if 'editing_template' not in st.session_state:
        st.session_state.editing_template = None
    if 'new_template_mode' not in st.session_state:
        st.session_state.new_template_mode = False

    # 页眉页脚配置
    if 'header_footer_config' not in st.session_state:
        st.session_state.header_footer_config = HeaderFooterConfig().to_dict()


init_session_state()

# 加载持久化配置
config_manager = ConfigManager()


# ========================
# 辅助函数
# ========================
TRANSLATIONS = {
    "zh": {
        "language_selector": "Language / 语言",
        "language_option_zh": "中文",
        "language_option_en": "English",
        "sidebar_tagline": "AI智能文档排版工具",
        "sidebar_status_ready": "API已配置",
        "sidebar_status_missing": "API未配置",
        "page_document_format": "文档排版",
        "page_template_management": "模板管理",
        "page_api_config": "API配置",
        "page_text_parsing": "从文本解析",
        "page_help": "帮助",
        "api_required": "请先在「API配置」页面设置API参数",
        "upload_document": "上传文档",
        "select_docx": "选择Word文档",
        "select_docx_help": "支持.docx格式的Word文档",
        "selected_file": "已选择: {name} ({size_kb:.1f} KB)",
        "template_selection": "模板选择",
        "select_template": "选择排版模板",
        "template_preview": "模板预览",
        "no_templates": "没有可用的模板，请先创建模板",
        "header_footer_settings": "页眉页脚设置（可选）",
        "enable_header": "启用页眉",
        "header_content": "页眉内容",
        "enable_footer": "启用页脚",
        "footer_content": "页脚内容",
        "start_formatting": "开始排版",
        "clear": "清除",
        "download_result": "下载结果",
        "processing_spinner": "正在处理...",
        "processing_document_status": "正在处理文档...",
        "processing_failed": "处理失败: {error}",
        "formatting_complete": "排版完成！点击上方按钮下载结果。",
        "processing_logs": "处理日志",
        "ai_parsing_spinner": "AI正在解析...",
        "log_start_processing": "开始处理文档...",
        "log_temp_created": "临时文件已创建: {path}",
        "log_doc_read": "文档读取成功，共 {count} 个段落",
        "log_template_loaded": "已加载模板: {name}",
        "log_calling_ai": "正在调用AI API...",
        "log_ai_received": "AI响应已接收",
        "log_generated_instructions": "排版指令已生成，共 {count} 个元素",
        "log_format_complete": "文档排版完成！",
        "error_doc_read_failed": "文档读取失败",
        "error_template_not_found": "模板 '{name}' 不存在",
        "error_invalid_api_config": "API配置无效: {message}",
        "error_ai_request_failed": "AI请求失败: {message}",
        "error_parse_response_failed": "解析响应失败: {message}",
        "error_invalid_header_footer": "页眉页脚配置无效: {message}",
        "error_formatting_failed": "应用排版格式失败",
        "error_output_not_found": "未找到输出文件",
        "template_management_title": "模板管理",
        "new_template": "新建模板",
        "refresh_list": "刷新列表",
        "no_template_yet": "暂无模板，请点击「新建模板」创建",
        "edit": "编辑",
        "delete": "删除",
        "deleted_template": "已删除模板: {name}",
        "delete_failed": "删除失败",
        "view_rules": "查看规则",
        "create_template_title": "新建模板",
        "edit_template_title": "编辑模板: {name}",
        "template_name": "模板名称",
        "template_description": "模板描述",
        "format_rules": "格式规则",
        "add_new_rule": "添加新规则",
        "element_type": "元素类型",
        "font": "字体",
        "font_size": "字号",
        "alignment": "对齐",
        "bold": "粗体",
        "add_rule": "添加规则",
        "current_rules": "当前规则:",
        "save_template": "保存模板",
        "cancel": "取消",
        "enter_template_name": "请输入模板名称",
        "add_rule_required": "请至少添加一条规则",
        "template_saved": "模板已保存: {name}",
        "save_failed": "保存失败",
        "api_config_info": "配置AI API参数，用于文档智能排版",
        "api_url_label": "API地址",
        "api_url_help": "API基础地址，如: https://api.deepseek.com 或 https://api.openai.com",
        "api_url_placeholder": "https://api.deepseek.com",
        "api_key_label": "API密钥",
        "api_key_help": "您的API密钥",
        "api_key_placeholder": "sk-xxxxxxxxxxxxxxxx",
        "model_selection_mode": "模型选择方式",
        "preset_model": "选择预设模型",
        "custom_model": "输入自定义模型",
        "model_label": "模型",
        "custom_model_name": "自定义模型名称",
        "custom_model_placeholder": "model-name",
        "save_config": "保存配置",
        "config_saved": "配置已保存",
        "test_connection": "测试连接",
        "fill_api_url_key": "请填写API URL和Key",
        "testing": "测试中...",
        "connection_success": "连接成功！模型: {model}",
        "connection_failed": "连接失败: {message}",
        "test_failed": "测试失败: {error}",
        "current_config": "当前配置",
        "not_set": "(未设置)",
        "unknown": "(未知)",
        "no_saved_config": "暂无保存的配置",
        "text_parsing_info": "输入自然语言描述的格式要求，AI将自动生成排版模板",
        "template_name_placeholder": "例如：学术论文模板",
        "template_desc_placeholder": "例如：适用于学术论文排版",
        "format_desc_label": "格式要求描述",
        "format_desc_placeholder": "请输入格式要求，例如：\n标题使用黑体小二号字，居中对齐\n正文使用宋体小四号字，左对齐，行距1.5倍\n一级标题使用黑体三号字，左对齐",
        "generate_template": "AI解析生成模板",
        "enter_format_desc": "请输入格式要求描述",
        "parse_failed": "解析失败: {message}",
        "invalid_template_format": "模板格式无效: {message}",
        "template_created": "模板已创建: {name}",
        "help_markdown": """
## FormulaAI Web - AI智能文档排版工具

### 功能介绍

FormulaAI 是一款基于AI的智能文档排版工具，能够自动识别文档结构并应用专业排版格式。

### 使用步骤

1. **配置API**
   - 在「API配置」页面设置您的AI API参数
   - 支持DeepSeek、OpenAI等兼容API
   - 点击「测试连接」验证配置

2. **管理模板**
   - 在「模板管理」页面创建或编辑排版模板
   - 定义各类文档元素（标题、正文等）的格式规则

3. **排版文档**
   - 在「文档排版」页面上传Word文档
   - 选择排版模板
   - 点击「开始排版」
   - 下载排版后的文档

4. **智能解析**
   - 在「从文本解析」页面输入自然语言描述
   - AI自动生成排版模板

### 支持的API

- **DeepSeek**: `https://api.deepseek.com`
- **OpenAI**: `https://api.openai.com`
- **其他兼容API**: 输入对应的Base URL
""",
    },
    "en": {
        "language_selector": "Language / 语言",
        "language_option_zh": "中文",
        "language_option_en": "English",
        "sidebar_tagline": "AI document formatting",
        "sidebar_status_ready": "API configured",
        "sidebar_status_missing": "API not configured",
        "page_document_format": "Document Formatting",
        "page_template_management": "Template Manager",
        "page_api_config": "API Settings",
        "page_text_parsing": "Parse from Text",
        "page_help": "Help",
        "api_required": "Please configure the API in \"API Settings\" first.",
        "upload_document": "Upload Document",
        "select_docx": "Select Word document",
        "select_docx_help": "Supports .docx Word files",
        "selected_file": "Selected: {name} ({size_kb:.1f} KB)",
        "template_selection": "Template",
        "select_template": "Choose a formatting template",
        "template_preview": "Template Preview",
        "no_templates": "No templates available. Please create one first.",
        "header_footer_settings": "Header & Footer (Optional)",
        "enable_header": "Enable header",
        "header_content": "Header content",
        "enable_footer": "Enable footer",
        "footer_content": "Footer content",
        "start_formatting": "Start Formatting",
        "clear": "Clear",
        "download_result": "Download Result",
        "processing_spinner": "Processing...",
        "processing_document_status": "Processing document...",
        "processing_failed": "Processing failed: {error}",
        "formatting_complete": "Formatting finished. Use the button above to download the result.",
        "processing_logs": "Processing Logs",
        "ai_parsing_spinner": "AI is parsing...",
        "log_start_processing": "Started processing document...",
        "log_temp_created": "Temporary file created: {path}",
        "log_doc_read": "Document loaded successfully with {count} paragraphs",
        "log_template_loaded": "Loaded template: {name}",
        "log_calling_ai": "Calling AI API...",
        "log_ai_received": "AI response received",
        "log_generated_instructions": "Generated formatting instructions for {count} elements",
        "log_format_complete": "Document formatting completed",
        "error_doc_read_failed": "Failed to read the document",
        "error_template_not_found": "Template '{name}' does not exist",
        "error_invalid_api_config": "Invalid API configuration: {message}",
        "error_ai_request_failed": "AI request failed: {message}",
        "error_parse_response_failed": "Failed to parse response: {message}",
        "error_invalid_header_footer": "Invalid header/footer configuration: {message}",
        "error_formatting_failed": "Failed to apply formatting",
        "error_output_not_found": "Output file not found",
        "template_management_title": "Template Manager",
        "new_template": "New Template",
        "refresh_list": "Refresh",
        "no_template_yet": "No templates yet. Click \"New Template\" to create one.",
        "edit": "Edit",
        "delete": "Delete",
        "deleted_template": "Deleted template: {name}",
        "delete_failed": "Delete failed",
        "view_rules": "View Rules",
        "create_template_title": "New Template",
        "edit_template_title": "Edit Template: {name}",
        "template_name": "Template name",
        "template_description": "Template description",
        "format_rules": "Formatting Rules",
        "add_new_rule": "Add Rule",
        "element_type": "Element type",
        "font": "Font",
        "font_size": "Font size",
        "alignment": "Alignment",
        "bold": "Bold",
        "add_rule": "Add Rule",
        "current_rules": "Current rules:",
        "save_template": "Save Template",
        "cancel": "Cancel",
        "enter_template_name": "Please enter a template name.",
        "add_rule_required": "Please add at least one rule.",
        "template_saved": "Template saved: {name}",
        "save_failed": "Save failed",
        "api_config_info": "Configure AI API settings for smart document formatting.",
        "api_url_label": "API URL",
        "api_url_help": "Base API URL, for example: https://api.deepseek.com or https://api.openai.com",
        "api_url_placeholder": "https://api.deepseek.com",
        "api_key_label": "API Key",
        "api_key_help": "Your API key",
        "api_key_placeholder": "sk-xxxxxxxxxxxxxxxx",
        "model_selection_mode": "Model selection",
        "preset_model": "Choose preset model",
        "custom_model": "Enter custom model",
        "model_label": "Model",
        "custom_model_name": "Custom model name",
        "custom_model_placeholder": "model-name",
        "save_config": "Save Settings",
        "config_saved": "Settings saved",
        "test_connection": "Test Connection",
        "fill_api_url_key": "Please fill in API URL and API Key.",
        "testing": "Testing...",
        "connection_success": "Connection succeeded. Model: {model}",
        "connection_failed": "Connection failed: {message}",
        "test_failed": "Test failed: {error}",
        "current_config": "Current Settings",
        "not_set": "(Not set)",
        "unknown": "(Unknown)",
        "no_saved_config": "No saved settings.",
        "text_parsing_info": "Describe formatting rules in natural language and AI will generate a template.",
        "template_name_placeholder": "e.g. Academic Paper Template",
        "template_desc_placeholder": "e.g. Suitable for academic papers",
        "format_desc_label": "Formatting description",
        "format_desc_placeholder": "Describe the rules, for example:\nUse bold HeiTi small-size-2 for the title and center it.\nUse SongTi size small-4 for body text, left aligned, 1.5 line spacing.\nUse HeiTi size 3 for level-1 headings, left aligned.",
        "generate_template": "Generate Template with AI",
        "enter_format_desc": "Please enter a formatting description.",
        "parse_failed": "Parsing failed: {message}",
        "invalid_template_format": "Invalid template format: {message}",
        "template_created": "Template created: {name}",
        "help_markdown": """
## FormulaAI Web - AI Document Formatting Tool

### Overview

FormulaAI is an AI-powered document formatting tool that detects document structure and applies professional formatting rules automatically.

### Workflow

1. **Configure API**
   - Set API parameters on the \"API Settings\" page
   - Supports DeepSeek, OpenAI, and compatible APIs
   - Use \"Test Connection\" to verify the configuration

2. **Manage Templates**
   - Create or edit templates on the \"Template Manager\" page
   - Define formatting rules for titles, body text, and more

3. **Format Documents**
   - Upload a Word document on the \"Document Formatting\" page
   - Choose a formatting template
   - Click \"Start Formatting\"
   - Download the result

4. **Parse from Text**
   - Describe formatting rules in natural language
   - Let AI generate a reusable template

### Supported APIs

- **DeepSeek**: `https://api.deepseek.com`
- **OpenAI**: `https://api.openai.com`
- **Other compatible APIs**: use the corresponding base URL
""",
    },
}

ELEMENT_TYPE_LABELS = {
    "标题": {"zh": "标题", "en": "Title"},
    "一级标题": {"zh": "一级标题", "en": "Heading 1"},
    "二级标题": {"zh": "二级标题", "en": "Heading 2"},
    "三级标题": {"zh": "三级标题", "en": "Heading 3"},
    "正文": {"zh": "正文", "en": "Body"},
    "摘要": {"zh": "摘要", "en": "Abstract"},
    "关键词": {"zh": "关键词", "en": "Keywords"},
    "参考文献": {"zh": "参考文献", "en": "References"},
}


def add_log(message: str, level: str = "INFO"):
    """添加日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] [{level}] {message}")


def t(key: str, **kwargs):
    """获取当前语言的界面文案。"""
    language = st.session_state.get("language", "zh")
    text = TRANSLATIONS.get(language, TRANSLATIONS["zh"]).get(key, key)
    return text.format(**kwargs) if kwargs else text


def element_type_label(value: str) -> str:
    """返回元素类型的本地化显示文案。"""
    language = st.session_state.get("language", "zh")
    return ELEMENT_TYPE_LABELS.get(value, {}).get(language, value)


ALIGNMENT_ALIASES = {
    "left": "left",
    "center": "center",
    "right": "right",
    "justify": "justify",
    "justified": "justify",
    "leftalign": "left",
    "centeralign": "center",
    "rightalign": "right",
    "justifiedalign": "justify",
    "左对齐": "left",
    "左": "left",
    "居中": "center",
    "居中对齐": "center",
    "右对齐": "right",
    "右": "right",
    "两端对齐": "justify",
    "两端": "justify",
}


def normalize_alignment(value):
    """统一对齐值为 left/center/right/justify"""
    raw = str(value or "").strip()
    key = raw.lower().replace(" ", "")

    if key in ALIGNMENT_ALIASES:
        return ALIGNMENT_ALIASES[key]

    if "居中" in raw:
        return "center"
    if "右" in raw:
        return "right"
    if "两端" in raw:
        return "justify"
    return "left"


def normalize_template_rules(rules: dict):
    """标准化模板规则，当前主要统一 alignment 字段"""
    if not isinstance(rules, dict):
        return {}

    normalized = {}
    for element_type, rule in rules.items():
        if not isinstance(rule, dict):
            continue
        normalized_rule = dict(rule)
        normalized_rule["alignment"] = normalize_alignment(rule.get("alignment", "left"))
        normalized[element_type] = normalized_rule
    return normalized


def load_api_config():
    """加载API配置"""
    api_config = config_manager.get_api_config()
    if api_config:
        st.session_state.api_url = api_config.get('api_url', '')
        st.session_state.api_key = api_config.get('api_key', '')
        st.session_state.model = api_config.get('model', 'deepseek-chat')


def save_api_config():
    """保存API配置"""
    config_manager.save_api_config({
        'api_url': st.session_state.api_url,
        'api_key': st.session_state.api_key,
        'model': st.session_state.model
    })


def load_header_footer_config():
    """加载页眉页脚配置"""
    app_config = config_manager.get_app_config()
    st.session_state.language = app_config.get('language', st.session_state.language)
    if 'header_footer_config' in app_config:
        st.session_state.header_footer_config = app_config['header_footer_config']


def save_header_footer_config():
    """保存页眉页脚配置"""
    app_config = config_manager.get_app_config()
    app_config['language'] = st.session_state.language
    app_config['header_footer_config'] = st.session_state.header_footer_config
    config_manager.save_app_config(app_config)


def save_language_config():
    """保存语言设置"""
    app_config = config_manager.get_app_config()
    app_config['language'] = st.session_state.language
    config_manager.save_app_config(app_config)


# 初始化时加载配置
load_api_config()
load_header_footer_config()


# ========================
# 文档处理函数
# ========================
def process_document(uploaded_file, template_name: str, api_url: str, api_key: str, model: str, hf_config: dict):
    """处理文档排版"""
    add_log(t("log_start_processing"))
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.docx")
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        add_log(t("log_temp_created", path=input_path))

        # 1. 读取文档（复用核心处理链路）
        doc_processor = DocProcessor()
        if not doc_processor.read_document(input_path):
            raise ValueError(t("error_doc_read_failed"))
        paragraphs_text = doc_processor.get_document_text()
        add_log(t("log_doc_read", count=len(paragraphs_text)))

        # 2. 获取并标准化模板
        format_manager = FormatManager()
        template = format_manager.get_template(template_name)
        if not template:
            raise ValueError(t("error_template_not_found", name=template_name))
        template_rules = normalize_template_rules(template.get("rules", {}))
        add_log(t("log_template_loaded", name=template_name))

        # 3. 调用AI API生成排版指令
        api_config = {
            "api_url": api_url,
            "api_key": api_key,
            "model": model,
            "timeout": 300,
        }
        ai_connector = AIConnector(api_config)
        valid, error_msg = ai_connector.validate_config()
        if not valid:
            raise ValueError(t("error_invalid_api_config", message=error_msg))

        add_log(t("log_calling_ai"))
        prompt = ai_connector.generate_prompt(paragraphs_text, template_rules)
        success, response = ai_connector.send_request(prompt)
        if not success:
            raise ValueError(t("error_ai_request_failed", message=response))
        add_log(t("log_ai_received"))

        success, formatting_instructions = ai_connector.parse_response(response)
        if not success:
            raise ValueError(t("error_parse_response_failed", message=formatting_instructions))
        add_log(t("log_generated_instructions", count=len(formatting_instructions.get('elements', []))))

        # 4. 复用核心文档处理器（含页眉页脚）
        header_footer_config = HeaderFooterConfig.from_dict(hf_config or {})
        is_valid_hf, hf_error = header_footer_config.validate()
        if not is_valid_hf:
            raise ValueError(t("error_invalid_header_footer", message=hf_error))

        success = doc_processor.apply_formatting(
            formatting_instructions,
            custom_save_path=temp_dir,
            header_footer_config=header_footer_config,
        )
        if not success:
            raise ValueError(t("error_formatting_failed"))

        output_file = doc_processor.get_output_file()
        if not output_file or not os.path.exists(output_file):
            raise ValueError(t("error_output_not_found"))

        with open(output_file, "rb") as f:
            output_bytes = f.read()

        add_log(t("log_format_complete"))
        return output_bytes


# ========================
# 页面：文档排版
# ========================
def page_document_format():
    """文档排版页面"""
    st.markdown(f'<p class="main-header">{t("page_document_format")}</p>', unsafe_allow_html=True)

    # 检查API配置
    if not st.session_state.api_url or not st.session_state.api_key:
        st.warning(t("api_required"))
        st.stop()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(t("upload_document"))
        uploaded_file = st.file_uploader(
            t("select_docx"),
            type=['docx'],
            help=t("select_docx_help")
        )

        if uploaded_file:
            st.success(t("selected_file", name=uploaded_file.name, size_kb=uploaded_file.size / 1024))
            st.session_state.uploaded_file = uploaded_file

    with col2:
        st.subheader(t("template_selection"))
        format_manager = FormatManager()
        template_names = format_manager.get_template_names()

        if template_names:
            selected_template = st.selectbox(
                t("select_template"),
                template_names,
                index=0
            )

            # 显示模板预览
            if selected_template:
                template = format_manager.get_template(selected_template)
                if template:
                    with st.expander(t("template_preview")):
                        st.json(normalize_template_rules(template.get('rules', {})))
        else:
            st.warning(t("no_templates"))
            selected_template = None

    st.divider()

    # 页眉页脚设置（折叠）
    with st.expander(t("header_footer_settings")):
        hf_config = st.session_state.header_footer_config

        c1, c2 = st.columns(2)
        with c1:
            enable_header = st.checkbox(t("enable_header"), value=hf_config.get('enable_header', False))
            header_content = st.text_input(t("header_content"), value=hf_config.get('header_content', ''))
        with c2:
            enable_footer = st.checkbox(t("enable_footer"), value=hf_config.get('enable_footer', False))
            footer_content = st.text_input(t("footer_content"), value=hf_config.get('footer_content', ''))

        # 更新配置
        st.session_state.header_footer_config.update({
            'enable_header': enable_header,
            'header_content': header_content,
            'enable_footer': enable_footer,
            'footer_content': footer_content
        })

    # 排版按钮
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        can_format = uploaded_file and selected_template and st.session_state.api_url and st.session_state.api_key
        start_button = st.button(
            t("start_formatting"),
            type="primary",
            use_container_width=True,
            disabled=not can_format
        )

    with col2:
        if st.button(t("clear"), use_container_width=True):
            st.session_state.uploaded_file = None
            st.session_state.output_bytes = None
            st.session_state.logs = []
            st.rerun()

    with col3:
        if st.session_state.output_bytes:
            st.download_button(
                label=t("download_result"),
                data=st.session_state.output_bytes,
                file_name=f"formatted_{uploaded_file.name if uploaded_file else 'document.docx'}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    # 处理排版
    if start_button:
        st.session_state.logs = []

        with st.spinner(t("processing_spinner")):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text(t("processing_document_status"))
                progress_bar.progress(20)

                output_bytes = process_document(
                    uploaded_file,
                    selected_template,
                    st.session_state.api_url,
                    st.session_state.api_key,
                    st.session_state.model,
                    st.session_state.header_footer_config
                )

                progress_bar.progress(100)
                st.session_state.output_bytes = output_bytes

                st.success(t("formatting_complete"))

            except Exception as e:
                st.error(t("processing_failed", error=str(e)))
                add_log(f"错误: {str(e)}", "ERROR")

    # 日志显示
    if st.session_state.logs:
        st.divider()
        st.subheader(t("processing_logs"))
        with st.container(height=200):
            for log in st.session_state.logs:
                if "[ERROR]" in log:
                    st.error(log)
                elif "[WARNING]" in log:
                    st.warning(log)
                else:
                    st.text(log)


# ========================
# 页面：模板管理
# ========================
def page_template_management():
    """模板管理页面"""
    st.markdown(f'<p class="main-header">{t("template_management_title")}</p>', unsafe_allow_html=True)

    format_manager = FormatManager()

    # 操作按钮
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(t("new_template"), type="primary", use_container_width=True):
            st.session_state.new_template_mode = True
            st.session_state.editing_template = {
                'name': '',
                'description': '',
                'rules': {}
            }

    with col2:
        if st.button(t("refresh_list"), use_container_width=True):
            format_manager.load_templates()
            st.rerun()

    st.divider()

    # 新建/编辑模板表单
    if st.session_state.new_template_mode or st.session_state.editing_template:
        template_editor(format_manager)
        return

    # 模板列表
    templates = format_manager.get_templates()

    if not templates:
        st.info(t("no_template_yet"))
        return

    for name, template in templates.items():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{name}**")
                if template.get('description'):
                    st.caption(template['description'])

            with col2:
                if st.button(t("edit"), key=f"edit_{name}", use_container_width=True):
                    st.session_state.editing_template = template.copy()
                    st.session_state.new_template_mode = False
                    st.rerun()

            with col3:
                if st.button(t("delete"), key=f"del_{name}", use_container_width=True):
                    if format_manager.delete_template(name):
                        st.success(t("deleted_template", name=name))
                        st.rerun()
                    else:
                        st.error(t("delete_failed"))

            # 显示模板规则
            with st.expander(t("view_rules")):
                rules = template.get('rules', {})
                for element_type, rule in rules.items():
                    st.markdown(f"**{element_type_label(element_type)}**: {rule.get('font', '宋体')}, {rule.get('size', '小四')}")

            st.divider()


def template_editor(format_manager: FormatManager):
    """模板编辑器"""
    template = st.session_state.editing_template or {
        'name': '',
        'description': '',
        'rules': {}
    }

    is_new = st.session_state.new_template_mode

    st.subheader(t("create_template_title") if is_new else t("edit_template_title", name=template.get('name', '')))

    # 基本信息
    name = st.text_input(t("template_name"), value=template.get('name', ''), disabled=not is_new)
    description = st.text_input(t("template_description"), value=template.get('description', ''))

    # 规则编辑
    st.subheader(t("format_rules"))

    rules = normalize_template_rules(template.get('rules', {}))
    element_types = ['标题', '一级标题', '二级标题', '三级标题', '正文', '摘要', '关键词', '参考文献']

    # 字体选项
    fonts = ['宋体', '黑体', '楷体', '仿宋', 'Times New Roman', 'Arial']
    # 字号选项
    sizes = ['初号', '小初', '一号', '小一', '二号', '小二', '三号', '小三', '四号', '小四', '五号', '小五', '六号']
    # 对齐选项
    alignments = ['left', 'center', 'right', 'justify']
    alignment_names = {
        'left': 'Left' if st.session_state.language == 'en' else '左对齐',
        'center': 'Center' if st.session_state.language == 'en' else '居中',
        'right': 'Right' if st.session_state.language == 'en' else '右对齐',
        'justify': 'Justify' if st.session_state.language == 'en' else '两端对齐',
    }

    # 添加新规则
    with st.expander(t("add_new_rule")):
        new_type = st.selectbox(t("element_type"), element_types, format_func=element_type_label, key="new_rule_type")

        col1, col2, col3 = st.columns(3)
        with col1:
            new_font = st.selectbox(t("font"), fonts, key="new_rule_font")
        with col2:
            new_size = st.selectbox(t("font_size"), sizes, key="new_rule_size")
        with col3:
            new_align = st.selectbox(t("alignment"), alignments, format_func=lambda x: alignment_names[x], key="new_rule_align")

        new_bold = st.checkbox(t("bold"), key="new_rule_bold")

        if st.button(t("add_rule"), key="add_rule_btn"):
            rules[new_type] = {
                'font': new_font,
                'size': new_size,
                'alignment': new_align,
                'bold': new_bold
            }
            template['rules'] = rules

    # 显示现有规则
    st.markdown(f"**{t('current_rules')}**")
    for element_type, rule in list(rules.items()):
        col1, col2, col3 = st.columns([3, 4, 1])
        with col1:
            st.markdown(f"**{element_type_label(element_type)}**")
        with col2:
            alignment_value = normalize_alignment(rule.get('alignment', 'left'))
            st.text(f"{rule.get('font', '宋体')}, {rule.get('size', '小四')}, {alignment_names.get(alignment_value, alignment_names['left'])}")
        with col3:
            if st.button(t("delete"), key=f"del_rule_{element_type}"):
                del rules[element_type]
                template['rules'] = rules
                st.rerun()

    st.divider()

    # 保存按钮
    col1, col2 = st.columns(2)

    with col1:
        if st.button(t("save_template"), type="primary", use_container_width=True):
            if not name:
                st.error(t("enter_template_name"))
            elif not rules:
                st.error(t("add_rule_required"))
            else:
                template['name'] = name
                template['description'] = description
                template['rules'] = normalize_template_rules(rules)

                if format_manager.save_template(name, template):
                    st.success(t("template_saved", name=name))
                    st.session_state.editing_template = None
                    st.session_state.new_template_mode = False
                    st.rerun()
                else:
                    st.error(t("save_failed"))

    with col2:
        if st.button(t("cancel"), use_container_width=True):
            st.session_state.editing_template = None
            st.session_state.new_template_mode = False
            st.rerun()


# ========================
# 页面：API配置
# ========================
def page_api_config():
    """API配置页面"""
    st.markdown(f'<p class="main-header">{t("page_api_config")}</p>', unsafe_allow_html=True)

    st.info(t("api_config_info"))

    # API URL
    api_url = st.text_input(
        t("api_url_label"),
        value=st.session_state.api_url,
        placeholder=t("api_url_placeholder"),
        help=t("api_url_help")
    )

    # API Key
    api_key = st.text_input(
        t("api_key_label"),
        value=st.session_state.api_key,
        type="password",
        placeholder=t("api_key_placeholder"),
        help=t("api_key_help")
    )

    # 模型选择
    common_models = [
        "deepseek-chat",
        "deepseek-coder",
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "claude-3-opus",
        "claude-3-sonnet"
    ]

    model_option = st.radio(
        t("model_selection_mode"),
        [t("preset_model"), t("custom_model")],
        horizontal=True
    )

    if model_option == t("preset_model"):
        model = st.selectbox(
            t("model_label"),
            common_models,
            index=0 if st.session_state.model not in common_models else common_models.index(st.session_state.model)
        )
    else:
        model = st.text_input(
            t("custom_model_name"),
            value=st.session_state.model,
            placeholder=t("custom_model_placeholder")
        )

    # 更新会话状态
    st.session_state.api_url = api_url
    st.session_state.api_key = api_key
    st.session_state.model = model

    st.divider()

    # 保存按钮
    col1, col2 = st.columns(2)

    with col1:
        if st.button(t("save_config"), type="primary", use_container_width=True):
            save_api_config()
            st.success(t("config_saved"))

    with col2:
        if st.button(t("test_connection"), use_container_width=True):
            if not api_url or not api_key:
                st.error(t("fill_api_url_key"))
            else:
                with st.spinner(t("testing")):
                    try:
                        api_config = {
                            "api_url": api_url,
                            "api_key": api_key,
                            "model": model
                        }
                        connector = AIConnector(api_config)
                        valid, msg = connector.validate_config()
                        if valid:
                            st.success(t("connection_success", model=model))
                        else:
                            st.error(t("connection_failed", message=msg))
                    except Exception as e:
                        st.error(t("test_failed", error=str(e)))

    # 显示当前配置
    st.divider()
    st.subheader(t("current_config"))

    api_config = config_manager.get_api_config()
    if api_config:
        st.json({
            "api_url": api_config.get('api_url', t("not_set")),
            "model": api_config.get('model', t("not_set")),
            "last_updated": api_config.get('last_updated', t("unknown"))
        })
    else:
        st.text(t("no_saved_config"))


# ========================
# 页面：从文本解析模板
# ========================
def page_text_parsing():
    """从文本解析模板页面"""
    st.markdown(f'<p class="main-header">{t("page_text_parsing")}</p>', unsafe_allow_html=True)

    st.info(t("text_parsing_info"))

    # 检查API配置
    if not st.session_state.api_url or not st.session_state.api_key:
        st.warning(t("api_required"))
        st.stop()

    # 模板名称
    template_name = st.text_input(t("template_name"), placeholder=t("template_name_placeholder"))
    template_desc = st.text_input(t("template_description"), placeholder=t("template_desc_placeholder"))

    # 格式要求文本
    format_text = st.text_area(
        t("format_desc_label"),
        height=200,
        placeholder=t("format_desc_placeholder")
    )

    if st.button(t("generate_template"), type="primary"):
        if not template_name:
            st.error(t("enter_template_name"))
        elif not format_text:
            st.error(t("enter_format_desc"))
        else:
            with st.spinner(t("ai_parsing_spinner")):
                try:
                    api_config = {
                        "api_url": st.session_state.api_url,
                        "api_key": st.session_state.api_key,
                        "model": st.session_state.model,
                        "timeout": 120
                    }
                    connector = AIConnector(api_config)
                    parser = TextTemplateParser(connector)

                    success, result = parser.parse_text_to_template(
                        format_text,
                        template_name=template_name,
                        template_description=template_desc or template_name
                    )
                    if not success:
                        st.error(t("parse_failed", message=result))
                        return

                    result["rules"] = normalize_template_rules(result.get("rules", {}))

                    # 保存模板
                    format_manager = FormatManager()
                    template_valid, template_error = format_manager.validate_template(result)
                    if not template_valid:
                        st.error(t("invalid_template_format", message=template_error))
                        return

                    if format_manager.save_template(template_name, result):
                        st.success(t("template_created", name=template_name))
                        st.json(result)
                    else:
                        st.error(t("save_failed"))

                except Exception as e:
                    st.error(t("processing_failed", error=str(e)))


# ========================
# 页面：帮助
# ========================
def page_help():
    """帮助页面"""
    st.markdown(f'<p class="main-header">{t("page_help")}</p>', unsafe_allow_html=True)

    st.markdown(t("help_markdown"))

    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666;">
        FormulaAI Web v2.0.0 |
        <a href="https://github.com/waterdrop26651/FormulaAI" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)


# ========================
# 主应用
# ========================
def main():
    """主应用"""
    # 侧边栏导航
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">
                <span style="color: #3b82f6;">F</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.title("FormulaAI")
        st.caption(t("sidebar_tagline"))

        language_options = {
            t("language_option_zh"): "zh",
            t("language_option_en"): "en",
        }
        current_language_label = next(
            (label for label, value in language_options.items() if value == st.session_state.language),
            t("language_option_zh"),
        )
        selected_language_label = st.selectbox(
            t("language_selector"),
            list(language_options.keys()),
            index=list(language_options.keys()).index(current_language_label),
        )
        selected_language = language_options[selected_language_label]
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            save_language_config()
            st.rerun()

        st.divider()

        page_options = [
            t("page_document_format"),
            t("page_template_management"),
            t("page_api_config"),
            t("page_text_parsing"),
            t("page_help"),
        ]
        page = st.radio(
            "导航",
            page_options,
            label_visibility="collapsed"
        )

        st.divider()

        # 状态显示
        if st.session_state.api_url and st.session_state.api_key:
            st.success(t("sidebar_status_ready"))
        else:
            st.warning(t("sidebar_status_missing"))

    # 根据选择显示页面
    if page == t("page_document_format"):
        page_document_format()
    elif page == t("page_template_management"):
        page_template_management()
    elif page == t("page_api_config"):
        page_api_config()
    elif page == t("page_text_parsing"):
        page_text_parsing()
    elif page == t("page_help"):
        page_help()


if __name__ == "__main__":
    main()
