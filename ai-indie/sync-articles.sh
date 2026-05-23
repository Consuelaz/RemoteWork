#!/bin/bash
# sync-articles.sh - 将 ~/articles/ 的最新公众号文章同步到 ai-indie/ 目录
# 用法: bash sync-articles.sh

set -e

WORK_DIR="/Users/qisoong/WorkBuddy/20260317141747"
AI_INDIE_DIR="$WORK_DIR/ai-indie"
ARTICLES_DIR="$HOME/articles"
LOG_FILE="$AI_INDIE_DIR/sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$AI_INDIE_DIR"

# 1. 复制 ~/articles/ 中所有 ai-indie-*.html 到 ai-indie 目录
NEW_COUNT=0
for f in "$ARTICLES_DIR"/ai-indie-*.html; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    if [ ! -f "$AI_INDIE_DIR/$fname" ]; then
        cp "$f" "$AI_INDIE_DIR/$fname"
        log "新文章: $fname"
        NEW_COUNT=$((NEW_COUNT + 1))
    fi
done

# 2. 用 Python 更新 index.html 中的文章列表
python3 << 'PYEOF'
import os, re, glob

AI_INDIE_DIR = '/Users/qisoong/WorkBuddy/20260317141747/ai-indie'
INDEX_FILE = os.path.join(AI_INDIE_DIR, 'index.html')

# 收集所有 HTML 文件
html_files = sorted(glob.glob(os.path.join(AI_INDIE_DIR, 'ai-indie-*.html')), reverse=True)

# 提取日期和标题
articles = []
for f in html_files:
    fname = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # 提取日期（从文件名）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    date_str = date_match.group(1) if date_match else ''
    
    # 提取标题
    title = ''
    # 尝试 h1 标签
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if h1_match:
        title = re.sub(r'<br\s*/?>', ' ', h1_match.group(1))
        title = re.sub(r'<[^>]+>', '', title).strip()
    # 如果 h1 为空，尝试 title 标签
    if not title:
        title_match = re.search(r'<title>(.*?)</title>', content)
        if title_match:
            title = title_match.group(1)
            # 去掉后缀 " | AI独立派"
            title = re.sub(r'\s*\|\s*AI独立派\s*$', '', title)
    
    if date_str and title:
        articles.append({
            'date': date_str,
            'file': fname,
            'title': title
        })

# 生成 JS 数组
js_content = '    const ARTICLES = [\n'
for a in articles:
    escaped_title = a['title'].replace("'", "\\'")
    js_content += f"        {{ date: '{a['date']}', file: '{a['file']}', title: '{escaped_title}' }},\n"
js_content += '    ];\n'

# 读取 index.html
with open(INDEX_FILE, 'r', encoding='utf-8') as fh:
    index_content = fh.read()

# 替换 ARTICLES 数组
pattern = r'    const ARTICLES = \[.*?\];'
new_content = re.sub(pattern, js_content, index_content, flags=re.DOTALL)

with open(INDEX_FILE, 'w', encoding='utf-8') as fh:
    fh.write(new_content)

print(f'更新文章列表: {len(articles)} 篇')
PYEOF

if [ $NEW_COUNT -gt 0 ]; then
    log "同步完成: $NEW_COUNT 篇新文章"
else
    log "同步完成: 无新文章"
fi
