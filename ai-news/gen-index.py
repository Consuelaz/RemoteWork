#!/usr/bin/env python3
"""
AI 资讯生成脚本 — 对标 remotework.asia/ai-news/2026-04-13.html 样式
"""

import json, os, re, subprocess
from datetime import datetime

SKILL_DIR  = '/Users/qisoong/.workbuddy/skills/follow-builders'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f'{SKILL_DIR}/feed-x.json', encoding='utf-8') as f:
    x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json', encoding='utf-8') as f:
    pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json', encoding='utf-8') as f:
    blog_data = json.load(f)

MAX_ARTICLES = 10
MAX_TWEETS   = 8
MAX_PODCASTS = 1
MAX_BLOGS    = 1
SEG_LEN      = 1200

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def smart_truncate(text, max_len):
    if len(text) <= max_len:
        return text
    min_keep = int(max_len * 0.7)
    for i in range(max_len - 1, min_keep - 1, -1):
        if text[i] in '.!?。！？\n':
            end = i
            while end > 0 and text[end].isspace():
                end -= 1
            if text[end] in '.!?。！？':
                return text[:end + 1].strip()
    for i in range(max_len, min(max_len + 300, len(text))):
        if text[i] in '.!?。！？\n':
            return text[:i + 1].strip()
    for i in range(max_len - 1, min_keep, -1):
        if text[i].isspace():
            return text[:i].strip()
    return text[:max_len].rsplit(' ', 1)[0] + '…'

def initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

articles = []

# X 推文
tweet_count = 0
for b in x_data.get('x', []):
    name   = b.get('name', '')
    handle = b.get('handle', '')
    bio    = (b.get('bio') or '').split('\n')[0][:60]
    av     = initials(name)
    for t in b.get('tweets', []):
        if tweet_count >= MAX_TWEETS:
            break
        txt   = t.get('text', '').strip()
        likes = t.get('likes', 0)
        rts   = t.get('retweets', 0)
        url   = t.get('url', '#')
        if not txt:
            continue
        tweet_count += 1
        body = smart_truncate(txt, 400)
        articles.append({
            'num': tweet_count,
            'avatar': av,
            'author': esc(name),
            'bio': esc(bio),
            'en_body': esc(body),
            'stats': f'<span>❤️ {likes:,.0f}</span><span>🔁 {rts:,.0f}</span>',
            'link_text': '原文 →',
            'link_url': esc(url),
            'type': 'tweet',
        })
    if tweet_count >= MAX_TWEETS:
        break

# 播客
pod_count = 0
for pod in pod_data.get('podcasts', []):
    if pod_count >= MAX_PODCASTS:
        break
    transcript = pod.get('transcript', '')
    if not transcript:
        continue
    title  = pod.get('title', '')[:80]
    url    = pod.get('url', '#')
    source = pod.get('source', pod.get('show', 'AI Podcast'))
    seg    = smart_truncate(transcript[:SEG_LEN], 600)
    if len(seg) < 50:
        continue
    pod_count += 1
    articles.append({
        'num': len(articles) + 1,
        'avatar': initials(source),
        'author': esc(source),
        'bio': esc(pod.get('show', 'AI Podcast')),
        'en_body': esc(seg) + '<br><br><em>...(see original for more)</em>',
        'stats': '<span>🎙️ Podcast</span>',
        'link_text': '收听 →',
        'link_url': esc(url),
        'type': 'podcast',
    })

# 博客
blog_count = 0
for blog in blog_data.get('blogs', []):
    if blog_count >= MAX_BLOGS:
        break
    content = blog.get('transcript', blog.get('content', ''))
    if not content:
        continue
    title  = blog.get('title', '')[:80]
    url    = blog.get('url', '#')
    source = blog.get('source', 'Tech Blog')
    seg    = smart_truncate(content[:SEG_LEN], 600)
    if len(seg) < 50:
        continue
    blog_count += 1
    articles.append({
        'num': len(articles) + 1,
        'avatar': initials(source),
        'author': esc(source),
        'bio': esc(source),
        'en_body': esc(seg) + '<br><br><em>...(read full article)</em>',
        'stats': '<span>📝 Blog</span>',
        'link_text': '阅读 →',
        'link_url': esc(url),
        'type': 'blog',
    })

for i, a in enumerate(articles, 1):
    a['num'] = i

TOTAL = len(articles)

today    = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August',
             'September','October','November','December']
date_en  = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

# 文章 HTML
articles_html = ''
for a in articles:
    num_str = f"{a['num']:02d}"
    articles_html += f'''        <!-- {num_str} -->
        <article class="article" id="article-{a['num']}">
            <div class="article-header">
                <div class="article-left">
                    <span class="article-number">{num_str}</span>
                    <div class="author-row">
                        <div class="author-avatar">{a['avatar']}</div>
                        <div class="author-info">
                            <span class="author-name">{a['author']}</span>
                            <span class="author-bio">{a['bio']}</span>
                        </div>
                    </div>
                </div>
                <div class="article-actions">
                    <button class="action-btn" id="play-btn-{a['num']}" onclick="togglePlay({a['num']})">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        朗读
                    </button>
                </div>
            </div>
            <div class="article-body">
                <p>{a['en_body']}</p>
            </div>
            <div class="article-footer">
                <div class="article-stats">{a['stats']}</div>
                <a href="{a['link_url']}" class="article-link" target="_blank">{a['link_text']}</a>
            </div>
        </article>
'''

# 历史存档
archive_files = sorted([
    f for f in os.listdir(OUTPUT_DIR)
    if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f)
], reverse=True)[:10]

archive_links = ''
for f in archive_files:
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})\.html', f)
    if m:
        y, mo, d = m.groups()
        archive_links += f'        <a href="{f}" class="archive-item">{y}年{int(mo)}月{int(d)}日</a>\n'

archive_section = ''
if archive_links:
    archive_section = f'''    <!-- 历史存档 -->
    <div class="archive-section">
        <h3>📅 历史存档</h3>
        <div class="archive-list">
{archive_links}        </div>
    </div>'''

# ======== 完整页面模板 ========
HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Builders · {date_str}</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
    <style>
        :root {{
            --bg: #fafaf9;
            --text: #1c1917;
            --text-secondary: #78716c;
            --accent: #ea580c;
            --border: #e7e5e4;
            --tag-bg: #f5f5f4;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            font-size: 15px;
        }}

        /* 控制栏 */
        .controls {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(250, 250, 249, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            padding: 12px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .lang-switch {{ display: flex; gap: 6px; }}
        .lang-btn {{
            padding: 6px 16px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 13px;
            border-radius: 20px;
            font-family: inherit;
            transition: all 0.2s;
        }}
        .lang-btn:hover {{ background: var(--tag-bg); }}
        .lang-btn.on {{ background: var(--text); color: white; border-color: var(--text); }}
        .audio-controls {{ display: flex; gap: 8px; align-items: center; }}
        .audio-btn {{
            padding: 6px 16px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 13px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: inherit;
        }}
        .audio-btn:hover {{ background: var(--tag-bg); }}
        .audio-btn.on {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .audio-btn svg {{ width: 14px; height: 14px; }}
        .voice-select {{
            padding: 6px 10px;
            border: 1px solid var(--border);
            border-radius: 16px;
            font-size: 12px;
            background: white;
            font-family: inherit;
        }}

        /* 头部 */
        .hero {{
            padding: 40px 40px 30px;
            max-width: 720px;
            margin: 0 auto;
            border-bottom: 1px solid var(--border);
        }}
        .date {{ font-size: 12px; letter-spacing: 1px; text-transform: uppercase; color: var(--accent); margin-bottom: 12px; }}
        .hero h1 {{ font-family: 'Noto Serif SC', serif; font-size: 1.8rem; font-weight: 600; margin-bottom: 12px; }}
        .hero-sub {{ font-size: 14px; color: var(--text-secondary); margin-bottom: 16px; }}
        .stats {{ font-size: 12px; color: var(--text-secondary); }}

        /* 文章列表 */
        .articles {{ max-width: 720px; margin: 0 auto; padding: 0 40px 80px; }}

        .article {{ padding: 32px 0; border-bottom: 1px solid var(--border); }}
        .article:last-child {{ border-bottom: none; }}
        .article-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }}
        .article-left {{ display: flex; align-items: center; gap: 12px; }}
        .article-number {{ font-size: 24px; font-weight: 600; color: var(--border); line-height: 1; min-width: 32px; }}
        .author-row {{ display: flex; align-items: center; gap: 10px; }}
        .author-avatar {{
            width: 32px; height: 32px; border-radius: 50%;
            background: linear-gradient(135deg, #1c1917 0%, #57534e 100%);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 600; font-size: 11px;
        }}
        .author-info {{ display: flex; flex-direction: column; }}
        .author-name {{ font-weight: 500; font-size: 13px; }}
        .author-bio {{ color: var(--text-secondary); font-size: 12px; }}
        .article-actions {{ display: flex; gap: 6px; }}
        .action-btn {{
            padding: 5px 10px; border: 1px solid var(--border);
            background: white; cursor: pointer; font-size: 12px;
            border-radius: 12px; display: flex; align-items: center; gap: 4px;
            font-family: inherit;
        }}
        .action-btn:hover {{ background: var(--tag-bg); }}
        .action-btn.on {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .action-btn svg {{ width: 12px; height: 12px; }}
        .article-body p {{ font-size: 14px; line-height: 1.75; color: var(--text); margin-bottom: 10px; }}
        .article-body em {{ color: var(--text-secondary); font-style: normal; font-size: 13px; }}
        .article-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 14px; }}
        .article-stats {{ display: flex; gap: 12px; font-size: 12px; color: var(--text-secondary); }}
        .article-link {{ color: var(--accent); font-size: 13px; font-weight: 500; text-decoration: none; }}
        .article-link:hover {{ text-decoration: underline; }}

        /* 历史存档 */
        .archive-section {{ max-width: 720px; margin: 0 auto; padding: 32px 40px; border-top: 1px solid var(--border); }}
        .archive-section h3 {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 14px; letter-spacing: .5px; text-transform: uppercase; }}
        .archive-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .archive-item {{ padding: 6px 14px; background: var(--tag-bg); border-radius: 8px; color: var(--text-secondary); text-decoration: none; font-size: 13px; transition: all .15s; }}
        .archive-item:hover {{ background: var(--accent); color: white; }}

        footer {{ text-align: center; padding: 32px 40px; color: var(--text-secondary); font-size: 12px; border-top: 1px solid var(--border); }}
        footer a {{ color: var(--text-secondary); text-decoration: none; }}
        footer a:hover {{ color: var(--accent); }}

        @media (max-width: 768px) {{
            .controls {{ padding: 10px 20px; flex-wrap: wrap; gap: 8px; }}
            .hero, .archive-section {{ padding: 30px 20px 20px; }}
            .hero h1 {{ font-size: 1.4rem; }}
            .articles {{ padding: 0 20px 60px; }}
        }}
    </style>
</head>
<body>

    <!-- 控制栏 -->
    <div class="controls">
        <div class="lang-switch">
            <button class="lang-btn on" id="btn-zh" onclick="setLang('zh')">中文</button>
            <button class="lang-btn" id="btn-en" onclick="setLang('en')">EN</button>
        </div>
        <div class="audio-controls">
            <select class="voice-select" id="voiceSelect"><option value="">选择语音</option></select>
            <button class="audio-btn" id="playAllBtn" onclick="togglePlayAll()">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span id="playAllLabel">全文朗读</span>
            </button>
        </div>
    </div>

    <!-- 头部 -->
    <header class="hero">
        <p class="date" id="date-en">{date_en}</p>
        <h1 id="title-zh">AI Builders 每日精选</h1>
        <p class="hero-sub" id="subtitle-zh">每日精选 AI 领域最有价值的深度内容</p>
        <p class="stats" id="stats-zh">📝 {TOTAL} 篇精选</p>
    </header>

    <!-- 文章列表 -->
    <main class="articles">
{articles_html}
    </main>

{archive_section}

    <footer>
        <p>Data by <a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a> · <a href="../index.html">Junes远程</a></p>
    </footer>

    <script>
        // ====== 语言切换 ======
        var LANG = 'zh';
        var LABELS = {{
            'zh': {{'title':'AI Builders 每日精选','subtitle':'每日精选 AI 领域最有价值的深度内容','stats':'📝 {TOTAL} 篇精选','playBtn':'朗读','playAll':'全文朗读','stopAll':'停止','voicePrompt':'选择语音'}},
            'en': {{'title':'AI Builders Daily Digest','subtitle':'Daily curated deep content from AI builders','stats':'📝 {TOTAL} Articles','playBtn':'Read','playAll':'Read All','stopAll':'Stop','voicePrompt':'Select Voice'}}
        }};

        function setLang(lang) {{
            LANG = lang;
            var ls = LABELS[lang];

            // 更新按钮高亮
            document.getElementById('btn-zh').className = 'lang-btn' + (lang === 'zh' ? ' on' : '');
            document.getElementById('btn-en').className = 'lang-btn' + (lang === 'en' ? ' on' : '');

            // 更新头部文本
            document.getElementById('title-zh').textContent = ls.title;
            document.getElementById('subtitle-zh').textContent = ls.subtitle;
            document.getElementById('stats-zh').textContent = ls.stats;
            document.getElementById('playAllLabel').textContent = isPlaying ? ls.stopAll : ls.playAll;
            document.getElementById('voiceSelect').options[0].textContent = ls.voicePrompt;

            // 更新每篇文章的朗读按钮
            var btns = document.querySelectorAll('.action-btn');
            btns.forEach(function(btn) {{
                var playing = btn.classList.contains('on');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>' + (playing ? ls.stopAll : ls.playBtn);
            }});

            // 保存偏好
            try {{ localStorage.setItem('ai-news-lang', lang); }} catch(e) {{}}
        }}

        // ====== 语音朗读 ======
        var voices = [];
        var isPlaying = false;
        var currentUtterance = null;

        function loadVoices() {{
            voices = speechSynthesis.getVoices();
            var sel = document.getElementById('voiceSelect');
            sel.innerHTML = '<option value="">' + LABELS[LANG].voicePrompt + '</option>';
            var zhList = [], enList = [];
            voices.forEach(function(v) {{
                if (v.lang.startsWith('zh')) zhList.push(v);
                else if (v.lang.startsWith('en')) enList.push(v);
            }});
            if (zhList.length) {{
                var og = document.createElement('optgroup'); og.label = '中文';
                zhList.forEach(function(v) {{ var o = document.createElement('option'); o.value = v.name; o.textContent = v.name + (v.localService ? ' ★' : ''); og.appendChild(o); }});
                sel.appendChild(og);
            }}
            if (enList.length) {{
                var og = document.createElement('optgroup'); og.label = 'English';
                enList.forEach(function(v) {{ var o = document.createElement('option'); o.value = v.name; o.textContent = v.name + (v.localService ? ' ★' : ''); og.appendChild(o); }});
                sel.appendChild(og);
            }}
        }}

        document.getElementById('voiceSelect').addEventListener('change', function(e) {{}});

        function getVoice() {{
            var sel = document.getElementById('voiceSelect');
            if (sel.value) return voices.find(function(v) {{ return v.name === sel.value; }});
            var pref = voices.find(function(v) {{ return v.localService && v.lang.startsWith(LANG); }});
            if (pref) return pref;
            return voices.find(function(v) {{ return v.lang.startsWith(LANG); }});
        }}

        function buildText(num) {{
            var art = document.getElementById('article-' + num);
            var parts = [];
            var ps = art.querySelectorAll('p');
            ps.forEach(function(p) {{ parts.push(p.textContent); }});
            return parts.join('。');
        }}

        function togglePlay(num) {{
            if (isPlaying && currentBtn && currentBtnNum === num) {{
                stopAll(); return;
            }}
            if (isPlaying) stopAll();
            var text = buildText(num);
            var btn = document.getElementById('play-btn-' + num);
            var u = new SpeechSynthesisUtterance(text);
            u.lang = 'en-US';
            u.rate = 0.85; u.pitch = 0.95; u.volume = 1.0;
            var v = getVoice();
            if (v) u.voice = v;
            u.onstart = function() {{
                isPlaying = true; currentBtn = btn; currentBtnNum = num;
                btn.classList.add('on');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>' + LABELS[LANG].stopAll;
            }};
            u.onend = u.onerror = function() {{
                isPlaying = false; currentBtn = null; currentBtnNum = null;
                btn.classList.remove('on');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>' + LABELS[LANG].playBtn;
                document.getElementById('playAllBtn').classList.remove('on');
                document.getElementById('playAllLabel').textContent = LABELS[LANG].playAll;
            }};
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }}

        function togglePlayAll() {{
            if (isPlaying) {{ stopAll(); return; }}
            var allText = 'Here is today AI builders digest. ';
            var arts = document.querySelectorAll('.article');
            arts.forEach(function(art, i) {{
                allText += 'Article ' + (i+1) + '. ';
                var ps = art.querySelectorAll('p');
                ps.forEach(function(p) {{ allText += p.textContent + '. '; }});
            }});
            var u = new SpeechSynthesisUtterance(allText);
            u.lang = 'en-US'; u.rate = 0.85; u.pitch = 0.95; u.volume = 1.0;
            var v = getVoice();
            if (v) u.voice = v;
            u.onstart = function() {{
                isPlaying = true;
                document.getElementById('playAllBtn').classList.add('on');
                document.getElementById('playAllLabel').textContent = LABELS[LANG].stopAll;
            }};
            u.onend = u.onerror = function() {{
                isPlaying = false;
                document.getElementById('playAllBtn').classList.remove('on');
                document.getElementById('playAllLabel').textContent = LABELS[LANG].playAll;
                document.querySelectorAll('.action-btn.on').forEach(function(b) {{ b.classList.remove('on'); }});
                document.querySelectorAll('.action-btn').forEach(function(btn) {{
                    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>' + LABELS[LANG].playBtn;
                }});
            }};
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }}

        function stopAll() {{
            speechSynthesis.cancel();
            isPlaying = false; currentBtn = null; currentBtnNum = null;
            document.getElementById('playAllBtn').classList.remove('on');
            document.getElementById('playAllLabel').textContent = LABELS[LANG].playAll;
            document.querySelectorAll('.action-btn').forEach(function(btn) {{
                btn.classList.remove('on');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>' + LABELS[LANG].playBtn;
            }});
        }}

        // 初始化
        speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();
        try {{
            var saved = localStorage.getItem('ai-news-lang');
            if (saved === 'en') setLang('en');
        }} catch(e) {{}}
    </script>
</body>
</html>'''

out_path   = os.path.join(OUTPUT_DIR, 'index.html')
dated_path = os.path.join(OUTPUT_DIR, f'{date_str}.html')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)
with open(dated_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'✅ 生成完成！')
print(f'   📝 {TOTAL} 篇精选')
print(f'   → {out_path}')
print(f'   → {dated_path}')

# Git 自动推送（不提交，由用户手动控制）
print()
print('=== Git 推送 ===')
def run_git(cmd):
    result = subprocess.run(cmd, shell=True, cwd=OUTPUT_DIR, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

rc, out, _ = run_git('git status --porcelain')
if not out.strip():
    print('⚪ 没有变更')
else:
    run_git('git add -A')
    commit_msg = f'🤖 AI News 更新 {date_str} ({TOTAL}篇)'
    rc, _, err = run_git(f'git commit -m "{commit_msg}"')
    if rc != 0:
        print(f'⚠️ commit: {err.strip()}')
    else:
        print(f'✅ 已提交: {commit_msg}')
        rc, _, err = run_git('git push')
        if rc != 0:
            print(f'⚠️ push: {err.strip()}')
        else:
            print('✅ 已推送到 GitHub')
