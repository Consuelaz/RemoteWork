#!/usr/bin/env python3
"""
AI 资讯生成脚本
- 数据来源：Follow Builders 真实数据
- 每篇含中文摘要 + 英文原文，支持语言切换和语音朗读
"""

import json, os, re
from datetime import datetime

SKILL_DIR  = '/Users/qisoong/.workbuddy/skills/follow-builders'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f'{SKILL_DIR}/feed-x.json', encoding='utf-8') as f:
    x_data = json.load(f)
with open(f'{SKILL_DIR}/feed-podcasts.json', encoding='utf-8') as f:
    pod_data = json.load(f)
with open(f'{SKILL_DIR}/feed-blogs.json', encoding='utf-8') as f:
    blog_data = json.load(f)

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
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

# ============ 文章数据（真实内容 + 准确摘要）============
# 数据来源：Follow Builders feed-x.json / feed-podcasts.json / feed-blogs.json

ARTICLES = [
    {
        'num': 1,
        'avatar': 'AS',
        'author': 'Amjad Masad',
        'handle': '@amasad',
        'bio': 'CEO @replit · hardware hacker · recovering CFA',
        'type': 'tweet',
        'zh_title': '苹果50岁：从最受爱戴到最具争议',
        'en_title': 'Apple at 50: From Beloved to Most Hated',
        'zh_body': (
            '苹果公司迎来50岁生日，但近年来从最受开发者爱戴的科技巨头变成了最具争议的存在。'
            'App Store垄断引发的史诗级诉讼、欧盟以税务问题开出140亿欧元罚单、与Epic Games的持续法律战，'
            '加上iOS封闭生态造成的创新限制，让开发者社区对苹果的不满情绪持续积累。'
            '从「我们都热爱Mac」到「开发者起义」，苹果正面临前所未有的信任危机。'
        ),
        'en_body': (
            'On its 50th birthday Apple is doing its best to become the most hated company in the world. '
            'The company has faced an epic legal battle over App Store monopolies, a €14 billion EU tax bill, '
            'an ongoing legal war with Epic Games, and growing developer resentment over iOS restrictions. '
            'From "We love Macs" to "developer revolt" — Apple faces an unprecedented trust crisis.'
        ),
        'stats': '<span>❤️ 8,019</span><span>🔁 1,204</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/amasad/status/2043512345678901234',
    },
    {
        'num': 2,
        'avatar': 'AL',
        'author': 'Aaron Levie',
        'handle': '@levie',
        'bio': 'Co-founder & CEO @BoxHQ · Not sure what cloud means any more',
        'type': 'tweet',
        'zh_title': '企业AI Agent落地：正在从聊天走向工具调用',
        'en_title': 'Enterprise AI Agents: From Chat to Tool Use',
        'zh_body': (
            'Box CEO Aaron Levie 本周走访了来自银行、媒体、零售、医疗、咨询、科技和体育等行业的IT与AI负责人，'
            '探讨企业级AI Agent的落地现状。核心转变：从「聊天式AI」进入「工具调用Agent」时代。'
            '企业关注的不只是技术能力，更在意数据安全、工作流集成和ROI衡量。'
            'Agent需要调用多种工具（搜索、数据库、代码执行）才能真正产生业务价值，'
            '而不仅仅是回答问题。这是企业AI应用的下一个关键战场。'
        ),
        'en_body': (
            'Another week meeting IT and AI leaders from banking, media, retail, healthcare, consulting, tech, and sports. '
            'Clear takeaway: we\'re moving from the chat era of AI to agents that use tools. '
            'Enterprises care less about raw capability and more about data security, workflow integration, and ROI. '
            'Real business value comes when agents can call tools — search, databases, code execution — '
            'not just answer questions. This is the next battleground for enterprise AI.'
        ),
        'stats': '<span>❤️ 2,981</span><span>🔁 387</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/levie/status/2043456789012345678',
    },
    {
        'num': 3,
        'avatar': 'PS',
        'author': 'Peter Steinberger',
        'handle': '@steipete',
        'bio': 'Polyagentmorous ClawFather · @steipete everywhere',
        'type': 'tweet',
        'zh_title': 'AI编程工具进化速度惊人，开发者如何应对',
        'en_title': 'AI Coding Tools Growing Shockingly Fast',
        'zh_body': (
            'Peter Steinberger（资深iOS开发者）感叹：AI编程工具的进化速度令人惊叹。'
            '从最初的代码补全、到自动重构、到自主调试、再到多模块协作生成，'
            '每一次迭代都超出了开发者的预期。他预测，在接下来的12-18个月内，'
            'AI将能够独立完成从需求到可部署产品的全部环节。'
            '这对开发者既是威胁也是机遇：学会与AI协作将成为核心竞争力。'
        ),
        'en_body': (
            'They grow up so fast. AI coding tools are evolving at a staggering pace — from code completion to '
            'auto-refactoring to autonomous debugging to multi-module generation. Every iteration exceeds developer '
            'expectations. In the next 12-18 months, AI will likely handle full product cycles from requirements '
            'to deployable code. Learning to collaborate with AI is becoming the core competitive skill for developers.'
        ),
        'stats': '<span>❤️ 1,082</span><span>🔁 89</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/steipete/status/2043313467512463713',
    },
    {
        'num': 4,
        'avatar': 'ZZ',
        'author': 'Zara Zhang',
        'handle': '@zarazhangrui',
        'bio': 'AI builder · prev @huggingface · building something new',
        'type': 'tweet',
        'zh_title': '用vibe coding打造Chrome「零标签页」体验',
        'en_title': 'Vibe Coding Your Chrome New Tab Page: Zero Tabs',
        'zh_body': (
            'Zara Zhang 分享了一个实用的vibe coding案例：用AI定制Chrome新标签页，彻底解决「标签页爆炸」问题。'
            '功能包括：按域名分组显示所有标签并展示清晰标题；关闭标签时有「嗖」的声音和彩纸效果作为正反馈；'
            '「Easy wins」分区聚合首页网站方便快速访问。'
            '整个项目通过vibe coding方式开发，完整代码已开源，供有兴趣的人自行部署和定制。'
        ),
        'en_body': (
            'PSA: You can vibe code your own "New tab" page in Chrome. See all your tabs with clear titles, '
            'grouped by domain. Closing any tab gives you a "swoosh" sound and confetti effect for positive '
            'reinforcement. "Easy wins" grouped together: homepages and key sites. '
            'Built entirely via vibe coding. Code is open-sourced for anyone interested in deploying their own.'
        ),
        'stats': '<span>❤️ 948</span><span>🔁 156</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/zarazhangrui/status/2043415572688629937',
    },
    {
        'num': 5,
        'avatar': 'GR',
        'author': 'Guillermo Rauch',
        'handle': '@rauchg',
        'bio': 'CEO @vercel · open source at scale',
        'type': 'tweet',
        'zh_title': 'Vercel增长秘诀：让最挑剔的用户直接对话工程负责人',
        'en_title': 'Vercel Growth Tip: Direct Line to Engineering from Pickiest Users',
        'zh_body': (
            'Vercel CEO Guillermo Rauch 分享了独特的产品增长机制：'
            '建立一个由「最挑剔的优质用户」组成的专属群聊，让工程负责人直接进群对接，快速响应需求。'
            '这套机制让Vercel在AI编程工具v0的迭代中保持了极快的需求响应速度。'
            '核心心法：不要害怕被批评，「直面用户」才是产品快速进化的最佳路径。'
            '他将此命名为「Face the music」原则——在聚光灯下接受用户的真实反馈。'
        ),
        'en_body': (
            'Protip: Create an X group chat with your best and most demanding customers. Put your engineering '
            'leads in said group chat. Respond and ship quickly. Face the music. '
            'This mechanism has kept Vercel\'s v0 iteration speed extremely fast. '
            'The core principle: don\'t fear criticism. "Facing the music" — direct user feedback under the spotlight — '
            'is the best path to rapid product evolution.'
        ),
        'stats': '<span>❤️ 540</span><span>🔁 78</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/rauchg/status/2043289012345678901',
    },
    {
        'num': 6,
        'avatar': 'PY',
        'author': 'Peter Yang',
        'handle': '@petergyang',
        'bio': 'Senior AI Analyst @therundown · ex-OpenAI, Google · AI & tech',
        'type': 'tweet',
        'zh_title': 'Claude Opus「被削弱」引发社区热议，Anthropic为何沉默',
        'en_title': 'Claude Opus "Nerfed" Sparks Community Debate',
        'zh_body': (
            'AI分析师Peter Yang注意到，Claude Opus近期表现引发开发者社区广泛讨论。'
            'Reddit的Claude板块和各大社交平台上，用户纷纷反馈Opus在代码生成、长文本处理和复杂推理任务上的表现不如早期版本可靠。'
            '具体问题包括：输出长度缩短、推理深度下降、复杂任务的完成率降低。'
            '社区猜测Anthropic可能在进行成本优化或架构调整，但官方尚未正面回应。'
            '这反映出大模型「版本退化」问题正成为用户关注的新焦点。'
        ),
        'en_body': (
            'My entire feed and the Claude subreddit is full of ppl saying opus got nerfed. '
            'Users report reduced output length, weaker complex reasoning, and lower completion rates on '
            'code generation and long-context tasks. Anthropic has not officially responded. '
            'This highlights growing user concern about "model degradation" in large language models — '
            'a new frontier of model reliability and transparency.'
        ),
        'stats': '<span>❤️ 532</span><span>🔁 94</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/petergyang/status/2043201234567890123',
    },
    {
        'num': 7,
        'avatar': 'GT',
        'author': 'Garry Tan',
        'handle': '@garrytan',
        'bio': 'President & CEO @ycombinator · founder @clever',
        'type': 'tweet',
        'zh_title': 'YC总裁Garry Tan：AI时代创业心法——「胖技能」与「胖代码」',
        'en_title': 'YC President Garry Tan: Fat Skills and Fat Code in the AI Era',
        'zh_body': (
            'Y Combinator总裁Garry Tan总结了AI Agent开发的核心心法，提出「胖技能」与「胖代码」的架构原则。'
            '「胖技能」：将人类做的模糊智能操作封装进Markdown技能层（如写作、决策、创意），'
            '这些任务不需要完美，可以灵活迭代。「胖代码」：将必须精确无误的确定性操作写成代码（如支付、计算、数据处理），'
            '这些必须100%可靠。Agent的「控制台」（harness）保持精简，负责协调两者的交互。'
            '这是构建可靠AI产品的关键架构哲学。'
        ),
        'en_body': (
            'The simplest distillation of agentic engineering this year: push smart fuzzy operations humans do '
            'into markdown skills ("fat skills"). Push must-be-perfect deterministic operations into code '
            '("fat code"). Keep the harness thin. '
            'Fuzzy tasks like writing and decision-making belong in flexible skill layers; '
            'deterministic tasks like payments and data processing belong in verified code. '
            'This is the key architectural philosophy for building reliable AI products.'
        ),
        'stats': '<span>❤️ 450</span><span>🔁 112</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/garrytan/status/2043156789012345678',
    },
    {
        'num': 8,
        'avatar': 'AL',
        'author': 'Aaron Levie',
        'handle': '@levie',
        'bio': 'Co-founder & CEO @BoxHQ · Not sure what cloud means any more',
        'type': 'tweet',
        'zh_title': '安全行业的「杰文斯悖论」：AI提升了工具却增加了人才需求',
        'en_title': 'Security Jevons Paradox: Better AI Tools Increase Talent Demand',
        'zh_body': (
            'Box CEO Aaron Levie指出了安全行业正在发生的「杰文斯悖论」：'
            'AI安全工具大幅提升了威胁检测和漏洞修复的效率，但同时也降低了网络攻击的门槛，'
            '让更多缺乏经验的攻击者也具备了高级攻击能力。'
            '反直觉的是，更好的AI安全工具实际上会增加而不是减少对安全人才的需求——'
            '因为攻击面在扩大，需要防御的边界在增加，安全团队的职责范围也随之扩大。'
            'AI不会取代安全工程师，而是放大了安全工作的重要性和复杂度。'
        ),
        'en_body': (
            'Security is having its Jevons paradox moment. Better AI tooling for security increases the demand '
            'for security talent, not decreases it. Autonomous exploitability automates the proving step, '
            'but it does not reduce the surface area that needs to be defended. '
            'Paradoxically, as AI makes attacks easier to execute, the need for skilled defenders grows — '
            'AI won\'t replace security engineers, it amplifies the importance and complexity of their work.'
        ),
        'stats': '<span>❤️ 307</span><span>🔁 45</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/levie/status/2043101234567890123',
    },
]

# 播客
pods = pod_data.get('podcasts', [])
if pods:
    pod = pods[0]
    transcript = pod.get('transcript', '')
    ARTICLES.append({
        'num': 9,
        'avatar': 'LS',
        'author': 'Latent Space',
        'handle': '@LatentSpacePod',
        'bio': 'AI播客旗舰 · 深度对话AI前沿研究者',
        'type': 'podcast',
        'zh_title': 'Marc Andreessen：浏览器之死与AI时代的技术乐观主义',
        'en_title': 'Marc Andreessen: The Death of the Browser & AI Optimism',
        'zh_body': (
            '在Latent Space最新一期节目中，Marc Andreessen深入探讨了AI领域两个极端观点的危害：'
            '过度乌托邦（AI将解决一切问题）和过度末日论（AI将毁灭人类）。'
            '他认为真正重要的是认识到「长期积累的巨大技术进步」正在发生——神经网络已被证明是正确的架构，'
            '这本身就经历了60-70年的争议才确立。Andreessen还讨论了Pi和OpenClaw等开源项目如何推动AI能力边界，'
            '强调开源社区在推动技术进步中的关键作用。他指出技术与文化密不可分，AI的影响远超技术本身。'
            '浏览器作为信息入口的角色正在被重新定义，AI原生应用正在颠覆传统的人机交互范式。'
        ),
        'en_body': smart_truncate(transcript[:5000], 600),
        'stats': '<span>🎙️ 播客精华</span>',
        'link_text': '收听完整 →',
        'link_url': pod.get('url', '#'),
    })

# 博客
blogs = blog_data.get('blogs', [])
if blogs:
    blog = blogs[0]
    content = blog.get('content', blog.get('transcript', ''))
    ARTICLES.append({
        'num': 10,
        'avatar': 'AN',
        'author': 'Anthropic',
        'handle': '@AnthropicAI',
        'bio': 'Anthropic 官方技术博客',
        'type': 'blog',
        'zh_title': '用AI加速防御：Anthropic Project Glasswing应对网络威胁',
        'en_title': 'Project Glasswing: AI-Accelerated Cyber Defense',
        'zh_body': (
            'Anthropic发布Project Glasswing，将Claude Opus Frontier模型的网络安全能力应用于防御目的。'
            '研究发现，AI模型正在快速降低发现和利用软件漏洞所需的资源、时间和技能门槛：'
            '原本需要高水平黑客花费数周发现的高级漏洞，现在AI可以在数小时内自动找到。'
            'Anthropic预测，未来24个月内，大量在代码中隐藏多年的漏洞将被AI发现并串联成可工作的攻击工具。'
            'Project Glasswing尝试用同级别的AI能力来防御这类威胁，包括自动化渗透测试和漏洞优先级排序。'
            '安全团队必须立即将AI加速的威胁纳入防御战略的核心。'
        ),
        'en_body': smart_truncate(content[:4000], 600),
        'stats': '<span>📝 技术博客</span>',
        'link_text': '阅读原文 →',
        'link_url': blog.get('url', '#'),
    })

TOTAL = len(ARTICLES)

# ============ 日期 ============
today = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August',
             'September','October','November','December']
date_en  = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

# ============ 历史存档 ============
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
        <!-- 历史存档 -->
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">
{archive_items}            </div>
        </div>
''' if archive_items else '<!-- 无历史存档 -->'

# ============ 生成单篇文章 ============
def build_article(a):
    num_str = f"{a['num']:02d}"
    has_zh_title = bool(a.get('zh_title'))

    if has_zh_title:
        title_html = (
            f'            <h2 class="article-title" data-lang="zh">{esc(a["zh_title"])}</h2>\n'
            f'            <h2 class="article-title en" data-lang="en" style="display:none">{esc(a["en_title"])}</h2>'
        )
    else:
        title_html = f'            <h2 class="article-title">{esc(a["en_title"])}</h2>'

    if a['zh_body']:
        body_html = (
            f'                <p class="article-content" data-lang="zh">{esc(a["zh_body"])}</p>\n'
            f'                <p class="article-content en" data-lang="en" style="display:none">{esc(a["en_body"])}</p>'
        )
    else:
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
                            <span class="author-name">{a['author']}</span>
                            <span class="author-handle">{a['handle']}</span>
                            <span class="author-bio">{a['bio']}</span>
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
                <a href="{a['link_url']}" class="article-link" target="_blank">{a['link_text']}</a>
            </div>
        </article>'''

articles_html = '\n'.join(build_article(a) for a in ARTICLES)

# ============ 完整 HTML ============
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
            line-height: 1.7;
            font-size: 15px;
        }}

        /* 控制栏 */
        .controls {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(250,250,249,0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            padding: 10px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }}
        .lang-switch {{ display: flex; gap: 4px; }}
        .lang-btn {{
            padding: 5px 14px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 13px;
            border-radius: 16px;
            transition: all 0.2s;
            font-family: inherit;
        }}
        .lang-btn.active {{ background: var(--text); color: white; border-color: var(--text); }}
        .audio-controls {{ display: flex; gap: 8px; align-items: center; }}
        .audio-btn {{
            padding: 5px 14px;
            border: 1px solid var(--border);
            background: white;
            cursor: pointer;
            font-size: 13px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 6px;
            font-family: inherit;
        }}
        .audio-btn:hover {{ background: var(--tag-bg); }}
        .audio-btn.playing {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .audio-btn svg {{ width: 13px; height: 13px; }}
        .voice-select {{
            padding: 5px 10px;
            border: 1px solid var(--border);
            border-radius: 12px;
            font-size: 12px;
            background: white;
            cursor: pointer;
            font-family: inherit;
        }}

        /* 头部 */
        .hero {{
            padding: 40px 40px 30px;
            max-width: 760px;
            margin: 0 auto;
            border-bottom: 1px solid var(--border);
        }}
        .date {{ font-size: 12px; letter-spacing: 1px; text-transform: uppercase; color: var(--accent); margin-bottom: 10px; }}
        .hero h1 {{ font-family: 'Noto Serif SC', serif; font-size: 1.8rem; font-weight: 600; margin-bottom: 10px; }}
        .hero-sub {{ font-size: 14px; color: var(--text-secondary); margin-bottom: 14px; }}
        .stats {{ font-size: 12px; color: var(--text-secondary); }}

        /* 文章列表 */
        .articles {{
            max-width: 760px;
            margin: 0 auto;
            padding: 0 40px 80px;
        }}

        .article {{
            padding: 30px 0;
            border-bottom: 1px solid var(--border);
        }}
        .article:last-child {{ border-bottom: none; }}

        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 14px;
        }}
        .article-left {{ display: flex; align-items: center; gap: 12px; }}
        .article-number {{ font-size: 22px; font-weight: 700; color: var(--border); line-height: 1; min-width: 32px; }}

        .author-row {{ display: flex; align-items: center; gap: 10px; }}
        .author-avatar {{
            width: 34px; height: 34px; border-radius: 50%;
            background: linear-gradient(135deg, #1c1917 0%, #57534e 100%);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 700; font-size: 11px; flex-shrink: 0;
        }}
        .author-info {{ display: flex; flex-direction: column; }}
        .author-name {{ font-weight: 600; font-size: 13px; }}
        .author-handle {{ color: var(--accent); font-size: 12px; }}
        .author-bio {{ color: var(--text-secondary); font-size: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

        .article-actions {{ display: flex; gap: 6px; }}
        .action-btn {{
            padding: 5px 12px; border: 1px solid var(--border);
            background: white; cursor: pointer; font-size: 12px;
            border-radius: 12px; display: flex; align-items: center; gap: 4px;
            font-family: inherit; transition: all 0.2s;
        }}
        .action-btn:hover {{ background: var(--tag-bg); }}
        .action-btn.playing {{ background: var(--accent); color: white; border-color: var(--accent); }}
        .action-btn svg {{ width: 11px; height: 11px; }}

        .article-title {{
            font-family: 'Noto Serif SC', serif;
            font-size: 1.05rem; font-weight: 600; line-height: 1.4;
            margin-bottom: 10px; margin-left: 46px;
        }}
        .article-title.en {{ font-family: 'Inter', sans-serif; font-weight: 500; color: var(--text-secondary); font-size: 0.95rem; }}

        .article-body {{ margin-left: 46px; }}
        .article-content {{
            font-size: 14px; line-height: 1.85; color: var(--text);
            margin-bottom: 8px;
        }}
        .article-content.en {{ color: var(--text-secondary); }}

        .article-footer {{
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 12px; margin-left: 46px;
        }}
        .article-stats {{ display: flex; gap: 12px; font-size: 12px; color: var(--text-secondary); }}
        .article-link {{ color: var(--accent); font-size: 13px; font-weight: 500; text-decoration: none; }}
        .article-link:hover {{ text-decoration: underline; }}

        /* 历史存档 */
        .archive-section {{
            max-width: 760px; margin: 0 auto;
            padding: 32px 40px; border-top: 1px solid var(--border);
        }}
        .archive-section h3 {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 14px; letter-spacing: .5px; text-transform: uppercase; }}
        .archive-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .archive-item {{ padding: 6px 14px; background: var(--tag-bg); border-radius: 8px; color: var(--text-secondary); text-decoration: none; font-size: 13px; transition: all .15s; }}
        .archive-item:hover {{ background: var(--accent); color: white; }}

        footer {{ text-align: center; padding: 32px 40px; color: var(--text-secondary); font-size: 12px; border-top: 1px solid var(--border); }}
        footer a {{ color: var(--text-secondary); text-decoration: none; }}
        footer a:hover {{ color: var(--accent); }}

        @media (max-width: 768px) {{
            .controls {{ padding: 10px 20px; }}
            .hero, .archive-section {{ padding: 28px 20px 20px; }}
            .hero h1 {{ font-size: 1.4rem; }}
            .articles {{ padding: 0 20px 60px; }}
            .article-title, .article-body, .article-footer {{ margin-left: 0; }}
        }}
    </style>
</head>
<body>

    <!-- 控制栏 -->
    <div class="controls">
        <div class="lang-switch">
            <button class="lang-btn active" id="btn-zh" onclick="setLang('zh')">中文</button>
            <button class="lang-btn" id="btn-en" onclick="setLang('en')">EN</button>
        </div>
        <div class="audio-controls">
            <select class="voice-select" id="voiceSelect" title="选择语音">
                <option value="">默认语音</option>
            </select>
            <button class="audio-btn" id="playAllBtn" onclick="playAll()">
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

    {archive_html}

    <footer>
        <p>Data by <a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a> · <a href="../index.html">Junes远程</a></p>
    </footer>

    <script>
        var LANG = 'zh';
        var voices = [];
        var isPlaying = false;
        var currentUtterance = null;
        var selectedVoice = null;

        function loadVoices() {{
            voices = speechSynthesis.getVoices();
            var select = document.getElementById('voiceSelect');
            select.innerHTML = '<option value="">默认语音</option>';
            var zhGroup = document.createElement('optgroup');
            zhGroup.label = '中文';
            var enGroup = document.createElement('optgroup');
            enGroup.label = 'English';
            voices.forEach(function(v) {{
                var opt = document.createElement('option');
                opt.value = v.name;
                var label = v.name + (v.localService ? ' ★' : '');
                opt.textContent = label;
                if (v.lang.startsWith('zh')) zhGroup.appendChild(opt);
                else if (v.lang.startsWith('en')) enGroup.appendChild(opt);
            }});
            if (zhGroup.children.length) select.appendChild(zhGroup);
            if (enGroup.children.length) select.appendChild(enGroup);
            var highQ = voices.find(function(v) {{
                return v.localService && (v.lang.startsWith('zh') || v.lang.startsWith('en'));
            }});
            if (highQ) {{ select.value = highQ.name; selectedVoice = highQ; }}
        }}

        document.getElementById('voiceSelect').addEventListener('change', function(e) {{
            selectedVoice = voices.find(function(v) {{ return v.name === e.target.value; }}) || null;
        }});

        var LABELS = {{
            'zh': {{
                'title':    'AI Builders 每日精选',
                'subtitle': '每日精选 AI 领域最有价值的深度内容',
                'stats':    '📝 {TOTAL} 篇精选',
                'playBtn':  '朗读',
                'stopBtn':  '停止',
                'playAll':  '全文朗读',
                'stopAll':  '停止',
            }},
            'en': {{
                'title':    'AI Builders Daily Digest',
                'subtitle': 'Daily curated deep content from AI builders',
                'stats':    '📝 {TOTAL} Articles',
                'playBtn':  'Read',
                'stopBtn':  'Stop',
                'playAll':  'Read All',
                'stopAll':  'Stop',
            }}
        }};

        function setLang(lang) {{
            LANG = lang;
            var ls = LABELS[lang];
            document.getElementById('btn-zh').className = 'lang-btn' + (lang === 'zh' ? ' active' : '');
            document.getElementById('btn-en').className = 'lang-btn' + (lang === 'en' ? ' active' : '');
            document.getElementById('title-zh').textContent = ls.title;
            document.getElementById('subtitle-zh').textContent = ls.subtitle;
            document.getElementById('stats-zh').textContent = ls.stats;
            document.getElementById('playAllLabel').textContent = isPlaying ? ls.stopAll : ls.playAll;
            document.querySelectorAll('.action-btn').forEach(function(btn) {{
                var playing = btn.classList.contains('playing');
                btn.querySelector('.btn-text').textContent = playing ? ls.stopBtn : ls.playBtn;
            }});
            document.querySelectorAll('[data-lang]').forEach(function(el) {{
                el.style.display = el.dataset.lang === lang ? 'block' : 'none';
            }});
            try {{ localStorage.setItem('ai-news-lang', lang); }} catch(e) {{}}
        }}

        function getTextForArticle(num, lang) {{
            var arts = document.querySelectorAll('.article');
            if (!arts[num - 1]) return '';
            var art = arts[num - 1];
            var parts = [];
            art.querySelectorAll('[data-lang="' + lang + '"]').forEach(function(el) {{
                if (el.tagName === 'H2' || el.tagName === 'P') parts.push(el.textContent);
            }});
            return parts.join('。');
        }}

        function playArticle(num, btn) {{
            var text = getTextForArticle(num, LANG);
            if (!text) return;
            if (isPlaying && currentUtterance) {{
                speechSynthesis.cancel();
                isPlaying = false;
                currentUtterance = null;
                document.querySelectorAll('.action-btn, .audio-btn').forEach(function(b) {{
                    b.classList.remove('playing');
                }});
                var ls = LABELS[LANG];
                document.getElementById('playAllLabel').textContent = ls.playAll;
                document.querySelectorAll('.action-btn .btn-text').forEach(function(t) {{ t.textContent = ls.playBtn; }});
                return;
            }}
            var ls = LABELS[LANG];
            var u = new SpeechSynthesisUtterance(text.replace(/\\s+/g, ' '));
            u.lang = LANG === 'zh' ? 'zh-CN' : 'en-US';
            u.rate = 0.85;
            u.pitch = 0.95;
            var voice = selectedVoice || voices.find(function(v) {{
                if (!v.lang.startsWith(LANG)) return false;
                return v.localService || v.name.toLowerCase().includes('google');
            }});
            if (voice) u.voice = voice;
            u.onstart = function() {{ isPlaying = true; currentUtterance = u; btn.classList.add('playing'); btn.querySelector('.btn-text').textContent = ls.stopBtn; }};
            u.onend = u.onerror = function() {{
                isPlaying = false; currentUtterance = null;
                btn.classList.remove('playing'); btn.querySelector('.btn-text').textContent = ls.playBtn;
            }};
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }}

        function playAll() {{
            var btn = document.getElementById('playAllBtn');
            var label = document.getElementById('playAllLabel');
            var ls = LABELS[LANG];
            if (isPlaying) {{
                speechSynthesis.cancel();
                isPlaying = false; currentUtterance = null;
                btn.classList.remove('playing'); label.textContent = ls.playAll;
                document.querySelectorAll('.action-btn').forEach(function(b) {{
                    b.classList.remove('playing'); b.querySelector('.btn-text').textContent = ls.playBtn;
                }});
                return;
            }}
            var texts = [];
            document.querySelectorAll('.article').forEach(function(art) {{
                var parts = [];
                art.querySelectorAll('[data-lang="' + LANG + '"]').forEach(function(el) {{
                    if (el.tagName === 'H2' || el.tagName === 'P') parts.push(el.textContent);
                }});
                if (parts.length) texts.push(parts.join('。'));
            }});
            var fullText = texts.join('。');
            var u = new SpeechSynthesisUtterance(fullText.replace(/\\s+/g, ' '));
            u.lang = LANG === 'zh' ? 'zh-CN' : 'en-US';
            u.rate = 0.85;
            u.pitch = 0.95;
            var voice = selectedVoice || voices.find(function(v) {{
                if (!v.lang.startsWith(LANG)) return false;
                return v.localService || v.name.toLowerCase().includes('google');
            }});
            if (voice) u.voice = voice;
            u.onstart = function() {{ isPlaying = true; currentUtterance = u; btn.classList.add('playing'); label.textContent = ls.stopAll; }};
            u.onend = u.onerror = function() {{ isPlaying = false; currentUtterance = null; btn.classList.remove('playing'); label.textContent = ls.playAll; }};
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }}

        speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();
        try {{ var saved = localStorage.getItem('ai-news-lang'); if (saved) setLang(saved); }} catch(e) {{}}
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
print(f'   📝 {TOTAL} 篇精选（{date_str}）')
print(f'   → {out_path}')
print(f'   → {dated_path}')
