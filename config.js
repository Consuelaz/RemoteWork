/* ============================================================
   前端配置
   - SUPABASE_ANON_KEY 是公开的（受 RLS 保护），可以提交到仓库
   - SERVICE_ROLE_KEY 是最高权限密钥，只能放 .env.local，绝不进仓库
   - DEV_MODE 只在 localhost / 127.0.0.1 下生效，用于没配邮件服务时
     本地走通交互流程；部署到线上后自动失效
   ============================================================ */

const SUPABASE_CONFIG = {
  // Supabase 控制台 → Project Settings → API → Project URL
  URL: 'https://doytntlxfidljoszhyje.supabase.co',

  // Supabase 控制台 → Project Settings → API → anon public key
  ANON_KEY:
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRveXRudGx4ZmlkbGpvc3poeWplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI5Nzc2MjUsImV4cCI6MjEwODU1MzYyNX0.lBmjNhocGApGDkeHwk0wHc5kO7b2wvkf-lkhuQznmpY',

  // 正式站点地址（登录邮件里的链接指向这里）
  // 必须与 Supabase 控制台 Authentication → URL Configuration 的
  // Site URL / Redirect URLs 白名单一致，否则链接会被回退到默认的 localhost:3000
  SITE_URL: 'https://remotework.asia',

  // 是否开启本地模拟登录（仅在 localhost 生效，线上自动关闭）
  DEV_MODE: true,
};

// 线上环境强制关闭 DEV 模式，避免绕过登录的后门被带到生产
const __isLocal =
  typeof location !== 'undefined' &&
  (location.hostname === 'localhost' ||
    location.hostname === '127.0.0.1' ||
    location.protocol === 'file:');

SUPABASE_CONFIG.DEV_ACTIVE = SUPABASE_CONFIG.DEV_MODE && __isLocal;
SUPABASE_CONFIG.IS_LOCAL = __isLocal;

// 登录链接回跳地址：本地调试用当前 origin，线上固定用 SITE_URL
// （避免 www / 预览域名 / 端口差异导致链接与白名单对不上）
SUPABASE_CONFIG.LOGIN_REDIRECT = (__isLocal ? location.origin : SUPABASE_CONFIG.SITE_URL).replace(/\/+$/, '') + '/account.html';

window.SUPABASE_CONFIG = SUPABASE_CONFIG;
