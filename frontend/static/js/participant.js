/**
 * 参会人投票页面逻辑
 */

const sessionId = localStorage.getItem('session_id');
let currentVote = null;
let selectedOptions = new Set();
let selectedRating = 0;

if (!sessionId) {
    window.location.href = '/signin';
}

// 初始化 WebSocket
const wsClient = new WebSocketClient('participant');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    wsClient.connect();
    loadParticipantStatus();

    // 注册 WebSocket 消息处理
    wsClient.on('vote_started', handleVoteStarted);
    wsClient.on('vote_ended', handleVoteEnded);
    wsClient.on('vote_exited', handleVoteExited);

    // 提交按钮
    document.getElementById('submit-btn').addEventListener('click', submitVote);

    // 文本输入字数统计
    const textAnswer = document.getElementById('text-answer');
    if (textAnswer) {
        textAnswer.addEventListener('input', () => {
            document.getElementById('char-count').textContent = textAnswer.value.length;
        });
    }

    // 评分星级
    document.querySelectorAll('.star').forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            selectRating(rating);
        });
    });
});

/**
 * 加载参会人状态
 */
async function loadParticipantStatus() {
    try {
        const data = await apiRequest('/api/participant/status', {
            headers: { 'X-Session-ID': sessionId }
        });

        document.getElementById('participant-name').textContent = data.name;
    } catch (error) {
        showMessage('加载失败: ' + error.message, 'error');
    }
}

/**
 * 处理投票开始
 */
function handleVoteStarted(data) {
    currentVote = data;
    selectedOptions.clear();
    selectedRating = 0;

    // 显示投票视图
    document.getElementById('waiting-view').style.display = 'none';
    document.getElementById('voting-view').style.display = 'block';
    document.getElementById('success-view').style.display = 'none';

    // 设置标题
    document.getElementById('vote-question').textContent = data.title;

    // 根据类型渲染
    if (data.type === 'single' || data.type === 'multiple') {
        renderOptions(data.options, data.type);
    } else if (data.type === 'text') {
        showTextView();
    } else if (data.type === 'rating') {
        showRatingView();
    }
}

/**
 * 渲染选项
 */
function renderOptions(options, type) {
    document.getElementById('options-view').style.display = 'block';
    document.getElementById('text-view').style.display = 'none';
    document.getElementById('rating-view').style.display = 'none';

    const optionsView = document.getElementById('options-view');
    optionsView.innerHTML = options.map((option, index) => `
        <div class="vote-option-item" data-option="${option}">
            <div class="option-checkbox">
                <span class="check-mark" style="display: none;">✓</span>
            </div>
            <div class="option-text">${option}</div>
        </div>
    `).join('');

    // 添加点击事件
    optionsView.querySelectorAll('.vote-option-item').forEach(item => {
        item.addEventListener('click', () => {
            const option = item.dataset.option;

            if (type === 'single') {
                // 单选：清除其他选择
                selectedOptions.clear();
                optionsView.querySelectorAll('.vote-option-item').forEach(i => {
                    i.classList.remove('selected');
                    i.querySelector('.check-mark').style.display = 'none';
                });
                selectedOptions.add(option);
                item.classList.add('selected');
                item.querySelector('.check-mark').style.display = 'block';
            } else {
                // 多选：切换选择
                if (selectedOptions.has(option)) {
                    selectedOptions.delete(option);
                    item.classList.remove('selected');
                    item.querySelector('.check-mark').style.display = 'none';
                } else {
                    selectedOptions.add(option);
                    item.classList.add('selected');
                    item.querySelector('.check-mark').style.display = 'block';
                }
            }
        });
    });
}

/**
 * 显示文本输入
 */
function showTextView() {
    document.getElementById('options-view').style.display = 'none';
    document.getElementById('text-view').style.display = 'block';
    document.getElementById('rating-view').style.display = 'none';

    document.getElementById('text-answer').value = '';
    document.getElementById('char-count').textContent = '0';
}

/**
 * 显示评分
 */
function showRatingView() {
    document.getElementById('options-view').style.display = 'none';
    document.getElementById('text-view').style.display = 'none';
    document.getElementById('rating-view').style.display = 'block';

    // 重置星级
    document.querySelectorAll('.star').forEach(star => {
        star.classList.remove('active');
    });
    document.getElementById('rating-label').textContent = '请选择评分';
}

/**
 * 选择评分
 */
function selectRating(rating) {
    selectedRating = rating;

    // 更新星级显示
    document.querySelectorAll('.star').forEach(star => {
        const starRating = parseInt(star.dataset.rating);
        if (starRating <= rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });

    document.getElementById('rating-label').textContent = `您的评分: ${rating} 分`;
}

/**
 * 提交投票
 */
async function submitVote() {
    if (!currentVote) return;

    let answer = null;

    if (currentVote.type === 'single') {
        if (selectedOptions.size === 0) {
            showMessage('请选择一个选项', 'error');
            return;
        }
        answer = { selected: Array.from(selectedOptions)[0] };
    } else if (currentVote.type === 'multiple') {
        if (selectedOptions.size === 0) {
            showMessage('请至少选择一个选项', 'error');
            return;
        }
        answer = { selected: Array.from(selectedOptions) };
    } else if (currentVote.type === 'text') {
        const text = document.getElementById('text-answer').value.trim();
        if (!text) {
            showMessage('请输入答案', 'error');
            return;
        }
        answer = { text };
    } else if (currentVote.type === 'rating') {
        if (selectedRating === 0) {
            showMessage('请选择评分', 'error');
            return;
        }
        answer = { rating: selectedRating };
    }

    try {
        await apiRequest('/api/participant/vote', {
            method: 'POST',
            headers: { 'X-Session-ID': sessionId },
            body: JSON.stringify({
                vote_id: currentVote.vote_id,
                answer
            })
        });

        // 显示成功状态
        document.getElementById('voting-view').style.display = 'none';
        document.getElementById('success-view').style.display = 'block';
    } catch (error) {
        showMessage('提交失败: ' + error.message, 'error');
    }
}

/**
 * 处理投票结束
 */
function handleVoteEnded(data) {
    // 保持在成功状态
    if (document.getElementById('success-view').style.display === 'block') {
        // 可以显示结果
    }
}

/**
 * 处理退出投票
 */
function handleVoteExited() {
    // 回到等待状态
    document.getElementById('waiting-view').style.display = 'block';
    document.getElementById('voting-view').style.display = 'none';
    document.getElementById('success-view').style.display = 'none';
    currentVote = null;
}
