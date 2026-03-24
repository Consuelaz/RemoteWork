// ============================================================
// Junes远程 · 核心交互逻辑
// 国内远程数据来自 jobs-mainlist.js（V2EX实时数据）
// 海外远程数据来自 jobs-global.js
// ============================================================

// 当前状态
let currentSource = 'cn';       // 'cn' | 'global'
let currentCategory = '全部';
let currentSearch = '';
let currentPage = 1;
const PAGE_SIZE = 10;
let filteredJobsCache = []; // 缓存过滤后的职位

// 各数据源的分类映射
const CATEGORIES_CN = ['全部','全栈开发','后端开发','前端开发','AI/算法','区块链','运营','多岗位','市场营销'];
const CATEGORIES_GLOBAL = ['全部','全栈开发','前端开发','后端开发','数据分析','产品经理','市场营销','UI/UX设计','运营','人力资源','技术/运营'];

// ── 通用工具函数 ──
// 截断过长标题
const truncateTitle = (title, maxLen = 28) => {
  return title.length > maxLen ? title.substring(0, maxLen) + '...' : title;
};

// 处理公司名显示 - 不显示V2EX相关内容
const formatCompany = (company) => {
  if (!company || company === '（V2EX用户招聘）') return '';
  if (company.length > 20) return company.substring(0, 20) + '...';
  return company;
};

// ── 获取当前数据集 ──
function getCurrentJobs() {
  if (currentSource === 'cn') {
    // 合并手动维护的精选岗位 + 自动抓取的 CN 岗位
    const mainList = (typeof JOBS_MAINLIST !== 'undefined') ? JOBS_MAINLIST : [];
    const cnList   = (typeof JOBS_CN      !== 'undefined') ? JOBS_CN      : [];
    // 用 id 去重
    const seen = new Set(mainList.map(j => j.id));
    const unique = cnList.filter(j => !seen.has(j.id));
    // 合并后按日期倒序排列（最新的在前）
    const allJobs = [...mainList, ...unique];
    return allJobs.sort((a, b) => new Date(b.date) - new Date(a.date));
  }
  // 海外岗位也按日期倒序
  const globalList = (typeof JOBS_GLOBAL !== 'undefined') ? JOBS_GLOBAL : [];
  return globalList.sort((a, b) => new Date(b.date) - new Date(a.date));
}

// ── 切换国内/国外 ──
function switchSource(source) {
  currentSource = source;
  currentCategory = '全部';
  currentSearch = '';
  currentPage = 1;
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

  const jobs = getCurrentJobs();

  // 优先用预设顺序，再补充数据里实际有的分类
  const presetOrder = currentSource === 'cn' ? CATEGORIES_CN : CATEGORIES_GLOBAL;
  const actualCats = [...new Set(jobs.map(j => j.category).filter(Boolean))];

  // 合并：预设在前（过滤掉无数据的），再追加预设里没有的实际分类
  const merged = ['全部',
    ...presetOrder.filter(c => c !== '全部' && actualCats.includes(c)),
    ...actualCats.filter(c => !presetOrder.includes(c))
  ];

  container.innerHTML = merged.map(c =>
    `<button class="tag ${c === currentCategory ? 'active' : ''}" onclick="filterByCategory('${c}')">${c}</button>`
  ).join('');
}

// ── 渲染岗位列表 ──
function renderJobs(jobs) {
  const list = document.getElementById('jobList');
  const empty = document.getElementById('emptyState');
  const pagination = document.getElementById('pagination');
  if (!list) return;

  if (jobs.length === 0) {
    list.innerHTML = '';
    if (empty) empty.style.display = 'block';
    if (pagination) pagination.style.display = 'none';
    return;
  }
  if (empty) empty.style.display = 'none';

  // 分页：只渲染当前页的数据
  const start = (currentPage - 1) * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const pageJobs = jobs.slice(start, end);

  list.innerHTML = pageJobs.map(job => `
    <div class="job-card ${job.isFeatured ? 'featured' : ''}" onclick="openModal('${job.id}')">
      <div class="job-logo">${job.logo}</div>
      <div class="job-info">
        <div class="job-title">${truncateTitle(job.title)}</div>
        <div class="job-company">
          ${formatCompany(job.company)}
          ${job.canRefer ? '<span class="job-source-badge" style="background:#dbeafe;color:#1e40af;">👥 内推岗</span>' : ''}
        </div>
        <div class="job-meta-row">${job.location}</div>
        <div class="job-tags">
          <span class="job-tag primary-tag">${job.category}</span>
          ${job.tags.filter(t => !['V2EX', '远程', '社群内推'].includes(t)).slice(0,2).map(t => `<span class="job-tag">${t}</span>`).join('')}
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

// ── 渲染分页 ──
function renderPagination() {
  const pagination = document.getElementById('pagination');
  const pageInfo = document.getElementById('pageInfo');
  const prevBtn = document.getElementById('prevPage');
  const nextBtn = document.getElementById('nextPage');
  if (!pagination) return;

  const totalPages = Math.ceil(filteredJobsCache.length / PAGE_SIZE);

  if (totalPages <= 1) {
    pagination.style.display = 'none';
    return;
  }

  pagination.style.display = 'flex';
  if (pageInfo) pageInfo.textContent = `${currentPage} / ${totalPages}`;
  if (prevBtn) prevBtn.disabled = currentPage <= 1;
  if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
}

// ── 上一页 ──
function prevPage() {
  if (currentPage <= 1) return;
  currentPage--;
  renderJobs(filteredJobsCache);
  renderPagination();
  scrollToJobList();
}

// ── 下一页 ──
function nextPage() {
  const totalPages = Math.ceil(filteredJobsCache.length / PAGE_SIZE);
  if (currentPage >= totalPages) return;
  currentPage++;
  renderJobs(filteredJobsCache);
  renderPagination();
  scrollToJobList();
}

// ── 滚动到列表顶部 ──
function scrollToJobList() {
  const jobsSection = document.getElementById('jobs');
  if (jobsSection) {
    jobsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
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

  // 缓存过滤结果，重置到第一页
  filteredJobsCache = filtered;
  currentPage = 1;

  renderJobs(filtered);
  renderPagination();
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
  const mainList   = (typeof JOBS_MAINLIST !== 'undefined') ? JOBS_MAINLIST : [];
  const cnList     = (typeof JOBS_CN       !== 'undefined') ? JOBS_CN       : [];
  const globalList = (typeof JOBS_GLOBAL   !== 'undefined') ? JOBS_GLOBAL   : [];
  const allJobs = [...mainList, ...cnList, ...globalList];
  const job = allJobs.find(j => j.id === id);
  if (!job) return;

  const sourceLabel = currentSource === 'global'
    ? `<span class="global-badge">🌍 海外岗位</span>` : '';
  const referBadge = job.canRefer
    ? `<span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:12px;margin-left:8px;">👥 内推岗</span>`
    : '';

  // 详情页标题截断处理
  const modalTitle = job.title.length > 50 ? job.title.substring(0, 50) + '...' : job.title;
  
  // 处理公司名显示 - 详情页也用相同逻辑
  const modalCompany = formatCompany(job.company);
  
  // 处理描述：如果是无意义的默认描述，则用标题替代
  const validDescription = (job.description && 
    job.description !== '来自V2EX远程工作社区的招聘帖子' && 
    job.description.length > 10) 
    ? job.description 
    : job.title;
  
  const content = document.getElementById('modalContent');
  // 过滤掉不需要展示的标签
  const filteredTags = (job.tags || []).filter(t => !['V2EX', '远程', '社群内推'].includes(t));
  content.innerHTML = `
    <div class="modal-logo">${job.logo}</div>
    <div class="modal-title">${modalTitle} ${sourceLabel} ${referBadge}</div>
    <div class="modal-company">${modalCompany}</div>
    <div style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
      📍 ${job.location} ${job.work_style ? '| ' + job.work_style : ''}
    </div>
    <div class="modal-tags">
      <span class="job-tag primary-tag">${job.category}</span>
      ${filteredTags.map(t => `<span class="job-tag">${t}</span>`).join('')}
    </div>
    <div class="modal-salary-big">${job.salary}</div>

    ${job.company_info && job.company_info.length > 10 ? `
    <div class="modal-section">
      <h4>公司介绍</h4>
      <p>${job.company_info}</p>
    </div>` : ''}

    ${validDescription ? `
    <div class="modal-section">
      <h4>岗位描述</h4>
      <p>${validDescription}</p>
    </div>` : ''}

    ${job.responsibilities && job.responsibilities.length ? `
    <div class="modal-section">
      <h4>岗位职责</h4>
      <ul>${job.responsibilities.map(r => `<li>${r}</li>`).join('')}</ul>
    </div>` : ''}

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
      ${job.canRefer 
        ? '<a href="community.html" target="_blank" class="btn btn-primary">加入社群内推 →</a>'
        : `<a href="${job.applyUrl || job.sourceUrl}" target="_blank" class="btn btn-primary">${job.applyUrl ? '申请职位 →' : '查看原帖投递 →'}</a>`
      }
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
  const mainList = (typeof JOBS_MAINLIST !== 'undefined') ? JOBS_MAINLIST : [];
  const cnList   = (typeof JOBS_CN      !== 'undefined') ? JOBS_CN      : [];
  const globalList = (typeof JOBS_GLOBAL !== 'undefined') ? JOBS_GLOBAL : [];

  // CN 去重合并
  const seen = new Set(mainList.map(j => j.id));
  const allCN = [...mainList, ...cnList.filter(j => !seen.has(j.id))];

  const total = allCN.length + globalList.length;

  const el = document.getElementById('totalJobCount');
  if (el) el.textContent = total;
  const cnEl = document.getElementById('cnJobCount');
  if (cnEl) cnEl.textContent = allCN.length;
  const globalEl = document.getElementById('globalJobCount');
  if (globalEl) globalEl.textContent = globalList.length;

  // 更新时间 - 使用最新岗位的日期
  const allJobsSorted = [...allCN, ...globalList].sort((a, b) => new Date(b.date) - new Date(a.date));
  const latestDate = allJobsSorted[0]?.date || '';
  const timeEl = document.getElementById('sourceUpdateTime');
  if (timeEl && latestDate) timeEl.textContent = `· 更新于 ${latestDate}`;
}

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', () => {
  console.log('🔍 页面初始化开始');
  console.log('📊 数据源检查:');
  console.log('  JOBS_MAINLIST:', typeof JOBS_MAINLIST !== 'undefined' ? JOBS_MAINLIST.length : 0, '条');
  console.log('  JOBS_CN:', typeof JOBS_CN !== 'undefined' ? JOBS_CN.length : 0, '条');
  console.log('  JOBS_GLOBAL:', typeof JOBS_GLOBAL !== 'undefined' ? JOBS_GLOBAL.length : 0, '条');
  
  const cnJobs = getCurrentJobs();
  console.log('✅ CN 模式合并后:', cnJobs.length, '条');
  
  updateStats();
  buildCategoryTags();
  applyFilters();
});
