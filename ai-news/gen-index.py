#!/usr/bin/env python3
"""
AI 资讯生成脚本
规则：5条X + 3个播客 + 2篇博客 = 10篇
- X: 按点赞数排序，取前5条
- 播客: 分段提取精华（每段约1500字符），不足则重复
- 博客: 分段提取精华（每段约1500字符），不足则重复
"""
import json
import os
import re
from datetime import datetime

# ============ 数据路径 ============
SKILL_DIR = '/Users/qisoong/.workbuddy/skills/follow-builders'

# 读取数据
with open(f'{SKILL_DIR}/feed-x.json') as f:
    x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json') as f:
    pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json') as f:
    blog_data = json.load(f)

# ============ 规则配置 ============
RULE_X_COUNT = 5       # X 推文数量
RULE_POD_COUNT = 3     # 播客数量
RULE_BLOG_COUNT = 2    # 博客数量
RULE_TOTAL = RULE_X_COUNT + RULE_POD_COUNT + RULE_BLOG_COUNT  # 总计10篇

# 内容长度配置
X_TEXT_MAX = 500        # X 推文截断长度
POD_SEGMENT_LEN = 1500  # 播客每段长度
BLOG_SEGMENT_LEN = 1500 # 博客每段长度

# ============ 数据处理函数 ============
def extract_text_segment(text, start, length):
    """从文本中提取指定长度的段落"""
    if len(text) <= start:
        return None
    segment = text[start:start + length]
    # 清理格式
    segment = segment.replace('\r\n', '\n').replace('\n\n', '\n')
    # 找句子边界
    segment = segment.strip()
    if segment and segment[-1] not in '.。！？!?':
        # 尝试找到最后一个完整句子
        for punct in ['. ', '。', '！', '？', '! ', '? ']:
            last_punct = segment.rfind(punct)
            if last_punct > len(segment) // 2:
                segment = segment[:last_punct + 1]
                break
    return segment if segment else None

def gen_excerpt(text, max_len=200):
    """生成简短摘要"""
    text = text[:max_len].replace('\n', ' ').strip()
    return text + ('...' if len(text) >= max_len else '')

# ============ 收集内容 ============
all_items = []
article_num = 0

# ---------- 1. X 推文 ----------
tweets = []
for builder in x_data.get('x', []):
    name = builder.get('name', '')
    handle = builder.get('handle', '')
    bio = builder.get('bio', '').split('\n')[0][:50]
    initials = ''.join([n[0] for n in name.split()[:2]]) if name else '??'

    for tweet in builder.get('tweets', [])[:3]:  # 每位开发者取最多3条
        likes = tweet.get('likes', 0)
        url = tweet.get('url', '#')
        text = tweet.get('text', '')
        if text:
            tweets.append({
                'type': 'x', 'name': name, 'handle': handle, 'bio': bio,
                'initials': initials, 'likes': likes, 'url': url, 'text': text
            })

# 按点赞排序，取前 RULE_X_COUNT 条
tweets.sort(key=lambda x: x['likes'], reverse=True)
for t in tweets[:RULE_X_COUNT]:
    article_num += 1
    text = t['text'][:X_TEXT_MAX]
    all_items.append({
        'num': article_num, 'type': 'x', 'name': t['name'], 'handle': t['handle'],
        'bio': t['bio'], 'initials': t['initials'], 'likes': t['likes'],
        'url': t['url'], 'text': text, 'excerpt': gen_excerpt(t['text'], 100)
    })

# ---------- 2. 播客 ----------
podcasts = pod_data.get('podcasts', [])
pod_segments = []

# 把单个播客分成多个段落
for pod in podcasts:
    transcript = pod.get('transcript', '')
    if not transcript:
        continue
    title = pod.get('title', '')[:70]
    url = pod.get('url', '#')
    show = pod.get('show', 'AI Podcast')

    # 分段提取
    for start_pos in range(0, len(transcript), POD_SEGMENT_LEN):
        segment = extract_text_segment(transcript, start_pos, POD_SEGMENT_LEN)
        if segment and len(segment) > 100:
            pod_segments.append({
                'title': title,
                'url': url,
                'show': f'🎙️ {show}',
                'segment': segment,
                'segment_idx': len(pod_segments) + 1
            })

# 取前 RULE_POD_COUNT 个播客段落
for i, pod_seg in enumerate(pod_segments[:RULE_POD_COUNT]):
    article_num += 1
    excerpt = gen_excerpt(pod_seg['segment'], 120)
    all_items.append({
        'num': article_num, 'type': 'podcast',
        'name': f"{pod_seg['title']} (Part {pod_seg['segment_idx']})",
        'bio': pod_seg['show'], 'initials': '🎙️',
        'likes': 0, 'url': pod_seg['url'],
        'text': pod_seg['segment'],
        'excerpt': excerpt
    })

# ---------- 3. 博客 ----------
blogs = blog_data.get('blogs', [])
blog_segments = []

for blog in blogs:
    content = blog.get('transcript', blog.get('content', ''))
    if not content:
        continue
    title = blog.get('title', '')[:70]
    url = blog.get('url', '#')
    source = blog.get('source', 'Tech Blog')

    # 分段提取
    for start_pos in range(0, len(content), BLOG_SEGMENT_LEN):
        segment = extract_text_segment(content, start_pos, BLOG_SEGMENT_LEN)
        if segment and len(segment) > 100:
            blog_segments.append({
                'title': title,
                'url': url,
                'source': f'📝 {source}',
                'segment': segment,
                'segment_idx': len(blog_segments) + 1
            })

# 取前 RULE_BLOG_COUNT 个博客段落
for i, blog_seg in enumerate(blog_segments[:RULE_BLOG_COUNT]):
    article_num += 1
    excerpt = gen_excerpt(blog_seg['segment'], 120)
    all_items.append({
        'num': article_num, 'type': 'blog',
        'name': f"{blog_seg['title']} (Part {blog_seg['segment_idx']})",
        'bio': blog_seg['source'], 'initials': '📝',
        'likes': 0, 'url': blog_seg['url'],
        'text': blog_seg['segment'],
        'excerpt': excerpt
    })

# ============ 生成 HTML ============
articles_html = ''
for item in all_items:
    num = item['num']
    text = item['text']
    excerpt = item.get('excerpt', gen_excerpt(text, 100))
    title = excerpt

    badge = {'x': 'X/Twitter', 'podcast': '🎙️ Podcast', 'blog': '📝 Blog'}.get(item['type'], '')

    articles_html += f'''
        <article class="article" data-article="{num}">
            <div class="article-header">
                <div class="article-left">
                    <span class="article-number">{num:02d}</span>
                    <div class="author-row">
                        <div class="author-avatar">{item['initials']}</div>
                        <div class="author-info">
                            <span class="author-name">{item['name']}</span>
                            <span class="author-bio">{item['bio']}</span>
                        </div>
                    </div>
                </div>
                <div class="article-actions">
                    <button class="action-btn" onclick="playArticle({num})">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        朗读
                    </button>
                </div>
            </div>
            <h2 data-lang="zh" class="show">{title}</h2>
            <h2 data-lang="en">{title}</h2>
            <div class="article-body">
                <p data-lang="zh" class="show">{text}</p>
                <p data-lang="en">{text}</p>
            </div>
            <div class="article-footer">
                <div class="article-stats">
                    <span>{badge}</span>
                    {f"<span>❤️ {item['likes']:,}</span>" if item['likes'] > 0 else ''}
                </div>
                <a href="{item['url']}" class="article-link" target="_blank">查看原文 →</a>
            </div>
        </article>'''

# ============ 历史存档 ============
archive_html = ''
archive_files = sorted([
    f for f in os.listdir('.')
    if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f)
    and f != 'index.html'
], reverse=True)

if archive_files:
    links = ''
    for f in archive_files[:5]:
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', f)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f'{year}年{int(month)}月{int(day)}日'
            links += f'<a href="{f}" class="archive-item">{date_str}</a>'
    archive_html = f'''
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">{links}
            </div>
        </div>'''

# ============ 页面模板 ============
today = datetime.now()
day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
date_en = f"{day_names[today.weekday()]}, {month_names[today.month]} {today.day}, {today.year}"

# 统计信息
x_count = len([i for i in all_items if i['type'] == 'x'])
pod_count = len([i for i in all_items if i['type'] == 'podcast'])
blog_count = len([i for i in all_items if i['type'] == 'blog'])

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Builders · {date_en}</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
    <style>
        :root {{--bg:#fafaf9;--text:#1c1917;--text-secondary:#78716c;--accent:#ea580c;--border:#e7e5e4;--tag-bg:#f5f5f4}}
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-size:15px}}
        .controls{{position:sticky;top:0;z-index:100;background:rgba(250,250,249,.95);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);padding:12px 40px;display:flex;justify-content:space-between;align-items:center}}
        .lang-switch{{display:flex;gap:6px}}
        .lang-btn{{padding:6px 14px;border:1px solid var(--border);background:white;cursor:pointer;font-size:13px;border-radius:16px;transition:all .2s}}
        .lang-btn.active{{background:var(--text);color:white;border-color:var(--text)}}
        .audio-controls{{display:flex;gap:8px;align-items:center}}
        .audio-btn{{padding:6px 14px;border:1px solid var(--border);background:white;cursor:pointer;font-size:13px;border-radius:16px;display:flex;align-items:center;gap:6px}}
        .audio-btn:hover{{background:var(--tag-bg)}}
        .audio-btn.playing{{background:var(--accent);color:white;border-color:var(--accent)}}
        .audio-btn svg, .action-btn svg{{width:12px;height:12px}}
        .voice-select{{padding:6px 10px;border:1px solid var(--border);border-radius:12px;font-size:12px;background:white;cursor:pointer}}
        .hero{{padding:40px 40px 30px;max-width:720px;margin:0 auto;border-bottom:1px solid var(--border)}}
        .date{{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:var(--accent);margin-bottom:12px}}
        .hero h1{{font-family:'Noto Serif SC',serif;font-size:1.8rem;font-weight:600;margin-bottom:12px}}
        .hero-sub{{font-size:14px;color:var(--text-secondary);margin-bottom:16px}}
        .stats{{font-size:12px;color:var(--text-secondary)}}
        .articles{{max-width:720px;margin:0 auto;padding:0 40px 80px}}
        .article{{padding:32px 0;border-bottom:1px solid var(--border)}}
        .article-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}}
        .article-left{{display:flex;align-items:center;gap:12px}}
        .article-number{{font-size:24px;font-weight:600;color:var(--border);line-height:1;min-width:32px}}
        .author-row{{display:flex;align-items:center;gap:10px}}
        .author-avatar{{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1c1917 0%,#57534e 100%);display:flex;align-items:center;justify-content:center;color:white;font-weight:600;font-size:11px}}
        .author-info{{display:flex;flex-direction:column}}
        .author-name{{font-weight:500;font-size:13px}}
        .author-bio{{color:var(--text-secondary);font-size:12px}}
        .article-actions{{display:flex;gap:6px}}
        .action-btn{{padding:5px 10px;border:1px solid var(--border);background:white;cursor:pointer;font-size:12px;border-radius:12px;display:flex;align-items:center;gap:4px}}
        .action-btn:hover{{background:var(--tag-bg)}}
        .action-btn.playing{{background:var(--accent);color:white;border-color:var(--accent)}}
        .article h2{{font-family:'Noto Serif SC',serif;font-size:1.1rem;font-weight:600;line-height:1.4;margin-bottom:12px;margin-left:44px}}
        .article-body{{margin-left:44px}}
        .article-body p{{font-size:14px;line-height:1.8;margin-bottom:10px}}
        .article-footer{{display:flex;justify-content:space-between;align-items:center;margin-top:14px;margin-left:44px}}
        .article-stats{{display:flex;gap:12px;font-size:12px;color:var(--text-secondary)}}
        .article-link{{color:var(--accent);font-size:13px;font-weight:500;text-decoration:none}}
        .article-link:hover{{text-decoration:underline}}
        .archive-section{{margin-top:40px;padding-top:30px;border-top:1px solid var(--border)}}
        .archive-section h3{{font-size:14px;color:var(--text-secondary);margin-bottom:16px}}
        .archive-list{{display:flex;flex-wrap:wrap;gap:10px}}
        .archive-item{{padding:8px 16px;background:var(--tag-bg);border-radius:8px;color:var(--text);text-decoration:none;font-size:14px;transition:all .2s}}
        .archive-item:hover{{background:var(--accent);color:#fff}}
        .footer{{text-align:center;padding:40px;color:var(--text-secondary);font-size:13px;border-top:1px solid var(--border)}}
        .footer a{{color:var(--accent);text-decoration:none}}
        [data-lang]{{display:none}}
        [data-lang].show{{display:block}}
        @media(max-width:768px){{.controls{{padding:10px 20px}}.hero{{padding:30px 20px 20px}}.hero h1{{font-size:1.4rem}}.articles{{padding:0 20px 60px}}.article h2,.article-body,.article-footer{{margin-left:0}}}}
    </style>
</head>
<body>
    <div class="controls">
        <div class="lang-switch">
            <button class="lang-btn active" data-lang-switch="zh">中文</button>
            <button class="lang-btn" data-lang-switch="en">EN</button>
        </div>
        <div class="audio-controls">
            <select class="voice-select" id="voiceSelect"><option value="">选择语音</option></select>
            <button class="audio-btn" id="playAllBtn" onclick="playAll()">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                全文朗读
            </button>
        </div>
    </div>
    <header class="hero">
        <p class="date">{date_en}</p>
        <h1>AI Builders Daily Digest</h1>
        <p class="hero-sub">每日精选 AI 领域最有价值的深度内容</p>
        <p class="stats">📝 {len(all_items)} 篇精选 ({x_count}条X · {pod_count}个播客 · {blog_count}篇博客)</p>
    </header>
    <main class="articles">
        {articles_html}
        {archive_html}
    </main>
    <footer class="footer">
        <p>Data by <a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a></p>
    </footer>
    <script>
        let currentLang='zh',voices=[],selectedVoice=null,isPlaying=false;
        function loadVoices(){{voices=speechSynthesis.getVoices();const s=document.getElementById('voiceSelect');s.innerHTML='<option value="">选择语音</option>';voices.filter(v=>v.lang.startsWith('zh')).forEach(v=>{{const o=document.createElement('option');o.value=v.name;o.textContent=v.name+(v.localService?' ★':'');s.appendChild(o)}})}}
        document.getElementById('voiceSelect').onchange=e=>{{selectedVoice=voices.find(v=>v.name===e.target.value)}};
        document.querySelectorAll('.lang-btn').forEach(btn=>{{btn.onclick=()=>{{currentLang=btn.dataset.langSwitch;document.querySelectorAll('.lang-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');document.querySelectorAll('[data-lang]').forEach(el=>{{el.classList.toggle('show',el.dataset.lang===currentLang)}});if(isPlaying)stopAll()}}}});
        function playArticle(n){{const a=document.querySelector(`[data-article="${{n}}"]`);let t='';a.querySelectorAll(`[data-lang="${{currentLang}}"]`).forEach(el=>{{if(el.tagName==='H2'||el.tagName==='P')t+=el.textContent+'。'}});speak(t,a.querySelector('.action-btn'))}}
        function playAll(){{const btn=document.getElementById('playAllBtn');if(isPlaying){{stopAll();return}}let t='今天为大家带来 AI 领域的重要资讯。';document.querySelectorAll('.article').forEach((a,i)=>{{t+=`第 ${{i+1}} 篇，`;a.querySelectorAll(`[data-lang="${{currentLang}}"]`).forEach(el=>{{if(el.tagName==='H2'||el.tagName==='P')t+=el.textContent}})}});speak(t,btn)}}
        function speak(text,btn){{if(isPlaying){{speechSynthesis.cancel();isPlaying=false;document.querySelectorAll('.action-btn,.audio-btn').forEach(b=>b.classList.remove('playing'));return}}const u=new SpeechSynthesisUtterance(text.replace(/。/g,'，').replace(/\\s+/g,' ').trim());u.lang=currentLang==='zh'?'zh-CN':'en-US';u.rate=0.85;u.pitch=0.95;const v=selectedVoice||voices.find(v=>v.lang.startsWith(currentLang));if(v)u.voice=v;u.onstart=()=>{{isPlaying=true;btn.classList.add('playing')}};u.onend=u.onerror=()=>{{isPlaying=false;document.querySelectorAll('.action-btn,.audio-btn').forEach(b=>b.classList.remove('playing'))}};speechSynthesis.cancel();speechSynthesis.speak(u)}}
        function stopAll(){{speechSynthesis.cancel();isPlaying=false;document.querySelectorAll('.action-btn,.audio-btn').forEach(b=>b.classList.remove('playing'))}}
        // 初始化中文显示
        document.querySelectorAll('[data-lang="zh"]').forEach(el=>el.classList.add('show'));
        speechSynthesis.onvoiceschanged=loadVoices;loadVoices();
    </script>
</body>
</html>'''

# ============ 输出 ============
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'生成完成！共 {len(all_items)} 篇')
print(f'  - X 推文: {x_count} 篇')
print(f'  - 播客: {pod_count} 篇')
print(f'  - 博客: {blog_count} 篇')
print()
print('=== 内容预览 ===')
for item in all_items:
    type_icon = {'x': '🐦', 'podcast': '🎙️', 'blog': '📝'}.get(item['type'], '•')
    print(f"{type_icon} {item['num']:02d}. [{item['type']}] {item['name'][:40]}")
    print(f"   {item['excerpt'][:80]}...")
