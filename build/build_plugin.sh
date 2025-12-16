#!/bin/bash

# 插件打包脚本
# 用法: ./build/build_plugin.sh <plugin_name> [plugin_dir]
# 示例: ./build/build_plugin.sh qianxiaoyin ./external_plugins

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 参数检查
if [ -z "$1" ]; then
    echo -e "${RED}❌ 错误: 请指定插件名称${NC}"
    echo "用法: $0 <plugin_name> [plugin_dir]"
    echo "示例: $0 qianxiaoyin ./external_plugins"
    exit 1
fi

PLUGIN_NAME="$1"
PLUGIN_DIR="${2:-$PROJECT_DIR/external_plugins}"
PLUGIN_PATH="$PLUGIN_DIR/$PLUGIN_NAME"

echo "=========================================="
echo "🔌 插件打包脚本"
echo "插件名称: $PLUGIN_NAME"
echo "插件目录: $PLUGIN_PATH"
echo "=========================================="

# 检查插件目录是否存在
if [ ! -d "$PLUGIN_PATH" ]; then
    echo -e "${RED}❌ 错误: 插件目录不存在: $PLUGIN_PATH${NC}"
    exit 1
fi

# 检查必要文件
if [ ! -f "$PLUGIN_PATH/__init__.py" ]; then
    echo -e "${RED}❌ 错误: 缺少 __init__.py 文件${NC}"
    exit 1
fi

# 尝试从 __init__.py 读取版本号
VERSION=$(grep -m 1 '__version__' "$PLUGIN_PATH/__init__.py" 2>/dev/null | sed 's/.*"\(.*\)".*/\1/' || echo "")
if [ -z "$VERSION" ]; then
    VERSION=$(date +%Y%m%d)
    echo -e "${YELLOW}⚠️ 未找到版本号，使用日期: $VERSION${NC}"
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 复制插件文件
echo "📁 复制插件文件..."
mkdir -p "$TEMP_DIR/$PLUGIN_NAME"
cp -r "$PLUGIN_PATH/"* "$TEMP_DIR/$PLUGIN_NAME/"

# 排除不需要的文件
rm -rf "$TEMP_DIR/$PLUGIN_NAME/__pycache__" 2>/dev/null || true
rm -rf "$TEMP_DIR/$PLUGIN_NAME/"*.pyc 2>/dev/null || true

# 生成 README（如果不存在）
if [ ! -f "$TEMP_DIR/$PLUGIN_NAME/README.md" ]; then
    echo "📝 生成 README.md..."
    cat > "$TEMP_DIR/README.md" << EOF
# $PLUGIN_NAME 插件

版本: $VERSION

## 安装方法

1. 将此文件夹放入主程序的 \`external_plugins/\` 目录
2. 如果有 \`requirements.txt\`，请先安装依赖
3. 重新启动主程序

## 配置

请参阅主程序的 .env.config.example 了解配置项。
EOF
fi

# 打包为 zip
OUTPUT_FILE="$PROJECT_DIR/${PLUGIN_NAME}_v${VERSION}.zip"
echo "📦 打包中..."

cd "$TEMP_DIR"
zip -r "$OUTPUT_FILE" . -x "*.DS_Store" -x "*__pycache__*"

echo ""
echo -e "${GREEN}✅ 打包完成！${NC}"
echo "📁 输出文件: $OUTPUT_FILE"
echo ""
echo "使用方法:"
echo "1. 将 zip 文件放入主程序的 external_plugins/ 目录"
echo "2. 或解压后将 $PLUGIN_NAME 文件夹放入 external_plugins/"
echo "3. 启动主程序，插件将自动加载"
