/**
 * 主持人控制页面逻辑
 */

const sessionId = localStorage.getItem('session_id');
let currentVoteId = null;

if (!sessionId) {
    window.location.href = '/signin';
}

// 初始化 WebSocket
const wsClient = new WebSocketClient('host');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    wsClient.connect();
    loadHostStatus();

    // 注册 WebSocket 消息处理
    wsClient.on('participant_signed_in', (data) => {
        document.getElementById('participant-count').textContent = data.count;
    });

    // 控制按钮
    document.getElementById('start-activity-btn').addEventListener('click', startActivity);
    document.getElementById('end-vote-btn').addEventListener('click', endVote);
    document.getElementById('exit-vote-btn').addEventListener('click', exitVote);
    document.getElementById('end-activity-btn').addEventListener('click', endActivity);
    document.getElementById('close-activity-btn').addEventListener('click', closeActivity);
});

/**
 * 加载主持人状态
 */
async function loadHostStatus() {
    try {
        const data = await apiRequest('/api/host/status', {
            headers: { 'X-Session-ID': sessionId }
        });

        // 更新活动名称
        document.getElementById('activity-name').textContent = data.activity_name;

        // 更新签到人数
        document.getElementById('participant-count').textContent = data.participant_count;

        // 渲染投票列表
        renderVoteList(data.votes);
    } catch (error) {
        showMessage('加载失败: ' + error.message, 'error');
    }
}

/**
 * 渲染投票列表
 */
function renderVoteList(votes) {
    const voteList = document.getElementById('vote-list');

    if (votes.length === 0) {
        voteList.innerHTML = '<p class="text-muted">暂无投票，请在管理员页面添加</p>';
        return;
    }

    voteList.innerHTML = votes.map(vote => `
        <div class="vote-select-item" onclick="selectVote(${vote.id})">
            <div class="vote-select-title">${vote.title}</div>
            <div class="vote-select-type">${getVoteTypeText(vote.type)}</div>
        </div>
    `).join('');
}

function getVoteTypeText(type) {
    const typeMap = {
        'single': '单选题',
        'multiple': '多选题',
        'text': '问答题',
        'rating': '评分题'
    };
    return typeMap[type] || type;
}

/**
 * 选择投票
 */
async function selectVote(voteId) {
    if (!confirm('确定开始这个投票吗?')) return;

    try {
        await apiRequest('/api/host/vote/start?vote_id=' + voteId, {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId }
        });

        currentVoteId = voteId;
        showMessage('投票已开始', 'success');

        // 显示控制按钮
        document.getElementById('end-vote-btn').style.display = 'block';
        document.getElementById('exit-vote-btn').style.display = 'block';
    } catch (error) {
        showMessage('开始失败: ' + error.message, 'error');
    }
}

/**
 * 开始活动
 */
async function startActivity() {
    try {
        await apiRequest('/api/host/activity/start', {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId }
        });

        showMessage('活动已开始', 'success');
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

/**
 * 结束投票
 */
async function endVote() {
    if (!currentVoteId) return;

    try {
        await apiRequest('/api/host/vote/end?vote_id=' + currentVoteId, {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId }
        });

        showMessage('投票已结束，正在显示结果', 'success');

        // 隐藏控制按钮
        document.getElementById('end-vote-btn').style.display = 'none';
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

/**
 * 退出投票
 */
async function exitVote() {
    try {
        await apiRequest('/api/host/vote/exit', {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId }
        });

        currentVoteId = null;
        showMessage('已退出投票', 'success');

        // 隐藏控制按钮
        document.getElementById('end-vote-btn').style.display = 'none';
        document.getElementById('exit-vote-btn').style.display = 'none';
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

/**
 * 结束活动
 */
async function endActivity() {
    if (!confirm('确定结束活动并显示统计吗?')) return;

    try {
        await apiRequest('/api/host/activity/end', {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId }
        });

        showMessage('活动已结束', 'success');
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

/**
 * 退出活动
 */
async function closeActivity() {
    if (!confirm('确定退出活动吗? 数据将被保存并重置。')) return;

    try {
        await apiRequest('/api/host/activity/close', {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId }
        });

        showMessage('活动已关闭，数据已保存', 'success');

        // 清除 session
        localStorage.removeItem('session_id');

        // 3秒后跳转到签到页
        setTimeout(() => {
            window.location.href = '/signin';
        }, 3000);
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}
