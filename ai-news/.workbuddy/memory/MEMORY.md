# MEMORY.md - 长期记忆

## 项目架构

### gen-index.py vs generate-digest.sh
- `gen-index.py`：当前自动化实际调用的脚本，但**推文内容硬编码**在 ARTICLES 列表里
- `generate-digest.sh`：使用真实 feed 数据从 feed-x.json 读取，两个脚本并存
- **feed-x.json 等数据文件停在 2026-04-13**（需要 X_BEARER_TOKEN + GitHub Actions 才能刷新）

### 新脚本版本
- `gen-index-v1.py`：从 feed-x.json 动态读取，英文原文展示（Feed更新于 2026-04-13）
- `gen-index-v2.py`：通过 web search 实时抓取最新AI资讯，中文摘要（真正新鲜的今日内容）

## 2026-04-21 执行记录

### AI 资讯自动化（ai-6 定时任务）
- 数据来源：Web Search 实时搜索（8组关键词）
- 生成内容：8篇精选（5条Tweet + 2条Podcast + 1条Blog）
- 输出文件：index.html + 2026-04-21.html
- Git：✅ 已推送（commit: 1cdc96a）
- 状态：成功

### 今日资讯亮点（2026-04-21）
1. Claude Mythos Preview：Anthropic CEO 透露其网络安全能力过强暂不发布（Project Glasswing 发现数千零日漏洞）
2. Andrej Karpathy：宣布 RAG 已死，LLM 直接处理个人知识库成为新范式
3. MiniMax M2.7：国产自进化 Agent 开源，SWE-Pro 56.22%，公司 80% 代码由 AI 生成
4. Stanford AI Index 2026：信任缺口扩大，公众焦虑达历史高点
5. Google Gemma 4：单块 80GB H100 即可运行，Apache 2.0 开源许可
6. Latent Space：Noetik 用 AI 解决癌症试验 95% 失败率困局
7. Lex Fridman #492：AI 对齐深度讨论
8. OX Security：揭露 Anthropic MCP 供应链安全漏洞

## 2026-04-20 执行记录

### AI 资讯自动化（ai-2）执行
- gen-index.py 正常执行，生成 10 篇精选
- 输出：index.html + 2026-04-20.html（已推送 GitHub, commit: 8515909）

## 2026-04-20 执行记录

### AI 资讯自动化（ai）执行
- generate-digest.sh 正常执行，数据：X=12, Podcasts=1, Blogs=1
- 生成文件：2026-04-20.html
- 输出：index.html + 2026-04-20.html（已推送 GitHub, commit: b23d853）

## 2026-04-20 执行记录

### AI 资讯自动化（ai-7 定时任务）
- 数据来源：web_search 多关键词搜索（8次搜索）
- JSON 数据路径：`~/.workbuddy/skills/ai-news-daily/data/today.json`
- 生成脚本：`~/.workbuddy/skills/ai-news-daily/scripts/gen-news.py`
- 输出：index.html + 2026-04-20.html（已推送 GitHub, commit: a345f37）

### 今日资讯亮点（2026-04-20）
1. Claude Opus 4.7 GA：SWE-bench 87.6%，xhigh Effort Control 模式
2. Factory AI $1.5B 独角兽融资，企业级 AI 编码 Droids 平台
3. 英国 $675M 主权 AI 基金启动
4. OpenAI/Anthropic 营收双双达 $19B，AI 透明度法案推进
5. 微软 MAI 模型 + Grok 4.20 上线 Microsoft Foundry
6. TWIML Podcast：Tri Dao 谈 Mamba-3
7. Latent Space：I-DLM-8B 扩散语言模型突破
8. NVIDIA NVFP4：FP8 降级，4 位量化成新基准

## 2026-04-19 执行记录

### AI 资讯自动化（ai-9）执行
- 数据来源：web_fetch 多源抓取（Web Search 不可用时的降级方案）
- 数据源：TechCrunch, The Verge, Ars Technica, VentureBeat, Reuters, Anthropic 官网, Google Blog, Lex Fridman
- JSON 数据路径：`~/.workbuddy/skills/ai-news-daily/data/today.json`
- 生成脚本：`~/.workbuddy/skills/ai-news-daily/scripts/gen-news.py`
- 输出：index.html + 2026-04-19.html（已推送 GitHub, commit: 5c6f7dc）
- **注意**：JSON 中不能使用中文引号（""），会导致 Python json.load() 解析失败

### 今日资讯亮点（2026-04-19）
1. Cerebras Systems 提交美股 IPO 申请，挑战 NVIDIA
2. Anthropic 推出 Claude Design，从模型商向全栈产品公司转型（$300亿 ARR）
3. OpenAI 发布 GPT-Rosalind 生物学专用 LLM
4. Mozilla 推出 Thunderbolt 开源主权 AI 客户端
5. DeepSeek 以 $100 亿估值融资，中美 AI 竞争升级
6. Lex Fridman 播客：黄仁勋谈 NVIDIA $4万亿市值与 AI 革命
7. Latent Space：OpenAI Dark Factory 内幕（10亿 tokens/日，零人工）
8. VentureBeat：AI 推理无需前沿大模型，train-to-test scaling 解读
