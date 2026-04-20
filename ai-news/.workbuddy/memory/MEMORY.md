# MEMORY.md - 长期记忆

## 项目架构

### gen-index.py vs generate-digest.sh
- `gen-index.py`：当前自动化实际调用的脚本，但**推文内容硬编码**在 ARTICLES 列表里
- `generate-digest.sh`：使用真实 feed 数据从 feed-x.json 读取，两个脚本并存
- **feed-x.json 等数据文件停在 2026-04-13**（需要 X_BEARER_TOKEN + GitHub Actions 才能刷新）

### 新脚本版本
- `gen-index-v1.py`：从 feed-x.json 动态读取，英文原文展示（Feed更新于 2026-04-13）
- `gen-index-v2.py`：通过 web search 实时抓取最新AI资讯，中文摘要（真正新鲜的今日内容）

## 2026-04-20 执行记录

### AI 资讯自动化（ai-2）执行
- gen-index.py 正常执行，生成 10 篇精选
- 输出：index.html + 2026-04-20.html（已推送 GitHub, commit: 8515909）

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
