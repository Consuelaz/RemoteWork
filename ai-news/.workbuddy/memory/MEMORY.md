# MEMORY.md - 长期记忆

## 项目架构

### gen-index.py vs generate-digest.sh
- `gen-index.py`：当前自动化实际调用的脚本，但**推文内容硬编码**在 ARTICLES 列表里
- `generate-digest.sh`：使用真实 feed 数据从 feed-x.json 读取，两个脚本并存
- **feed-x.json 等数据文件停在 2026-04-13**（需要 X_BEARER_TOKEN + GitHub Actions 才能刷新）

### 新脚本版本
- `gen-index-v1.py`：从 feed-x.json 动态读取，英文原文展示（Feed更新于 2026-04-13）
- `gen-index-v2.py`：通过 web search 实时抓取最新AI资讯，中文摘要（真正新鲜的今日内容）
