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

# 输出文件名
ARCHIVE_FILE="${TODAY}.html"

# 统计
X_COUNT=$(python3 -c "import json; print(len(json.load(open('$X_DATA'))['x']))")
POD_COUNT=$(python3 -c "import json; print(len(json.load(open('$POD_DATA')).get('podcasts', [])))")
BLOG_COUNT=$(python3 -c "import json; print(len(json.load(open('$BLOG_DATA')).get('blogs', [])))")

log "数据统计: X=$X_COUNT, Podcasts=$POD_COUNT, Blogs=$BLOG_COUNT"

# 用 Python 生成完整 HTML
python3 << 'PYEOF'
import json
import os
import re

X_DATA = '/Users/qisoong/.workbuddy/skills/follow-builders/feed-x.json'
POD_DATA = '/Users/qisoong/.workbuddy/skills/follow-builders/feed-podcasts.json'
BLOG_DATA = '/Users/qisoong/.workbuddy/skills/follow-builders/feed-blogs.json'

with open(X_DATA) as f:
    x_data = json.load(f)

with open(POD_DATA) as f:
    pod_data = json.load(f)

with open(BLOG_DATA) as f:
    blog_data = json.load(f)

# 获取日期变量
TODAY = os.environ.get('TODAY', '2026-04-14')
TODAY_CN = os.environ.get('TODAY_CN', '2026年04月14日')
TODAY_DISPLAY = os.environ.get('TODAY_DISPLAY', '2026 年 04 月 14 日')
ARCHIVE_FILE = os.environ.get('ARCHIVE_FILE', '2026-04-14.html')

# 生成卡片
cards = []
for builder in x_data.get('x', []):
    name = builder.get('name', '')
    handle = builder.get('handle', '')
    bio = builder.get('bio', '').split('\n')[0][:50]
    
    for tweet in builder.get('tweets', [])[:1]:
        likes = tweet.get('likes', 0)
        url = tweet.get('url', '#')
        text = tweet.get('text', '')
        text_en = text
        text_zh = text[:200] + '...' if len(text) > 200 else text
        initials = ''.join([n[0] for n in name.split()[:2]])
        
        cards.append({
            'name': name, 'handle': handle, 'bio': bio,
            'initials': initials, 'likes': likes, 'url': url,
            'text_en': text_en, 'text_zh': text_zh
        })

cards.sort(key=lambda x: x['likes'], reverse=True)
top_cards = cards[:10]

# 生成卡片 HTML
tweet_cards_html = ''
for card in top_cards:
    text_en = card['text_en'].replace('"', '&quot;').replace("'", '&#39;')
    text_zh = card['text_zh'].replace('"', '&quot;').replace("'", '&#39;')
    tweet_cards_html += f'''
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
                        <p data-lang="zh">{text_zh}</p>
                        <p data-lang="en" style="display:none">{text_en}</p>
                    </div>
                    <div class="insight-source">
                        <span class="source-badge">X/Twitter</span>
                        <a href="{card["url"]}" class="view-original" target="_blank">查看原文 →</a>
                    </div>
                </article>'''

# 播客
podcast_html = ''
for pod in pod_data.get('podcasts', [])[:1]:
    pod_episode = pod.get('title', '')[:100]
    pod_url = pod.get('url', '#')
    transcript = pod.get('transcript', '')[:2000]
    summary_en = transcript[:500] + '...' if len(transcript) > 500 else transcript
    podcast_html = f'''
                <article class="podcast-item">
                    <h3 class="podcast-title" data-lang="zh">{pod_episode}</h3>
                    <h3 class="podcast-title" data-lang="en" style="display:none">{pod_episode}</h3>
                    <p class="podcast-show">Latent Space Podcast</p>
                    <p data-lang="zh">Marc Andreessen 在 Latent Space 播客中深度探讨 AI 时代的技术变革。</p>
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
                    <p data-lang="zh">Anthropic 安全团队分享 AI 如何改变网络安全格局。</p>
                    <p data-lang="en" style="display:none">Anthropic security team shares insights on AI cybersecurity.</p>
                    <div class="insight-source">
                        <span class="source-badge">Claude Blog</span>
                        <a href="{blog_url}" class="view-original" target="_blank">阅读全文 →</a>
                    </div>
                </article>'''

# 历史存档
archives_html = ''
archive_files = sorted([f for f in os.listdir('.') if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f)], reverse=True)[:10]
for f in archive_files:
    if f != f'{TODAY}.html':
        date_part = f.replace('.html', '')
        year = date_part[:4]
        month = str(int(date_part[5:7]))
        day = str(int(date_part[8:10]))
        display = f'{year}年{month}月{day}日'
        archives_html += f'\n                <a href="{date_part}.html" class="archive-item">{display}</a>'

# 完整 HTML
archive_section = f'''
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">{archives_html}
            </div>
        </div>''' if archives_html else ''

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Builders · {TODAY_CN}</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
    <style>
        :root {{--bg:#fafaf9;--text:#1c1917;--text-secondary:#78716c;--accent:#ea580c;--border:#e7e5e4;--tag-bg:#f5f5f4}}
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-size:15px}}
        .controls{{position:sticky;top:0;z-index:100;background:rgba(250,250,249,.95);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);padding:12px 40px;display:flex;justify-content:space-between;align-items:center}}
        .back-link{{color:var(--text-secondary);text-decoration:none;font-size:14px}}
        .lang-switch{{display:flex;gap:6px}}
        .lang-btn{{padding:6px 14px;border:1px solid var(--border);background:#fff;cursor:pointer;font-size:13px;border-radius:16px;transition:all .2s}}
        .lang-btn:hover{{background:var(--tag-bg)}}
        .lang-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
        .audio-btn{{padding:6px 16px;background:var(--text);color:#fff;border:none;cursor:pointer;font-size:13px;border-radius:16px;display:flex;align-items:center;gap:6px}}
        .audio-btn:hover{{opacity:.85}}
        .audio-btn.playing{{background:var(--accent)}}
        .page-header{{text-align:center;padding:60px 40px 40px;border-bottom:1px solid var(--border)}}
        .page-header h1{{font-family:'Noto Serif SC',serif;font-size:28px;font-weight:600;margin-bottom:8px}}
        .page-header .subtitle{{color:var(--text-secondary);font-size:14px}}
        .container{{max-width:800px;margin:0 auto;padding:40px 20px}}
        .insight-card{{background:#fff;border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px}}
        .insight-header{{display:flex;gap:14px;margin-bottom:16px}}
        .author-avatar{{width:48px;height:48px;background:var(--accent);color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:16px;flex-shrink:0}}
        .author-info h3{{font-size:16px;margin-bottom:2px}}
        .author-bio{{font-size:13px;color:var(--text-secondary);margin-bottom:4px}}
        .author-handle{{font-size:13px;color:var(--accent);text-decoration:none}}
        .insight-stats{{margin-bottom:14px;font-size:13px;color:var(--text-secondary)}}
        .insight-content{{font-size:15px;line-height:1.7;margin-bottom:16px}}
        .insight-content p{{margin-bottom:12px}}
        .insight-source{{display:flex;align-items:center;justify-content:space-between;padding-top:14px;border-top:1px solid var(--border)}}
        .source-badge{{font-size:12px;background:var(--tag-bg);padding:4px 10px;border-radius:12px;color:var(--text-secondary)}}
        .view-original{{color:var(--accent);text-decoration:none;font-size:14px;font-weight:500}}
        .podcast-item,.blog-item{{background:#fff;border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px}}
        .podcast-title,.blog-title{{font-size:17px;margin-bottom:8px}}
        .podcast-show,.blog-source{{font-size:13px;color:var(--text-secondary);margin-bottom:12px}}
        .archive-section{{border-top:1px solid var(--border);padding-top:40px;margin-top:40px}}
        .archive-section h3{{font-size:14px;color:var(--text-secondary);margin-bottom:16px}}
        .archive-list{{display:flex;flex-wrap:wrap;gap:10px}}
        .archive-item{{padding:8px 16px;background:var(--tag-bg);border-radius:8px;color:var(--text);text-decoration:none;font-size:14px;transition:all .2s}}
        .archive-item:hover{{background:var(--accent);color:#fff}}
        .footer{{text-align:center;padding:40px;color:var(--text-secondary);font-size:13px;border-top:1px solid var(--border)}}
        .footer a{{color:var(--accent);text-decoration:none}}
    </style>
</head>
<body>
    <div class="controls">
        <a href="../index.html" class="back-link">← 返回首页</a>
        <div style="display:flex;gap:10px;align-items:center">
            <div class="lang-switch">
                <button class="lang-btn active" data-lang="zh">中文</button>
                <button class="lang-btn" data-lang="en">EN</button>
            </div>
            <button class="audio-btn" id="audioBtn" onclick="toggleAudio()">
                <span id="audioIcon">🔊</span><span id="audioText">朗读</span>
            </button>
        </div>
    </div>
    <div class="page-header">
        <h1>🤖 AI Builders 资讯</h1>
        <p class="subtitle">{TODAY_DISPLAY} · 每日追踪 AI 领域最前沿的开发者动态</p>
    </div>
    <div class="container">
        {tweet_cards_html}
        {podcast_html}
        {blog_html}
        {archive_section}
    </div>
    <div class="footer">
        <p>数据来源：<a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a></p>
    </div>
    <script>
        document.querySelectorAll('.lang-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const lang = btn.dataset.lang;
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('[data-lang]').forEach(el => {{
                    el.style.display = el.dataset.lang === lang ? 'block' : 'none';
                }});
            }});
        }});
        let utterance = null, isPlaying = false;
        function toggleAudio() {{
            const btn = document.getElementById('audioBtn');
            const icon = document.getElementById('audioIcon');
            const text = document.getElementById('audioText');
            if (isPlaying) {{
                speechSynthesis.cancel();
                isPlaying = false;
                btn.classList.remove('playing');
                icon.textContent = '🔊';
                text.textContent = '朗读';
            }} else {{
                const lang = document.querySelector('.lang-btn.active').dataset.lang;
                const texts = [];
                document.querySelectorAll('.insight-content p, .podcast-item p, .blog-item p').forEach(el => {{
                    if (el.dataset.lang === lang && el.style.display !== 'none') texts.push(el.textContent);
                }});
                let fullText = texts.join('。\\n\\n').replace(/\\.\\s/g, '。').replace(/!\\s/g, '！').replace(/\\?\\s/g, '？');
                utterance = new SpeechSynthesisUtterance(fullText);
                utterance.lang = lang === 'zh' ? 'zh-CN' : 'en-US';
                utterance.rate = 0.85;
                utterance.pitch = 0.95;
                const voices = speechSynthesis.getVoices();
                const preferredVoice = voices.find(v => (lang === 'zh' && v.lang.includes('zh')) || (lang === 'zh' && (v.name.includes('Ting') || v.name.includes('Mei')))) || voices.find(v => v.lang.includes(lang === 'zh' ? 'zh' : 'en'));
                if (preferredVoice) utterance.voice = preferredVoice;
                utterance.onend = () => {{ isPlaying = false; btn.classList.remove('playing'); icon.textContent = '🔊'; text.textContent = '朗读'; }};
                speechSynthesis.speak(utterance);
                isPlaying = true;
                btn.classList.add('playing');
                icon.textContent = '⏸️';
                text.textContent = '暂停';
            }}
        }}
        if (speechSynthesis.onvoiceschanged !== undefined) {{ speechSynthesis.onvoiceschanged = () => {{}}; }}
    </script>
</body>
</html>'''

# 写入文件
with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Generated: {ARCHIVE_FILE}')
PYEOF

log "生成存档: $ARCHIVE_FILE"

# 复制到 index.html
cp "$ARCHIVE_FILE" "index.html"
log "更新入口: index.html"

# Git 提交
cd "$WORK_DIR"
git add ai-news/
git commit -m "feat: 更新 AI 资讯 ${TODAY}" 2>/dev/null || log "没有变更需要提交"
git push

log "完成！"
