# -*- coding: utf-8 -*-
"""
AI接口连接器模块
负责与AI API通信，发送请求和处理响应。
"""

import json
import requests

try:
    import json5
except ImportError:
    json5 = None

from ..utils.logger import app_logger

class AIConnector:
    """AI接口连接器，负责与AI API通信"""
    
    def __init__(self, api_config):
        """
        初始化连接器
        
        Args:
            api_config: API配置信息，包含api_url, api_key, model, timeout等
        """
        self.api_url = api_config.get("api_url", "")
        self.api_key = api_config.get("api_key", "")
        self.model = api_config.get("model", "deepseek-chat")
        # 设置超时时间，默认300秒（5分钟），可通过配置文件调整
        self.timeout = api_config.get("timeout", 300)
        
        app_logger.info(f"AI连接器初始化完成，使用模型: {self.model}，超时时间: {self.timeout}秒")
    
    def validate_config(self):
        """
        验证API配置是否有效
        
        Returns:
            (bool, str): 是否有效及错误信息
        """
        if not self.api_url:
            return False, "API URL不能为空"
        
        if not self.api_key:
            return False, "API Key不能为空"
        
        if not self.model:
            return False, "模型名称不能为空"
        
        # 尝试发送测试请求
        try:
            response = self._send_test_request()
            if response.status_code == 200:
                app_logger.info("API配置验证成功")
                return True, "API配置验证成功"
            else:
                error_msg = f"API请求失败，状态码: {response.status_code}, 响应: {response.text}"
                app_logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"API请求异常: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
    
    def _send_test_request(self):
        """
        发送测试请求以验证API配置
        
        Returns:
            requests.Response: 响应对象
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
        生成AI提示词
        
        Args:
            document_content: 文档内容列表，每个元素为一个段落
            formatting_rules: 排版规则
            
        Returns:
            str: 生成的提示词
        """
        # 将文档内容列表转换为文本
        doc_text = "\n\n".join(document_content)
        
        # 将排版规则转换为文本
        rules_text = json.dumps(formatting_rules, ensure_ascii=False, indent=2)
        
        # 构建提示词
        prompt = f"""
你是一个专业的文档排版助手。请分析以下未经排版的文档内容（全部使用默认正文格式），通过语义理解识别其中的结构元素（如标题、摘要、正文、关键词等），并严格按照提供的排版规则，返回详细的排版指令。

文档内容：
<doc>
{doc_text}
</doc>

排版规则：
<rules>
{rules_text}
</rules>

请特别注意：
1. 文档没有任何预先排版，所有内容都使用相同的默认格式
2. 需要通过内容语义来判断每段文字的结构角色（如标题、小标题、摘要、正文等）
3. 标题通常简短、概括性强，且可能没有标点符号
4. 当文档中出现"摘要"标题后的段落，应识别为"摘要"类型，而非"正文"类型
5. 当文档中出现"关键词"开头的段落，应识别为"关键词"类型
6. 请识别出文档的层级结构，包括标题、小标题、摘要、关键词、正文等
7. 必须严格按照提供的排版规则中的字体设置，不要自行替换或修改字体
8. 对于学术论文格式，请特别注意正确识别摘要、关键词、参考文献等特殊部分
9. 如果排版规则中包含对齐方式(alignment)设置，必须应用到相应的元素中
10. **重要：必须为每个元素设置完整的格式属性，包括：**
    - 标题类元素（标题、一级标题、二级标题等）：必须设置 "bold": true
    - 正文类元素（正文、摘要等）：必须设置 "bold": false
    - 所有元素都必须包含 font、size、bold、line_spacing、alignment 等完整属性
    - 不要遗漏任何格式属性，确保生成的格式指令完整可用

请以JSON格式返回排版指令，格式如下：
{{
  "elements": [
{{
  "type": "标题",
  "content": "文本内容",
  "format": {{
    "font": "黑体",
    "size": "小二",
    "bold": true,
    "line_spacing": 1.0,
    "alignment": "center"
  }}
}},
{{
  "type": "一级标题",
  "content": "章节标题",
  "format": {{
    "font": "黑体",
    "size": "三号",
    "bold": true,
    "line_spacing": 1.5,
    "alignment": "left"
  }}
}},
{{
  "type": "正文",
  "content": "正文内容",
  "format": {{
    "font": "宋体",
    "size": "小四",
    "bold": false,
    "line_spacing": 1.5,
    "alignment": "justify"
  }}
}},
...
  ]
}}

请确保返回的JSON格式正确，可以被解析。只返回JSON内容，不要有其他说明文字。
"""
        
        # 记录文档长度和规则数量
        doc_length = len(doc_text)
        rules_count = len(formatting_rules) if isinstance(formatting_rules, dict) else 0
        app_logger.debug(f"文档长度: {doc_length} 字符, 规则数量: {rules_count}")
        
        # 记录完整提示词
        app_logger.debug(f"生成的提示词长度: {len(prompt)} 字符")
        
        # 记录提示词的前200个字符和后200个字符，方便调试
        prompt_start = prompt[:200] + "..." if len(prompt) > 200 else prompt
        prompt_end = "..." + prompt[-200:] if len(prompt) > 200 else prompt
        app_logger.debug(f"提示词开头: {prompt_start}")
        app_logger.debug(f"提示词结尾: {prompt_end}")
        
        app_logger.debug("生成AI提示词完成")
        return prompt
    
    def send_request(self, prompt):
        """
        发送请求到AI API
        
        Args:
            prompt: 提示词
            
        Returns:
            (bool, dict/str): 是否成功及响应内容/错误信息
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
        
        # 记录请求详情
        app_logger.info(f"发送请求到AI API: {self.api_url}")
        app_logger.debug(f"请求头信息: {headers}")
        
        # 记录提示词的前200个字符，避免日志过大
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        app_logger.debug(f"提示词预览: {prompt_preview}")
        
        # 记录模型参数
        app_logger.debug(f"使用模型: {self.model}")
        
        try:
            app_logger.info(f"开始发送请求，超时时间设置为{self.timeout}秒")
            # 使用配置的超时时间，给API更多处理时间
            response = requests.post(self.api_url, headers=headers, json=data, timeout=self.timeout)
            
            # 记录响应状态和时间
            app_logger.info(f"收到响应，状态码: {response.status_code}")
            
            if response.status_code == 200:
                app_logger.info("AI API请求成功")
                
                # 解析响应JSON
                response_json = response.json()
                
                # 记录响应的基本结构（不包含完整内容）
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    first_choice = response_json["choices"][0]
                    if "message" in first_choice and "content" in first_choice["message"]:
                        content = first_choice["message"]["content"]
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                        app_logger.debug(f"响应内容预览: {content_preview}")
                
                # 记录响应的其他元数据
                if "model" in response_json:
                    app_logger.debug(f"响应使用的模型: {response_json['model']}")
                if "usage" in response_json:
                    app_logger.debug(f"令牌使用情况: {response_json['usage']}")
                
                return True, response_json
            else:
                # 记录失败响应的完整内容
                error_msg = f"AI API请求失败，状态码: {response.status_code}"
                app_logger.error(error_msg)
                app_logger.error(f"错误响应内容: {response.text}")
                return False, error_msg
        except Exception as e:
            error_msg = f"AI API请求异常: {str(e)}"
            app_logger.error(error_msg)
            
            # 记录异常时的请求详情，方便调试
            app_logger.debug(f"异常时的请求数据: {data}")
            
            # 如果是超时异常，提供更多信息
            if "timeout" in str(e).lower():
                app_logger.error(f"请求超时，当前超时设置为{self.timeout}秒，可能需要增加超时时间或优化提示词")
            
            return False, error_msg
    
    def _fix_json(self, json_str):
        """
        尝试修复JSON格式错误

        Args:
            json_str: 需要修复的JSON字符串

        Returns:
            str: 修复后的JSON字符串
        """
        app_logger.debug("开始修复JSON格式")

        # 尝试使用json5库解析（更宽松的JSON解析器）
        if json5 is not None:
            try:
                result = json5.loads(json_str)
                app_logger.info("使用json5成功解析JSON")
                return json.dumps(result)
            except Exception:
                pass  # 继续尝试其他修复方法

        # 定义修复策略列表
        def fix_trailing_comma(s):
            """修复数组最后一个元素后的逗号"""
            result = []
            i = 0
            while i < len(s):
                if i < len(s) - 1 and s[i:i+2] == "},":
                    j = i + 2
                    while j < len(s) and s[j].isspace():
                        j += 1
                    if j < len(s) and s[j] == "]":
                        result.append("}")
                        i += 2
                        continue
                result.append(s[i])
                i += 1
            return "".join(result)

        def fix_missing_comma(s):
            """修复缺少逗号的问题"""
            patterns = [("}{", "},{"), ("][", "],[")]
            for old, new in patterns:
                s = s.replace(old, new)
            return s

        def fix_missing_brackets(s):
            """修复缺少括号的问题"""
            open_braces = s.count("{") - s.count("}")
            open_brackets = s.count("[") - s.count("]")
            return s + "}" * open_braces + "]" * open_brackets

        def fix_truncate_to_last_element(s):
            """截取到最后一个完整元素"""
            last_end = s.rfind("}}")
            if last_end > 0:
                return s[:last_end+2] + "]}"
            return s

        # 依次尝试各种修复策略
        strategies = [
            ("修复尾随逗号", fix_trailing_comma),
            ("修复缺少逗号", fix_missing_comma),
            ("修复缺少括号", fix_missing_brackets),
            ("截取到最后元素", fix_truncate_to_last_element),
        ]

        for name, strategy in strategies:
            try:
                fixed = strategy(json_str)
                json.loads(fixed)
                app_logger.info(f"成功使用策略: {name}")
                return fixed
            except json.JSONDecodeError:
                continue

        # 如果所有修复方法都失败，返回原始JSON
        app_logger.warning("无法修复JSON格式，返回原始字符串")
        return json_str
    
    def parse_response(self, response):
        """
        解析AI响应
        
        Args:
            response: AI API的响应内容
            
        Returns:
            (bool, dict/str): 是否成功及解析结果/错误信息
        """
        try:
            # 记录完整响应结构
            app_logger.debug(f"响应完整结构的键: {list(response.keys()) if isinstance(response, dict) else '非字典类型'}")
            
            # 记录使用情况
            if isinstance(response, dict) and "usage" in response:
                usage = response["usage"]
                app_logger.debug(f"令牌使用情况: {usage}")
            
            # 从响应中提取content内容
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                error_msg = "AI响应内容为空"
                app_logger.error(error_msg)
                return False, error_msg
            
            # 记录原始响应内容的长度
            app_logger.debug(f"原始响应内容长度: {len(content)} 字符")
            
            # 记录响应内容的前200个字符和后200个字符
            content_start = content[:200] + "..." if len(content) > 200 else content
            content_end = "..." + content[-200:] if len(content) > 200 else content
            app_logger.debug(f"响应内容开头: {content_start}")
            app_logger.debug(f"响应内容结尾: {content_end}")
            
            # 尝试解析JSON内容
            # 有时AI可能会在JSON前后添加额外文本，需要提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            app_logger.debug(f"JSON内容起始位置: {json_start}, 结束位置: {json_end}")
            
            if json_start >= 0 and json_end >= 0:
                json_content = content[json_start:json_end+1]
                app_logger.debug(f"提取的JSON内容长度: {len(json_content)} 字符")
                app_logger.debug(f"JSON内容前50个字符: {json_content[:50]}...")
                
                try:
                    # 尝试修复JSON格式错误
                    try:
                        formatting_instructions = json.loads(json_content)
                    except json.JSONDecodeError as e:
                        app_logger.warning(f"原始JSON解析失败，尝试修复: {str(e)}")
                        
                        # 尝试修复常见的JSON错误
                        fixed_json = self._fix_json(json_content)
                        app_logger.debug(f"尝试修复后的JSON内容长度: {len(fixed_json)} 字符")
                        app_logger.debug(f"修复后的JSON内容前50个字符: {fixed_json[:50]}...")
                        
                        try:
                            formatting_instructions = json.loads(fixed_json)
                            app_logger.info("JSON修复成功，解析完成")
                        except json.JSONDecodeError as e2:
                            app_logger.error(f"修复后的JSON仍然无法解析: {str(e2)}")
                            raise e  # 抛出原始异常
                    
                    # 验证格式化指令的结构
                    if not isinstance(formatting_instructions, dict):
                        app_logger.error(f"排版指令不是字典类型: {type(formatting_instructions)}")
                        return False, "响应格式错误: 排版指令应为字典类型"
                    
                    if 'elements' not in formatting_instructions:
                        app_logger.error("排版指令缺少elements字段")
                        return False, "响应格式错误: 缺少elements字段"
                    
                    elements = formatting_instructions['elements']
                    if not isinstance(elements, list):
                        app_logger.error(f"elements不是列表类型: {type(elements)}")
                        return False, "响应格式错误: elements应为列表类型"
                    
                    # 验证每个元素
                    for i, element in enumerate(elements):
                        if not isinstance(element, dict):
                            app_logger.error(f"元素 {i} 不是字典类型: {type(element)}")
                            return False, f"响应格式错误: 元素 {i} 应为字典类型"
                        
                        if 'type' not in element:
                            app_logger.error(f"元素 {i} 缺少type字段")
                            return False, f"响应格式错误: 元素 {i} 缺少type字段"
                        
                        if 'content' not in element:
                            app_logger.error(f"元素 {i} 缺少content字段")
                            return False, f"响应格式错误: 元素 {i} 缺少content字段"
                        
                        if 'format' not in element:
                            app_logger.error(f"元素 {i} 缺少format字段")
                            return False, f"响应格式错误: 元素 {i} 缺少format字段"
                    
                    app_logger.debug(f"JSON解析成功，得到字典类型数据")
                    
                    # 记录解析后的数据结构
                    if isinstance(formatting_instructions, dict):
                        app_logger.debug(f"格式化指令的键: {list(formatting_instructions.keys())}")
                        
                        # 检查元素数量
                        elements = formatting_instructions.get('elements', [])
                        if isinstance(elements, list):
                            app_logger.debug(f"元素数量: {len(elements)}")
                            
                            # 记录前三个元素的类型
                            element_types = [element.get('type', '未知') for element in elements[:3]]
                            app_logger.debug(f"前三个元素类型: {element_types}")
                    
                    return True, formatting_instructions
                except json.JSONDecodeError as e:
                    error_msg = f"JSON解析失败: {str(e)}"
                    app_logger.error(error_msg)
                    
                    # 记录导致解析失败的JSON内容
                    problem_part = json_content[max(0, e.pos-50):min(len(json_content), e.pos+50)]
                    app_logger.error(f"解析失败位置附近的内容: ...{problem_part}...")
                    app_logger.error(f"解析失败位置: {e.pos}, 行: {e.lineno}, 列: {e.colno}")
                    
                    return False, error_msg
            else:
                error_msg = "响应中未找到有效的JSON内容"
                app_logger.error(error_msg)
                
                # 记录完整响应内容，便于调试
                app_logger.error(f"完整响应内容: {content}")
                
                return False, error_msg
        except Exception as e:
            error_msg = f"解析AI响应异常: {str(e)}"
            app_logger.error(error_msg)
            
            # 记录异常详情
            import traceback
            app_logger.error(f"异常详情: {traceback.format_exc()}")
            
            return False, error_msg
