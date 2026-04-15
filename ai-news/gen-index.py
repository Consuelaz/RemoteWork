#!/usr/bin/env python3
"""
AI 资讯生成脚本 — 参照 2026-04-13.html 样式体系

页面结构（与参考页面保持一致）：
- Navbar：顶部导航
- Hero：蓝色渐变大头部（含统计徽章）
- Section "建造者动态"：X 推文按建造者分组
- Section "播客精华"：播客卡片
- Section "官方博客"：博客卡片
- 中英文切换 + 语音朗读

数据规则：
- X: 按建造者分组，每位最多3条推文，取前8位建造者
- 播客: 分段提取精华（每段1500字符），取前3段
- 博客: 分段提取精华（每段1500字符），取前2段
"""
import json, os, re, subprocess
from datetime import datetime

# ============ 路径配置 ============
SKILL_DIR  = '/Users/qisoong/.workbuddy/skills/follow-builders'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f'{SKILL_DIR}/feed-x.json') as f:
    x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json') as f:
    pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json') as f:
    blog_data = json.load(f)

# ============ 规则配置 ============
MAX_TWEETS_PER_BUILDER = 3   # 每位建造者最多显示推文数
MAX_BUILDERS           = 8   # 最多展示建造者数
SEG_LEN                = 1500  # 播客/博客每段长度
MAX_PODCASTS           = 3
MAX_BLOGS              = 2

# ============ 工具函数 ============
def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def smart_truncate(text, max_len):
    """在自然断点（句子/段落边界）处截断，不从单词中间截断"""
    if len(text) <= max_len:
        return text
    target  = max_len
    min_keep = int(max_len * 0.7)
    sentence_ends = '.!?。！？\n'
    for i in range(target - 1, min_keep - 1, -1):
        if text[i] in sentence_ends:
            end = i
            while end > i - 3 and text[end].isspace():
                end -= 1
            if text[end] in sentence_ends:
                return text[:end + 1].strip()
    for i in range(target, min(target + 200, len(text))):
        if text[i] in sentence_ends:
            return text[:i + 1].strip()
    for i in range(target - 1, min_keep, -1):
        if text[i].isspace():
            return text[:i].strip()
    return text[:max_len].rsplit(' ', 1)[0] + '…'

def extract_segment(text, start, length):
    if len(text) <= start:
        return None
    seg = smart_truncate(text[start:], length)
    return seg if len(seg) > 80 else None

# ============ 收集 X 建造者数据 ============
builders_data = []
for b in x_data.get('x', []):
    name     = b.get('name', '')
    handle   = b.get('handle', '')
    bio      = b.get('bio', '').split('\n')[0][:80]
    initials = ''.join(n[0].upper() for n in name.split()[:2]) or '?'
    tweets = []
    for t in b.get('tweets', [])[:MAX_TWEETS_PER_BUILDER]:
        txt = t.get('text', '').strip()
        if txt:
            tweets.append({
                'text': txt,
                'likes': t.get('likes', 0),
                'url': t.get('url', '#'),
            })
    if tweets:
        builders_data.append({
            'name': name, 'handle': handle, 'bio': bio,
            'initials': initials, 'tweets': tweets,
            'total_likes': sum(t['likes'] for t in tweets),
        })

# 按总点赞数排序
builders_data.sort(key=lambda x: x['total_likes'], reverse=True)
builders_data = builders_data[:MAX_BUILDERS]

# ============ 收集播客数据 ============
pod_items = []
for pod in pod_data.get('podcasts', []):
    transcript = pod.get('transcript', '')
    if not transcript:
        continue
    title  = pod.get('title', '')[:70]
    url    = pod.get('url', '#')
    show   = pod.get('show', 'AI Podcast')
    source = pod.get('source', show)
    for part_idx, start in enumerate(range(0, len(transcript), SEG_LEN), 1):
        seg = extract_segment(transcript, start, SEG_LEN)
        if seg:
            pod_items.append({'title': title, 'url': url, 'show': show, 'source': source, 'seg': seg})
        if len(pod_items) >= MAX_PODCASTS:
            break
    if len(pod_items) >= MAX_PODCASTS:
        break

# ============ 收集博客数据 ============
blog_items = []
for blog in blog_data.get('blogs', []):
    content = blog.get('transcript', blog.get('content', ''))
    if not content:
        continue
    title  = blog.get('title', '')[:70]
    url    = blog.get('url', '#')
    source = blog.get('source', 'Tech Blog')
    for part_idx, start in enumerate(range(0, len(content), SEG_LEN), 1):
        seg = extract_segment(content, start, SEG_LEN)
        if seg:
            blog_items.append({'title': title, 'url': url, 'source': source, 'seg': seg})
        if len(blog_items) >= MAX_BLOGS:
            break
    if len(blog_items) >= MAX_BLOGS:
        break

# ============ 统计数字 ============
builder_count = len(builders_data)
tweet_count   = sum(len(b['tweets']) for b in builders_data)
pod_count     = len(pod_items)
blog_count    = len(blog_items)

# ============ 生成建造者卡片 HTML ============
def build_builder_cards(builders, lang):
    html = ''
    for b in builders:
        tweets_html = ''
        for i, tw in enumerate(b['tweets']):
            en_text  = smart_truncate(tw['text'], 400)
            url_label = '🔗 查看原文' if lang == 'zh' else '🔗 View Tweet'
            # 在英文模式下，显示英文推文；中文模式下，推文内容依旧是英文原文（保持原始）
            tweets_html += f'''
      <div class="tweet-item">
        <div class="tweet-text">{esc(en_text)}</div>
        <a class="tweet-url" href="{esc(tw['url'])}" target="_blank">{url_label}</a>
      </div>'''
        html += f'''
    <div class="builder-card">
      <div class="builder-header">
        <div class="builder-avatar">{esc(b['initials'])}</div>
        <div class="builder-info">
          <h3>{esc(b['name'])}</h3>
          <div class="handle">@{esc(b['handle'])} · {esc(b['bio'])}</div>
        </div>
      </div>{tweets_html}
    </div>'''
    return html

# ============ 生成播客卡片 HTML ============
def build_podcast_cards(pods):
    html = ''
    for p in pods:
        seg_display = smart_truncate(p['seg'], 500)
        html += f'''
    <div class="podcast-card">
      <h3>{esc(p['title'])}</h3>
      <div class="podcast-meta">
        <span>🎧 {esc(p['source'])}</span>
      </div>
      <a class="podcast-link" href="{esc(p['url'])}" target="_blank">▶️ 收听节目 →</a>
      <div class="podcast-summary">
        <strong>字幕摘要：</strong><br>
        {esc(seg_display)}<br>...（更多内容见原文）
      </div>
    </div>'''
    return html

# ============ 生成播客卡片 HTML（英文版） ============
def build_podcast_cards_en(pods):
    html = ''
    for p in pods:
        seg_display = smart_truncate(p['seg'], 500)
        html += f'''
    <div class="podcast-card">
      <h3>{esc(p['title'])}</h3>
      <div class="podcast-meta">
        <span>🎧 {esc(p['source'])}</span>
      </div>
      <a class="podcast-link" href="{esc(p['url'])}" target="_blank">▶️ Listen Now →</a>
      <div class="podcast-summary">
        <strong>Transcript excerpt:</strong><br>
        {esc(seg_display)}<br>...(see original for more)
      </div>
    </div>'''
    return html

# ============ 生成博客卡片 HTML ============
def build_blog_cards(blogs):
    html = ''
    for b in blogs:
        html += f'''
    <div class="blog-card">
      <div class="blog-source">{esc(b['source'])}</div>
      <h3>{esc(b['title'])}</h3>
      <a class="blog-link" href="{esc(b['url'])}" target="_blank">📖 阅读原文 →</a>
    </div>'''
    return html

def build_blog_cards_en(blogs):
    html = ''
    for b in blogs:
        html += f'''
    <div class="blog-card">
      <div class="blog-source">{esc(b['source'])}</div>
      <h3>{esc(b['title'])}</h3>
      <a class="blog-link" href="{esc(b['url'])}" target="_blank">📖 Read More →</a>
    </div>'''
    return html

# ============ 历史存档 ============
archive_files = sorted([
    f for f in os.listdir(OUTPUT_DIR)
    if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f)
], reverse=True)[:10]

archive_links = ''
for f in archive_files:
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})\.html', f)
    if m:
        y, mo, d = m.groups()
        archive_links += f'<a href="{f}" class="archive-item">{y}年{int(mo)}月{int(d)}日</a>\n        '

archive_html = f'''
  <div class="archive-section">
    <h3>📅 历史存档</h3>
    <div class="archive-list">
      {archive_links}
    </div>
  </div>''' if archive_links else ''

# ============ 日期 ============
today    = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August',
             'September','October','November','December']
date_en  = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_zh  = f"{today.year}年{today.month}月{today.day}日"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

# 生成建造者 / 播客 / 博客 HTML（中英两套）
zh_builders_html = build_builder_cards(builders_data, 'zh')
en_builders_html = build_builder_cards(builders_data, 'en')
zh_podcast_html  = build_podcast_cards(pod_items)
en_podcast_html  = build_podcast_cards_en(pod_items)
zh_blog_html     = build_blog_cards(blog_items)
en_blog_html     = build_blog_cards_en(blog_items)

# ============ 完整页面模板（对标 2026-04-13.html 风格）============
HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Builders Digest · {date_zh} | Junes远程</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet" />
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif; background: #F9FAFB; color: #111827; line-height: 1.6; font-size: 15px; }}

    /* === Navbar === */
    .navbar {{ position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,.92); backdrop-filter: blur(10px); border-bottom: 1px solid #E5E7EB; }}
    .nav-inner {{ display: flex; align-items: center; height: 60px; gap: 24px; max-width: 960px; margin: 0 auto; padding: 0 24px; }}
    .logo {{ display: flex; align-items: center; gap: 6px; text-decoration: none; font-weight: 700; font-size: 18px; color: #111827; }}
    .logo span:last-child {{ color: #2563EB; }}
    .nav-links {{ display: flex; gap: 20px; margin-left: auto; }}
    .nav-links a {{ text-decoration: none; color: #374151; font-size: 14px; font-weight: 500; }}
    .nav-links a:hover {{ color: #2563EB; }}
    /* 语言切换和音频按钮放在 navbar 右侧 */
    .nav-controls {{ display: flex; align-items: center; gap: 10px; margin-left: 20px; }}
    .lang-btn {{ padding: 4px 12px; border: 1px solid #E5E7EB; background: #fff; cursor: pointer; font-size: 13px; border-radius: 14px; transition: all .15s; }}
    .lang-btn.active {{ background: #111827; color: #fff; border-color: #111827; }}
    .audio-btn {{ padding: 4px 10px; border: 1px solid #E5E7EB; background: #fff; cursor: pointer; font-size: 12px; border-radius: 14px; display: flex; align-items: center; gap: 4px; white-space: nowrap; }}
    .audio-btn:hover {{ background: #F3F4F6; }}
    .audio-btn.playing {{ background: #2563EB; color: #fff; border-color: #2563EB; }}
    .voice-sel {{ padding: 4px 8px; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 12px; background: #fff; cursor: pointer; }}
    svg.icon {{ width: 11px; height: 11px; vertical-align: middle; }}

    /* === Hero === */
    .hero {{ background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%); color: white; padding: 64px 24px; text-align: center; }}
    .hero-inner {{ max-width: 720px; margin: 0 auto; }}
    .hero-badge {{ display: inline-block; background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.3); border-radius: 20px; padding: 4px 14px; font-size: 12px; margin-bottom: 20px; letter-spacing: .5px; }}
    .hero-title {{ font-size: 36px; font-weight: 700; line-height: 1.2; margin-bottom: 16px; }}
    .hero-subtitle {{ font-size: 16px; opacity: .85; margin-bottom: 32px; }}
    .hero-meta {{ display: flex; justify-content: center; gap: 32px; font-size: 14px; opacity: .9; flex-wrap: wrap; }}
    .hero-meta span {{ display: flex; align-items: center; gap: 6px; }}

    /* === 内容区 === */
    .content {{ max-width: 800px; margin: 40px auto; padding: 0 24px; }}

    /* === 统计徽章 === */
    .stats-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 32px; }}
    .stat-chip {{ display: inline-flex; align-items: center; gap: 6px; background: #EFF6FF; color: #2563EB; border-radius: 20px; padding: 4px 12px; font-size: 13px; font-weight: 500; }}
    .stat-chip.green {{ background: #ECFDF5; color: #059669; }}
    .stat-chip.purple {{ background: #F5F3FF; color: #7C3AED; }}
    .stat-chip.orange {{ background: #FFF7ED; color: #EA580C; }}

    /* === Section 标题 === */
    .section-title {{ display: flex; align-items: center; gap: 10px; margin: 36px 0 16px; }}
    .section-title h2 {{ font-size: 18px; font-weight: 700; color: #111827; }}
    .section-title .tag {{ display: inline-flex; align-items: center; background: #DBEAFE; color: #1D4ED8; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; }}
    .section-title .tag.green {{ background: #D1FAE5; color: #065F46; }}
    .section-title .tag.purple {{ background: #EDE9FE; color: #5B21B6; }}
    .section-title::after {{ content: ''; flex: 1; height: 1px; background: #E5E7EB; margin-left: 12px; }}

    /* === 建造者卡片 === */
    .builder-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06); border: 1px solid #E5E7EB; transition: box-shadow .2s; }}
    .builder-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.1); }}
    .builder-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
    .builder-avatar {{ width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667EEA, #764BA2); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px; flex-shrink: 0; }}
    .builder-info h3 {{ font-size: 15px; font-weight: 600; color: #111827; }}
    .builder-info .handle {{ font-size: 13px; color: #6B7280; margin-top: 2px; }}
    .tweet-item {{ padding: 10px 0; border-top: 1px solid #F3F4F6; }}
    .tweet-item:first-of-type {{ border-top: none; padding-top: 0; }}
    .tweet-text {{ font-size: 14px; color: #111827; line-height: 1.65; margin-bottom: 6px; white-space: pre-wrap; }}
    .tweet-url {{ font-size: 12px; color: #2563EB; text-decoration: none; }}
    .tweet-url:hover {{ text-decoration: underline; }}

    /* === 播客卡片 === */
    .podcast-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06); border: 1px solid #E5E7EB; }}
    .podcast-card h3 {{ font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 8px; }}
    .podcast-meta {{ display: flex; gap: 12px; margin-bottom: 12px; }}
    .podcast-meta span {{ font-size: 12px; color: #6B7280; background: #F3F4F6; border-radius: 4px; padding: 2px 8px; }}
    .podcast-link {{ display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #2563EB; text-decoration: none; font-weight: 500; }}
    .podcast-summary {{ font-size: 14px; color: #374151; line-height: 1.65; background: #FFFBEB; border-left: 3px solid #F59E0B; padding: 12px 14px; border-radius: 0 6px 6px 0; margin-top: 10px; white-space: pre-wrap; }}

    /* === 博客卡片 === */
    .blog-card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.06); border: 1px solid #E5E7EB; }}
    .blog-card h3 {{ font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 8px; }}
    .blog-card .blog-source {{ font-size: 12px; color: #6B7280; margin-bottom: 8px; }}
    .blog-card .blog-link {{ display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #2563EB; text-decoration: none; font-weight: 500; }}

    /* === 历史存档 === */
    .archive-section {{ margin-top: 48px; padding-top: 28px; border-top: 1px solid #E5E7EB; }}
    .archive-section h3 {{ font-size: 13px; color: #6B7280; margin-bottom: 14px; }}
    .archive-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .archive-item {{ padding: 6px 14px; background: #F3F4F6; border-radius: 8px; color: #374151; text-decoration: none; font-size: 13px; transition: all .15s; }}
    .archive-item:hover {{ background: #2563EB; color: #fff; }}

    /* === 页脚 === */
    footer {{ text-align: center; padding: 32px 24px; color: #9CA3AF; font-size: 13px; border-top: 1px solid #E5E7EB; margin-top: 40px; }}
    footer a {{ color: #6B7280; text-decoration: none; }}
    footer a:hover {{ color: #2563EB; }}

    /* === 响应式 === */
    @media (max-width: 768px) {{
      .hero {{ padding: 40px 16px; }}
      .hero-title {{ font-size: 26px; }}
      .hero-meta {{ gap: 16px; font-size: 13px; }}
      .content {{ padding: 0 16px; margin: 24px auto; }}
      .nav-inner {{ padding: 0 16px; gap: 12px; }}
      .nav-links {{ display: none; }}
      .nav-controls {{ margin-left: auto; }}
    }}
  </style>
</head>
<body>

  <!-- Navbar -->
  <header class="navbar">
    <div class="nav-inner">
      <a href="../index.html" class="logo"><span>🌐</span><span>Junes<span>远程</span></span></a>
      <div class="nav-links">
        <a href="../index.html">远程岗位</a>
        <a href="../companies.html">科技公司</a>
        <a href="./index.html">AI 资讯</a>
      </div>
      <div class="nav-controls">
        <button class="lang-btn active" id="btnZh" onclick="setLang('zh')">中文</button>
        <button class="lang-btn" id="btnEn" onclick="setLang('en')">EN</button>
        <select class="voice-sel" id="voiceSel"><option value="">语音</option></select>
        <button class="audio-btn" id="playAllBtn" onclick="togglePlayAll()">
          <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          <span class="zh-text">全文朗读</span><span class="en-text" style="display:none">Read All</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Hero -->
  <section class="hero">
    <div class="hero-inner">
      <div class="hero-badge">📡 AI Builders Digest</div>
      <h1 class="hero-title">
        <span class="zh-text">追踪建造者，而非网红</span>
        <span class="en-text" style="display:none">Track Builders, Not Influencers</span>
      </h1>
      <p class="hero-subtitle">
        <span class="zh-text">每日汇总 AI 领域顶尖建造者的关键观点、播客精华与官方博客更新</span>
        <span class="en-text" style="display:none">Daily digest of key insights, podcast highlights, and official blog updates from top AI builders</span>
      </p>
      <div class="hero-meta">
        <span class="zh-text">📅 {date_zh}</span>
        <span class="en-text" style="display:none">📅 {date_en}</span>
        <span>🕐 <span class="zh-text">北京时间每日更新</span><span class="en-text" style="display:none">Updated daily (Beijing Time)</span></span>
        <span>🤖 <span class="zh-text">AI 整理</span><span class="en-text" style="display:none">AI curated</span></span>
      </div>
    </div>
  </section>

  <!-- 内容 -->
  <main class="content">

    <!-- 统计徽章 -->
    <div class="stats-row">
      <span class="stat-chip">👤 {builder_count} <span class="zh-text">位建造者</span><span class="en-text" style="display:none">builders</span></span>
      <span class="stat-chip green">🐦 {tweet_count} <span class="zh-text">条推文</span><span class="en-text" style="display:none">tweets</span></span>
      <span class="stat-chip purple">🎙️ {pod_count} <span class="zh-text">期播客</span><span class="en-text" style="display:none">podcasts</span></span>
      <span class="stat-chip orange">📝 {blog_count} <span class="zh-text">篇博客</span><span class="en-text" style="display:none">blogs</span></span>
    </div>

    <!-- X 建造者动态 -->
    <div class="section-title">
      <span class="tag">🐦 X / Twitter</span>
      <h2><span class="zh-text">建造者动态</span><span class="en-text" style="display:none">Builder Updates</span></h2>
    </div>
    <div id="builders-zh" class="zh-text">{zh_builders_html}</div>
    <div id="builders-en" class="en-text" style="display:none">{en_builders_html}</div>

    <!-- 播客 -->
    <div class="section-title">
      <span class="tag green">🎙️ <span class="zh-text">播客</span><span class="en-text" style="display:none">Podcast</span></span>
      <h2><span class="zh-text">最新节目</span><span class="en-text" style="display:none">Latest Episodes</span></h2>
    </div>
    <div class="zh-text">{zh_podcast_html}</div>
    <div class="en-text" style="display:none">{en_podcast_html}</div>

    <!-- 博客 -->
    <div class="section-title">
      <span class="tag purple">📝 <span class="zh-text">官方博客</span><span class="en-text" style="display:none">Official Blog</span></span>
      <h2><span class="zh-text">公司博客更新</span><span class="en-text" style="display:none">Company Blog Updates</span></h2>
    </div>
    <div class="zh-text">{zh_blog_html}</div>
    <div class="en-text" style="display:none">{en_blog_html}</div>

    {archive_html}
  </main>

  <footer>
    <p>数据来源：<a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a> · <a href="../index.html">Junes远程</a></p>
  </footer>

  <script>
  // ===== 语言切换 =====
  var currentLang = 'zh';
  function setLang(lang) {{
    currentLang = lang;
    document.getElementById('btnZh').classList.toggle('active', lang === 'zh');
    document.getElementById('btnEn').classList.toggle('active', lang === 'en');
    document.querySelectorAll('.zh-text').forEach(function(el) {{
      el.style.display = lang === 'zh' ? '' : 'none';
    }});
    document.querySelectorAll('.en-text').forEach(function(el) {{
      el.style.display = lang === 'en' ? '' : 'none';
    }});
    if (isPlaying) stopAll();
  }}

  // ===== 语音朗读 =====
  var voices = [], selectedVoice = null, isPlaying = false;

  function loadVoices() {{
    voices = speechSynthesis.getVoices();
    var s = document.getElementById('voiceSel');
    s.innerHTML = '<option value="">语音</option>';
    voices.forEach(function(v) {{
      if (v.lang.startsWith('zh') || v.lang.startsWith('en')) {{
        var o = document.createElement('option');
        o.value = v.name;
        o.textContent = v.name + (v.localService ? ' ★' : '');
        s.appendChild(o);
      }}
    }});
  }}
  document.getElementById('voiceSel').onchange = function(e) {{
    selectedVoice = voices.find(function(v) {{ return v.name === e.target.value; }}) || null;
  }};

  function getAllReadText() {{
    var text = currentLang === 'zh' ? '今天为大家带来 AI 领域精选资讯。' : 'Here is today\'s AI builders digest.';
    var cls = currentLang === 'zh' ? '.zh-text' : '.en-text';
    document.querySelectorAll('.builder-card, .podcast-card, .blog-card').forEach(function(card, i) {{
      card.querySelectorAll(cls + ' .tweet-text, ' + cls + '.tweet-text, ' +
                            cls + ' .podcast-summary, ' + cls + '.podcast-summary').forEach(function(el) {{
        text += ' ' + (el.innerText || el.textContent);
      }});
    }});
    return text;
  }}

  function togglePlayAll() {{
    if (isPlaying) {{ stopAll(); return; }}
    speak(getAllReadText(), document.getElementById('playAllBtn'));
  }}

  function speak(text, btn) {{
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text.replace(/[。！？]/g, '，').replace(/\\s+/g, ' ').trim());
    u.lang = currentLang === 'zh' ? 'zh-CN' : 'en-US';
    u.rate = 0.85; u.pitch = 0.95;
    var v = selectedVoice || voices.find(function(v) {{ return v.lang.startsWith(currentLang === 'zh' ? 'zh' : 'en'); }});
    if (v) u.voice = v;
    u.onstart = function() {{ isPlaying = true; if (btn) btn.classList.add('playing'); }};
    u.onend = u.onerror = function() {{ stopAll(); }};
    speechSynthesis.speak(u);
  }}

  function stopAll() {{
    speechSynthesis.cancel();
    isPlaying = false;
    document.querySelectorAll('.audio-btn').forEach(function(b) {{ b.classList.remove('playing'); }});
  }}

  speechSynthesis.onvoiceschanged = loadVoices;
  loadVoices();
  </script>
</body>
</html>'''

# ============ 写文件 ============
out_path   = os.path.join(OUTPUT_DIR, 'index.html')
dated_path = os.path.join(OUTPUT_DIR, f'{date_str}.html')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)
with open(dated_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'✅ 生成完成！')
print(f'   👤 {builder_count} 位建造者  🐦 {tweet_count} 条推文  🎙️ {pod_count} 期播客  📝 {blog_count} 篇博客')
print(f'   → {out_path}')
print(f'   → {dated_path}')

# ============ Git 自动提交推送 ============
print()
print('=== Git 自动推送 ===')

def run_git(cmd, cwd):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

rc, out, err = run_git('git status --porcelain', OUTPUT_DIR)
if not out.strip():
    print('⚪ 没有变更，跳过提交')
else:
    print(f'📝 检测到变更:\n{out}')
    rc, out, err = run_git('git add -A', OUTPUT_DIR)
    if rc != 0:
        print(f'❌ git add 失败: {err}')
    else:
        commit_msg = f'🤖 AI News 更新 {date_str} ({builder_count}位建造者·{tweet_count}推·{pod_count}播·{blog_count}博)'
        rc, out, err = run_git(f'git commit -m "{commit_msg}"', OUTPUT_DIR)
        if rc != 0:
            print(f'❌ git commit 失败: {err}')
        else:
            print(f'✅ 已提交: {commit_msg}')
            rc, out, err = run_git('git push', OUTPUT_DIR)
            if rc != 0:
                print(f'❌ git push 失败: {err}')
            else:
                print('✅ 已推送到 GitHub')
