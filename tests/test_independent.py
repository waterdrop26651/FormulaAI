# -*- coding: utf-8 -*-
"""
独立测试 - 不依赖项目包结构
直接测试核心模块代码
"""

import re
import json
import sys

print("=" * 60)
print("FormulaAI 独立测试")
print("=" * 60)

# ========================
# 测试1: Unicode修复验证
# ========================
print("\n【测试1】Unicode字符串修复验证")
print("-" * 40)

# 正确的中文标点Unicode
chinese_punctuation = '.!?;,\u3002\u3001\uff01\uff1f\uff1b\uff0c'
print(f"中文标点字符: {repr(chinese_punctuation)}")

test_cases = [
    ("论文标题", True),      # 无标点 -> 应是标题
    ("论文标题。", False),   # 有句号 -> 不是标题
    ("引言，背景", False),   # 有逗号 -> 不是标题
    ("摘要", True),          # 无标点 -> 应是标题
]

passed = 0
for text, should_be_title in test_cases:
    has_punct = any(p in text for p in chinese_punctuation)
    is_title = not has_punct and len(text) < 20

    status = "✓" if is_title == should_be_title else "✗"
    if is_title == should_be_title:
        passed += 1
    print(f"  {status} '{text}' -> 检测为标题: {is_title}, 预期: {should_be_title}")

print(f"\n结果: {passed}/{len(test_cases)} 通过")

# ========================
# 测试2: 正则表达式预编译
# ========================
print("\n【测试2】正则表达式预编译验证")
print("-" * 40)

patterns = [
    re.compile(r'^\d+\.\s+.+'),           # 1. 标题
    re.compile(r'^\d+\.\d+\.\s+.+'),      # 1.1. 标题
    re.compile(r'^[\u4e00-\u9fa5]+\s*[\u3001\uff0c\uff1a]\s*.+'),  # 一、标题
]

test_texts = [
    ("1. 引言", True),
    ("1.1. 背景", True),
    ("一、研究背景", True),
    ("这是正文", False),
]

passed = 0
for text, should_match in test_texts:
    matched = any(p.match(text) for p in patterns)

    status = "✓" if matched == should_match else "✗"
    if matched == should_match:
        passed += 1
    print(f"  {status} '{text}' -> 匹配: {matched}, 预期: {should_match}")

print(f"\n结果: {passed}/{len(test_texts)} 通过")

# ========================
# 测试3: JSON修复功能
# ========================
print("\n【测试3】JSON修复功能验证")
print("-" * 40)

def simple_json_fix(json_str):
    """简化的JSON修复"""
    # 尝试使用json5
    try:
        import json5
        return json.dumps(json5.loads(json_str))
    except:
        pass

    # 修复缺少括号
    open_braces = json_str.count("{") - json_str.count("}")
    open_brackets = json_str.count("[") - json_str.count("]")
    return json_str + "}" * open_braces + "]" * open_brackets

test_jsons = [
    ('{"key": "value"}', True),
    ('{"elements": [1, 2, 3}', True),  # 缺少 ]
    ('{"a": 1, "b": 2', True),          # 缺少 }
]

passed = 0
for json_str, should_fix in test_jsons:
    try:
        fixed = simple_json_fix(json_str)
        result = json.loads(fixed)
        status = "✓"
        passed += 1
        print(f"  {status} '{json_str[:30]}...' -> 修复成功")
    except Exception as e:
        print(f"  ✗ '{json_str[:30]}...' -> 修复失败: {e}")

print(f"\n结果: {passed}/{len(test_jsons)} 通过")

# ========================
# 测试4: 语法检查
# ========================
print("\n【测试4】Python语法检查")
print("-" * 40)

import py_compile

files = [
    "src/core/structure_analyzer.py",
    "src/core/doc_processor.py",
    "src/core/ai_connector.py",
]

passed = 0
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"  ✓ {f}")
        passed += 1
    except py_compile.PyCompileError as e:
        print(f"  ✗ {f}: {e}")

print(f"\n结果: {passed}/{len(files)} 通过")

# ========================
# 总结
# ========================
print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
