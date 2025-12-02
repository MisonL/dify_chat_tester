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
        """从指定路径读取配置文件"""
        with open(config_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    self.config[key.strip()] = value.strip()

    def _get_config_file_path(self):
        """获取配置文件的完整路径"""
        # 如果是打包后的程序
        if getattr(sys, "frozen", False):
            # 配置文件在程序所在目录
            return os.path.join(os.path.dirname(sys.executable), self.env_file)
        else:
            # 开发环境，配置文件在项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            return os.path.join(project_dir, self.env_file)

    def _create_default_config_file(self):
        """创建默认配置文件"""
        # 获取程序运行目录（对于打包后的程序，这是程序所在目录）
        if getattr(sys, "frozen", False):
            # PyInstaller 打包后的程序
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)

        # 优先从程序目录查找 .env.config.example
        example_file = os.path.join(base_dir, ".env.config.example")

        # 如果程序目录没有，尝试从源码目录查找
        if not os.path.exists(example_file) and not getattr(sys, "frozen", False):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            example_file = os.path.join(project_dir, ".env.config.example")

        # 配置文件创建在程序运行目录
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
