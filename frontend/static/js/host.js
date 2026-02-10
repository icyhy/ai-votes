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

    wsClient.on('activity_started', () => {
        showMessage('活动已开始', 'success');
        updateButtons('active');
    });

    wsClient.on('vote_started', (data) => {
        currentVoteId = data.vote_id;
        showMessage('投票已开始: ' + data.title, 'success');
        updateButtons('voting');
    });

    wsClient.on('vote_ended', () => {
        showMessage('投票已结束', 'info');
        updateButtons('result');
    });

    wsClient.on('vote_exited', () => {
        currentVoteId = null;
        showMessage('已退出当前投票', 'info');
        updateButtons('active');
    });

    wsClient.on('activity_ended', () => {
        showMessage('活动统计已生成', 'success');
        updateButtons('summary');
    });

    wsClient.on('activity_closed', () => {
        showMessage('活动已关闭', 'info');
        localStorage.removeItem('session_id');
        setTimeout(() => window.location.href = '/signin', 2000);
    });

    // 控制按钮事件监听
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
        const data = await apiRequest('/api/host/status');

        document.getElementById('activity-name').textContent = data.activity_name;
        document.getElementById('participant-count').textContent = data.participant_count;

        // 恢复当前投票 ID
        currentVoteId = data.current_vote_id;

        // 根据活动状态初始化按钮显示
        updateButtons(data.activity_status, currentVoteId !== null);

        renderVoteList(data.votes);
    } catch (error) {
        showMessage('加载失败: ' + error.message, 'error');
    }
}

/**
 * 更新按钮显示状态
 */
function updateButtons(status, isVoting = false) {
    const startBtn = document.getElementById('start-activity-btn');
    const endVoteBtn = document.getElementById('end-vote-btn');
    const exitVoteBtn = document.getElementById('exit-vote-btn');
    const endActivityBtn = document.getElementById('end-activity-btn');
    const closeBtn = document.getElementById('close-activity-btn');

    // 默认全部隐藏
    [startBtn, endVoteBtn, exitVoteBtn, endActivityBtn, closeBtn].forEach(btn => {
        if (btn) btn.style.display = 'none';
    });

    console.log('Updating buttons for status:', status, 'isVoting:', isVoting);

    if (status === 'pending') {
        startBtn.style.display = 'block';
    } else if (status === 'active' || status === 'voting' || status === 'result') {
        // 活动进行中
        if (currentVoteId) {
            // 如果有正在进行的投票或结果展示
            if (status === 'voting' || (status === 'active' && !isVoting)) {
                // 这里的逻辑需要根据 backend 同步的状态来
                // 简化: 只要有 currentVoteId, 就显示 End 和 Exit
                endVoteBtn.style.display = 'block';
                exitVoteBtn.style.display = 'block';
            } else if (status === 'result') {
                exitVoteBtn.style.display = 'block';
            } else {
                // 兜底
                endVoteBtn.style.display = 'block';
                exitVoteBtn.style.display = 'block';
            }
        } else {
            // 没有活动投票, 显示结束活动按钮
            endActivityBtn.style.display = 'block';
        }
    } else if (status === 'summary' || status === 'ended') {
        closeBtn.style.display = 'block';
    }
}

/**
 * 渲染投票列表
 */
function renderVoteList(votes) {
    const voteList = document.getElementById('vote-list');

    if (!votes || votes.length === 0) {
        voteList.innerHTML = '<p class="text-muted">暂无投票项目</p>';
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
    if (currentVoteId) {
        showMessage('当前已有投票正在开启,请先退出', 'error');
        return;
    }

    if (!confirm('确定开始这个投票吗?')) return;

    try {
        await apiRequest('/api/host/vote/start?vote_id=' + voteId, {
            method: 'POST'
        });
    } catch (error) {
        showMessage('开始失败: ' + error.message, 'error');
    }
}

// 绑定到 window 以便 onclick 调用
window.selectVote = selectVote;

async function startActivity() {
    try {
        await apiRequest('/api/host/activity/start', { method: 'POST' });
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

async function endVote() {
    if (!currentVoteId) return;
    try {
        await apiRequest('/api/host/vote/end?vote_id=' + currentVoteId, { method: 'POST' });
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

async function exitVote() {
    try {
        await apiRequest('/api/host/vote/exit', { method: 'POST' });
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

async function endActivity() {
    if (!confirm('确定结束活动并显示总结统计吗?')) return;
    try {
        await apiRequest('/api/host/activity/end', { method: 'POST' });
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}

async function closeActivity() {
    if (!confirm('确定关闭并同步数据吗?')) return;
    try {
        await apiRequest('/api/host/activity/close', { method: 'POST' });
    } catch (error) {
        showMessage('操作失败: ' + error.message, 'error');
    }
}
