"""
配置加载器
从 config.env 文件中加载所有配置参数

作者：Mison
邮箱：1360962086@qq.com
"""

import os
import sys
from typing import List, Any, Optional


class ConfigLoader:
    """配置加载器 - 从 .env 文件加载配置"""

    def __init__(self, env_file: str = "config.env"):
        self.env_file = env_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.env_file):
            print(f"警告: 配置文件 '{self.env_file}' 不存在，使用默认配置", file=sys.stderr)
            self._load_defaults()
            return

        with open(self.env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue

                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    self.config[key] = value

    def _load_defaults(self):
        """加载默认配置（当配置文件不存在时）"""
        self.config = {
            'CHAT_LOG_FILE_NAME': 'chat_log.xlsx',
            'ROLES': '员工,门店',
            'AI_PROVIDERS': '1:Dify:dify;2:OpenAI 兼容接口:openai;3:iFlow:iflow',
            'BATCH_REQUEST_INTERVAL': '1.0',
            'BATCH_DEFAULT_SHOW_RESPONSE': 'false',
            'IFLOW_MODELS': 'qwen3-max,kimi-k2-0905,glm-4.6,deepseek-v3.2',
            'OPENAI_MODELS': 'gpt-4o,gpt-4o-mini,gpt-4-turbo,gpt-3.5-turbo,custom-model',
            'WAITING_INDICATORS': '⣾,⣽,⣻,⢿,⡿,⣟,⣯,⣷',
            'WAITING_TEXT': '正在思考',
            'WAITING_DELAY': '0.1'
        }

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

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes', 'on')

    def get_list(self, key: str, delimiter: str = ',', default: Optional[List[str]] = None) -> List[str]:
        """获取列表配置"""
        if default is None:
            default = []
        value = self.get(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(delimiter) if item.strip()]




# 全局配置实例
config_loader = ConfigLoader()


def get_config():
    """获取配置加载器实例"""
    return config_loader
