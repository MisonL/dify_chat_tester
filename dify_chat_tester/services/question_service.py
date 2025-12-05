"""
问题生成服务模块

封装问题生成相关的业务逻辑，支持单一知识点和跨知识点两种生成模式。
"""

from typing import Optional

from dify_chat_tester.selectors import select_folder_path
from dify_chat_tester.terminal_ui import console, print_info


class QuestionService:
    """问题生成服务类"""

    def __init__(self, provider, role: str, provider_name: str, model: str):
        """初始化问题生成服务

        Args:
            provider: AI 供应商实例
            role: 角色名称
            provider_name: 供应商名称（用于展示）
            model: 模型名称
        """
        self.provider = provider
        self.role = role
        self.provider_name = provider_name
        self.model = model

    def run_single_knowledge_generation(
        self, folder_path: Optional[str] = None
    ) -> None:
        """运行单一知识点问题生成

        Args:
            folder_path: 文档文件夹路径，为 None 时进入交互式选择
        """
        self._run_generation(folder_path, is_cross_knowledge=False)

    def run_cross_knowledge_generation(
        self, folder_path: Optional[str] = None
    ) -> None:
        """运行跨知识点问题生成

        Args:
            folder_path: 文档文件夹路径，为 None 时进入交互式选择
        """
        self._run_generation(folder_path, is_cross_knowledge=True)

    def _run_generation(
        self, folder_path: Optional[str], is_cross_knowledge: bool
    ) -> None:
        """内部方法：执行问题生成

        Args:
            folder_path: 文档文件夹路径
            is_cross_knowledge: 是否为跨知识点模式
        """
        console.print()
        mode_name = (
            "AI生成跨知识点测试提问点"
            if is_cross_knowledge
            else "AI生成单一知识点测试提问点"
        )
        print_info(f"已选择: {mode_name}")

        # 选择文档文件夹路径（未指定时走交互）
        if not folder_path:
            folder_path = select_folder_path(default_path="./kb-docs")

        if is_cross_knowledge:
            from dify_chat_tester.question_generator import (
                run_cross_knowledge_generation,
            )

            run_cross_knowledge_generation(
                provider=self.provider,
                role=self.role,
                provider_name=self.provider_name,
                selected_model=self.model,
                folder_path=folder_path,
            )
        else:
            from dify_chat_tester.question_generator import run_question_generation

            run_question_generation(
                provider=self.provider,
                role=self.role,
                provider_name=self.provider_name,
                selected_model=self.model,
                folder_path=folder_path,
            )
