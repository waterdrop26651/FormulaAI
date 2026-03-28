# Runtime Eval Harness Phase 2 Design

## Goal

为 FormulaAI 增加一条离线、可复放、CI 友好的评测链路，把现有 `DocumentFormatHarness` 从“只负责一次运行”推进到“可被固定样例系统化检验”。

## Scope

Phase 2 只做离线 eval，不做在线 API 评测平台。

- 复用现有 `DocumentFormatHarness`
- 使用冻结的输入段落、模板规则和 AI 响应内容进行回放
- 产出机器可读的 suite 结果文件
- 提供一个可直接在本地和 CI 调用的 CLI 入口

不在本阶段做的内容：

- 不接外部真实模型
- 不做复杂指标平台或可视化 dashboard
- 不持久化敏感原文、prompt、response

## Design

### 1. Eval Case Contract

新增 `formulaai.eval_case.v1` JSON 用例格式。单个 case 包含：

- `id`
- `description`
- `source`
  - `source_name`
  - `paragraphs`
- `template`
  - `name`
  - `rules`
- `ai`
  - `validate_ok`
  - `validate_message`
  - `request_ok`
  - `response_content`
- `header_footer_config`
- `expect`
  - `status`
  - `final_stage`
  - `instruction_count`
  - `processed_elements`
  - `error_code`
  - `output_document_loadable`
  - `output_paragraph_count`
  - `output_alignments`

这样可以覆盖成功路径、AI 配置失败、AI 返回格式错误三类典型场景，同时保持 case 可读、可扩展。

### 2. Eval Runner

新增 `RuntimeEvalHarness`，职责如下：

- 从 case 目录加载用例
- 为每个 case 临时生成输入 docx
- 注入回放版 `AIConnector`
- 调用现有 `DocumentFormatHarness.run(...)`
- 读取运行产出的 `manifest.json`
- 将实际结果与期望断言比对，生成 case 级结果
- 写出 suite 级 `summary.json`

Runner 自己不处理 UI，不依赖 Streamlit。

### 3. Replay AI Connector

新增一个只用于 eval 的连接器包装：

- `validate_config()` 按 case 固定返回
- `send_request()` 返回固定响应或固定失败
- `parse_response()` 复用现有 `AIConnector.parse_response()`
- `generate_prompt()` 复用现有 `AIConnector.generate_prompt()`

这样可以让 eval 覆盖现有 prompt/response 解析链路，同时完全离线。

### 4. Result Artifact

新增 `formulaai.eval_suite.v1` 结果文件，路径为 `runtime/evals/<suite_id>/summary.json`。

结果包含：

- `suite_id`
- `created_at`
- `cases_total`
- `cases_passed`
- `cases_failed`
- `results`
  - `case_id`
  - `passed`
  - `mismatches`
  - `actual`
  - `manifest_path`
  - `run_id`

有任一 case 未通过时，CLI 返回非零退出码，便于 CI 直接消费。

## Testing Strategy

- 用测试先锁定：
  - case 加载
  - 成功 case 汇总结果
  - 失败 case 的 mismatch 输出
  - CLI 退出码
- fixture case 至少覆盖：
  - 成功渲染并标准化 alignment
  - 包装型 JSON 响应解析成功
  - 缺失 `elements` 导致 AI 响应无效

## Risks

- `docx` 二进制整体不稳定，不能做字节级全等断言
- 运行时会清理 temp 目录，因此 eval 必须基于独立 case 输入，而不是依赖临时工件
- 结果断言应以结构化指标为主，如阶段、元素数、段落数、alignment 和错误码
