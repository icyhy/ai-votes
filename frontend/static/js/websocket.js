/**
 * WebSocket 客户端管理
 */
class WebSocketClient {
    constructor(clientType = 'display') {
        this.clientType = clientType;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.messageHandlers = {};
    }

    /**
     * 连接 WebSocket
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws?client_type=${this.clientType}`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket 连接成功');
            this.reconnectAttempts = 0;
            this.onOpen();
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('解析消息失败:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket 连接关闭');
            this.reconnect();
        };
    }

    /**
     * 重新连接
     */
    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
            console.error('WebSocket 重连失败,已达到最大重试次数');
        }
    }

    /**
     * 发送消息
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.error('WebSocket 未连接');
        }
    }

    /**
     * 处理接收到的消息
     */
    handleMessage(message) {
        const { type, data } = message;

        if (this.messageHandlers[type]) {
            this.messageHandlers[type](data);
        } else {
            console.log('未处理的消息类型:', type, data);
        }
    }

    /**
     * 注册消息处理器
     */
    on(messageType, handler) {
        this.messageHandlers[messageType] = handler;
    }

    /**
     * 连接成功回调(可被覆盖)
     */
    onOpen() {
        // 子类可以覆盖此方法
    }

    /**
     * 关闭连接
     */
    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

/**
 * 主题切换功能
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    // 从 localStorage 读取主题设置
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

/**
 * 工具函数 - HTTP 请求
 */
async function apiRequest(url, options = {}) {
    try {
        // 自动处理 URL 参数
        if (options.params) {
            const query = new URLSearchParams(options.params).toString();
            url = `${url}${url.includes('?') ? '&' : '?'}${query}`;
        }

        // 自动处理身份验证
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // 如果有 admin_token,自动加入(除非显式提供)
        const adminToken = localStorage.getItem('admin_token');
        if (adminToken && !url.includes('token=')) {
            url = `${url}${url.includes('?') ? '&' : '?'}token=${adminToken}`;
        }

        // 如果有 session_id,加入请求头
        const sessionId = localStorage.getItem('session_id');
        if (sessionId) {
            headers['X-Session-ID'] = sessionId;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            const error = await response.json();
            // 如果是 401 或 403,说明 session 失效
            if (response.status === 401 || response.status === 403) {
                if (window.location.pathname.includes('/host') || window.location.pathname.includes('/participant')) {
                    localStorage.removeItem('session_id');
                    window.location.href = '/signin';
                }
            }
            throw new Error(error.detail || '请求失败');
        }

        return await response.json();
    } catch (error) {
        console.error('API 请求失败:', error);
        throw error;
    }
}

/**
 * 显示提示消息
 */
function showMessage(message, type = 'info') {
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type} fade-in`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        border-radius: 8px;
        background-color: ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--danger)' : 'var(--primary)'};
        color: white;
        font-size: 16px;
        z-index: 9999;
        box-shadow: var(--shadow-lg);
    `;

    document.body.appendChild(messageEl);

    setTimeout(() => {
        messageEl.style.opacity = '0';
        setTimeout(() => messageEl.remove(), 300);
    }, 3000);
}
