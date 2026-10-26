#!/usr/bin/env node
/**
 * 生成 supabase/job-access.csv —— 会员专属数据（申请链接 + 内推联系方式）
 *
 * 数据来源：
 *   1. jobs-cn.js / jobs-global.js 里的 applyUrl
 *   2. jobs-cn.js 里的 contact（V2EX 内推联系方式）
 *   3. supabase/money-contacts.csv（由 scripts/export-money-contacts.py 从 money.xlsx 抽出）
 *   4. jobs-featured.js「每日精选」里的 apply_url / contact（手动维护，优先级最高）
 *
 * 用法：
 *   node scripts/export-job-access.mjs
 *
 * 输出：supabase/job-access.csv（列：job_id,apply_url,contact,contact_type）
 * 注意：该文件含内推人隐私联系方式，已加入 .gitignore，千万不要提交。
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const loadJsArray = (file, name) => {
  const p = path.join(ROOT, file);
  if (!fs.existsSync(p)) return [];
  const code = fs.readFileSync(p, 'utf8');
  return new Function(code + `; return ${name};`)();
};

// 正确的 CSV 解析：支持带引号、引号内逗号、"" 转义
const splitCsvLine = (line) => {
  const out = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (line[i + 1] === '"') { cur += '"'; i++; }
        else inQuotes = false;
      } else cur += ch;
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      out.push(cur);
      cur = '';
    } else cur += ch;
  }
  out.push(cur);
  return out;
};

const parseCsv = (file) => {
  const p = path.join(ROOT, file);
  if (!fs.existsSync(p)) return [];
  const text = fs.readFileSync(p, 'utf8').trim();
  if (!text) return [];
  const lines = text.split(/\r?\n/);
  const header = splitCsvLine(lines[0]).map((h) => h.trim());
  return lines.slice(1)
    .filter((l) => l.trim() !== '')
    .map((line) => {
      const cols = splitCsvLine(line);
      const obj = {};
      header.forEach((h, i) => { obj[h] = (cols[i] ?? '').trim(); });
      return obj;
    });
};

const normUrl = (u) => (u || '').trim().replace(/#.*$/, '').replace(/\/+$/, '');

const detectType = (c) => {
  if (!c) return '';
  if (/telegram|tg[:：]/i.test(c)) return 'telegram';
  if (/微信|wechat|wx[:：]/i.test(c)) return 'wechat';
  if (/邮箱|email|@/i.test(c)) return 'email';
  if (/电话|手机|1[3-9]\d{9}/.test(c)) return 'phone';
  return 'other';
};

// ── 1. 汇总岗位数据 ──
const featured = loadJsArray('jobs-featured.js', 'JOBS_FEATURED');
const cn = loadJsArray('jobs-cn.js', 'JOBS_CN');
const global = loadJsArray('jobs-global.js', 'JOBS_GLOBAL');
// 精选放最前：万一 id 与抓取数据撞了，以手动维护的精选为准
const all = [...featured, ...cn, ...global];
const featuredIds = new Set(featured.map((j) => j.id));
console.log(`岗位数据：精选 ${featured.length} + CN ${cn.length} + Global ${global.length} = ${all.length}`);

// ── 2. money.xlsx 联系方式按 sourceUrl 建索引 ──
const moneyRows = parseCsv(path.join('supabase', 'money-contacts.csv'));
const moneyByUrl = new Map();
for (const r of moneyRows) {
  const key = normUrl(r.source_url);
  if (key && r.contact) moneyByUrl.set(key, r);
}
console.log(`money.xlsx 联系方式：${moneyByUrl.size} 条`);

// ── 3. 合并 ──
const csvEscape = (v) => {
  const s = (v ?? '').toString().replace(/\r?\n/g, ' ').trim();
  return /[",]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

const out = [];
const seenIds = new Set();
let withContact = 0;
let withApply = 0;
let featuredCount = 0;

for (const job of all) {
  if (seenIds.has(job.id)) continue;
  const isFeatured = featuredIds.has(job.id);

  const money = moneyByUrl.get(normUrl(job.sourceUrl));
  // 精选岗用 apply_url（手动维护），抓取数据用 applyUrl
  const rawApply = ((job.apply_url || job.applyUrl) || '').trim();
  const contact = ((job.contact || '').trim() || (money?.contact || '').trim());

  if (!rawApply && !contact) continue;

  // 精选岗的 apply_url 是手动配的真实投递入口，直接采用；
  // 抓取数据里的远程中文网 /login?next= 属于公开跳转，不作为付费权益
  const paidApply = isFeatured
    ? rawApply
    : (rawApply && !/^\/login\?next=/.test(rawApply) && /^https?:\/\//.test(rawApply) ? rawApply : '');

  if (!paidApply && !contact) continue;

  seenIds.add(job.id);
  if (paidApply) withApply++;
  if (contact) withContact++;
  if (isFeatured) featuredCount++;

  out.push([
    job.id,
    paidApply,
    contact,
    (job.contact_type || '').trim() || detectType(contact),
  ].map(csvEscape).join(','));
}

const outPath = path.join(ROOT, 'supabase', 'job-access.csv');
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, 'job_id,apply_url,contact,contact_type\n' + out.join('\n') + '\n', 'utf8');

console.log(`\n✅ 生成 ${out.length} 条会员权益数据`);
console.log(`   含申请链接: ${withApply} 条`);
console.log(`   含内推联系方式: ${withContact} 条`);
console.log(`   其中来自「每日精选」: ${featuredCount} 条`);
console.log(`   输出: supabase/job-access.csv（勿提交，已 gitignore）`);
