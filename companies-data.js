// ============================================================
// 全球顶尖 100% 远程工作公司列表
// 数据来源：公开资料整理
// 最后更新：2026-03-18
// ============================================================

const COMPANIES = [
  // ── 科技巨头 ──
  {
    name: "GitHub",
    logo: "🐙",
    description: "全球最大的代码托管平台，被微软收购后仍保持远程优先文化，支持全球开发者协作。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://github.com"
  },
  {
    name: "GitLab",
    logo: "🦊",
    description: "全球最大的全远程公司之一，提供完整的 DevOps 平台，拥有超过 2000 名远程员工。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://about.gitlab.com"
  },
  {
    name: "Automattic",
    logo: "📝",
    description: "WordPress.com 和 WooCommerce 的母公司，全远程模式运营超过 15 年，员工遍布全球 90+ 国家。",
    tags: ["科技", "SaaS", "设计"],
    website: "https://automattic.com"
  },
  {
    name: "Zapier",
    logo: "⚡",
    description: "无代码自动化工具领域的领导者，连接 5000+ 应用，全远程团队分布在全球各地。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://zapier.com"
  },
  {
    name: "Stripe",
    logo: "💳",
    description: "全球领先的在线支付基础设施公司，为互联网经济提供支付解决方案。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://stripe.com"
  },
  {
    name: "Notion",
    logo: "📓",
    description: "一体化工作空间工具，集笔记、知识库、项目管理于一体，深受远程团队喜爱。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://notion.so"
  },
  {
    name: "Figma",
    logo: "🎨",
    description: "基于云端的协作设计工具，彻底改变了设计团队的工作方式，支持实时协作。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://figma.com"
  },
  {
    name: "Canva",
    logo: "🖼️",
    description: "全球最受欢迎的在线设计平台，让设计变得简单易用，用户遍布全球。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://canva.com"
  },
  {
    name: "Shopify",
    logo: "🛒",
    description: "全球领先的电商 SaaS 平台，帮助数百万商家建立在线商店。",
    tags: ["科技", "SaaS", "电商"],
    website: "https://shopify.com"
  },
  {
    name: "Twilio",
    logo: "📱",
    description: "通信 API 平台领导者，为开发者提供短信、语音、视频等通信能力。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://twilio.com"
  },
  {
    name: "DigitalOcean",
    logo: "🌊",
    description: "面向开发者的云计算平台，以简单易用的云服务器和优质文档著称。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://digitalocean.com"
  },
  {
    name: "HashiCorp",
    logo: "🔐",
    description: "云基础设施自动化领域的领导者，产品包括 Terraform、Vault 等。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://hashicorp.com"
  },
  {
    name: "Dropbox",
    logo: "📦",
    description: "云存储和文件同步领域的先驱，支持团队协作和文件管理。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://dropbox.com"
  },
  {
    name: "Atlassian",
    logo: "🛠️",
    description: "Jira、Confluence、Trello 等知名工具的母公司，助力团队协作与项目管理。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://atlassian.com"
  },
  {
    name: "Elastic",
    logo: "🔍",
    description: "Elasticsearch 和 Kibana 的开发公司，提供企业级搜索和分析解决方案。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://elastic.co"
  },
  {
    name: "Datadog",
    logo: "🐕",
    description: "云监控和分析平台，为企业提供全方位的可观测性解决方案。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://datadoghq.com"
  },
  {
    name: "Postman",
    logo: "📬",
    description: "API 开发和测试工具的领导者，被数百万开发者使用。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://postman.com"
  },
  {
    name: "Vercel",
    logo: "▲",
    description: "Next.js 的母公司，提供前端部署和托管服务，专注于开发者体验。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://vercel.com"
  },
  {
    name: "Netlify",
    logo: "🌐",
    description: "现代 Web 开发平台，提供静态网站托管和无服务器后端服务。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://netlify.com"
  },
  {
    name: "Linear",
    logo: "📊",
    description: "现代化的项目管理工具，专注于速度和简洁，深受软件团队喜爱。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://linear.app"
  },

  // ── AI 公司 ──
  {
    name: "OpenAI",
    logo: "🤖",
    description: "ChatGPT 和 GPT 系列模型的开发公司，AI 领域的领导者。",
    tags: ["科技", "AI", "SaaS"],
    website: "https://openai.com"
  },
  {
    name: "Anthropic",
    logo: "🧠",
    description: "Claude AI 的开发公司，专注于 AI 安全和可靠性研究。",
    tags: ["科技", "AI", "SaaS"],
    website: "https://anthropic.com"
  },
  {
    name: "Hugging Face",
    logo: "🤗",
    description: "AI 开源社区和模型托管平台，被称为 AI 界的 GitHub。",
    tags: ["科技", "AI", "开发工具"],
    website: "https://huggingface.co"
  },
  {
    name: "Scale AI",
    logo: "📊",
    description: "AI 数据标注和训练基础设施提供商，服务顶级 AI 公司。",
    tags: ["科技", "AI", "SaaS"],
    website: "https://scale.com"
  },
  {
    name: "Midjourney",
    logo: "🎨",
    description: "AI 图像生成领域的领导者，提供高质量的 AI 绘画服务。",
    tags: ["科技", "AI", "设计"],
    website: "https://midjourney.com"
  },
  {
    name: "Stability AI",
    logo: "🖼️",
    description: "Stable Diffusion 的开发公司，开源 AI 图像生成领域的先驱。",
    tags: ["科技", "AI", "设计"],
    website: "https://stability.ai"
  },

  // ── 金融科技 ──
  {
    name: "Coinbase",
    logo: "₿",
    description: "美国最大的加密货币交易所，提供数字资产的买卖和托管服务。",
    tags: ["科技", "金融", "区块链"],
    website: "https://coinbase.com"
  },
  {
    name: "Kraken",
    logo: "🦑",
    description: "全球知名的加密货币交易所，专注于安全性和合规性。",
    tags: ["科技", "金融", "区块链"],
    website: "https://kraken.com"
  },
  {
    name: "Chainalysis",
    logo: "⛓️",
    description: "区块链数据分析公司，为政府和金融机构提供合规和调查工具。",
    tags: ["科技", "金融", "区块链"],
    website: "https://chainalysis.com"
  },
  {
    name: "Plaid",
    logo: "🏦",
    description: "金融数据连接平台，让应用能够安全访问用户的银行账户。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://plaid.com"
  },
  {
    name: "Mercury",
    logo: "💰",
    description: "面向创业公司的数字银行，提供现代化的银行账户体验。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://mercury.com"
  },
  {
    name: "Brex",
    logo: "💳",
    description: "面向创业公司的企业信用卡和财务管理平台。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://brex.com"
  },
  {
    name: "Wise",
    logo: "💸",
    description: "国际汇款和多币种账户服务，以低汇率著称。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://wise.com"
  },
  {
    name: "Deel",
    logo: "🌍",
    description: "全球雇佣和薪酬支付平台，帮助企业远程雇佣全球人才。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://deel.com"
  },
  {
    name: "Remote",
    logo: "🌐",
    description: "全球雇佣和薪酬管理平台，简化国际雇佣流程。",
    tags: ["科技", "金融", "SaaS"],
    website: "https://remote.com"
  },

  // ── 区块链/Web3 ──
  {
    name: "Ethereum Foundation",
    logo: "💎",
    description: "以太坊生态系统的核心开发组织，推动去中心化未来。",
    tags: ["科技", "区块链", "开发工具"],
    website: "https://ethereum.org"
  },
  {
    name: "ConsenSys",
    logo: "🔗",
    description: "以太坊生态系统的主要贡献者，开发 MetaMask 等知名工具。",
    tags: ["科技", "区块链", "开发工具"],
    website: "https://consensys.net"
  },
  {
    name: "Alchemy",
    logo: "⚗️",
    description: "Web3 开发平台，为区块链应用提供基础设施。",
    tags: ["科技", "区块链", "开发工具"],
    website: "https://alchemy.com"
  },
  {
    name: "QuickNode",
    logo: "⚡",
    description: "区块链节点服务提供商，支持多链开发。",
    tags: ["科技", "区块链", "开发工具"],
    website: "https://quicknode.com"
  },
  {
    name: "OpenSea",
    logo: "🌊",
    description: "全球最大的 NFT 交易市场，连接数字创作者和收藏者。",
    tags: ["科技", "区块链", "SaaS"],
    website: "https://opensea.io"
  },

  // ── 远程招聘/HR ──
  {
    name: "Remote OK",
    logo: "✅",
    description: "最大的远程工作招聘平台之一，连接远程人才和公司。",
    tags: ["科技", "SaaS"],
    website: "https://remoteok.com"
  },
  {
    name: "We Work Remotely",
    logo: "🏠",
    description: "远程工作招聘领域的老牌平台，拥有大量优质职位。",
    tags: ["科技", "SaaS"],
    website: "https://weworkremotely.com"
  },
  {
    name: "FlexJobs",
    logo: "💼",
    description: "专业远程和灵活工作机会平台，提供人工审核的职位。",
    tags: ["科技", "SaaS"],
    website: "https://flexjobs.com"
  },
  {
    name: "Oyster",
    logo: "🦪",
    description: "全球雇佣平台，帮助企业轻松雇佣和管理远程团队。",
    tags: ["科技", "SaaS", "金融"],
    website: "https://oysterhr.com"
  },
  {
    name: "Lano",
    logo: "🌐",
    description: "全球雇佣和薪酬平台，简化跨境雇佣流程。",
    tags: ["科技", "SaaS", "金融"],
    website: "https://lano.io"
  },

  // ── 教育/学习 ──
  {
    name: "Coursera",
    logo: "📚",
    description: "全球领先的在线学习平台，与顶尖大学合作提供课程。",
    tags: ["科技", "教育", "SaaS"],
    website: "https://coursera.org"
  },
  {
    name: "Duolingo",
    logo: "🦉",
    description: "全球最受欢迎的语言学习应用，游戏化学习体验。",
    tags: ["科技", "教育", "AI"],
    website: "https://duolingo.com"
  },
  {
    name: "Khan Academy",
    logo: "🎓",
    description: "免费在线教育平台，为全球学习者提供优质教育资源。",
    tags: ["教育", "科技"],
    website: "https://khanacademy.org"
  },
  {
    name: "Skillshare",
    logo: "🎨",
    description: "创意类在线学习社区，涵盖设计、摄影、插画等领域。",
    tags: ["科技", "教育", "设计"],
    website: "https://skillshare.com"
  },
  {
    name: "Udemy",
    logo: "📖",
    description: "开放式在线课程市场，任何人都可以创建和销售课程。",
    tags: ["科技", "教育", "SaaS"],
    website: "https://udemy.com"
  },
  {
    name: "Brilliant",
    logo: "💡",
    description: "互动式学习平台，专注于数学、科学和计算机科学。",
    tags: ["科技", "教育", "AI"],
    website: "https://brilliant.org"
  },

  // ── 设计/创意 ──
  {
    name: "InVision",
    logo: "🎯",
    description: "产品设计协作平台，帮助团队设计、原型制作和协作。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://invisionapp.com"
  },
  {
    name: "Sketch",
    logo: "💎",
    description: "Mac 平台的专业 UI 设计工具，深受设计师喜爱。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://sketch.com"
  },
  {
    name: "Adobe (远程岗位)",
    logo: "🎨",
    description: "创意软件巨头，Photoshop、Illustrator 等工具的开发者。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://adobe.com"
  },
  {
    name: "Dribbble",
    logo: "🏀",
    description: "设计师社区和作品展示平台，连接设计师与雇主。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://dribbble.com"
  },
  {
    name: "Behance",
    logo: "🎨",
    description: "Adobe 旗下的创意作品展示平台，展示全球顶尖设计作品。",
    tags: ["科技", "设计", "SaaS"],
    website: "https://behance.net"
  },
  {
    name: "Loom",
    logo: "🎬",
    description: "异步视频通信工具，帮助团队高效沟通和协作。",
    tags: ["科技", "SaaS", "设计"],
    website: "https://loom.com"
  },

  // ── 开发工具 ──
  {
    name: "JetBrains",
    logo: "🧰",
    description: "专业开发工具公司，开发 IntelliJ IDEA、PyCharm 等 IDE。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://jetbrains.com"
  },
  {
    name: "Sourcegraph",
    logo: "🔍",
    description: "代码搜索和智能代码理解平台，帮助大型代码库导航。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://sourcegraph.com"
  },
  {
    name: "CircleCI",
    logo: "🔄",
    description: "持续集成和持续部署平台，自动化软件交付流程。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://circleci.com"
  },
  {
    name: "Travis CI",
    logo: "🔧",
    description: "开源项目的持续集成服务，与 GitHub 深度集成。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://travis-ci.com"
  },
  {
    name: "Snyk",
    logo: "🛡️",
    description: "开发者优先的安全平台，帮助发现和修复代码漏洞。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://snyk.io"
  },
  {
    name: "SonarSource",
    logo: "📊",
    description: "代码质量管理平台，SonarQube 的开发公司。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://sonarsource.com"
  },
  {
    name: "JFrog",
    logo: "🐸",
    description: "软件供应链管理平台，Artifactory 的开发公司。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://jfrog.com"
  },
  {
    name: "LaunchDarkly",
    logo: "🚀",
    description: "功能管理平台，帮助团队安全地发布和管理功能。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://launchdarkly.com"
  },
  {
    name: "PagerDuty",
    logo: "pager",
    description: "事件管理和运营平台，帮助团队快速响应和解决问题。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://pagerduty.com"
  },
  {
    name: "New Relic",
    logo: "📈",
    description: "可观测性平台，提供应用性能监控和分析服务。",
    tags: ["科技", "开发工具", "SaaS"],
    website: "https://newrelic.com"
  },

  // ── SaaS/生产力 ──
  {
    name: "Airtable",
    logo: "📋",
    description: "灵活的云端数据库和协作平台，结合电子表格和数据库的优势。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://airtable.com"
  },
  {
    name: "ClickUp",
    logo: "👆",
    description: "一站式生产力平台，集项目管理、文档、目标追踪于一体。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://clickup.com"
  },
  {
    name: "Asana",
    logo: "🎯",
    description: "团队协作和项目管理工具，帮助团队组织和追踪工作。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://asana.com"
  },
  {
    name: "Monday.com",
    logo: "📅",
    description: "工作操作系统，帮助团队规划、追踪和交付项目。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://monday.com"
  },
  {
    name: "Miro",
    logo: "🎨",
    description: "在线白板和协作平台，支持团队头脑风暴和视觉协作。",
    tags: ["科技", "SaaS", "设计"],
    website: "https://miro.com"
  },
  {
    name: "Mural",
    logo: "🖼️",
    description: "数字协作白板平台，帮助团队进行视觉思维和协作。",
    tags: ["科技", "SaaS", "设计"],
    website: "https://mural.co"
  },
  {
    name: "Slack",
    logo: "💬",
    description: "企业即时通讯和协作平台，被 Salesforce 收购后仍保持远程文化。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://slack.com"
  },
  {
    name: "Discord",
    logo: "🎮",
    description: "即时通讯和语音平台，从游戏社区发展为企业协作工具。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://discord.com"
  },
  {
    name: "Twitch",
    logo: "📺",
    description: "全球最大的游戏直播平台，亚马逊旗下公司。",
    tags: ["科技", "SaaS"],
    website: "https://twitch.tv"
  },
  {
    name: "Calendly",
    logo: "📆",
    description: "日程安排工具，消除安排会议的繁琐工作。",
    tags: ["科技", "SaaS"],
    website: "https://calendly.com"
  },
  {
    name: "Typeform",
    logo: "📝",
    description: "交互式表单和调查工具，提供出色的用户体验。",
    tags: ["科技", "SaaS"],
    website: "https://typeform.com"
  },
  {
    name: "Paperform",
    logo: "📄",
    description: "在线表单和调查工具，支持丰富的自定义选项。",
    tags: ["科技", "SaaS"],
    website: "https://paperform.co"
  },
  {
    name: "Webflow",
    logo: "🌐",
    description: "无代码网站建设平台，让设计师能够构建专业网站。",
    tags: ["科技", "SaaS", "设计"],
    website: "https://webflow.com"
  },
  {
    name: "Bubble",
    logo: "💭",
    description: "无代码应用开发平台，无需编程即可构建 Web 应用。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://bubble.io"
  },
  {
    name: "Coda",
    logo: "📄",
    description: "一体化文档工具，结合文档、电子表格和应用功能。",
    tags: ["科技", "SaaS"],
    website: "https://coda.io"
  },
  {
    name: "Pitch",
    logo: "📊",
    description: "协作式演示文稿工具，帮助团队创建美观的演示。",
    tags: ["科技", "SaaS", "设计"],
    website: "https://pitch.com"
  },
  {
    name: "Lattice",
    logo: "🎯",
    description: "人员管理平台，帮助公司建立高绩效团队。",
    tags: ["科技", "SaaS"],
    website: "https://lattice.com"
  },
  {
    name: "Culture Amp",
    logo: "❤️",
    description: "员工敬业度平台，帮助公司理解和改善员工体验。",
    tags: ["科技", "SaaS"],
    website: "https://cultureamp.com"
  },
  {
    name: "15Five",
    logo: "📈",
    description: "绩效管理和员工参与平台，帮助团队持续进步。",
    tags: ["科技", "SaaS"],
    website: "https://15five.com"
  },

  // ── 健康/医疗 ──
  {
    name: "Teladoc Health",
    logo: "🏥",
    description: "远程医疗服务领导者，提供虚拟医疗健康解决方案。",
    tags: ["科技", "健康", "SaaS"],
    website: "https://teladochealth.com"
  },
  {
    name: "Headspace",
    logo: "🧘",
    description: "冥想和心理健康应用，帮助用户减压和改善睡眠。",
    tags: ["科技", "健康", "SaaS"],
    website: "https://headspace.com"
  },
  {
    name: "Calm",
    logo: "🌙",
    description: "冥想和睡眠应用，全球最受欢迎的心理健康应用之一。",
    tags: ["科技", "健康", "SaaS"],
    website: "https://calm.com"
  },
  {
    name: "Noom",
    logo: "💪",
    description: "行为改变和体重管理平台，帮助用户建立健康习惯。",
    tags: ["科技", "健康", "AI"],
    website: "https://noom.com"
  },
  {
    name: "Talkspace",
    logo: "💬",
    description: "在线心理治疗平台，连接用户与持证治疗师。",
    tags: ["科技", "健康", "SaaS"],
    website: "https://talkspace.com"
  },
  {
    name: "Ro",
    logo: "💊",
    description: "数字健康平台，提供在线诊疗和药品配送服务。",
    tags: ["科技", "健康", "SaaS"],
    website: "https://ro.co"
  },
  {
    name: "Oscar Health",
    logo: "🏥",
    description: "科技驱动的健康保险公司，提供简化的健康保险体验。",
    tags: ["科技", "健康", "金融"],
    website: "https://hioscar.com"
  },

  // ── 安全 ──
  {
    name: "1Password",
    logo: "🔐",
    description: "密码管理工具，帮助个人和团队安全地管理密码。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://1password.com"
  },
  {
    name: "LastPass",
    logo: "🔑",
    description: "密码管理和单点登录解决方案，简化身份验证。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://lastpass.com"
  },
  {
    name: "Okta",
    logo: "🛡️",
    description: "身份和访问管理平台，帮助企业保护数字资产。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://okta.com"
  },
  {
    name: "Auth0",
    logo: "🔒",
    description: "身份验证即服务平台，被 Okta 收购后继续运营。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://auth0.com"
  },
  {
    name: "Cloudflare",
    logo: "☁️",
    description: "网络安全和性能平台，为网站提供 CDN 和安全服务。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://cloudflare.com"
  },
  {
    name: "Nord Security",
    logo: "🛡️",
    description: "网络安全公司，开发 NordVPN 等隐私保护工具。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://nordsecurity.com"
  },
  {
    name: "Tailscale",
    logo: "🐉",
    description: "VPN 和网络解决方案，简化安全网络连接。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://tailscale.com"
  },

  // ── 电商/市场 ──
  {
    name: "Amazon (远程岗位)",
    logo: "📦",
    description: "全球最大的电商平台，提供大量远程工作机会。",
    tags: ["科技", "电商", "SaaS"],
    website: "https://amazon.com"
  },
  {
    name: "Etsy",
    logo: "🎨",
    description: "手工艺品和创意商品电商平台，连接买家和卖家。",
    tags: ["科技", "电商", "SaaS"],
    website: "https://etsy.com"
  },
  {
    name: "Wayfair",
    logo: "🛋️",
    description: "家居电商平台，提供丰富的家具和家居装饰产品。",
    tags: ["科技", "电商", "SaaS"],
    website: "https://wayfair.com"
  },
  {
    name: "Gumroad",
    logo: "🛒",
    description: "创作者销售平台，帮助创作者销售数字产品。",
    tags: ["科技", "电商", "SaaS"],
    website: "https://gumroad.com"
  },
  {
    name: "Substack",
    logo: "📝",
    description: "付费通讯平台，帮助作者建立订阅者社区。",
    tags: ["科技", "SaaS", "教育"],
    website: "https://substack.com"
  },
  {
    name: "Patreon",
    logo: "❤️",
    description: "创作者会员平台，帮助创作者从粉丝获得收入。",
    tags: ["科技", "SaaS", "教育"],
    website: "https://patreon.com"
  },

  // ── 咨询/服务 ──
  {
    name: "Toptal",
    logo: "💎",
    description: "顶级自由职业者网络，连接企业与顶级人才。",
    tags: ["科技", "SaaS"],
    website: "https://toptal.com"
  },
  {
    name: "G2i",
    logo: "⚡",
    description: "React 和 React Native 开发者招聘平台。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://g2i.co"
  },
  {
    name: "Crossover",
    logo: "🔄",
    description: "远程工作招聘平台，专注于高技能岗位。",
    tags: ["科技", "SaaS"],
    website: "https://crossover.com"
  },
  {
    name: "Turing",
    logo: "🤖",
    description: "AI 驱动的远程开发者招聘平台。",
    tags: ["科技", "SaaS", "AI"],
    website: "https://turing.com"
  },

  // ── 其他知名公司 ──
  {
    name: "Buffer",
    logo: "📊",
    description: "社交媒体管理平台，全远程运营超过 10 年。",
    tags: ["科技", "SaaS", "市场营销"],
    website: "https://buffer.com"
  },
  {
    name: "Doist",
    logo: "✅",
    description: "Todoist 和 Twist 的开发公司，全远程团队。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://doist.com"
  },
  {
    name: "Hotjar",
    logo: "🔥",
    description: "用户行为分析工具，帮助理解用户如何使用网站。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://hotjar.com"
  },
  {
    name: "Mailchimp",
    logo: "🐵",
    description: "邮件营销平台领导者，被 Intuit 收购后继续运营。",
    tags: ["科技", "SaaS", "市场营销"],
    website: "https://mailchimp.com"
  },
  {
    name: "ConvertKit",
    logo: "📧",
    description: "面向创作者的邮件营销平台，专注于创作者经济。",
    tags: ["科技", "SaaS", "市场营销"],
    website: "https://convertkit.com"
  },
  {
    name: "Transistor",
    logo: "🎙️",
    description: "播客托管平台，帮助创作者发布和分发播客。",
    tags: ["科技", "SaaS"],
    website: "https://transistor.fm"
  },
  {
    name: "Podia",
    logo: "🎓",
    description: "在线课程和数字产品销售平台，服务创作者。",
    tags: ["科技", "SaaS", "教育"],
    website: "https://podia.com"
  },
  {
    name: "Teachable",
    logo: "📚",
    description: "在线课程创建和销售平台，帮助知识创作者变现。",
    tags: ["科技", "SaaS", "教育"],
    website: "https://teachable.com"
  },
  {
    name: "Thinkific",
    logo: "💡",
    description: "在线课程平台，帮助企业和创作者创建和销售课程。",
    tags: ["科技", "SaaS", "教育"],
    website: "https://thinkific.com"
  },
  {
    name: "Kajabi",
    logo: "🎯",
    description: "知识商业平台，一站式创建和销售在线课程。",
    tags: ["科技", "SaaS", "教育"],
    website: "https://kajabi.com"
  },
  {
    name: "Ghost",
    logo: "👻",
    description: "开源博客平台，帮助创作者建立付费订阅通讯。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://ghost.org"
  },
  {
    name: "Ghost.org",
    logo: "👻",
    description: "Ghost 博客平台的公司实体，全远程运营。",
    tags: ["科技", "SaaS", "开发工具"],
    website: "https://ghost.org/about"
  }
];
