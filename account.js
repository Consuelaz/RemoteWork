/* 个人中心：登录 + 兑换码激活 */

(function () {
  const $ = (id) => document.getElementById(id);
  const cfg = window.SUPABASE_CONFIG || {};

  const el = {
    guestBox: $('guestBox'), userBox: $('userBox'),
    emailInput: $('emailInput'), sendCodeBtn: $('sendCodeBtn'),
    otpRow: $('otpRow'), otpInput: $('otpInput'), loginBtn: $('loginBtn'),
    loginMsg: $('loginMsg'),
    userEmail: $('userEmail'), memberStatus: $('memberStatus'),
    expireRow: $('expireRow'), memberExpire: $('memberExpire'), logoutBtn: $('logoutBtn'),
    redeemInput: $('redeemInput'), redeemBtn: $('redeemBtn'), redeemMsg: $('redeemMsg'),
    devTip: $('devTip'),
  };

  const isDev = () => !!(cfg.DEV_ACTIVE) && !(cfg.URL && cfg.ANON_KEY);

  const setMsg = (node, text, type) => {
    node.textContent = text || '';
    node.className = 'member-msg' + (type ? ` is-${type}` : '');
  };

  function render() {
    const A = window.Auth;
    if (!A) return;

    el.devTip.style.display = isDev() ? 'block' : 'none';

    if (A.isLoggedIn()) {
      el.guestBox.style.display = 'none';
      el.userBox.style.display = 'block';
      el.userEmail.textContent = A.email || '-';
      if (A.isMember()) {
        el.memberStatus.textContent = '✅ 会员生效中';
        el.memberStatus.className = 'is-member';
        el.expireRow.style.display = 'flex';
        el.memberExpire.textContent = A.memberExpiresText;
      } else {
        el.memberStatus.textContent = '未开通';
        el.memberStatus.className = '';
        el.expireRow.style.display = 'none';
      }
    } else {
      el.guestBox.style.display = 'block';
      el.userBox.style.display = 'none';
    }
  }

  // ── 发送邮箱验证码 ──
  el.sendCodeBtn.addEventListener('click', async () => {
    const A = window.Auth;
    const email = el.emailInput.value.trim();
    if (!email) return setMsg(el.loginMsg, '请输入邮箱', 'err');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
      return setMsg(el.loginMsg, '邮箱格式不正确', 'err');
    }

    el.sendCodeBtn.disabled = true;
    el.sendCodeBtn.textContent = '发送中...';
    const r = await A.sendOtp(email);
    el.sendCodeBtn.disabled = false;
    el.sendCodeBtn.textContent = '获取验证码';

    if (!r.ok) return setMsg(el.loginMsg, r.error || '发送失败', 'err');

    if (isDev()) {
      // 本地模拟：直接登录成功
      setMsg(el.loginMsg, '本地模拟模式：已直接登录', 'ok');
      render();
      return;
    }
    el.otpRow.style.display = 'flex';
    setMsg(el.loginMsg, '验证码已发送到邮箱，请查收（注意垃圾箱）', 'ok');
    el.otpInput.focus();
  });

  // ── 验证码登录 ──
  el.loginBtn.addEventListener('click', async () => {
    const A = window.Auth;
    const email = el.emailInput.value.trim();
    const token = el.otpInput.value.trim();
    if (!token) return setMsg(el.loginMsg, '请输入验证码', 'err');

    el.loginBtn.disabled = true;
    el.loginBtn.textContent = '登录中...';
    const r = await A.verifyOtp(email, token);
    el.loginBtn.disabled = false;
    el.loginBtn.textContent = '登录';

    if (!r.ok) return setMsg(el.loginMsg, r.error || '登录失败', 'err');
    setMsg(el.loginMsg, '', '');
    render();
  });

  el.otpInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') el.loginBtn.click();
  });

  // ── 兑换 ──
  el.redeemBtn.addEventListener('click', async () => {
    const A = window.Auth;
    const code = el.redeemInput.value.trim();
    if (!code) return setMsg(el.redeemMsg, '请输入兑换码', 'err');
    if (!A.isLoggedIn()) {
      setMsg(el.redeemMsg, '请先登录，兑换码要绑定到账号', 'err');
      el.emailInput.focus();
      return;
    }

    el.redeemBtn.disabled = true;
    el.redeemBtn.textContent = '激活中...';
    const r = await A.redeem(code);
    el.redeemBtn.disabled = false;
    el.redeemBtn.textContent = '激活会员';

    if (!r.ok) return setMsg(el.redeemMsg, A.errorText(r.error), 'err');

    el.redeemInput.value = '';
    setMsg(el.redeemMsg, `🎉 会员已开通，有效期至 ${r.expires_at || A.memberExpiresText}`, 'ok');
    render();
  });

  el.redeemInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') el.redeemBtn.click();
  });

  // ── 退出 ──
  el.logoutBtn.addEventListener('click', async () => {
    await window.Auth.signOut();
    el.otpRow.style.display = 'none';
    setMsg(el.loginMsg, '', '');
    setMsg(el.redeemMsg, '', '');
    render();
  });

  // ── 订阅状态 ──
  window.Auth.onChange(render);
  render();
})();
