#!/bin/bash

# macOS Build Script
# Usage: Run ./build/build_macos.sh from project root

set -e  # Exit on error

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录（脚本所在目录的父目录）
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目根目录执行所有操作
cd "$PROJECT_DIR"

echo "=========================================="
echo "macOS Build Script"
echo "Project directory: $PROJECT_DIR"
echo "Build directory: $SCRIPT_DIR"
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
if [ -f "$PROJECT_DIR/release_macos/dify_chat_tester" ]; then
    echo "✅ 打包成功！"
    echo "📁 可执行文件位置: $PROJECT_DIR/release_macos/dify_chat_tester"
    
    # 创建启动脚本
    cat > "$PROJECT_DIR/release_macos/run.sh" << 'EOF'
#!/bin/bash
# 获取脚本所在目录
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 切换到脚本目录并运行
cd "$DIR"
./dify_chat_tester
EOF
    chmod +x "$PROJECT_DIR/release_macos/run.sh"
    
    # 压缩发布包
    cd "$PROJECT_DIR"
    RELEASE_NAME="dify_chat_tester_macos_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$RELEASE_NAME" -C release_macos .
    
    echo "📦 发布包已创建: $PROJECT_DIR/$RELEASE_NAME"
    echo ""
    echo "📋 使用说明:"
    echo "1. 解压 $RELEASE_NAME"
    echo "2. 复制 config.env.example 为 config.env"
    echo "3. 编辑 config.env 配置 API 信息"
    echo "4. 运行 ./run.sh 启动程序"
    echo ""
    echo "🎉 打包完成！"
else
    echo "❌ 打包失败！"
    echo "请检查错误信息并重试"
    exit 1
fi