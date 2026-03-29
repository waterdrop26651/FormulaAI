# FormulaAI - AI 智能文档排版工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

FormulaAI 是一款基于 AI 技术的智能文档排版工具，提供 Web 界面，能够自动分析未排版的 Word 文档结构，并根据用户配置的排版规则进行专业排版。本工具特别适合学术论文、研究报告、技术文档等需要规范格式的文档处理。

**项目致谢**：本项目沿用 `https://github.com/chenningling/AIPoliDoc` 的项目结构和部分代码。

## 简历 / 面试版项目表述

### 项目介绍

FormulaAI 是一款面向学术论文、研究报告等场景的 AI 智能文档排版工具，能够自动识别未排版 Word 文档的结构，并按模板规则完成格式化输出。我主导推动了项目从“可用的 AI 功能”向“可验证、可回归、可持续迭代的 AI 产品系统”升级，重点补齐了 runtime harness、offline eval harness 与 CI 质量门禁，使 AI 排版结果不再依赖人工肉眼检查，而是具备结构化验证和持续优化能力。

### 技术栈

Python、Streamlit、python-docx、pytest、GitHub Actions

### 个人贡献

- 负责设计并落地 FormulaAI 的 runtime harness，统一文档排版链路的输入输出契约、阶段事件、失败分类和运行工件，提升 AI 流程的可观测性与可控性。
- 负责搭建 offline eval harness，通过冻结样例回放 AI 响应，并校验真实 Word 渲染结果，把 AI 排版能力从“人工体验判断”升级为“可复放、可评测、可回归”的产品能力。
- 负责将 `pytest + formulaai-eval` 接入 GitHub Actions，形成自动化 CI gate，并完善 README 中对 Harness Engineering 方案、价值和落地方式的说明。

## 什么是 Harness Engineering

Harness Engineering 不是单纯“把模型接进产品”，而是给 AI 系统补上一层可控、可测、可复放、可在 CI 中稳定运行的工程化外骨骼。  
它关注的重点不是 prompt 写得多花，而是：

- 把原本一次性的 AI 调用链路收敛成显式运行时入口
- 为输入、阶段、输出、失败原因建立结构化契约
- 让同一条链路可以被离线回放、评测和回归测试
- 让结果产生可追踪工件，而不是只停留在页面上的“看起来成功”
- 把这些能力接进 CI，变成真正的质量门禁

对 FormulaAI 这种“AI 识别文档结构 -> 生成排版指令 -> 渲染 Word 输出”的产品来说，Harness Engineering 的价值很直接：它把文档排版从“依赖人工点点看效果”升级成“可以稳定验证、持续迭代、可回归检查”的 AI 产品系统。

## 本次 Harness Engineering 更新

这次更新的核心，不是再加一个页面或一个按钮，而是把 FormulaAI 从“有 AI 功能的应用”进一步改造成“带 runtime/eval/CI harness 的 AI 系统”。

具体包括：

- **Phase 1: Runtime Harness**
  - 把文档排版主链路收敛到 `DocumentFormatHarness`
  - 引入请求/结果契约、阶段记录、错误分类、运行清单和事件日志
  - Web 页面不再直接拼装核心流程，而是走统一 runtime 入口

- **Phase 2: Offline Eval Harness**
  - 新增 `formulaai-eval` CLI 和离线 replay case
  - 使用冻结样例回放 AI 响应，不依赖外部 API
  - 不只检查 AI 返回的计划，还验证最终渲染出来的文档文本和 alignment
  - 输出 `summary.json` 和 `results.jsonl`，让评测结果可机器消费

- **CI Gate**
  - GitHub Actions 自动运行 `pytest + formulaai-eval`
  - 把 eval 结果作为 CI 工件上传，形成可回看的回归记录

一句话概括：这次更新让 FormulaAI 不再只是“能跑的 AI 排版工具”，而是具备了 runtime harness、offline eval harness 和 CI gate 的工程化 AI 产品。

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
│   ├── runtime/         # 运行时编排层
│   │   ├── contracts.py # 运行时请求/结果/阶段契约
│   │   ├── document_format_harness.py # 文档排版运行时 harness
│   │   ├── eval_harness.py # 离线评测 harness 与 CLI
│   │   ├── events.py    # 运行时事件适配
│   │   ├── run_store.py # 运行元数据持久化
│   │   └── template_rules.py # 共享规则标准化
│   └── utils/           # 工具类模块
│       ├── config_manager.py  # 配置管理器
│       ├── font_manager.py    # 字体管理器
│       ├── file_utils.py      # 文件工具
│       └── logger.py          # 日志系统
├── evals/               # 离线评测样例
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

### 运行离线评测

安装项目后可直接运行：

```bash
formulaai-eval --cases-dir evals/cases
```

或使用模块方式：

```bash
python3 -m src.runtime.eval_harness --cases-dir evals/cases
```

评测特性：

- 不访问外部 API，适合本地回归和 CI
- 复用现有 runtime 文档排版链路
- 默认把 suite 结果写到 `runtime/evals/<suite_id>/summary.json`
- 同时写出逐条 case 结果 `runtime/evals/<suite_id>/results.jsonl`
- 任一 case 断言不满足时返回非零退出码

CI 现在会自动执行：

- `python3 -m pytest -q`
- `formulaai-eval --cases-dir evals/cases`

并把 eval 结果工件上传，方便回看 `summary.json` 和 `results.jsonl`

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
- 运行时 harness、运行记录与 Web 编排入口
- 离线 eval harness、case 回放与 CLI 退出码
- `ConfigManager` / `FormatManager`
- `HeaderFooterConfig` / `HeaderFooterProcessor`
- `AIConnector` 的无网络解析逻辑

## 当前状态

- FormulaAI 已形成 `runtime harness + offline eval harness + CI gate` 的基本 Harness Engineering 结构
- Web 页面现在通过 `src/runtime/document_format_harness.py` 调用核心排版链路
- Runtime Harness 已提供显式请求/结果契约、阶段记录、脱敏运行元数据与输出校验
- Offline Eval Harness 可对冻结 case 做回放评测，并输出 `summary.json + results.jsonl`
- GitHub Actions 已接入 `pytest + formulaai-eval`，可把 harness 结果作为 CI gate
- 运行记录默认只保留 `manifest.json` / `events.jsonl` 这类脱敏元数据，不默认持久化原始文档、prompt、response
- Web 排版流程已接入核心 `DocProcessor`
- 页眉页脚配置已接入实际文档输出链路
- 模板和 AI 响应中的 `alignment` 会统一标准化为 `left / center / right / justify`
- 旧版 Qt UI 测试已移除，测试体系已切换到当前 Web/核心逻辑

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
