"""
配置加载器
从 .env.config 文件中加载所有配置参数

作者：Mison
邮箱：1360962086@qq.com
"""

import os
import sys
from typing import Any, List, Optional


class ConfigLoader:
    """配置加载器 - 从 .env.config 文件加载配置"""

    def __init__(self, env_file: str = ".env.config"):
        self.env_file = env_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        config_file_path = self._get_config_file_path()

        if not os.path.exists(config_file_path):
            print(
                f"警告: 配置文件 '{self.env_file}' 不存在，正在尝试创建默认配置...",
                file=sys.stderr,
            )
            self._create_default_config_file()  # This function now handles printing success/failure

            # After attempting to create, check if it now exists
            if os.path.exists(config_file_path):
                print(
                    f"信息: 配置文件 '{self.env_file}' 已成功创建并加载。",
                    file=sys.stderr,
                )
                self._read_config_file(config_file_path)
            else:
                print(
                    f"警告: 无法创建配置文件 '{self.env_file}'，将使用内置默认配置。",
                    file=sys.stderr,
                )
                self._load_defaults()
        else:
            self._read_config_file(config_file_path)

    def _read_config_file(self, config_file_path: str):
        """从指定路径读取配置文件

        支持两种形式的配置：
        1. 单行键值：KEY=value
        2. 使用三引号包裹的多行值（KEY= 后面的值写在接下来的多行中，以三引号结束）
        """
        multiline_key: Optional[str] = None
        multiline_buffer: list[str] = []

        with open(config_file_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                stripped = line.strip()

                # 处理多行值收集阶段
                if multiline_key is not None:
                    # 查找结束标记 """
                    if '"""' in stripped:
                        # 截取结束标记之前的内容
                        end_idx = line.find('"""')
                        content_part = line[:end_idx]
                        if content_part:
                            multiline_buffer.append(content_part)
                        # 合并为最终值
                        self.config[multiline_key] = "\n".join(multiline_buffer)
                        multiline_key = None
                        multiline_buffer = []
                    else:
                        multiline_buffer.append(line)
                    continue

                # 跳过空行和注释
                if not stripped or stripped.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value_stripped = value.lstrip()

                # 多行值起始：KEY=""" ...
                if value_stripped.startswith('"""'):
                    after = value_stripped[3:]
                    # 同一行就结束：KEY="""single line"""
                    if '"""' in after:
                        end_idx = after.find('"""')
                        content = after[:end_idx]
                        self.config[key] = content
                    else:
                        multiline_key = key
                        multiline_buffer = []
                        if after:
                            multiline_buffer.append(after)
                    continue

                # 普通单行键值
                self.config[key] = value_stripped.strip()

    def _get_project_root(self):
        """获取项目根目录"""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        
        # 开发环境：当前文件在 dify_chat_tester/config/loader.py
        # 需要向上两级：dify_chat_tester/config -> dify_chat_tester -> root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.dirname(current_dir)
        return os.path.dirname(package_dir)

    def _get_config_file_path(self):
        """获取配置文件的完整路径"""
        return os.path.join(self._get_project_root(), self.env_file)

    def _create_default_config_file(self):
        """创建默认配置文件"""
        base_dir = self._get_project_root()
        
        # 优先从 config/ 目录查找模板文件（新标准位置）
        example_file = os.path.join(base_dir, "config", ".env.config.example")
        
        # 如果没找到，尝试从根目录查找（旧位置）
        if not os.path.exists(example_file):
            example_file = os.path.join(base_dir, ".env.config.example")

        # 配置文件创建在项目根目录（或程序运行目录）
        config_file_path = os.path.join(base_dir, self.env_file)

        # 如果 .env.config.example 存在，复制它作为默认配置
        if os.path.exists(example_file):
            try:
                with open(example_file, "r", encoding="utf-8") as src:
                    content = src.read()

                with open(config_file_path, "w", encoding="utf-8") as dst:
                    dst.write(content)

                print(f"✅ 已从模板创建配置文件: {config_file_path}", file=sys.stderr)
            except Exception as e:
                print(f"❌ 创建配置文件失败: {e}", file=sys.stderr)
                print("将使用内置默认配置", file=sys.stderr)
        else:
            # 如果模板文件不存在，创建一个基本的配置文件
            self._create_basic_config_file(base_dir)


    def _get_default_config_dict(self) -> dict:
        """返回默认配置字典

        说明：
        - Provider 相关敏感信息（如 API_KEY 等）默认留空，
          用户可在 .env.config 中自行填写；
        - 读取时如果为空字符串，会被视为“未配置”，
          程序会自动回退到交互式输入方式。
        """
        return {
            "CHAT_LOG_FILE_NAME": "chat_log.xlsx",
            "ROLES": "员工,门店",
            "AI_PROVIDERS": "1:Dify:dify;2:OpenAI 兼容接口:openai;3:iFlow:iflow",
            "BATCH_REQUEST_INTERVAL": "1.0",
            "BATCH_DEFAULT_SHOW_RESPONSE": "false",
            "IFLOW_MODELS": "qwen3-max,kimi-k2-0905,glm-4.6,deepseek-v3.2",
            "OPENAI_MODELS": "gpt-4o,gpt-4o-mini,gpt-4-turbo,gpt-3.5-turbo,custom-model",
            "WAITING_INDICATORS": "⣾,⣽,⣻,⢿,⡿,⣟,⣯,⣷",
            "WAITING_TEXT": "正在思考",
            "WAITING_DELAY": "0.1",
            # 网络重试配置
            "NETWORK_MAX_RETRIES": "3",
            "NETWORK_RETRY_DELAY": "1.0",
            # 跨知识点生成配置
            "CROSS_KNOWLEDGE_MIN_ITERATIONS": "5",
            "CROSS_KNOWLEDGE_MAX_ITERATIONS": "20",
            # 日志配置
            "LOG_LEVEL": "INFO",
            "LOG_TO_FILE": "false",
            "LOG_FILE_NAME": "dify_chat_tester.log",
            # UI 配置
            "USE_RICH_UI": "true",  # 是否使用富文本 UI（false 时使用简单文本输出）
            # Provider 默认配置（留空即可，通过 .env.config 配置）
            "DIFY_BASE_URL": "",
            "DIFY_API_KEY": "",
            "DIFY_APP_ID": "",
            "OPENAI_BASE_URL": "",
            "OPENAI_API_KEY": "",
            "IFLOW_API_KEY": "",
            # 思维链配置
            "ENABLE_THINKING": "true",  # 是否默认开启思维链/推理过程
        }

    def _create_basic_config_file(self, base_dir):
        """创建基本的配置文件（当模板文件不存在时）"""
        config_file_path = os.path.join(base_dir, self.env_file)
        default_config_dict = self._get_default_config_dict()

        config_content = [
            "# AI 聊天客户端测试工具 - 配置文件",
            "# 复制此文件为 .env.config 并根据需要修改配置",
            "",
        ]
        for key, value in default_config_dict.items():
            config_content.append(f"{key}={value}")

        try:
            with open(config_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(config_content))
            print(f"✅ 已创建基本配置文件: {config_file_path}", file=sys.stderr)
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}", file=sys.stderr)

    def _load_defaults(self):
        """加载默认配置（当配置文件不存在时）"""
        self.config = self._get_default_config_dict()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def get_str(self, key: str, default: str = "") -> str:
        """获取字符串配置"""
        return self.get(key, default)

    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置"""
        try:
            return float(self.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置"""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes", "on")

    def get_list(
        self, key: str, delimiter: str = ",", default: Optional[List[str]] = None
    ) -> List[str]:
        """获取列表配置"""
        if default is None:
            default = []
        value = self.get(key, "")
        if not value:
            return default
        return [item.strip() for item in value.split(delimiter) if item.strip()]

    def get_enable_thinking(self) -> bool:
        """获取是否默认启用思维链/推理过程显示"""
        # 优先从环境变量获取
        value = os.getenv("ENABLE_THINKING")
        if value is not None:
            return value.lower() in ("true", "1", "yes", "on")

        # 从配置文件获取
        return self.get_bool("ENABLE_THINKING", True)

    def get_system_prompt(self, role: str = "员工") -> str:
        """
        获取系统提示词
        优先从环境变量获取，其次从 .env.config 文件获取

        Args:
            role: 当前角色

        Returns:
            str: 系统提示词（已替换占位符）
        """
        # 默认提示词模板
        default_template = (
            "你是一个AI助手。当前角色：{role}。请以专业、友好的方式回答问题。"
        )

        # 优先从环境变量获取
        value = os.getenv("SYSTEM_PROMPT")
        if value is None:
            # 从配置文件获取
            value = self.get("SYSTEM_PROMPT", default_template)

        # 替换占位符
        template = value or default_template
        return template.format(role=role)

    def get_single_knowledge_prompt(self) -> str:
        """
        获取单一知识点生成问题的提示词模板
        """
        # 默认提示词模板（保留代码中原有的逻辑）
        default_template = """你是一个专业的测试问题生成助手。请仔细阅读以下文档内容，生成尽可能多的测试问题。

当前为第 {idx}/{total_chunks} 个内容分块，请尽量覆盖本分块中的知识点。

要求：
1. 先识别本分块中有哪些独立的知识点或主题，并大致评估每个知识点被真实用户询问的概率（高/中/低）。
2. 问题需要模仿普通用户的真实提问语气，口语化、自然。
3. 问题应该覆盖文档中的各个知识点。
4. 问题的难度应该有所变化，包括简单查询、复杂推理等。
5. 每个问题都应该能从文档中找到答案依据。
6. 生成的问题数量不做固定限制：
   - 知识点较少时，覆盖所有知识点即可；
   - 对"高概率"知识点，多写几个不同角度的提问；
   - 对"中概率"知识点，至少生成 1-2 个提问；
   - 对"低概率"知识点，可适当精简。
7. 最终只输出问题列表，不要输出对知识点或概率的解释。
8. 以 JSON 数组格式返回，每个元素是一个问题字符串。

文档名称：{document_name}

文档内容（第 {idx}/{total_chunks} 块）：
{chunk}

请生成问题列表（必须是 JSON 数组格式，例如:["问题1","问题2","问题3"]）："""

        # 优先从环境变量获取
        value = os.getenv("SINGLE_KNOWLEDGE_PROMPT")
        if value is None:
            # 从配置文件获取
            value = self.get("SINGLE_KNOWLEDGE_PROMPT", default_template)

        return value or default_template

    def get_cross_knowledge_prompt(self) -> str:
        """
        获取跨知识点生成问题的提示词模板
        """
        # 默认提示词模板
        default_template = """你是一个专业的测试问题生成助手。请阅读以下来自不同（或相同）文档的多个知识点片段，尝试寻找它们之间的关联，生成跨知识点的测试问题。

要求：
1. 先从“真实用户在一个具体场景中”的角度出发，思考这些知识点在实际工作中可能如何被组合使用。
2. 分析提供的多个知识点来源，寻找逻辑关联（例如：同一流程的前后步骤、不同工具在同一任务中的配合、概念/方案的对比、不同角色围绕同一问题的协同等）。
3. 评估这些关联在用户真实场景中出现的概率：
   - 关联度和场景概率较高时，可以多设计几个不同角度的问题；
   - 关联度一般但仍有合理使用场景时，也可以适当生成少量问题；
   - 只有在你几乎无法找到合理关联、强行组合才会误导用户时，才不要生成问题（可以返回空数组）。
4. 每个问题都应该需要结合多个知识点来源的内容才能完整回答（即真正的“跨知识点问题”，不是简单拷贝单一文档的问题）。
5. 问题要模仿真实用户的自然提问，用口语化的方式表达需求。
6. 以 JSON 数组格式返回问题列表；如果最终确实没有合适的问题，再返回空数组 []。

{context_text}

请生成问题列表（必须是 JSON 数组格式，例如: ["问题1", "问题2"]）："""

        # 优先从环境变量获取
        value = os.getenv("CROSS_KNOWLEDGE_PROMPT")
        if value is None:
            # 从配置文件获取
            value = self.get("CROSS_KNOWLEDGE_PROMPT", default_template)

        return value or default_template


# 全局配置实例
config_loader = ConfigLoader()


def get_config():
    """获取配置加载器实例"""
    return config_loader


# 特殊解析 AI_PROVIDERS 配置（格式：序号:名称:ID;序号:名称:ID）
def parse_ai_providers(value: str) -> dict:
    """解析 AI_PROVIDERS 配置（格式：序号:名称:ID）"""
    default = {
        "1": {"name": "Dify", "id": "dify"},
        "2": {"name": "OpenAI 兼容接口", "id": "openai"},
        "3": {"name": "iFlow", "id": "iflow"},
    }
    if not value:
        return default

    result = {}
    for item in value.split(";"):
        if ":" in item:
            parts = item.split(":", 2)  # 最多分割2次，得到3个部分
            if len(parts) == 3:
                key, name, provider_id = parts
                result[key.strip()] = {"name": name.strip(), "id": provider_id.strip()}
    return result if result else default
