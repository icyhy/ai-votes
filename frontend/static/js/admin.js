/**
 * 管理员页面逻辑
 */

let adminToken = localStorage.getItem('admin_token');
let currentActivityId = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    if (adminToken) {
        showMainView();
        loadCurrentActivity();
        loadVoteTemplates();
        loadExportFiles();
        loadNetworkInfo();
    } else {
        showLoginView();
    }

    // 登录表单
    document.getElementById('login-form').addEventListener('submit', handleLogin);

    // 退出登录
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // 导航切换
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => switchSection(btn.dataset.section));
    });

    // 活动表单
    document.getElementById('activity-form').addEventListener('submit', handleCreateActivity);

    // 投票类型选择
    document.querySelectorAll('.type-option').forEach(option => {
        option.addEventListener('click', () => selectVoteType(option.dataset.type));
    });

    // 投票表单
    document.getElementById('vote-form').addEventListener('submit', handleSaveVote);
    document.getElementById('add-option-btn').addEventListener('click', addOption);
    document.getElementById('cancel-edit-btn').addEventListener('click', cancelEdit);

    // 密码表单
    document.getElementById('password-form').addEventListener('submit', handleSavePasswords);

    // 网络配置表单
    document.getElementById('network-form').addEventListener('submit', handleSaveNetwork);
});

/**
 * 显示登录界面
 */
function showLoginView() {
    document.getElementById('login-view').style.display = 'block';
    document.getElementById('main-view').style.display = 'none';
}

/**
 * 显示主界面
 */
function showMainView() {
    document.getElementById('login-view').style.display = 'none';
    document.getElementById('main-view').style.display = 'block';
}

/**
 * 处理登录
 */
async function handleLogin(e) {
    e.preventDefault();
    const password = document.getElementById('login-password').value;

    try {
        const data = await apiRequest('/api/admin/login', {
            method: 'POST',
            body: JSON.stringify({ password })
        });

        adminToken = data.token;
        localStorage.setItem('admin_token', adminToken);
        showMessage('登录成功', 'success');
        showMainView();
        loadCurrentActivity();
        loadVoteTemplates();
        loadExportFiles();
        loadNetworkInfo();
    } catch (error) {
        showMessage('登录失败: ' + error.message, 'error');
    }
}

/**
 * 处理退出登录
 */
function handleLogout() {
    adminToken = null;
    localStorage.removeItem('admin_token');
    showLoginView();
    document.getElementById('login-password').value = '';
}

/**
 * 切换导航
 */
function switchSection(section) {
    // 更新导航按钮
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.section === section);
    });

    // 更新内容区域
    document.querySelectorAll('.admin-section').forEach(sec => {
        sec.classList.toggle('active', sec.id === `${section}-section`);
    });
}

/**
 * 加载当前活动
 */
async function loadCurrentActivity() {
    try {
        const data = await apiRequest('/api/admin/activities/current');

        currentActivityId = data.id;
        document.getElementById('current-activity').innerHTML = `
            <div class="card">
                <h3>${data.name}</h3>
                <p class="text-muted">${data.theme || '无主题'}</p>
                <p class="text-sm">状态: <span class="text-primary">${getStatusText(data.status)}</span></p>
                <p class="text-sm">创建时间: ${new Date(data.created_at).toLocaleString('zh-CN')}</p>
            </div>
        `;
    } catch (error) {
        document.getElementById('current-activity').innerHTML = '<p class="text-muted">暂无活动</p>';
    }
}

function getStatusText(status) {
    const statusMap = {
        'pending': '待开始',
        'active': '进行中',
        'ended': '已结束'
    };
    return statusMap[status] || status;
}

/**
 * 创建活动
 */
async function handleCreateActivity(e) {
    e.preventDefault();

    const name = document.getElementById('activity-name').value;
    const theme = document.getElementById('activity-theme').value;

    try {
        await apiRequest('/api/admin/activities', {
            method: 'POST',
            body: JSON.stringify({ name, theme })
        });

        showMessage('活动创建成功，已自动复制投票模板', 'success');
        document.getElementById('activity-form').reset();
        loadCurrentActivity();
    } catch (error) {
        showMessage('创建失败: ' + error.message, 'error');
    }
}

/**
 * 选择投票类型
 */
function selectVoteType(type) {
    document.querySelectorAll('.type-option').forEach(opt => {
        opt.classList.toggle('selected', opt.dataset.type === type);
    });

    document.getElementById('vote-type').value = type;

    // 显示/隐藏选项编辑器
    const optionsContainer = document.getElementById('options-container');
    if (type === 'single' || type === 'multiple') {
        optionsContainer.style.display = 'block';
    } else {
        optionsContainer.style.display = 'none';
    }
}

/**
 * 添加选项
 */
function addOption() {
    const optionsList = document.getElementById('options-list');
    const optionCount = optionsList.querySelectorAll('.option-item').length;

    if (optionCount >= 6) {
        showMessage('最多只能添加6个选项', 'error');
        return;
    }

    const optionItem = document.createElement('div');
    optionItem.className = 'option-item';
    optionItem.innerHTML = `
        <input type="text" class="input option-input" placeholder="选项 ${optionCount + 1}">
        <button type="button" class="btn btn-danger btn-icon remove-option">✕</button>
    `;

    optionItem.querySelector('.remove-option').addEventListener('click', () => {
        optionItem.remove();
    });

    optionsList.appendChild(optionItem);
}

// 初始化删除按钮
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-option')) {
        e.target.closest('.option-item').remove();
    }
});

/**
 * 保存投票模板
 */
async function handleSaveVote(e) {
    e.preventDefault();

    const title = document.getElementById('vote-title').value;
    const type = document.getElementById('vote-type').value;
    const editVoteId = document.getElementById('edit-vote-id').value;

    let options = null;
    if (type === 'single' || type === 'multiple') {
        options = Array.from(document.querySelectorAll('.option-input'))
            .map(input => input.value.trim())
            .filter(val => val);

        if (options.length < 2) {
            showMessage('至少需要2个选项', 'error');
            return;
        }
    }

    try {
        if (editVoteId) {
            // 更新投票模板
            await apiRequest(`/api/admin/vote-templates/${editVoteId}`, {
                method: 'PUT',
                body: JSON.stringify({ title, type, options })
            });
            showMessage('投票模板更新成功', 'success');
        } else {
            // 创建投票模板
            await apiRequest('/api/admin/vote-templates', {
                method: 'POST',
                body: JSON.stringify({ title, type, options })
            });
            showMessage('投票模板创建成功', 'success');
        }

        document.getElementById('vote-form').reset();
        document.getElementById('edit-vote-id').value = '';
        document.getElementById('cancel-edit-btn').style.display = 'none';
        selectVoteType('single');
        loadVoteTemplates();
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

/**
 * 加载投票模板列表
 */
async function loadVoteTemplates() {
    try {
        const templates = await apiRequest('/api/admin/vote-templates');

        const voteList = document.getElementById('vote-list');

        if (templates.length === 0) {
            voteList.innerHTML = '<p class="text-muted">暂无投票模板</p>';
            return;
        }

        voteList.innerHTML = templates.map(template => `
            <div class="vote-item">
                <div class="vote-info">
                    <div class="vote-title-text">${template.title}</div>
                    <div>
                        <span class="vote-type-badge">${getVoteTypeText(template.type)}</span>
                        ${template.options ? `<span class="vote-options-preview">${template.options.join(', ')}</span>` : ''}
                    </div>
                </div>
                <div class="vote-actions">
                    <button class="btn btn-primary btn-icon" onclick="editVoteTemplate(${template.id})">✏️</button>
                    <button class="btn btn-danger btn-icon" onclick="deleteVoteTemplate(${template.id})">🗑️</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载投票模板失败:', error);
    }
}

function getVoteTypeText(type) {
    const typeMap = {
        'single': '单选',
        'multiple': '多选',
        'text': '问答',
        'rating': '评分'
    };
    return typeMap[type] || type;
}

/**
 * 编辑投票模板
 */
async function editVoteTemplate(templateId) {
    try {
        const templates = await apiRequest('/api/admin/vote-templates');

        const template = templates.find(t => t.id === templateId);
        if (!template) return;

        document.getElementById('vote-title').value = template.title;
        document.getElementById('vote-type').value = template.type;
        document.getElementById('edit-vote-id').value = template.id;
        document.getElementById('cancel-edit-btn').style.display = 'inline-block';

        selectVoteType(template.type);

        if (template.options && (template.type === 'single' || template.type === 'multiple')) {
            const optionsList = document.getElementById('options-list');
            optionsList.innerHTML = template.options.map((opt, idx) => `
                <div class="option-item">
                    <input type="text" class="input option-input" placeholder="选项 ${idx + 1}" value="${opt}">
                    <button type="button" class="btn btn-danger btn-icon remove-option">✕</button>
                </div>
            `).join('');
        }

        // 滚动到表单
        document.getElementById('vote-form').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showMessage('加载投票模板失败: ' + error.message, 'error');
    }
}

/**
 * 取消编辑
 */
function cancelEdit() {
    document.getElementById('vote-form').reset();
    document.getElementById('edit-vote-id').value = '';
    document.getElementById('cancel-edit-btn').style.display = 'none';
    selectVoteType('single');
}

/**
 * 删除投票模板
 */
async function deleteVoteTemplate(templateId) {
    if (!confirm('确定要删除这个投票模板吗？')) return;

    try {
        await apiRequest(`/api/admin/vote-templates/${templateId}`, {
            method: 'DELETE'
        });

        showMessage('删除成功', 'success');
        loadVoteTemplates();
    } catch (error) {
        showMessage('删除失败: ' + error.message, 'error');
    }
}

/**
 * 保存密码
 */
async function handleSavePasswords(e) {
    e.preventDefault();

    const adminPassword = document.getElementById('admin-password').value;
    const hostPassword = document.getElementById('host-password').value;

    if (!adminPassword && !hostPassword) {
        showMessage('请至少输入一个密码', 'error');
        return;
    }

    try {
        await apiRequest('/api/admin/passwords', {
            method: 'POST',
            body: JSON.stringify({
                admin_password: adminPassword || undefined,
                host_password: hostPassword || undefined
            })
        });

        showMessage('密码保存成功', 'success');
        document.getElementById('password-form').reset();
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

/**
 * 加载网络信息
 */
async function loadNetworkInfo() {
    try {
        const data = await apiRequest('/api/signin/info');
        const url = new URL(data.signin_url);
        document.getElementById('detected-ip').textContent = url.hostname;
    } catch (error) {
        document.getElementById('detected-ip').textContent = '检测失败';
    }
}

/**
 * 保存网络配置
 */
async function handleSaveNetwork(e) {
    e.preventDefault();

    const manualIp = document.getElementById('manual-ip').value;

    try {
        await apiRequest('/api/admin/network', {
            method: 'POST',
            body: JSON.stringify({ manual_ip: manualIp })
        });

        showMessage('网络配置保存成功', 'success');
        loadNetworkInfo();
    } catch (error) {
        showMessage('保存失败: ' + error.message, 'error');
    }
}

/**
 * 加载导出文件
 */
async function loadExportFiles() {
    try {
        const data = await apiRequest('/api/admin/exports');

        const exportFiles = document.getElementById('export-files');

        if (data.files.length === 0) {
            exportFiles.innerHTML = '<p class="text-muted">暂无导出文件</p>';
            return;
        }

        exportFiles.innerHTML = data.files.map(file => `
            <div class="export-item">
                <div>
                    <div class="export-filename">${file.filename}</div>
                    <div class="export-date">${new Date(file.created_at).toLocaleString('zh-CN')}</div>
                </div>
                <div>
                    <a href="/api/admin/exports/${file.filename}?token=${adminToken}" 
                       class="btn btn-primary" download>下载</a>
                    <button class="btn btn-danger" onclick="deleteExportFile('${file.filename}')">删除</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('加载导出文件失败:', error);
    }
}

/**
 * 删除导出文件
 */
async function deleteExportFile(filename) {
    if (!confirm('确定要删除这个导出文件吗？')) return;

    try {
        await apiRequest(`/api/admin/exports/${filename}`, {
            method: 'DELETE'
        });

        showMessage('删除成功', 'success');
        loadExportFiles();
    } catch (error) {
        showMessage('删除失败: ' + error.message, 'error');
    }
}
