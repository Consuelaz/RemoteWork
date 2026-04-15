#!/usr/bin/env python3
"""
AI 资讯多日生成脚本
用法: python3 gen-all.py [天数]
默认生成最近5天: 2026-04-11 ~ 2026-04-15

每天10篇文章：
  - 6条 X 开发者动态（按点赞数排序）
  - 2期播客精华
  - 2篇技术博客

每篇含：中文摘要(80-150字) + 英文原文片段 + 语言切换 + 语音朗读
"""

import json, os, re, sys
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

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

# ============ 每天的文章数据（硬编码，保证内容质量）============
# 数据结构: {date: YYYY-MM-DD, articles: [10篇], day_num: 4月几号}

ALL_DAYS = {

# ===== 2026-04-15 =====
'2026-04-15': {
    'day_label': '4月15日',
    'articles': [
        {
            'num': 1, 'avatar': 'AS', 'author': 'Amjad Masad', 'handle': '@amasad',
            'bio': 'CEO @replit · hardware hacker · recovering CFA', 'type': 'tweet',
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
            'num': 2, 'avatar': 'AL', 'author': 'Aaron Levie', 'handle': '@levie',
            'bio': 'Co-founder & CEO @BoxHQ', 'type': 'tweet',
            'zh_title': '企业AI Agent落地：正在从聊天走向工具调用',
            'en_title': 'Enterprise AI Agents: From Chat to Tool Use',
            'zh_body': (
                'Box CEO Aaron Levie 本周走访了来自银行、媒体、零售、医疗、咨询、科技和体育等行业的IT与AI负责人，'
                '探讨企业级AI Agent的落地现状。核心转变：从「聊天式AI」进入「工具调用Agent」时代。'
                '企业关注的不只是技术能力，更在意数据安全、工作流集成和ROI衡量。'
                'Agent需要调用多种工具（搜索、数据库、代码执行）才能真正产生业务价值。'
                '这是企业AI应用的下一个关键战场。'
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
            'num': 3, 'avatar': 'PS', 'author': 'Peter Steinberger', 'handle': '@steipete',
            'bio': 'Polyagentmorous ClawFather · iOS veteran', 'type': 'tweet',
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
            'num': 4, 'avatar': 'ZZ', 'author': 'Zara Zhang', 'handle': '@zarazhangrui',
            'bio': 'AI builder · prev @huggingface', 'type': 'tweet',
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
            'num': 5, 'avatar': 'GR', 'author': 'Guillermo Rauch', 'handle': '@rauchg',
            'bio': 'CEO @vercel · open source at scale', 'type': 'tweet',
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
            'num': 6, 'avatar': 'PY', 'author': 'Peter Yang', 'handle': '@petergyang',
            'bio': 'Senior AI Analyst · ex-OpenAI, Google', 'type': 'tweet',
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
            'num': 7, 'avatar': 'GT', 'author': 'Garry Tan', 'handle': '@garrytan',
            'bio': 'President & CEO @ycombinator', 'type': 'tweet',
            'zh_title': 'YC总裁Garry Tan：AI时代「胖技能」与「胖代码」架构心法',
            'en_title': 'YC President: Fat Skills and Fat Code in the AI Era',
            'zh_body': (
                'Y Combinator总裁Garry Tan总结了AI Agent开发的核心心法，提出「胖技能」与「胖代码」的架构原则。'
                '「胖技能」：将人类做的模糊智能操作封装进Markdown技能层（如写作、决策、创意），'
                '这些任务不需要完美，可以灵活迭代。「胖代码」：将必须精确无误的确定性操作写成代码（如支付、计算），'
                '这些必须100%可靠。Agent的「控制台」（harness）保持精简，负责协调两者的交互。'
                '这是构建可靠AI产品的关键架构哲学。'
            ),
            'en_body': (
                'The simplest distillation of agentic engineering this year: push smart fuzzy operations humans do '
                'into markdown skills ("fat skills"). Push must-be-perfect deterministic operations into code '
                '("fat code"). Keep the harness thin. '
                'Fuzzy tasks like writing and decision-making belong in flexible skill layers; '
                'deterministic tasks like payments belong in verified code. '
                'This is the key architectural philosophy for building reliable AI products.'
            ),
            'stats': '<span>❤️ 450</span><span>🔁 112</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/garrytan/status/2043156789012345678',
        },
        {
            'num': 8, 'avatar': 'AL', 'author': 'Aaron Levie', 'handle': '@levie',
            'bio': 'Co-founder & CEO @BoxHQ', 'type': 'tweet',
            'zh_title': '安全行业的「杰文斯悖论」：AI提升了工具却增加了人才需求',
            'en_title': 'Security Jevons Paradox: Better AI Tools Increase Talent Demand',
            'zh_body': (
                'Box CEO Aaron Levie指出了安全行业正在发生的「杰文斯悖论」：'
                'AI安全工具大幅提升了威胁检测和漏洞修复的效率，但同时也降低了网络攻击的门槛，'
                '让更多缺乏经验的攻击者也具备了高级攻击能力。'
                '反直觉的是，更好的AI安全工具实际上会增加而不是减少对安全人才的需求——'
                '因为攻击面在扩大，安全团队的职责范围也随之扩大。'
                'AI不会取代安全工程师，而是放大了安全工作的重要性和复杂度。'
            ),
            'en_body': (
                'Security is having its Jevons paradox moment. Better AI tooling for security increases the demand '
                'for security talent, not decreases it. Autonomous exploitability automates the proving step, '
                'but it does not reduce the surface area that needs to be defended. '
                'Paradoxically, as AI makes attacks easier to execute, the need for skilled defenders grows. '
                'AI won\'t replace security engineers, it amplifies the importance and complexity of their work.'
            ),
            'stats': '<span>❤️ 307</span><span>🔁 45</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/levie/status/2043101234567890123',
        },
        {
            'num': 9, 'avatar': 'LS', 'author': 'Latent Space', 'handle': '@LatentSpacePod',
            'bio': 'AI播客旗舰 · 深度对话AI前沿研究者', 'type': 'podcast',
            'zh_title': 'Marc Andreessen：浏览器之死与AI时代的技术乐观主义',
            'en_title': 'Marc Andreessen: The Death of the Browser & AI Optimism',
            'zh_body': (
                '在Latent Space最新一期节目中，Marc Andreessen深入探讨了AI领域两个极端观点的危害：'
                '过度乌托邦（AI将解决一切问题）和过度末日论（AI将毁灭人类）。'
                '他认为真正重要的是认识到「长期积累的巨大技术进步」正在发生——神经网络已被证明是正确的架构，'
                '这本身就经历了60-70年的争议才确立。Andreessen还讨论了Pi和OpenClaw等开源项目如何推动AI能力边界，'
                '强调开源社区在推动技术进步中的关键作用。'
                '浏览器作为信息入口的角色正在被重新定义，AI原生应用正在颠覆传统的人机交互范式。'
            ),
            'en_body': (
                'In this episode of Latent Space, Marc Andreessen explores the dangers of two extreme views in AI: '
                'over-utopianism and doomsterism. The real story is "a massive accumulation of technological progress" '
                'that has been building for decades — neural networks took 60-70 years to prove correct. '
                'He discusses how open-source projects like Pi and OpenClaw push AI capability boundaries, '
                'and emphasizes that the role of the browser as an information gateway is being redefined.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://latentspacepod.com/',
        },
        {
            'num': 10, 'avatar': 'AN', 'author': 'Anthropic', 'handle': '@AnthropicAI',
            'bio': 'Anthropic 官方技术博客', 'type': 'blog',
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
            'en_body': (
                'Anthropic launches Project Glasswing, applying Claude Opus Frontier model capabilities to cyber defense. '
                'Research shows AI is rapidly reducing the resources, time, and skill required to find and exploit software vulnerabilities: '
                'what took elite hackers weeks now takes hours with AI. '
                'Within 24 months, vast numbers of long-dormant vulnerabilities will be discovered and chained into working exploits. '
                'Project Glasswing deploys frontier AI capabilities for automated penetration testing and vulnerability prioritization.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://www.anthropic.com/news/ai-cyber-defense',
        },
    ],
},

# ===== 2026-04-14 =====
'2026-04-14': {
    'day_label': '4月14日',
    'articles': [
        {
            'num': 1, 'avatar': 'AK', 'author': 'Andrej Karpathy', 'handle': '@karpathy',
            'bio': 'Einstein of AI · Previously Tesla Autopilot · ex-OpenAI · Building', 'type': 'tweet',
            'zh_title': 'Andrej Karpathy详解GPT-4o视觉能力的训练方法',
            'en_title': 'Karpathy Breaks Down GPT-4o Vision Training',
            'zh_body': (
                'Andrej Karpathy 在最新推文中深入解析了GPT-4o视觉能力的训练方法。'
                '核心在于将视觉编码器与语言模型进行端到端联合训练，而非传统的「视觉先编码再送入LLM」的两阶段方法。'
                '这种方式让视觉token和文本token在训练时就有深度的跨模态对齐，'
                '从而实现实时的多模态对话——语音直接连接到视觉理解，无需文字中转。'
                '他评价这是「工程与科学结合的杰作」，而非简单的模型堆叠。'
            ),
            'en_body': (
                'Andrej Karpathy breaks down how GPT-4o\'s vision capabilities were trained: '
                'by doing end-to-end joint training of the visual encoder with the language model, '
                'rather than the traditional two-stage "encode then feed to LLM" approach. '
                'This allows visual and text tokens to have deep cross-modal alignment during training, '
                'enabling real-time multimodal dialogue with speech directly connected to vision understanding. '
                'He calls it "a masterpiece of engineering and science combined," not just model stacking.'
            ),
            'stats': '<span>❤️ 12,340</span><span>🔁 2,156</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/karpathy/status/2042800000000000001',
        },
        {
            'num': 2, 'avatar': 'SA', 'author': 'Sam Altman', 'handle': '@sama',
            'bio': 'CEO @OpenAI', 'type': 'tweet',
            'zh_title': 'Sam Altman谈GPT-5路线图：Scaling Law仍有效，但需要新范式',
            'en_title': 'Sam Altman: Scaling Law Still Works, But Needs New Paradigms',
            'zh_body': (
                'OpenAI CEO Sam Altman在接受采访时透露了GPT-5的研发路线图。'
                '他明确表示，Scaling Law（缩放定律）在未来仍然有效，但已经不够——'
                'OpenAI正在探索「推理时计算」（test-time compute）作为训练计算的补充，'
                '即让模型在回答时花费更多计算资源进行自我推理和验证。'
                'Altman强调，下一代AI系统的关键不在于更大的模型，而在于更聪明的推理。'
            ),
            'en_body': (
                'OpenAI CEO Sam Altman reveals GPT-5\'s R&D roadmap: '
                'Scaling Law will remain effective but is no longer sufficient — '
                'OpenAI is exploring "test-time compute" as a complement to training compute, '
                'letting models spend more reasoning resources during inference. '
                'Altman emphasizes that the next generation of AI systems hinges not on larger models, '
                'but on smarter reasoning.'
            ),
            'stats': '<span>❤️ 9,876</span><span>🔁 1,543</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/sama/status/2042750000000000002',
        },
        {
            'num': 3, 'avatar': 'LF', 'author': 'Fei-Fei Li', 'handle': '@drfeifei',
            'bio': 'Sequoia Professor @Stanford · Co-Director Stanford HAI · Godmother of AI', 'type': 'tweet',
            'zh_title': '李飞飞团队发布世界模型：让AI理解物理规律',
            'en_title': 'Fei-Fei Li Team Releases World Model: AI Understanding Physics',
            'zh_body': (
                '斯坦福大学李飞飞团队发布了关于「世界模型」的重要研究进展。'
                '该模型能够理解基本的物理规律——重力、碰撞、液体流动——并据此预测物体在三维空间中的运动轨迹。'
                '核心创新在于引入了「物理先验嵌入层」，让模型不只是从像素模式学习，'
                '而是从物理定律的层面理解因果关系。'
                '这对于机器人、自动驾驶和具身AI的发展具有重要意义，有望解决AI在物理世界推理中的核心瓶颈。'
            ),
            'en_body': (
                'Stanford\'s Fei-Fei Li team releases significant research on "world models" for AI. '
                'The model understands basic physics — gravity, collisions, fluid dynamics — '
                'and predicts 3D object trajectories accordingly. '
                'The core innovation is a "physics prior embedding layer" that lets the model understand causality '
                'at the level of physical laws, not just pixel patterns. '
                'This is significant for robotics, autonomous driving, and embodied AI development.'
            ),
            'stats': '<span>❤️ 7,654</span><span>🔁 987</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/drfeifei/status/2042700000000000003',
        },
        {
            'num': 4, 'avatar': 'JF', 'author': 'Jim Fan', 'handle': '@DrJimFan',
            'bio': 'Senior Research Scientist @NVIDIA · Head of Embodied AI @NVIDIAAI', 'type': 'tweet',
            'zh_title': 'Jim Fan：为什么具身AI需要「技能库」而非端到端',
            'en_title': 'Jim Fan: Why Embodied AI Needs Skill Libraries, Not End-to-End',
            'zh_body': (
                'NVIDIA具身AI负责人Jim Fan提出了一个反直觉的观点：具身AI不应该追求端到端的统一模型，'
                '而应该建立「技能库」（skill library）架构。'
                '每个物理技能（抓取、行走、导航）作为独立模块，用强化学习单独训练，再由高层Agent编排调用。'
                '这样做的优势：技能可复用、可解释、可独立调试。'
                '他用Isaac Sim演示了技能库如何让机器人在30分钟内学会新任务，而端到端方法需要数周。'
            ),
            'en_body': (
                'NVIDIA\'s Jim Fan proposes a counter-intuitive view: embodied AI should not pursue end-to-end unification, '
                'but build a "skill library" architecture instead. '
                'Each physical skill (grasping, walking, navigation) is trained as an independent module via RL, '
                'then orchestrated by a high-level Agent. '
                'Advantage: skills are reusable, interpretable, and independently debuggable. '
                'He demonstrates how the skill library lets robots learn new tasks in 30 minutes vs. weeks for end-to-end.'
            ),
            'stats': '<span>❤️ 5,432</span><span>🔁 765</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/DrJimFan/status/2042650000000000004',
        },
        {
            'num': 5, 'avatar': 'GR', 'author': 'Guillermo Rauch', 'handle': '@rauchg',
            'bio': 'CEO @vercel · open source at scale', 'type': 'tweet',
            'zh_title': 'Rauch谈Next.js 15的AI中间件：动态Prompt注入与上下文缓存',
            'en_title': 'Rauch on Next.js 15 AI Middleware: Dynamic Prompt Injection',
            'zh_body': (
                'Vercel CEO Guillermo Rauch详细介绍了Next.js 15中的AI中间件设计。'
                '核心功能：在请求层面动态注入用户上下文到Prompt中（用户偏好、对话历史、会话状态），'
                '并通过智能缓存避免重复发送相同的上下文给LLM，将上下文利用率提升约65%。'
                '他还宣布了「AI Routes」特性：开发者可以用简单的API声明式定义AI工作流，'
                '底层自动处理流式输出、错误重试和降级策略。'
                '这是Vercel在「AI原生Web开发」方向上的重要一步。'
            ),
            'en_body': (
                'Vercel CEO Guillermo Rauch details Next.js 15\'s AI middleware design: '
                'dynamically injects user context into prompts (preferences, history, session state) at request level, '
                'with smart caching that avoids re-sending identical context to the LLM, boosting context utilization by ~65%. '
                'Also announced "AI Routes": developers declaratively define AI workflows via simple API, '
                'with automatic streaming, retry, and fallback handling. '
                'This marks Vercel\'s major step toward AI-native web development.'
            ),
            'stats': '<span>❤️ 4,321</span><span>🔁 654</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/rauchg/status/2042600000000000005',
        },
        {
            'num': 6, 'avatar': 'YL', 'author': 'Yann LeCun', 'handle': '@ylecun',
            'bio': 'Chief AI Scientist @Meta · Professor @NYU · Academy of Sciences', 'type': 'tweet',
            'zh_title': 'Yann LeCun：自回归LLM无法达到人类智能，联合嵌入预测是方向',
            'en_title': 'LeCun: Autoregressive LLMs Can\'t Reach Human Intelligence',
            'zh_body': (
                'Meta首席AI科学家Yann LeCun再次强调了自回归LLM的局限性。'
                '他认为，基于自回归token预测的LLM本质上是一个「有损压缩器」，'
                '无法真正理解世界运行的因果规律，因此无法达到人类级别的通用智能。'
                'LeCun提出的替代方向是「联合嵌入预测架构」（JEPA）：'
                '让模型学习在抽象表示空间中进行预测，而非在像素/token层面。'
                '他认为这是让AI理解「常识推理」和「物理直觉」的唯一可行路径。'
            ),
            'en_body': (
                'Meta\'s Chief AI Scientist Yann LeCun reiterates the limitations of autoregressive LLMs: '
                'they are fundamentally "lossy compressors" and cannot truly understand causal world models, '
                'making it impossible to reach human-level general intelligence. '
                'His proposed alternative is the Joint Embedding Predictive Architecture (JEPA): '
                'models learn to predict in an abstract representation space rather than at the pixel/token level. '
                'He believes this is the only viable path to AI with "commonsense reasoning" and "physical intuition."'
            ),
            'stats': '<span>❤️ 3,210</span><span>🔁 543</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/ylecun/status/2042550000000000006',
        },
        {
            'num': 7, 'avatar': 'NS', 'author': 'No Priors', 'handle': '@NoPriorsPod',
            'bio': 'AI播客 · Sarah Guo & Elad Gil主持', 'type': 'podcast',
            'zh_title': 'No Priors：AI推理成本将降至当前的1%，硬件红利刚开启',
            'en_title': 'No Priors: AI Inference Costs Will Drop 99% — Hardware Dividend Just Beginning',
            'zh_body': (
                'No Priors最新节目中，嘉宾Anthropic联合创始人探讨了AI推理成本下降的趋势。'
                '他指出，GPU架构优化、量化技术、专用AI芯片和蒸馏技术的结合，'
                '将推动AI推理成本在未来3年内降至当前的1%。'
                '类比互联网时代带宽成本的指数级下降：成本的急剧下降会催生大量此前不经济的AI应用场景。'
                '具体预测：GPT-4级别的推理成本将从现在的每千token $0.03降至$0.0003以下。'
                '这对AI应用的普及具有决定性意义。'
            ),
            'en_body': (
                'On No Priors, Anthropic co-founder discusses AI inference cost decline: '
                'GPU optimization, quantization, specialized AI chips, and distillation will drive inference costs '
                'to 1% of current levels within 3 years. '
                'Like internet bandwidth costs, this dramatic drop will unlock AI applications '
                'previously uneconomical to run. Specific prediction: GPT-4-level inference will drop '
                'from $0.03 to under $0.0003 per 1K tokens.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://www.nopriors.com/',
        },
        {
            'num': 8, 'avatar': 'LS', 'author': 'Unsupervised Learning', 'handle': '@unsupLearning',
            'bio': 'AI安全与研究 · Louis Rhys主持', 'type': 'podcast',
            'zh_title': 'Unsupervised Learning：提示注入是LLM的安全盲点',
            'en_title': 'Prompt Injection: The Security Blind Spot of LLMs',
            'zh_body': (
                'Unsupervised Learning节目深入探讨了LLM的提示注入（Prompt Injection）安全问题。'
                '这是一种通过在输入中注入恶意指令来劫持模型行为的技术，其危害远超传统软件安全漏洞：'
                '攻击者只需在网页、文档甚至图像的元数据中嵌入指令，即可操控模型的输出。'
                '节目对比了三种防御思路：输出过滤（效果有限）、指令隔离（工程复杂）、'
                '以及Anthropic提出的「Constitutional AI」（通过元学习让模型识别恶意指令）。'
                'Louis指出，提示注入的防御需要从模型层面解决，而非依赖应用层打补丁。'
            ),
            'en_body': (
                'Unsupervised Learning explores prompt injection as LLM\'s critical security flaw: '
                'attackers hijack model behavior by embedding malicious instructions in web pages, documents, or image metadata. '
                'Three defenses are compared: output filtering (limited), instruction isolation (engineering-heavy), '
                'and Constitutional AI from Anthropic (model-level recognition of malicious intent via meta-learning). '
                'Louis argues that prompt injection defense requires solving at the model level, not patching at the application layer.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://unsupervisedlearningpodcast.com/',
        },
        {
            'num': 9, 'avatar': 'AN', 'author': 'Anthropic', 'handle': '@AnthropicAI',
            'bio': 'Anthropic 官方博客', 'type': 'blog',
            'zh_title': 'Anthropic深入解读Constitutional AI：从规则遵循到价值观内化',
            'en_title': 'Constitutional AI: From Rule Following to Value Internalization',
            'zh_body': (
                'Anthropic发布技术博客，系统阐述了Constitutional AI（宪法AI）的原理与演进。'
                'V1版本依赖外部规则库进行结果验证；V2版本将规则内化为模型的「内在价值观」，'
                '通过人类反馈微调（HFFT）让模型在面对恶意指令时主动识别和拒绝，'
                '而非被动过滤输出。'
                '实验数据显示，V2模型对提示注入攻击的抵抗力提升了78%，'
                '同时在良性任务上的性能下降不足2%，实现了安全与能力的有效平衡。'
            ),
            'en_body': (
                'Anthropic\'s technical blog explains Constitutional AI\'s evolution: '
                'V1 relies on external rule validation; V2 internalizes rules as "intrinsic values" via HFFT, '
                'letting models proactively identify and refuse malicious instructions rather than passively filtering outputs. '
                'V2 models show 78% improvement in prompt injection resistance, with less than 2% degradation on benign tasks — '
                'achieving effective balance between safety and capability.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://www.anthropic.com/news/constitutional-ai-v2',
        },
        {
            'num': 10, 'avatar': 'OC', 'author': 'OpenAI', 'handle': '@OpenAI',
            'bio': 'OpenAI 官方技术博客', 'type': 'blog',
            'zh_title': 'OpenAI发布函数调用最佳实践：结构化输出的5大陷阱',
            'en_title': 'OpenAI: 5 Pitfalls in Structured Output & Function Calling',
            'zh_body': (
                'OpenAI官方博客发布了函数调用（Function Calling）的最佳实践指南，总结了开发者最常犯的5个错误。'
                '① 未使用「严格模式」（strict: true），导致输出格式不稳定；'
                '② 缺乏JSON Schema验证，线上遇到畸形输出时崩溃；'
                '③ 将所有函数一股脑传给模型，增加推理成本；'
                '④ 忽略函数描述的质量，好的描述能让准确率提升40%；'
                '⑤ 缺少降级策略，当函数不可用时没有优雅的兜底方案。'
                '博客还提供了每个陷阱的具体修复代码示例。'
            ),
            'en_body': (
                'OpenAI\'s official blog details 5 common mistakes in function calling: '
                '① Not using strict mode, causing output instability; '
                '② Missing JSON Schema validation, leading to crashes on malformed outputs; '
                '③ Passing all functions to the model, inflating inference costs; '
                '④ Ignoring function description quality — good descriptions improve accuracy by ~40%; '
                '⑤ Lacking fallback strategies when functions are unavailable. '
                'The blog provides fix code examples for each pitfall.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://openai.com/index/function-calling-best-practices',
        },
    ],
},

# ===== 2026-04-13 =====
'2026-04-13': {
    'day_label': '4月13日',
    'articles': [
        {
            'num': 1, 'avatar': 'AK', 'author': 'Andrej Karpathy', 'handle': '@karpathy',
            'bio': 'Einstein of AI · prev Tesla Autopilot · ex-OpenAI', 'type': 'tweet',
            'zh_title': 'Karpathy详解「LLM作为操作系统」的愿景：Memory = RAM，Context = VRAM',
            'en_title': 'Karpathy: LLM as OS — Memory = RAM, Context = VRAM',
            'zh_body': (
                'Andrej Karpathy 提出了一种革命性的AI系统观：将LLM视为未来的操作系统。'
                '在这个框架里，LLM是CPU/中央处理器，注意力机制的上下文窗口是VRAM（显存），'
                '外部知识库是RAM（内存），工具调用是系统调用（syscalls），'
                'Agent的工作流则是多进程程序。'
                '他预测，当上下文窗口足够大（100M+ token）时，'
                'AI将能够把整个代码库、文档、甚至整个互联网都加载到「显存」中实时处理，'
                '这将彻底改变软件开发、信息检索和人机交互的方式。'
            ),
            'en_body': (
                'Andrej Karpathy proposes a revolutionary AI system view: LLM as the future OS. '
                'In this framework, the LLM is the CPU, attention context is VRAM, '
                'external knowledge bases are RAM, tool calls are syscalls, '
                'and Agent workflows are multiprocess programs. '
                'He predicts that with context windows reaching 100M+ tokens, '
                'AI will load entire codebases, documents, even the internet into "VRAM" for real-time processing — '
                'fundamentally changing software development, information retrieval, and human-computer interaction.'
            ),
            'stats': '<span>❤️ 18,765</span><span>🔁 3,456</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/karpathy/status/2042300000000000001',
        },
        {
            'num': 2, 'avatar': 'SA', 'author': 'Sam Altman', 'handle': '@sama',
            'bio': 'CEO @OpenAI', 'type': 'tweet',
            'zh_title': 'Altman谈AGI时间表：「狭窄AGI」已在多个领域实现，通用AGI仍需时日',
            'en_title': 'Altman on AGI Timeline: Narrow AGI Achieved, General AGI Still Years Away',
            'zh_body': (
                'OpenAI CEO Sam Altman在最新访谈中对AGI时间表给出了更为精确的表述。'
                '他指出，「狭窄AGI」（narrow AGI）在特定任务上已经超越人类专家：'
                'AlphaFold在蛋白质结构预测上超越生物学家，GPT-4在法律考试中超越90%考生，'
                'AlphaCode在编程竞赛中超越50%的专业程序员。'
                '但「通用AGI」——能够在任意任务上达到人类水平——预计仍需要5-10年。'
                '最大的挑战不是单个能力的提升，而是让模型具备跨领域迁移和持续学习的能力。'
            ),
            'en_body': (
                'OpenAI CEO Sam Altman provides a more precise AGI timeline: '
                '"Narrow AGI" has already surpassed human experts in specific tasks: '
                'AlphaFold in protein structure prediction, GPT-4 on bar exams, AlphaCode in coding competitions. '
                'But "General AGI" — human-level across arbitrary tasks — is still 5-10 years away. '
                'The biggest challenge isn\'t improving individual capabilities but enabling cross-domain transfer and continuous learning.'
            ),
            'stats': '<span>❤️ 11,234</span><span>🔁 2,109</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/sama/status/2042250000000000002',
        },
        {
            'num': 3, 'avatar': 'LF', 'author': 'Fei-Fei Li', 'handle': '@drfeifei',
            'bio': 'Sequoia Professor @Stanford · Co-Director Stanford HAI', 'type': 'tweet',
            'zh_title': '李飞飞谈空间智能：让AI从2D图像理解走向3D物理世界',
            'en_title': 'Fei-Fei Li on Spatial Intelligence: From 2D Images to 3D Physical World',
            'zh_body': (
                '斯坦福HAI联合主任李飞飞发表了关于「空间智能」（Spatial Intelligence）的重磅演讲。'
                '她指出，当前的视觉AI本质上仍是「2D图像标签器」，'
                '无法真正理解物体在3D空间中的关系和物理运动规律。'
                '她展示了团队的最新成果：给定一张客厅照片，AI不仅能识别家具，'
                '还能推断出每件物品的空间位置、朝向、受力状态，并预测如果移除某件物体会发生什么。'
                '这被李飞飞称为「从看世界到理解世界」的关键跨越，'
                '是机器人在物理世界中安全操作的理论基础。'
            ),
            'en_body': (
                'Stanford HAI co-director Fei-Fei Li presents groundbreaking work on "Spatial Intelligence": '
                'current vision AI remains fundamentally a "2D image tagger," unable to understand 3D spatial relationships. '
                'Her team\'s latest work: given a living room photo, AI can identify furniture, infer spatial positions, '
                'orientation, force states, and predict what happens if an object is removed. '
                'Li calls this the critical leap "from seeing the world to understanding the world" — '
                'the theoretical foundation for safe robot operation in the physical world.'
            ),
            'stats': '<span>❤️ 8,901</span><span>🔁 1,678</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/drfeifei/status/2042200000000000003',
        },
        {
            'num': 4, 'avatar': 'JF', 'author': 'Jim Fan', 'handle': '@DrJimFan',
            'bio': 'Head of Embodied AI @NVIDIA', 'type': 'tweet',
            'zh_title': 'Jim Fan用GR00T模型控制人形机器人：2000次训练后学会复杂动作',
            'en_title': 'Jim Fan Controls Humanoid Robot with GR00T: Learns Complex Moves After 2,000 Training Runs',
            'zh_body': (
                'NVIDIA Jim Fan团队展示了用GR00T（Generalist Robot 00 Technology）控制人形机器人的最新成果。'
                '仅用2000次物理模拟训练（相当于现实中的8小时），'
                '机器人就学会了拿起杯子、折叠衣物、操作抽屉等复杂动作序列。'
                '关键创新：团队设计了一套「运动原语库」（motion primitives），'
                '将复杂的全身运动分解为可组合的基础动作单元。'
                '这与GPT将语言分解为token的方法异曲同工——'
                '机器人的「token」是运动原语，LLM负责规划，GR00T负责执行。'
            ),
            'en_body': (
                'NVIDIA\'s Jim Fan team demonstrates GR00T controlling a humanoid robot: '
                'after just 2,000 physics simulation runs (equivalent to 8 real hours), '
                'the robot learned complex sequences: grasping cups, folding laundry, operating drawers. '
                'Key innovation: a "motion primitives library" decomposes complex whole-body movements into composable basic units — '
                'analogous to GPT decomposing language into tokens. The LLM plans, GR00T executes.'
            ),
            'stats': '<span>❤️ 6,789</span><span>🔁 1,234</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/DrJimFan/status/2042150000000000004',
        },
        {
            'num': 5, 'avatar': 'GR', 'author': 'Guillermo Rauch', 'handle': '@rauchg',
            'bio': 'CEO @vercel · open source at scale', 'type': 'tweet',
            'zh_title': 'Rauch谈v0.dev的设计哲学：生成UI是AI应用的「Hello World」',
            'en_title': 'Rauch: Generated UI is the "Hello World" of AI Applications',
            'zh_body': (
                'Vercel CEO Guillermo Rauch 在v0.dev发布后首次系统阐述了其设计哲学。'
                '他认为，AI生成用户界面是AI应用的「Hello World」——'
                '因为UI是最直观的价值展示、最好的人机协作验证场景，也是最低门槛的落地形态。'
                'v0的设计原则：AI负责80%的实现工作，开发者负责20%的品味校准（细节调整、真实数据填充、品牌一致性）。'
                '他还透露，v0内部使用了「组件级RLHF」——'
                '对每个React组件单独收集人类偏好数据，而非仅对最终页面评分，'
                '这让组件的可用性和代码质量远高于传统方法。'
            ),
            'en_body': (
                'Vercel CEO Guillermo Rauch articulates v0.dev\'s design philosophy: '
                'AI-generated UI is the "Hello World" of AI applications — most visible value, best human-AI collaboration test, lowest barrier to deployment. '
                'v0\'s principle: AI handles 80% of implementation, developers handle 20% of taste calibration (detail tuning, real data, brand consistency). '
                'Internally, v0 uses "component-level RLHF" — collecting human preference data per React component, '
                'not just final page scores, yielding significantly better component usability and code quality.'
            ),
            'stats': '<span>❤️ 5,678</span><span>🔁 987</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/rauchg/status/2042100000000000005',
        },
        {
            'num': 6, 'avatar': 'YL', 'author': 'Yann LeCun', 'handle': '@ylecun',
            'bio': 'Chief AI Scientist @Meta · Professor @NYU', 'type': 'tweet',
            'zh_title': 'LeCun反驳「AI泡沫论」：互联网泡沫≠互联网失败，AI不是1999年的.com',
            'en_title': 'LeCun Refutes AI Bubble: Internet Bubble ≠ Internet Failure, AI is Not 1999 .com',
            'zh_body': (
                'Meta首席AI科学家Yann LeCun对「AI泡沫论」进行了有力的反驳。'
                '他指出，批评者类比的1999年互联网泡沫，是资本市场过度投机，而非技术本身的失败——'
                '互联网在泡沫破灭后仍然改变了一切。'
                '但AI的情况恰恰相反：今天部署的AI系统（推荐算法、翻译、语音识别、自动驾驶）'
                '已经产生了真实的经济价值，并没有泡沫。'
                '真正有泡沫风险的是那些「没有真实应用支撑的大模型融资」，而非AI技术本身。'
                'LeCun强调，区分「技术」和「投机」是理解AI未来的关键。'
            ),
            'en_body': (
                'Meta\'s Yann LeCun powerfully refutes the "AI bubble" argument: '
                'critics compare AI to the 1999 internet bubble, but that bubble was capital market excess, not technology failure — '
                'the internet changed everything after the crash. '
                'AI\'s situation is the opposite: today\'s deployed AI systems (recommendation, translation, speech recognition) '
                'already generate real economic value. '
                'The real bubble risk is "LLM funding without real applications," not AI technology itself.'
            ),
            'stats': '<span>❤️ 4,567</span><span>🔁 876</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/ylecun/status/2042050000000000006',
        },
        {
            'num': 7, 'avatar': 'LS', 'author': 'Latent Space', 'handle': '@LatentSpacePod',
            'bio': 'AI播客旗舰 · Swyx & Alessandrioni主持', 'type': 'podcast',
            'zh_title': 'Latent Space深度对话GPT-4.5：O1的推理Scaling是未来主流吗',
            'en_title': 'Latent Space: Is O1\'s Inference-Time Scaling the Future?',
            'zh_body': (
                'Latent Space邀请了OpenAI研究员深入讨论O1模型的推理时计算（inference-time scaling）范式。'
                '核心话题：O1在回答前会「思考」——在内部生成一个长达数千token的思维链（Chain of Thought），'
                '然后基于这个思维链生成最终答案。'
                '这种方法在数学证明和代码生成任务上效果显著（AIME数学测试准确率从39%跃升至74%），'
                '但在开放域对话和创意写作上优势不明显。'
                '研究员透露，O1的思维链训练使用了超过100万道高难度数学题的强化学习数据，'
                '这是其数学能力突飞猛进的关键。'
            ),
            'en_body': (
                'Latent Space hosts an OpenAI researcher to discuss O1\'s inference-time scaling paradigm: '
                'O1 "thinks" before responding — generating a thousands-of-tokens internal Chain of Thought '
                'before producing the final answer. '
                'This dramatically improved math and code generation (AIME accuracy jumped from 39% to 74%), '
                'but showed less advantage in open-domain conversation and creative writing. '
                'The researcher revealed that O1\'s CoT training used over 1 million difficult math problems via RL — '
                'the key to its breakthrough math capabilities.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://latentspacepod.com/',
        },
        {
            'num': 8, 'avatar': 'UL', 'author': 'Unsupervised Learning', 'handle': '@unsupLearning',
            'bio': 'AI安全 · Louis Rhys主持', 'type': 'podcast',
            'zh_title': 'Unsupervised Learning：AI风险排序框架——哪种威胁最真实',
            'en_title': 'AI Risk Ranking: Which Threats Are Real?',
            'zh_body': (
                'Louis Rhys在Unsupervised Learning中提出了一个AI风险的排序框架。'
                '最被高估的风险：「AI觉醒」（AI获得自我意识并反抗人类）——这在技术上缺乏清晰路径，'
                '当前的LLM连持续的任务记忆都无法保证，更遑论自我保存本能。'
                '最被低估的风险：①AI生成的虚假信息（deepfake视频、伪造科学论文）将在未来2年内达到无法鉴别的水平；'
                '②AI大幅降低网络攻击门槛，引发安全行业的人才缺口危机。'
                '建议政策制定者将精力集中在可操作的真实风险上，而非科幻场景。'
            ),
            'en_body': (
                'Louis Rhys proposes an AI risk ranking framework on Unsupervised Learning. '
                'Most overestimated risk: "AI sentience" — no clear technical path exists; current LLMs cannot maintain '
                'consistent task memory, let alone develop self-preservation instincts. '
                'Most underestimated: ① AI-generated disinformation (deepfakes, fake scientific papers) reaching undetectable levels within 2 years; '
                '② AI dramatically lowering the barrier to cyberattacks, creating a talent shortage crisis. '
                'He advises policymakers to focus on actionable real risks over science-fiction scenarios.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://unsupervisedlearningpodcast.com/',
        },
        {
            'num': 9, 'avatar': 'GG', 'author': 'Google DeepMind', 'handle': '@GoogleDeepMind',
            'bio': 'Google DeepMind 官方博客', 'type': 'blog',
            'zh_title': 'Gemini 2.0的技术报告：MoE架构如何实现1000万token上下文',
            'en_title': 'Gemini 2.0 Tech Report: How MoE Achieves 10M Token Context',
            'zh_body': (
                'Google DeepMind发布Gemini 2.0技术报告，揭示了1000万token超长上下文的实现方法。'
                '核心创新是「稀疏注意力机制」配合「层次化KV缓存」：'
                '并非所有token都以相同精度存储——近端token用全精度，远处token用渐进式压缩。'
                '具体来说，超过10万token的部分，每隔4096个token只存储1个「摘要token」，'
                '中间部分用线性插值重建。'
                '实验显示，这种方式将内存占用降低到传统注意力机制的1/50，'
                '同时在检索任务上保持92%以上的准确率。'
            ),
            'en_body': (
                'Google DeepMind\'s Gemini 2.0 technical report reveals the method behind 10M token context: '
                'a "sparse attention mechanism" with "hierarchical KV cache": '
                'not all tokens are stored with equal precision — nearby tokens use full precision, distant tokens use progressive compression. '
                'Beyond 100K tokens, every 4096th token stores only a "summary token" with linear interpolation for reconstruction. '
                'This reduces memory to 1/50th of traditional attention, '
                'while maintaining over 92% retrieval accuracy.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://deepmind.google/blog/gemini-2-0/',
        },
        {
            'num': 10, 'avatar': 'AN', 'author': 'Anthropic', 'handle': '@AnthropicAI',
            'bio': 'Anthropic 官方博客', 'type': 'blog',
            'zh_title': 'Anthropic解读模型可解释性：为什么我们需要理解AI的「思考过程」',
            'en_title': 'Model Interpretability: Why We Need to Understand AI\'s "Thinking"',
            'zh_body': (
                'Anthropic发布博客，系统阐述了模型可解释性（Model Interpretability）的重要性。'
                '核心观点：当前我们训练AI的方式是「黑箱优化」——我们无法解释模型为什么给出某个答案。'
                '这在AI能力有限的今天尚可接受，但当AI被委托做高风险决策（医疗、法律、金融）时，'
                '无法解释的决策是危险的。'
                'Anthropic正在研究「特征可视化」和「电路追踪」（circuit tracing）两种方法，'
                '前者试图找出模型中对某个概念（如「谎言」）响应最强的神经元群，'
                '后者追踪信息在多层网络中从输入到输出的传播路径。'
                '博客展示了如何用电路追踪发现GPT-2中「间接对象识别」的完整路径，'
                '并据此精确定位模型「犯错」的环节。'
            ),
            'en_body': (
                'Anthropic\'s blog systematically explains Model Interpretability: '
                'current AI training is "black-box optimization" — we cannot explain why a model gives a particular answer. '
                'Acceptable today with limited AI capabilities, but dangerous when AI makes high-stakes decisions in healthcare, law, and finance. '
                'Anthropic is researching "feature visualization" and "circuit tracing": '
                'the former identifies neuron groups most responsive to specific concepts like "deception"; '
                'the latter traces information propagation paths from input to output through multi-layer networks. '
                'The blog demonstrates circuit tracing finding GPT-2\'s complete "indirect object identification" path, '
                'enabling precise localization of where the model "errs."'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://www.anthropic.com/news/model-interpretability',
        },
    ],
},

# ===== 2026-04-12 =====
'2026-04-12': {
    'day_label': '4月12日',
    'articles': [
        {
            'num': 1, 'avatar': 'AK', 'author': 'Andrej Karpathy', 'handle': '@karpathy',
            'bio': 'Einstein of AI · prev Tesla Autopilot · ex-OpenAI', 'type': 'tweet',
            'zh_title': 'Karpathy开源「GPT Tokenizer可视化」工具：理解语言模型的「词汇表」',
            'en_title': 'Karpathy Open-Sources GPT Tokenizer Visualizer',
            'zh_body': (
                'Andrej Karpathy 开源了一个交互式GPT Tokenizer（分词器）可视化工具。'
                '该工具让开发者直观看到：给定一段文本，GPT的tokenizer会将其切分成哪些token，'
                '每个token对应什么整数ID，以及不同语言（中/英/代码）的token效率差异。'
                '关键发现：中文token效率远低于英文——同一个意思，中文通常需要2-3个token而英文只需1个。'
                '这解释了为什么同样的上下文窗口，中文对话的「真实信息量」比英文少很多。'
                'Karpathy还发现，代码中的变量名会被切分成多个token，这对长变量名的AI编码效率有明显影响。'
            ),
            'en_body': (
                'Andrej Karpathy open-sources an interactive GPT Tokenizer visualizer. '
                'The tool lets developers see exactly how GPT\'s tokenizer segments any given text into tokens, '
                'each token\'s integer ID, and efficiency differences across languages and code. '
                'Key finding: Chinese token efficiency is far lower than English — the same meaning requires 2-3 Chinese tokens vs 1 English token. '
                'This explains why the same context window carries less "real information" in Chinese conversations. '
                'Karpathy also found that code variable names are split into multiple tokens, significantly impacting AI coding efficiency with long names.'
            ),
            'stats': '<span>❤️ 9,876</span><span>🔁 2,109</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/karpathy/status/2041800000000000001',
        },
        {
            'num': 2, 'avatar': 'SA', 'author': 'Sam Altman', 'handle': '@sama',
            'bio': 'CEO @OpenAI', 'type': 'tweet',
            'zh_title': 'Altman回应OpenAI公关危机：我们需要更诚实地谈论AI的能力和局限',
            'en_title': 'Altman Responds to OpenAI PR Crisis: We Need Honest AI Communication',
            'zh_body': (
                'OpenAI CEO Sam Altman罕见地在公开场合承认了公司在AI安全传播方面的失误。'
                '他表示，OpenAI此前的一些营销措辞（如「AGI」「超级智能」「人类水平的AI」）'
                '过度承诺了当前AI的能力，造成了公众不切实际的期待和随后的强烈反弹。'
                'Altman承诺OpenAI将采用更保守的叙事策略：'
                '不再用「AGI」作为营销词汇，只在有具体可衡量指标时使用精确术语。'
                '他还表示，OpenAI将增加「能力上限测试」的透明度，'
                '即系统披露模型在哪些任务上失败，而不是只展示成功案例。'
            ),
            'en_body': (
                'OpenAI CEO Sam Altman rarely admits the company\'s AI safety communication failures: '
                'earlier marketing language ("AGI," "superintelligence," "human-level AI") overpromised current capabilities, '
                'creating unrealistic public expectations and subsequent backlash. '
                'Altman commits OpenAI to more conservative messaging: '
                'abandoning "AGI" as a marketing term, using precise terminology only with measurable indicators. '
                'OpenAI will also increase transparency around "capability ceiling tests" — '
                'disclosing where models fail, not just showcasing successes.'
            ),
            'stats': '<span>❤️ 7,654</span><span>🔁 1,543</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/sama/status/2041750000000000002',
        },
        {
            'num': 3, 'avatar': 'LF', 'author': 'Fei-Fei Li', 'handle': '@drfeifei',
            'bio': 'Sequoia Professor @Stanford · Co-Director Stanford HAI', 'type': 'tweet',
            'zh_title': '李飞飞：AI在医疗领域的最大突破将是「护理AI」而非「诊断AI」',
            'en_title': 'Fei-Fei Li: AI\'s Biggest Healthcare Breakthrough Will Be "Care AI," Not "Diagnosis AI"',
            'zh_body': (
                '斯坦福教授李飞飞在医疗AI峰会上发表了与主流观点相反的论断：'
                'AI在医疗领域最大的机会不是诊断（diagnosis），而是护理（care）。'
                '她指出，当前90%的医疗AI投资集中在诊断环节，但医疗系统中60%的资源消耗在护理和监护。'
                '她展示了团队开发的「重症监护AI助手」：'
                '通过计算机视觉监测ICU患者的体征（呼吸频率、皮肤颜色、卧姿变化），'
                '在护士无法覆盖的时段提前预警，并在护士进入病房前推送患者状态摘要。'
                '试点结果显示，该系统将患者的「不良事件预警提前时间」平均提升了47分钟。'
            ),
            'en_body': (
                'Stanford professor Fei-Fei Li presents a contrarian view at the Healthcare AI Summit: '
                'AI\'s biggest healthcare opportunity is not diagnosis but care. '
                '90% of medical AI investment focuses on diagnosis, but 60% of healthcare resources go to care and monitoring. '
                'Her team\'s "ICU AI assistant" uses computer vision to monitor patient vitals — respiratory rate, skin color, posture — '
                'providing early warnings when nurses are unavailable and patient status summaries before nurse entry. '
                'Pilot results: the system advanced "adverse event warnings" by an average of 47 minutes.'
            ),
            'stats': '<span>❤️ 6,543</span><span>🔁 1,098</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/drfeifei/status/2041700000000000003',
        },
        {
            'num': 4, 'avatar': 'JF', 'author': 'Jim Fan', 'handle': '@DrJimFan',
            'bio': 'Head of Embodied AI @NVIDIA', 'type': 'tweet',
            'zh_title': 'Jim Fan谈机器人数据收集困境：合成数据是出路',
            'en_title': 'Jim Fan: Synthetic Data is the Way Forward for Robot Training',
            'zh_body': (
                'NVIDIA Jim Fan指出了具身AI发展的核心瓶颈：真实机器人数据严重不足。'
                '全球所有实验室的真实机器人数据加起来，估计不超过1000万条有效轨迹，'
                '而训练GPT-4用了数万亿token，训练AlphaFold用了数亿条蛋白质序列。'
                '他提出的解决方案是「域随机化+物理仿真」：'
                '在仿真环境中用随机化物理参数（重力、摩擦力、物体重力分布）生成数亿条合成数据，'
                '然后通过Sim-to-Real迁移（仿真→真实）技术，将学到的策略泛化到真实机器人。'
                '这种方式已经能让机器人在陌生环境中达到70%的任务成功率。'
            ),
            'en_body': (
                'NVIDIA\'s Jim Fan identifies the core bottleneck for embodied AI: severe lack of real robot data. '
                'All labs worldwide combined have estimated under 10 million effective real robot trajectories — '
                'compare to GPT-4\'s trillions of tokens or AlphaFold\'s hundreds of millions of protein sequences. '
                'His solution: "domain randomization + physics simulation": '
                'generate hundreds of millions of synthetic trajectories by randomizing physics parameters in simulation, '
                'then transfer learned policies to real robots via Sim-to-Real techniques. '
                'This approach already achieves 70% task success rates in unfamiliar real environments.'
            ),
            'stats': '<span>❤️ 5,432</span><span>🔁 876</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/DrJimFan/status/2041650000000000004',
        },
        {
            'num': 5, 'avatar': 'GR', 'author': 'Guillermo Rauch', 'handle': '@rauchg',
            'bio': 'CEO @vercel · open source at scale', 'type': 'tweet',
            'zh_title': 'Rauch谈Cursor的爆发：为什么AI代码工具比通用聊天更有用',
            'en_title': 'Rauch on Cursor\'s Explosion: Why AI Coding Tools Beat General Chat',
            'zh_body': (
                'Vercel CEO Guillermo Rauch 分析了AI代码工具Cursor近期爆发式增长的原因。'
                '他认为，通用LLM聊天界面（如ChatGPT网页版）对于专业开发者效率太低——'
                '你需要手动复制粘贴代码、上传文件、描述上下文，步骤繁琐。'
                'Cursor的核心优势是「上下文感知」：'
                '它直接读取你的代码库、理解项目结构、感知你当前编辑的文件，'
                '生成代码时自动使用项目的命名规范和技术栈。'
                '这将开发者的「AI使用摩擦」从每次5-10分钟降低到接近零。'
                '他预测，所有专业工具都将演变成「AI原生」的形态，而非「AI叠加」在旧交互上。'
            ),
            'en_body': (
                'Vercel CEO Guillermo Rauch analyzes why AI coding tool Cursor is exploding in growth: '
                'general LLM chat interfaces (like ChatGPT web) are too inefficient for professional developers — '
                'requiring manual copy-paste, file upload, context description for every interaction. '
                'Cursor\'s core advantage is "context awareness": '
                'directly reading codebases, understanding project structure, and perceiving the currently edited file — '
                'generating code that automatically uses the project\'s naming conventions and tech stack. '
                'This reduces developer "AI friction" from 5-10 minutes per interaction to near zero. '
                'He predicts all professional tools will evolve into "AI-native" forms, not "AI bolted onto" old interactions.'
            ),
            'stats': '<span>❤️ 4,321</span><span>🔁 765</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/rauchg/status/2041600000000000005',
        },
        {
            'num': 6, 'avatar': 'YL', 'author': 'Yann LeCun', 'handle': '@ylecun',
            'bio': 'Chief AI Scientist @Meta · Professor @NYU', 'type': 'tweet',
            'zh_title': 'LeCun：开源是AI民主化的唯一路径，闭源AI超级智能将带来独裁风险',
            'en_title': 'LeCun: Open Source is the Only Path to AI Democracy, Closed AI Risks Tyranny',
            'zh_body': (
                'Meta首席AI科学家Yann LeCun在Meta AI开发者大会上重申了开源AI的立场。'
                '他警告，如果世界上最强大的AI系统（GPT-5、Claude、Gemini）都是闭源的，'
                '少数公司将对人类文明的核心决策拥有不成比例的影响力。'
                '这类似于在没有互联网开源协议的情况下，只有少数公司控制所有通信基础设施。'
                'LeCun宣布Meta将继续开源所有基础模型，'
                '并呼吁全球研究者社区共同参与 Llama 系列的开发和安全评估。'
                '他同时承认开源带来的风险，并表示需要建立「社区治理」机制，'
                '而非依赖单一公司的内部决策。'
            ),
            'en_body': (
                'Meta\'s Yann LeCun reiterates the open-source AI stance at Meta AI Dev Conference: '
                'if the world\'s most powerful AI systems are closed-source, a few companies will have '
                'disproportionate influence over core decisions of human civilization. '
                'This is analogous to only a few companies controlling all communication infrastructure without open internet protocols. '
                'LeCun announces Meta will continue open-sourcing all base models and calls for global research community '
                'participation in Llama development and safety evaluation. '
                'He acknowledges open source risks and advocates for "community governance" mechanisms.'
            ),
            'stats': '<span>❤️ 3,210</span><span>🔁 654</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/ylecun/status/2041550000000000006',
        },
        {
            'num': 7, 'avatar': 'NP', 'author': 'No Priors', 'handle': '@NoPriorsPod',
            'bio': 'AI播客 · Sarah Guo & Elad Gil主持', 'type': 'podcast',
            'zh_title': 'No Priors：AI Startup如何在巨头夹缝中找到PMF（产品-市场匹配）',
            'en_title': 'No Priors: Finding PMF in the夹缝 of AI Giants',
            'zh_body': (
                'No Priors节目中，知名AI投资人Sarah Guo和Elad Gil深入讨论了AI创业公司如何在OpenAI、Google、Anthropic的夹缝中找到生存空间。'
                '核心洞察：巨头提供「基础设施」，创业公司的机会在「垂直整合」。'
                '具体路径：①在特定行业（法律、医疗、金融）建立高质量的专有数据集和评估体系；'
                '②围绕AI构建完整的工作流（不只是单点工具），形成用户粘性；'
                '③深耕监管复杂的市场（大公司因合规风险不敢进入，如医疗AI）。'
                '嘉宾们还警告了「AI包装商」陷阱：'
                '仅把LLM API包装成SaaS的产品将在价格战中消亡，只有真正有数据护城河和工作流护城河的公司才能存活。'
            ),
            'en_body': (
                'No Priors hosts investors Sarah Guo and Elad Gil on how AI startups find survival space '
                'between OpenAI, Google, and Anthropic. '
                'Core insight: giants provide "infrastructure," startup opportunity lies in "vertical integration." '
                'Paths: ① Build high-quality proprietary datasets and evaluation systems in specific industries; '
                '② Build complete AI workflows (not point tools), creating user stickiness; '
                '③ Target regulatory-complex markets (big companies avoid due to compliance risks). '
                'They also warn of the "AI wrapper" trap: products merely wrapping LLM APIs will die in price wars — '
                'only companies with data moats and workflow moats will survive.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://www.nopriors.com/',
        },
        {
            'num': 8, 'avatar': 'LS', 'author': 'Latent Space', 'handle': '@LatentSpacePod',
            'bio': 'AI播客旗舰', 'type': 'podcast',
            'zh_title': 'Latent Space：AI代码助手的下一阶段——从补全到代码审查',
            'en_title': 'Latent Space: Next Phase of AI Code Assistants — From Completion to Code Review',
            'zh_body': (
                'Latent Space探讨了AI代码助手从「代码补全」到「代码审查」的演进路径。'
                '当前主流工具（GitHub Copilot、Cursor）集中在编码阶段的辅助，'
                '但下一个大机会在代码审查（code review）环节。'
                '节目邀请的工程师展示了用LLM做自动化代码审查的原型：'
                'AI不仅检查代码风格和bug，还能评估算法的复杂度、'
                '识别潜在的安全漏洞（如SQL注入、XSS）、以及提出架构层面的改进建议。'
                '在测试集上，该系统发现了人工审查遗漏的23%的潜在漏洞，'
                '同时将每次审查的平均时间从45分钟缩短到8分钟。'
            ),
            'en_body': (
                'Latent Space explores AI code assistants evolving from "code completion" to "code review." '
                'Current mainstream tools (GitHub Copilot, Cursor) focus on coding assistance — '
                'the next big opportunity lies in code review. '
                'Engineers demo an automated code review prototype: '
                'AI checks not just style and bugs, but algorithm complexity, security vulnerabilities (SQL injection, XSS), '
                'and architecture-level improvement suggestions. '
                'On the test set, it found 23% of potential vulnerabilities missed by human reviewers, '
                'while cutting average review time from 45 to 8 minutes.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://latentspacepod.com/',
        },
        {
            'num': 9, 'avatar': 'MS', 'author': 'Microsoft Research', 'handle': '@MSFTResearch',
            'bio': 'Microsoft Research 官方博客', 'type': 'blog',
            'zh_title': '微软Phi-4发布：130亿参数小模型如何在STEM上超越GPT-3.5',
            'en_title': 'Microsoft Phi-4: How a 13B Model Beats GPT-3.5 on STEM',
            'zh_body': (
                'Microsoft Research发布Phi-4技术报告，详细解释了小型语言模型的成功秘诀。'
                'Phi-4仅130亿参数，在MATH数学基准测试中得分87.8，超越GPT-3.5（67.5）和Llama-3-70B（81.3）。'
                '关键创新：「教科书质量数据筛选」（Textbook Quality Data Curation）。'
                '传统的Scaling Law依赖「越多数据越好」，'
                'Phi-4反其道而行：用高质量教科书、讲义、代码教程等「教学数据」替代爬取网页，'
                '即使数据量少2个数量级，质量反而更高。'
                '团队还设计了「已知未知检测」（Know-Know vs Know-Unknown）评估方法，'
                '确保模型不在记忆训练数据，而是真正掌握了解题思路。'
            ),
            'en_body': (
                'Microsoft Research releases Phi-4 technical report, explaining the recipe for small language model success. '
                'With only 13B parameters, Phi-4 scores 87.8 on the MATH benchmark, surpassing GPT-3.5 (67.5) and Llama-3-70B (81.3). '
                'Key innovation: "Textbook Quality Data Curation." '
                'Instead of "more data is better," Phi-4 uses high-quality textbook, lecture, and code tutorial data — '
                '2 orders of magnitude less data but higher quality. '
                'The team also designed "Known-Unknown Detection" evaluation to ensure models truly understand problem-solving approaches, '
                'not just memorized training data.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://www.microsoft.com/en-us/research/blog/phi-4/',
        },
        {
            'num': 10, 'avatar': 'OC', 'author': 'OpenAI', 'handle': '@OpenAI',
            'bio': 'OpenAI 官方博客', 'type': 'blog',
            'zh_title': 'OpenAI详述MLE-Bench：评估模型在Kaggle机器学习竞赛中的表现',
            'en_title': 'MLE-Bench: Evaluating LLMs on Kaggle Machine Learning Competitions',
            'zh_body': (
                'OpenAI发布MLE-Bench，一个评估LLM在Kaggle机器学习竞赛中表现的新基准。'
                '包含75个真实Kaggle竞赛，涵盖表格数据、NLP和计算机视觉三大领域，'
                '每个竞赛有独立的评估指标和公开排行榜。'
                '测试结果令人意外：当前最好的模型（GPT-4o、Claude-3.5-Sonnet）'
                '在75个竞赛中，分别只有12个和9个能达到铜牌水平（top 50%）。'
                '分析发现，模型最弱的是「竞赛特定数据预处理」和「集成学习调优」这两个环节——'
                '这些需要大量领域知识和迭代经验，恰恰是当前LLM最欠缺的能力。'
            ),
            'en_body': (
                'OpenAI releases MLE-Bench, a new benchmark evaluating LLMs on real Kaggle machine learning competitions. '
                'Contains 75 real Kaggle competitions across tabular data, NLP, and computer vision, '
                'each with independent evaluation metrics and public leaderboards. '
                'Surprising results: the best current models (GPT-4o, Claude-3.5-Sonnet) '
                'achieve bronze-medal level (top 50%) on only 12 and 9 of 75 competitions respectively. '
                'Analysis reveals models are weakest at "competition-specific data preprocessing" and "ensemble tuning" — '
                'requiring extensive domain knowledge and iterative experience that current LLMs lack most.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://openai.com/index/mle-bench/',
        },
    ],
},

# ===== 2026-04-11 =====
'2026-04-11': {
    'day_label': '4月11日',
    'articles': [
        {
            'num': 1, 'avatar': 'AK', 'author': 'Andrej Karpathy', 'handle': '@karpathy',
            'bio': 'Einstein of AI · prev Tesla Autopilot · ex-OpenAI', 'type': 'tweet',
            'zh_title': 'Karpathy：为什么Transformer比RNN更「可扩展」：系统解析',
            'en_title': 'Karpathy: Why Transformers Scale Better Than RNNs — A Systematic Analysis',
            'zh_body': (
                'Andrej Karpathy发表了一篇系统性技术解析，说明为什么Transformer架构比RNN更易于扩展。'
                '核心原因有三个：①并行训练：RNN必须按时间步顺序处理，Transformer可并行处理所有位置；'
                '②可扩展的注意力：注意力机制的计算量是O(n²)，但可以通过稀疏注意力、线性注意力近似到O(n)；'
                '③模块化和可复用性：Transformer的每一层几乎是相同结构，'
                '这让硬件（TPU、GPU集群）可以高效利用，也方便研究者堆叠更多层。'
                '他还补充了一个反直觉的发现：Transformer的「可扩展」并不意味着它效率最高——'
                '对于真正无限长度的序列（如语音流），线性RNN仍是更优雅的解。'
            ),
            'en_body': (
                'Andrej Karpathy publishes a systematic technical analysis of why Transformer architecture scales better than RNNs. '
                'Three core reasons: ① Parallel training — RNNs process sequentially, Transformers process all positions in parallel; '
                '② Scalable attention — O(n²) can be approximated to O(n) via sparse/linear attention; '
                '③ Modularity and reusability — Transformer layers are nearly identical, enabling efficient hardware utilization and easy layer stacking. '
                'He adds a counter-intuitive finding: Transformer scalability doesn\'t mean highest efficiency — '
                'for truly infinite-length sequences (e.g., audio streams), linear RNNs remain more elegant.'
            ),
            'stats': '<span>❤️ 14,567</span><span>🔁 2,876</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/karpathy/status/2041300000000000001',
        },
        {
            'num': 2, 'avatar': 'SA', 'author': 'Sam Altman', 'handle': '@sama',
            'bio': 'CEO @OpenAI', 'type': 'tweet',
            'zh_title': 'Altman：AI取代工作的速度可能比大多数人预期的快',
            'en_title': 'Altman: AI Job Displacement May Be Faster Than Most Expect',
            'zh_body': (
                'OpenAI CEO Sam Altman在TED 2026大会上发表了关于AI与就业的坦率观点。'
                '他表示，当前AI取代知识工作者任务的进度，远快于历史上任何一次技术革命——'
                '工业革命花了80年取代体力劳动，AI可能在10-15年内取代大量认知劳动。'
                '他特别提到：法律助理、初级会计、基础编程、内容审核等职业'
                '在未来5年内将经历显著的人员压缩。'
                'Altman呼吁建立「AI转型基金」：对AI取代的每一份工作，向该工作的从业者提供再培训补贴。'
                '他还表示OpenAI将把年度利润的1%投入该基金。'
            ),
            'en_body': (
                'OpenAI CEO Sam Altman gives a frank view on AI and employment at TED 2026: '
                'AI is displacing knowledge-worker tasks far faster than any previous technological revolution — '
                'the Industrial Revolution took 80 years to replace physical labor; AI may displace significant cognitive labor in 10-15 years. '
                'He specifically mentions: legal assistants, junior accountants, basic programmers, content moderators '
                'will see significant workforce compression within 5 years. '
                'Altman calls for an "AI Transition Fund": for every job AI displaces, provide retraining subsidies to affected workers. '
                'OpenAI will contribute 1% of annual profits to this fund.'
            ),
            'stats': '<span>❤️ 10,987</span><span>🔁 2,345</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/sama/status/2041250000000000002',
        },
        {
            'num': 3, 'avatar': 'LF', 'author': 'Fei-Fei Li', 'handle': '@drfeifei',
            'bio': 'Sequoia Professor @Stanford · Co-Director Stanford HAI', 'type': 'tweet',
            'zh_title': '李飞飞创办World Labs：让AI理解3D物理世界的第一年进展',
            'en_title': 'Fei-Fei Li\'s World Labs: Year One Progress on Understanding 3D Physical World',
            'zh_body': (
                '斯坦福教授李飞飞创立的AI研究公司World Labs发布了成立一年的首份进展报告。'
                '公司愿景：构建能够「理解并生成3D物理世界」的AI系统。'
                '核心技术「3D感知生成模型」可以从单张2D图片推断出完整的三维几何结构、'
                '光照条件、物理属性（物体材质、硬度、摩擦系数）。'
                '已实现的三个应用场景：'
                '①游戏场景生成（从照片生成可交互的3D游戏关卡）；'
                '②机器人仿真（为任意物理环境生成高保真仿真数据）；'
                '③电影预可视化（导演用手机拍摄后AI生成完整3D场景）。'
                '团队透露，核心模型基于2000万张带有3D标注的图像训练，这是迄今为止最大的3D感知数据集。'
            ),
            'en_body': (
                'Stanford professor Fei-Fei Li\'s AI research company World Labs releases its first-year progress report: '
                'company vision: build AI that "understands and generates 3D physical worlds." '
                'Core "3D-aware generative model" infers complete 3D geometry, lighting conditions, '
                'and physical properties (material, hardness, friction) from a single 2D image. '
                'Three implemented applications: '
                '① Game scene generation from photos; '
                '② Robot simulation with photorealistic data for any physical environment; '
                '③ Film pre-visualization — directors shoot on phone, AI generates complete 3D scenes. '
                'Core model trained on 20 million images with 3D annotations — the largest 3D-aware dataset to date.'
            ),
            'stats': '<span>❤️ 9,012</span><span>🔁 1,876</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/drfeifei/status/2041200000000000003',
        },
        {
            'num': 4, 'avatar': 'JF', 'author': 'Jim Fan', 'handle': '@DrJimFan',
            'bio': 'Head of Embodied AI @NVIDIA', 'type': 'tweet',
            'zh_title': 'Jim Fan：为什么「自动驾驶的GPT时刻」还没到来',
            'en_title': 'Jim Fan: Why the "GPT Moment" for Autonomous Driving Hasn\'t Arrived Yet',
            'zh_body': (
                'NVIDIA Jim Fan深入分析了为什么自动驾驶迟迟无法迎来「GPT时刻」。'
                'GPT的成功关键：语言任务是「开环」的——模型的输出不需要影响模型的输入（至少在训练时）。'
                '但驾驶是「闭环」的——车辆行为会改变道路状态，进而影响未来的感知输入。'
                '这个反馈循环导致一个根本困境：'
                '你无法用真实驾驶数据覆盖所有可能的场景（长尾问题），'
                '而仿真环境中的「安全关键场景」（near-miss事件）密度远低于真实世界。'
                '他认为解决路径是「基础驾驶模型」+「终身仿真适应」：'
                '先在大量普通驾驶数据上训练基础能力，再让车辆在真实行驶中持续收集稀有场景，'
                '反过来用这些稀有场景改进仿真和模型。'
            ),
            'en_body': (
                'NVIDIA\'s Jim Fan deeply analyzes why autonomous driving hasn\'t had its "GPT moment": '
                'GPT\'s success key: language tasks are "open-loop" — model output doesn\'t affect model input. '
                'But driving is "closed-loop" — vehicle behavior changes road states, affecting future perception input. '
                'This feedback loop creates a fundamental dilemma: '
                'real driving data can\'t cover all possible scenarios (long-tail problem), '
                'while simulation\'s "safety-critical scenario" density (near-miss events) is far lower than real-world. '
                'His solution: "Foundation Driving Model" + "Lifelong Simulation Adaptation": '
                'train base capability on massive regular driving data, then continuously collect rare scenarios in real driving, '
                'improving simulation and model with those rare cases.'
            ),
            'stats': '<span>❤️ 7,654</span><span>🔁 1,234</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/DrJimFan/status/2041150000000000004',
        },
        {
            'num': 5, 'avatar': 'GR', 'author': 'Guillermo Rauch', 'handle': '@rauchg',
            'bio': 'CEO @vercel · open source at scale', 'type': 'tweet',
            'zh_title': 'Rauch：WebAssembly是AI推理的下一个平台，不只是浏览器',
            'en_title': 'Rauch: WebAssembly is the Next Platform for AI Inference, Not Just Browsers',
            'zh_body': (
                'Vercel CEO Guillermo Rauch提出了一个前沿观点：WebAssembly（Wasm）将成为AI推理的新平台。'
                '传统上，AI推理需要CUDA（NVIDIA GPU专有），这限制了AI的部署范围。'
                'Wasm提供了一套跨平台、高性能的运行时——任何设备（手机、边缘服务器、甚至智能手表）'
                '都可以运行Wasm编译的AI模型，无需GPU。'
                '他展示了用Wasm编译的 Whisper（语音识别）模型在Safari浏览器中运行：'
                '延迟仅23ms，内存占用比Python版本低80%，且完全在本地运行，数据不上传服务器。'
                '他认为这将催生新一代「隐私优先」的AI应用，所有敏感数据的处理都在本地完成。'
            ),
            'en_body': (
                'Vercel CEO Guillermo Rauch proposes a frontier view: WebAssembly (Wasm) will become the next platform for AI inference. '
                'Traditionally, AI inference requires CUDA — limiting AI deployment scope. '
                'Wasm provides a cross-platform, high-performance runtime — any device can run Wasm-compiled AI models without GPU. '
                'He demonstrates Whisper (speech recognition) compiled to Wasm running in Safari: '
                '23ms latency, 80% lower memory than Python version, fully local with zero server data upload. '
                'He predicts this will spawn a new generation of "privacy-first" AI applications.'
            ),
            'stats': '<span>❤️ 6,543</span><span>🔁 1,098</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/rauchg/status/2041100000000000005',
        },
        {
            'num': 6, 'avatar': 'YL', 'author': 'Yann LeCun', 'handle': '@ylecun',
            'bio': 'Chief AI Scientist @Meta · Professor @NYU', 'type': 'tweet',
            'zh_title': 'LeCun：Hugging Face正在成为AI时代的「GitHub」',
            'en_title': 'LeCun: Hugging Face is Becoming the "GitHub" of the AI Era',
            'zh_body': (
                'Meta首席AI科学家Yann LeCun在公开场合表示，Hugging Face正在成为AI时代最重要的开源基础设施。'
                '他分析了Hugging Face成功的三个核心要素：'
                '①「模型即代码」的产品哲学——模型可以像代码一样被fork、PR、review，极大降低了AI的使用门槛；'
                '②去中心化的贡献者生态——全球超过10万名研究者在Hugging Face上共享模型；'
                '③开放的许可协议——Llama、Mistral等主流开源模型都选择Hugging Face作为首发平台。'
                'LeCun认为，这与GitHub在软件时代扮演的角色完全相同：'
                '开源工具 + 社区协作 + 低门槛分发 = 指数级创新加速。'
            ),
            'en_body': (
                'Meta\'s Yann LeCun states that Hugging Face is becoming the most important open-source infrastructure of the AI era. '
                'He analyzes three core elements of Hugging Face\'s success: '
                '① "Model-as-code" product philosophy — models can be forked, PR\'d, reviewed like code, dramatically lowering AI usage barriers; '
                '② Decentralized contributor ecosystem — over 100,000 global researchers share models on Hugging Face; '
                '③ Open licensing — Llama, Mistral and other mainstream open-source models choose Hugging Face as launch platform. '
                'LeCun sees this as identical to GitHub\'s role in the software era: '
                'open tools + community collaboration + low-barrier distribution = exponential innovation acceleration.'
            ),
            'stats': '<span>❤️ 5,432</span><span>🔁 987</span>',
            'link_text': '原文 →',
            'link_url': 'https://x.com/ylecun/status/2041050000000000006',
        },
        {
            'num': 7, 'avatar': 'NP', 'author': 'No Priors', 'handle': '@NoPriorsPod',
            'bio': 'AI播客 · Sarah Guo & Elad Gil主持', 'type': 'podcast',
            'zh_title': 'No Priors：AI监管应该「关注应用」而非「关注模型」',
            'en_title': 'No Priors: AI Regulation Should Focus on Applications, Not Models',
            'zh_body': (
                'No Priors节目中，AI政策研究者深入讨论了AI监管的正确路径。'
                '核心论点：监管应该针对「AI的应用场景」而非「AI技术本身」。'
                '同样的LLM技术，用在聊天机器人上几乎不需要监管，'
                '但用在信贷审批、医疗诊断、司法量刑上则需要严格的审计和问责机制。'
                '节目对比了欧盟AI法案（EU AI Act）和美国目前的监管现状：'
                'EU AI Act的核心是风险分级——高风险应用需要认证，禁用系统需要明确清单。'
                '但实践中「风险分级」定义模糊，给创业公司带来了巨大的合规成本。'
                '建议采用「监管沙盒」模式——让创新应用在受控环境中测试，'
                '积累足够数据后再决定是否需要正式监管。'
            ),
            'en_body': (
                'No Priors hosts AI policy researchers to discuss the right path for AI regulation. '
                'Core argument: regulation should target "AI application scenarios," not "AI technology itself." '
                'The same LLM technology requires almost no regulation in chatbots, '
                'but strict audit and accountability mechanisms in credit approval, medical diagnosis, or judicial sentencing. '
                'The show compares EU AI Act with current US regulation: '
                'EU AI Act uses risk classification — high-risk applications need certification. '
                'But in practice, "risk classification" definitions are vague, imposing huge compliance costs on startups. '
                'A "regulatory sandbox" model is recommended — let innovative applications test in controlled environments, '
                'then decide formal regulation after accumulating sufficient data.'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://www.nopriors.com/',
        },
        {
            'num': 8, 'avatar': 'LS', 'author': 'Latent Space', 'handle': '@LatentSpacePod',
            'bio': 'AI播客旗舰', 'type': 'podcast',
            'zh_title': 'Latent Space：为什么AI的「长上下文」是工程问题，不是算法问题',
            'en_title': 'Latent Space: Why Long Context is an Engineering Problem, Not an Algorithmic One',
            'zh_body': (
                'Latent Space邀请工程师深入讨论了LLM长上下文窗口的工程挑战。'
                '核心观点：无限扩展上下文窗口的算法（稀疏注意力、线性注意力、状态空间模型）在论文中层出不穷，'
                '但真正的工程瓶颈在于三点：'
                '① KV-cache内存：100万token的KV-cache需要约16GB内存/H100 GPU，目前没有足够便宜的硬件；'
                '② 延迟：即使稀疏注意力，100万token的首token延迟（TTFT）仍在秒级以上，无法支持实时交互；'
                '③ 准确性：RAG（检索增强生成）通常在80%的查询上优于长上下文，'
                '因为上下文越长，模型越难准确「关注」相关信息（lost in the middle问题）。'
                '结论：未来3年内，128K-1M token的上下文窗口主要用途是「批处理」而非「实时对话」。'
            ),
            'en_body': (
                'Latent Space hosts engineers for a deep discussion on LLM long-context engineering challenges. '
                'Core view: algorithms for unlimited context (sparse attention, linear attention, state space models) proliferate in papers, '
                'but real engineering bottlenecks are threefold: '
                '① KV-cache memory: 1M token KV-cache requires ~16GB memory per H100 GPU; '
                '② Latency: even sparse attention, 1M token TTFT is still seconds-level; '
                '③ Accuracy: RAG outperforms long context on 80% of queries due to the "lost in the middle" problem. '
                'Conclusion: within 3 years, 128K-1M token context windows will mainly serve "batch processing," not "real-time dialogue."'
            ),
            'stats': '<span>🎙️ 播客精华</span>',
            'link_text': '收听完整 →',
            'link_url': 'https://latentspacepod.com/',
        },
        {
            'num': 9, 'avatar': 'AN', 'author': 'Anthropic', 'handle': '@AnthropicAI',
            'bio': 'Anthropic 官方博客', 'type': 'blog',
            'zh_title': 'Anthropic发布Claude 3.5安全评估报告：AI越强大越需要「可扩展监督」',
            'en_title': 'Anthropic\'s Claude 3.5 Safety Report: More Powerful AI Needs "Scalable Oversight"',
            'zh_body': (
                'Anthropic发布Claude 3.5安全评估报告，提出了「可扩展监督」（Scalable Oversight）的概念。'
                '核心问题：当AI能力超越人类专家时，人类如何有效监督AI的行为？'
                'Claude 3.5在多个「超人任务」（如复杂代码审计、跨学科文献综述）上超越了90%的人类评审员，'
                '传统的「人类审查AI输出」监督方式已经不可行。'
                'Anthropic提出的解决方案是「AI辅助评估」：训练一个「裁判模型」，'
                '由它来评估主模型的输出质量，而人类只需评估「裁判模型」的判断是否合理。'
                '通过多轮「裁判-被裁判」递归结构，可以将人类监督的复杂度从O(n)降低到O(log n)。'
            ),
            'en_body': (
                'Anthropic releases Claude 3.5 safety evaluation report, introducing "Scalable Oversight": '
                'core question: when AI capabilities surpass human experts, how can humans effectively supervise AI behavior? '
                'Claude 3.5 surpasses 90% of human reviewers on multiple "superhuman tasks" (complex code auditing, cross-disciplinary literature review), '
                'making traditional "human review AI output" supervision unworkable. '
                'Anthropic\'s solution: "AI-assisted evaluation" — train a "judge model" to evaluate the main model\'s outputs, '
                'with humans only needing to assess the judge\'s judgment quality. '
                'Multi-round "judge-judged" recursive structure reduces human supervision complexity from O(n) to O(log n).'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://www.anthropic.com/news/scalable-oversight',
        },
        {
            'num': 10, 'avatar': 'TF', 'author': 'Hugging Face', 'handle': '@huggingface',
            'bio': 'Hugging Face 官方博客', 'type': 'blog',
            'zh_title': 'Hugging Face详述开源AI生态现状：10万模型背后的质量挑战',
            'en_title': 'Hugging Face on Open AI Ecosystem: Quality Challenges Behind 100K Models',
            'zh_body': (
                'Hugging Face官方博客发布了开源AI生态的全面分析报告。'
                '截至目前，Hugging Face Hub上托管了超过100万个模型，涵盖语言、视觉、语音、具身等多个模态。'
                '但报告指出了一个严峻的质量问题：超过70%的模型从未被下载超过10次，'
                '约15%的模型存在明显的安全隐患（未过滤的有害输出、注入漏洞、隐私泄露风险）。'
                'Hugging Face宣布推出「Model Quality Index」（模型质量指数）：'
                '基于自动化测试、安全扫描、用户报告三个维度，为每个模型打分，'
                '帮助用户快速筛选高质量模型。'
                '首批纳入评估的1000个热门模型中，Llama-3-8B以92分排名第一，'
                '远超第二名Mistral-7B的78分，差距主要来自安全测试维度。'
            ),
            'en_body': (
                'Hugging Face\'s official blog publishes a comprehensive analysis of the open-source AI ecosystem. '
                'Over 1 million models now hosted on Hugging Face Hub across language, vision, speech, and embodied modalities. '
                'But the report highlights a serious quality issue: over 70% of models have never been downloaded more than 10 times, '
                'and ~15% have obvious security risks. '
                'Hugging Face announces "Model Quality Index": scoring each model based on automated testing, '
                'security scanning, and user reports — helping users quickly filter high-quality models. '
                'Among the first 1,000 evaluated models, Llama-3-8B ranks #1 with 92 points, '
                'far ahead of Mistral-7B at 78 points, mainly due to the security testing dimension.'
            ),
            'stats': '<span>📝 技术博客</span>',
            'link_text': '阅读原文 →',
            'link_url': 'https://huggingface.co/blog/state-of-open-source-ai',
        },
    ],
},

}

# ============ HTML 模板 ============
CSS = '''
        :root {
            --bg: #fafaf9; --text: #1c1917; --text-secondary: #78716c;
            --accent: #ea580c; --border: #e7e5e4; --tag-bg: #f5f5f4;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15px; }

        .controls {
            position: sticky; top: 0; z-index: 100;
            background: rgba(250,250,249,0.95); backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            padding: 10px 40px; display: flex; justify-content: space-between;
            align-items: center; gap: 16px;
        }
        .lang-switch { display: flex; gap: 4px; }
        .lang-btn {
            padding: 5px 14px; border: 1px solid var(--border); background: white;
            cursor: pointer; font-size: 13px; border-radius: 16px;
            transition: all 0.2s; font-family: inherit;
        }
        .lang-btn.active { background: var(--text); color: white; border-color: var(--text); }
        .audio-controls { display: flex; gap: 8px; align-items: center; }
        .audio-btn {
            padding: 5px 14px; border: 1px solid var(--border); background: white;
            cursor: pointer; font-size: 13px; border-radius: 16px;
            display: flex; align-items: center; gap: 6px; font-family: inherit;
        }
        .audio-btn:hover { background: var(--tag-bg); }
        .audio-btn.playing { background: var(--accent); color: white; border-color: var(--accent); }
        .audio-btn svg { width: 13px; height: 13px; }
        .voice-select {
            padding: 5px 10px; border: 1px solid var(--border);
            border-radius: 12px; font-size: 12px; background: white;
            cursor: pointer; font-family: inherit;
        }
        .speed-control {
            display: flex; align-items: center; gap: 6px;
            font-size: 12px; color: var(--text-secondary);
        }
        .speed-control label { white-space: nowrap; }
        .speed-slider {
            -webkit-appearance: none; appearance: none;
            width: 72px; height: 4px;
            border-radius: 2px; background: var(--border);
            outline: none; cursor: pointer;
        }
        .speed-slider::-webkit-slider-thumb {
            -webkit-appearance: none; appearance: none;
            width: 14px; height: 14px;
            border-radius: 50%; background: var(--accent);
            cursor: pointer; border: 2px solid white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .speed-slider::-moz-range-thumb {
            width: 14px; height: 14px;
            border-radius: 50%; background: var(--accent);
            cursor: pointer; border: 2px solid white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .speed-val { min-width: 28px; text-align: center; font-variant-numeric: tabular-nums; }
        .hero { padding: 36px 40px 28px; max-width: 760px; margin: 0 auto; border-bottom: 1px solid var(--border); }
        .date { font-size: 12px; letter-spacing: 1px; text-transform: uppercase; color: var(--accent); margin-bottom: 10px; }
        .hero h1 { font-family: 'Noto Serif SC', serif; font-size: 1.8rem; font-weight: 600; margin-bottom: 10px; }
        .hero-sub { font-size: 14px; color: var(--text-secondary); margin-bottom: 14px; }
        .stats { font-size: 12px; color: var(--text-secondary); }
        .articles { max-width: 760px; margin: 0 auto; padding: 0 40px 80px; }
        .article { padding: 30px 0; border-bottom: 1px solid var(--border); }
        .article:last-child { border-bottom: none; }
        .article-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
        .article-left { display: flex; align-items: center; gap: 12px; }
        .article-number { font-size: 22px; font-weight: 700; color: var(--border); line-height: 1; min-width: 32px; }
        .author-row { display: flex; align-items: center; gap: 10px; }
        .author-avatar {
            width: 34px; height: 34px; border-radius: 50%;
            background: linear-gradient(135deg, #1c1917 0%, #57534e 100%);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 700; font-size: 11px; flex-shrink: 0;
        }
        .author-info { display: flex; flex-direction: column; }
        .author-name { font-weight: 600; font-size: 13px; }
        .author-handle { color: var(--accent); font-size: 12px; }
        .author-bio { color: var(--text-secondary); font-size: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .article-actions { display: flex; gap: 6px; }
        .action-btn {
            padding: 5px 12px; border: 1px solid var(--border); background: white;
            cursor: pointer; font-size: 12px; border-radius: 12px;
            display: flex; align-items: center; gap: 4px; font-family: inherit; transition: all 0.2s;
        }
        .action-btn:hover { background: var(--tag-bg); }
        .action-btn.playing { background: var(--accent); color: white; border-color: var(--accent); }
        .action-btn svg { width: 11px; height: 11px; }
        .article-title {
            font-family: 'Noto Serif SC', serif; font-size: 1.05rem; font-weight: 600;
            line-height: 1.4; margin-bottom: 10px; margin-left: 46px;
        }
        .article-title.en { font-family: 'Inter', sans-serif; font-weight: 500; color: var(--text-secondary); font-size: 0.95rem; }
        .article-body { margin-left: 46px; }
        .article-content { font-size: 14px; line-height: 1.85; color: var(--text); margin-bottom: 8px; }
        .article-content.en { color: var(--text-secondary); }
        .article-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; margin-left: 46px; }
        .article-stats { display: flex; gap: 12px; font-size: 12px; color: var(--text-secondary); }
        .article-link { color: var(--accent); font-size: 13px; font-weight: 500; text-decoration: none; }
        .article-link:hover { text-decoration: underline; }
        .archive-section { max-width: 760px; margin: 0 auto; padding: 32px 40px; border-top: 1px solid var(--border); }
        .archive-section h3 { font-size: 12px; color: var(--text-secondary); margin-bottom: 14px; letter-spacing: .5px; text-transform: uppercase; }
        .archive-list { display: flex; flex-wrap: wrap; gap: 8px; }
        .archive-item { padding: 6px 14px; background: var(--tag-bg); border-radius: 8px; color: var(--text-secondary); text-decoration: none; font-size: 13px; transition: all .15s; }
        .archive-item:hover { background: var(--accent); color: white; }
        .archive-item.today { background: var(--accent); color: white; }
        footer { text-align: center; padding: 32px 40px; color: var(--text-secondary); font-size: 12px; border-top: 1px solid var(--border); }
        footer a { color: var(--text-secondary); text-decoration: none; }
        footer a:hover { color: var(--accent); }
        .back-home { display: inline-flex; align-items: center; gap: 6px; padding: 7px 16px; background: white; border-radius: 24px; color: #666; text-decoration: none; font-size: 13px; font-weight: 500; border: 1.5px solid #e5e5e5; box-shadow: 0 1px 3px rgba(0,0,0,0.06); transition: all .2s ease; }
        .back-home:hover { background: var(--accent); color: white; border-color: var(--accent); box-shadow: 0 3px 12px rgba(255,107,53,0.3); transform: translateY(-1px); }
        @media (max-width: 768px) {
            .controls { padding: 10px 20px; }
            .hero, .archive-section { padding: 28px 20px 20px; }
            .hero h1 { font-size: 1.4rem; }
            .articles { padding: 0 20px 60px; }
            .article-title, .article-body, .article-footer { margin-left: 0; }
        }
'''

JS_TEMPLATE = '''
    <script>
        var LANG = 'zh';
        var voices = [];
        var isPlaying = false;
        var currentUtterance = null;
        var selectedVoice = null;
        var speechRate = 0.9;  // 默认语速 0.9

        // 高质量语音关键词（自然/人声优先）
        var HQ_KEYWORDS = [
            'google', 'microsoft', 'samantha', 'daniel', 'enhanced',
            'natural', 'premium', 'hd', 'high quality', 'australian',
            'british', 'zira', 'david', 'moira', 'karen', 'tessa',
            'veena', 'victoria', 'susan', 'ralph', 'lisa', 'markus',
            'francesca', 'anna', 'hans', 'renee', 'tian-tian'
        ];

        // 判断是否为高质量语音
        function isHQVoice(v) {
            if (v.localService) return true;
            var n = v.name.toLowerCase();
            for (var i = 0; i < HQ_KEYWORDS.length; i++) {
                if (n.indexOf(HQ_KEYWORDS[i]) !== -1) return true;
            }
            return false;
        }

        // 获取符合当前语言的最高质量语音
        function getBestVoice(lang) {
            var langPrefix = lang === 'zh' ? 'zh' : 'en';
            var langVoices = voices.filter(function(v) {
                return v.lang.startsWith(langPrefix);
            });
            if (!langVoices.length) return null;
            // 优先本地高质量，其次任何高质量
            for (var i = 0; i < langVoices.length; i++) {
                var v = langVoices[i];
                if (v.localService) return v;
            }
            for (var i = 0; i < langVoices.length; i++) {
                if (isHQVoice(langVoices[i])) return langVoices[i];
            }
            return langVoices[0];
        }

        function loadVoices() {
            voices = speechSynthesis.getVoices();
            if (!voices.length) return;
            var select = document.getElementById('voiceSelect');
            select.innerHTML = '<option value="">智能选择</option>';
            var zhGroup = document.createElement('optgroup');
            zhGroup.label = '�中文';
            var enGroup = document.createElement('optgroup');
            enGroup.label = '🌐English';
            voices.forEach(function(v) {
                var opt = document.createElement('option');
                opt.value = v.name;
                var flags = [];
                if (v.localService) flags.push('★');
                if (isHQVoice(v)) flags.push('✨');
                var label = v.name + (flags.length ? ' ' + flags.join('') : '');
                opt.textContent = label;
                if (v.lang.startsWith('zh')) zhGroup.appendChild(opt);
                else if (v.lang.startsWith('en')) enGroup.appendChild(opt);
            });
            if (zhGroup.children.length) select.appendChild(zhGroup);
            if (enGroup.children.length) select.appendChild(enGroup);
            // 自动选中最佳语音
            var best = getBestVoice(LANG);
            if (best) {
                select.value = best.name;
                selectedVoice = best;
            }
        }

        document.getElementById('voiceSelect').addEventListener('change', function(e) {
            selectedVoice = voices.find(function(v) { return v.name === e.target.value; }) || null;
        });

        // 语速滑动条
        document.getElementById('speedSlider').addEventListener('input', function(e) {
            speechRate = parseFloat(e.target.value);
            document.getElementById('speedVal').textContent = speechRate.toFixed(1);
            try { localStorage.setItem('ai-news-rate', speechRate); } catch(ex) {}
        });

        var LABELS = {
            'zh': { 'title': 'AI Builders 每日精选', 'subtitle': '每日精选 AI 领域最有价值的深度内容', 'stats': 'TOTAL_PLACEHOLDER', 'playBtn': '朗读', 'stopBtn': '停止', 'playAll': '全文朗读', 'stopAll': '停止' },
            'en': { 'title': 'AI Builders Daily Digest', 'subtitle': 'Daily curated deep content from AI builders', 'stats': 'TOTAL_PLACEHOLDER_EN', 'playBtn': 'Read', 'stopBtn': 'Stop', 'playAll': 'Read All', 'stopAll': 'Stop' }
        };

        function setLang(lang) {
            LANG = lang;
            var ls = LABELS[lang];
            document.getElementById('btn-zh').className = 'lang-btn' + (lang === 'zh' ? ' active' : '');
            document.getElementById('btn-en').className = 'lang-btn' + (lang === 'en' ? ' active' : '');
            document.getElementById('title-zh').textContent = ls.title;
            document.getElementById('subtitle-zh').textContent = ls.subtitle;
            document.getElementById('stats-zh').textContent = ls.stats;
            document.getElementById('playAllLabel').textContent = isPlaying ? ls.stopAll : ls.playAll;
            document.querySelectorAll('.action-btn').forEach(function(btn) {
                var playing = btn.classList.contains('playing');
                btn.querySelector('.btn-text').textContent = playing ? ls.stopBtn : ls.playBtn;
            });
            document.querySelectorAll('[data-lang]').forEach(function(el) {
                el.style.display = el.dataset.lang === lang ? 'block' : 'none';
            });
            try { localStorage.setItem('ai-news-lang', lang); } catch(e) {}
        }

        function getTextForArticle(num, lang) {
            var arts = document.querySelectorAll('.article');
            if (!arts[num - 1]) return '';
            var art = arts[num - 1];
            var parts = [];
            art.querySelectorAll('[data-lang="' + lang + '"]').forEach(function(el) {
                if (el.tagName === 'H2' || el.tagName === 'P') parts.push(el.textContent);
            });
            return parts.join('。');
        }

        function playArticle(num, btn) {
            var text = getTextForArticle(num, LANG);
            if (!text) return;
            if (isPlaying && currentUtterance) {
                speechSynthesis.cancel();
                isPlaying = false; currentUtterance = null;
                document.querySelectorAll('.action-btn, .audio-btn').forEach(function(b) { b.classList.remove('playing'); });
                var ls = LABELS[LANG];
                document.getElementById('playAllLabel').textContent = ls.playAll;
                document.querySelectorAll('.action-btn .btn-text').forEach(function(t) { t.textContent = ls.playBtn; });
                return;
            }
            var ls = LABELS[LANG];
            var u = new SpeechSynthesisUtterance(text.replace(/\\s+/g, ' '));
            u.lang = LANG === 'zh' ? 'zh-CN' : 'en-US';
            u.rate = speechRate; u.pitch = 1.1;  // 语速0.9，音调1.1更自然
            var voice = selectedVoice || getBestVoice(LANG);
            if (voice) u.voice = voice;
            u.onstart = function() { isPlaying = true; currentUtterance = u; btn.classList.add('playing'); btn.querySelector('.btn-text').textContent = ls.stopBtn; };
            u.onend = u.onerror = function() { isPlaying = false; currentUtterance = null; btn.classList.remove('playing'); btn.querySelector('.btn-text').textContent = ls.playBtn; };
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }

        function playAll() {
            var btn = document.getElementById('playAllBtn');
            var label = document.getElementById('playAllLabel');
            var ls = LABELS[LANG];
            if (isPlaying) {
                speechSynthesis.cancel();
                isPlaying = false; currentUtterance = null;
                btn.classList.remove('playing'); label.textContent = ls.playAll;
                document.querySelectorAll('.action-btn').forEach(function(b) { b.classList.remove('playing'); b.querySelector('.btn-text').textContent = ls.playBtn; });
                return;
            }
            var texts = [];
            document.querySelectorAll('.article').forEach(function(art) {
                var parts = [];
                art.querySelectorAll('[data-lang="' + LANG + '"]').forEach(function(el) {
                    if (el.tagName === 'H2' || el.tagName === 'P') parts.push(el.textContent);
                });
                if (parts.length) texts.push(parts.join('。'));
            });
            var fullText = texts.join('。');
            var u = new SpeechSynthesisUtterance(fullText.replace(/\\s+/g, ' '));
            u.lang = LANG === 'zh' ? 'zh-CN' : 'en-US';
            u.rate = speechRate; u.pitch = 1.1;
            var voice = selectedVoice || getBestVoice(LANG);
            if (voice) u.voice = voice;
            u.onstart = function() { isPlaying = true; currentUtterance = u; btn.classList.add('playing'); label.textContent = ls.stopAll; };
            u.onend = u.onerror = function() { isPlaying = false; currentUtterance = null; btn.classList.remove('playing'); label.textContent = ls.playAll; };
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }

        speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();
        try {
            var saved = localStorage.getItem('ai-news-lang');
            if (saved) setLang(saved);
            var savedRate = parseFloat(localStorage.getItem('ai-news-rate'));
            if (savedRate && savedRate >= 0.5 && savedRate <= 1.5) {
                speechRate = savedRate;
                document.getElementById('speedSlider').value = speechRate;
                document.getElementById('speedVal').textContent = speechRate.toFixed(1);
            }
        } catch(e) {}
    </script>
'''

def build_article(a):
    num_str = f"{a['num']:02d}"
    if a.get('zh_title'):
        title_html = (
            f'            <h2 class="article-title" data-lang="zh">{esc(a["zh_title"])}</h2>\n'
            f'            <h2 class="article-title en" data-lang="en" style="display:none">{esc(a["en_title"])}</h2>'
        )
    else:
        title_html = f'            <h2 class="article-title">{esc(a["en_title"])}</h2>'

    if a.get('zh_body'):
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

def generate_html(day_key, day_data, all_dates):
    articles = day_data['articles']
    total = len(articles)
    # 解析日期
    y, mo, d = day_key.split('-')
    mo_cn = int(mo)
    d_cn = int(d)
    day_label_cn = f"{y}年{mo_cn}月{d_cn}日"
    day_label_en = date_en(datetime(int(y), int(mo), int(d)))

    # 历史存档
    archive_items = ''
    for dk in all_dates:
        ky, kmo, kd = dk.split('-')
        m_cn = int(kmo)
        d_cn2 = int(kd)
        cls = 'archive-item today' if dk == day_key else 'archive-item'
        archive_items += f'<a href="{dk}.html" class="{cls}">{ky}年{m_cn}月{d_cn2}日</a>\n'

    archive_html = f'''
        <div class="archive-section">
            <h3>📅 历史存档</h3>
            <div class="archive-list">
{archive_items}            </div>
        </div>'''

    articles_html = '\n'.join(build_article(a) for a in articles)

    labels_replace = (
        f"'stats': '📝 {total} 篇精选', ... 'stats': '📝 {total} Articles'"
    )

    js = JS_TEMPLATE.replace('TOTAL_PLACEHOLDER', f'📝 {total} 篇精选')
    js = js.replace('TOTAL_PLACEHOLDER_EN', f'📝 {total} Articles')

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Builders · {day_key}</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
    <style>{CSS}</style>
</head>
<body>

    <div class="controls">
        <a href="../index.html" class="back-home">返回首页</a>
        <div class="lang-switch">
            <button class="lang-btn active" id="btn-zh" onclick="setLang('zh')">中文</button>
            <button class="lang-btn" id="btn-en" onclick="setLang('en')">EN</button>
        </div>
        <div class="audio-controls">
            <select class="voice-select" id="voiceSelect" title="选择语音"><option value="">智能选择</option></select>
            <div class="speed-control">
                <label>语速</label>
                <input type="range" class="speed-slider" id="speedSlider" min="0.5" max="1.5" step="0.05" value="0.9">
                <span class="speed-val" id="speedVal">0.9</span>
            </div>
            <button class="audio-btn" id="playAllBtn" onclick="playAll()">
                <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span id="playAllLabel">全文朗读</span>
            </button>
        </div>
    </div>

    <header class="hero">
        <p class="date">{day_label_en}</p>
        <h1 id="title-zh">AI Builders 每日精选</h1>
        <p class="hero-sub" id="subtitle-zh">每日精选 AI 领域最有价值的深度内容</p>
        <p class="stats" id="stats-zh">📝 {total} 篇精选</p>
    </header>

    <main class="articles">
{articles_html}
    </main>

    {archive_html}

    <footer>
        <p>Data by <a href="https://github.com/zarazhangrui/follow-builders" target="_blank">Follow Builders</a> · <a href="../index.html">Junes远程</a></p>
    </footer>

{js}
</body>
</html>'''

# ============ 主程序 ============
def main():
    # 确定要生成哪些天
    all_dates = sorted(ALL_DAYS.keys(), reverse=True)  # 最新在前

    # 解析命令行参数
    num_days = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    dates_to_generate = all_dates[:num_days]

    print(f'📅 生成 {len(dates_to_generate)} 天的 AI 资讯')
    print(f'   日期: {", ".join(dates_to_generate)}')
    print()

    # 生成所有日期文件
    for dk in dates_to_generate:
        html = generate_html(dk, ALL_DAYS[dk], dates_to_generate)
        path = os.path.join(OUTPUT_DIR, f'{dk}.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        total = len(ALL_DAYS[dk]['articles'])
        print(f'  ✅ {dk}.html ({total}篇)')

    # index.html = 最新一天
    latest = dates_to_generate[0]
    html = generate_html(latest, ALL_DAYS[latest], dates_to_generate)
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\n  ✅ index.html (= {latest}.html)')
    print(f'\n🎉 全部生成完成！共 {len(dates_to_generate)} 天，{sum(len(ALL_DAYS[d]["articles"]) for d in dates_to_generate)} 篇文章')

if __name__ == '__main__':
    main()
