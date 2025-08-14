# MeetSpot + Eko 集成部署指南

## 🚀 快速部署

### 1. 安装Node.js依赖

```bash
cd app/eko_integration
npm install
```

### 2. 测试集成功能

```bash
# 测试eko集成
node test_integration.js --test
```

### 3. 启动增强版MeetSpot

```bash
# 回到项目根目录
cd ../..

# 启动服务器
python web_server.py
```

## 🎯 新增API端点

### 1. 智能推荐API
```
POST /api/smart_recommend
```

请求示例：
```json
{
  "query": "我需要在北京朝阳区和海淀区之间找一个适合商务会谈的咖啡馆，要有停车位和WiFi",
  "mode": "intelligent"
}
```

### 2. 对话式推荐API
```
POST /api/conversational_recommend
```

请求示例：
```json
{
  "message": "帮我找个会面地点",
  "conversation": [
    {"user": "我在朝阳区", "assistant": "好的，还有其他参与者吗？"}
  ]
}
```

## 🧠 AI模型配置

- **提供商**: OpenRouter
- **模型**: anthropic/claude-3.5-sonnet
- **API地址**: https://openrouter.ai/api/v1
- **已配置密钥**: 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

## 📱 使用示例

### 自然语言推荐
```
用户输入：
"我们团队5个人要开会，分别在：
1. 朝阳区国贸
2. 海淀区五道口
3. 丰台区总部基地
需要一个安静的咖啡馆，有包间最好，预算200元左右"

系统输出：
自动分析位置 → 计算中心点 → 搜索附近场所 → 智能排序 → 生成可视化报告
```

### 渐进式对话
```
用户：帮我找个会面地点
助手：好的！请告诉我参与者的大概位置？

用户：一个在朝阳区，一个在海淀区
助手：明白了。您希望找什么类型的场所？比如咖啡馆、餐厅还是其他？

用户：咖啡馆，要安静一些
助手：好的，为您推荐适合的咖啡馆...
```

## 🔧 技术架构

- **多Agent协作**: LocationAgent + POISearchAgent + RecommendationAgent + VisualizationAgent
- **智能工作流**: 自动规划和执行复杂推荐任务
- **降级机制**: 自动切换到传统模式保证可用性
- **流式处理**: 实时反馈执行过程

## 📊 优势对比

| 功能 | 传统模式 | Eko智能模式 |
|-----|---------|------------|
| 输入方式 | 结构化参数 | 自然语言 |
| 处理能力 | 单一推荐 | 多维度分析 |
| 交互方式 | 一次性 | 多轮对话 |
| 智能程度 | 规则匹配 | AI推理 |
| 扩展性 | 有限 | 高度灵活 |

## 🎉 立即体验

访问 http://localhost:8000 体验增强版MeetSpot！
