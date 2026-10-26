#!/usr/bin/env node
/**
 * 批量生成会员兑换码
 *
 * 用法：
 *   node scripts/gen-codes.mjs --count 100 --plan monthly --days 30 --batch BATCH001
 *   node scripts/gen-codes.mjs --count 50 --days 365 --expires 2027-12-31 --import
 *
 * 参数：
 *   --count    生成数量（默认 50）
 *   --plan     套餐名，如 monthly / quarterly / yearly（默认 monthly）
 *   --days     会员天数（默认 30）
 *   --batch    批次号，便于对账（默认当天日期 BATCH-YYYYMMDD）
 *   --expires  兑换码本身的有效期 YYYY-MM-DD，过期未用即作废（可选）
 *   --out      输出 CSV 路径（默认 supabase/codes-<batch>.csv）
 *   --import   生成后直接写入 Supabase（需要 .env.local 里的 SERVICE_ROLE_KEY）
 *
 * 说明：
 *   兑换码使用 crypto 随机生成，字母表去掉了 0/O/1/I/L/U 等易混淆字符。
 */

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

// ── 参数解析 ──
const argv = process.argv.slice(2);
const arg = (name, def = null) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : def;
};
const has = (name) => argv.includes(`--${name}`);

const COUNT = parseInt(arg('count', '50'), 10);
const PLAN = arg('plan', 'monthly');
const DAYS = parseInt(arg('days', '30'), 10);
const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
const BATCH = arg('batch', `BATCH-${today}`);
const EXPIRES = arg('expires', null);
const OUT = arg('out', path.join('supabase', `codes-${BATCH}.csv`));
const DO_IMPORT = has('import');

if (!Number.isFinite(COUNT) || COUNT <= 0) {
  console.error('❌ --count 必须是正整数');
  process.exit(1);
}

// ── 生成兑换码 ──
// 去掉易混淆字符：0 O 1 I L U
const ALPHABET = 'ABCDEFGHJKMNPQRSTVWXYZ23456789';
const randomBlock = (len) => {
  const bytes = crypto.randomBytes(len);
  let out = '';
  for (let i = 0; i < len; i++) out += ALPHABET[bytes[i] % ALPHABET.length];
  return out;
};

const codes = new Set();
while (codes.size < COUNT) {
  codes.add(`JUNES-${randomBlock(4)}-${randomBlock(4)}-${randomBlock(4)}`);
}
const codeList = [...codes];

// ── 写 CSV ──
const outPath = path.resolve(ROOT, OUT);
fs.mkdirSync(path.dirname(outPath), { recursive: true });
const header = 'code,plan,duration_days,batch,status,expires_at\n';
const rows = codeList
  .map((c) => `${c},${PLAN},${DAYS},${BATCH},unused,${EXPIRES || ''}`)
  .join('\n');
fs.writeFileSync(outPath, header + rows, 'utf8');

console.log(`✅ 已生成 ${codeList.length} 个兑换码`);
console.log(`   套餐: ${PLAN} | 天数: ${DAYS} | 批次: ${BATCH}${EXPIRES ? ` | 有效期至: ${EXPIRES}` : ''}`);
console.log(`   CSV: ${OUT}`);
console.log(`   样例: ${codeList.slice(0, 3).join('  ')}`);

// ── 可选：直接导入 Supabase ──
if (!DO_IMPORT) {
  console.log('\n提示：加 --import 可直接写入数据库（需 .env.local 配置 SERVICE_ROLE_KEY）');
  process.exit(0);
}

function loadEnv() {
  const envPath = path.join(ROOT, '.env.local');
  if (!fs.existsSync(envPath)) {
    console.error(`❌ 缺少 ${envPath}`);
    console.error('   请创建该文件并写入：');
    console.error('   SUPABASE_URL=https://xxxx.supabase.co');
    console.error('   SERVICE_ROLE_KEY=eyJxxx...');
    process.exit(1);
  }
  const env = {};
  for (const line of fs.readFileSync(envPath, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, '').trim();
  }
  return env;
}

const env = loadEnv();
const BASE = env.SUPABASE_URL;
const KEY = env.SERVICE_ROLE_KEY;
if (!BASE || !KEY) {
  console.error('❌ .env.local 里缺少 SUPABASE_URL 或 SERVICE_ROLE_KEY');
  process.exit(1);
}

const payload = codeList.map((code) => ({
  code,
  plan: PLAN,
  duration_days: DAYS,
  batch: BATCH,
  status: 'unused',
  expires_at: EXPIRES ? `${EXPIRES}T23:59:59+08:00` : null,
}));

const CHUNK = 500;
let ok = 0;
for (let i = 0; i < payload.length; i += CHUNK) {
  const chunk = payload.slice(i, i + CHUNK);
  const res = await fetch(`${BASE}/rest/v1/redeem_codes`, {
    method: 'POST',
    headers: {
      apikey: KEY,
      Authorization: `Bearer ${KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal',
    },
    body: JSON.stringify(chunk),
  });
  if (!res.ok) {
    const text = await res.text();
    console.error(`❌ 导入失败（第 ${i / CHUNK + 1} 批）: ${res.status} ${text}`);
    process.exit(1);
  }
  ok += chunk.length;
}

console.log(`\n🚀 已导入 ${ok} 个兑换码到 Supabase（批次 ${BATCH}）`);

const check = await fetch(
  `${BASE}/rest/v1/redeem_codes?select=code&batch=eq.${encodeURIComponent(BATCH)}`,
  { headers: { apikey: KEY, Authorization: `Bearer ${KEY}` } }
);
if (check.ok) {
  const rows = await check.json();
  console.log(`   校验：库中该批次共 ${rows.length} 条`);
}
