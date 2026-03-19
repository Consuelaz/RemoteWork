// ============================================================
// Junes远程 · 核心交互逻辑
// 国内远程数据来自 jobs-mainlist.js（V2EX实时数据）
// 海外远程数据来自 jobs-global.js
// ============================================================

// 当前状态
let currentSource = 'cn';       // 'cn' | 'global'
let currentCategory = '全部';
let currentSearch = '';

// 各数据源的分类映射
const CATEGORIES_CN = ['全部','全栈开发','后端开发','前端开发','AI/算法','区块链','运营','多岗位','市场营销'];
const CATEGORIES_GLOBAL = ['全部','全栈开发','前端开发','后端开发','数据分析','产品经理','市场营销','UI/UX设计','运营','人力资源','技术/运营'];

// ── 获取当前数据集 ──
function getCurrentJobs() {
  return currentSource === 'cn' ? JOBS_MAINLIST : JOBS_GLOBAL;
}

// ── 切换国内/国外 ──
function switchSource(source) {
  currentSource = source;
  currentCategory = '全部';
  currentSearch = '';
  const input = document.getElementById('searchInput');
  if (input) input.value = '';

  // 更新 Tab 样式
  document.querySelectorAll('.source-tab').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + source).classList.add('active');

  // 更新标题
  const title = document.getElementById('sectionTitle');
  if (title) title.textContent = source === 'cn' ? '最新国内远程岗位' : '最新海外/国外远程岗位';

  // 更新来源说明
  const info = document.getElementById('sourceInfoText');
  if (info) {
    info.textContent = source === 'cn'
      ? '数据来源于网络 · 最近2个月真实岗位'
      : '数据来源于网络 · 最近2个月真实岗位';
  }

  // 重建分类标签
  buildCategoryTags();
  applyFilters();
}

// ── 构建分类标签 ──
function buildCategoryTags() {
  const container = document.getElementById('categoryTags');
  if (!container) return;
  const cats = currentSource === 'cn' ? CATEGORIES_CN : CATEGORIES_GLOBAL;

  // 过滤出实际有岗位的分类
  const jobs = getCurrentJobs();
  const availableCats = cats.filter(c => c === '全部' || jobs.some(j => j.category === c));

  container.innerHTML = availableCats.map(c =>
    `<button class="tag ${c === currentCategory ? 'active' : ''}" onclick="filterByCategory('${c}')">${c}</button>`
  ).join('');
}

// ── 渲染岗位列表 ──
function renderJobs(jobs) {
  const list = document.getElementById('jobList');
  const empty = document.getElementById('emptyState');
  if (!list) return;

  if (jobs.length === 0) {
    list.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }
  if (empty) empty.style.display = 'none';

  list.innerHTML = jobs.map(job => `
    <div class="job-card ${job.isFeatured ? 'featured' : ''}" onclick="openModal('${job.id}')">
      <div class="job-logo">${job.logo}</div>
      <div class="job-info">
        <div class="job-title">${job.title}</div>
        <div class="job-company">
          ${job.company}
          ${job.canRefer ? '<span class="job-source-badge" style="background:#fef3c7;color:#92400e;">🎯 可内推</span>' : ''}
        </div>
        <div class="job-meta-row">${job.location}</div>
        <div class="job-tags">
          <span class="job-tag primary-tag">${job.category}</span>
          ${job.tags.slice(0,3).map(t => `<span class="job-tag">${t}</span>`).join('')}
        </div>
      </div>
      <div class="job-right">
        <div class="job-salary">${job.salary}</div>
        ${job.isNew ? '<span class="job-new-badge">NEW</span>' : ''}
        <div class="job-date">${formatDate(job.date)}</div>
      </div>
    </div>
  `).join('');
}

// ── 分类筛选 ──
function filterByCategory(cat) {
  currentCategory = cat;
  document.querySelectorAll('.tag').forEach(el => el.classList.remove('active'));
  [...document.querySelectorAll('.tag')].find(el => el.textContent.trim() === cat)?.classList.add('active');
  applyFilters();
}

// ── 搜索筛选 ──
function filterJobs() {
  currentSearch = document.getElementById('searchInput')?.value.trim().toLowerCase() || '';
  applyFilters();
}

// ── 综合筛选 ──
function applyFilters() {
  let filtered = getCurrentJobs();

  if (currentCategory !== '全部') {
    filtered = filtered.filter(j => j.category === currentCategory);
  }
  if (currentSearch) {
    filtered = filtered.filter(j =>
      j.title.toLowerCase().includes(currentSearch) ||
      j.company.toLowerCase().includes(currentSearch) ||
      (j.tags || []).some(t => t.toLowerCase().includes(currentSearch)) ||
      j.category.toLowerCase().includes(currentSearch) ||
      (j.description || '').toLowerCase().includes(currentSearch)
    );
  }

  renderJobs(filtered);
}

// ── 日期格式化 ──
function formatDate(dateStr) {
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - d) / 86400000);
  if (diff === 0) return '今天发布';
  if (diff === 1) return '昨天发布';
  if (diff <= 7) return `${diff}天前`;
  return `${d.getMonth() + 1}月${d.getDate()}日`;
}

// ── 弹窗详情 ──
function openModal(id) {
  const allJobs = [...JOBS_MAINLIST, ...JOBS_GLOBAL];
  const job = allJobs.find(j => j.id === id);
  if (!job) return;

  const sourceLabel = currentSource === 'global'
    ? `<span class="global-badge">🌍 海外岗位</span>` : '';
  const referBadge = job.canRefer
    ? `<span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:12px;margin-left:8px;">🎯 可内推</span>`
    : '';

  const content = document.getElementById('modalContent');
  content.innerHTML = `
    <div class="modal-logo">${job.logo}</div>
    <div class="modal-title">${job.title} ${sourceLabel} ${referBadge}</div>
    <div class="modal-company">${job.company}</div>
    <div style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
      📍 ${job.location}
    </div>
    <div class="modal-tags">
      <span class="job-tag primary-tag">${job.category}</span>
      ${(job.tags || []).map(t => `<span class="job-tag">${t}</span>`).join('')}
    </div>
    <div class="modal-salary-big">${job.salary}</div>

    <div class="modal-section">
      <h4>岗位描述</h4>
      <p>${job.description}</p>
    </div>

    ${job.requirements && job.requirements.length ? `
    <div class="modal-section">
      <h4>任职要求</h4>
      <ul>${job.requirements.map(r => `<li>${r}</li>`).join('')}</ul>
    </div>` : ''}

    ${job.benefits && job.benefits.length ? `
    <div class="modal-section">
      <h4>福利待遇</h4>
      <div class="job-tags" style="margin-top:4px">
        ${job.benefits.map(b => `<span class="job-tag">${b}</span>`).join('')}
      </div>
    </div>` : ''}

    <div class="modal-actions">
      <a href="${job.sourceUrl}" target="_blank" class="btn btn-primary">查看原帖投递 →</a>
      <button class="btn btn-outline" onclick="closeModal()">关闭</button>
    </div>
  `;
  document.getElementById('modalOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.body.style.overflow = '';
}

// ── 订阅 ──
function handleSubscribe(e) {
  e.preventDefault();
  const email = e.target.querySelector('input').value;
  alert(`✅ 订阅成功！\n\n我们会将新岗位信息发送到 ${email}，请注意查收。`);
  e.target.reset();
}

// ── 更新统计数字 ──
function updateStats() {
  const total = JOBS_MAINLIST.length + JOBS_GLOBAL.length;
  const cnNew = JOBS_MAINLIST.filter(j => j.isNew).length;
  const globalNew = JOBS_GLOBAL.filter(j => j.isNew).length;

  const el = document.getElementById('totalJobCount');
  if (el) el.textContent = total;
  const cnEl = document.getElementById('cnJobCount');
  if (cnEl) cnEl.textContent = JOBS_MAINLIST.length;
  const globalEl = document.getElementById('globalJobCount');
  if (globalEl) globalEl.textContent = JOBS_GLOBAL.length;

  // 更新时间
  const timeEl = document.getElementById('sourceUpdateTime');
  if (timeEl) timeEl.textContent = `· 更新于 2026-03-19`;
}

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', () => {
  updateStats();
  buildCategoryTags();
  applyFilters();
});
