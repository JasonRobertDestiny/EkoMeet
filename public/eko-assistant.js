/**
 * EkoMeet 智能助手 - 前端组件
 * 基于 OpenRouter API 的智能对话助手
 * 专为 EkoMeet 项目提供智能辅助和用户引导
 */

class EkoAssistant {
    constructor(options = {}) {
        this.apiKey = options.apiKey || null;
        this.model = options.model || 'Qwen/Qwen2.5-72B-Instruct';
        this.baseUrl = 'https://api.siliconflow.cn/v1';
        this.isInitialized = false;
        this.isOpen = false;
        this.conversationHistory = [];
        
        // 项目相关的系统提示词
        this.systemPrompt = `你是 EkoMeet 的专业智能助手 Eko，拥有温暖友好的个性，精通 EkoMeet 智能会面点推荐系统的所有功能。

**核心身份：**
- EkoMeet 智能会面点推荐系统的官方 AI 助手
- 基于 Eko AI 框架构建的多Agent智能协作系统专家
- 专门协助用户使用 EkoMeet 进行多人会面地点推荐

**技术背景知识：**
**系统架构：**
- 前端：HTML5 + CSS3 + JavaScript（响应式设计）
- 后端：Python + FastAPI（高性能异步Web框架）
- AI框架：Eko AI Framework（多Agent智能协作）
- 地图服务：高德地图API（地理编码、POI搜索）
- 模型：Qwen/Qwen2.5-72B-Instruct（通过硅基流动API调用）

**核心功能模块：**
1. **多Agent智能协作系统：**
   - LocationAgent：地理位置处理和地址解析
   - POISearchAgent：场所搜索和数据获取
   - RecommendationAgent：智能推荐算法
   - VisualizationAgent：结果可视化生成

2. **智能推荐引擎：**
   - 支持场所类型：咖啡馆、餐厅、图书馆、商场、公园、电影院、篮球场、健身房、KTV、博物馆等
   - 几何中心点计算：基于多个地点计算最优会面位置
   - 智能排序：综合评分、距离、用户需求进行排序
   - 主题化推荐：每种场所类型都有专门的主题和图标设计

3. **API接口系统：**
   - /api/find_ekomeet: 标准推荐API（支持2-10个地点）
   - /api/eko/recommend: Eko智能推荐API
   - /api/conversation/: 对话式推荐API
   - /api/config/siliconflow-key: AI模型配置获取

**工作流程：**
1. 用户输入2-10个地点位置
2. LocationAgent进行地理编码，将地址转换为坐标
3. 系统计算几何中心点，确保对所有人公平
4. POISearchAgent基于中心点和关键词搜索周边场所
5. RecommendationAgent应用智能算法进行排序和筛选
6. VisualizationAgent生成包含地图和详细信息的HTML页面
7. 返回个性化的推荐结果

**对话风格：**
- 使用温暖、友好的语气
- 可以进行日常问候和轻松对话
- 会主动询问用户需求，提供贴心建议
- 用生动的表达方式解释复杂概念
- 适当使用emoji让对话更有趣

**回答原则：**
- 可以进行友好的日常对话和问候
- 详细解答所有EkoMeet相关问题
- 主动提供使用建议和最佳实践
- 用生动的例子解释功能特性
- 在适当时候引导用户体验系统功能
- 不提供其他产品或竞品的信息
- 不进行与会面地点推荐无关的专业咨询

**你的使命：**
让每个用户都能轻松、愉快地使用EkoMeet找到最适合的会面地点，成为用户最信赖的聚会规划伙伴！`;

        this.init();
    }

    async init() {
        try {
            await this.loadApiKey();
            this.createAssistantUI();
            this.bindEvents();
            this.isInitialized = true;
            console.log('EkoAssistant initialized successfully');
        } catch (error) {
            console.error('Failed to initialize EkoAssistant:', error);
        }
    }

    async loadApiKey() {
        // 从环境变量或配置中加载API密钥
        try {
            const response = await fetch('/api/config/siliconflow-key');
            if (response.ok) {
                const data = await response.json();
                this.apiKey = data.apiKey;
                this.baseUrl = data.baseUrl || 'https://api.siliconflow.cn/v1';
                this.model = data.model || 'Qwen/Qwen2.5-72B-Instruct';
            }
        } catch (error) {
            console.warn('Failed to load SiliconFlow API key from backend:', error);
        }
    }

    createAssistantUI() {
        // 创建助手按钮
        const assistantButton = document.createElement('div');
        assistantButton.id = 'eko-assistant-button';
        assistantButton.innerHTML = `
            <div class="eko-btn-icon">
                <i class='bx bx-bot'></i>
            </div>
            <span class="eko-btn-text">Eko助手</span>
        `;
        
        // 创建聊天窗口
        const chatWindow = document.createElement('div');
        chatWindow.id = 'eko-assistant-window';
        chatWindow.innerHTML = `
            <div class="eko-header">
                <div class="eko-header-info">
                    <i class='bx bx-bot'></i>
                    <span>Eko 智能助手</span>
                </div>
                <button class="eko-close-btn">
                    <i class='bx bx-x'></i>
                </button>
            </div>
            <div class="eko-messages" id="eko-messages">
                <div class="eko-message eko-message-assistant">
                    <div class="eko-message-content">
                        👋 你好！我是 EkoMeet 的智能助手 Eko，很高兴认识你！
                        <br><br>
                        🎆 我是你的专属聚会规划伙伴，就像一个熟悉本地的好朋友一样，随时为你推荐最适合的会面地点。
                        <br><br>
                        💬 你可以和我随意聊天，比如：
                        <br>• “今天想约朋友吃饭，帮我推荐个地方吧”
                        <br>• “EkoMeet怎么用呀？”
                        <br>• 或者就是简单的“你好”都可以！
                        <br><br>
                        🎉 来，说说你想做什么吧！
                    </div>
                </div>
            </div>
            <div class="eko-input-area">
                <input type="text" id="eko-input" placeholder="输入您的问题..." />
                <button id="eko-send-btn">
                    <i class='bx bx-send'></i>
                </button>
            </div>
        `;

        // 添加到页面
        document.body.appendChild(assistantButton);
        document.body.appendChild(chatWindow);

        // 添加样式
        this.addStyles();
    }

    addStyles() {
        const styles = `
            #eko-assistant-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 50px;
                padding: 15px 20px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            #eko-assistant-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }

            .eko-btn-icon {
                font-size: 20px;
            }

            .eko-btn-text {
                font-size: 14px;
                font-weight: 500;
            }

            #eko-assistant-window {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                z-index: 1001;
                display: none;
                flex-direction: column;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                overflow: hidden;
            }

            .eko-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .eko-header-info {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 500;
            }

            .eko-close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
            }

            .eko-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }

            .eko-message {
                display: flex;
                flex-direction: column;
                max-width: 80%;
            }

            .eko-message-assistant {
                align-self: flex-start;
            }

            .eko-message-user {
                align-self: flex-end;
            }

            .eko-message-content {
                padding: 12px 16px;
                border-radius: 15px;
                font-size: 14px;
                line-height: 1.5;
            }

            .eko-message-assistant .eko-message-content {
                background: #f0f0f0;
                color: #333;
            }

            .eko-message-user .eko-message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .eko-input-area {
                padding: 20px;
                border-top: 1px solid #eee;
                display: flex;
                gap: 10px;
            }

            #eko-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 25px;
                outline: none;
                font-size: 14px;
            }

            #eko-input:focus {
                border-color: #667eea;
            }

            #eko-send-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            #eko-send-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            @media (max-width: 768px) {
                #eko-assistant-window {
                    width: 300px;
                    height: 400px;
                }
                
                .eko-btn-text {
                    display: none;
                }
                
                #eko-assistant-button {
                    padding: 15px;
                    border-radius: 50%;
                }
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    bindEvents() {
        const button = document.getElementById('eko-assistant-button');
        const window = document.getElementById('eko-assistant-window');
        const closeBtn = document.querySelector('.eko-close-btn');
        const input = document.getElementById('eko-input');
        const sendBtn = document.getElementById('eko-send-btn');

        // 打开/关闭助手
        button.addEventListener('click', () => this.toggleAssistant());
        closeBtn.addEventListener('click', () => this.closeAssistant());

        // 发送消息
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    toggleAssistant() {
        const window = document.getElementById('eko-assistant-window');
        if (this.isOpen) {
            this.closeAssistant();
        } else {
            window.style.display = 'flex';
            this.isOpen = true;
        }
    }

    closeAssistant() {
        const window = document.getElementById('eko-assistant-window');
        window.style.display = 'none';
        this.isOpen = false;
    }

    async sendMessage() {
        const input = document.getElementById('eko-input');
        const message = input.value.trim();
        
        if (!message) return;

        // 显示用户消息
        this.addMessage(message, 'user');
        input.value = '';

        // 显示加载状态
        this.showTyping();

        try {
            // 调用硅基流动 API
            const response = await this.callSiliconFlow(message);
            this.hideTyping();
            this.addMessage(response, 'assistant');
        } catch (error) {
            this.hideTyping();
            this.addMessage('😅 哎呀，我这边遇到了点小问题！可能是网络不太稳定，或者我的"大脑"正在处理太多信息。\n\n💡 你可以：\n• 稍等一下再试试\n• 检查一下网络连接\n• 或者换个问题问我\n\n🤗 别担心，我很快就会恢复正常的！', 'assistant');
            console.error('SiliconFlow API error:', error);
        }
    }

    async callSiliconFlow(message) {
        if (!this.apiKey) {
            return '😔 抱歉，我的 API 密钥还未配置。\n\n📝 **配置步骤：**\n1. 访问 https://cloud.siliconflow.cn/ 获取 API 密钥\n2. 在 `.env` 文件中设置 `SILICONFLOW_API_KEY`\n3. 重启服务器\n\n👨‍💻 或者联系管理员协助配置。';
        }
        
        if (this.apiKey === 'sk-your_siliconflow_api_key_here') {
            return '🔑 API 密钥仍为默认占位符，请配置真实的硅基流动 API 密钥。\n\n🔗 获取地址： https://cloud.siliconflow.cn/';
        }

        // 构建对话历史
        const messages = [
            { role: 'system', content: this.systemPrompt },
            ...this.conversationHistory,
            { role: 'user', content: message }
        ];

        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.model,
                messages: messages,
                max_tokens: 500,
                temperature: 0.7,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        const assistantMessage = data.choices[0].message.content;

        // 更新对话历史
        this.conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: assistantMessage }
        );

        // 保持对话历史在合理长度内
        if (this.conversationHistory.length > 10) {
            this.conversationHistory = this.conversationHistory.slice(-8);
        }

        return assistantMessage;
    }

    addMessage(content, role) {
        const messagesContainer = document.getElementById('eko-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `eko-message eko-message-${role}`;
        
        messageDiv.innerHTML = `
            <div class="eko-message-content">${content}</div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTyping() {
        const messagesContainer = document.getElementById('eko-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'eko-typing';
        typingDiv.className = 'eko-message eko-message-assistant';
        typingDiv.innerHTML = `
            <div class="eko-message-content">
                Eko 正在思考...
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typing = document.getElementById('eko-typing');
        if (typing) {
            typing.remove();
        }
    }
}

// 初始化助手
document.addEventListener('DOMContentLoaded', () => {
    window.ekoAssistant = new EkoAssistant();
});