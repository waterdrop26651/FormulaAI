# FormulaAI - AI 智能文档排版工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

FormulaAI 是一款基于 AI 技术的智能文档排版工具。它能够自动分析未排版的 Word 文档结构，并根据用户配置的排版规则（如学术论文、研究报告、技术文档规范）进行专业级的自动化排版，极大提升长文档格式化的效率与规范性。

## 📑 目录
- [ 核心特性](#-核心特性)
- [ 工程化实践 (Harness Engineering)](#-工程化实践-harness-engineering)
- [ 快速开始](#-快速开始)
- [ 使用指南](#-使用指南)
- [ 项目结构](#-项目结构)
- [ 常见问题](#-常见问题)
- [ 参与贡献](#-参与贡献)
- [ 许可证](#-许可证)
- [ 致谢](#-致谢)

##  核心特性

- **文档结构智能分析**：利用大语言模型 (LLM) 分析未排版文档的结构，自动识别标题、摘要、关键词、正文等内容。
- **灵活的排版规则管理**：
  - 内置多种预设模板（学术论文格式、研究报告等）。
  - 支持通过 Web 界面创建、编辑、删除模板。
  - 支持通过自然语言描述直接生成对应的排版规则配置。
- **细粒度格式控制**：支持页眉页脚的定制化配置（字体、字号、对齐方式），并已深度整合到核心渲染链路中。
- **现代化 Web 交互**：
  - 基于 Streamlit 打造的响应式 Web 界面。
  - 支持中英文双语界面切换，并持久化保存用户偏好设置。
- **多模型 API 支持**：原生支持 DeepSeek、OpenAI 等兼容 API，配置灵活且持久化。
- **跨平台与易部署**：默认不依赖复杂 GUI 库（如 PyQt6），支持在本地终端、CI 和 Headless 环境下稳定运行。

##  工程化实践 (Harness Engineering)

本项目不仅是一个 AI 应用，更是一个具备完整 **Harness Engineering（工程化外骨骼）** 的 AI 系统，确保了 AI 排版流程的可控、可测与可回归：

- **Runtime Harness (运行时契约)**：将复杂的文档排版链路收敛至 `DocumentFormatHarness`，建立结构化的输入/输出契约、阶段记录与错误分类。
- **Offline Eval Harness (离线评测)**：提供 `formulaai-eval` CLI 工具，支持通过冻结的测试用例进行离线回放。不仅检查 AI 响应计划，还验证最终渲染文档的文本和排版对齐效果，并输出机器可读的 `summary.json` 和 `results.jsonl`。
- **CI Gate (持续集成门禁)**：全面接入 GitHub Actions，自动执行 `pytest` 与离线评测，将 eval 结果作为 CI 工件上传，生成可追溯的回归测试记录，保障每一次迭代的质量。

##  快速开始

### 1. 环境要求
- **操作系统**：Windows / macOS / Linux
- **Python 版本**：>= 3.8
- **浏览器**：Chrome / Firefox / Safari / Edge 等现代浏览器

### 2. 安装与配置

```bash
# 克隆项目代码
git clone https://github.com/waterdrop26651/FormulaAI.git
cd FormulaAI

# 安装基础依赖
pip install -e .

# （可选）如果需要 Qt 字体探测功能，可安装完整 GUI 依赖
pip install -e .[gui]
```
> **注**：默认使用系统命令进行字体探测，非常适合本地终端、CI 和服务器 (Headless) 环境。

## 📖 使用指南

### 启动 Web 界面

```bash
streamlit run web_app.py
```
启动后，浏览器会自动打开 `http://localhost:8501`。

### 核心工作流

1. **配置 AI 模型**（首次使用）：
   - 进入左侧导航栏的「API 配置」。
   - 填入兼容的 API URL（如 `https://api.deepseek.com` 或 `https://api.openai.com`）和对应的 API Key。
   - 选择模型后，点击保存并测试连接。
2. **执行文档排版**：
   - 切换到「文档排版」页面，上传待处理的 `.docx` 文档。
   - 选择目标排版模板，并按需配置页眉页脚。
   - 点击「开始排版」，处理完成后即可下载标准化排版后的文档。
3. **自然语言生成模板**：
   - 在「从文本解析」页面，输入如“一级标题黑体三号居中，正文宋体小四，首行缩进两字符”等描述。
   - AI 将自动为您生成结构化的排版模板，可直接保存使用。

### 运行离线评测 (Eval)

开发者可直接运行内置的评测套件，用于回归测试：

```bash
# 使用 CLI 运行
formulaai-eval --cases-dir evals/cases

# 或通过 Python 模块运行
python3 -m src.runtime.eval_harness --cases-dir evals/cases
```

##  项目结构

```text
FormulaAI/
├── config/                # 配置文件目录 (API配置、应用配置、预设模板)
├── src/                   # 源代码目录
│   ├── core/              # 核心功能模块 (AI连接、文档处理、格式管理)
│   ├── runtime/           # 运行时编排层 (Harness、契约、评测、事件流)
│   └── utils/             # 通用工具类 (配置、字体、日志等)
├── evals/                 # 离线评测用例 (Cases)
├── tests/                 # 单元测试与集成测试
├── web_app.py             # Streamlit Web 应用入口
└── pyproject.toml         # 项目依赖与构建配置
```

##  常见问题

**Q: API 连接失败或超时怎么办？**
- 请检查网络环境，确认 API Key 填写无误且账户有充足余额。部分服务商可能需要配置网络代理。

**Q: 排版后发现字体未生效？**
- 排版生成的 Word 文档依赖于打开它的电脑上是否安装了对应字体。请确保目标设备已安装所需的字体（如“黑体”、“宋体”等）。

**Q: AI 识别文档结构不准确？**
- 确保原始文档有基本的段落区分。您也可以通过调整 API 的 Temperature 参数或更换推理能力更强的模型（如 DeepSeek V3/R1 或 GPT-4o）来改善结构识别效果。

##  参与贡献

欢迎通过 Issue 或 Pull Request 参与项目建设！

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

在提交 PR 前，请确保通过了所有的单元测试与评测用例：
```bash
python -m pytest -q
formulaai-eval --cases-dir evals/cases
```

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

##  致谢

本项目在开发过程中，部分结构与代码参考了 [AIPoliDoc](https://github.com/chenningling/AIPoliDoc)，特此致谢！
