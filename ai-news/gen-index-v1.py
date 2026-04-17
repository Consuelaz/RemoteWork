#!/usr/bin/env python3
"""
AI 资讯生成脚本 V1 - 动态从 feed 读取版本
数据来源：follow-builders feed-x.json / feed-podcasts.json / feed-blogs.json
"""
import json, os, re
from datetime import datetime

SKILL_DIR = '/Users/qisoong/.workbuddy/skills/follow-builders'
OUTPUT_DIR = '/Users/qisoong/WorkBuddy/20260317141747/ai-news'

with open(f'{SKILL_DIR}/feed-x.json') as f: x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json') as f: pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json') as f: blog_data = json.load(f)

def zh_summary(text):
    t = re.sub(r'https?://\S+', '', text).strip()
    t = re.sub(r'\s+', ' ', t)
    if len(t) > 280:
        for i in range(280, 100, -1):
            if t[i] in '.!?。！？':
                t = t[:i+1]
                break
        else:
            t = t[:280] + '…'
    return t

def initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

# ---- 收集推文（按点赞排序）----
all_tweets = []
for b in x_data.get('x', []):
    for t in b.get('tweets', []):
        all_tweets.append({
            'name': b['name'],
            'handle': b['handle'],
            'bio': b['bio'],
            'text': t['text'],
            'url': t['url'],
            'likes': t.get('likes', 0),
            'createdAt': t.get('createdAt', '')
        })

all_tweets.sort(key=lambda x: x['likes'], reverse=True)

ARTICLES = []
for i, tw in enumerate(all_tweets[:8], 1):
    en_body = zh_summary(tw['text'])
    ARTICLES.append({
        'num': i,
        'avatar': initials(tw['name']),
        'author': tw['name'],
        'handle': '@' + tw['handle'],
        'bio': tw['bio'].split('\n')[0][:60] if tw['bio'] else '',
        'type': 'tweet',
        'en_title': en_body[:80] + ('…' if len(en_body) > 80 else ''),
        'en_body': en_body,
        'stats': f'<span>❤️ {tw["likes"]:,}</span>',
        'link_text': '原文 →',
        'link_url': tw['url'],
    })

# ---- 播客 ----
pods = pod_data.get('podcasts', [])
if pods:
    pod = pods[0]
    transcript = pod.get('transcript', '')
    en_body = transcript[:600].strip()
    ARTICLES.append({
        'num': 9,
        'avatar': 'LS',
        'author': 'Latent Space',
        'handle': '@LatentSpacePod',
        'bio': 'AI播客旗舰 · 深度对话AI前沿研究者',
        'type': 'podcast',
        'en_title': pod.get('title', '')[:80],
        'en_body': en_body,
        'stats': '<span>🎙️ 播客精华</span>',
        'link_text': '收听完整 →',
        'link_url': pod.get('url', '#'),
    })

# ---- 博客 ----
blogs = blog_data.get('blogs', [])
if blogs:
    blog = blogs[0]
    content = blog.get('content', blog.get('transcript', ''))
    en_body = content[:600].strip()
    ARTICLES.append({
        'num': 10,
        'avatar': 'AN',
        'author': blog.get('author', 'Anonymous'),
        'handle': '@' + (blog.get('author_handle', 'Unknown')),
        'bio': '技术博客',
        'type': 'blog',
        'en_title': blog.get('title', '')[:80],
        'en_body': en_body,
        'stats': '<span>📝 技术博客</span>',
        'link_text': '阅读原文 →',
        'link_url': blog.get('url', '#'),
    })

TOTAL = len(ARTICLES)

today = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August',
             'September','October','November','December']
date_en = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

# ---- 历史存档 ----
archive_files = sorted([
    f for f in os.listdir(OUTPUT_DIR)
    if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f) and f != f'{date_str}.html'
], reverse=True)[:10]

archive_items = ''
for f in archive_files:
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', f)
    if m:
        y, mo, d = m.groups()
        archive_items += f'<a href="{f}" class="archive-item">{y}年{int(mo)}月{int(d)}日</a>\n'

archive_html = f'''
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">
{archive_items}            </div>
        </div>
''' if archive_items else '<!-- 无历史存档 -->'

# ---- 生成单篇 ----
def build_article(a):
    num_str = f"{a['num']:02d}"
    title_html = f'            <h2 class="article-title en">{esc(a["en_title"])}</h2>'
    body_html = f'                <p class="article-content en">{esc(a["en_body"])}</p>'
    return f'''
        <!-- {num_str} -->
        <article class="article">
            <div class="article-header">
                <div class="article-left">
                    <span class="article-number">{num_str}</span>
                    <div class="author-row">
                        <div class="author-avatar">{a['avatar']}</div>
                        <div class="author-info">
                            <span class="author-name">{esc(a['author'])}</span>
                            <span class="author-handle">{esc(a['handle'])}</span>
                            <span class="author-bio">{esc(a['bio'])}</span>
                        </div>
                    </div>
                </div>
                <div class="article-actions">
                    <button class="action-btn play-btn" onclick="playArticle({a['num']}, this)">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        <span class="btn-text">朗读</span>
                    </button>
                </div>
            </div>
            {title_html}
            <div class="article-body">
{body_html}
            </div>
            <div class="article-footer">
                <div class="article-stats">{a['stats']}</div>
                <a href="{esc(a['link_url'])}" class="article-link" target="_blank">{esc(a['link_text'])}</a>
            </div>
        </article>'''

articles_html = '\n'.join(build_article(a) for a in ARTICLES)

# ---- 完整 HTML ----
HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Builders · {date_str} (V1动态版)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
    <style>
        :root {{ --bg:#fafaf9;--text:#1c1917;--text-secondary:#78716c;--accent:#ea580c;--border:#e7e5e4;--tag-bg:#f5f5f4 }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Inter',-apple-system,sans-serif; background:var(--bg); color:var(--text); line-height:1.7; font-size:15px }}
        .controls {{ position:sticky; top:0; z-index:100; background:rgba(250,250,249,.95); backdrop-filter:blur(10px); border-bottom:1px solid var(--border); padding:10px 40px; display:flex; justify-content:space-between; align-items:center; gap:16px }}
        .lang-switch {{ display:flex; gap:4px }}
        .lang-btn {{ padding:5px 14px; border:1px solid var(--border); background:white; cursor:pointer; font-size:13px; border-radius:16px; transition:all .2s; font-family:inherit }}
        .lang-btn.active {{ background:var(--text); color:white; border-color:var(--text) }}
        .audio-controls {{ display:flex; gap:8px; align-items:center }}
        .audio-btn {{ padding:5px 14px; border:1px solid var(--border); background:white; cursor:pointer; font-size:13px; border-radius:16px; display:flex; align-items:center; gap:6px; font-family:inherit }}
        .audio-btn:hover {{ background:var(--tag-bg) }}
        .audio-btn.playing {{ background:var(--accent); color:white; border-color:var(--accent) }}
        .audio-btn svg {{ width:13px; height:13px }}
        .voice-select {{ padding:5px 10px; border:1px solid var(--border); border-radius:12px; font-size:12px; background:white; cursor:pointer; font-family:inherit }}
        .hero {{ padding:40px 40px 30px; max-width:760px; margin:0 auto; border-bottom:1px solid var(--border) }}
        .badge {{ display:inline-block; background:var(--accent); color:white; font-size:11px; padding:2px 8px; border-radius:10px; margin-right:8px; vertical-align:middle }}
        .date {{ font-size:12px; letter-spacing:1px; text-transform:uppercase; color:var(--accent); margin-bottom:10px }}
        .hero h1 {{ font-size:1.8rem; font-weight:600; margin-bottom:10px }}
        .hero-sub {{ font-size:14px; color:var(--text-secondary); margin-bottom:8px }}
        .stats {{ font-size:12px; color:var(--text-secondary) }}
        .articles {{ max-width:760px; margin:0 auto; padding:0 40px 80px }}
        .article {{ padding:30px 0; border-bottom:1px solid var(--border) }}
        .article:last-child {{ border-bottom:none }}
        .article-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px }}
        .article-left {{ display:flex; align-items:center; gap:12px }}
        .article-number {{ font-size:22px; font-weight:700; color:var(--border); line-height:1; min-width:32px }}
        .author-row {{ display:flex; align-items:center; gap:10px }}
        .author-avatar {{ width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#1c1917 0%,#57534e 100%); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:11px; flex-shrink:0 }}
        .author-info {{ display:flex; flex-direction:column }}
        .author-name {{ font-weight:600; font-size:13px }}
        .author-handle {{ color:var(--accent); font-size:12px }}
        .author-bio {{ color:var(--text-secondary); font-size:12px; max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap }}
        .article-actions {{ display:flex; gap:6px }}
        .action-btn {{ padding:5px 12px; border:1px solid var(--border); background:white; cursor:pointer; font-size:12px; border-radius:12px; display:flex; align-items:center; gap:4px; font-family:inherit; transition:all .2s }}
        .action-btn:hover {{ background:var(--tag-bg) }}
        .action-btn.playing {{ background:var(--accent); color:white; border-color:var(--accent) }}
        .action-btn svg {{ width:11px; height:11px }}
        .article-title {{ font-size:1rem; font-weight:600; line-height:1.4; margin-bottom:10px; margin-left:46px; color:var(--text) }}
        .article-title.en {{ font-size:.9rem; font-weight:500; color:var(--text-secondary) }}
        .article-body {{ margin-left:46px }}
        .article-content {{ font-size:14px; line-height:1.85; color:var(--text) }}
        .article-content.en {{ color:var(--text-secondary) }}
        .article-footer {{ display:flex; justify-content:space-between; align-items:center; margin-top:12px; margin-left:46px }}
        .article-stats {{ display:flex; gap:12px; font-size:12px; color:var(--text-secondary) }}
        .article-link {{ color:var(--accent); font-size:13px; font-weight:500; text-decoration:none }}
        .article-link:hover {{ text-decoration:underline }}
        .archive-section {{ max-width:760px; margin:0 auto; padding:32px 40px; border-top:1px solid var(--border) }}
        .archive-section h3 {{ font-size:12px; color:var(--text-secondary); margin-bottom:14px; letter-spacing:.5px; text-transform:uppercase }}
        .archive-list {{ display:flex; flex-wrap:wrap; gap:8px }}
        .archive-item {{ padding:6px 14px; background:var(--tag-bg); border-radius:8px; color:var(--text-secondary); text-decoration:none; font-size:13px; transition:all .15s }}
        .archive-item:hover {{ background:var(--accent); color:white }}
        footer {{ text-align:center; padding:32px 40px; color:var(--text-secondary); font-size:12px; border-top:1px solid var(--border) }}
        footer a {{ color:var(--text-secondary); text-decoration:none }}
        footer a:hover {{ color:var(--accent) }}
        @media(max-width:768px) {{ .controls{{padding:10px 20px}} .hero,.archive-section{{padding:28px 20px 20px}} .hero h1{{font-size:1.4rem}} .articles{{padding:0 20px 60px}} .article-title,.article-body,.article-footer{{margin-left:0}} }}
    </style>
</head>
<body>
    <div class="controls">
        <div class="lang-switch">
            <button class="lang-btn" disabled style="opacity:.4" title="英文原文版本">🌐 English Only</button>
        </div>
        <div class="audio-controls">
            <select class="voice-select" id="voiceSelect"><option>默认语音</option></select>
            <button class="audio-btn" id="playAllBtn" onclick="playAll()">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span id="playAllLabel">朗读全文</span>
            </button>
        </div>
    </div>
    <header class="hero">
        <p class="date"><span class="badge">V1</span>{date_en}</p>
        <h1>🤖 AI Builders · 动态版</h1>
        <p class="hero-sub">数据来源：Follow Builders · 实时抓取真实内容</p>
        <p class="stats">📝 {TOTAL} 篇精选 &nbsp;|&nbsp; Feed 更新于 {x_data.get('generatedAt','')[:10]}</p>
    </header>
    <main class="articles">
{articles_html}
    </main>
    {archive_html}
    <footer>
        <p>Data by <a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a> · <a href="../index.html">Junes远程</a></p>
    </footer>
    <script>
        var voices=[];var isPlaying=false;var currentUtterance=null;var selectedVoice=null;
        function loadVoices(){{voices=speechSynthesis.getVoices();var s=document.getElementById('voiceSelect');s.innerHTML='<option>默认语音</option>';voices.forEach(function(v){{var o=document.createElement('option');o.value=v.name;o.textContent=v.name+(v.localService?' ★':'');if(v.lang.startsWith('en'))s.appendChild(o)}})}}
        document.getElementById('voiceSelect').addEventListener('change',function(e){{selectedVoice=voices.find(function(v){{return v.name===e.target.value}})||null}});
        function getText(num){{var arts=document.querySelectorAll('.article');if(!arts[num-1])return'';var a=arts[num-1];var parts=[];a.querySelectorAll('.article-content').forEach(function(el){{parts.push(el.textContent)}});return parts.join(' ')}}
        function playArticle(num,btn){{var text=getText(num);if(!text)return;if(isPlaying){{speechSynthesis.cancel();isPlaying=false;currentUtterance=null;document.querySelectorAll('.action-btn,.audio-btn').forEach(function(b){{b.classList.remove('playing')}});document.getElementById('playAllLabel').textContent='朗读全文';document.querySelectorAll('.action-btn .btn-text').forEach(function(t){{t.textContent='朗读'}});return}}var u=new SpeechSynthesisUtterance(text.replace(/\s+/g,' '));u.lang='en-US';u.rate=0.85;var v=selectedVoice||voices.find(function(v){{return v.localService||v.name.toLowerCase().includes('google')}});if(v)u.voice=v;u.onstart=function(){{isPlaying=true;currentUtterance=u;btn.classList.add('playing');btn.querySelector('.btn-text').textContent='停止'}};u.onend=u.onerror=function(){{isPlaying=false;currentUtterance=null;btn.classList.remove('playing');btn.querySelector('.btn-text').textContent='朗读'}};speechSynthesis.cancel();speechSynthesis.speak(u)}}
        function playAll(){{var btn=document.getElementById('playAllBtn');var label=document.getElementById('playAllLabel');if(isPlaying){{speechSynthesis.cancel();isPlaying=false;currentUtterance=null;btn.classList.remove('playing');label.textContent='朗读全文';return}}var texts=[];document.querySelectorAll('.article').forEach(function(a){{var parts=[];a.querySelectorAll('.article-content').forEach(function(el){{parts.push(el.textContent)}});if(parts.length)texts.push(parts.join(' '))}});var u=new SpeechSynthesisUtterance(texts.join(' ').replace(/\s+/g,' '));u.lang='en-US';u.rate=0.85;var v=selectedVoice||voices.find(function(v){{return v.localService||v.name.toLowerCase().includes('google')}});if(v)u.voice=v;u.onstart=function(){{isPlaying=true;currentUtterance=u;btn.classList.add('playing');label.textContent='停止'}};u.onend=u.onerror=function(){{isPlaying=false;currentUtterance=null;btn.classList.remove('playing');label.textContent='朗读全文'}};speechSynthesis.cancel();speechSynthesis.speak(u)}}
        speechSynthesis.onvoiceschanged=loadVoices;loadVoices();
    </script>
</body>
</html>'''

out_path = os.path.join(OUTPUT_DIR, 'index-v1.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'✅ 版本1生成完成')
print(f'   文件: {out_path}')
print(f'   📝 {TOTAL} 篇精选')
print(f'   Feed更新: {x_data.get("generatedAt","")[:10]}')
print(f'   来源: feed-x.json 动态读取（英文原文）')
