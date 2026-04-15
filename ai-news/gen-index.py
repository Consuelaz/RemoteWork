#!/usr/bin/env python3
"""
AI 资讯生成脚本 — 完全对标 remotework.asia/ai-news/2026-04-13.html 样式

核心变化（相比旧版）：
- 布局：统一编号文章列表（01-10），不分建造者/播客/博客区块
- 样式：极简奶油色（#fafaf9）+ 橙色强调（#ea580c）+ 衬线标题
- 语言切换：data-lang 属性（不是 .zh-text/.en-text class）
- 朗读：每篇文章可单独朗读 + 全文朗读
- 语音选择：按语言分组下拉
- 语言偏好：localStorage 持久化

数据规则：
- X: 每条推文一条 article，建造者信息显示在 header
- 播客: 1 条 article，含来源标签
- 博客: 1 条 article，含来源标签
"""

import json, os, re, subprocess
from datetime import datetime

# ============ 路径配置 ============
SKILL_DIR  = '/Users/qisoong/.workbuddy/skills/follow-builders'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f'{SKILL_DIR}/feed-x.json', encoding='utf-8') as f:
    x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json', encoding='utf-8') as f:
    pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json', encoding='utf-8') as f:
    blog_data = json.load(f)

# ============ 规则配置 ============
MAX_ARTICLES  = 10    # 最多文章数
MAX_TWEETS    = 8     # X 推文最多条数
MAX_PODCASTS  = 1    # 播客最多条数
MAX_BLOGS     = 1    # 博客最多条数
SEG_LEN       = 1200  # 播客/博客每段字数

# ============ 工具函数 ============
def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def smart_truncate(text, max_len):
    """在自然断点（句子边界）处截断，不从单词中间截断"""
    if len(text) <= max_len:
        return text
    min_keep = int(max_len * 0.7)
    sentence_ends = '.!?。！？\n'
    for i in range(max_len - 1, min_keep - 1, -1):
        if text[i] in sentence_ends:
            end = i
            while end > 0 and text[end].isspace():
                end -= 1
            if text[end] in sentence_ends:
                return text[:end + 1].strip()
    for i in range(max_len, min(max_len + 300, len(text))):
        if text[i] in sentence_ends:
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

# ============ 收集文章列表 ============
articles = []  # 每篇: {num, avatar, author_name, author_bio, zh_title, en_title,
                #      zh_body, en_body, stats, link_text, link_url, type}

# --- X 推文 ---
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
        body_en = smart_truncate(txt, 400)
        body_zh = ''  # 推文保持英文原文
        articles.append({
            'num':        tweet_count,
            'avatar':     av,
            'author':     esc(name),
            'bio':        esc(bio),
            'zh_title':   '',
            'en_title':   '',
            'zh_body':    esc(body_zh),
            'en_body':    esc(body_en),
            'stats':      f'<span>❤️ {likes:,.0f}</span><span>🔁 {rts:,.0f}</span>',
            'link_text':  '原文 →',
            'link_url':   esc(url),
            'type':       'tweet',
        })
    if tweet_count >= MAX_TWEETS:
        break

# --- 播客 ---
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
        'num':        len(articles) + 1,
        'avatar':     initials(source),
        'author':     esc(source),
        'bio':        esc(pod.get('show', 'AI Podcast')),
        'zh_title':   '',
        'en_title':   esc(title),
        'zh_body':    esc(seg) + '<br><br><em>…（更多内容见原文）</em>',
        'en_body':    esc(seg) + '<br><br><em>...(see original for more)</em>',
        'stats':      '<span>🎙️ Podcast</span>',
        'link_text':  '收听 →',
        'link_url':   esc(url),
        'type':       'podcast',
    })

# --- 博客 ---
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
        'num':        len(articles) + 1,
        'avatar':     initials(source),
        'author':     esc(source),
        'bio':        esc(source),
        'zh_title':   '',
        'en_title':   esc(title),
        'zh_body':    '',
        'en_body':    esc(seg) + '<br><br><em>...(read full article)</em>',
        'stats':      '<span>📝 Blog</span>',
        'link_text':  '阅读 →',
        'link_url':   esc(url),
        'type':       'blog',
    })

# 确保编号连续
for i, a in enumerate(articles, 1):
    a['num'] = i

TOTAL = len(articles)

# ============ 日期 ============
today    = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August',
             'September','October','November','December']
date_en  = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_zh  = f"{today.year}年{today.month}月{today.day}日"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

# ============ 生成文章 HTML ============
def build_article_html(a):
    num_str = f"{a['num']:02d}"
    has_zh_title = bool(a['zh_title'])
    has_zh_body  = bool(a['zh_body'])
    has_body     = a['en_body']

    # 标题行（有中文标题才显示中文行）
    if has_zh_title:
        title_html = f'''            <h2 data-lang="zh">{a['zh_title']}</h2>
            <h2 data-lang="en" style="display:none">{a['en_title']}</h2>'''
    else:
        title_html = f'''            <h2 data-lang="en">{a['en_title']}</h2>'''

    # 正文：有中文正文则双语，否则纯英文
    if has_zh_body:
        body_html = f'''<p data-lang="zh">{a['zh_body']}</p>
                <p data-lang="en" style="display:none">{a['en_body']}</p>'''
    else:
        body_html = f'''<p data-lang="en">{a['en_body']}</p>'''

    return f'''        <!-- {num_str} -->
        <article class="article" data-article="{a['num']}">
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
                    <button class="action-btn" onclick="playArticle({a['num']})">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        朗读
                    </button>
                </div>
            </div>
{title_html}
            <div class="article-body">
{body_html}
            </div>
            <div class="article-footer">
                <div class="article-stats">{a['stats']}</div>
                <a href="{a['link_url']}" class="article-link" target="_blank">{a['link_text']}</a>
            </div>
        </article>'''

articles_html = '\n'.join(build_article_html(a) for a in articles)

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
        archive_links += f'        <a href="{f}" class="archive-item">{y}年{int(mo)}月{int(d)}日</a>\n'

archive_html = f'''    <!-- 历史存档 -->
    <div class="archive-section">
        <h3>📅 历史存档</h3>
        <div class="archive-list">
{archive_links}        </div>
    </div>''' if archive_links else ''

# ============ 完整页面模板（对标 2026-04-13.html）============
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
            --summary-bg: #fff7ed;
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
            padding: 6px 14px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 13px;
            border-radius: 16px;
            transition: all 0.2s;
        }}
        .lang-btn.active {{ background: var(--text); color: white; border-color: var(--text); }}
        .audio-controls {{ display: flex; gap: 8px; align-items: center; }}
        .audio-btn {{
            padding: 6px 14px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 13px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .audio-btn:hover {{ background: var(--tag-bg); }}
        .audio-btn.playing {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .audio-btn svg {{ width: 14px; height: 14px; }}
        .voice-select {{
            padding: 6px 10px;
            border: 1px solid var(--border);
            border-radius: 12px;
            font-size: 12px;
            background: white;
            cursor: pointer;
        }}

        /* 头部 */
        .hero {{
            padding: 40px 40px 30px;
            max-width: 720px;
            margin: 0 auto;
            border-bottom: 1px solid var(--border);
        }}
        .date {{
            font-size: 12px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 12px;
        }}
        .hero h1 {{
            font-family: 'Noto Serif SC', serif;
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        .hero-sub {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}
        .stats {{ font-size: 12px; color: var(--text-secondary); }}

        /* 文章列表 */
        .articles {{
            max-width: 720px;
            margin: 0 auto;
            padding: 0 40px 80px;
        }}

        .article {{
            padding: 32px 0;
            border-bottom: 1px solid var(--border);
        }}
        .article:last-child {{ border-bottom: none; }}

        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}

        .article-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .article-number {{
            font-size: 24px;
            font-weight: 600;
            color: var(--border);
            line-height: 1;
            min-width: 32px;
        }}

        .author-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .author-avatar {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1c1917 0%, #57534e 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 11px;
        }}

        .author-info {{
            display: flex;
            flex-direction: column;
        }}
        .author-name {{ font-weight: 500; font-size: 13px; }}
        .author-bio {{ color: var(--text-secondary); font-size: 12px; }}

        .article-actions {{ display: flex; gap: 6px; }}

        .action-btn {{
            padding: 5px 10px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 12px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .action-btn:hover {{ background: var(--tag-bg); }}
        .action-btn.playing {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .action-btn svg {{ width: 12px; height: 12px; }}

        .article h2 {{
            font-family: 'Noto Serif SC', serif;
            font-size: 1.1rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: 12px;
            margin-left: 44px;
        }}

        .article-body {{ margin-left: 44px; }}

        .article-body p {{
            font-size: 14px;
            line-height: 1.7;
            color: var(--text);
            margin-bottom: 10px;
        }}

        .article-body strong {{ color: var(--accent); }}
        .article-body em {{ color: var(--text-secondary); font-style: normal; font-size: 13px; }}

        .article-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 14px;
            margin-left: 44px;
        }}

        .article-stats {{ display: flex; gap: 12px; font-size: 12px; color: var(--text-secondary); }}
        .article-link {{ color: var(--accent); font-size: 13px; font-weight: 500; text-decoration: none; }}
        .article-link:hover {{ text-decoration: underline; }}

        [data-lang] {{ display: none; }}
        [data-lang].active {{ display: block; }}

        /* 历史存档 */
        .archive-section {{
            max-width: 720px;
            margin: 0 auto;
            padding: 32px 40px;
            border-top: 1px solid var(--border);
        }}
        .archive-section h3 {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 14px; letter-spacing: .5px; text-transform: uppercase; }}
        .archive-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .archive-item {{ padding: 6px 14px; background: var(--tag-bg); border-radius: 8px; color: var(--text-secondary); text-decoration: none; font-size: 13px; transition: all .15s; }}
        .archive-item:hover {{ background: var(--accent); color: white; }}

        /* 页脚 */
        footer {{
            text-align: center;
            padding: 32px 40px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }}
        footer a {{ color: var(--text-secondary); text-decoration: none; }}
        footer a:hover {{ color: var(--accent); }}

        /* 响应式 */
        @media (max-width: 768px) {{
            .controls {{ padding: 10px 20px; }}
            .hero, .archive-section {{ padding: 30px 20px 20px; }}
            .hero h1 {{ font-size: 1.4rem; }}
            .articles {{ padding: 0 20px 60px; }}
            .article h2, .article-body, .article-footer {{ margin-left: 0; }}
        }}
    </style>
</head>
<body>

    <!-- 控制栏 -->
    <div class="controls">
        <div class="lang-switch">
            <button class="lang-btn active" data-lang-switch="zh">中文</button>
            <button class="lang-btn" data-lang-switch="en">EN</button>
        </div>
        <div class="audio-controls">
            <select class="voice-select" id="voiceSelect" title="选择语音">
                <option value="">默认语音</option>
            </select>
            <button class="audio-btn" id="playAllBtn" onclick="playAll()">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                全文朗读
            </button>
        </div>
    </div>

    <!-- 头部 -->
    <header class="hero">
        <p class="date">{date_en}</p>
        <h1>AI Builders Daily Digest</h1>
        <p class="hero-sub" data-lang="zh">每日精选 AI 领域最有价值的深度内容</p>
        <p class="hero-sub" data-lang="en" style="display:none">Daily curated deep content from AI builders</p>
        <p class="stats">
            <span data-lang="zh">📝 {TOTAL} 篇精选</span>
            <span data-lang="en">📝 {TOTAL} Articles</span>
        </p>
    </header>

    <!-- 文章列表 -->
    <main class="articles">
{articles_html}
    </main>

    {archive_html}

    <footer>
        <p>Data by <a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a> · <a href="../index.html">Junes远程</a></p>
    </footer>

    <script>
        let currentUtterance = null;
        let isPlaying = false;
        let currentLang = 'zh';
        let voices = [];
        let selectedVoice = null;

        // 加载语音列表（按语言分组）
        // 初始化：恢复语言偏好
        (function initLang() {{
            const savedLang = localStorage.getItem('ai-news-lang') || 'zh';
            currentLang = savedLang;
            // 更新按钮状态
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.querySelector(`[data-lang-switch="${{savedLang}}"]`);
            if (activeBtn) activeBtn.classList.add('active');
            // 切换所有 data-lang 元素
            document.querySelectorAll('[data-lang]').forEach(el => {{
                el.style.display = el.dataset.lang === savedLang ? 'block' : 'none';
            }});
        }})();

        // 语音加载
        function loadVoices() {{
            voices = speechSynthesis.getVoices();
            const select = document.getElementById('voiceSelect');
            select.innerHTML = '<option value="">选择语音</option>';

            const zhVoices = voices.filter(v => v.lang.startsWith('zh'));
            const enVoices = voices.filter(v => v.lang.startsWith('en'));

            if (zhVoices.length > 0) {{
                const og = document.createElement('optgroup');
                og.label = '中文';
                zhVoices.forEach(v => {{
                    const opt = document.createElement('option');
                    opt.value = v.name;
                    opt.textContent = v.name + (v.localService ? ' ★' : '');
                    og.appendChild(opt);
                }});
                select.appendChild(og);
            }}

            if (enVoices.length > 0) {{
                const og = document.createElement('optgroup');
                og.label = 'English';
                enVoices.forEach(v => {{
                    const opt = document.createElement('option');
                    opt.value = v.name;
                    opt.textContent = v.name + (v.localService ? ' ★' : '');
                    og.appendChild(opt);
                }});
                select.appendChild(og);
            }}

            // 默认选择高质量本地语音
            const highQuality = voices.find(v => v.localService && (v.lang.startsWith('zh') || v.lang.startsWith('en')));
            if (highQuality) {{
                select.value = highQuality.name;
                selectedVoice = highQuality;
            }}
        }}

        document.getElementById('voiceSelect').addEventListener('change', (e) => {{
            selectedVoice = voices.find(v => v.name === e.target.value);
        }});

        // 语言切换（点击按钮）
        document.querySelectorAll('.lang-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const lang = btn.dataset.langSwitch;
                if (currentLang === lang) return;
                currentLang = lang;
                document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('[data-lang]').forEach(el => {{
                    el.style.display = el.dataset.lang === lang ? 'block' : 'none';
                }});
                localStorage.setItem('ai-news-lang', lang);
                if (isPlaying) stopAll();
            }});
        }});

        // 语音预加载
        speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();

        // 单篇朗读
        function playArticle(num) {{
            const article = document.querySelector(`[data-article="${{num}}"]`);
            let text = '';
            article.querySelectorAll(`[data-lang="${{currentLang}}"]`).forEach(el => {{
                if (el.tagName === 'H2' || el.tagName === 'P') {{
                    text += el.textContent + '。';
                }}
            }});
            speak(text, article.querySelector('.action-btn'));
        }}

        // 全文朗读
        function playAll() {{
            const btn = document.getElementById('playAllBtn');
            if (isPlaying) {{ stopAll(); return; }}
            let text = currentLang === 'zh' ? '今天为大家带来 AI 领域的重要资讯。' : 'Here is today\'s AI builders digest.';
            document.querySelectorAll('.article').forEach((a, i) => {{
                text += `第 ${{i + 1}} 篇，`;
                a.querySelectorAll(`[data-lang="${{currentLang}}"]`).forEach(el => {{
                    if (el.tagName === 'H2' || el.tagName === 'P') {{
                        text += el.textContent;
                    }}
                }});
                text += '。';
            }});
            speak(text, btn);
        }}

        function speak(text, btn) {{
            if (isPlaying) {{
                speechSynthesis.cancel();
                isPlaying = false;
                document.querySelectorAll('.action-btn, .audio-btn').forEach(b => b.classList.remove('playing'));
                return;
            }}

            let optimizedText = text
                .replace(/。/g, '，')
                .replace(/\\s+/g, ' ')
                .trim();

            const u = new SpeechSynthesisUtterance(optimizedText);
            u.lang = currentLang === 'zh' ? 'zh-CN' : 'en-US';
            u.rate = 0.85;
            u.pitch = 0.95;
            u.volume = 1.0;

            let voice = selectedVoice;
            if (!voice || !voice.lang.startsWith(currentLang)) {{
                const preferred = voices.find(v => {{
                    if (!v.lang.startsWith(currentLang)) return false;
                    if (v.localService) return true;
                    const n = v.name.toLowerCase();
                    return n.includes('premium') || n.includes('enhanced') ||
                           n.includes('google') || n.includes('apple');
                }});
                voice = preferred || voices.find(v => v.lang.startsWith(currentLang));
            }}

            if (voice) u.voice = voice;

            u.onstart = () => {{ isPlaying = true; btn.classList.add('playing'); }};
            u.onend = u.onerror = () => {{
                isPlaying = false;
                document.querySelectorAll('.action-btn, .audio-btn').forEach(b => b.classList.remove('playing'));
            }};

            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }}

        function stopAll() {{
            speechSynthesis.cancel();
            isPlaying = false;
            document.querySelectorAll('.action-btn, .audio-btn').forEach(b => b.classList.remove('playing'));
        }}

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
print(f'   📝 {TOTAL} 篇精选')
print(f'   → {out_path}')
print(f'   → {dated_path}')

# ============ Git 自动提交推送 ============
print()
print('=== Git 自动推送 ===')

def run_git(cmd):
    result = subprocess.run(cmd, shell=True, cwd=OUTPUT_DIR, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

rc, out, _ = run_git('git status --porcelain')
if not out.strip():
    print('⚪ 没有变更，跳过提交')
else:
    print(f'📝 检测到变更:\n{out}')
    rc, _, err = run_git('git add -A')
    if rc != 0:
        print(f'❌ git add 失败: {err}')
    else:
        commit_msg = f'🤖 AI News 更新 {date_str} ({TOTAL}篇)'
        rc, _, err = run_git(f'git commit -m "{commit_msg}"')
        if rc != 0:
            print(f'❌ git commit 失败: {err}')
        else:
            print(f'✅ 已提交: {commit_msg}')
            rc, _, err = run_git('git push')
            if rc != 0:
                print(f'❌ git push 失败: {err}')
            else:
                print('✅ 已推送到 GitHub')
