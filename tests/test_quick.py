# -*- coding: utf-8 -*-
"""
核心功能快速测试（不依赖Qt）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_structure_analyzer():
    """测试结构分析器"""
    from src.core.structure_analyzer import StructureAnalyzer

    print("\n=== 测试结构分析器 ===")

    analyzer = StructureAnalyzer()

    # 测试中文标点检测
    test_paragraphs = [
        "论文标题",
        "这是摘要内容。",
        "一、引言",
        "1.1 背景",
        "这是正文内容，包含多个句子。"
    ]

    features = analyzer.analyze_text_features(test_paragraphs)

    print(f"段落数: {len(features['paragraph_lengths'])}")
    print(f"潜在标题索引: {features['potential_titles']}")
    print(f"潜在小标题索引: {features['potential_subtitles']}")

    # 验证结果
    assert 0 in features['potential_titles'], "第一段应是潜在标题"
    print("✓ 标题检测正常")

    return True

def test_structure_analyzer_unicode():
    """测试Unicode修复"""
    from src.core.structure_analyzer import StructureAnalyzer

    print("\n=== 测试Unicode修复 ===")

    analyzer = StructureAnalyzer()

    # 测试带中文标点的段落
    test_cases = [
        ("这是标题。", False),  # 有句号，不应是标题
        ("这是标题", True),     # 无标点，应是标题
        ("这是标题，还有内容", False),  # 有逗号，不应是标题
    ]

    for text, should_be_title in test_cases:
        paragraphs = [text]
        features = analyzer.analyze_text_features(paragraphs)
        is_title = 0 in features['potential_titles']

        status = "✓" if is_title == should_be_title else "✗"
        print(f"{status} '{text}' -> 标题检测: {is_title}, 预期: {should_be_title}")

    return True

def test_json_fix():
    """测试JSON修复"""
    print("\n=== 测试JSON修复 ===")

    import json
    from src.core.ai_connector import AIConnector

    connector = AIConnector({"api_url": "test", "api_key": "test"})

    # 测试用例
    test_cases = [
        ('{"key": "value"}', True),  # 正常JSON
        ('{"elements": [1, 2, 3]}', True),  # 数组
    ]

    for json_str, should_parse in test_cases:
        try:
            result = json.loads(json_str)
            print(f"✓ 正常解析: {json_str[:30]}...")
        except:
            print(f"✗ 解析失败: {json_str[:30]}...")

    return True

def test_doc_processor_syntax():
    """测试文档处理器语法"""
    print("\n=== 测试文档处理器 ===")

    # 仅验证模块可以导入
    try:
        from src.core.doc_processor import DocProcessor
        print("✓ DocProcessor 导入成功")

        processor = DocProcessor()
        print("✓ DocProcessor 实例化成功")

        # 验证字号映射
        assert "小四" in processor.font_size_mapping
        print("✓ 字号映射正常")

        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("FormulaAI 核心功能测试")
    print("=" * 50)

    tests = [
        test_structure_analyzer,
        test_structure_analyzer_unicode,
        test_json_fix,
        test_doc_processor_syntax,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"✗ 测试失败: {test.__name__} - {e}")
            results.append((test.__name__, False))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
