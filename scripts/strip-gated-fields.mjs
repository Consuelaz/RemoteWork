#!/usr/bin/env node
/**
 * 从 jobs-featured.js / jobs-cn.js / jobs-global.js 剥离需要付费才能看的字段：
 *   - contact / contact_type   内推人联系方式
 *   - applyUrl (apply_url)     真实投递链接
 *
 * 这两个字段已经导出到 supabase/job-access.csv，数据库才是它们唯一的家。
 * 留在前端 JS 里 = 任何人 F12 就能白嫖，会员权益形同虚设。
 *
 * 用法：
 *   node scripts/strip-gated-fields.mjs           # 预览，不改文件
 *   node scripts/strip-gated-fields.mjs --apply   # 真正执行（自动备份 .bak）
 *
 * ⚠️ 执行前提：supabase/job-access.csv 已经导入数据库。
 *    顺序反了 = 权益数据永久丢失（本地 money.xlsx 还留着一份，但 CN 的 contact 没有）。
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const APPLY = process.argv.includes('--apply');

// 精选岗用下划线命名（apply_url / contact / contact_type），抓取数据用驼峰（applyUrl）
const FILES = ['jobs-featured.js', 'jobs-cn.js', 'jobs-global.js'];
const PATTERNS = [
  { name: 'applyUrl', re: /^(\s*)applyUrl:\s*'.*',\s*$/gm, repl: "$1applyUrl: ''," },
  { name: 'apply_url', re: /^(\s*)apply_url:\s*'.*',\s*$/gm, repl: "$1apply_url: ''," },
  { name: 'contact', re: /^(\s*)contact:\s*'.*',\s*$/gm, repl: "$1contact: ''," },
  { name: 'contact_type', re: /^(\s*)contact_type:\s*'.*',\s*$/gm, repl: "$1contact_type: ''," },
];

// 前置检查：权益 CSV 必须存在且非空
const csvPath = path.join(ROOT, 'supabase', 'job-access.csv');
if (APPLY) {
  if (!fs.existsSync(csvPath)) {
    console.error('❌ 找不到 supabase/job-access.csv，请先跑 export-job-access.mjs');
    process.exit(1);
  }
  const lines = fs.readFileSync(csvPath, 'utf8').trim().split('\n');
  if (lines.length < 2) {
    console.error('❌ supabase/job-access.csv 是空的，导入数据库前不能剥离前端字段');
    process.exit(1);
  }
  console.log(`✅ 权益数据已就绪（${lines.length - 1} 条），可以安全剥离`);
}

for (const file of FILES) {
  const p = path.join(ROOT, file);
  if (!fs.existsSync(p)) {
    console.log(`- ${file} 不存在，跳过`);
    continue;
  }
  const src = fs.readFileSync(p, 'utf8');
  let out = src;
  const stat = {};

  for (const { name, re, repl } of PATTERNS) {
    const before = out;
    out = out.replace(re, repl);
    stat[name] = (before.match(re) || []).length;
  }

  const summary = PATTERNS.map((p) => `${p.name} ${stat[p.name] || 0}`).join(', ');
  console.log(`${APPLY ? '✂️ ' : '🔍 '}${file}: ${summary} 条`);

  if (!APPLY) continue;

  fs.writeFileSync(`${p}.bak`, src, 'utf8');
  fs.writeFileSync(p, out, 'utf8');
  console.log(`   已写入，原文件备份为 ${file}.bak`);
}

if (!APPLY) {
  console.log('\n这是预览。确认已导入数据库后，加 --apply 执行。');
}
