# 自动化任务执行记录

## 最新执行

- **日期**: 2026-04-16
- **状态**: ✅ 成功
- **数据源**: Remote OK(94) + Remotive(21) + 远程岛(150) + who-is-hiring(434) + 远程中文网(15) + V2EX(0，跳过非今日20条)
- **数据合并**: CN=601, Global=2000
- **money.xlsx**: 插入 0 条 V2EX 数据 + 434 条 who-is-hiring 数据
- **Git 提交**: `bba2052`，已推送至 `master`
- **备注**: 电鸭仍无法抓取（curl 无法渲染 JS 页面）

## 执行历史

| 日期 | CN岗位数 | Global岗位数 | 状态 |
|------|----------|--------------|------|
| 2026-04-16 | 601 | 2000 | ✅ 成功 |
| 2026-04-14 | 583 | 1957 | ✅ 成功 |
| 2026-04-09 | 557 | 1616 | ✅ 成功 |
| 2026-04-07 | 537 | 1505 | ✅ 成功 |
| 2026-04-03 | 95 | 1341 | ✅ 成功 |
| 2026-03-30 | 80 | 1150 | ✅ 成功 |
| 2026-03-28 | 75 | 967 | ✅ 成功 |
| 2026-03-27 | 724 | 2000 | ✅ 成功 |
| 2026-03-26 | 689 | 1815 | ✅ 成功 |
| 2026-03-25 | 375 | 598 | ✅ 成功 |
| 2026-03-24 | 180 | 200 | ✅ 成功 |

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
