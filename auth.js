/* ============================================================
   账号 / 会员模块
   对外暴露 window.Auth
     Auth.init()              初始化（页面加载时自动执行）
     Auth.isLoggedIn()        是否已登录
     Auth.isMember()          是否为有效会员
     Auth.sendOtp(email)         发送邮箱验证码（6 位）
     Auth.verifyOtp(email,code)  验证码登录
     Auth.signInWithMagicLink(email)  发送魔法链接（可选）
     Auth.signOut()           退出
     Auth.redeem(code)        兑换会员（服务端校验，返回结果对象）
     Auth.refreshMembership() 刷新会员状态
     Auth.getJobAccess(ids)   批量取会员专属数据（申请链接/内推联系方式）
     Auth.onChange(fn)        登录态/会员态变化订阅
   ============================================================ */

(function () {
  const cfg = window.SUPABASE_CONFIG || {};
  const DEV = () => !!cfg.DEV_ACTIVE;

  let client = null;
  if (cfg.URL && cfg.ANON_KEY && window.supabase && window.supabase.createClient) {
    client = window.supabase.createClient(cfg.URL, cfg.ANON_KEY, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
    });
  }

  const state = {
    user: null,          // { id, email }
    membership: null,    // { plan, expires_at, is_active }
    loading: true,
  };

  const listeners = [];
  const emit = () => listeners.forEach((fn) => { try { fn(state); } catch (e) {} });

  // ── 兑换结果错误码 → 中文提示 ──
  const ERROR_TEXT = {
    not_authenticated: '请先登录后再兑换',
    code_not_found: '兑换码不存在，请检查是否输错',
    code_disabled: '该兑换码已被停用，请联系卖家',
    code_expired: '兑换码已过期',
    code_already_used: '该兑换码已被其他账号使用',
    already_used_by_you: '你已经兑换过这个兑换码了',
    unknown: '兑换失败，请稍后重试',
  };

  // ── 本地模拟（仅 localhost，未配邮件服务时用来走通 UI）──
  const DEV_KEY_USER = 'junes_dev_user';
  const DEV_KEY_MEMBER = 'junes_dev_member';
  const DEV_KEY_USED = 'junes_dev_used_codes';

  const devRead = (k, def) => {
    try { return JSON.parse(localStorage.getItem(k)) ?? def; } catch { return def; }
  };
  const devWrite = (k, v) => localStorage.setItem(k, JSON.stringify(v));
  const devUsedCodes = () => new Set(devRead(DEV_KEY_USED, []));

  async function devLogin(email) {
    const user = devRead(DEV_KEY_USER, null) || { id: 'dev-' + Date.now(), email };
    user.email = email;
    devWrite(DEV_KEY_USER, user);
    state.user = user;
    const m = devRead(DEV_KEY_MEMBER, null);
    state.membership = m;
    state.loading = false;
    emit();
    return { ok: true };
  }

  async function devRedeem(code) {
    const used = devUsedCodes();
    const key = String(code || '').trim().toUpperCase();
    if (!key) return { ok: false, error: 'code_not_found' };
    if (used.has(key)) return { ok: false, error: 'already_used_by_you' };
    if (!/^JUNES(-[A-Z2-9]{4}){3}$/.test(key) && key.length < 8) {
      return { ok: false, error: 'code_not_found' };
    }
    used.add(key);
    devWrite(DEV_KEY_USED, [...used]);
    const base = state.membership?.expires_at ? new Date(state.membership.expires_at) : new Date();
    const exp = new Date(Math.max(base.getTime(), Date.now()) + 30 * 86400000);
    const m = { plan: 'monthly', expires_at: exp.toISOString(), is_active: true };
    devWrite(DEV_KEY_MEMBER, m);
    state.membership = m;
    emit();
    return { ok: true, plan: 'monthly', days: 30, expires_at: fmt(exp) };
  }

  const fmt = (d) => {
    const dt = typeof d === 'string' ? new Date(d) : d;
    if (!dt || isNaN(dt)) return '';
    const p = (n) => String(n).padStart(2, '0');
    return `${dt.getFullYear()}-${p(dt.getMonth() + 1)}-${p(dt.getDate())} ${p(dt.getHours())}:${p(dt.getMinutes())}`;
  };

  // ── 会员状态 ──
  async function refreshMembership() {
    if (DEV() && !client) {
      state.membership = devRead(DEV_KEY_MEMBER, null);
      return state.membership;
    }
    if (!client || !state.user) { state.membership = null; return null; }
    try {
      const { data, error } = await client.rpc('my_membership');
      if (error) throw error;
      state.membership = data && data[0] ? data[0] : null;
    } catch (e) {
      state.membership = null;
    }
    return state.membership;
  }

  // ── 初始化 ──
  async function init() {
    state.loading = true;
    try {
      if (DEV() && !client) {
        const u = devRead(DEV_KEY_USER, null);
        state.user = u;
        state.membership = devRead(DEV_KEY_MEMBER, null);
      } else if (client) {
        const { data } = await client.auth.getSession();
        if (data?.session?.user) {
          state.user = {
            id: data.session.user.id,
            email: data.session.user.email || '',
          };
          await refreshMembership();
        }
        client.auth.onAuthStateChange(async (_e, session) => {
          state.user = session?.user
            ? { id: session.user.id, email: session.user.email || '' }
            : null;
          if (state.user) await refreshMembership();
          else state.membership = null;
          emit();
        });
      }
    } finally {
      state.loading = false;
      emit();
    }
  }

  const Auth = {
    state,
    fmt,
    onChange(fn) { listeners.push(fn); return () => listeners.splice(listeners.indexOf(fn), 1); },
    isLoggedIn: () => !!state.user,
    isMember() {
      const m = state.membership;
      if (!m) return false;
      if (m.is_active === false) return false;
      if (!m.expires_at) return !!m.is_active;
      return new Date(m.expires_at).getTime() > Date.now();
    },
    get email() { return state.user?.email || ''; },
    // 保留 phone 访问器：老代码/后续加手机号绑定时不报错
    get phone() { return state.user?.phone || state.user?.email || ''; },
    get memberExpiresText() {
      const m = state.membership;
      if (!m || !m.expires_at) return '';
      return fmt(m.expires_at);
    },

    async init() { return init(); },

    // 邮箱验证码登录：输入邮箱 → 收 6 位码 → 回填即登录
    async sendOtp(email) {
      const e = normalizeEmail(email);
      if (!e) return { ok: false, error: '请输入正确的邮箱地址' };
      if (DEV() && !client) return devLogin(e);
      if (!client) return { ok: false, error: '未配置 Supabase，请填写 config.js' };
      const { error } = await client.auth.signInWithOtp({
        email: e,
        options: { shouldCreateUser: true },
      });
      if (error) return { ok: false, error: mapAuthError(error) };
      return { ok: true };
    },

    // 魔法链接登录（备用）：点击邮件里的链接直接回到站点完成登录
    // 线上用 redirectTo 指回 account.html，Supabase 客户端会自动接管 URL 里的 token
    async signInWithMagicLink(email) {
      const e = normalizeEmail(email);
      if (!e) return { ok: false, error: '请输入正确的邮箱地址' };
      if (DEV() && !client) return devLogin(e);
      if (!client) return { ok: false, error: '未配置 Supabase，请填写 config.js' };
      const { error } = await client.auth.signInWithOtp({
        email: e,
        options: {
          shouldCreateUser: true,
          emailRedirectTo: location.origin + '/account.html',
        },
      });
      if (error) return { ok: false, error: mapAuthError(error) };
      return { ok: true };
    },

    async verifyOtp(email, token) {
      if (!client) return { ok: false, error: '未配置 Supabase' };
      const { data, error } = await client.auth.verifyOtp({
        email: normalizeEmail(email),
        token: String(token || '').trim(),
        type: 'email',
      });
      if (error) return { ok: false, error: mapAuthError(error, true) };
      state.user = { id: data.user.id, email: data.user.email || '' };
      await refreshMembership();
      emit();
      return { ok: true };
    },

    async signOut() {
      if (DEV() && !client) {
        localStorage.removeItem(DEV_KEY_USER);
        localStorage.removeItem(DEV_KEY_MEMBER);
        state.user = null;
        state.membership = null;
        emit();
        return;
      }
      if (client) await client.auth.signOut();
      state.user = null;
      state.membership = null;
      emit();
    },

    async redeem(code) {
      if (DEV() && !client) return devRedeem(code);
      if (!client) return { ok: false, error: '未配置 Supabase' };
      const { data, error } = await client.rpc('redeem_code', { p_code: code });
      if (error) {
        // 兜底：万一唯一约束先抛出，也按"已被使用"处理
        if (/duplicate key|23505/i.test(error.message || '')) {
          return { ok: false, error: 'code_already_used' };
        }
        return { ok: false, error: 'unknown' };
      }
      const r = data || {};
      const result = r.ok
        ? { ok: true, plan: r.plan, days: r.days, expires_at: r.expires_at }
        : { ok: false, error: r.error || 'unknown' };
      if (result.ok) await refreshMembership();
      return result;
    },

    async refreshMembership() { const m = await refreshMembership(); emit(); return m; },

    // 批量取会员专属数据：返回 { [jobId]: {apply_url, contact, contact_type} }
    async getJobAccess(jobIds) {
      const ids = (jobIds || []).filter(Boolean);
      if (!ids.length) return {};
      if (DEV() && !client) {
        // 本地模拟：直接返回假数据，用来看 UI
        if (!Auth.isMember()) return {};
        return ids.reduce((acc, id) => {
          acc[id] = { apply_url: 'https://example.com/apply/' + id, contact: 'Telegram: @demo_contact', contact_type: 'telegram' };
          return acc;
        }, {});
      }
      if (!client || !Auth.isMember()) return {};
      const { data, error } = await client.rpc('get_job_access', { p_job_ids: ids });
      if (error) return {};
      return (data || []).reduce((acc, r) => { acc[r.job_id] = r; return acc; }, {});
    },

    errorText: (code) => ERROR_TEXT[code] || ERROR_TEXT.unknown,
  };

  // ── 邮箱规范化：去空格、统一小写 ──
  function normalizeEmail(raw) {
    const e = String(raw || '').trim().toLowerCase();
    if (!e) return '';
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) ? e : '';
  }

  // ── 常见邮箱错误 → 中文提示 ──
  // Supabase 内置邮件服务有发送频率限制（免费项目约每小时几封），
  // 上线前建议换成自定义 SMTP（Resend / 阿里云邮件推送等）
  const AUTH_ERROR_TEXT = {
    'over_email_send_rate_limit': '发送太频繁了，请稍等一会儿再试',
    'over_request_rate_limit': '操作过于频繁，请稍后再试',
    'otp_expired': '验证码已过期，请重新获取',
    'email_not_confirmed': '邮箱未验证，请点击邮件里的链接完成验证',
  };

  function mapAuthError(error, isVerify) {
    const msg = error?.message || '';
    const code = error?.code || error?.error_description || '';
    if (error && (error.code === 'otp_expired' || /expired/i.test(code))) {
      return AUTH_ERROR_TEXT.otp_expired;
    }
    if (/rate.?limit/i.test(code) || /rate.?limit/i.test(msg)) {
      return AUTH_ERROR_TEXT.over_email_send_rate_limit;
    }
    if (isVerify && /invalid|token/i.test(msg)) return '验证码不正确或已过期';
    for (const k of Object.keys(AUTH_ERROR_TEXT)) {
      if (code === k || msg.includes(k)) return AUTH_ERROR_TEXT[k];
    }
    return msg || '操作失败，请稍后重试';
  }

  Auth.normalizeEmail = normalizeEmail;

  window.Auth = Auth;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { Auth.init(); });
  } else {
    Auth.init();
  }
})();
