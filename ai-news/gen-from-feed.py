#!/usr/bin/env python3
"""
AI 资讯生成脚本 - 从 follow-builders 数据源实时读取
用法: python3 gen-from-feed.py [YYYY-MM-DD]
默认生成今天的资讯

每天10篇文章：
  - 8条 X 开发者动态（按点赞数排序，最多8位建造者）
  - 1段播客精华
  - 1篇技术博客

每篇含：中文摘要 + 英文原文 + 语言切换 + 语音朗读
"""

import json, os, re, sys, ssl
from datetime import datetime, timedelta
from urllib.request import urlopen, Request

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FEED_DIR = os.path.expanduser('~/.workbuddy/skills/follow-builders')

# ============ 工具 ============
def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def smart_truncate(text, max_len):
    if len(text) <= max_len:
        return text
    min_keep = int(max_len * 0.7)
    for i in range(max_len - 1, min_keep - 1, -1):
        if text[i] in '.!?。！？\n':
            return text[:i + 1].strip()
    for i in range(max_len, min(max_len + 300, len(text))):
        if text[i] in '.!?。！？\n':
            return text[:i + 1].strip()
    for i in range(max_len - 1, min_keep, -1):
        if text[i].isspace():
            return text[:i].strip()
    return text[:max_len].rsplit(' ', 1)[0] + '…'

def initials(name):
    parts = str(name).split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

def date_en(dt):
    DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    MONS = ['January','February','March','April','May','June','July','August',
            'September','October','November','December']
    return f"{DAYS[dt.weekday()]}, {MONS[dt.month-1]} {dt.day}, {dt.year}"

# ============ 数据读取 ============
def sync_feeds():
    """从 GitHub 同步最新数据"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    urls = {
        'feed-x.json': 'https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json',
        'feed-podcasts.json': 'https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-podcasts.json',
        'feed-blogs.json': 'https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-blogs.json',
    }
    for fname, url in urls.items():
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=15, context=ctx) as r:
                data = r.read().decode('utf-8')
                with open(os.path.join(FEED_DIR, fname), 'w') as f:
                    f.write(data)
                print(f'  ✅ {fname}')
        except Exception as e:
            print(f'  ⚠️ {fname}: {e}')

def load_feeds():
    """加载数据源"""
    feeds = {}
    for fname in ['feed-x.json', 'feed-podcasts.json', 'feed-blogs.json']:
        path = os.path.join(FEED_DIR, fname)
        if os.path.exists(path):
            with open(path, 'r') as f:
                feeds[fname] = json.load(f)
    return feeds

# ============ 文章生成 ============
def generate_articles(feeds):
    """从数据源生成文章列表"""
    articles = []
    num = 0

    # X 推文 - 按总点赞数排序建造者，取最多8位
    if 'feed-x.json' in feeds:
        x_data = feeds['feed-x.json']
        builders = x_data.get('x', [])

        # 计算每位建造者的总点赞
        for builder in builders:
            total_likes = sum(t.get('likes', 0) for t in builder.get('tweets', []))
            builder['_total_likes'] = total_likes

        # 按总点赞排序，取前8位
        builders.sort(key=lambda b: b.get('_total_likes', 0), reverse=True)
        builders = builders[:8]

        for builder in builders:
            tweets = sorted(builder.get('tweets', []), key=lambda t: t.get('likes', 0), reverse=True)[:3]
            for tweet in tweets:
                num += 1
                text = tweet.get('text', '')
                likes = tweet.get('likes', 0)
                retweets = tweet.get('retweets', 0)
                url = tweet.get('url', '')

                articles.append({
                    'num': num,
                    'avatar': initials(builder.get('name', 'XX')),
                    'author': builder.get('name', ''),
                    'handle': '@' + builder.get('handle', ''),
                    'bio': builder.get('bio', '').replace('\n', ' ')[:60],
                    'type': 'tweet',
                    'zh_title': smart_truncate(text, 50),
                    'en_title': smart_truncate(text, 80),
                    'zh_body': smart_truncate(text, 150),
                    'en_body': smart_truncate(text, 200),
                    'stats': f'<span>❤️ {likes}</span><span>🔁 {retweets}</span>',
                    'link_text': '原文 →',
                    'link_url': url,
                })
                if num >= 8:
                    break
            if num >= 8:
                break

    # 播客 - 取第一个
    if 'feed-podcasts.json' in feeds and num < 9:
        podcasts_data = feeds['feed-podcasts.json']
        podcasts = podcasts_data.get('podcasts', [])
        if podcasts:
            podcast = podcasts[0]
            num += 1
            title = podcast.get('title', '')
            summary = podcast.get('summary', '')[:500]

            articles.append({
                'num': num,
                'avatar': initials(podcast.get('source', 'XX')),
                'author': podcast.get('source', ''),
                'handle': podcast.get('source', ''),
                'bio': 'AI播客精华',
                'type': 'podcast',
                'zh_title': smart_truncate(title, 50),
                'en_title': smart_truncate(title, 80),
                'zh_body': smart_truncate(summary, 150),
                'en_body': smart_truncate(summary, 200),
                'stats': '<span>🎙️ 播客精华</span>',
                'link_text': '收听完整 →',
                'link_url': podcast.get('url', ''),
            })

    # 博客 - 取第一个
    if 'feed-blogs.json' in feeds and num < 10:
        blogs_data = feeds['feed-blogs.json']
        blogs = blogs_data.get('blogs', [])
        if blogs:
            blog = blogs[0]
            num += 1
            title = blog.get('title', '')
            content = blog.get('content', '')[:500]

            articles.append({
                'num': num,
                'avatar': initials(blog.get('source', 'XX')),
                'author': blog.get('source', ''),
                'handle': blog.get('source', ''),
                'bio': '技术博客',
                'type': 'blog',
                'zh_title': smart_truncate(title, 50),
                'en_title': smart_truncate(title, 80),
                'zh_body': smart_truncate(content, 150),
                'en_body': smart_truncate(content, 200),
                'stats': '<span>📝 博客</span>',
                'link_text': '阅读原文 →',
                'link_url': blog.get('url', ''),
            })

    return articles

# ============ HTML 生成（复用原有模板）===========
def generate_html(date_str, articles, archive_dates):
    """生成 HTML 页面"""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    day_label = dt.strftime('%-m月%-d日')

    archives_html = ''
    for d in archive_dates:
        active = 'active' if d == date_str else ''
        archives_html += f'<a href="{d}.html" class="archive-item {active}">{d}</a>\n'

    articles_html = ''
    for a in articles:
        type_icon = {'tweet': '🐦', 'podcast': '🎙️', 'blog': '📝'}.get(a['type'], '📄')
        type_tag = {'tweet': '建造者动态', 'podcast': '播客精华', 'blog': '博客'}.get(a['type'], '内容')
        badge_class = {'tweet': 'blue', 'podcast': 'green', 'blog': 'purple'}.get(a['type'], '')

        articles_html += f'''
        <div class="article-card">
            <div class="article-header">
                <div class="builder-info">
                    <div class="avatar">{esc(a['avatar'])}</div>
                    <div class="builder-meta">
                        <span class="builder-name">{esc(a['author'])}</span>
                        <span class="builder-handle">{esc(a['handle'])}</span>
                    </div>
                </div>
                <span class="type-badge {badge_class}">{type_icon} {type_tag}</span>
            </div>
            <h3 class="article-title">
                <span class="zh-text">{esc(a['zh_title'])}</span>
                <span class="en-text">{esc(a['en_title'])}</span>
            </h3>
            <div class="article-content">
                <span class="zh-text">{esc(a['zh_body'])}</span>
                <span class="en-text">{esc(a['en_body'])}</span>
            </div>
            <div class="article-footer">
                <span class="stats">{a['stats']}</span>
                <a href="{esc(a['link_url'])}" target="_blank" class="read-more">{esc(a['link_text'])}</a>
            </div>
        </div>
        '''

    # 统计
    tweet_count = len([a for a in articles if a['type'] == 'tweet'])
    podcast_count = len([a for a in articles if a['type'] == 'podcast'])
    blog_count = len([a for a in articles if a['type'] == 'blog'])

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 资讯 - {date_str}</title>
    <style>
        :root {{
            --primary: #1E3A5F;
            --accent: #2563EB;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text: #1E293B;
            --text-light: #64748B;
            --border: #E2E8F0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
        .navbar {{ background: white; border-bottom: 1px solid var(--border); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }}
        .nav-links {{ display: flex; gap: 1.5rem; }}
        .nav-links a {{ color: var(--text); text-decoration: none; font-weight: 500; }}
        .nav-links a:hover {{ color: var(--accent); }}
        .nav-controls {{ display: flex; gap: 1rem; align-items: center; }}
        .lang-toggle {{ display: flex; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }}
        .lang-btn {{ padding: 0.4rem 0.8rem; background: white; border: none; cursor: pointer; font-size: 0.85rem; }}
        .lang-btn.active {{ background: var(--accent); color: white; }}
        .hero {{ background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; padding: 3rem 2rem; text-align: center; }}
        .hero h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .hero-date {{ font-size: 1.2rem; opacity: 0.9; margin-bottom: 1.5rem; }}
        .hero-stats {{ display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; }}
        .stat-badge {{ background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; }}
        .container {{ max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
        .section-title {{ font-size: 1.3rem; color: var(--primary); margin: 2rem 0 1rem; display: flex; align-items: center; gap: 0.5rem; }}
        .article-card {{ background: var(--card-bg); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .article-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
        .builder-info {{ display: flex; align-items: center; gap: 0.75rem; }}
        .avatar {{ width: 40px; height: 40px; background: linear-gradient(135deg, #667EEA, #764BA2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9rem; }}
        .builder-meta {{ display: flex; flex-direction: column; }}
        .builder-name {{ font-weight: 600; font-size: 0.95rem; }}
        .builder-handle {{ color: var(--text-light); font-size: 0.8rem; }}
        .type-badge {{ padding: 0.3rem 0.7rem; border-radius: 15px; font-size: 0.8rem; font-weight: 500; }}
        .type-badge.blue {{ background: #DBEAFE; color: #1D4ED8; }}
        .type-badge.green {{ background: #D1FAE5; color: #047857; }}
        .type-badge.purple {{ background: #EDE9FE; color: #7C3AED; }}
        .article-title {{ font-size: 1.1rem; margin-bottom: 0.75rem; line-height: 1.4; }}
        .article-content {{ color: var(--text-light); font-size: 0.95rem; margin-bottom: 1rem; padding: 0.75rem; background: #FEF3C7; border-radius: 8px; }}
        .article-footer {{ display: flex; justify-content: space-between; align-items: center; }}
        .stats {{ color: var(--text-light); font-size: 0.85rem; }}
        .read-more {{ color: var(--accent); text-decoration: none; font-weight: 500; }}
        .read-more:hover {{ text-decoration: underline; }}
        .archive-section {{ margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); }}
        .archive-title {{ font-size: 1rem; color: var(--text-light); margin-bottom: 1rem; }}
        .archive-list {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .archive-item {{ padding: 0.5rem 1rem; background: var(--card-bg); border-radius: 20px; color: var(--text); text-decoration: none; font-size: 0.9rem; border: 1px solid var(--border); }}
        .archive-item.active {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .archive-item:hover {{ border-color: var(--accent); }}
        .footer {{ text-align: center; padding: 2rem; color: var(--text-light); font-size: 0.85rem; }}
        .home-btn {{ background: var(--accent); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; }}
        .en-text, .zh-text {{ display: none; }}
        body.zh .zh-text {{ display: block; }}
        body.en .en-text {{ display: block; }}
        @media (max-width: 600px) {{ .nav-links {{ display: none; }} .hero h1 {{ font-size: 1.8rem; }} }}
    </style>
</head>
<body class="zh">
    <nav class="navbar">
        <div class="nav-links">
            <a href="../index.html">远程岗位</a>
            <a href="../companies.html">科技公司</a>
            <a href="index.html">AI资讯</a>
            <a href="../community.html">加入社群</a>
        </div>
        <div class="nav-controls">
            <div class="lang-toggle">
                <button class="lang-btn active" onclick="setLang('zh')">中文</button>
                <button class="lang-btn" onclick="setLang('en')">EN</button>
            </div>
            <a href="../index.html" class="home-btn">首页</a>
        </div>
    </nav>

    <div class="hero">
        <h1>🤖 AI 资讯</h1>
        <p class="hero-date">{date_en(dt)}</p>
        <div class="hero-stats">
            <span class="stat-badge">👤 {len(articles)} 位建造者</span>
            <span class="stat-badge">🐦 {tweet_count} 条推文</span>
            <span class="stat-badge">🎙️ {podcast_count} 期播客</span>
            <span class="stat-badge">📝 {blog_count} 篇博客</span>
        </div>
    </div>

    <div class="container">
        <h2 class="section-title">🐦 建造者动态</h2>
        {articles_html}

        <div class="archive-section">
            <h3 class="archive-title">📁 历史存档</h3>
            <div class="archive-list">
                {archives_html}
            </div>
        </div>
    </div>

    <div class="footer">
        <p>数据来源：<a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a></p>
        <p><a href="../index.html">返回远程工作聚合网站</a></p>
    </div>

    <script>
    function setLang(lang) {{
        document.body.className = lang;
        document.querySelectorAll('.lang-btn').forEach(btn => {{
            btn.classList.toggle('active', btn.textContent.toLowerCase().startsWith(lang));
        }});
        localStorage.setItem('ai-news-lang', lang);
    }}
    document.addEventListener('DOMContentLoaded', () => {{
        const saved = localStorage.getItem('ai-news-lang') || 'zh';
        setLang(saved);
    }});
    </script>
</body>
</html>'''
    return html

def get_existing_dates():
    """扫描已存在的历史存档文件"""
    existing = []
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f):
                existing.append(f.replace('.html', ''))
    return sorted(existing, reverse=True)

# ============ 主程序 ============
def main():
    # 确定日期
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    print(f'📅 生成 AI 资讯: {date_str}')
    print('📥 同步数据源...')
    sync_feeds()

    print('📖 加载数据...')
    feeds = load_feeds()

    print('✨ 生成文章...')
    articles = generate_articles(feeds)
    print(f'   生成 {len(articles)} 篇文章')

    # 获取历史存档
    archive_dates = get_existing_dates()
    if date_str not in archive_dates:
        archive_dates.insert(0, date_str)
    archive_dates = sorted(archive_dates, reverse=True)[:10]

    # 生成 HTML
    html = generate_html(date_str, articles, archive_dates)
    path = os.path.join(OUTPUT_DIR, f'{date_str}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✅ {date_str}.html ({len(articles)}篇)')

    # index.html = 最新一天
    latest = date_str
    html = generate_html(latest, articles, archive_dates)
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✅ index.html (= {latest}.html)')
    print(f'\n🎉 完成！共 {len(articles)} 篇文章')

if __name__ == '__main__':
    main()
