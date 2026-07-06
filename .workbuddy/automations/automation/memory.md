# 每日职位数据更新 - 执行记录

## 最近一次执行: 2026-07-03 12:26

**结果**: ✅ 成功（手动触发）
- Remote OK: 100 条
- Remotive: 31 条
- 远程岛: 150 条
- who-is-hiring: 431 条（含联系方式 431 条）
- 远程中文网: 15 条
- V2EX: 5 条新帖（跳过 15 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=1087, Global=2000
- **数据变化**: CN 1064→1087 (+23), Global 2000 (不变)
- **Git**: commit 45c335f，push 成功（74f5dd7..45c335f）
- **money.xlsx**: 更新成功（5条V2EX + 431条who-is-hiring）
- **代理**: 127.0.0.1:7892 可用
- **备注**: 本次运行无异常，所有数据源均正常抓取



**结果**: ✅ 成功（手动触发）
- Remote OK: 100 条
- Remotive: 31 条
- 远程岛: 150 条
- who-is-hiring: ❌ 解析失败（JSON 损坏 line 89206 char 2885480）— 0 条入库
- 远程中文网: 15 条
- V2EX: 3 条新帖（跳过 17 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=1064, Global=2000
- **数据变化**: CN 1053→1064 (+11), Global 2000 (不变)
- **Git**: commit 74f5dd7，push 成功（36e7c52..74f5dd7）
- **money.xlsx**: 仅插入 3 条V2EX（who-is-hiring 0 条，因解析失败）
- **异常**: who-is-hiring 临时数据 JSON 在 line 89206 损坏（连续任务累积？），导致解析失败但不影响主流程
- **代理**: 127.0.0.1:7892 可用

## 上次执行: 2026-06-30 11:12

**结果**: ✅ 成功（自动化触发）
- Remote OK: 100 条
- Remotive: 34 条
- 远程岛: 150 条
- who-is-hiring: 428 条（含联系方式 428 条）
- 远程中文网: 15 条
- V2EX: 3 条新帖（跳过 17 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=1053, Global=2000
- **数据变化**: CN 1042→1053 (+11), Global 2000 (不变)
- **Git**: commit 36e7c52，push 成功（696f425..36e7c52）
- **money.xlsx**: 更新成功（3条V2EX + 428条who-is-hiring）
- **代理**: 7892 端口正常
- **文件大小**: jobs-cn.js 1.4MB, jobs-global.js 3.0MB, money.xlsx 4.5MB

## 最近一次执行: 2026-06-29 10:46

**结果**: ✅ 成功（手动触发）
- Remote OK: 100 条
- Remotive: 34 条
- 远程岛: 150 条
- who-is-hiring: 428 条（含联系方式 428 条）
- 远程中文网: 15 条
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=1042, Global=2000
- **数据变化**: CN 1034→1042 (+8), Global 2000 (不变)
- **Git**: commit 696f425，push 成功（1b6fd27..696f425）
- **money.xlsx**: 更新成功（0条V2EX + 428条who-is-hiring）
- **代理**: 7892 端口正常
- **文件大小**: jobs-cn.js 1.4MB, jobs-global.js 3.2MB, money.xlsx 4.5MB

## 最近一次执行: 2026-06-26 11:06

**结果**: ✅ 成功（手动触发）
- Remote OK: 100 条
- Remotive: 32 条
- 远程岛: 150 条
- who-is-hiring: 429 条（含联系方式 429 条）
- 远程中文网: 15 条
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（JS 渲染无法抓取）
- **汇总**: CN=1034, Global=2000
- **数据变化**: CN 1019→1034 (+15), Global 2000 (不变)
- **Git**: commit 218f7ed，push 成功
- **money.xlsx**: 更新成功（0条V2EX + 429条who-is-hiring）
- **修复**: scrape.sh 增加 `GIT_SSH_COMMAND="ssh -o ControlMaster=no"`，解决 git push 因 SSH mux 挂起的问题；修正 automation memory 路径为 `.workbuddy/...`

## 最近一次执行: 2026-06-22 13:55

**结果**: ✅ 成功（自动化触发）
- Remote OK: 100 条
- Remotive: 30 条
- 远程岛: 150 条
- who-is-hiring: 428 条（含联系方式 428 条）
- 远程中文网: 15 条
- V2EX: 2 条新帖（跳过 18 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=1006, Global=2000
- **数据变化**: CN 995→1006 (+11), Global 2000 (不变)
- **Git**: commit a0d11fe, push 成功
- **money.xlsx**: 更新成功（2条V2EX + 428条who-is-hiring）
- **代理**: 7892 端口正常

## 上次执行: 2026-06-18 10:39

**结果**: ✅ 成功（手动触发）
- Remote OK: 100 条
- Remotive: 30 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=995, Global=2000
- **数据变化**: CN 982→995 (+13), Global 2000 (不变)
- **Git**: commit be1098b, push 成功
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）
- **代理**: 7892 端口正常
- **备注**: 自动化任务 2026-06-16 后未自动触发，间隔 2 天后手动运行

## 上次执行: 2026-06-16 07:11

**结果**: ✅ 成功（手动触发）
- Remote OK: 100 条
- Remotive: 31 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（文件不存在 /tmp/dianyu.html）
- **汇总**: CN=982, Global=2000
- **数据变化**: CN 963→982 (+19), Global 2000 (不变)
- **Git**: commit 23c0d78, push 成功
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）
- **代理**: 7892 端口正常

## 上次执行: 2026-06-11 11:31

**结果**: ✅ 成功（自动化触发）
- Remote OK: 100 条
- Remotive: 28 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 1 条新帖（跳过 19 个非今日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=963, Global=2000
- **数据变化**: CN 948→963 (+15), Global 2000 (不变)
- **Git**: commit b437784, push 成功
- **money.xlsx**: 更新成功（1条V2EX + 427条who-is-hiring）

## 上次执行: 2026-06-09 07:59

**结果**: ✅ 成功（手动触发）
- Remote OK: 99 条
- Remotive: 28 条
- 远程岛: **150 条**（✅ 已恢复，上次120条异常）
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=948, Global=2000
- **数据变化**: CN 941→948 (+7), Global 2000 (不变)
- **Git**: commit 83f2f24, push 成功
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）

## 上次执行: 2026-06-07 09:35

**结果**: ✅ 成功（手动触发）
- Remote OK: 99 条
- Remotive: 28 条
- 远程岛: **120 条**（⚠️ 第3页 JSON 解析失败，少抓 30 条）
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=941, Global=2000（无变化）
- **Git**: commit 1ec399c, push 成功
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）
- **异常**: 远程岛第3页 JSON 解析失败 `Unterminated string`

## 上次执行: 2026-06-07 09:32

**结果**: ✅ 成功（自动化触发，重复进程干扰已修复）
- Remote OK: 99 条
- Remotive: 28 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条 ✅
- V2EX: 0 条新帖（跳过 20 个非今日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=941, Global=2000
- **数据变化**: CN 927→941 (+14), Global 2000 (不变)
- **Git**: commit 6fc9539, push 成功
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）
- **异常**: 首次运行出现重复进程导致 /tmp/ 临时文件丢失，远程中文网和V2EX解析失败；杀掉重复进程后重新运行成功
- **代理**: 7892 端口正常

## 上次执行: 2026-06-04 15:49

**结果**: ✅ 成功（V2EX 恢复！代理切换至 7892）
- Remote OK: 78 条
- Remotive: 23 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: **4 条新帖**（跳过 16 个非今日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=927, Global=2000
- **数据变化**: CN 923→927 (+4), Global 2000 (不变)
- **Git**: commit f704bff, push 成功
- **money.xlsx**: 更新成功（4条V2EX + 427条who-is-hiring）
- **修复**: scrape.sh 代理端口从 7897 切换至 7892（旧代理已不可用）

## 上次执行: 2026-06-04 12:13

**结果**: ✅ 成功
- Remote OK: 78 条
- Remotive: 23 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 失败（代理 127.0.0.1:7897 不可用）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=923, Global=2000
- **数据变化**: CN 912→923 (+11), Global 2000 (不变)
- **Git**: commit 343ab99, push 成功（需 `GIT_SSH_COMMAND="ssh -o ControlMaster=no"` 绕过 sandbox）
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）

## 上次执行: 2026-06-03 07:25

**结果**: ✅ 成功
- Remote OK: 94 条
- Remotive: 18 条
- 远程岛: 150 条
- who-is-hiring: 427 条（含联系方式 427 条）
- 远程中文网: 15 条
- V2EX: 失败（代理 127.0.0.1:7897 不可用）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=912, Global=2000
- **数据变化**: CN 901→912 (+11), Global 2000 (不变)
- **Git**: commit 6b57c13, push 成功
- **money.xlsx**: 更新成功（0条V2EX + 427条who-is-hiring）

## 上次执行: 2026-06-01 13:53

**结果**: ✅ 成功
- Remote OK: 95 条
- Remotive: 19 条
- 远程岛: 150 条
- who-is-hiring: 428 条（含联系方式 428 条）
- 远程中文网: 15 条
- V2EX: 2 条新帖（跳过 18 个非今日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=901, Global=2000
- **数据变化**: CN 891→901 (+10), Global 2000 (不变)
- **Git**: commit 16e24ca, push 成功
- **money.xlsx**: 更新成功（2条V2EX + 428条who-is-hiring）
- **修复**: scrape.sh 添加 Python venv PATH（解决 bs4 模块缺失）；git push 添加 SSH ControlMaster=no 解决 sandbox 拦截

## 上次执行: 2026-05-29 11:42

**结果**: ✅ 成功
- Remote OK: 100 条
- Remotive: 17 条
- 远程岛: 150 条
- who-is-hiring: 428 条（去重后 428 条）
- 远程中文网: 15 条
- V2EX: 1 条新帖（跳过19个非当日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=891, Global=2000
- **数据变化**: CN 883→891 (+8), Global 2000 (不变)
- **Git**: commit 35c0e2d, push 成功
- **money.xlsx**: 重建空文件后成功写入（1条V2EX + 428条who-is-hiring）
- **异常**: 无

## 上次执行: 2026-05-28 10:40

**结果**: ✅ 成功
- Remote OK: 85 条
- Remotive: 15 条
- 远程岛: 150 条
- who-is-hiring: 429 条（去重后 429 条）
- 远程中文网: 15 条
- V2EX: 2 条新帖（跳过18个非当日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=883, Global=2000
- **数据变化**: CN 874→883 (+9), Global 2000 (不变)
- **Git**: commit affdbbf, push 成功
- **money.xlsx**: 更新失败（File is not a zip file，文件可能损坏）
- **异常**: 无

## 上次执行: 2026-05-27 11:21

**结果**: ✅ 成功
- Remote OK: 56 条
- Remotive: 16 条
- 远程岛: 150 条
- who-is-hiring: 428 条（去重后 428 条）
- 远程中文网: 15 条
- V2EX: 1 条新帖（跳过19个非当日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=874, Global=2000
- **数据变化**: CN 857→874 (+17), Global 2000 (不变)
- **Git**: commit 71a1496, push 成功
- **money.xlsx**: 更新失败（File is not a zip file，文件可能损坏）
- **异常**: 远程中文网 URL 去重 15 条，V2EX 去重 20 条

## 上次执行: 2026-05-25 16:55

**结果**: ✅ 成功
- Remote OK: 61 条
- Remotive: 18 条
- 远程岛: 150 条
- who-is-hiring: 428 条
- 远程中文网: 跳过（文件不存在）
- V2EX: 1 条（跳过19个非当日帖子）
- 电鸭: 跳过（文件不存在）
- **汇总**: CN=857, Global=2000
- **Git**: e56bc3d 已推送
- **money.xlsx**: 新增 1 条V2EX + 428 条who-is-hiring

## 上次执行: 2026-05-25 16:10

**结果**: ✅ 成功
- Remote OK: 61 条
- Remotive: 18 条
- 远程岛: 150 条
- who-is-hiring: 428 条
- 远程中文网: 15 条
- V2EX: 1 条新帖
- 电鸭: 跳过（JS渲染无法抓取）

**数据变化**: CN 837→857 (+20), Global 2000 (不变)
**Git**: commit 51048bc, push 成功
**money.xlsx**: 更新 1 条 V2EX + 428 条 who-is-hiring

## 上一次执行: 2026-05-15 (app.js git add 修复版)
