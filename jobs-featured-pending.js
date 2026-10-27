// ============================================================
// 每日精选 · 待审池（人工把关前的数据都放这里）
// ------------------------------------------------------------
// 这个文件前端（index.html）不会引入，里面的内容绝不会直接展示给用户。
// 只有经过 review.html 审核台人工过审「上线」后，才会进入 jobs-featured.js。
//
// 【人工把关流程】
//   1. 候选进池（两种方式）
//      a. 打开 review.html →「从岗位库提候选」，从 jobs-cn.js / jobs-global.js
//         里搜索，看中的点「提为候选」
//      b. 手动往下面数组里加一条（自己找的岗位 / 社群投稿）
//   2. 打开 review.html →「待审候选」，逐条过目：
//      · 改写 description（人工摘要，一句话说清这岗位干啥、值不值得投）
//      · 看着不对劲的点「淘汰」，别手软 —— 标准是「看起来不至于太离谱」
//   3. 点「上线」→ 该条进入审核台的已上线区，date 自动填当天
//   4. 全部过完后点底部「导出」，把生成的两个文件覆盖回仓库：
//        导出 jobs-featured.js        → 覆盖根目录 jobs-featured.js
//        导出 jobs-featured-pending.js → 覆盖本文件
//   5. 提交前记得跑一次剥离脚本（见 jobs-featured.js 头部说明）
//
// 【字段说明】
//   status: 'pending' = 待审   'rejected' = 已淘汰（保留标记，避免下次重复出现）
//   _from : 'cn' / 'global' / 'manual'，标记候选来源，导出时会自动剔除
//   其余字段与正式精选岗基本一致，description 建议写成人工摘要
// ============================================================

const JOBS_FEATURED_PENDING = [
  // 示例（确认无误后可删掉这条）：
  // {
  //   'id': 'pending-20261027-01',
  //   'status': 'pending',
  //   '_from': 'manual',
  //   'addedAt': '2026-10-27',
  //   'title': '岗位标题',
  //   'company': '公司名',
  //   'category': '技术开发',
  //   'tags': ['远程', '全职'],
  //   'salary': '15-25k',
  //   'location': '全国远程',
  //   'description': '一句话人工摘要：这岗位干什么的、适合谁。',
  //   'responsibilities': [],
  //   'requirements': [],
  //   'benefits': [],
  //   'company_info': '',
  //   'sourceUrl': 'https://原文链接',
  // },
];

// 历史淘汰记录：人工判过「离谱」的岗位，id 记这里，避免以后重复提议
const JOBS_FEATURED_REJECTED = [
];
