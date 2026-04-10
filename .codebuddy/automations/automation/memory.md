# 自动化任务执行记录

## 最新执行

- **日期**: 2026-04-09（下午修复）
- **问题**: 海外岗位显示 0 → `JOBS_GLOBAL` 未定义
- **根本原因①**: 早晨截断脚本用正则操作 JS 文件，含 `\'` 的 description 导致单引号不闭合，JS 语法出错
- **根本原因②**: `load_js_array` 读取历史数据时不做 unescape，每次运行多一层转义
- **修复**: `scrape.sh` load_js_array 第1281行加 unescape；手动修复历史数据转义；恢复 1616 条历史记录重新生成
- **最终结果**: CN=557, Global=1617，commit `0e4eec1` 已推送


  - Remote OK: 96 个岗位（成功）
  - Remotive: 20 个岗位（成功）
  - 远程岛: 150 个岗位（成功）
  - 远程中文网: 15 个岗位（成功）
  - V2EX: 1 条（代理可用，跳过非今日帖子18条）
  - who-is-hiring: 434 个岗位（成功）
- **数据合并**: CN 548→557（+9），Global 1566→1616（+50）
- **money.xlsx**: 插入 1 条 V2EX + 434 条 who-is-hiring 数据
- **额外处理**: jobs-global.js 历史description超长（11MB），截断1240条 → 2.2MB
- **Git 提交**: `3cfc175`，已推送至 `master`
- **依赖**: 首次在此环境运行，已补装 beautifulsoup4/requests/lxml/openpyxl

## 执行历史

| 日期 | CN岗位数 | Global岗位数 | 状态 |
|------|----------|--------------|------|
| 2026-04-09 | 557 | 1616 | ✅ 成功（补装依赖，修复description超长11MB→2.2MB） |
| 2026-04-07 | 537 | 1505 | ✅ 成功（修复 who-is-hiring NoneType + jobs-global.js 文件过大） |
| 2026-04-03 | 95 | 1341 | ✅ 成功（V2EX不可用，修复who-is-hiring guess_category Bug） |
| 2026-03-30 | 80 | 1150 | ✅ 成功（V2EX 5条新帖，代理可用） |
| 2026-03-28 | 75 | 967 | ✅ 成功（V2EX今日无新帖） |
| 2026-03-27 | 724 | 2000 | ✅ 成功（含远程岛150条） |
| 2026-04-03 | 95 | 1341 | ✅ 成功（V2EX不可用，修复who-is-hiring guess_category Bug） |
| 2026-03-30 | 80 | 1150 | ✅ 成功（V2EX 5条新帖，代理可用） |
| 2026-03-28 | 75 | 967 | ✅ 成功（V2EX今日无新帖） |
| 2026-03-27 | 724 | 2000 | ✅ 成功（含远程岛150条） |
| 2026-03-26 | 689 | 1815 | ✅ 成功（含远程岛150条） |
| 2026-03-25 | 375 | 598 | ✅ 成功（V2EX可用，Remotive新增） |
| 2026-03-24 | 180 | 200 | ✅ 成功（V2EX可用） |

## Bug 修复记录

- **2026-04-07 修复①**：who-is-hiring 解析 NoneType —— `work_mode/company/salary/requirements/responsibilities/benefits/contact_channels` 字段均可能为 null，统一加兜底。`requirements` 兼容字符串/列表/null 三种类型。
- **2026-04-07 修复②**：`jobs-global.js` 超过 GitHub 100MB 限制 —— 远程岛 description 含完整 HTML（最大 3.4MB/条），968 条历史数据未截断，文件累积到 347MB。用 Node.js 对全部 description 截断到 500 字符，文件降至 2.5MB。Remote OK description 也补加 `[:500]` 截断。
- **2026-04-03 修复**：`scrape.sh` 第701行 `guess_category` → `guess_category_cn`（who-is-hiring 解析段）
- **2026-03-21 修复**：`scrape.sh` 中 `jobs_to_js()` 函数将 Python 布尔值 `True/False` 直接写入 JS，导致 JS 语法错误、网站无数据显示。已修复为输出 `true/false`（JS 格式）。

## 注意事项

- V2EX 需要代理（`http://127.0.0.1:7897`），代理未启动时抓取失败属正常现象
- 电鸭页面选择器（`div.post-item` 等）可能需要更新以匹配当前页面结构
- **description 字段必须限长**：所有数据源的 description 均要 `[:500]`，否则会导致 js 文件过大
- **每次脚本运行后检查文件大小**：`ls -lh jobs-global.js`，超过 10MB 需要警惕
