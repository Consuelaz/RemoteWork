#!/usr/bin/env python3
import json
import os

with open('/Users/qisoong/.workbuddy/skills/follow-builders/feed-x.json') as f:
    x_data = json.load(f)
with open('/Users/qisoong/.workbuddy/skills/follow-builders/feed-podcasts.json') as f:
    pod_data = json.load(f)
with open('/Users/qisoong/.workbuddy/skills/follow-builders/feed-blogs.json') as f:
    blog_data = json.load(f)

cards = []
for builder in x_data.get('x', []):
    name = builder.get('name', '')
    handle = builder.get('handle', '')
    bio = builder.get('bio', '').split('\n')[0][:60]
    initials = ''.join([n[0] for n in name.split()[:2]])
    
    for tweet in builder.get('tweets', [])[:1]:
        likes = tweet.get('likes', 0)
        url = tweet.get('url', '#')
        text = tweet.get('text', '')[:300]
        cards.append({'name': name, 'handle': handle, 'bio': bio, 'initials': initials, 'likes': likes, 'url': url, 'text': text})

cards.sort(key=lambda x: x['likes'], reverse=True)
top_cards = cards[:10]

date_en = 'Tuesday, April 14, 2026'

articles_html = ''
for i, card in enumerate(top_cards, 1):
    zh_title = card['text'][:50] + '...' if len(card['text']) > 50 else card['text']
    articles_html += f'''
        <article class="article" data-article="{i}">
            <div class="article-header">
                <div class="article-left">
                    <span class="article-number">{i:02d}</span>
                    <div class="author-row">
                        <div class="author-avatar">{card["initials"]}</div>
                        <div class="author-info">
                            <span class="author-name">{card["name"]}</span>
                            <span class="author-bio">{card["bio"]}</span>
                        </div>
                    </div>
                </div>
                <div class="article-actions">
                    <button class="action-btn" onclick="playArticle({i})">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        朗读
                    </button>
                </div>
            </div>
            <h2 data-lang="zh">{zh_title}</h2>
            <h2 data-lang="en" style="display:none">{card["text"]}</h2>
            <div class="article-body">
                <p data-lang="zh">{card["text"]}</p>
                <p data-lang="en" style="display:none">{card["text"]}</p>
            </div>
            <div class="article-footer">
                <div class="article-stats"><span>❤️ {card["likes"]:,}</span></div>
                <a href="{card["url"]}" class="article-link" target="_blank">原文 →</a>
            </div>
        </article>'''

archives = []
for f in os.listdir('.'):
    if f.startswith('2026-') and f.endswith('.html') and f != 'index.html' and '2026-04' in f and '04-14' not in f:
        archives.append(f)
archives.sort(reverse=True)

archive_html = ''
if archives:
    archive_html = f'''
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">
                <a href="{archives[0]}" class="archive-item">{archives[0].replace('.html','').replace('2026-','年').replace('-','月')}日</a>
            </div>
        </div>'''

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
        .article-body p{{font-size:14px;line-height:1.7;margin-bottom:10px}}
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
        [data-lang].active{{display:block}}
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
        <p class="stats">📝 {len(top_cards)} 篇精选</p>
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
        document.querySelectorAll('.lang-btn').forEach(btn=>{{btn.onclick=()=>{{currentLang=btn.dataset.langSwitch;document.querySelectorAll('.lang-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');document.querySelectorAll('[data-lang]').forEach(el=>{{el.style.display=el.dataset.lang===currentLang?'block':'none'}});if(isPlaying)stopAll()}}}});
        function playArticle(n){{const a=document.querySelector(`[data-article="${{n}}"]`);let t='';a.querySelectorAll(`[data-lang="${{currentLang}}"]`).forEach(el=>{{if(el.tagName==='H2'||el.tagName==='P')t+=el.textContent+'。'}});speak(t,a.querySelector('.action-btn'))}}
        function playAll(){{const btn=document.getElementById('playAllBtn');if(isPlaying){{stopAll();return}}let t='今天为大家带来 AI 领域的重要资讯。';document.querySelectorAll('.article').forEach((a,i)=>{{t+=`第 ${{i+1}} 篇，`;a.querySelectorAll(`[data-lang="${{currentLang}}"]`).forEach(el=>{{if(el.tagName==='H2'||el.tagName==='P')t+=el.textContent}})}});speak(t,btn)}}
        function speak(text,btn){{if(isPlaying){{speechSynthesis.cancel();isPlaying=false;document.querySelectorAll('.action-btn,.audio-btn').forEach(b=>b.classList.remove('playing'));return}}const u=new SpeechSynthesisUtterance(text.replace(/。/g,'，').replace(/\\s+/g,' ').trim());u.lang=currentLang==='zh'?'zh-CN':'en-US';u.rate=0.85;u.pitch=0.95;const v=selectedVoice||voices.find(v=>v.lang.startsWith(currentLang));if(v)u.voice=v;u.onstart=()=>{{isPlaying=true;btn.classList.add('playing')}};u.onend=u.onerror=()=>{{isPlaying=false;document.querySelectorAll('.action-btn,.audio-btn').forEach(b=>b.classList.remove('playing'))}};speechSynthesis.cancel();speechSynthesis.speak(u)}}
        function stopAll(){{speechSynthesis.cancel();isPlaying=false;document.querySelectorAll('.action-btn,.audio-btn').forEach(b=>b.classList.remove('playing'))}}
        document.querySelector('[data-lang-switch="zh"]').click();
        speechSynthesis.onvoiceschanged=loadVoices;loadVoices();
    </script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done! {len(top_cards)} articles generated')
