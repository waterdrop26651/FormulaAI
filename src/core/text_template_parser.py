# -*- coding: utf-8 -*-
"""
DocumentBookTemplateParse器模块
负责ParseUser提供的Format要求DocumentBook，并生成结构化的FormattingTemplate。
"""

import re
import json
from ..utils.logger import app_logger
from .ai_connector import AIConnector

class TextTemplateParser:
    """DocumentBookTemplateParse器，负责ParseFormat要求DocumentBook并生成Template"""
    
    def __init__(self, ai_connector):
        """
        初始化DocumentBookTemplateParse器
        
        Args:
            ai_connector: AIJoin器Instance
        """
        self.ai_connector = ai_connector
        
        # CharacterNumberMappingTable
        self.font_size_mapping = {
            "初Number": "初Number",
            "Small初": "Small初", 
            "OneNumber": "OneNumber",
            "SmallOne": "SmallOne",
            "二Number": "二Number",
            "Small二": "Small二",
            "三Number": "三Number",
            "Small三": "Small三",
            "四Number": "四Number",
            "Small四": "Small四",
            "五Number": "五Number",
            "Small五": "Small五",
            "六Number": "六Number",
            "Small六": "Small六",
            "七Number": "七Number",
            "八Number": "八Number"
        }
        
        # 对齐方式Mapping
        self.alignment_mapping = {
            "居Center": "center",
            "Left对齐": "left", 
            "Right对齐": "right",
            "两端对齐": "justify",
            "center": "center",
            "left": "left",
            "right": "right",
            "justify": "justify"
        }
        
        app_logger.info("DocumentBookTemplateParse器初始化Complete")
    
    def parse_text_to_template(self, text_content, template_name="CustomTemplate", template_description="从DocumentBookParse生成的Template"):
        """
        ParseDocumentBookContent并生成Template
        
        Args:
            text_content: Format要求DocumentBookContent
            template_name: Template name
            template_description: Template描述
            
        Returns:
            (bool, dict/str): YesNoSuccess及TemplateContent/ErrorInformation
        """
        try:
            app_logger.info("StartParseDocumentBookFormat要求")
            
            # 生成AI提示Word
            prompt = self._generate_parsing_prompt(text_content)
            
            # 发送Request到AI
            success, response = self.ai_connector.send_request(prompt)
            
            if not success:
                app_logger.error(f"AIParseRequestFailed: {response}")
                return False, f"AIParseFailed: {response}"
            
            # ParseAIResponse
            success, template_rules = self._parse_ai_response(response)
            
            if not success:
                app_logger.error(f"ParseAIResponseFailed: {template_rules}")
                return False, f"ParseAIResponseFailed: {template_rules}"
            
            # 构建CompleteTemplate
            template = {
                "name": template_name,
                "description": template_description,
                "rules": template_rules
            }
            
            app_logger.info(f"SuccessParseDocumentBook，生成了 {len(template_rules)} 个FormatRule")
            return True, template
            
        except Exception as e:
            error_msg = f"ParseDocumentBookTime发生Abnormal: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
    
    def _generate_parsing_prompt(self, text_content):
        """
        生成用于ParseDocumentBook的AI提示Word
        
        Args:
            text_content: DocumentBookContent
            
        Returns:
            str: 生成的提示Word
        """
        prompt = f"""
你YesOne个专业的DocumentFormatParse助手。请Analyze以DownDocumentBookCenter的Format要求，提取出所Has的FormattingRule，并Conversion为结构化的JSONFormat。

DocumentBookContent：
<text>
{text_content}
</text>

请仔细AnalyzeDocumentBookCenter提到的所HasFormat要求，包括但不限于：
1. 标题Format（Font、CharacterNumber、对齐方式、粗体等）
2. 正DocumentFormat（Font、CharacterNumber、LineBetween距等）
3. 摘要Format
4. KeyWordFormat
5. 参考Document献Format
6. 图TableFormat
7. 其他SpecialElementFormat

注意事Item：
1. Font名称请UseStandardCenterDocumentFont名称（如：宋体、Black体、楷体、仿宋等）
2. CharacterNumber请UseCenterDocumentCharacterNumber（如：Small二、三Number、四Number、Small四、五Number等）
3. 对齐方式请Use：居Center、Left对齐、Right对齐、两端对齐
4. LineBetween距请Use数Value（如：1.5、1.25、2.0等）
5. 粗体请UseBooleanValue：true或false

请以JSONFormatReturnFormattingRule，Format如Down：
{{
  "论Document题目": {{
    "font": "Black体",
    "size": "四Number",
    "bold": true,
    "alignment": "center",
    "line_spacing": 1.5
  }},
  "OneLevel标题": {{
    "font": "Black体",
    "size": "四Number",
    "bold": true,
    "alignment": "center",
    "line_spacing": 1.5
  }},
  "二Level标题": {{
    "font": "宋体",
    "size": "Small四",
    "bold": true,
    "alignment": "left",
    "line_spacing": 1.25
  }},
  "正Document": {{
    "font": "宋体",
    "size": "Small四",
    "bold": false,
    "alignment": "left",
    "line_spacing": 1.25
  }}
}}

只ReturnJSONContent，不要Has其他说明DocumentCharacter。
"""
        
        app_logger.debug(f"生成的Parse提示WordLength: {len(prompt)} Character符")
        return prompt
    
    def _parse_ai_response(self, response):
        """
        ParseAIResponse并提取TemplateRule
        
        Args:
            response: AIResponseContent
            
        Returns:
            (bool, dict/str): YesNoSuccess及RuleDictionary/ErrorInformation
        """
        try:
            # 从ResponseCenter提取Content
            if isinstance(response, dict):
                if "choices" in response and len(response["choices"]) > 0:
                    content = response["choices"][0]["message"]["content"]
                else:
                    return False, "AIResponseFormatError：缺少choicesField"
            else:
                content = str(response)
            
            app_logger.debug(f"AIResponseContent: {content[:200]}...")
            
            # 尝试提取JSONContent
            json_str = self._extract_json_from_content(content)
            
            # 清理JSONString
            json_str = self._clean_json_string(json_str)
            
            # ParseJSON
            try:
                app_logger.debug(f"准备ParseJSON: {json_str[:500]}...")
                rules = json.loads(json_str)
                app_logger.info(f"SuccessParseAIResponse，提取了 {len(rules)} 个Rule")
                
                # RecordParse出的Rule
                app_logger.debug(f"Parse出的CompleteRule结构: {rules}")
                for rule_name, rule_content in rules.items():
                    app_logger.debug(f"Parse出Rule: {rule_name} -> {rule_content} (Type: {type(rule_content)})")
                
                # Validate和Standard化Rule
                normalized_rules = self._normalize_rules(rules)
                app_logger.info(f"Standard化Next的RuleQuantity: {len(normalized_rules)}")
                
                return True, normalized_rules
                
            except json.JSONDecodeError as e:
                app_logger.error(f"JSONParseFailed: {str(e)}")
                app_logger.error(f"尝试Parse的JSON: {json_str}")
                
                # 尝试修复Common的JSONFormat问题
                fixed_json = self._try_fix_json(json_str)
                if fixed_json != json_str:
                    try:
                        app_logger.info("尝试Use修复Next的JSON")
                        rules = json.loads(fixed_json)
                        normalized_rules = self._normalize_rules(rules)
                        return True, normalized_rules
                    except json.JSONDecodeError:
                        pass
                
                return False, f"JSONFormatError: {str(e)}"
                
        except Exception as e:
            app_logger.error(f"ParseAIResponseTime发生Abnormal: {str(e)}")
            return False, f"ParseAbnormal: {str(e)}"
    
    def _extract_json_from_content(self, content):
        """
        从AIResponseContentCenter提取JSONString
        
        Args:
            content: AIResponseContent
            
        Returns:
            str: 提取的JSONString
        """
        # Method1: 寻找Complete的JSONObject（支持嵌Set）
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
                    # 找到Complete的JSONObject
                    json_str = content[start_pos:i+1]
                    app_logger.debug(f"提取的JSONLength: {len(json_str)} Character符")
                    return json_str
        
        # Method2: If没Has找到CompleteJSON，尝试正RuleMatch
        json_patterns = [
            r'\{[\s\S]*?\}',  # Match最OuterLayerBig括Number
            r'```json\s*([\s\S]*?)```',  # Matchmarkdown代Yard块
            r'```\s*([\s\S]*?)```'  # MatchOrdinary代Yard块
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                if len(match.groups()) > 0:
                    json_str = match.group(1).strip()
                else:
                    json_str = match.group(0).strip()
                
                # ValidateYesNoContainsJSON结构
                if '{' in json_str and '}' in json_str:
                    app_logger.debug(f"Through正Rule提取JSON，Length: {len(json_str)} Character符")
                    return json_str
        
        # Method3: If都没找到，ReturnEntireContent
        app_logger.warning("未找到明确的JSON结构，UseEntireResponseContent")
        return content.strip()
    
    def _clean_json_string(self, json_str):
        """
        清理JSONString
        
        Args:
            json_str: 原始JSONString
            
        Returns:
            str: 清理Next的JSONString
        """
        # Remove可能的markdown代Yard块标记
        json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'^```\s*$', '', json_str, flags=re.MULTILINE)
        
        # RemoveMultiple余的SpaceBlankCharacter符
        json_str = json_str.strip()
        
        return json_str
    
    def _try_fix_json(self, json_str):
        """
        尝试修复Common的JSONFormat问题
        
        Args:
            json_str: 原始JSONString
            
        Returns:
            str: 修复Next的JSONString
        """
        # Remove可能的PreviousNext缀DocumentBook
        json_str = json_str.strip()
        
        # 查找第One个 { 和最NextOne个 }
        start = json_str.find('{')
        end = json_str.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = json_str[start:end+1]
        
        # 修复Common的Format问题
        fixes = [
            # 修复单引Number为双引Number
            (r"'([^']*)'\s*:", r'"\1":'),
            (r":\s*'([^']*)'", r': "\1"'),
            # 修复缺少引Number的键
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":'),
            # 修复尾随逗Number
            (r',\s*}', '}'),
            (r',\s*]', ']'),
        ]
        
        for pattern, replacement in fixes:
            json_str = re.sub(pattern, replacement, json_str)
        
        app_logger.debug(f"JSON修复Next: {json_str[:200]}...")
        return json_str
    
    def _normalize_rules(self, rules):
        """
        Standard化RuleFormat
        
        Args:
            rules: 原始RuleDictionary
            
        Returns:
            dict: Standard化Next的RuleDictionary
        """
        normalized = {}
        
        for element_type, rule in rules.items():
            if not isinstance(rule, dict):
                app_logger.warning(f"SkipInvalidRule: {element_type}")
                continue
            
            normalized_rule = {
                "font": rule.get("font", "宋体"),
                "size": rule.get("size", "五Number"),
                "bold": bool(rule.get("bold", False)),
                "line_spacing": float(rule.get("line_spacing", 1.5)),
                "alignment": self.alignment_mapping.get(rule.get("alignment", "left"), "left")
            }
            
            # ValidateCharacterNumber
            if normalized_rule["size"] not in self.font_size_mapping:
                app_logger.warning(f"未知CharacterNumber '{normalized_rule['size']}'，UseDefaultValue'五Number'")
                normalized_rule["size"] = "五Number"
            
            normalized[element_type] = normalized_rule
            app_logger.debug(f"Standard化Rule: {element_type} -> {normalized_rule}")
        
        return normalized