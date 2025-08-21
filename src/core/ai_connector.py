# -*- coding: utf-8 -*-
"""
AIInterfaceJoin器模块
负责与AI API通信，发送Request和ProcessResponse。
"""

import json
import requests
from ..utils.logger import app_logger

class AIConnector:
    """AIInterfaceJoin器，负责与AI API通信"""
    
    def __init__(self, api_config):
        """
        初始化Join器
        
        Args:
            api_config: APIConfigurationInformation，Containsapi_url, api_key, model, timeout等
        """
        self.api_url = api_config.get("api_url", "")
        self.api_key = api_config.get("api_key", "")
        self.model = api_config.get("model", "deepseek-chat")
        # SetTimeoutTime，Default300Second（5Minute），可ThroughConfigurationFile调整
        self.timeout = api_config.get("timeout", 300)
        
        app_logger.info(f"AIJoin器初始化Complete，UseModel: {self.model}，TimeoutTime: {self.timeout}Second")
    
    def validate_config(self):
        """
        ValidateAPIConfigurationYesNoValid
        
        Returns:
            (bool, str): YesNoValid及ErrorInformation
        """
        if not self.api_url:
            return False, "API URL不能为Space"
        
        if not self.api_key:
            return False, "API Key不能为Space"
        
        if not self.model:
            return False, "Model名称不能为Space"
        
        # 尝试发送TestRequest
        try:
            response = self._send_test_request()
            if response.status_code == 200:
                app_logger.info("APIConfigurationValidateSuccess")
                return True, "APIConfigurationValidateSuccess"
            else:
                error_msg = f"APIRequestFailed，StatusYard: {response.status_code}, Response: {response.text}"
                app_logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"APIRequestAbnormal: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
    
    def _send_test_request(self):
        """
        发送TestRequest以ValidateAPIConfiguration
        
        Returns:
            requests.Response: ResponseObject
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ],
            "stream": False
        }
        
        return requests.post(self.api_url, headers=headers, json=data, timeout=self.timeout)
    
    def generate_prompt(self, document_content, formatting_rules):
        """
        生成AI提示Word
        
        Args:
            document_content: DocumentContentList，EachElement为One个Paragraph
            formatting_rules: FormattingRule
            
        Returns:
            str: 生成的提示Word
        """
        # 将DocumentContentListConversion为DocumentBook
        doc_text = "\n\n".join(document_content)
        
        # 将FormattingRuleConversion为DocumentBook
        rules_text = json.dumps(formatting_rules, ensure_ascii=False, indent=2)
        
        # 构建提示Word
        prompt = f"""
你YesOne个专业的DocumentFormatting助手。请Analyze以Down未经Formatting的DocumentContent（AllUseDefault正DocumentFormat），Through语义理解识别其Center的结构Element（如标题、摘要、正Document、KeyWord等），并严格按照提供的FormattingRule，Return详细的Formatting指令。

DocumentContent：
<doc>
{doc_text}
</doc>

FormattingRule：
<rules>
{rules_text}
</rules>

请特别注意：
1. Document没Has任何预先Formatting，所HasContent都UseSame的DefaultFormat
2. 需要ThroughContent语义来判断每PhaseDocumentCharacter的结构角色（如标题、Small标题、摘要、正Document等）
3. 标题Usually简Short、概括性Strong，且可能没Has标Point符Number
4. WhenDocumentCenter出现"摘要"标题Next的Paragraph，应识别为"摘要"Type，而非"正Document"Type
5. WhenDocumentCenter出现"KeyWord"Beginning的Paragraph，应识别为"KeyWord"Type
6. 请识别出Document的LayerLevel结构，包括标题、Small标题、摘要、KeyWord、正Document等
7. 必须严格按照提供的FormattingRuleCenter的FontSettings，不要自LineReplace或ModifyFont
8. 对于学术论DocumentFormat，请特别注意正确识别摘要、KeyWord、参考Document献等SpecialPart
9. IfFormattingRuleCenterContains对齐方式(alignment)Settings，必须Application到相应的ElementCenter
10. **Important：必须为EachElementSettingsComplete的FormatProperty，包括：**
    - 标题ClassElement（标题、OneLevel标题、二Level标题等）：必须Settings "bold": true
    - 正DocumentClassElement（正Document、摘要等）：必须Settings "bold": false
    - 所HasElement都必须Contains font、size、bold、line_spacing、alignment 等CompleteProperty
    - 不要遗漏任何FormatProperty，确保生成的Format指令CompleteAvailable

请以JSONFormatReturnFormatting指令，Format如Down：
{{
  "elements": [
{{
  "type": "标题",
  "content": "DocumentBookContent",
  "format": {{
    "font": "Black体",
    "size": "Small二",
    "bold": true,
    "line_spacing": 1.0,
    "alignment": "center"
  }}
}},
{{
  "type": "OneLevel标题",
  "content": "Chapter标题",
  "format": {{
    "font": "Black体",
    "size": "三Number",
    "bold": true,
    "line_spacing": 1.5,
    "alignment": "left"
  }}
}},
{{
  "type": "正Document",
  "content": "正DocumentContent",
  "format": {{
    "font": "宋体",
    "size": "Small四",
    "bold": false,
    "line_spacing": 1.5,
    "alignment": "justify"
  }}
}},
...
  ]
}}

请确保Return的JSONFormat正确，可以被Parse。只ReturnJSONContent，不要Has其他说明DocumentCharacter。
"""
        
        # RecordDocumentLength和RuleQuantity
        doc_length = len(doc_text)
        rules_count = len(formatting_rules) if isinstance(formatting_rules, dict) else 0
        app_logger.debug(f"DocumentLength: {doc_length} Character符, RuleQuantity: {rules_count}")
        
        # RecordComplete提示Word
        app_logger.debug(f"生成的提示WordLength: {len(prompt)} Character符")
        
        # Record提示Word的Previous200个Character符和Next200个Character符，方便Debug
        prompt_start = prompt[:200] + "..." if len(prompt) > 200 else prompt
        prompt_end = "..." + prompt[-200:] if len(prompt) > 200 else prompt
        app_logger.debug(f"提示WordBeginning: {prompt_start}")
        app_logger.debug(f"提示WordEnd: {prompt_end}")
        
        app_logger.debug("生成AI提示WordComplete")
        return prompt
    
    def send_request(self, prompt):
        """
        发送Request到AI API
        
        Args:
            prompt: 提示Word
            
        Returns:
            (bool, dict/str): YesNoSuccess及ResponseContent/ErrorInformation
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        # RecordRequest详情
        app_logger.info(f"发送Request到AI API: {self.api_url}")
        app_logger.debug(f"Request头Information: {headers}")
        
        # Record提示Word的Previous200个Character符，避免Log过Big
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        app_logger.debug(f"提示WordPreview: {prompt_preview}")
        
        # RecordModelParameters
        app_logger.debug(f"UseModel: {self.model}")
        
        try:
            app_logger.info(f"Start发送Request，TimeoutTimeSettings为{self.timeout}Second")
            # UseConfiguration的TimeoutTime，给API更MultipleProcessTime
            response = requests.post(self.api_url, headers=headers, json=data, timeout=self.timeout)
            
            # RecordResponseStatus和Time
            app_logger.info(f"收到Response，StatusYard: {response.status_code}")
            
            if response.status_code == 200:
                app_logger.info("AI APIRequestSuccess")
                
                # ParseResponseJSON
                response_json = response.json()
                
                # RecordResponse的Basic结构（不ContainsCompleteContent）
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    first_choice = response_json["choices"][0]
                    if "message" in first_choice and "content" in first_choice["message"]:
                        content = first_choice["message"]["content"]
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                        app_logger.debug(f"ResponseContentPreview: {content_preview}")
                
                # RecordResponse的其他元Data
                if "model" in response_json:
                    app_logger.debug(f"ResponseUse的Model: {response_json['model']}")
                if "usage" in response_json:
                    app_logger.debug(f"令牌Use情况: {response_json['usage']}")
                
                return True, response_json
            else:
                # RecordFailedResponse的CompleteContent
                error_msg = f"AI APIRequestFailed，StatusYard: {response.status_code}"
                app_logger.error(error_msg)
                app_logger.error(f"ErrorResponseContent: {response.text}")
                return False, error_msg
        except Exception as e:
            error_msg = f"AI APIRequestAbnormal: {str(e)}"
            app_logger.error(error_msg)
            
            # RecordAbnormalTime的Request详情，方便Debug
            app_logger.debug(f"AbnormalTime的RequestData: {data}")
            
            # IfYesTimeoutAbnormal，提供更MultipleInformation
            if "timeout" in str(e).lower():
                app_logger.error(f"RequestTimeout，WhenPreviousTimeoutSettings为{self.timeout}Second，可能需要增加TimeoutTime或Optimization提示Word")
            
            return False, error_msg
    
    def _fix_json(self, json_str):
        """
        尝试修复JSONFormatError
        
        Args:
            json_str: 需要修复的JSONString
            
        Returns:
            str: 修复Next的JSONString
        """
        app_logger.debug("Start修复JSONFormat")
        
        # 修复1: ProcessArray最NextOne个ElementNext的逗Number问题
        # 查找所Has可能的Array结束Position
        array_end_positions = []
        i = 0
        while i < len(json_str) - 1:
            if json_str[i:i+2] == "},":
                # 往Next找到DownOne个非SpaceBlankCharacter符
                j = i + 2
                while j < len(json_str) and json_str[j].isspace():
                    j += 1
                
                # IfDownOne个非SpaceBlankCharacter符YesRight方括Number，Rule可能YesArray结束
                if j < len(json_str) and json_str[j] == "]":
                    array_end_positions.append(i)
            i += 1
        
        # Process可能的ErrorPosition
        for pos in array_end_positions:
            # CreateOne个New的JSONString，将逗NumberReplace为Space格
            fixed = json_str[:pos] + "} " + json_str[pos+2:]
            try:
                # 尝试Parse修复Next的JSON
                json.loads(fixed)
                app_logger.info(f"Success修复ArrayElementNext的逗Number问题，Position: {pos}")
                return fixed
            except json.JSONDecodeError:
                # If仍然NoneLawParse，尝试DownOne个Position
                pass
        
        # 修复2: Process缺少逗Number的问题
        # 查找所Has可能缺少逗Number的Position
        missing_comma_positions = []
        i = 0
        while i < len(json_str) - 1:
            if json_str[i] == "}" and json_str[i+1] == "{":
                missing_comma_positions.append(i + 1)
            i += 1
        
        # Process可能的ErrorPosition
        for pos in missing_comma_positions:
            # CreateOne个New的JSONString，Add缺失的逗Number
            fixed = json_str[:pos] + "," + json_str[pos:]
            try:
                # 尝试Parse修复Next的JSON
                json.loads(fixed)
                app_logger.info(f"Success修复缺少逗Number问题，Position: {pos}")
                return fixed
            except json.JSONDecodeError:
                # If仍然NoneLawParse，尝试DownOne个Position
                pass
        
        # 修复3: ProcessJSON不Complete的问题
        # CheckJSONYesNo不Complete（缺少Right花括Number或Right方括Number）
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        open_brackets = json_str.count("[")
        close_brackets = json_str.count("]")
        
        if open_braces > close_braces:
            # 缺少Right花括Number，Add缺失的Right花括Number
            missing = open_braces - close_braces
            fixed = json_str + "}" * missing
            app_logger.info(f"Add {missing} 个缺失的Right花括Number")
            try:
                json.loads(fixed)
                return fixed
            except json.JSONDecodeError:
                # If仍然NoneLawParse，尝试DownOne个修复Method
                pass
        
        if open_brackets > close_brackets:
            # 缺少Right方括Number，Add缺失的Right方括Number
            missing = open_brackets - close_brackets
            fixed = json_str + "]" * missing
            app_logger.info(f"Add {missing} 个缺失的Right方括Number")
            try:
                json.loads(fixed)
                return fixed
            except json.JSONDecodeError:
                # If仍然NoneLawParse，尝试DownOne个修复Method
                pass
        
        # 修复4: Process特定Error - WhenPreviousErrorYes缺少逗Number
        # 尝试InEach可能的PositionAdd逗Number
        for i in range(len(json_str)-1):
            if (json_str[i] == "}" and json_str[i+1] == "{"
                or json_str[i] == "]" and json_str[i+1] == "["
                or json_str[i] == "}" and json_str[i+1] == "["
                or json_str[i] == "]" and json_str[i+1] == "{"
            ):
                fixed = json_str[:i+1] + "," + json_str[i+1:]
                try:
                    json.loads(fixed)
                    app_logger.info(f"Success修复缺少逗Number问题，Position: {i+1}")
                    return fixed
                except json.JSONDecodeError:
                    pass
        
        # 修复5: If所Has修复Method都Failed，尝试修复最NextOne个Element
        # 找到最NextOne个Element的结束Position
        last_element_end = json_str.rfind("}}")
        if last_element_end > 0:
            # 尝试截取到最NextOne个Element结束并Add必要的结束括Number
            fixed = json_str[:last_element_end+2] + "]}"
            try:
                json.loads(fixed)
                app_logger.info("Success修复最NextOne个Element并Add结束括Number")
                return fixed
            except json.JSONDecodeError:
                pass
        
        # If所Has修复Method都Failed，Return原始JSON
        app_logger.warning("NoneLaw修复JSONFormat，Return原始String")
        return json_str
    
    def parse_response(self, response):
        """
        ParseAIResponse
        
        Args:
            response: AI API的ResponseContent
            
        Returns:
            (bool, dict/str): YesNoSuccess及ParseResult/ErrorInformation
        """
        try:
            # RecordCompleteResponse结构
            app_logger.debug(f"ResponseComplete结构的键: {list(response.keys()) if isinstance(response, dict) else '非DictionaryType'}")
            
            # RecordUse情况
            if isinstance(response, dict) and "usage" in response:
                usage = response["usage"]
                app_logger.debug(f"令牌Use情况: {usage}")
            
            # 从ResponseCenter提取contentContent
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                error_msg = "AIResponseContent为Space"
                app_logger.error(error_msg)
                return False, error_msg
            
            # Record原始ResponseContent的Length
            app_logger.debug(f"原始ResponseContentLength: {len(content)} Character符")
            
            # RecordResponseContent的Previous200个Character符和Next200个Character符
            content_start = content[:200] + "..." if len(content) > 200 else content
            content_end = "..." + content[-200:] if len(content) > 200 else content
            app_logger.debug(f"ResponseContentBeginning: {content_start}")
            app_logger.debug(f"ResponseContentEnd: {content_end}")
            
            # 尝试ParseJSONContent
            # HasTimeAI可能会InJSONPreviousNextAdd额OuterDocumentBook，需要提取JSONPart
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            app_logger.debug(f"JSONContent起始Position: {json_start}, 结束Position: {json_end}")
            
            if json_start >= 0 and json_end >= 0:
                json_content = content[json_start:json_end+1]
                app_logger.debug(f"提取的JSONContentLength: {len(json_content)} Character符")
                app_logger.debug(f"JSONContentPrevious50个Character符: {json_content[:50]}...")
                
                try:
                    # 尝试修复JSONFormatError
                    try:
                        formatting_instructions = json.loads(json_content)
                    except json.JSONDecodeError as e:
                        app_logger.warning(f"原始JSONParseFailed，尝试修复: {str(e)}")
                        
                        # 尝试修复Common的JSONError
                        fixed_json = self._fix_json(json_content)
                        app_logger.debug(f"尝试修复Next的JSONContentLength: {len(fixed_json)} Character符")
                        app_logger.debug(f"修复Next的JSONContentPrevious50个Character符: {fixed_json[:50]}...")
                        
                        try:
                            formatting_instructions = json.loads(fixed_json)
                            app_logger.info("JSON修复Success，ParseComplete")
                        except json.JSONDecodeError as e2:
                            app_logger.error(f"修复Next的JSON仍然NoneLawParse: {str(e2)}")
                            raise e  # 抛出原始Abnormal
                    
                    # ValidateFormat指令的结构
                    if not isinstance(formatting_instructions, dict):
                        app_logger.error(f"Formatting指令不YesDictionaryType: {type(formatting_instructions)}")
                        return False, "ResponseFormatError: Formatting指令应为DictionaryType"
                    
                    if 'elements' not in formatting_instructions:
                        app_logger.error("Formatting指令缺少elementsField")
                        return False, "ResponseFormatError: 缺少elementsField"
                    
                    elements = formatting_instructions['elements']
                    if not isinstance(elements, list):
                        app_logger.error(f"elements不YesListType: {type(elements)}")
                        return False, "ResponseFormatError: elements应为ListType"
                    
                    # ValidateEachElement
                    for i, element in enumerate(elements):
                        if not isinstance(element, dict):
                            app_logger.error(f"Element {i} 不YesDictionaryType: {type(element)}")
                            return False, f"ResponseFormatError: Element {i} 应为DictionaryType"
                        
                        if 'type' not in element:
                            app_logger.error(f"Element {i} 缺少typeField")
                            return False, f"ResponseFormatError: Element {i} 缺少typeField"
                        
                        if 'content' not in element:
                            app_logger.error(f"Element {i} 缺少contentField")
                            return False, f"ResponseFormatError: Element {i} 缺少contentField"
                        
                        if 'format' not in element:
                            app_logger.error(f"Element {i} 缺少formatField")
                            return False, f"ResponseFormatError: Element {i} 缺少formatField"
                    
                    app_logger.debug(f"JSONParseSuccess，得到DictionaryTypeData")
                    
                    # RecordParseNext的Data结构
                    if isinstance(formatting_instructions, dict):
                        app_logger.debug(f"Format指令的键: {list(formatting_instructions.keys())}")
                        
                        # CheckElementQuantity
                        elements = formatting_instructions.get('elements', [])
                        if isinstance(elements, list):
                            app_logger.debug(f"ElementQuantity: {len(elements)}")
                            
                            # RecordPrevious三个Element的Type
                            element_types = [element.get('type', '未知') for element in elements[:3]]
                            app_logger.debug(f"Previous三个ElementType: {element_types}")
                    
                    return True, formatting_instructions
                except json.JSONDecodeError as e:
                    error_msg = f"JSONParseFailed: {str(e)}"
                    app_logger.error(error_msg)
                    
                    # Record导致ParseFailed的JSONContent
                    problem_part = json_content[max(0, e.pos-50):min(len(json_content), e.pos+50)]
                    app_logger.error(f"ParseFailedPosition附Near的Content: ...{problem_part}...")
                    app_logger.error(f"ParseFailedPosition: {e.pos}, Line: {e.lineno}, Column: {e.colno}")
                    
                    return False, error_msg
            else:
                error_msg = "ResponseCenter未找到Valid的JSONContent"
                app_logger.error(error_msg)
                
                # RecordCompleteResponseContent，便于Debug
                app_logger.error(f"CompleteResponseContent: {content}")
                
                return False, error_msg
        except Exception as e:
            error_msg = f"ParseAIResponseAbnormal: {str(e)}"
            app_logger.error(error_msg)
            
            # RecordAbnormal详情
            import traceback
            app_logger.error(f"Abnormal详情: {traceback.format_exc()}")
            
            return False, error_msg
