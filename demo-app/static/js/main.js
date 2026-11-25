/**
 * 主JavaScript文件 - 提供基础交互功能
 */

// API基础配置
const API_CONFIG = {
    baseURL: '/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// 通用工具函数
class Utils {
    /**
     * 格式化时间戳
     */
    static formatTime(timestamp) {
        if (!timestamp) return '-';
        const date = new Date(timestamp);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * 格式化时长（秒转分钟）
     */
    static formatDuration(seconds) {
        if (!seconds && seconds !== 0) return '-';
        if (seconds < 60) {
            return `${seconds}秒`;
        }
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}分${remainingSeconds}秒`;
    }

    /**
     * 格式化百分比
     */
    static formatPercent(value) {
        if (value === undefined || value === null) return '-';
        return `${(value * 100).toFixed(1)}%`;
    }

    /**
     * 显示通知消息
     */
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
        
        // 点击关闭
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        });
    }

    /**
     * 防抖函数
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * 节流函数
     */
    static throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// API请求封装
class ApiService {
    /**
     * 发起GET请求
     */
    static async get(endpoint) {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
                method: 'GET',
                headers: API_CONFIG.headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`GET ${endpoint} failed:`, error);
            Utils.showNotification(`请求失败: ${error.message}`, 'error');
            throw error;
        }
    }

    /**
     * 发起POST请求
     */
    static async post(endpoint, data = {}) {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
                method: 'POST',
                headers: API_CONFIG.headers,
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`POST ${endpoint} failed:`, error);
            Utils.showNotification(`操作失败: ${error.message}`, 'error');
            throw error;
        }
    }

    /**
     * 获取文档信息
     */
    static async getDocument() {
        return this.get('/document');
    }

    /**
     * 开始审查
     */
    static async startReview() {
        return this.post('/review/start');
    }

    /**
     * 获取审查进度
     */
    static async getReviewProgress() {
        return this.get('/review/progress');
    }

    /**
     * 获取审查结果
     */
    static async getReviewResults() {
        return this.get('/review/results');
    }

    /**
     * 获取指标数据
     */
    static async getMetrics() {
        return this.get('/metrics');
    }

    /**
     * 重试节点
     */
    static async retryNode(nodeId) {
        return this.post(`/nodes/${nodeId}/retry`);
    }
}

// 状态管理
class StateManager {
    constructor() {
        this.state = {
            document: null,
            reviewState: 'not_started',
            nodes: [],
            results: [],
            metrics: null
        };
        this.listeners = new Set();
    }

    /**
     * 更新状态并通知监听器
     */
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notifyListeners();
    }

    /**
     * 添加状态监听器
     */
    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    /**
     * 通知所有监听器
     */
    notifyListeners() {
        this.listeners.forEach(listener => listener(this.state));
    }

    /**
     * 加载初始数据
     */
    async loadInitialData() {
        try {
            const [documentRes, progressRes] = await Promise.all([
                ApiService.getDocument(),
                ApiService.getReviewProgress()
            ]);

            this.setState({
                document: documentRes.data,
                reviewState: progressRes.data.review_state,
                nodes: Object.values(progressRes.data.node_states)
            });

            return true;
        } catch (error) {
            console.error('Failed to load initial data:', error);
            return false;
        }
    }
}

// 应用初始化
class App {
    constructor() {
        this.stateManager = new StateManager();
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        // 加载初始数据
        this.stateManager.loadInitialData().then(success => {
            if (success) {
                console.log('App initialized successfully');
            } else {
                console.warn('App initialization completed with warnings');
            }
        });

        // 添加全局事件监听
        this.setupGlobalListeners();
    }

    /**
     * 设置全局事件监听器
     */
    setupGlobalListeners() {
        // 窗口大小变化时重新布局
        window.addEventListener('resize', Utils.throttle(() => {
            this.handleResize();
        }, 250));

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.handlePageVisible();
            }
        });

        // 全局错误处理
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            Utils.showNotification('发生未知错误，请刷新页面重试', 'error');
        });

        // 未处理的Promise rejection
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            Utils.showNotification('操作处理失败，请稍后重试', 'error');
        });
    }

    /**
     * 处理窗口大小变化
     */
    handleResize() {
        // 可以在这里添加响应式布局逻辑
        const isMobile = window.innerWidth <= 768;
        document.documentElement.setAttribute('data-device', isMobile ? 'mobile' : 'desktop');
    }

    /**
     * 处理页面可见性变化
     */
    handlePageVisible() {
        // 页面恢复可见时刷新数据
        this.stateManager.loadInitialData();
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 创建全局应用实例
    window.app = new App();
    
    // 初始化设备类型
    const isMobile = window.innerWidth <= 768;
    document.documentElement.setAttribute('data-device', isMobile ? 'mobile' : 'desktop');
    
    // 添加CSS变量支持检测
    if (!window.CSS || !CSS.supports('color', 'var(--color-primary)')) {
        console.warn('Browser does not support CSS Custom Properties');
        // 可以在这里添加降级处理
    }
    
    console.log('Demo application initialized successfully');
});

// 全局样式
const globalStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: var(--spacing-md) var(--spacing-lg);
    background-color: var(--color-white);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md);
    min-width: 300px;
    max-width: 500px;
    animation: slideIn 0.3s ease-out;
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.notification-info {
    border-left: 4px solid var(--color-primary);
}

.notification-success {
    border-left: 4px solid var(--color-green);
}

.notification-warning {
    border-left: 4px solid var(--color-yellow);
}

.notification-error {
    border-left: 4px solid var(--color-red);
}

.notification-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    color: var(--color-secondary);
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}

.notification-close:hover {
    background-color: var(--color-light);
}

.notification.fade-out {
    opacity: 0;
    transform: translateX(100%);
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

[data-device="mobile"] .notification {
    left: 20px;
    right: 20px;
    min-width: auto;
    max-width: none;
    animation: slideInMobile 0.3s ease-out;
}

@keyframes slideInMobile {
    from {
        opacity: 0;
        transform: translateY(-100%);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

[data-device="mobile"] .notification.fade-out {
    transform: translateY(-100%);
}
`;

// 注入全局样式
const styleSheet = document.createElement('style');
styleSheet.textContent = globalStyles;
document.head.appendChild(styleSheet);