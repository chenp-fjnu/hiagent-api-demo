/**
 * HiAgent API Demo - 前端交互逻辑
 */

class HiAgentDemo {
    constructor() {
        this.config = {
            apiBaseUrl: '',
            apiKey: '',
            agentId: '',
            userId: '',
            streamingMode: false
        };
        this.isConnected = false;
        this.isProcessing = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadConfig();
        this.updateUI();
        this.updateTimestamp();
        
        // 定期更新时间戳
        setInterval(() => this.updateTimestamp(), 1000);
    }
    
    bindEvents() {
        // 发送消息
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        messageInput.addEventListener('input', this.handleInputChange.bind(this));
        messageInput.addEventListener('keydown', this.handleKeyDown.bind(this));
        sendBtn.addEventListener('click', this.sendMessage.bind(this));
        
        // 配置相关
        document.getElementById('configBtn').addEventListener('click', this.showConfigModal.bind(this));
        document.getElementById('configClose').addEventListener('click', this.hideConfigModal.bind(this));
        document.getElementById('configForm').addEventListener('submit', this.saveConfig.bind(this));
        document.getElementById('testConnection').addEventListener('click', this.testConnection.bind(this));
        
        // 其他按钮
        document.getElementById('clearBtn').addEventListener('click', this.clearChat.bind(this));
        document.getElementById('notificationClose').addEventListener('click', this.hideNotification.bind(this));
        
        // 示例按钮
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.getAttribute('data-message');
                this.setMessageInput(message);
            });
        });
        
        // 点击模态框外部关闭
        document.getElementById('configModal').addEventListener('click', (e) => {
            if (e.target.id === 'configModal') {
                this.hideConfigModal();
            }
        });
        
        // 页面加载完成检查
        window.addEventListener('load', () => {
            this.showWelcomeMessage();
        });
    }
    
    loadConfig() {
        // 从 localStorage 加载配置
        const savedConfig = localStorage.getItem('hiagent_demo_config');
        if (savedConfig) {
            try {
                this.config = { ...this.config, ...JSON.parse(savedConfig) };
            } catch (e) {
                console.warn('无法解析保存的配置:', e);
            }
        }
        
        // 更新配置表单
        this.updateConfigForm();
    }
    
    saveConfig() {
        // 从表单获取配置
        this.config.apiBaseUrl = document.getElementById('apiBaseUrl').value.trim();
        this.config.apiKey = document.getElementById('apiKey').value.trim();
        this.config.agentId = document.getElementById('agentId').value.trim();
        this.config.userId = document.getElementById('userId').value.trim();
        this.config.streamingMode = document.getElementById('streamingMode').checked;
        
        // 保存到 localStorage
        localStorage.setItem('hiagent_demo_config', JSON.stringify(this.config));
        
        this.updateUI();
        this.hideConfigModal();
        this.showNotification('配置已保存', 'success');
        
        return false; // 阻止表单提交
    }
    
    updateConfigForm() {
        document.getElementById('apiBaseUrl').value = this.config.apiBaseUrl;
        document.getElementById('apiKey').value = this.config.apiKey;
        document.getElementById('agentId').value = this.config.agentId;
        document.getElementById('userId').value = this.config.userId;
        document.getElementById('streamingMode').checked = this.config.streamingMode;
    }
    
    updateUI() {
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        const agentInfo = document.getElementById('agentInfo');
        
        // 检查是否已配置
        const isConfigured = this.config.apiBaseUrl && this.config.apiKey && this.config.agentId;
        
        sendBtn.disabled = !isConfigured || this.isProcessing;
        messageInput.disabled = !isConfigured || this.isProcessing;
        
        // 更新状态显示
        const statusDot = document.getElementById('connectionStatus');
        const statusText = document.getElementById('statusText');
        
        if (isConfigured) {
            if (this.isConnected) {
                statusDot.className = 'fas fa-circle status-dot connected';
                statusText.textContent = '已连接';
            } else {
                statusDot.className = 'fas fa-circle status-dot connecting';
                statusText.textContent = '未连接';
            }
        } else {
            statusDot.className = 'fas fa-circle status-dot';
            statusText.textContent = '未配置';
        }
        
        // 更新智能体信息
        agentInfo.textContent = this.config.agentId ? `智能体: ${this.config.agentId}` : '请配置Agent ID';
        
        // 更新字符计数
        this.updateCharCount();
    }
    
    updateCharCount() {
        const messageInput = document.getElementById('messageInput');
        const charCount = document.querySelector('.char-count');
        const currentLength = messageInput.value.length;
        const maxLength = 1000;
        
        charCount.textContent = `${currentLength}/${maxLength}`;
        
        if (currentLength > maxLength * 0.9) {
            charCount.style.color = '#ef4444';
        } else if (currentLength > maxLength * 0.7) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#64748b';
        }
    }
    
    handleInputChange(e) {
        const textarea = e.target;
        
        // 自动调整高度
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        
        this.updateCharCount();
        this.updateUI();
    }
    
    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isProcessing) return;
        
        // 清空输入框
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // 添加用户消息到界面
        this.addMessage('user', message);
        
        // 显示加载状态
        this.setProcessing(true);
        
        try {
            const response = await this.callHiAgentAPI(message);
            
            if (response.success) {
                this.addMessage('assistant', response.reply);
                this.isConnected = true;
            } else {
                this.addMessage('system', `错误: ${response.error}`);
                this.isConnected = false;
            }
        } catch (error) {
            console.error('API调用失败:', error);
            this.addMessage('system', `网络错误: ${error.message}`);
            this.isConnected = false;
        } finally {
            this.setProcessing(false);
        }
    }
    
    async callHiAgentAPI(message) {
        // 模拟API调用（在实际应用中，这里应该调用真实的HiAgent API）
        // 由于这是demo，我们模拟一些响应
        
        const apiUrl = this.config.apiBaseUrl ? 
            `${this.config.apiBaseUrl}/api/v1/agents/${this.config.agentId}/chat` : null;
        
        if (!apiUrl || !this.config.apiKey) {
            // 模拟无配置情况
            await this.sleep(1000);
            return {
                success: false,
                error: '请先在配置中设置API Base URL和API Key'
            };
        }
        
        // 模拟API请求（替换为真实的fetch调用）
        try {
            // 实际实现中应该使用：
            /*
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.config.userId || 'demo_user'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return {
                success: true,
                reply: data.reply || data.message || '暂无回复'
            };
            */
            
            // Demo模拟：随机模拟成功/失败
            await this.sleep(1500); // 模拟网络延迟
            
            const success = Math.random() > 0.2; // 80%成功率
            
            if (success) {
                // 根据消息内容返回相应回复
                let reply = this.generateReply(message);
                return {
                    success: true,
                    reply: reply
                };
            } else {
                throw new Error('模拟的API错误');
            }
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    generateReply(message) {
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('你好') || lowerMessage.includes('hello')) {
            return "你好！我是HiAgent智能体，很高兴为您服务。我可以帮助您处理各种任务，包括问答、文本生成、数据分析等。您有什么需要帮助的吗？";
        } else if (lowerMessage.includes('做什么') || lowerMessage.includes('帮助')) {
            return "我可以为您提供以下服务：\n• 智能对话和问答\n• 文本创作和编辑\n• 数据分析和处理\n• 代码编写和调试\n• 知识查询和学习\n\n请告诉我您需要什么帮助！";
        } else if (lowerMessage.includes('人工智能') || lowerMessage.includes('ai')) {
            return "人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，旨在创建能够模拟人类智能行为的机器和软件。AI技术包括机器学习、深度学习、自然语言处理、计算机视觉等领域，在现代社会中有着广泛的应用前景。";
        } else if (lowerMessage.includes('天气')) {
            return "抱歉，我无法获取实时天气信息。作为HiAgent智能体，我可以帮您解答一般性问题、协助工作、学习知识等。如果您需要天气信息，建议您使用专门的天气应用程序或网站。";
        } else if (lowerMessage.includes('谢谢') || lowerMessage.includes('感谢')) {
            return "不客气！很高兴能帮助到您。如果还有其他问题，请随时告诉我。HiAgent随时为您服务！";
        } else if (lowerMessage.includes('再见') || lowerMessage.includes('拜拜')) {
            return "再见！感谢使用HiAgent API Demo，期待为您提供更多帮助！";
        } else {
            return `感谢您的消息："${message}"。作为HiAgent智能体，我正在学习和改进中。虽然我可能无法立即回答所有问题，但我会尽力为您提供有用的信息。如果您有具体问题，请详细描述，我很乐意帮助您！`;
        }
    }
    
    async testConnection() {
        const testBtn = document.getElementById('testConnection');
        const originalText = testBtn.innerHTML;
        
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 测试中...';
        testBtn.disabled = true;
        
        try {
            // 模拟连接测试
            await this.sleep(2000);
            
            const success = Math.random() > 0.3; // 70%成功率
            
            if (success) {
                this.showNotification('连接测试成功！', 'success');
                this.isConnected = true;
            } else {
                this.showNotification('连接测试失败，请检查配置', 'error');
                this.isConnected = false;
            }
        } catch (error) {
            this.showNotification(`连接测试失败: ${error.message}`, 'error');
        } finally {
            testBtn.innerHTML = originalText;
            testBtn.disabled = false;
            this.updateUI();
        }
    }
    
    addMessage(type, content) {
        const chatMessages = document.getElementById('chatMessages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const avatar = type === 'user' ? 'fas fa-user' : 
                      type === 'assistant' ? 'fas fa-robot' : 
                      'fas fa-cog';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatar}"></i>
            </div>
            <div class="message-content">
                ${content.split('\n').map(line => `<p>${this.escapeHtml(line)}</p>`).join('')}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 添加动画效果
        requestAnimationFrame(() => {
            messageDiv.style.animation = 'messageSlideIn 0.3s ease';
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    setProcessing(processing) {
        this.isProcessing = processing;
        this.updateUI();
        
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (processing) {
            loadingIndicator.style.display = 'flex';
        } else {
            loadingIndicator.style.display = 'none';
        }
    }
    
    setMessageInput(message) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = message;
        this.handleInputChange({ target: messageInput });
        messageInput.focus();
    }
    
    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        this.showWelcomeMessage();
    }
    
    showWelcomeMessage() {
        const welcomeHtml = `
            <div class="message welcome-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <h3>欢迎使用HiAgent API Demo</h3>
                    <p>这是一个演示HiAgent接口调用的交互式界面。</p>
                    <p>请先在配置中设置您的API密钥和Agent ID，然后开始对话。</p>
                </div>
            </div>
        `;
        
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages.children.length === 0 || 
            chatMessages.children[0].classList.contains('welcome-message')) {
            chatMessages.innerHTML = welcomeHtml;
        }
    }
    
    showConfigModal() {
        this.updateConfigForm();
        document.getElementById('configModal').style.display = 'flex';
    }
    
    hideConfigModal() {
        document.getElementById('configModal').style.display = 'none';
    }
    
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        const messageElement = document.getElementById('notificationMessage');
        
        messageElement.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'flex';
        
        // 自动隐藏
        setTimeout(() => {
            this.hideNotification();
        }, 5000);
    }
    
    hideNotification() {
        document.getElementById('notification').style.display = 'none';
    }
    
    updateTimestamp() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-CN', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('timestamp').textContent = timeString;
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.hiAgentDemo = new HiAgentDemo();
});

// 添加一些实用工具
window.utils = {
    // 格式化时间
    formatTime: (date) => {
        return new Intl.DateTimeFormat('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(date);
    },
    
    // 防抖函数
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 节流函数
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};