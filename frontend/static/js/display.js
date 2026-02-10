/**
 * 大屏页面逻辑
 */

// 初始化 WebSocket 客户端
const wsClient = new WebSocketClient('display');

// 当前视图状态
let currentView = 'signin';

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    wsClient.connect();
    loadSigninInfo();

    // 注册消息处理器
    wsClient.on('participant_signed_in', handleParticipantSignedIn);
    wsClient.on('activity_started', handleActivityStarted);
    wsClient.on('vote_started', handleVoteStarted);
    wsClient.on('vote_ended', handleVoteEnded);
    wsClient.on('vote_exited', handleVoteExited);
    wsClient.on('activity_ended', handleActivityEnded);
    wsClient.on('activity_closed', handleActivityClosed);
});

/**
 * 加载签到信息
 */
async function loadSigninInfo() {
    try {
        const data = await apiRequest('/api/signin/info');

        // 更新二维码
        document.getElementById('qrcode').src = data.qrcode_url;
        document.getElementById('small-qrcode').src = data.qrcode_url;

        // 更新活动名称
        if (data.activity_name) {
            document.getElementById('activity-name').textContent = data.activity_name;
        }

        // 更新签到人数
        document.getElementById('participant-count').textContent = data.participant_count || 0;
    } catch (error) {
        console.error('加载签到信息失败:', error);
    }
}

/**
 * 切换视图
 */
function switchView(viewName) {
    // 隐藏所有视图
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    // 显示目标视图
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.classList.add('active');
        currentView = viewName;
    }
}

/**
 * 处理签到通知
 */
function handleParticipantSignedIn(data) {
    document.getElementById('participant-count').textContent = data.count;
}

/**
 * 处理活动开始
 */
function handleActivityStarted(data) {
    switchView('signin');
    loadSigninInfo();
}

/**
 * 处理投票开始
 */
function handleVoteStarted(data) {
    switchView('voting');

    // 更新投票标题
    document.getElementById('vote-title').textContent = data.title;

    // 渲染投票选项
    const optionsContainer = document.getElementById('vote-options');
    optionsContainer.innerHTML = '';

    if (data.type === 'single' || data.type === 'multiple') {
        data.options.forEach(option => {
            const optionEl = document.createElement('div');
            optionEl.className = 'vote-option fade-in';
            optionEl.textContent = option;
            optionsContainer.appendChild(optionEl);
        });
    } else if (data.type === 'rating') {
        optionsContainer.innerHTML = '<div class="vote-option fade-in">评分题 (1-5星)</div>';
    } else if (data.type === 'text') {
        optionsContainer.innerHTML = '<div class="vote-option fade-in">问答题</div>';
    }
}

/**
 * 处理投票结束
 */
function handleVoteEnded(data) {
    switchView('result');

    const resultContainer = document.getElementById('result-content');
    resultContainer.innerHTML = '';

    if (data.results) {
        data.results.forEach((result, index) => {
            setTimeout(() => {
                const itemEl = document.createElement('div');
                itemEl.className = 'result-item fade-in';

                const percentage = parseFloat(result.percentage) || 0;

                itemEl.innerHTML = `
                    <div class="result-option">${result.option}</div>
                    <div class="result-bar-container">
                        <div class="result-bar" style="width: ${percentage}%">
                            ${result.percentage}
                        </div>
                    </div>
                    <div class="result-count">${result.count} 票</div>
                `;

                resultContainer.appendChild(itemEl);
            }, index * 200);
        });
    }

    // 显示平均分(如果是评分题)
    if (data.average) {
        setTimeout(() => {
            const avgEl = document.createElement('div');
            avgEl.className = 'result-item fade-in';
            avgEl.innerHTML = `
                <div class="result-option">平均分</div>
                <div class="result-count" style="flex: 1; text-align: center; font-size: var(--text-3xl);">
                    ${data.average} 分
                </div>
            `;
            resultContainer.appendChild(avgEl);
        }, data.results.length * 200);
    }
}

/**
 * 处理退出投票
 */
function handleVoteExited() {
    switchView('signin');
    loadSigninInfo();
}

/**
 * 处理活动结束
 */
function handleActivityEnded(data) {
    switchView('summary');

    const summaryContainer = document.getElementById('summary-content');
    summaryContainer.innerHTML = `
        <div class="summary-card fade-in">
            <div class="summary-label">总签到人数</div>
            <div class="summary-value">${data.total_participants} 人</div>
        </div>
        <div class="summary-card fade-in">
            <div class="summary-label">完成投票数</div>
            <div class="summary-value">${data.votes_completed} 个</div>
        </div>
    `;

    // 显示每个投票的参与情况
    if (data.votes_summary && data.votes_summary.length > 0) {
        data.votes_summary.forEach((vote, index) => {
            setTimeout(() => {
                const voteCard = document.createElement('div');
                voteCard.className = 'summary-card fade-in';
                voteCard.innerHTML = `
                    <div class="summary-label">${vote.title}</div>
                    <div class="summary-value">${vote.participants} 人参与</div>
                `;
                summaryContainer.appendChild(voteCard);
            }, (index + 2) * 200);
        });
    }
}

/**
 * 处理活动关闭
 */
function handleActivityClosed() {
    switchView('end');
}
