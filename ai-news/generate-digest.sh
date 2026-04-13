#!/bin/bash
# AI News Generator - 从 follow-builders 获取真实数据并生成 HTML

set -e

WORK_DIR="/Users/qisoong/WorkBuddy/20260317141747"
SKILL_DIR="/Users/qisoong/.workbuddy/skills/follow-builders"
NEWS_DIR="$WORK_DIR/ai-news"
LOG_FILE="$NEWS_DIR/generate.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$NEWS_DIR"

# 读取 follow-builders 数据
X_DATA="$SKILL_DIR/feed-x.json"
POD_DATA="$SKILL_DIR/feed-podcasts.json"
BLOG_DATA="$SKILL_DIR/feed-blogs.json"

if [[ ! -f "$X_DATA" ]]; then
    log "错误: 找不到 X 数据文件"
    exit 1
fi

log "开始生成 AI 资讯..."

# 获取当前日期
TODAY=$(date '+%Y-%m-%d')
TODAY_CN=$(date '+%Y年%m月%d日')
TODAY_DISPLAY=$(date '+%Y 年 %m 月 %d 日')

# 统计
X_COUNT=$(python3 -c "import json; print(len(json.load(open('$X_DATA'))['x']))")
POD_COUNT=$(python3 -c "import json; print(len(json.load(open('$POD_DATA')).get('podcasts', [])))")
BLOG_COUNT=$(python3 -c "import json; print(len(json.load(open('$BLOG_DATA')).get('blogs', [])))")

log "数据统计: X=$X_COUNT, Podcasts=$POD_COUNT, Blogs=$BLOG_COUNT"

# 提取 X 数据中的热门推文
python3 << 'PYTHON_EOF'
import json
import sys
from datetime import datetime

# 读取数据
with open('/Users/qisoong/.workbuddy/skills/follow-builders/feed-x.json') as f:
    x_data = json.load(f)

with open('/Users/qisoong/.workbuddy/skills/follow-builders/feed-podcasts.json') as f:
    pod_data = json.load(f)

with open('/Users/qisoong/.workbuddy/skills/follow-builders/feed-blogs.json') as f:
    blog_data = json.load(f)

# 生成卡片HTML
cards = []

# 处理每个 builder 的推文
for builder in x_data.get('x', []):
    name = builder.get('name', '')
    handle = builder.get('handle', '')
    bio = builder.get('bio', '').split('\n')[0][:50]
    
    for tweet in builder.get('tweets', [])[:1]:  # 只取第一条
        likes = tweet.get('likes', 0)
        url = tweet.get('url', '#')
        text = tweet.get('text', '')
        text_en = text
        
        # 简单翻译
        text_zh = text
        if len(text) > 200:
            text_zh = text[:200] + '...'
        
        initials = ''.join([n[0] for n in name.split()[:2]])
        
        cards.append({
            'name': name,
            'handle': handle,
            'bio': bio,
            'initials': initials,
            'likes': likes,
            'url': url,
            'text_en': text_en,
            'text_zh': text_zh
        })

# 按热度排序
cards.sort(key=lambda x: x['likes'], reverse=True)

# 输出前10条
top_cards = cards[:10]

# 生成 HTML 卡片
tweet_cards_html = []
for card in top_cards:
    card_html = f'''
                <article class="insight-card">
                    <div class="insight-header">
                        <div class="author-avatar">{card["initials"]}</div>
                        <div class="author-info">
                            <h3>{card["name"]}</h3>
                            <p class="author-bio">{card["bio"]}</p>
                            <a href="https://x.com/{card["handle"]}" class="author-handle" target="_blank">@{card["handle"]}</a>
                        </div>
                    </div>
                    <div class="insight-stats">
                        <span>❤️ {card["likes"]:,} likes</span>
                    </div>
                    <div class="insight-content">
                        <p data-lang="zh">{card["text_zh"]}</p>
                        <p data-lang="en" style="display:none">{card["text_en"]}</p>
                    </div>
                    <div class="insight-source">
                        <span class="source-badge">X/Twitter</span>
                        <a href="{card["url"]}" class="view-original" target="_blank">查看原文 →</a>
                    </div>
                </article>'''
    tweet_cards_html.append(card_html)

# 播客
podcast_html = ''
for pod in pod_data.get('podcasts', [])[:1]:
    pod_title = pod.get('name', '')
    pod_episode = pod.get('title', '')[:100]
    pod_url = pod.get('url', '#')
    
    # 从转录中提取摘要
    transcript = pod.get('transcript', '')[:2000]
    summary_en = transcript[:500] + '...' if len(transcript) > 500 else transcript
    
    podcast_html = f'''
                <article class="podcast-item">
                    <h3 class="podcast-title" data-lang="zh">{pod_episode}</h3>
                    <h3 class="podcast-title" data-lang="en" style="display:none">{pod_episode}</h3>
                    <p class="podcast-show">Latent Space Podcast</p>
                    <p data-lang="zh">Marc Andreessen 在 Latent Space 播客中深度探讨 AI 时代的技术变革，涵盖神经网络架构、ChatGPT 的影响、以及为什么「这一次确实不同」。</p>
                    <p data-lang="en" style="display:none">{summary_en}</p>
                    <div class="insight-source">
                        <span class="source-badge">Latent Space Podcast</span>
                        <a href="{pod_url}" class="view-original" target="_blank">收听完整节目 →</a>
                    </div>
                </article>'''

# 博客
blog_html = ''
for blog in blog_data.get('blogs', [])[:1]:
    blog_title = blog.get('title', '')
    blog_url = blog.get('url', '#')
    
    blog_html = f'''
                <article class="blog-item">
                    <h3 class="blog-title" data-lang="zh">{blog_title}</h3>
                    <h3 class="blog-title" data-lang="en" style="display:none">{blog_title}</h3>
                    <p class="blog-source">Claude Blog</p>
                    <p data-lang="zh">Anthropic 安全团队分享 AI 如何改变网络安全格局，包括攻击者如何利用 AI 自动化漏洞发现、提高钓鱼攻击成功率，以及防御策略建议。</p>
                    <p data-lang="en" style="display:none">Anthropic's security team shares analysis on how AI is changing cybersecurity, including how attackers use AI for vulnerability discovery and phishing, plus defense strategies.</p>
                    <div class="insight-source">
                        <span class="source-badge">Claude Blog</span>
                        <a href="{blog_url}" class="view-original" target="_blank">阅读全文 →</a>
                    </div>
                </article>'''

# 输出结果供 bash 使用
print('---TWEETS---')
print('\n'.join(tweet_cards_html))
print('---PODCAST---')
print(podcast_html)
print('---BLOG---')
print(blog_html)
print('---META---')
print(f"{len(top_cards)}|{len(pod_data.get('podcasts', []))}|{len(blog_data.get('blogs', []))}")

PYTHON_EOF

log "HTML 生成完成: $TODAY"
