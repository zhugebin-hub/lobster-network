// 新生选寝系统 - 前端交互
const API_BASE = '';
let currentPlan = null;
let currentFilter = 'all';
let searchKeyword = '';

// Token 管理
function getToken() { return localStorage.getItem('dorm_token') || ''; }
function saveToken() {
    const token = document.getElementById('api-token').value.trim();
    if (!token) { showToast('请输入 Token', 'error'); return; }
    localStorage.setItem('dorm_token', token);
    showToast('Token 已保存', 'success');
    showMainUI();
}
function authHeaders() {
    const h = {};
    const t = getToken();
    if (t) h['Authorization'] = 'Bearer ' + t;
    return h;
}

// Toast 提示
function showToast(msg, type = '') {
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

// 初始化
window.onload = function() {
    if (getToken()) showMainUI();
};

function showMainUI() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('import-section').style.display = 'block';
}

// API 调用
async function apiGet(url) {
    const resp = await fetch(url, { headers: authHeaders() });
    return resp.json();
}
async function apiPost(url, body) {
    const resp = await fetch(url, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const ct = resp.headers.get('Content-Type') || '';
    if (ct.includes('application/json')) return resp.json();
    return resp.blob();
}
async function apiPostFile(url, formData) {
    const resp = await fetch(url, {
        method: 'POST',
        headers: authHeaders(),
        body: formData
    });
    return resp.json();
}

// 加载示例数据
async function loadDemo() {
    const btn = document.getElementById('demo-btn');
    btn.disabled = true;
    btn.textContent = '加载中...';
    try {
        const data = await apiGet(API_BASE + '/api/demo');
        if (data.error) { showToast(data.error, 'error'); return; }
        currentPlan = data;
        renderDashboard(data);
        renderRooms(data);
        renderSuspended(data);
        showToast('示例数据加载成功', 'success');
    } catch (e) {
        showToast('加载失败: ' + e.message, 'error');
    }
    btn.disabled = false;
    btn.textContent = '加载示例数据';
}

// 智能匹配
async function doMatch() {
    const official = document.getElementById('official-file').files[0];
    const survey = document.getElementById('survey-file').files[0];
    const roomSize = parseInt(document.getElementById('room-size').value) || 4;
    if (!official || !survey) { showToast('请上传两个文件', 'error'); return; }
    const btn = document.getElementById('match-btn');
    btn.disabled = true;
    btn.textContent = '匹配中...';
    const formData = new FormData();
    formData.append('official', official);
    formData.append('survey', survey);
    formData.append('roomSize', roomSize);
    try {
        const data = await apiPostFile(API_BASE + '/api/match', formData);
        if (data.error) { showToast(data.error, 'error'); return; }
        currentPlan = data;
        renderDashboard(data);
        renderRooms(data);
        renderSuspended(data);
        showSection('dashboard-section');
        showSection('filter-section');
        showSection('rooms-section');
        showSection('suspended-section');
        showSection('version-section');
        showSection('action-section');
        showToast(`匹配完成！${data.summary.total_students}人 → ${data.summary.room_count}间寝室`, 'success');
    } catch (e) {
        showToast('匹配失败: ' + e.message, 'error');
    }
    btn.disabled = false;
    btn.textContent = '🦞 导入并智能匹配';
}

// 渲染看板
function renderDashboard(data) {
    const s = data.summary;
    document.getElementById('stats').innerHTML = `
        <div class="stat-item"><div class="num">${s.total_students}</div><div class="label">总人数</div></div>
        <div class="stat-item"><div class="num">${s.room_count}</div><div class="label">寝室数</div></div>
        <div class="stat-item"><div class="num">${s.suspended_count}</div><div class="label">挂起人数</div></div>
        <div class="stat-item"><div class="num" style="color:${s.conflict_count > 0 ? '#ea4335' : '#34a853'}">${s.conflict_count}</div><div class="label">冲突寝室</div></div>
        <div class="stat-item"><div class="num">${s.room_size}</div><div class="label">每寝人数</div></div>
    `;
    const wDiv = document.getElementById('warnings');
    wDiv.style.display = data.warnings && data.warnings.length ? 'block' : 'none';
    wDiv.innerHTML = data.warnings.map(w => '⚠️ ' + w).join('<br>');
    const aDiv = document.getElementById('advice');
    aDiv.style.display = data.advice && data.advice.length ? 'block' : 'none';
    aDiv.innerHTML = data.advice.map(a => '💡 ' + a).join('<br>');
    document.getElementById('generated-at').textContent = '生成时间: ' + s.generated_at;
}

// 渲染寝室列表
function renderRooms(data) {
    const grid = document.getElementById('rooms-grid');
    let rooms = data.rooms || [];
    if (currentFilter === 'risk') rooms = rooms.filter(r => r[0] && r[0]._room_conflicts && r[0]._room_conflicts.length > 0);
    else if (currentFilter !== 'all') rooms = rooms.filter(r => r.some(s => s.gender === currentFilter));
    if (searchKeyword) {
        const kw = searchKeyword.toLowerCase();
        rooms = rooms.filter(r => r.some(s => (s.name + s.id + s.origin + s.undergrad_school).toLowerCase().includes(kw)));
    }
    grid.innerHTML = rooms.map(room => {
        if (!room.length) return '';
        const conflicts = room[0]._room_conflicts || [];
        const bonds = room[0]._room_bonds || [];
        const hasRisk = conflicts.length > 0;
        return `<div class="room-card ${hasRisk ? 'risk' : ''}" onclick="showRoomDetail(this)">
            <div class="room-header">
                <span class="room-id">🏠 寝室 ${room[0]._room_id}</span>
                <span class="room-badge ${hasRisk ? 'badge-risk' : 'badge-normal'}">${hasRisk ? '⚠️ 需复核' : '✅ 正常'}</span>
            </div>
            <div class="student-list">
                ${room.map(s => `<div class="student-item" onclick="event.stopPropagation(); showProfile('${s.id}')">
                    <div class="student-avatar ${s.gender === '男' ? 'male' : s.gender === '女' ? 'female' : 'other'}">${s.name[0]}</div>
                    <div class="student-info">
                        <div class="student-name">${s.name}</div>
                        <div class="student-detail">${s.undergrad_school || s.origin || ''}</div>
                    </div>
                    <div class="student-tags">
                        ${s.missing_survey ? '<span class="tag tag-missing">漏报</span>' : ''}
                        ${s.is_local === '是' ? '<span class="tag tag-local">本地</span>' : ''}
                        ${s.is_home_school === '是' ? '<span class="tag tag-home">本校</span>' : ''}
                        ${s.smoke === '抽烟' ? '<span class="tag tag-smoke">抽烟</span>' : ''}
                    </div>
                </div>`).join('')}
            </div>
            ${conflicts.length ? `<div class="conflicts-box">⚠️ ${conflicts.join('<br>⚠️ ')}</div>` : ''}
            ${bonds.length ? `<div class="bonds-box">🔗 ${bonds.join('<br>🔗 ')}</div>` : ''}
        </div>`;
    }).join('');
    if (!rooms.length) grid.innerHTML = '<p style="text-align:center;color:#999;padding:40px;">没有匹配的寝室</p>';
}

// 渲染挂起池
function renderSuspended(data) {
    const list = document.getElementById('suspended-list');
    const sec = document.getElementById('suspended-section');
    if (!data.suspended || !data.suspended.length) {
        sec.style.display = 'none';
        return;
    }
    sec.style.display = 'block';
    list.innerHTML = data.suspended.map(s => `<div class="suspended-item">${s.name} (${s.gender}) - ${s.origin || ''}</div>`).join('');
}

// 筛选
function setFilter(f, el) {
    currentFilter = f;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    if (currentPlan) renderRooms(currentPlan);
}
function applySearch() {
    searchKeyword = document.getElementById('search-input').value;
    if (currentPlan) renderRooms(currentPlan);
}

// 学生画像
function showProfile(studentId) {
    if (!currentPlan) return;
    let student = null;
    for (const room of currentPlan.rooms) {
        for (const s of room) { if (s.id === studentId) { student = s; break; } }
        if (student) break;
    }
    if (!student) return;
    document.getElementById('profile-name').textContent = student.name;
    document.getElementById('profile-body').innerHTML = `
        <div class="profile-row"><div class="profile-label">学号</div><div class="profile-value">${student.id}</div></div>
        <div class="profile-row"><div class="profile-label">性别</div><div class="profile-value">${student.gender}</div></div>
        <div class="profile-row"><div class="profile-label">手机</div><div class="profile-value">${student.phone || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">生源地</div><div class="profile-value">${student.origin || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">本科院校</div><div class="profile-value">${student.undergrad_school || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">本科城市</div><div class="profile-value">${student.undergrad_city || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">是否本校</div><div class="profile-value">${student.is_home_school || '否'}</div></div>
        <div class="profile-row"><div class="profile-label">是否本地</div><div class="profile-value">${student.is_local || '否'}</div></div>
        <div class="profile-row"><div class="profile-label">抽烟</div><div class="profile-value">${student.smoke || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">作息</div><div class="profile-value">${student.schedule || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">游戏</div><div class="profile-value">${student.game_freq || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">噪音敏感</div><div class="profile-value">${student.noise_sensitive ? '是' : '否'}</div></div>
        <div class="profile-row"><div class="profile-label">卫生</div><div class="profile-value">${student.hygiene || '未填'}</div></div>
        <div class="profile-row"><div class="profile-label">空调</div><div class="profile-value">${student.ac || '无特殊'}</div></div>
        <div class="profile-row"><div class="profile-label">备注</div><div class="profile-value">${student.remark || '无'}</div></div>
        ${student.intent ? `<div class="profile-row"><div class="profile-label">意向室友</div><div class="profile-value">${student.intent}</div></div>` : ''}
    `;
    document.getElementById('profile-modal').style.display = 'flex';
}
function closeModal() { document.getElementById('profile-modal').style.display = 'none'; }

// 导出
async function exportExcel() {
    if (!currentPlan) { showToast('请先生成方案', 'error'); return; }
    try {
        const blob = await apiPost(API_BASE + '/api/export', { plan_id: currentPlan.plan_id });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dormitory_assignment.xlsx';
        a.click();
        URL.revokeObjectURL(url);
        showToast('导出成功', 'success');
    } catch (e) {
        showToast('导出失败: ' + e.message, 'error');
    }
}

// 版本管理
async function saveVersion() {
    if (!currentPlan) return;
    const name = document.getElementById('version-name').value.trim() || '方案 ' + new Date().toLocaleString();
    try {
        const data = await apiPost(API_BASE + '/api/save_version', { plan_id: currentPlan.plan_id, version_name: name });
        if (data.error) { showToast(data.error, 'error'); return; }
        showToast(`版本 "${name}" 已保存`, 'success');
        loadVersions();
    } catch (e) { showToast('保存失败', 'error'); }
}
async function loadVersions() {
    if (!currentPlan) return;
    try {
        const data = await apiPost(API_BASE + '/api/list_versions', {});
        const list = document.getElementById('version-list');
        list.innerHTML = (data.versions || []).map(v => `
            <div class="version-item">
                <span class="version-name">${v.version_name}</span>
                <span class="version-time">${v.created_at.replace('T', ' ').substring(0, 19)}</span>
            </div>
        `).join('');
    } catch (e) {}
}

// 下载示例模板
function downloadSample() {
    window.open(API_BASE + '/api/sample-official.xlsx', '_blank');
    setTimeout(() => window.open(API_BASE + '/api/sample-survey.xlsx', '_blank'), 500);
}

function showSection(id) { document.getElementById(id).style.display = 'block'; }
function showRoomDetail(el) { /* 可展开详情 */ }
