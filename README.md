# FormulaAI - AI 智能文档排版工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

FormulaAI 是一款基于 AI 技术的智能文档排版工具，提供 Web 界面，能够自动分析未排版的 Word 文档结构，并根据用户配置的排版规则进行专业排版。本工具特别适合学术论文、研究报告、技术文档等需要规范格式的文档处理。

**项目致谢**：本项目沿用 `https://github.com/chenningling/AIPoliDoc` 的项目结构和部分代码。

## 主要功能

- **文档结构智能分析**：利用 AI 能力分析未排版文档的结构，自动识别标题、摘要、关键词、正文等内容
- **Web 图形界面**：
  - 基于 Streamlit 的现代化 Web 界面
  - 支持多页面导航（文档排版、模板管理、API 配置、从文本解析、帮助）
  - 响应式设计，支持不同屏幕尺寸
  - 支持中英文界面切换，并持久化保存语言设置
- **排版规则管理**：
  - 支持预设模板和自定义排版规则
  - 提供多个预设模板（论文格式、研究报告等）
  - Web 界面直接创建、编辑、删除模板
  - AI 智能解析：从自然语言描述生成模板
- **页眉页脚配置**：
  - 支持页眉页脚内容设置
  - 可配置字体、字号、对齐方式
  - Web 排版流程已接入核心页眉页脚处理器
- **多种 AI API 支持**：
  - 支持 DeepSeek、OpenAI 等兼容 API
  - 配置持久化保存
- **运行环境兼容**：
  - 默认不依赖 PyQt6，CLI、CI 和 headless 环境可直接运行
  - 如需 Qt 字体探测，可额外安装 GUI 依赖
- **详细日志**：提供详细的处理日志和进度显示
- **自动化测试**：
  - 覆盖核心解析、模板标准化、页眉页脚、配置管理与 AI 响应解析
  - 不依赖旧版 Qt UI，也不依赖外部 API

## 系统要求

- **操作系统**：跨平台（Windows、macOS、Linux）
- **Python 环境**：Python 3.8 或更高版本
- **浏览器**：现代浏览器（Chrome、Firefox、Safari、Edge）

## 项目结构

```
FormulaAI/
├── config/                # 配置文件目录
│   ├── api_config.json   # AI API配置
│   ├── app_config.json   # 应用配置
│   └── templates/        # 排版模板目录
├── src/                  # 源代码目录
│   ├── core/            # 核心功能模块
│   │   ├── ai_connector.py     # AI服务连接器
│   │   ├── doc_processor.py    # 文档处理器
│   │   ├── format_manager.py   # 格式管理器
│   │   ├── structure_analyzer.py# 结构分析器
│   │   ├── header_footer_config.py # 页眉页脚配置
│   │   └── header_footer_processor.py # 页眉页脚处理器
│   └── utils/           # 工具类模块
│       ├── config_manager.py  # 配置管理器
│       ├── font_manager.py    # 字体管理器
│       ├── file_utils.py      # 文件工具
│       └── logger.py          # 日志系统
├── tests/               # 测试文件
├── web_app.py           # Web应用入口
└── pyproject.toml       # 项目配置
```

## 安装方法

1. 克隆项目代码：
   ```bash
   git clone https://github.com/waterdrop26651/FormulaAI.git
   cd FormulaAI
   ```

2. 安装基础依赖：
   ```bash
   pip install -e .
   ```

   或手动安装：
   ```bash
   pip install python-docx requests pillow chardet json5 streamlit
   ```

3. 可选：安装 GUI 字体探测依赖：
   ```bash
   pip install -e .[gui]
   ```

说明：
- `PyQt6` 现在是可选依赖，不再是 Web 版本必装项
- 默认字体发现会优先使用系统命令，适合本地终端、CI 和 headless 环境

## 使用说明

### 启动应用

```bash
python -m streamlit run web_app.py
```

或：

```bash
streamlit run web_app.py
```

启动后默认在浏览器访问 `http://localhost:8501`

### 使用流程

1. **配置 API**（首次使用）
   - 在侧边栏点击「API配置 / API Settings」
   - 填写 API URL（如 `https://api.deepseek.com`）
   - 填写 API Key
   - 选择模型
   - 点击「保存配置」
   - 可用「测试连接」验证配置

2. **排版文档**
   - 点击「文档排版」
   - 上传 Word 文档（`.docx` 格式）
   - 选择排版模板
   - （可选）配置页眉页脚
   - 点击「开始排版」
   - 下载排版后的文档

3. **管理模板**
   - 点击「模板管理」
   - 查看现有模板规则
   - 创建新模板或编辑现有模板
   - 删除不需要的模板

4. **AI 解析模板**
   - 点击「从文本解析」
   - 输入模板名称
   - 用自然语言描述格式要求
   - AI 自动生成排版模板

5. **切换界面语言**
   - 在左侧边栏使用 `Language / 语言` 切换
   - 当前支持 `中文` 和 `English`
   - 语言设置会写入应用配置并在下次启动时恢复

### API 配置示例

支持的 API 服务：

| 服务商 | Base URL |
|--------|----------|
| DeepSeek | `https://api.deepseek.com` |
| OpenAI | `https://api.openai.com` |
| 其他 | 输入兼容 API 的 Base URL |

## 常见问题

1. **API 配置问题**
   - 确保 API 密钥正确
   - 检查网络连接
   - 确认账户余额充足

2. **排版效果问题**
   - 检查文档结构是否规范
   - 尝试调整模板参数
   - 查看日志了解 AI 识别结果

3. **字体问题**
   - 请确保打开文档的电脑安装了相应字体
   - 默认不依赖 PyQt6 也可以完成字体发现与文档生成
   - 如需 Qt 字体探测，可安装 `.[gui]`

## 技术栈

- **后端框架**：Python 3.8+
- **Web 框架**：Streamlit
- **文档处理**：python-docx
- **AI 接口**：支持 OpenAI 兼容 API
- **测试框架**：pytest

## 测试

运行测试：

```bash
python -m pytest -q
```

当前测试覆盖：
- 文档结构分析器
- 模板文本解析与规则标准化
- `ConfigManager` / `FormatManager`
- `HeaderFooterConfig` / `HeaderFooterProcessor`
- `AIConnector` 的无网络解析逻辑

## 当前状态

- Web 排版流程已接入核心 `DocProcessor`
- 页眉页脚配置已接入实际文档输出链路
- 模板和 AI 响应中的 `alignment` 会统一标准化为 `left / center / right / justify`
- 旧版 Qt UI 测试已移除，测试体系已切换到当前 Web/核心逻辑

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
