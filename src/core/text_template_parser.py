# -*- coding: utf-8 -*-
"""
文本模板解析器模块
负责解析用户提供的格式要求文本，并生成结构化的排版模板。
"""

import re
import json
from ..utils.logger import app_logger
from .ai_connector import AIConnector

class TextTemplateParser:
    """文本模板解析器，负责解析格式要求文本并生成模板"""
    
    def __init__(self, ai_connector):
        """
        初始化文本模板解析器
        
        Args:
            ai_connector: AI连接器实例
        """
        self.ai_connector = ai_connector
        
        # 字号映射表
        self.font_size_mapping = {
            "初号": "初号",
            "小初": "小初", 
            "一号": "一号",
            "小一": "小一",
            "二号": "二号",
            "小二": "小二",
            "三号": "三号",
            "小三": "小三",
            "四号": "四号",
            "小四": "小四",
            "五号": "五号",
            "小五": "小五",
            "六号": "六号",
            "小六": "小六",
            "七号": "七号",
            "八号": "八号"
        }
        
        # 对齐方式映射
        self.alignment_mapping = {
            "居中": "center",
            "左对齐": "left", 
            "右对齐": "right",
            "两端对齐": "justify",
            "center": "center",
            "left": "left",
            "right": "right",
            "justify": "justify"
        }
        
        app_logger.info("文本模板解析器初始化完成")
    
    def parse_text_to_template(self, text_content, template_name="自定义模板", template_description="从文本解析生成的模板"):
        """
        解析文本内容并生成模板
        
        Args:
            text_content: 格式要求文本内容
            template_name: 模板名称
            template_description: 模板描述
            
        Returns:
            (bool, dict/str): 是否成功及模板内容/错误信息
        """
        try:
            app_logger.info("开始解析文本格式要求")
            
            # 生成AI提示词
            prompt = self._generate_parsing_prompt(text_content)
            
            # 发送请求到AI
            success, response = self.ai_connector.send_request(prompt)
            
            if not success:
                app_logger.error(f"AI解析请求失败: {response}")
                return False, f"AI解析失败: {response}"
            
            # 解析AI响应
            success, template_rules = self._parse_ai_response(response)
            
            if not success:
                app_logger.error(f"解析AI响应失败: {template_rules}")
                return False, f"解析AI响应失败: {template_rules}"
            
            # 构建完整模板
            template = {
                "name": template_name,
                "description": template_description,
                "rules": template_rules
            }
            
            app_logger.info(f"成功解析文本，生成了 {len(template_rules)} 个格式规则")
            return True, template
            
        except Exception as e:
            error_msg = f"解析文本时发生异常: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
    
    def _generate_parsing_prompt(self, text_content):
        """
        生成用于解析文本的AI提示词
        
        Args:
            text_content: 文本内容
            
        Returns:
            str: 生成的提示词
        """
        prompt = f"""
你是一个专业的文档格式解析助手。请分析以下文本中的格式要求，提取出所有的排版规则，并转换为结构化的JSON格式。

文本内容：
<text>
{text_content}
</text>

请仔细分析文本中提到的所有格式要求，包括但不限于：
1. 标题格式（字体、字号、对齐方式、粗体等）
2. 正文格式（字体、字号、行间距等）
3. 摘要格式
4. 关键词格式
5. 参考文献格式
6. 图表格式
7. 其他特殊元素格式

注意事项：
1. 字体名称请使用标准中文字体名称（如：宋体、黑体、楷体、仿宋等）
2. 字号请使用中文字号（如：小二、三号、四号、小四、五号等）
3. 对齐方式请使用：居中、左对齐、右对齐、两端对齐
4. 行间距请使用数值（如：1.5、1.25、2.0等）
5. 粗体请使用布尔值：true或false

请以JSON格式返回排版规则，格式如下：
{{
  "论文题目": {{
    "font": "黑体",
    "size": "四号",
    "bold": true,
    "alignment": "center",
    "line_spacing": 1.5
  }},
  "一级标题": {{
    "font": "黑体",
    "size": "四号",
    "bold": true,
    "alignment": "center",
    "line_spacing": 1.5
  }},
  "二级标题": {{
    "font": "宋体",
    "size": "小四",
    "bold": true,
    "alignment": "left",
    "line_spacing": 1.25
  }},
  "正文": {{
    "font": "宋体",
    "size": "小四",
    "bold": false,
    "alignment": "left",
    "line_spacing": 1.25
  }}
}}

只返回JSON内容，不要有其他说明文字。
"""
        
        app_logger.debug(f"生成的解析提示词长度: {len(prompt)} 字符")
        return prompt
    
    def _parse_ai_response(self, response):
        """
        解析AI响应并提取模板规则
        
        Args:
            response: AI响应内容
            
        Returns:
            (bool, dict/str): 是否成功及规则字典/错误信息
        """
        try:
            # 从响应中提取内容
            if isinstance(response, dict):
                if "choices" in response and len(response["choices"]) > 0:
                    content = response["choices"][0]["message"]["content"]
                else:
                    return False, "AI响应格式错误：缺少choices字段"
            else:
                content = str(response)
            
            app_logger.debug(f"AI响应内容: {content[:200]}...")
            
            # 尝试提取JSON内容
            json_str = self._extract_json_from_content(content)
            
            # 清理JSON字符串
            json_str = self._clean_json_string(json_str)
            
            # 解析JSON
            try:
                app_logger.debug(f"准备解析JSON: {json_str[:500]}...")
                rules = json.loads(json_str)
                app_logger.info(f"成功解析AI响应，提取了 {len(rules)} 个规则")
                
                # 记录解析出的规则
                app_logger.debug(f"解析出的完整规则结构: {rules}")
                for rule_name, rule_content in rules.items():
                    app_logger.debug(f"解析出规则: {rule_name} -> {rule_content} (类型: {type(rule_content)})")
                
                # 验证和标准化规则
                normalized_rules = self._normalize_rules(rules)
                app_logger.info(f"标准化后的规则数量: {len(normalized_rules)}")
                
                return True, normalized_rules
                
            except json.JSONDecodeError as e:
                app_logger.error(f"JSON解析失败: {str(e)}")
                app_logger.error(f"尝试解析的JSON: {json_str}")
                
                # 尝试修复常见的JSON格式问题
                fixed_json = self._try_fix_json(json_str)
                if fixed_json != json_str:
                    try:
                        app_logger.info("尝试使用修复后的JSON")
                        rules = json.loads(fixed_json)
                        normalized_rules = self._normalize_rules(rules)
                        return True, normalized_rules
                    except json.JSONDecodeError:
                        pass
                
                return False, f"JSON格式错误: {str(e)}"
                
        except Exception as e:
            app_logger.error(f"解析AI响应时发生异常: {str(e)}")
            return False, f"解析异常: {str(e)}"
    
    def _extract_json_from_content(self, content):
        """
        从AI响应内容中提取JSON字符串
        
        Args:
            content: AI响应内容
            
        Returns:
            str: 提取的JSON字符串
        """
        # 方法1: 寻找完整的JSON对象（支持嵌套）
        brace_count = 0
        start_pos = -1
        
        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    start_pos = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_pos != -1:
                    # 找到完整的JSON对象
                    json_str = content[start_pos:i+1]
                    app_logger.debug(f"提取的JSON长度: {len(json_str)} 字符")
                    return json_str
        
        # 方法2: 如果没有找到完整JSON，尝试正则匹配
        json_patterns = [
            r'\{[\s\S]*?\}',  # 匹配最外层大括号
            r'```json\s*([\s\S]*?)```',  # 匹配markdown代码块
            r'```\s*([\s\S]*?)```'  # 匹配普通代码块
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                if len(match.groups()) > 0:
                    json_str = match.group(1).strip()
                else:
                    json_str = match.group(0).strip()
                
                # 验证是否包含JSON结构
                if '{' in json_str and '}' in json_str:
                    app_logger.debug(f"通过正则提取JSON，长度: {len(json_str)} 字符")
                    return json_str
        
        # 方法3: 如果都没找到，返回整个内容
        app_logger.warning("未找到明确的JSON结构，使用整个响应内容")
        return content.strip()
    
    def _clean_json_string(self, json_str):
        """
        清理JSON字符串
        
        Args:
            json_str: 原始JSON字符串
            
        Returns:
            str: 清理后的JSON字符串
        """
        # 移除可能的markdown代码块标记
        json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'^```\s*$', '', json_str, flags=re.MULTILINE)
        
        # 移除多余的空白字符
        json_str = json_str.strip()
        
        return json_str
    
    def _try_fix_json(self, json_str):
        """
        尝试修复常见的JSON格式问题
        
        Args:
            json_str: 原始JSON字符串
            
        Returns:
            str: 修复后的JSON字符串
        """
        # 移除可能的前后缀文本
        json_str = json_str.strip()
        
        # 查找第一个 { 和最后一个 }
        start = json_str.find('{')
        end = json_str.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = json_str[start:end+1]
        
        # 修复常见的格式问题
        fixes = [
            # 修复单引号为双引号
            (r"'([^']*)'\s*:", r'"\1":'),
            (r":\s*'([^']*)'", r': "\1"'),
            # 修复缺少引号的键
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":'),
            # 修复尾随逗号
            (r',\s*}', '}'),
            (r',\s*]', ']'),
        ]
        
        for pattern, replacement in fixes:
            json_str = re.sub(pattern, replacement, json_str)
        
        app_logger.debug(f"JSON修复后: {json_str[:200]}...")
        return json_str
    
    def _normalize_rules(self, rules):
        """
        标准化规则格式
        
        Args:
            rules: 原始规则字典
            
        Returns:
            dict: 标准化后的规则字典
        """
        normalized = {}
        
        for element_type, rule in rules.items():
            if not isinstance(rule, dict):
                app_logger.warning(f"跳过无效规则: {element_type}")
                continue
            
            normalized_rule = {
                "font": rule.get("font", "宋体"),
                "size": rule.get("size", "五号"),
                "bold": bool(rule.get("bold", False)),
                "line_spacing": float(rule.get("line_spacing", 1.5)),
                "alignment": self.alignment_mapping.get(rule.get("alignment", "left"), "left")
            }
            
            # 验证字号
            if normalized_rule["size"] not in self.font_size_mapping:
                app_logger.warning(f"未知字号 '{normalized_rule['size']}'，使用默认值'五号'")
                normalized_rule["size"] = "五号"
            
            normalized[element_type] = normalized_rule
            app_logger.debug(f"标准化规则: {element_type} -> {normalized_rule}")
        
        return normalized