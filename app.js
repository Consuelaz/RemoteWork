// ============================================================
// Junes远程 · 核心交互逻辑
// 国内远程数据来自 jobs-mainlist.js（V2EX实时数据）
// 海外远程数据来自 jobs-global.js
// ============================================================

// 当前状态
let currentSource = 'cn';       // 'cn' | 'global'
let currentCategory = '全部';
let currentSearch = '';
let currentReferOnly = false;  // 是否只显示内推岗（仅国内 Tab 生效）
let currentPage = 1;
const PAGE_SIZE = 20;
let filteredJobsCache = []; // 缓存过滤后的职位

// 各数据源的分类映射
const CATEGORIES_CN = ['全部','全栈开发','后端开发','前端开发','AI/算法','区块链','运营','多岗位','市场营销'];
const CATEGORIES_GLOBAL = ['全部','全栈开发','前端开发','后端开发','数据分析','产品经理','市场营销','UI/UX设计','运营','人力资源','技术/运营'];

// ── 通用工具函数 ──
// 截断过长标题
const truncateTitle = (title, maxLen = 28) => {
  return title.length > maxLen ? title.substring(0, maxLen) + '...' : title;
};

// 处理公司名显示 - 过滤数据源网站名称等无意义内容
const INVALID_COMPANY_NAMES = ['（V2EX用户招聘）', '远程中文网', 'Remote China', 'remote-china'];
const formatCompany = (company) => {
  if (!company) return '';
  if (INVALID_COMPANY_NAMES.some(n => company.includes(n))) return '';
  if (company.length > 20) return company.substring(0, 20) + '...';
  return company;
};

// ── 获取当前数据集 ──
// 排序策略：所有岗位统一按日期倒序
// ── 每日精选 ──
// 精选岗是手动维护的（jobs-featured.js），会员可解锁申请链接与内推人联系方式。
// 这些岗位只在精选板块出现，普通列表里会被排除——否则用户从普通列表点开
// 就能看到申请链接，付费墙形同虚设。
const FEATURED_WINDOW_DAYS = 7;   // 精选板块展示窗口：最近 N 天
const FEATURED_PREVIEW = 6;       // 默认展示条数，其余折叠
let featuredShowAll = false;

const getFeaturedList = () => (typeof JOBS_FEATURED !== 'undefined') ? JOBS_FEATURED : [];
const featuredIdSet = () => new Set(getFeaturedList().map(j => j.id));
const isFeaturedJob = (job) => !!job && featuredIdSet().has(job.id);

// 精选板块要展示的岗位：优先最近 FEATURED_WINDOW_DAYS 天；
// 窗口内没有则退回最新的 FEATURED_PREVIEW 条，避免板块空白
function getFeaturedJobs() {
  const list = [...getFeaturedList()].sort((a, b) => new Date(b.date) - new Date(a.date));
  if (!list.length) return [];
  const cutoff = Date.now() - FEATURED_WINDOW_DAYS * 86400000;
  const recent = list.filter(j => new Date(j.date).getTime() >= cutoff);
  return recent.length ? recent : list.slice(0, FEATURED_PREVIEW);
}

function getCurrentJobs() {
  const featuredIds = featuredIdSet();
  if (currentSource === 'cn') {
    const mainList = (typeof JOBS_MAINLIST !== 'undefined') ? JOBS_MAINLIST : [];
    const cnList   = (typeof JOBS_CN      !== 'undefined') ? JOBS_CN      : [];
    const seen = new Set(mainList.map(j => j.id));
    const unique = cnList.filter(j => !seen.has(j.id) && !featuredIds.has(j.id));
    const allJobs = [...mainList.filter(j => !featuredIds.has(j.id)), ...unique];
    return allJobs.sort((a, b) => new Date(b.date) - new Date(a.date));
  }
  const globalList = (typeof JOBS_GLOBAL !== 'undefined') ? JOBS_GLOBAL : [];
  return globalList
    .filter(j => !featuredIds.has(j.id))
    .sort((a, b) => new Date(b.date) - new Date(a.date));
}

// ── 切换国内/国外 ──
function switchSource(source) {
  currentSource = source;
  currentCategory = '全部';
  currentSearch = '';
  currentReferOnly = false;
  currentPage = 1;
  const input = document.getElementById('searchInput');
  if (input) input.value = '';

  // 更新 Tab 样式
  document.querySelectorAll('.source-tab').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + source).classList.add('active');

  // 更新标题
  const title = document.getElementById('sectionTitle');
  if (title) title.textContent = source === 'cn' ? '最新国内远程岗位' : '🌏 海外远程岗位（华人友好）';

  // 切换布局显示
  const cnLayout = document.getElementById('jobList');
  const globalLayout = document.getElementById('globalLayout');
  const categoryTags = document.getElementById('categoryTags');
  
  if (source === 'global') {
    // 海外模式
    if (cnLayout) cnLayout.style.display = 'none';
    if (globalLayout) globalLayout.style.display = 'block';
    if (categoryTags) categoryTags.style.display = 'flex';
    // 重建分类标签（海外）
    buildCategoryTags();
    applyFilters();
  } else {
    // 国内模式：显示原有布局
    if (cnLayout) cnLayout.style.display = 'grid';
    if (globalLayout) globalLayout.style.display = 'none';
    if (categoryTags) categoryTags.style.display = 'flex';
    // 重建分类标签
    buildCategoryTags();
    applyFilters();
  }
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

  // 国内 Tab：在最前面插入「内推岗」快捷筛选按钮
  let tags = '';
  if (currentSource === 'cn') {
    const referCount = jobs.filter(j => j.canRefer).length;
    if (referCount > 0) {
      tags += `<button class="tag tag-refer ${currentReferOnly ? 'active' : ''}" onclick="toggleReferOnly()">
        <svg class="refer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        内推岗 <span class="tag-count">${referCount}</span>
      </button>`;
    }
  }

  tags += merged.map(c =>
    `<button class="tag ${c === currentCategory && !currentReferOnly ? 'active' : ''}" onclick="filterByCategory('${c}')">${c}</button>`
  ).join('');

  container.innerHTML = tags;
}

// ── 切换内推岗筛选（国内 Tab 专用） ──
function toggleReferOnly() {
  currentReferOnly = !currentReferOnly;
  if (currentReferOnly) {
    // 切到内推筛选时，取消具体分类的高亮，保持「全部」高亮
    currentCategory = '全部';
  }
  buildCategoryTags();
  applyFilters();
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

  // 使用与海外岗位一致的列表卡片样式
  list.innerHTML = pageJobs.map(job => {
    const postedTime = formatTimeAgo(job.date);
    // 提取地点信息
    const locationParts = job.location ? job.location.split(/[,，]/) : [''];
    const cityCountry = locationParts.length > 1 
      ? `${locationParts[0].trim()}, ${locationParts[1].trim()}`
      : job.location || '远程';
    
    return `
    <div class="global-job-card ${job.isFeatured ? 'featured' : ''}" onclick="openModal('${job.id}')" style="cursor: pointer;">
      <div class="global-job-header">
        <div class="global-job-logo">
          ${job.logo && job.logo.startsWith('http') 
            ? `<img src="${job.logo}" alt="${job.company}">` 
            : `<div class="logo-placeholder"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><path d="M2 12h20"></path><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg></div>`}
        </div>
        <div class="global-job-info">
          <div class="global-job-title">${job.title}</div>
          <div class="global-job-company-row">
            <span class="company-name">${formatCompany(job.company)}</span>
            ${job.canRefer ? '<span class="job-source-badge refer-badge"><svg class="refer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>内推岗</span>' : ''}
            <span class="location">📍 ${cityCountry}</span>
          </div>
        </div>
        <div class="global-job-time">${postedTime}</div>
      </div>
    </div>
  `}).join('');
}

// ── 渲染「每日精选」板块 ──
function renderFeatured() {
  const section = document.getElementById('featuredSection');
  const list = document.getElementById('featuredList');
  if (!section || !list) return;

  const jobs = getFeaturedJobs();
  if (!jobs.length) { section.style.display = 'none'; return; }
  section.style.display = 'block';

  const subtitle = document.getElementById('featuredSubtitle');
  if (subtitle) {
    subtitle.textContent = '每天人工筛选，含内推岗与直申岗 · 点开岗位查看详情';
  }

  const shown = featuredShowAll ? jobs : jobs.slice(0, FEATURED_PREVIEW);

  list.innerHTML = shown.map(job => `
    <div class="featured-card" onclick="openModal('${job.id}')">
      <div class="featured-card-head">
        <span class="featured-logo">${job.logo || '💼'}</span>
        <div class="featured-main">
          <div class="featured-job-title">${job.title}</div>
          <div class="featured-job-meta">
            <span class="f-company">${formatCompany(job.company)}</span>
            <span class="f-loc">📍 ${job.location || '远程'}</span>
            <span class="f-salary">${job.salary || '面议'}</span>
          </div>
        </div>
        <div class="featured-right">
          ${job.canRefer
            ? '<span class="featured-tag refer">内推岗</span>'
            : '<span class="featured-tag direct">直申岗</span>'}
        </div>
      </div>
      <div class="featured-foot">
        <span class="featured-date">${formatTimeAgo(job.date)}</span>
        <span class="featured-cat">${job.category || ''}</span>
      </div>
    </div>
  `).join('');

  const moreBtn = document.getElementById('featuredMore');
  const moreText = document.getElementById('featuredMoreText');
  const moreCount = document.getElementById('featuredMoreCount');
  if (moreBtn && jobs.length > FEATURED_PREVIEW) {
    moreBtn.style.display = 'inline-flex';
    if (moreText) moreText.textContent = featuredShowAll ? '收起' : '查看全部精选';
    if (moreCount) moreCount.textContent = featuredShowAll ? '' : `（还有 ${jobs.length - FEATURED_PREVIEW} 条）`;
  } else if (moreBtn) {
    moreBtn.style.display = 'none';
  }
}

function toggleFeaturedAll() {
  featuredShowAll = !featuredShowAll;
  renderFeatured();
}

// ── 海外岗位：构建筛选器 ──
function buildGlobalFilters() {
  const jobs = getCurrentJobs();
  
  // 提取所有地点
  const locations = [...new Set(jobs.map(j => j.companyCountry).filter(Boolean))];
  const locationContainer = document.getElementById('locationFilters');
  if (locationContainer) {
    locationContainer.innerHTML = `
      <label class="filter-option"><input type="checkbox" value="all" checked onchange="applyGlobalFilters()"> 不限</label>
      ${locations.map(loc => `<label class="filter-option"><input type="checkbox" value="${loc}" onchange="applyGlobalFilters()"> ${loc}</label>`).join('')}
    `;
  }
  
  // 提取所有分类
  const categories = [...new Set(jobs.map(j => j.category).filter(Boolean))];
  const categoryContainer = document.getElementById('categoryFilters');
  if (categoryContainer) {
    categoryContainer.innerHTML = `
      <label class="filter-option"><input type="checkbox" value="all" checked onchange="applyGlobalFilters()"> 不限</label>
      ${categories.map(cat => `<label class="filter-option"><input type="checkbox" value="${cat}" onchange="applyGlobalFilters()"> ${cat}</label>`).join('')}
    `;
  }
}

// ── 海外岗位：应用筛选 ──
function applyGlobalFilters() {
  let jobs = getCurrentJobs();
  
  // 获取选中的地点
  const locationCheckboxes = document.querySelectorAll('#locationFilters input:checked');
  const selectedLocations = Array.from(locationCheckboxes).map(cb => cb.value);
  if (!selectedLocations.includes('all') && selectedLocations.length > 0) {
    jobs = jobs.filter(j => selectedLocations.includes(j.companyCountry));
  }
  
  // 获取选中的薪资范围
  const salaryCheckboxes = document.querySelectorAll('#salaryFilters input:checked');
  const selectedSalary = Array.from(salaryCheckboxes).map(cb => cb.value);
  if (!selectedSalary.includes('all') && selectedSalary.length > 0) {
    jobs = jobs.filter(j => {
      const salary = j.salary || '';
      // 简单匹配薪资范围
      if (selectedSalary.includes('0-20') && (salary.includes('面议') || salary.match(/\d+/))) return true;
      if (selectedSalary.includes('20-50') && salary.match(/[2-4]\d/)) return true;
      if (selectedSalary.includes('50-100') && salary.match(/[5-9]\d/)) return true;
      if (selectedSalary.includes('100+') && salary.match(/1\d{2}/)) return true;
      return selectedSalary.includes('all');
    });
  }
  
  // 获取选中的分类
  const categoryCheckboxes = document.querySelectorAll('#categoryFilters input:checked');
  const selectedCategories = Array.from(categoryCheckboxes).map(cb => cb.value);
  if (!selectedCategories.includes('all') && selectedCategories.length > 0) {
    jobs = jobs.filter(j => selectedCategories.includes(j.category));
  }
  
  // 搜索过滤
  if (currentSearch) {
    const keyword = currentSearch.toLowerCase();
    jobs = jobs.filter(j => 
      j.title.toLowerCase().includes(keyword) || 
      j.company.toLowerCase().includes(keyword) ||
      (j.tags && j.tags.some(t => t.toLowerCase().includes(keyword)))
    );
  }
  
  filteredJobsCache = jobs;
  renderGlobalJobs(jobs);
}

// ── 海外岗位：渲染职位列表 ──
function renderGlobalJobs(jobs) {
  const list = document.getElementById('globalJobList');
  if (!list) return;
  
  if (jobs.length === 0) {
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>没有找到相关岗位，试试调整筛选条件~</p></div>';
    return;
  }
  
  // 分页
  const start = (currentPage - 1) * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const pageJobs = jobs.slice(start, end);
  
  list.innerHTML = pageJobs.map(job => {
    const postedTime = formatTimeAgo(job.date);
    // 提取国家和城市信息
    const locationParts = job.location ? job.location.split(/[,，]/) : [''];
    const cityCountry = locationParts.length > 1 
      ? `${locationParts[0].trim()}, ${locationParts[1].trim()}`
      : job.location || '全球远程';
    
    return `
    <div class="global-job-card" onclick="openModal('${job.id}')" style="cursor: pointer;">
      <div class="global-job-header">
        <div class="global-job-logo">
          ${job.logo && job.logo.startsWith('http') 
            ? `<img src="${job.logo}" alt="${job.company}">` 
            : `<div class="logo-placeholder"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><path d="M2 12h20"></path><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg></div>`}
        </div>
        <div class="global-job-info">
          <div class="global-job-title">${job.title}</div>
          <div class="global-job-company-row">
            <span class="company-name">${job.company}</span>
            <span class="location">📍 ${cityCountry}</span>
          </div>
        </div>
        <div class="global-job-time">${postedTime}</div>
      </div>
    </div>
  `}).join('');
  
  // 更新分页
  renderGlobalPagination();
}

// ── 海外岗位：渲染分页 ──
function renderGlobalPagination() {
  const totalPages = Math.ceil(filteredJobsCache.length / PAGE_SIZE);
  const pagination = document.getElementById('pagination');
  const pageInfo = document.getElementById('pageInfo');
  const prevBtn = document.getElementById('prevPage');
  const nextBtn = document.getElementById('nextPage');
  
  if (!pagination) return;
  
  if (totalPages <= 1) {
    pagination.style.display = 'none';
    return;
  }
  
  pagination.style.display = 'flex';
  if (pageInfo) pageInfo.textContent = `${currentPage} / ${totalPages}`;
  if (prevBtn) prevBtn.disabled = currentPage <= 1;
  if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
}

// ── 格式化相对时间 ──
function formatTimeAgo(dateStr) {
  if (!dateStr) return '未知时间';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) return '今天';
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  if (days < 30) return `${Math.floor(days / 7)}周前`;
  return `${Math.floor(days / 30)}个月前`;
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
  if (currentSource === 'global') {
    renderGlobalJobs(filteredJobsCache);
    renderGlobalPagination();
  } else {
    renderJobs(filteredJobsCache);
    renderPagination();
  }
  scrollToJobList();
}

// ── 下一页 ──
function nextPage() {
  const totalPages = Math.ceil(filteredJobsCache.length / PAGE_SIZE);
  if (currentPage >= totalPages) return;
  currentPage++;
  if (currentSource === 'global') {
    renderGlobalJobs(filteredJobsCache);
    renderGlobalPagination();
  } else {
    renderJobs(filteredJobsCache);
    renderPagination();
  }
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
  currentReferOnly = false;  // 切换具体分类时清掉内推快捷筛选
  buildCategoryTags();
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

  if (currentReferOnly && currentSource === 'cn') {
    filtered = filtered.filter(j => j.canRefer);
  }

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

  // 根据当前模式选择渲染函数
  if (currentSource === 'global') {
    renderGlobalJobs(filtered);
    renderGlobalPagination();
  } else {
    renderJobs(filtered);
    renderPagination();
  }
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
  const featuredList = (typeof JOBS_FEATURED !== 'undefined') ? JOBS_FEATURED : [];
  const mainList   = (typeof JOBS_MAINLIST !== 'undefined') ? JOBS_MAINLIST : [];
  const cnList     = (typeof JOBS_CN       !== 'undefined') ? JOBS_CN       : [];
  const globalList = (typeof JOBS_GLOBAL   !== 'undefined') ? JOBS_GLOBAL   : [];
  const allJobs = [...featuredList, ...mainList, ...cnList, ...globalList];
  const job = allJobs.find(j => j.id === id);
  if (!job) return;

  const featured = isFeaturedJob(job);
  const sourceLabel = currentSource === 'global'
    ? `<span class="global-badge">🌍 海外岗位</span>` : '';
  const featuredBadge = featured
    ? `<span class="featured-badge-inline">每日精选</span>` : '';
  const referBadge = job.canRefer
    ? `<span class="refer-badge" style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:12px;margin-left:8px;display:inline-flex;align-items:center;gap:4px;"><svg class="refer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>内推岗</span>`
    : '';

  // 详情页标题截断处理
  const modalTitle = job.title.length > 50 ? job.title.substring(0, 50) + '...' : job.title;
  
  // 处理公司名显示 - 详情页也用相同逻辑
  const modalCompany = formatCompany(job.company);
  
  // 处理描述：过滤无意义的默认描述（数据源名称等占位内容）
  const INVALID_DESCRIPTIONS = [
    '来自V2EX远程工作社区的招聘帖子',
    '来自远程中文网的远程工作机会',
    '来自远程中文网',
  ];
  const validDescription = (job.description && 
    !INVALID_DESCRIPTIONS.some(d => job.description.includes(d)) && 
    job.description.length > 10) 
    ? job.description 
    : '';
  
  const content = document.getElementById('modalContent');
  // 过滤掉不需要展示的标签
  const filteredTags = (job.tags || []).filter(t => !['V2EX', '远程', '社群内推'].includes(t));
  // 过滤 responsibilities / requirements 中含数据源网站链接的行
  const filterSourceLines = (arr) => (arr || []).filter(line =>
    !/https?:\/\/(www\.)?v2ex\.com/i.test(line) &&
    !/https?:\/\/remote-china\.com/i.test(line)
  );
  content.innerHTML = `
    <div class="modal-logo">${job.logo}</div>
    <div class="modal-title">${modalTitle} ${featuredBadge} ${sourceLabel} ${referBadge}</div>
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
      <ul>${filterSourceLines(job.responsibilities).map(r => `<li>${r}</li>`).join('')}</ul>
    </div>` : ''}

    ${job.requirements && job.requirements.length ? `
    <div class="modal-section">
      <h4>任职要求</h4>
      <ul>${filterSourceLines(job.requirements).map(r => `<li>${r}</li>`).join('')}</ul>
    </div>` : ''}

    ${job.benefits && job.benefits.length ? `
    <div class="modal-section">
      <h4>福利待遇</h4>
      <div class="job-tags" style="margin-top:4px">
        ${job.benefits.map(b => `<span class="job-tag">${b}</span>`).join('')}
      </div>
    </div>` : ''}

    <div id="modalAccess"></div>

    <div class="modal-actions" id="modalActions"></div>
  `;
  document.getElementById('modalOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';

  // 会员权益（申请链接 / 内推联系方式）异步渲染，不阻塞弹窗打开
  renderJobAccess(job);
}

// ── 详情页底部按钮（所有岗位统一逻辑，无会员门控）──
//   内推岗 → 加入社群内推；有申请链接 → 申请职位；都没有 → 查看原帖
const escapeHtml = (s) => String(s || '').replace(/[&<>"']/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
));

function defaultJobAction(job) {
  if (job.canRefer) {
    return '<a href="community.html" target="_blank" class="btn btn-primary">加入社群内推 →</a>';
  }
  const url = job.applyUrl || job.sourceUrl || '#';
  const label = job.applyUrl ? '申请职位 →' : '查看原帖投递 →';
  return `<a href="${escapeHtml(url)}" target="_blank" class="btn btn-primary">${label}</a>`;
}

function renderJobAccess(job) {
  const box = document.getElementById('modalAccess');
  const actions = document.getElementById('modalActions');
  if (!box || !actions) return;
  box.innerHTML = '';
  actions.innerHTML =
    defaultJobAction(job) +
    '<button class="btn btn-outline" onclick="closeModal()">关闭</button>';
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

  // 精选岗单独成板块，不计入国内/海外计数，但要计入总数
  const featuredList = getFeaturedList();
  if (el) el.textContent = allCN.length + globalList.length + featuredList.length;
}

// ── 初始化 ──
document.addEventListener('DOMContentLoaded', () => {
  const cnJobs = getCurrentJobs();
  updateStats();

  // 每日精选板块（会员权益入口）
  renderFeatured();
  // 登录/会员状态变化时重渲染，让「已解锁」标记实时更新
  if (window.Auth) window.Auth.onChange(() => renderFeatured());
  
  // 根据当前模式初始化
  if (currentSource === 'global') {
    const globalLayout = document.getElementById('globalLayout');
    const cnLayout = document.getElementById('jobList');
    const categoryTags = document.getElementById('categoryTags');
    if (globalLayout) globalLayout.style.display = 'flex';
    if (cnLayout) cnLayout.style.display = 'none';
    if (categoryTags) categoryTags.style.display = 'none';
    buildGlobalFilters();
    applyGlobalFilters();
  } else {
    buildCategoryTags();
    applyFilters();
  }
});
