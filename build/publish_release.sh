#!/bin/bash

# ============================================================================
# Dify Chat Tester 主程序发布脚本
# ============================================================================
#
# 功能：
#   1. 从 CHANGELOG 中解析最新版本号和更新日志
#   2. 自动查找最近打包生成的 macOS / Windows 压缩包
#   3. 使用 gh / glab 分别在 GitHub / GitLab 创建 Release 并上传压缩包
#   4. 向企业微信群机器人 Webhook 推送发布通知
#   5. 在执行任何发布操作前，先汇总所有关键信息并交互确认
#
# 环境变量配置：
#   脚本会自动加载同目录下的 .env 文件，请先配置：
#     cp build/.env.example build/.env
#     # 编辑 .env 填入实际的 WECHAT_WEBHOOK_URL
#
# 使用示例：
#   bash build/publish_release.sh
#   bash build/publish_release.sh --tag v1.3.1
#
# 可选参数：
#   -c, --changelog PATH     指定 changelog 文件（默认: CHANGELOG.md）
#       --version VERSION    强制指定版本号（否则从 changelog 自动解析）
#       --tag TAG            指定 Git tag（默认: v<版本号>）
#       --mac-pkg PATH       覆盖自动检测的 macOS 压缩包路径
#       --win-pkg PATH       覆盖自动检测的 Windows 压缩包路径
#       --wechat-webhook URL 覆盖 .env 中的企业微信 Webhook
#       --only-gitlab        仅发布到 GitLab
#       --only-github        仅发布到 GitHub
#   -h, --help               显示帮助
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# 加载环境变量配置文件
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

CHANGELOG="$PROJECT_DIR/CHANGELOG.md"
TAG=""
VERSION_OVERRIDE=""
MAC_PKG=""
WIN_PKG=""
PUBLISH_GITHUB=1
PUBLISH_GITLAB=1
# 企微 Webhook（从环境变量或 .env 读取）
WECHAT_WEBHOOK_URL="${WECHAT_WEBHOOK_URL:-}"

print_usage() {
  cat <<EOF
用法：
  bash build/publish_release.sh [选项]

选项：
  -c, --changelog PATH     指定 changelog 文件（默认: CHANGELOG.md）
      --version VERSION    强制指定版本号（否则从 changelog 自动解析）
      --tag TAG            指定 Git tag（默认: v<版本号>）
      --mac-pkg PATH       覆盖自动检测的 macOS 压缩包路径
      --win-pkg PATH       覆盖自动检测的 Windows 压缩包路径
      --wechat-webhook URL 企业微信 Webhook（也可通过环境变量 WECHAT_WEBHOOK_URL 提供）
      --only-gitlab        仅发布到 GitLab，不创建/更新 GitHub Release
      --only-github        仅发布到 GitHub，不创建/更新 GitLab Release
  -h, --help               显示本帮助
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--changelog)
      CHANGELOG="$2"
      shift 2
      ;;
    --version)
      VERSION_OVERRIDE="$2"
      shift 2
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --mac-pkg)
      MAC_PKG="$2"
      shift 2
      ;;
    --win-pkg)
      WIN_PKG="$2"
      shift 2
      ;;
    --wechat-webhook)
      WECHAT_WEBHOOK_URL="$2"
      shift 2
      ;;
    --only-gitlab)
      PUBLISH_GITHUB=0
      PUBLISH_GITLAB=1
      shift 1
      ;;
    --only-github)
      PUBLISH_GITHUB=1
      PUBLISH_GITLAB=0
      shift 1
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      print_usage
      exit 1
      ;;
  esac
done

# 基础依赖检查
NEEDED_CMDS=(git curl python)
if [[ "$PUBLISH_GITHUB" -eq 1 ]]; then
  NEEDED_CMDS+=(gh)
fi
if [[ "$PUBLISH_GITLAB" -eq 1 ]]; then
  NEEDED_CMDS+=(glab)
fi
for cmd in "${NEEDED_CMDS[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "❌ 错误: 未找到命令 '$cmd'，请先安装并加入 PATH。" >&2
    exit 1
  fi
done

# 检查 changelog
if [[ ! -f "$CHANGELOG" ]]; then
  echo "❌ 错误: 找不到 CHANGELOG 文件: $CHANGELOG" >&2
  exit 1
fi

# 解析版本号
if [[ -n "$VERSION_OVERRIDE" ]]; then
  VERSION="$VERSION_OVERRIDE"
else
  VERSION=$(grep -E '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' "$CHANGELOG" | head -n1 | sed -E 's/^## \[([0-9]+\.[0-9]+\.[0-9]+)\].*/\1/') || true
fi

if [[ -z "${VERSION:-}" ]]; then
  echo "❌ 错误: 无法从 $CHANGELOG 中解析最新版本号，请检查格式。" >&2
  exit 1
fi

# 解析发布说明
RELEASE_NOTES=$(awk -v ver="$VERSION" '
  index($0, "## [" ver "]") == 1 { in_block=1; next }
  in_block && /^## \[[0-9]+\.[0-9]+\.[0-9]+\]/ { exit }
  in_block && /^---$/ { exit }
  in_block { print }
' "$CHANGELOG")

if [[ -z "${RELEASE_NOTES:-}" ]]; then
  echo "⚠️ 警告: 未能从 CHANGELOG 中提取版本 ""$VERSION"" 的详细更新日志，发布说明将为空。" >&2
fi

# 计算 tag & 标题
if [[ -z "$TAG" ]]; then
  TAG="v$VERSION"
fi
RELEASE_TITLE="Dify Chat Tester v$VERSION"

# 自动查找默认压缩包（可被命令行参数覆盖）
if [[ -z "$MAC_PKG" ]]; then
  MAC_PKG=$(ls -t "$PROJECT_DIR"/dify_chat_tester_macos_v*.tar.gz 2>/dev/null | head -n1 || true)
fi
if [[ -z "$WIN_PKG" ]]; then
  WIN_PKG=$(ls -t "$PROJECT_DIR"/dify_chat_tester_windows_v*.zip 2>/dev/null | head -n1 || true)
fi

# 校验压缩包
if [[ -z "$MAC_PKG" || ! -f "$MAC_PKG" ]]; then
  echo "❌ 错误: 未找到 macOS 发布包，请先执行 build/build_macos.sh 或通过 --mac-pkg 指定。" >&2
  exit 1
fi
if [[ -z "$WIN_PKG" || ! -f "$WIN_PKG" ]]; then
  echo "❌ 错误: 未找到 Windows 发布包，请先执行 Windows 打包流程或通过 --win-pkg 指定。" >&2
  exit 1
fi

# 读取远程仓库信息
GITHUB_REMOTE=""
GITLAB_REMOTE=""

if [[ "$PUBLISH_GITHUB" -eq 1 ]]; then
  GITHUB_REMOTE=$(git remote get-url origin 2>/dev/null || true)
  if [[ -z "$GITHUB_REMOTE" ]]; then
    echo "❌ 错误: 未找到 GitHub 远程 origin，但当前配置为需要发布 GitHub Release。" >&2
    exit 1
  fi
fi

if [[ "$PUBLISH_GITLAB" -eq 1 ]]; then
  GITLAB_REMOTE=$(git remote get-url gitlab 2>/dev/null || true)
  if [[ -z "$GITLAB_REMOTE" ]]; then
    echo "⚠️ 警告: 未找到 GitLab 远程 gitlab，将无法创建 GitLab Release。" >&2
  fi
fi

GITLAB_PROJECT=""
if [[ -n "$GITLAB_REMOTE" ]]; then
  # 从 URL 提取类似 Mison/dify-chat-tester 的项目路径
  GITLAB_PROJECT=$(echo "$GITLAB_REMOTE" | sed -E 's#https?://[^/]+/##; s#\.git$##')
fi

# 当前分支（用于生成 GitLab CHANGELOG 链接），获取失败则回退到 main
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo main)

# GitLab 上的 CHANGELOG 远程链接（如果配置了 gitlab 远程）
GITLAB_CHANGELOG_URL=""
if [[ -n "$GITLAB_REMOTE" ]]; then
  GITLAB_CHANGELOG_URL="${GITLAB_REMOTE%.git}/-/blob/${CURRENT_BRANCH}/CHANGELOG.md"
fi

# 汇总信息并请求确认
MAC_SIZE=$(stat -f "%z" "$MAC_PKG" 2>/dev/null || echo "-")
WIN_SIZE=$(stat -f "%z" "$WIN_PKG" 2>/dev/null || echo "-")

echo "=========================================="
echo "🔥 即将发布新版本"
echo "------------------------------------------"
echo "项目目录:       $PROJECT_DIR"
echo "版本号:         $VERSION"
echo "Git tag:        $TAG"
echo "Release 标题:   $RELEASE_TITLE"
if [[ -n "$GITLAB_CHANGELOG_URL" ]]; then
  echo "CHANGELOG:      $GITLAB_CHANGELOG_URL"
else
  echo "CHANGELOG:      $CHANGELOG"
fi
if [[ "$PUBLISH_GITHUB" -eq 1 ]]; then
  echo "GitHub 远程:    ${GITHUB_REMOTE:-未配置}"
else
  echo "GitHub 远程:    已禁用 (仅发布 GitLab)"
fi
if [[ "$PUBLISH_GITLAB" -eq 1 ]]; then
  if [[ -n "$GITLAB_REMOTE" ]]; then
    echo "GitLab 远程:    $GITLAB_REMOTE (项目: $GITLAB_PROJECT)"
  else
    echo "GitLab 远程:    未配置 (将跳过 GitLab Release)"
  fi
else
  echo "GitLab 远程:    已禁用 (仅发布 GitHub)"
fi

echo ""
echo "附件(1): macOS 发布包"
echo "  路径: $MAC_PKG"
echo "  大小: $MAC_SIZE 字节"
echo "附件(2): Windows 发布包"
echo "  路径: $WIN_PKG"
echo "  大小: $WIN_SIZE 字节"

echo ""
if [[ -n "$WECHAT_WEBHOOK_URL" ]]; then
  echo "企业微信 Webhook: 已配置 (${WECHAT_WEBHOOK_URL:0:40}...)"
else
  echo "企业微信 Webhook: 未配置 (将跳过群消息推送)"
fi

echo ""
echo "=== 发布说明（CHANGELOG 摘要） ==="
if [[ -n "$RELEASE_NOTES" ]]; then
  echo "$RELEASE_NOTES" | sed 's/^/  /'
else
  echo "  (无内容)"
fi
echo "=========================================="
echo ""

echo "默认值: Y（直接回车将继续执行完整发布流程）"
read -r -p "请确认以上信息无误后继续执行发布操作？[Y/n] " CONFIRM
CONFIRM=${CONFIRM:-Y}
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "已取消发布。"
  exit 0
fi

# 检查是否已存在同名 GitHub Release
SKIP_GH_RELEASE=0
if [[ "$PUBLISH_GITHUB" -eq 1 ]]; then
  if gh release view "$TAG" >/dev/null 2>&1; then
    echo "⚠️ 检测到 GitHub 上已存在 tag 为 $TAG 的 Release。"
    echo "    默认值: N（直接回车表示跳过，不会删除已有 Release）"
    read -r -p "是否重新发布（删除后重建）该 GitHub Release？[y/N, 默认 N 跳过] " GH_REDO
    if [[ "$GH_REDO" =~ ^[Yy]$ ]]; then
      echo "🗑️ 正在删除已有 GitHub Release $TAG..."
      gh release delete "$TAG" -y
    else
      echo "ℹ️ 已选择跳过 GitHub Release 创建。"
      SKIP_GH_RELEASE=1
    fi
  fi
fi

# 检查是否已存在同名 GitLab Release（如果配置了 gitlab 远程）
SKIP_GL_RELEASE=0
if [[ "$PUBLISH_GITLAB" -eq 1 && -n "$GITLAB_PROJECT" ]]; then
  if glab release view "$TAG" >/dev/null 2>&1; then
    echo "⚠️ 检测到 GitLab 上已存在 tag 为 $TAG 的 Release。"
    echo "    默认值: N（直接回车表示跳过，不会删除已有 Release）"
    read -r -p "是否重新发布（删除后重建）该 GitLab Release？[y/N, 默认 N 跳过] " GL_REDO
    if [[ "$GL_REDO" =~ ^[Yy]$ ]]; then
      echo "🗑️ 正在删除已有 GitLab Release $TAG..."
      GITLAB_REPO="$GITLAB_PROJECT" glab release delete "$TAG" -y
    else
      echo "ℹ️ 已选择跳过 GitLab Release 创建。"
      SKIP_GL_RELEASE=1
    fi
  fi
fi

# 创建 GitHub Release（除非选择跳过）
if [[ "$PUBLISH_GITHUB" -eq 1 && "$SKIP_GH_RELEASE" -eq 0 ]]; then
  echo "🚀 正在创建 GitHub Release..."
  GH_CMD=(
    gh release create "$TAG" "$MAC_PKG" "$WIN_PKG" \
      --title "$RELEASE_TITLE" \
      --notes "$RELEASE_NOTES"
  )
  "${GH_CMD[@]}"
  echo "✅ GitHub Release 创建完成。"
else
  echo "⚠️ 本次已跳过 GitHub Release 创建。"
fi

# 创建 GitLab Release（如果配置了 gitlab 远程且未选择跳过）
if [[ "$PUBLISH_GITLAB" -eq 1 && -n "$GITLAB_PROJECT" ]]; then
  if [[ "$SKIP_GL_RELEASE" -eq 0 ]]; then
    echo "🚀 正在创建 GitLab Release..."
    GITLAB_REPO="$GITLAB_PROJECT" glab release create "$TAG" \
      "$MAC_PKG" "$WIN_PKG" \
      --name "$RELEASE_TITLE" \
      --notes "$RELEASE_NOTES"
    echo "✅ GitLab Release 创建完成。"
  else
    echo "⚠️ 本次已跳过 GitLab Release 创建。"
  fi
else
  echo "⚠️ 已跳过 GitLab Release（未检测到 gitlab 远程）。"
fi
# 推送企业微信群消息（使用 template_card 文本通知卡片）
if [[ -n "$WECHAT_WEBHOOK_URL" ]]; then
  echo "📢 正在推送企业微信群通知..."
  WECOM_JSON=$(WE_TITLE="$RELEASE_TITLE" WE_TAG="$TAG" WE_NOTES="$RELEASE_NOTES" WE_CHANGELOG_URL="${GITLAB_CHANGELOG_URL:-}" python - <<'PY'
import json
import os


title = os.environ.get("WE_TITLE", "")  # 例如: "Dify Chat Tester v1.3.1"
tag = os.environ.get("WE_TAG", "")      # 例如: "v1.3.1"
notes = os.environ.get("WE_NOTES", "")
changelog_url = os.environ.get("WE_CHANGELOG_URL", "")

# 将 CHANGELOG 片段按「新增 / 优化 / 修复」分组做摘要
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
    if not line.startswith("-"):
        # 非列表行直接跳过，避免把整段说明塞进摘要
        continue
    if current is None:
        # 没有显式标题，就算在「新增」里
        current = "新增"
    text = line.lstrip("-• ").strip()
    if not text:
        continue
    sections[current].append(f"· {text}")

main_title = title or "Dify Chat Tester 发布"
sub_title = f"Tag: {tag}" if tag else "版本发布通知"

# 二级标题 + 文本列表：分三块展示「新增 / 优化 / 修复」
horizontal_content_list = []
for key in ("新增", "优化", "修复"):
    items = sections.get(key) or []
    if not items:
        continue
    # 每类最多取 3 条，长度控制在 120 字符左右
    summary = "\n".join(items[:3])[:120]
    horizontal_content_list.append({
        "keyname": key,
        "value": summary,
    })

# 如果三类都为空，兜底给一条通用摘要
if not horizontal_content_list and notes.strip():
    fallback = "".join(notes.splitlines())
    horizontal_content_list.append({
        "keyname": "更新摘要",
        "value": fallback[:120],
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

payload = {
    "msgtype": "template_card",
    "template_card": {
        "card_type": "text_notice",
        "source": {
            "desc": "Dify Chat Tester 发布",
            "desc_color": 0,
        },
        "main_title": {
            "title": main_title,
            "desc": sub_title,
        },
        # 不使用 emphasis_content，避免中间版本号过大占空间
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
    -d "$WECOM_JSON" >/dev/null

  echo "✅ 企业微信通知已发送。"
else
  echo "ℹ️ 未配置企业微信 Webhook，已跳过群消息推送。"
fi
echo "🎉 全部发布流程完成。"
