"""
选择器模块
负责处理用户选择逻辑（模型、角色、模式）
"""

import sys

from dify_chat_tester.terminal_ui import console, print_error, print_input_prompt, print_success


def select_model(available_models, provider_name):
    """选择模型"""
    # 如果只有一个模型且是Dify，则自动选择
    if len(available_models) == 1 and "Dify" in provider_name:
        selected_model = available_models[0]
        print(f"自动选择模型: {selected_model}")
        return selected_model

    # 显示所有可用模型
    print("可用的模型:")
    for i, model in enumerate(available_models, 1):
        # 使用原始print避免Rich的语法高亮
        print(f"  {i}. {model}")
    # 添加自定义模型选项
    print(f"  {len(available_models) + 1}. 自定义模型")
    console.print()

    while True:
        model_choice = print_input_prompt(
            f"请选择模型（输入 1-{len(available_models) + 1}）或直接输入模型名"
        )
        try:
            # 尝试将输入作为数字处理
            if model_choice.isdigit():
                model_num = int(model_choice)
                if 1 <= model_num <= len(available_models):
                    # 选择预设模型
                    selected_model = available_models[model_num - 1]
                    print_success(f"已选择模型: {selected_model}")
                    return selected_model
                elif model_num == len(available_models) + 1:
                    # 选择自定义模型
                    custom_model = print_input_prompt("请输入自定义模型名称")
                    if custom_model:
                        selected_model = custom_model
                        print_success(f"已选择模型: {selected_model}")
                        return selected_model
                    else:
                        print_error("模型名称不能为空，请重新输入。")
                else:
                    print_error(
                        f"无效的模型序号！请输入 1-{len(available_models) + 1} 之间的数字。"
                    )
            else:
                # 直接输入模型名称（不是数字）
                if model_choice:
                    selected_model = model_choice
                    print_success(f"已选择模型: {selected_model}")
                    return selected_model
                else:
                    print_error("输入不能为空，请选择模型或输入自定义模型名称。")
        except ValueError:
            print_error("请输入有效的数字或模型名称！")


def select_role(available_roles):
    """选择角色"""
    print("可用角色:")
    for i, role in enumerate(available_roles, 1):
        print(f"  {i}. {role}")
    print(f"  {len(available_roles) + 1}. 用户(user)")
    print(f"  {len(available_roles) + 2}. 自定义角色")
    console.print()

    while True:
        try:
            role_choice = print_input_prompt(f"请选择角色（输入 1-{len(available_roles) + 2}）")

            # 尝试转换为数字
            if role_choice.isdigit():
                role_num = int(role_choice)

                # 选择预设角色
                if 1 <= role_num <= len(available_roles):
                    selected_role = available_roles[role_num - 1]
                    return selected_role

                # 选择用户角色
                elif role_num == len(available_roles) + 1:
                    return "user"

                # 自定义角色
                elif role_num == len(available_roles) + 2:
                    while True:
                        custom_role = print_input_prompt("请输入自定义角色名称")
                        if custom_role:
                            selected_role = custom_role
                            return selected_role
                        else:
                            print_error("角色名称不能为空，请重新输入。")
                    break

                else:
                    print_error(f"无效的角色序号！请输入 1-{len(available_roles) + 2} 之间的数字。")
            else:
                # 直接输入角色名称
                if role_choice:
                    selected_role = role_choice
                    return selected_role
                else:
                    print("输入不能为空，请选择角色或输入自定义角色名称。", file=sys.stderr)

        except ValueError:
            print_error("请输入有效的数字！")
        except KeyboardInterrupt:
            from dify_chat_tester.terminal_ui import print_warning

            print_warning("用户取消操作，程序退出。")
            sys.exit(0)


def select_mode():
    """选择运行模式"""
    print("请选择运行模式:")
    print("1. 会话模式 (实时对话)")
    print("2. 批量询问模式 (通过 Excel 文件批量询问)")
    print("3. 退出程序")
    console.print()

    while True:
        mode_choice = print_input_prompt("请输入模式序号")

        if mode_choice in ["1", "2", "3"]:
            return mode_choice
        else:
            print_error("无效的模式选择，请重新输入。")
            console.print()
            continue
