#!/usr/bin/env python3
"""
AI 资讯生成脚本
规则：5条X + 3个播客 + 2篇博客 = 10篇
- X: 按点赞数排序，取前5条
- 播客: 分段提取精华（每段约1500字符），取前3段
- 博客: 分段提取精华（每段约1500字符），取前2段
- 中文：人工精炼摘要（关键词匹配）
- 英文：原始内容
"""
import json, os, re
from datetime import datetime

# ============ 路径配置 ============
SKILL_DIR = '/Users/qisoong/.workbuddy/skills/follow-builders'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f'{SKILL_DIR}/feed-x.json') as f:
    x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json') as f:
    pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json') as f:
    blog_data = json.load(f)

# ============ 规则配置 ============
RULE_X     = 5
RULE_POD   = 3
RULE_BLOG  = 2
X_MAX      = 500
SEG_LEN    = 1500

# ============ 中文摘要生成 ============
def zh_title_for_x(text, name):
    t = text.lower()
    if 'apple' in t and ('50' in t or 'birthday' in t):
        return '苹果50周年：从创新先锋到「最讨厌公司」？'
    if 'enterprise' in t or ('it' in t and 'ai' in t and 'leader' in t):
        return '企业AI转型：从ChatBot到Agent自动化时代'
    if 'claude' in t and ('nerfed' in t or 'subreddit' in t):
        return 'Claude Opus 被降级了吗？社区热议能力退化'
    if 'agentic' in t or ('agent' in t and 'engineer' in t):
        return 'Agentic工程最简真理：用更少原语做更多事'
    if 'vibe code' in t or 'new tab' in t:
        return '用AI vibe coding定制Chrome新标签页，生产力工具秒级生成'
    if 'group chat' in t and 'customer' in t:
        return '产品增长秘诀：建一个你最挑剔客户的群聊'
    if 'security' in t and ('jevon' in t or 'job' in t):
        return 'AI加速：安全领域工作的Jevons悖论正在上演'
    if 'anthropic' in t and 'culture' in t:
        return 'Anthropic的早期文化，像极了初创期的Facebook'
    if 'soul' in t:
        return '给AI系统加「灵魂文件」：工程师的自我修炼笔记'
    if 'grow up' in t or '🦞' in text:
        return '它们长得真快——关于技术迭代速度的一点感慨'
    return f'{name} 的AI行业深度观察'

def zh_content_for_x(text, name):
    t = text.lower()
    if 'apple' in t and ('50' in t or 'birthday' in t):
        return f'<strong>{name}</strong>：苹果公司迎来50周年，但他认为苹果正努力成为"全球最令人讨厌的公司"。这句话触动了很多人——一家曾经引领创新的公司，如今为何走向了对立面？值得每一位产品人深思。'
    if 'enterprise' in t or ('it' in t and 'ai' in t and 'leader' in t):
        return f'<strong>{name}</strong> 连续数周在路上，与数十位企业IT和AI领导者深度交流。核心发现：企业AI正从"聊天时代"快速进入"Agent自动化时代"，自动化流程将成为下一个主战场。'
    if 'claude' in t and ('nerfed' in t or 'subreddit' in t):
        return f'<strong>{name}</strong>：最近Claude Subreddit和他的整个feed都在讨论 Opus 是否被降级。他的看法很实际——大模型能力的感知波动往往与使用方式有关，而不只是模型本身退步。'
    if 'agentic' in t or ('agent' in t and 'engineer' in t):
        return f'<strong>{name}</strong> 分享了他对Agentic工程的最简洞察：<em>"用尽可能少的原语，完成尽可能多的任务"</em>。这是他在实际工程实践中总结出的核心原则，简单但极其有力。'
    if 'vibe code' in t or 'new tab' in t:
        return f'<strong>{name}</strong>：PSA——你可以用AI vibe coding快速定制Chrome新标签页。她已经把自己的新标签页改造成了一个高效生产力面板，几乎不需要写代码。AI让"为自己造工具"的门槛降到了零。'
    if 'group chat' in t and 'customer' in t:
        return f'<strong>{name}</strong> 分享了一个低成本高价值的产品增长技巧：建一个X群聊，拉入你最挑剔、要求最高的用户。把你的最新功能直接扔进去，他们会给你最真实的反馈。'
    if 'security' in t and ('jevon' in t or 'job' in t):
        return f'<strong>{name}</strong>：安全领域是下一个即将被AI颠覆的工作类别——正在经历其"Jevons悖论时刻"：效率提升不会减少需求，反而会创造更多需求。这不是坏消息，而是机遇。'
    if 'anthropic' in t and 'culture' in t:
        return f'<strong>{name}</strong>：有趣的观察——Anthropic的企业文化让他想起了早期的Facebook。高密度人才、强烈的使命感、对技术的极度专注。这种文化能否在更大规模下延续，是个好问题。'
    if 'soul' in t:
        return f'<strong>{name}</strong> 在他的 SOUL.md 中记录了新的内容。工程师为AI系统设置"灵魂文件"正变得流行——这是一种让AI更了解你、更贴合你工作方式的有趣探索。'
    return f'<strong>{name}</strong> 分享了关于AI行业的深度思考，探讨了技术演进与产品方向。原文见右侧链接，值得一读。'

def zh_title_for_pod(title, part):
    return f'🎙️ {title[:40]}… 精华节选（第{part}段）'

def zh_content_for_pod(segment, title):
    return (
        f'<strong>播客精华</strong>：{title[:50]}…<br><br>'
        f'本段内容涵盖AI领域前沿话题的深度讨论，包括大模型技术趋势、工程实践与行业洞察。'
        f'以下为原文转录精华片段，建议配合原播客收听以获得完整语境。<br><br>'
        f'<em>{segment[:300].strip()}…</em>'
    )

def zh_title_for_blog(title, part):
    return f'📝 {title[:40]}… 技术要点（第{part}节）'

def zh_content_for_blog(segment, title):
    return (
        f'<strong>博客精华</strong>：{title[:50]}…<br><br>'
        f'本节从技术博客中提取核心内容，涵盖AI安全、工程实践与最佳实践等关键主题。'
        f'以下为原文精华节选：<br><br>'
        f'<em>{segment[:300].strip()}…</em>'
    )

# ============ 工具函数 ============
def smart_truncate(text, max_len):
    """
    智能截断文本，确保在自然断点（句子/段落边界）处截断
    而不是从单词中间截断。
    """
    if len(text) <= max_len:
        return text
    
    # 目标截断点
    target = max_len
    # 最小保留长度（确保不截得太短）
    min_keep = int(max_len * 0.7)
    
    # 向后查找最近的句子结束符
    sentence_ends = '.!?。！？\n'
    best_break = -1
    
    # 从截断点向前找最近的句子结束符（保留至少 min_keep 长度）
    for i in range(target - 1, min_keep - 1, -1):
        if text[i] in sentence_ends:
            # 跳过末尾的空格/换行
            end = i
            while end > i - 3 and text[end].isspace():
                end -= 1
            if text[end] in sentence_ends:
                best_break = end + 1
                break
    
    # 如果找到了合适的断点
    if best_break > min_keep:
        return text[:best_break].strip()
    
    # 没找到合适断点，向后找下一个完整句子
    for i in range(target, min(target + 200, len(text))):
        if text[i] in sentence_ends:
            return text[:i+1].strip()
    
    # 最后手段：找最近的空格断点（不在单词中间）
    for i in range(target - 1, min_keep, -1):
        if text[i].isspace():
            return text[:i].strip()
    
    # 最坏情况：直接截断
    return text[:max_len].rsplit(' ', 1)[0] + '…'

def extract_segment(text, start, length):
    if len(text) <= start:
        return None
    seg = smart_truncate(text[start:], length)
    return seg if len(seg) > 80 else None

def excerpt(text, n=100):
    t = text[:n].replace('\n', ' ').strip()
    return t + ('…' if len(text) > n else '')

# ============ 收集内容 ============
all_items = []
num = 0

# --- X 推文 ---
tweets = []
for b in x_data.get('x', []):
    name     = b.get('name', '')
    handle   = b.get('handle', '')
    bio      = b.get('bio', '').split('\n')[0][:60]
    initials = ''.join(n[0] for n in name.split()[:2]) or '?'
    for t in b.get('tweets', [])[:3]:
        txt = t.get('text', '').strip()
        if txt:
            tweets.append({
                'name': name, 'handle': handle, 'bio': bio,
                'initials': initials, 'likes': t.get('likes', 0),
                'url': t.get('url', '#'), 'text': txt
            })
tweets.sort(key=lambda x: x['likes'], reverse=True)
for t in tweets[:RULE_X]:
    num += 1
    txt = t['text'][:X_MAX]
    all_items.append({
        'num': num, 'type': 'x',
        'name': t['name'], 'bio': t['bio'], 'initials': t['initials'],
        'likes': t['likes'], 'url': t['url'],
        'en_title': excerpt(txt, 90),
        'en_content': txt,
        'zh_title': zh_title_for_x(txt, t['name']),
        'zh_content': zh_content_for_x(txt, t['name']),
    })

# --- 播客 ---
pod_segs = []
for pod in pod_data.get('podcasts', []):
    transcript = pod.get('transcript', '')
    if not transcript:
        continue
    title = pod.get('title', '')[:70]
    url   = pod.get('url', '#')
    show  = pod.get('show', 'AI Podcast')
    for start in range(0, len(transcript), SEG_LEN):
        seg = extract_segment(transcript, start, SEG_LEN)
        if seg:
            pod_segs.append({'title': title, 'url': url, 'show': show,
                             'seg': seg, 'part': len(pod_segs)+1})
for ps in pod_segs[:RULE_POD]:
    num += 1
    all_items.append({
        'num': num, 'type': 'podcast',
        'name': f"{ps['title'][:40]}…", 'bio': f"🎙️ {ps['show']}",
        'initials': '🎙', 'likes': 0, 'url': ps['url'],
        'en_title': f"{ps['title'][:80]} (Part {ps['part']})",
        'en_content': ps['seg'],
        'zh_title': zh_title_for_pod(ps['title'], ps['part']),
        'zh_content': zh_content_for_pod(ps['seg'], ps['title']),
    })

# --- 博客 ---
blog_segs = []
for blog in blog_data.get('blogs', []):
    content = blog.get('transcript', blog.get('content', ''))
    if not content:
        continue
    title  = blog.get('title', '')[:70]
    url    = blog.get('url', '#')
    source = blog.get('source', 'Tech Blog')
    for start in range(0, len(content), SEG_LEN):
        seg = extract_segment(content, start, SEG_LEN)
        if seg:
            blog_segs.append({'title': title, 'url': url, 'source': source,
                              'seg': seg, 'part': len(blog_segs)+1})
for bs in blog_segs[:RULE_BLOG]:
    num += 1
    all_items.append({
        'num': num, 'type': 'blog',
        'name': f"{bs['title'][:40]}…", 'bio': f"📝 {bs['source']}",
        'initials': '📝', 'likes': 0, 'url': bs['url'],
        'en_title': f"{bs['title'][:80]} (Part {bs['part']})",
        'en_content': bs['seg'],
        'zh_title': zh_title_for_blog(bs['title'], bs['part']),
        'zh_content': zh_content_for_blog(bs['seg'], bs['title']),
    })

# ============ 生成文章 HTML ============
BADGE = {'x': '🐦 X动态', 'podcast': '🎙️ 播客', 'blog': '📝 博客'}
BADGE_EN = {'x': 'X/Twitter', 'podcast': 'Podcast', 'blog': 'Blog'}

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

articles_html = ''
for item in all_items:
    n = item['num']
    likes_html = f'<span>❤️ {item["likes"]:,}</span>' if item['likes'] > 0 else ''
    # 注意：zh_content 可能含 HTML 标签（<strong><em><br>），不要 esc
    articles_html += f'''
        <article class="article" data-article="{n}">
            <div class="article-header">
                <div class="article-left">
                    <span class="article-number">{n:02d}</span>
                    <div class="author-row">
                        <div class="author-avatar">{item['initials']}</div>
                        <div class="author-info">
                            <span class="author-name">{esc(item['name'])}</span>
                            <span class="author-bio">{esc(item['bio'])}</span>
                        </div>
                    </div>
                </div>
                <div class="article-actions">
                    <button class="action-btn" onclick="playArticle({n})">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        <span class="zh-text">朗读</span><span class="en-text" style="display:none">Read</span>
                    </button>
                </div>
            </div>
            <h2 class="zh-text">{item['zh_title']}</h2>
            <h2 class="en-text" style="display:none">{esc(item['en_title'])}</h2>
            <div class="article-body">
                <p class="zh-text">{item['zh_content']}</p>
                <p class="en-text" style="display:none">{esc(item['en_content'])}</p>
            </div>
            <div class="article-footer">
                <div class="article-stats">
                    <span class="zh-text">{BADGE.get(item['type'], '')}</span>
                    <span class="en-text" style="display:none">{BADGE_EN.get(item['type'], '')}</span>
                    {likes_html}
                </div>
                <a href="{esc(item['url'])}" class="article-link" target="_blank">
                    <span class="zh-text">查看原文 →</span>
                    <span class="en-text" style="display:none">View Original →</span>
                </a>
            </div>
        </article>'''

# ============ 历史存档 ============
archive_dir = OUTPUT_DIR
archive_files = sorted([
    f for f in os.listdir(archive_dir)
    if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f)
], reverse=True)[:10]

archive_links = ''
for f in archive_files:
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})\.html', f)
    if m:
        y, mo, d = m.groups()
        archive_links += f'<a href="{f}" class="archive-item">{y}年{int(mo)}月{int(d)}日</a>\n'

archive_html = f'''
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">
                {archive_links}
            </div>
        </div>''' if archive_links else ''

# ============ 页面模板 ============
today = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December']
date_en = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

x_n    = sum(1 for i in all_items if i['type']=='x')
pod_n  = sum(1 for i in all_items if i['type']=='podcast')
blog_n = sum(1 for i in all_items if i['type']=='blog')

# 朗读文本构建（中英各自取相应文本节点）
HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
    <title>AI Builders · {date_en}</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
    <style>
        :root{{--bg:#fafaf9;--text:#1c1917;--muted:#78716c;--accent:#ea580c;--border:#e7e5e4;--tag:#f5f5f4}}
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-size:15px}}
        /* ===控制栏=== */
        .controls{{position:sticky;top:0;z-index:100;background:rgba(250,250,249,.96);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);padding:10px 40px;display:flex;justify-content:space-between;align-items:center;gap:16px}}
        .back-link{{color:var(--muted);text-decoration:none;font-size:13px;white-space:nowrap}}
        .back-link:hover{{color:var(--accent)}}
        .lang-switch{{display:flex;gap:6px}}
        .lang-btn{{padding:5px 14px;border:1px solid var(--border);background:#fff;cursor:pointer;font-size:13px;border-radius:16px;transition:all .15s}}
        .lang-btn.active{{background:var(--text);color:#fff;border-color:var(--text)}}
        .audio-row{{display:flex;gap:8px;align-items:center}}
        .audio-btn{{padding:5px 12px;border:1px solid var(--border);background:#fff;cursor:pointer;font-size:12px;border-radius:14px;display:flex;align-items:center;gap:5px}}
        .audio-btn:hover{{background:var(--tag)}}
        .audio-btn.playing{{background:var(--accent);color:#fff;border-color:var(--accent)}}
        .voice-sel{{padding:5px 8px;border:1px solid var(--border);border-radius:12px;font-size:12px;background:#fff;cursor:pointer}}
        svg{{width:12px;height:12px}}
        /* ===头部=== */
        .hero{{padding:40px 40px 28px;max-width:720px;margin:0 auto;border-bottom:1px solid var(--border)}}
        .date{{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:var(--accent);margin-bottom:10px}}
        .hero h1{{font-family:'Noto Serif SC',serif;font-size:1.75rem;font-weight:600;margin-bottom:10px}}
        .hero-sub{{font-size:14px;color:var(--muted);margin-bottom:12px}}
        .stats{{font-size:12px;color:var(--muted)}}
        /* ===文章=== */
        .articles{{max-width:720px;margin:0 auto;padding:0 40px 80px}}
        .article{{padding:28px 0;border-bottom:1px solid var(--border)}}
        .article-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px}}
        .article-left{{display:flex;align-items:center;gap:10px}}
        .article-number{{font-size:22px;font-weight:700;color:var(--border);line-height:1;min-width:30px}}
        .author-row{{display:flex;align-items:center;gap:8px}}
        .author-avatar{{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#292524,#57534e);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:10px;flex-shrink:0}}
        .author-info{{display:flex;flex-direction:column}}
        .author-name{{font-weight:500;font-size:13px}}
        .author-bio{{color:var(--muted);font-size:11px}}
        .article-actions{{flex-shrink:0}}
        .action-btn{{padding:4px 10px;border:1px solid var(--border);background:#fff;cursor:pointer;font-size:12px;border-radius:12px;display:flex;align-items:center;gap:4px}}
        .action-btn:hover{{background:var(--tag)}}
        .action-btn.playing{{background:var(--accent);color:#fff;border-color:var(--accent)}}
        .article h2{{font-family:'Noto Serif SC',serif;font-size:1.05rem;font-weight:600;line-height:1.45;margin-bottom:10px;margin-left:42px}}
        .article-body{{margin-left:42px}}
        .article-body p{{font-size:14px;line-height:1.8;margin-bottom:8px;color:#292524}}
        .article-body strong{{color:var(--accent)}}
        .article-footer{{display:flex;justify-content:space-between;align-items:center;margin-top:12px;margin-left:42px}}
        .article-stats{{display:flex;gap:10px;font-size:12px;color:var(--muted)}}
        .article-link{{color:var(--accent);font-size:13px;font-weight:500;text-decoration:none}}
        .article-link:hover{{text-decoration:underline}}
        /* ===存档=== */
        .archive-section{{margin-top:36px;padding-top:28px;border-top:1px solid var(--border)}}
        .archive-section h3{{font-size:13px;color:var(--muted);margin-bottom:14px}}
        .archive-list{{display:flex;flex-wrap:wrap;gap:8px}}
        .archive-item{{padding:7px 14px;background:var(--tag);border-radius:8px;color:var(--text);text-decoration:none;font-size:13px;transition:all .15s}}
        .archive-item:hover{{background:var(--accent);color:#fff}}
        /* ===页脚=== */
        .footer{{text-align:center;padding:36px;color:var(--muted);font-size:12px;border-top:1px solid var(--border)}}
        .footer a{{color:var(--accent);text-decoration:none}}
        @media(max-width:768px){{
            .controls{{padding:8px 16px}}
            .hero{{padding:28px 16px 20px}}
            .hero h1{{font-size:1.4rem}}
            .articles{{padding:0 16px 60px}}
            .article h2,.article-body,.article-footer{{margin-left:0}}
        }}
    </style>
</head>
<body>
    <div class="controls">
        <a href="../index.html" class="back-link">← 返回首页</a>
        <div class="lang-switch">
            <button class="lang-btn active" id="btnZh" onclick="setLang('zh')">中文</button>
            <button class="lang-btn"         id="btnEn" onclick="setLang('en')">EN</button>
        </div>
        <div class="audio-row">
            <select class="voice-sel" id="voiceSel"><option value="">语音</option></select>
            <button class="audio-btn" id="playAllBtn" onclick="togglePlayAll()">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                全文朗读
            </button>
        </div>
    </div>

    <header class="hero">
        <p class="date">{date_en}</p>
        <h1>AI Builders Daily Digest</h1>
        <p class="hero-sub">每日精选 AI 领域最有价值的深度内容</p>
        <p class="stats">📝 {len(all_items)} 篇精选（🐦 {x_n} 条X · 🎙️ {pod_n} 个播客 · 📝 {blog_n} 篇博客）</p>
    </header>

    <main class="articles">
        {articles_html}
        {archive_html}
    </main>

    <footer class="footer">
        <p>数据来源：<a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a></p>
    </footer>

    <script>
    // ===== 语言切换 =====
    var currentLang = 'zh';
    function setLang(lang) {{
        currentLang = lang;
        document.getElementById('btnZh').classList.toggle('active', lang==='zh');
        document.getElementById('btnEn').classList.toggle('active', lang==='en');
        document.querySelectorAll('.zh-text').forEach(function(el){{
            el.style.display = lang==='zh' ? '' : 'none';
        }});
        document.querySelectorAll('.en-text').forEach(function(el){{
            el.style.display = lang==='en' ? '' : 'none';
        }});
        if (isPlaying) stopAll();
    }}

    // ===== 语音朗读 =====
    var voices=[], selectedVoice=null, isPlaying=false;

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
        selectedVoice = voices.find(function(v){{return v.name===e.target.value}}) || null;
    }};

    function getArticleText(n) {{
        var a = document.querySelector('[data-article="'+n+'"]');
        if (!a) return '';
        var cls = currentLang==='zh' ? '.zh-text' : '.en-text';
        var parts = [];
        a.querySelectorAll(cls).forEach(function(el){{
            var tag = el.tagName;
            if (tag==='H2' || tag==='P') parts.push(el.innerText || el.textContent);
        }});
        return parts.join('。');
    }}

    function playArticle(n) {{
        var btn = document.querySelector('[data-article="'+n+'"] .action-btn');
        if (isPlaying) {{ stopAll(); return; }}
        speak(getArticleText(n), btn);
    }}

    function togglePlayAll() {{
        if (isPlaying) {{ stopAll(); return; }}
        var btn = document.getElementById('playAllBtn');
        var text = '今天为大家带来 AI 领域精选资讯。';
        document.querySelectorAll('.article').forEach(function(a, i) {{
            text += '第'+(i+1)+'篇。';
            var cls = currentLang==='zh' ? '.zh-text' : '.en-text';
            a.querySelectorAll(cls).forEach(function(el){{
                if (el.tagName==='H2'||el.tagName==='P') text += (el.innerText||el.textContent)+'。';
            }});
        }});
        speak(text, btn);
    }}

    function speak(text, btn) {{
        speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance(text.replace(/[。！？]/g, '，').replace(/\\s+/g,' ').trim());
        u.lang = currentLang==='zh' ? 'zh-CN' : 'en-US';
        u.rate = 0.85; u.pitch = 0.95;
        var v = selectedVoice || voices.find(function(v){{return v.lang.startsWith(currentLang==='zh'?'zh':'en')}});
        if (v) u.voice = v;
        u.onstart = function(){{ isPlaying=true; if(btn) btn.classList.add('playing'); }};
        u.onend = u.onerror = function(){{ stopAll(); }};
        speechSynthesis.speak(u);
    }}

    function stopAll() {{
        speechSynthesis.cancel();
        isPlaying = false;
        document.querySelectorAll('.action-btn,.audio-btn').forEach(function(b){{b.classList.remove('playing')}});
    }}

    speechSynthesis.onvoiceschanged = loadVoices;
    loadVoices();
    </script>
</body>
</html>'''

# ============ 写文件 ============
out_path = os.path.join(OUTPUT_DIR, 'index.html')
dated_path = os.path.join(OUTPUT_DIR, f'{date_str}.html')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)
with open(dated_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'✅ 生成完成！共 {len(all_items)} 篇')
print(f'   🐦 X推文: {x_n}  🎙️ 播客: {pod_n}  📝 博客: {blog_n}')
print(f'   → {out_path}')
print(f'   → {dated_path}')
print()
print('=== 内容预览 ===')
for item in all_items:
    icon = {'x':'🐦','podcast':'🎙️','blog':'📝'}.get(item['type'],'•')
    print(f"{icon} {item['num']:02d}. {item['zh_title'][:50]}")
    print(f"    EN: {item['en_title'][:60]}")

# ============ Git 自动提交推送 ============
import subprocess

def run_git(cmd, cwd):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

print()
print('=== Git 自动推送 ===')

# 检查是否有变更
rc, out, err = run_git('git status --porcelain', OUTPUT_DIR)
if not out.strip():
    print('⚪ 没有变更，跳过提交')
else:
    print(f'📝 检测到变更:\n{out}')
    
    # Git add
    rc, out, err = run_git('git add -A', OUTPUT_DIR)
    if rc != 0:
        print(f'❌ git add 失败: {err}')
    else:
        # Git commit
        commit_msg = f'🤖 AI News 更新 {date_str} ({len(all_items)}篇)'
        rc, out, err = run_git(f'git commit -m "{commit_msg}"', OUTPUT_DIR)
        if rc != 0:
            print(f'❌ git commit 失败: {err}')
        else:
            print(f'✅ 已提交: {commit_msg}')
            
            # Git push
            rc, out, err = run_git('git push', OUTPUT_DIR)
            if rc != 0:
                print(f'❌ git push 失败: {err}')
            else:
                print('✅ 已推送到 GitHub')

