/* 个人中心：登录 + 兑换码激活 */

(function () {
  const $ = (id) => document.getElementById(id);
  const cfg = window.SUPABASE_CONFIG || {};

  const el = {
    guestBox: $('guestBox'), userBox: $('userBox'),
    emailInput: $('emailInput'), sendLinkBtn: $('sendLinkBtn'),
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

  // ── 发送邮箱登录链接 ──
  el.sendLinkBtn.addEventListener('click', async () => {
    const A = window.Auth;
    const email = el.emailInput.value.trim();
    if (!email) return setMsg(el.loginMsg, '请输入邮箱', 'err');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
      return setMsg(el.loginMsg, '邮箱格式不正确', 'err');
    }

    el.sendLinkBtn.disabled = true;
    el.sendLinkBtn.textContent = '发送中...';
    const r = await A.sendLoginLink(email);
    el.sendLinkBtn.disabled = false;
    el.sendLinkBtn.textContent = '发送登录链接';

    if (!r.ok) return setMsg(el.loginMsg, r.error || '发送失败', 'err');

    if (isDev()) {
      // 本地模拟：直接登录成功
      setMsg(el.loginMsg, '本地模拟模式：已直接登录', 'ok');
      render();
      return;
    }
    setMsg(el.loginMsg, '登录链接已发送到邮箱，请查收邮件并点击链接完成登录（注意垃圾箱）', 'ok');
  });

  el.emailInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') el.sendLinkBtn.click();
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
    setMsg(el.loginMsg, '', '');
    setMsg(el.redeemMsg, '', '');
    render();
  });

  // ── 订阅状态 ──
  window.Auth.onChange(render);
  render();
})();
