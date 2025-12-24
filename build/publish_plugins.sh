#!/bin/bash

# ============================================================================
# Dify Chat Tester 插件发布脚本
# ============================================================================
#
# 功能：
#   1. 从插件的 CHANGELOG 中解析最新版本号和更新日志
#   2. 打包指定插件或所有插件
#   3. 在 GitLab 创建 Release 并上传压缩包
#   4. 向企业微信群机器人 Webhook 推送发布通知
#   5. 在执行发布操作前，先汇总关键信息并交互确认
#
# 环境变量配置：
#   脚本会自动加载同目录下的 .env 文件，请先配置：
#     cp build/.env.example build/.env
#     # 编辑 .env 填入实际的 WECHAT_WEBHOOK_URL
#
# 使用示例：
#   bash build/publish_plugins.sh              # 交互式选择插件
#   bash build/publish_plugins.sh qianxiaoyin  # 发布指定插件
#   bash build/publish_plugins.sh all          # 发布所有插件
#
# 可选参数：
#       --wechat-webhook URL 覆盖 .env 中的企业微信 Webhook
#       --skip-release       跳过 GitLab Release 创建
#       --skip-wechat        跳过企业微信通知
#   -h, --help               显示帮助
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_BASE_DIR="$PROJECT_DIR/external_plugins"

# 加载环境变量配置文件
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 企微 Webhook（从环境变量或 .env 读取）
WECHAT_WEBHOOK_URL="${WECHAT_WEBHOOK_URL:-}"

print_usage() {
  cat <<EOF
用法：
  bash build/publish_plugin.sh <plugin_name|all> [选项]

选项：
  --wechat-webhook URL   企业微信 Webhook（也可通过环境变量 WECHAT_WEBHOOK_URL 提供）
  --skip-release         跳过 GitLab Release 创建
  --skip-wechat          跳过企业微信通知
  -h, --help             显示本帮助
EOF
}

# 发布单个插件
publish_single_plugin() {
    local plugin_name="$1"
    local plugin_path="$PLUGIN_BASE_DIR/$plugin_name"
    
    echo ""
    echo -e "${CYAN}=========================================="
    echo "🚀 发布插件: $plugin_name"
    echo -e "==========================================${NC}"
    
    # 检查插件目录
    if [ ! -d "$plugin_path" ]; then
        echo -e "${RED}❌ 插件目录不存在: $plugin_path${NC}"
        return 1
    fi
    
    # 读取版本号
    local version=$(grep -m 1 '__version__' "$plugin_path/__init__.py" 2>/dev/null | sed 's/.*"\(.*\)".*/\1/' || echo "")
    if [ -z "$version" ]; then
        echo -e "${RED}❌ 未找到版本号，请在 __init__.py 中定义 __version__${NC}"
        return 1
    fi
    
    local tag="v$version"
    local zip_file="$PROJECT_DIR/${plugin_name}_v${version}.zip"
    
    echo "版本: $version"
    echo "Tag: $tag"
    
    # 打包
    echo "📦 打包插件..."
    "$SCRIPT_DIR/build_plugins.sh" "$plugin_name" "$PLUGIN_BASE_DIR"

    # 查找生成的 zip 文件 (适配带时间戳的文件名)
    local zip_file=$(ls -t "$PROJECT_DIR/${plugin_name}_v${version}_"*.zip 2>/dev/null | head -n1)
    if [ -z "$zip_file" ] || [ ! -f "$zip_file" ]; then
        echo -e "${RED}❌ 打包失败: 未找到 ${plugin_name}_v${version}_*.zip${NC}"
        return 1
    fi
    
    # 解析 CHANGELOG
    # 优先查找插件目录下的 CHANGELOG.md，其次查找 external_plugins/CHANGELOG.md
    local changelog_file=""
    if [ -f "$plugin_path/CHANGELOG.md" ]; then
        changelog_file="$plugin_path/CHANGELOG.md"
    elif [ -f "$PLUGIN_BASE_DIR/CHANGELOG.md" ]; then
        changelog_file="$PLUGIN_BASE_DIR/CHANGELOG.md"
    fi

    local release_notes=""
    if [ -n "$changelog_file" ]; then
        release_notes=$(awk -v ver="$version" '
            /^## \[/ && index($0, "## [" ver "]") == 1 { in_block=1; next }
            in_block && /^## \[[0-9]+\.[0-9]+\.[0-9]+\]/ { exit }
            in_block && /^---$/ { exit }
            in_block { print }
        ' "$changelog_file")
    fi
    
    # 获取 GitLab 远程 (用于 Release 和通知链接)
    local gitlab_remote=$(cd "$PLUGIN_BASE_DIR" && git remote get-url origin 2>/dev/null || true)
    local changelog_url=""
    if [ -n "$gitlab_remote" ]; then
        # 简单处理：将 SSH/HTTPS git URL 转换为 HTTP 浏览 URL
        # 假设移除 .git 后缀，替换 git@xxx: 为 https://xxx/
        local base_url=$(echo "$gitlab_remote" | sed -E 's#^git@([^:]+):#https://\1/#; s#\.git$##')
        
        # 获取当前分支，默认为 main
        local current_branch=$(cd "$PLUGIN_BASE_DIR" && git symbolic-ref --short HEAD 2>/dev/null || echo "main")
        
        # 跳转到具体插件的 CHANGELOG 文件
        # 假设 external_plugins 是仓库根目录，插件各自在子目录中
        changelog_url="${base_url}/-/blob/${current_branch}/${plugin_name}/CHANGELOG.md"
    fi

    # 显示发布信息摘要并等待确认
    echo ""
    echo -e "${CYAN}==========================================
🔥 即将发布插件
------------------------------------------${NC}"
    echo "插件名称:       $plugin_name"
    echo "版本号:         $version"
    echo "Git tag:        $tag"
    echo "ZIP 文件:       $zip_file"
    [ -n "$changelog_url" ] && echo "CHANGELOG:      $changelog_url"
    echo ""
    if [ -n "$release_notes" ]; then
        echo -e "${CYAN}=== 发布说明（CHANGELOG 摘要） ===${NC}"
        echo "$release_notes"
    else
        echo -e "${YELLOW}⚠️ 未找到 CHANGELOG 内容${NC}"
    fi
    echo -e "${CYAN}==========================================${NC}"
    echo ""
    echo -e "默认值: Y（直接回车将继续执行发布流程）"
    read -p "请确认以上信息无误后继续执行发布操作？[Y/n] " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}❌ 已取消发布${NC}"
        rm -f "$zip_file"
        return 1
    fi

    # 创建 GitLab Release（如果未跳过）
    if [ "$SKIP_RELEASE" -eq 0 ]; then
        # local gitlab_remote=... (moved up)
        if [ -n "$gitlab_remote" ]; then
            echo "🚀 正在创建 GitLab Release..."
            
            # 检查是否已存在
            if (cd "$PLUGIN_BASE_DIR" && glab release view "$tag" >/dev/null 2>&1); then
                echo -e "${YELLOW}⚠️ Release $tag 已存在，跳过创建${NC}"
            else
                (cd "$PLUGIN_BASE_DIR" && glab release create "$tag" \
                    "$zip_file" \
                    --name "$plugin_name $tag" \
                    --notes "${release_notes:-初始版本}")
                echo -e "${GREEN}✅ GitLab Release 创建完成${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ 未找到 GitLab 远程，跳过 Release 创建${NC}"
        fi
    fi
    
    # 推送企业微信通知（如果未跳过）
    if [ "$SKIP_WECHAT" -eq 0 ] && [ -n "$WECHAT_WEBHOOK_URL" ]; then
        echo "📢 推送企业微信通知..."
        
        # 构造 GitLab CHANGELOG 链接 (如果存在)
        # 这里假设 CHANGELOG 在插件根目录或者 external_plugins 根目录
        # 我们使用发布脚本中已有的 release_notes，不强求链接
        
        local wecom_json=$(WE_TITLE="插件发布: $plugin_name" WE_TAG="$tag" WE_NOTES="$release_notes" WE_CHANGELOG_URL="$changelog_url" python3 - <<'PY'
import json
import os

title = os.environ.get("WE_TITLE", "")
tag = os.environ.get("WE_TAG", "")
notes = os.environ.get("WE_NOTES", "")
changelog_url = os.environ.get("WE_CHANGELOG_URL", "")

# ... (omitted for brevity, assume script continues) ...
sections = {"新增": [], "优化": [], "修复": []}
current = None
for raw in notes.splitlines():
    line = raw.strip()
    if not line:
        continue
    # 标题行（例如 "新增"、"优化"、"修复"），兼容 Markdown 的 "### 新增" 格式
    clean_key = line.lstrip("#").strip()
    if clean_key in sections:
        current = clean_key
        continue
    if not line.startswith("-") and not line.startswith("•") and not line.startswith("*"):
        # 非列表行直接跳过
        continue
    if current is None:
        # 没有显式标题，就算在「新增」里
        current = "新增"
    text = line.lstrip("-•* ").strip()
    if not text:
        continue
    sections[current].append(f"· {text}")

main_title = title
sub_title = f"版本: {tag}" if tag else "插件发布通知"

# 二级标题 + 文本列表：分三块展示「新增 / 优化 / 修复」
horizontal_content_list = []
for key in ("新增", "优化", "修复"):
    items = sections.get(key) or []
    if not items:
        continue
    # 每类最多取 4 条，长度控制在 150 字符左右 (插件可能不像主程序那么频繁，稍微放宽一点)
    summary = "\n".join(items[:4])[:150]
    horizontal_content_list.append({
        "keyname": key,
        "value": summary,
    })

# 如果三类都为空，兜底给一条通用摘要
if not horizontal_content_list and notes.strip():
    fallback = "".join(notes.splitlines())
    horizontal_content_list.append({
        "keyname": "更新内容",
        "value": fallback[:150],
    })

# 跳转链接：指向完整 CHANGELOG
jump_list = []
card_action = {"type": 1}
if changelog_url:
    jump = {
        "type": 1,
        "title": "查看完整更新日志",
        "url": changelog_url,
    }
    jump_list.append(jump)
    card_action["url"] = changelog_url
else:
    card_action["url"] = "https://gitlab-base.qdama.cn"

payload = {
    "msgtype": "template_card",
    "template_card": {
        "card_type": "text_notice",
        "source": {
            "desc": "插件发布通知",
            "desc_color": 0,
        },
        "main_title": {
            "title": main_title,
            "desc": sub_title,
        },
        "horizontal_content_list": horizontal_content_list,
        "jump_list": jump_list,
        "card_action": card_action,
    },
}

print(json.dumps(payload, ensure_ascii=False))
PY
)
        curl -sS -X POST "$WECHAT_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "$wecom_json" >/dev/null
        
        echo -e "${GREEN}✅ 企业微信通知已发送${NC}"
    fi
    
    # 清理 zip 文件
    rm -f "$zip_file"
    
    echo -e "${GREEN}✅ 插件 $plugin_name $tag 发布完成${NC}"
    return 0
}

# 参数解析
SKIP_RELEASE=0
SKIP_WECHAT=0
PLUGIN_NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --wechat-webhook)
            WECHAT_WEBHOOK_URL="$2"
            shift 2
            ;;
        --skip-release)
            SKIP_RELEASE=1
            shift 1
            ;;
        --skip-wechat)
            SKIP_WECHAT=1
            shift 1
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            if [ -z "$PLUGIN_NAME" ]; then
                PLUGIN_NAME="$1"
            fi
            shift 1
            ;;
    esac
done

if [ -z "$PLUGIN_NAME" ]; then
    # 交互式选择插件
    echo -e "${CYAN}请选择要发布的插件：${NC}"
    echo "0) 全部 (all) - 默认不包含示例插件"
    
    # 获取可用插件列表
    plugins=()
    i=1
    for plugin_path in "$PLUGIN_BASE_DIR"/*/; do
        name=$(basename "$plugin_path")
        # 跳过隐藏目录和特殊目录
        [[ "$name" == .* ]] && continue
        [[ "$name" == "__pycache__" ]] && continue
        
        if [ -f "$plugin_path/__init__.py" ]; then
            desc=""
            # 尝试获取描述（可选）
            if [ -f "$plugin_path/__init__.py" ]; then
               # 简单提取第一行非空注释作为描述，或者是 DOCSTRING
               desc=$(grep -m 1 '^"""' "$plugin_path/__init__.py" | sed 's/"""//g' || echo "")
            fi
            
            echo "$i) $name ${desc:+- $desc}"
            plugins+=("$name")
            ((i++))
        fi
    done
    
    echo ""
    read -p "请输入序号 (0-$((i-1))): " choice
    
    if [[ "$choice" == "0" ]]; then
        PLUGIN_NAME="all"
    elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#plugins[@]}" ]; then
        PLUGIN_NAME="${plugins[$((choice-1))]}"
    else
        echo -e "${RED}❌ 无效的选择${NC}"
        exit 1
    fi
    echo -e "${GREEN}已选择: $PLUGIN_NAME${NC}"
fi

echo "=========================================="
echo "🔌 插件发布脚本"
echo "插件目录: $PLUGIN_BASE_DIR"
echo "=========================================="

# 处理 all 参数
if [ "$PLUGIN_NAME" = "all" ]; then
    echo -e "${CYAN}📦 发布所有插件... (已自动跳过 demo_plugin)${NC}"
    
    success_count=0
    fail_count=0
    
    for plugin_path in "$PLUGIN_BASE_DIR"/*/; do
        name=$(basename "$plugin_path")
        
        [[ "$name" == .* ]] && continue
        [[ "$name" == "__pycache__" ]] && continue
        [[ "$name" == "demo_plugin" ]] && continue
        
        if [ -f "$plugin_path/__init__.py" ]; then
            if publish_single_plugin "$name"; then
                ((success_count++))
            else
                ((fail_count++))
            fi
        fi
    done
    
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🎉 发布完成！${NC}"
    echo "成功: $success_count 个"
    [ $fail_count -gt 0 ] && echo -e "${RED}失败: $fail_count 个${NC}"
    echo "=========================================="
else
    publish_single_plugin "$PLUGIN_NAME"
fi
