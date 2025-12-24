#!/bin/bash

# ============================================================================
# Dify Chat Tester macOS 打包脚本
# ============================================================================
#
# 功能：
#   1. 使用 PyInstaller 将项目打包为 macOS 可执行文件
#   2. 复制配置模板、文档、示例插件到发布目录
#   3. 生成带版本号和时间戳的 tar.gz 压缩包
#
# 前置条件：
#   - uv 包管理器 (https://astral.sh/uv)
#   - Python 3.10+
#
# 使用示例：
#   bash build/build_macos.sh
#
# 输出：
#   - release_macos/           发布目录
#   - dify_chat_tester_macos_v*.tar.gz  发布压缩包
# ============================================================================

set -e  # Exit on error

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录（脚本所在目录的父目录）
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目根目录执行所有操作
cd "$PROJECT_DIR"

echo "=========================================="
echo "Dify Chat Tester macOS 打包脚本"
echo "项目目录: $PROJECT_DIR"
echo "构建目录: $SCRIPT_DIR"
echo "=========================================="

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: uv 未安装"
    echo "请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查 Python 版本
echo "🐍 检查 Python 版本..."
uv run python --version

# 安装/更新依赖
echo "📦 安装/更新依赖..."
uv sync

# 安装 PyInstaller
echo "🔧 安装 PyInstaller..."
uv add --dev pyinstaller

# 清理之前的构建（只清理build目录下的临时文件，保留spec文件）
echo "🧹 清理之前的构建..."
rm -rf "$PROJECT_DIR/build/dify_chat_tester" 2>/dev/null || true
rm -rf "$PROJECT_DIR/build/dify_chat_tester.dist" 2>/dev/null || true
rm -rf "$PROJECT_DIR/build/dify_chat_tester.build" 2>/dev/null || true

# 优先使用项目根目录的spec文件，如果不存在则使用build目录的
SPEC_FILE="$PROJECT_DIR/dify_chat_tester.spec"
if [ ! -f "$SPEC_FILE" ]; then
    SPEC_FILE="$SCRIPT_DIR/dify_chat_tester.spec"
    if [ ! -f "$SPEC_FILE" ]; then
        echo "❌ 错误: 找不到 spec 文件"
        exit 1
    fi
fi

echo "📄 使用 spec 文件: $SPEC_FILE"

# 运行 PyInstaller
echo "🚀 开始打包..."
uv run pyinstaller "$SPEC_FILE"

# 检查打包结果
if [ -f "$PROJECT_DIR/dist/dify_chat_tester" ]; then
    echo "✅ 打包成功！"
    echo "📁 可执行文件位置: $PROJECT_DIR/dist/dify_chat_tester"
    
    # 创建发布目录
    mkdir -p "$PROJECT_DIR/release_macos"
    
    # 复制文件到发布目录
    cp "$PROJECT_DIR/dist/dify_chat_tester" "$PROJECT_DIR/release_macos/"
    
    # 复制必要的配置文件
    cp "$PROJECT_DIR/.env.config.example" "$PROJECT_DIR/release_macos/"
    cp "$PROJECT_DIR/dify_chat_tester_template.xlsx" "$PROJECT_DIR/release_macos/"
    
    # 复制文档文件（如果存在）
    [ -f "$PROJECT_DIR/README.md" ] && cp "$PROJECT_DIR/README.md" "$PROJECT_DIR/release_macos/"
    [ -f "$PROJECT_DIR/docs/用户使用指南.md" ] && cp "$PROJECT_DIR/docs/用户使用指南.md" "$PROJECT_DIR/release_macos/"
    
    # 复制知识库文档目录（如果存在）
    [ -d "$PROJECT_DIR/kb-docs" ] && cp -r "$PROJECT_DIR/kb-docs" "$PROJECT_DIR/release_macos/"

    # 创建并复制外部插件目录（包含说明文档和示例插件）
    mkdir -p "$PROJECT_DIR/release_macos/external_plugins"
    [ -f "$PROJECT_DIR/external_plugins/README.md" ] && cp "$PROJECT_DIR/external_plugins/README.md" "$PROJECT_DIR/release_macos/external_plugins/"
    [ -d "$PROJECT_DIR/external_plugins/demo_plugin" ] && cp -r "$PROJECT_DIR/external_plugins/demo_plugin" "$PROJECT_DIR/release_macos/external_plugins/"
    
    # 获取版本号
    VERSION=$(grep -m 1 'version = ' "$PROJECT_DIR/pyproject.toml" | sed 's/version = "//;s/"//')
    if [ -z "$VERSION" ]; then
        VERSION="unknown"
    fi

    # 压缩发布包
    cd "$PROJECT_DIR"
    RELEASE_NAME="dify_chat_tester_macos_v${VERSION}_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$RELEASE_NAME" -C release_macos .
    
    echo "📦 发布包已创建: $PROJECT_DIR/$RELEASE_NAME"
    echo ""
    echo "📋 使用说明:"
    echo "1. 解压 $RELEASE_NAME"
    echo "2. 复制 .env.config.example 为 .env.config"
    echo "3. 编辑 .env.config 配置 API 信息"
    echo "4. 赋予可执行权限: chmod +x ./dify_chat_tester"
    echo "5. 运行 ./dify_chat_tester 启动程序"
    echo ""
    echo "🎉 打包完成！"
    
    # 清理临时文件
    echo "🧹 清理临时文件..."
    rm -rf "$PROJECT_DIR/build/dify_chat_tester" 2>/dev/null || true
    rm -rf "$PROJECT_DIR/build/dify_chat_tester.dist" 2>/dev/null || true
    rm -rf "$PROJECT_DIR/build/dify_chat_tester.build" 2>/dev/null || true
    echo "✅ 清理完成"
else
    echo "❌ 打包失败！"
    echo "请检查错误信息并重试"
    exit 1
fi