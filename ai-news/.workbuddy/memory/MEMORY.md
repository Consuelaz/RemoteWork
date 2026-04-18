# MEMORY.md - 长期记忆

## 项目架构

### gen-index.py vs generate-digest.sh
- `gen-index.py`：当前自动化实际调用的脚本，但**推文内容硬编码**在 ARTICLES 列表里
- `generate-digest.sh`：使用真实 feed 数据从 feed-x.json 读取，两个脚本并存
- **feed-x.json 等数据文件停在 2026-04-13**（需要 X_BEARER_TOKEN + GitHub Actions 才能刷新）

### 新脚本版本
- `gen-index-v1.py`：从 feed-x.json 动态读取，英文原文展示（Feed更新于 2026-04-13）
- `gen-index-v2.py`：通过 web search 实时抓取最新AI资讯，中文摘要（真正新鲜的今日内容）

## 2026-04-19 执行记录

### AI 资讯自动化（ai-6）执行
- 数据来源：Web Search 实时搜索（替代 feed-x.json）
- JSON 数据路径：`~/.workbuddy/skills/ai-news-daily/data/today.json`
- 生成脚本：`~/.workbuddy/skills/ai-news-daily/scripts/gen-news.py`
- 输出：index.html + 2026-04-19.html（已推送 GitHub）
- **注意**：JSON 中不能使用中文引号（""），会导致 Python json.load() 解析失败

### 今日资讯亮点（2026-04-19）
1. Anthropic 发布 Claude Opus 4.7 + Claude Design 设计工具
2. Google DeepMind 发布 Gemini Robotics-ER 1.6
3. OpenAI 收购个人理财 AI 初创公司 Hiro
4. Kimi K2.6 Code Preview 进入公开测试
5. Lex Fridman #490：2026 年 AI 全景图播客
6. Latent Space：LLM 评测方法论深度讨论
7. Epsilla：AI Agent 最新技术突破总结
8. buildfastwithai：2026年3月12个模型集中发布分析
