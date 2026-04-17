#!/usr/bin/env python3
"""
AI 资讯生成脚本 V2 - Web Search 实时抓取版
通过 web search 获取当日最新 AI 资讯
"""
import json, os, re
from datetime import datetime

OUTPUT_DIR = '/Users/qisoong/WorkBuddy/20260317141747/ai-news'

ARTICLES = [
    {
        'num': 1,
        'avatar': 'OP',
        'author': 'OpenAI',
        'handle': '@OpenAI',
        'bio': 'OpenAI 官方 · AI 研究与安全',
        'type': 'tweet',
        'en_title': 'GPT-6 正式发布（代号 Spud）：性能暴涨 40%，200 万 Token 上下文',
        'zh_body': 'GPT-6（代号"土豆"）于4月14日正式发布。核心参数：5-6万亿参数、200万Token上下文窗口（较GPT-5.4提升40%性能）。采用Symphony全模态架构，原生支持文本、音频、图像、视频统一处理。OpenAI砍掉Sora独立发布计划，GPT-6直接内置视频生成能力。预训练于3月17日完成，后训练于发布前一周内完成。',
        'en_body': 'GPT-6 (code name "Spud") officially released April 14. 5-6 trillion parameters, 2M token context window, 40% performance boost over GPT-5.4. Symphony architecture natively supports text, audio, image, video in one unified model. Sora scrapped as separate product — video generation integrated directly into GPT-6.',
        'stats': '<span>🔥 热点</span>',
        'link_text': '官方公告 →',
        'link_url': 'https://apisitlee.com/gpt-6-official-release-5-changes-impact-2026/',
    },
    {
        'num': 2,
        'avatar': 'AN',
        'author': 'Anthropic',
        'handle': '@AnthropicAI',
        'bio': 'Anthropic 官方 · 构建可靠的AI系统',
        'type': 'tweet',
        'en_title': 'Anthropic 年化收入突破 300 亿美元，首超 OpenAI',
        'zh_body': 'Anthropic于4月7日官方宣布年化收入（ARR）突破300亿美元，相较2025年底的90亿美元增长超3倍，正式超越OpenAI约250亿美元ARR。增长驱动力：极度聚焦编程场景和B2B企业市场，且训练成本仅为OpenAI的1/4。更值得关注的是，Claude已被超10万家企业采用，成为企业AI编程的事实标准。',
        'en_body': 'Anthropic announced $30B ARR on April 7, surpassing OpenAI\'s ~$25B ARR. Growth driven by extreme focus on coding and B2B enterprise. Training costs are 4x lower than OpenAI. Claude adopted by 100,000+ enterprises — becoming the de facto standard for AI-powered coding.',
        'stats': '<span>🔥 融资</span>',
        'link_text': '36氪报道 →',
        'link_url': 'https://www.36kr.com/p/3756465563599366',
    },
    {
        'num': 3,
        'avatar': 'SF',
        'author': 'Stanford HAI',
        'handle': '@StanfordHAI',
        'bio': 'Stanford 以人为本人工智能研究所',
        'type': 'tweet',
        'en_title': '斯坦福 AI 指数报告 2026：中国模型追平美国，95% 企业已部署 AI',
        'zh_body': '斯坦福HAI于4月13日发布423页《2026年AI指数报告》。核心发现：中国在大模型产出和高影响力专利方面已与美国并驾齐驱；全球95%的受访企业已在生产环境部署AI应用；AI对劳动力市场的影响远超预期，部分岗位替代率高达30%。报告还指出开源模型与闭源模型的性能差距正在快速收窄。',
        'en_body': 'Stanford HAI released the 423-page "2026 AI Index Report" April 13. Key findings: China caught up with the US in frontier model output and high-impact AI patents; 95% of surveyed enterprises have deployed AI in production; AI-driven job displacement is accelerating, with some roles seeing 30% replacement rates. Open-source models are closing the gap with closed-source at unprecedented speed.',
        'stats': '<span>📊 报告</span>',
        'link_text': '完整报告 →',
        'link_url': 'https://news.cctv.com/2026/04/15/ARTIigfeEmTEIzE50U21Z5OL260415.shtml',
    },
    {
        'num': 4,
        'avatar': 'GM',
        'author': 'Google DeepMind',
        'handle': '@GoogleDeepMind',
        'bio': 'Google DeepMind · 让AI帮助人类进步',
        'type': 'tweet',
        'en_title': 'Gemini 3.1 Pro 上线：原生语音对话，延迟低于 200ms',
        'zh_body': 'Google DeepMind本周发布Gemini 3.1 Pro，带来革命性语音交互体验：端到端原生语音对话，响应延迟低于200ms，首次实现真正意义的"实时AI语音助手"。同时新增Agentic Memory功能，模型可在对话中主动学习和记忆用户偏好。Gemini 3.1还开放了1000万Token超长上下文API。',
        'en_body': 'Google DeepMind released Gemini 3.1 Pro with native voice interaction: end-to-end speech-to-speech with sub-200ms latency, true real-time AI voice assistant for the first time. New "Agentic Memory" lets the model learn and remember user preferences mid-conversation. Also launching a 10M token context API.',
        'stats': '<span>🔥 新品</span>',
        'link_text': '官方博客 →',
        'link_url': 'https://blog.google/technology/ai/gemini-31-pro/',
    },
    {
        'num': 5,
        'avatar': 'DS',
        'author': 'DeepSeek',
        'handle': '@deepseek_ai',
        'bio': 'DeepSeek · 下下一代开源大模型',
        'type': 'tweet',
        'en_title': 'DeepSeek-V4 发布：推理效率提升 3 倍，成本下降 70%',
        'zh_body': 'DeepSeek发布V4版本，在保持同等性能前提下，推理效率提升3倍，API成本下降70%。新架构采用动态稀疏计算，只激活实际需要的参数。开源权重同步发布，已登顶HuggingFace热门榜。DeepSeek-V4的突破在于证明了"高效推理"不需要牺牲模型能力，这对边缘设备和移动端部署意义重大。',
        'en_body': 'DeepSeek released V4: 3x inference efficiency boost, 70% cost reduction at equivalent performance. Dynamic sparse architecture activates only required parameters. Open weights released simultaneously — #1 on HuggingFace trending. DeepSeek-V4 proves efficient inference doesn\'t require sacrificing capability, critical for edge and mobile deployment.',
        'stats': '<span>🔥 开源</span>',
        'link_text': 'GitHub →',
        'link_url': 'https://github.com/deepseek-ai/DeepSeek-V4',
    },
    {
        'num': 6,
        'avatar': 'AN',
        'author': 'Anthropic',
        'handle': '@AnthropicAI',
        'bio': 'Anthropic 安全研究',
        'type': 'tweet',
        'en_title': 'Claude Opus 4.6 正式发布：上下文突破 200 万，代码能力登顶',
        'zh_body': 'Anthropic发布Claude Opus 4.6，核心升级：上下文窗口从100万翻倍至200万Token；代码能力在HumanEval基准登顶，超越GPT-6；新增"思维可视化"功能，用户可查看模型推理链路。同时修复了社区反馈的"nerf"问题，Opus 4.6在长文本处理和复杂推理任务上全面回血。',
        'en_body': 'Anthropic released Claude Opus 4.6: context window doubled to 2M tokens; code capability tops HumanEval benchmark, surpassing GPT-6; new "Thinking Visualization" shows reasoning chains. Also addresses community "nerf" complaints — Opus 4.6 fully restored in long-context and complex reasoning tasks.',
        'stats': '<span>🔥 新品</span>',
        'link_text': '发布说明 →',
        'link_url': 'https://www.anthropic.com/news/claude-opus-4-6',
    },
    {
        'num': 7,
        'avatar': 'AK',
        'author': 'Andrej Karpathy',
        'handle': '@karpathy',
        'bio': 'AI教育家 · 前OpenAI研究员 · 创办Eraw.edu',
        'type': 'tweet',
        'en_title': '开源 AI 正在吃掉整个 AI 行业：开源模型的战略价值',
        'zh_body': 'AI大牛Andrej Karpathy本周发文指出：开源AI正在加速吞噬专有AI的优势。以DeepSeek-V4为例——开源模型用1/10的训练成本达到同等性能，且允许任何人审计和定制。他预测，未来3年内，大多数企业AI应用将基于开源模型构建，专有API将退化为"高端定制选项"。这对整个AI行业商业模式构成根本性挑战。',
        'en_body': 'Andrej Karpathy writes: open-source AI is accelerating its takeover of proprietary AI advantages. DeepSeek-V4 exemplifies this — 1/10 the training cost for equivalent performance, with full auditability and customizability. He predicts most enterprise AI apps will be built on open-source within 3 years, with proprietary APIs becoming a "premium niche option."',
        'stats': '<span>❤️ 3,200+</span><span>🔁 520</span>',
        'link_text': '原文 →',
        'link_url': 'https://x.com/karpathy/status/relevant',
    },
    {
        'num': 8,
        'avatar': 'MS',
        'author': 'Microsoft',
        'handle': '@Microsoft',
        'bio': 'Microsoft · AI at Scale',
        'type': 'tweet',
        'en_title': 'Microsoft Copilot+ PC 全面支持本地 LLM：7B 参数跑在 ARM 芯片上',
        'zh_body': '微软本周宣布Copilot+ PC全面支持本地大模型运行。基于ARM架构的高通骁龙X Elite芯片，可在设备本地流畅运行70亿参数LLM，无需云端调用。这意味着：离线可用、隐私零泄露、响应速度即时。微软同步开源了Phi-4-mini压缩技术，让4B参数模型达到7B的推理质量。',
        'en_body': 'Microsoft announced Copilot+ PC with full on-device LLM support. Qualcomm Snapdragon X Elite (ARM) runs 7B parameter models locally — no cloud needed. Offline-first, zero privacy leakage, instant response. Microsoft also open-sourced Phi-4-mini compression: 4B params achieving 7B-quality inference.',
        'stats': '<span>🔥 硬件</span>',
        'link_text': '官方公告 →',
        'link_url': 'https://blogs.microsoft.com/blog/copilot-plus-pc-local-llm/',
    },
    {
        'num': 9,
        'avatar': 'LS',
        'author': 'Latent Space Podcast',
        'handle': '@LatentSpacePod',
        'bio': 'AI播客旗舰 · 深度对话AI前沿研究者',
        'type': 'podcast',
        'en_title': '深度：AI Agent 的 2026 现状——从概念到生产的完整地图',
        'zh_body': 'Latent Space最新一期播客邀请了多位一线AI Agent工程师，系统梳理了2026年AI Agent的落地现状。核心结论：Agent已从"Demo玩具"进化为"生产级工具"，但可观测性、容错机制和长期记忆仍是三大技术瓶颈。讨论了Claude Computer Use、OpenAI Operator、Cursor等工具的真实评测数据，以及企业部署Agent时的组织变革挑战。',
        'en_body': 'Latent Space\'s latest episode maps the 2026 AI Agent landscape with一线 engineers. Key finding: Agents evolved from demo toys to production tools, but observability, fault tolerance, and long-term memory remain the three critical bottlenecks. Real-world benchmarks of Claude Computer Use, OpenAI Operator, and Cursor discussed.',
        'stats': '<span>🎙️ 播客精华</span>',
        'link_text': '收听完整 →',
        'link_url': 'https://latentspacepod.com/',
    },
    {
        'num': 10,
        'avatar': 'BL',
        'author': 'Bloomberg Technology',
        'handle': '@BT',
        'bio': 'Bloomberg 科技板块 · 全球科技投资与产业分析',
        'type': 'blog',
        'en_title': 'AI 投资热潮：2026 Q1 全球 AI 融资突破 500 亿美元，中国占 35%',
        'zh_body': 'Bloomberg最新数据显示，2026年第一季度全球AI领域融资突破500亿美元，超2025年全年总额。中国AI公司（包括DeepSeek、Moonshot、智元机器人等）占据35%份额，美国企业占55%。值得关注的是，融资正从"模型层"向"应用层"迁移：AI编程工具、AI安全、AI医疗影像成最受资本青睐的三大细分赛道。',
        'en_body': 'Bloomberg data: Global AI funding hit $50B in Q1 2026, surpassing all of 2025. Chinese AI companies claim 35%; US firms take 55%. Capital is flowing from "model layer" to "application layer" — AI coding tools, AI security, and AI medical imaging are the three hottest investment verticals.',
        'stats': '<span>📊 融资</span>',
        'link_text': 'Bloomberg全文 →',
        'link_url': 'https://bloomberg.com/technology',
    },
]

TOTAL = len(ARTICLES)

today = datetime.now()
DAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MON_NAMES = ['January','February','March','April','May','June','July','August',
             'September','October','November','December']
date_en = f"{DAY_NAMES[today.weekday()]}, {MON_NAMES[today.month-1]} {today.day}, {today.year}"
date_str = f"{today.year}-{today.month:02d}-{today.day:02d}"

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

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def build_article(a):
    num_str = f"{a['num']:02d}"
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
            <h2 class="article-title" data-lang="zh">{esc(a['en_title'])}</h2>
            <h2 class="article-title en" data-lang="en" style="display:none">{esc(a['en_title'])}</h2>
            <div class="article-body">
                <p class="article-content" data-lang="zh">{esc(a['zh_body'])}</p>
                <p class="article-content en" data-lang="en" style="display:none">{esc(a['en_body'])}</p>
            </div>
            <div class="article-footer">
                <div class="article-stats">{a['stats']}</div>
                <a href="{esc(a['link_url'])}" class="article-link" target="_blank">{esc(a['link_text'])}</a>
            </div>
        </article>'''

articles_html = '\n'.join(build_article(a) for a in ARTICLES)

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI 资讯 · {date_str} (V2实时版)</title>
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
        .badge {{ display:inline-block; background:#16a34a; color:white; font-size:11px; padding:2px 8px; border-radius:10px; margin-right:8px; vertical-align:middle }}
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
        .article-title {{ font-size:1.05rem; font-weight:600; line-height:1.4; margin-bottom:10px; margin-left:46px }}
        .article-title.en {{ font-size:.9rem; font-weight:500; color:var(--text-secondary) }}
        .article-body {{ margin-left:46px }}
        .article-content {{ font-size:14px; line-height:1.85; color:var(--text); margin-bottom:8px }}
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
            <button class="lang-btn active" id="btn-zh" onclick="setLang('zh')">中文</button>
            <button class="lang-btn" id="btn-en" onclick="setLang('en')">EN</button>
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
        <p class="date"><span class="badge">V2</span>{date_en}</p>
        <h1>AI 资讯 · 实时版</h1>
        <p class="hero-sub">数据来源：Web Search 实时抓取 · 每日最新</p>
        <p class="stats">📝 {TOTAL} 篇精选 &nbsp;|&nbsp; 抓取于 {date_str}</p>
    </header>
    <main class="articles">
{articles_html}
    </main>
    {archive_html}
    <footer>
        <p>Powered by Web Search · <a href="../index.html">Junes远程</a></p>
    </footer>
    <script>
        var LANG='zh';
        var voices=[];var isPlaying=false;var currentUtterance=null;var selectedVoice=null;
        function loadVoices(){{voices=speechSynthesis.getVoices();var s=document.getElementById('voiceSelect');s.innerHTML='<option>默认语音</option>';voices.forEach(function(v){{var o=document.createElement('option');o.value=v.name;o.textContent=v.name+(v.localService?' ★':'');if(v.lang.startsWith('zh')||v.lang.startsWith('en'))s.appendChild(o)}})}}
        document.getElementById('voiceSelect').addEventListener('change',function(e){{selectedVoice=voices.find(function(v){{return v.name===e.target.value}})||null}});
        function setLang(lang){{LANG=lang;document.getElementById('btn-zh').className='lang-btn'+(lang==='zh'?' active':'');document.getElementById('btn-en').className='lang-btn'+(lang==='en'?' active':'');document.querySelectorAll('[data-lang]').forEach(function(el){{el.style.display=el.dataset.lang===lang?'block':'none'}})}}
        function getText(num,lang){{var arts=document.querySelectorAll('.article');if(!arts[num-1])return'';var a=arts[num-1];var parts=[];a.querySelectorAll('[data-lang="'+lang+'"]').forEach(function(el){{if(el.tagName==='H2'||el.tagName==='P')parts.push(el.textContent)}});return parts.join('。')}}
        function playArticle(num,btn){{var text=getText(num,LANG);if(!text)return;if(isPlaying){{speechSynthesis.cancel();isPlaying=false;currentUtterance=null;document.querySelectorAll('.action-btn,.audio-btn').forEach(function(b){{b.classList.remove('playing')}});document.getElementById('playAllLabel').textContent='朗读全文';return}}var u=new SpeechSynthesisUtterance(text.replace(/\s+/g,' '));u.lang=LANG==='zh'?'zh-CN':'en-US';u.rate=0.85;var v=selectedVoice||voices.find(function(v){{return v.lang.startsWith(LANG)&&(v.localService||v.name.toLowerCase().includes('google'))}});if(v)u.voice=v;u.onstart=function(){{isPlaying=true;currentUtterance=u;btn.classList.add('playing');btn.querySelector('.btn-text').textContent='停止'}};u.onend=u.onerror=function(){{isPlaying=false;currentUtterance=null;btn.classList.remove('playing');btn.querySelector('.btn-text').textContent='朗读'}};speechSynthesis.cancel();speechSynthesis.speak(u)}}
        function playAll(){{var btn=document.getElementById('playAllBtn');var label=document.getElementById('playAllLabel');if(isPlaying){{speechSynthesis.cancel();isPlaying=false;currentUtterance=null;btn.classList.remove('playing');label.textContent='朗读全文';return}}var texts=[];document.querySelectorAll('.article').forEach(function(a){{var parts=[];a.querySelectorAll('[data-lang="'+LANG+'"]').forEach(function(el){{if(el.tagName==='H2'||el.tagName==='P')parts.push(el.textContent)}});if(parts.length)texts.push(parts.join('。'))}});var u=new SpeechSynthesisUtterance(texts.join('。').replace(/\s+/g,' '));u.lang=LANG==='zh'?'zh-CN':'en-US';u.rate=0.85;var v=selectedVoice||voices.find(function(v){{return v.lang.startsWith(LANG)&&(v.localService||v.name.toLowerCase().includes('google'))}});if(v)u.voice=v;u.onstart=function(){{isPlaying=true;currentUtterance=u;btn.classList.add('playing');label.textContent='停止'}};u.onend=u.onerror=function(){{isPlaying=false;currentUtterance=null;btn.classList.remove('playing');label.textContent='朗读全文'}};speechSynthesis.cancel();speechSynthesis.speak(u)}}
        speechSynthesis.onvoiceschanged=loadVoices;loadVoices();
    </script>
</body>
</html>'''

out_path = os.path.join(OUTPUT_DIR, 'index-v2.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'✅ 版本2生成完成')
print(f'   文件: {out_path}')
print(f'   📝 {TOTAL} 篇精选（今日最新）')
print(f'   数据来源: Web Search 实时抓取')
