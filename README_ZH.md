<div align="center">

# 🚀 EkoMeet

<img src="docs/logo.png" alt="EkoMeet Logo" width="200"/>

**AI驱动的智能会面点推荐系统**

基于Eko AI框架的智能会面点推荐系统，通过多Agent协作实现自然语言驱动的地点推荐。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![Eko Framework](https://img.shields.io/badge/Eko-v3.0--alpha-purple.svg)](https://github.com/FellouAI/eko)

🎯 **AI智能驱动** | 🤖 **多Agent架构** | 🌐 **自然语言交互**

</div>

## ✨ 核心特性

- 🤖 **多Agent智能协作** - 基于Eko框架的分布式AI架构
- 🌍 **智能地理分析** - 高德地图API集成，精准位置计算
- 💬 **自然语言交互** - 一句话描述需求，AI智能理解
- 🎯 **个性化推荐** - 基于用户偏好的智能排序算法
- 📱 **响应式界面** - 适配PC和移动端的现代化UI
- ⚡ **实时处理** - 异步处理，快速响应

## 🏗️ 技术架构

```
前端界面 (HTML/CSS/JS) 
    ↓
FastAPI 后端服务
    ↓
Eko AI 框架
    ↓
多Agent协作系统
    ↓
- LocationAgent (地理位置处理)
- POISearchAgent (场所搜索)  
- RecommendationAgent (智能推荐)
- VisualizationAgent (结果可视化)
```

## 🛠️ 技术栈

- **后端**: Python + FastAPI
- **AI框架**: Eko AI Framework
- **LLM**: OpenRouter (Claude-3.5-Sonnet)
- **地图服务**: 高德地图API
- **前端**: HTML5 + CSS3 + JavaScript
- **类型系统**: TypeScript (工具开发)

<div align="center">

### 主界面
<img src="docs/show1.png" alt="Main Interface" width="800"/>

### 多场所选择
<img src="docs/show2.png" alt="Multi-Venue Selection" width="800"/>

### 推荐结果
<img src="docs/show3.png" alt="Recommendation Results" width="800"/>

### 详细信息
<img src="docs/show4.png" alt="Detailed Information" width="800"/>

</div>

## 🌟 功能特色

EkoMeet是一个智能会面点推荐系统，基于多个参与者的地理位置计算最佳会面地点，并推荐附近的优质场所。

### ✨ 主要功能

- 🎯 **智能中心点计算**: 基于多个位置计算几何中心，确保对所有人公平
- 🏢 **多场景推荐**: 同时搜索多种场所类型（咖啡馆 + 餐厅 + 图书馆）
- 📍 **多地点支持**: 支持2-10个参与者位置
- 🎨 **直观用户界面**: 现代化响应式设计
- 🚀 **实时推荐**: 快速生成个性化推荐
- 📊 **智能排序**: 基于评分、距离和用户需求的综合排序

### 🔥 最新优化

- ✅ **多场景推荐**: 支持同时选择多种场所类型
- ✅ **前端多选界面**: 直观的场所类型选择界面
- ✅ **智能排序算法**: 场景匹配奖励机制
- ✅ **性能监控**: 完整的性能统计和健康检查
- ✅ **错误处理**: 健壮的异常处理机制

## 🚀 快速开始

### 系统要求

- Python 3.11+
- 高德地图API密钥
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/JasonRobertDestiny/EkoMeet.git
cd EkoMeet
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**
```bash
cp config/config.toml.example config/config.toml
```

编辑 `config/config.toml` 文件，添加您的高德地图API密钥：
```toml
[amap]
api_key = "your_amap_api_key_here"
```

4. **启动服务**
```bash
python web_server.py
```

5. **访问应用**
打开浏览器访问: http://127.0.0.1:8000

## 📱 使用方法

### 基础使用

1. **输入位置**: 添加2-10个参与者位置
2. **选择场景**: 选择1-3种场所类型（咖啡馆、餐厅、图书馆等）
3. **设置需求**: 添加特殊需求（方便停车、环境安静等）
4. **获取推荐**: 点击搜索获得智能推荐

### 高级功能

- **多场景组合**: 同时搜索"咖啡馆 餐厅"获得更多选择
- **自定义关键词**: 输入特殊场所类型如"密室逃脱"
- **筛选条件**: 按评分、距离、价格筛选
- **特殊需求**: 支持停车、WiFi、包间等需求

## 🏗️ 系统架构

### 后端技术栈

- **FastAPI**: 高性能Web框架
- **Pydantic**: 数据验证和设置管理
- **aiohttp**: 异步HTTP客户端
- **高德地图API**: 地理编码和POI搜索

### 前端技术栈

- **HTML5 + CSS3**: 响应式设计
- **原生JavaScript**: 轻量级交互
- **Boxicons**: 图标库
- **现代UI设计**: 渐变和玻璃效果

### 核心算法

- **几何中心计算**: 多点质心算法
- **智能排序**: 多因子评分系统
- **场景匹配**: 关键词匹配奖励
- **去重算法**: 基于名称和地址的智能去重

## 📊 API文档

### 主要端点

- `GET /` - 首页重定向
- `POST /api/find_meetspot` - 会面点推荐
- `GET /health` - 健康检查
- `GET /workspace/js_src/{filename}` - 生成的推荐页面

### 请求示例

```bash
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": ["北京大学", "清华大学"],
    "keywords": "咖啡馆 餐厅",
    "user_requirements": "方便停车"
  }'
```

### 响应示例

```json
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250624_12345678.html",
  "locations_count": 2,
  "keywords": "咖啡馆 餐厅",
  "processing_time": 0.52
}
```

## 🔧 开发环境设置

### 环境配置

1. **Python环境**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. **安装开发依赖**
```bash
pip install -r requirements.txt
```

3. **环境变量配置**
```bash
export AMAP_API_KEY="your_api_key"
export PYTHON_ENV="development"
```

### 代码规范

- 遵循PEP8 Python编码规范
- 使用类型提示
- 编写文档字符串
- 代码提交前进行格式化

## 🚢 部署指南

### 本地部署

```bash
# 启动开发服务器
python web_server.py

# 或使用npm脚本
npm run dev
```

### 生产部署

支持多种部署方式：
- **Render**: 使用 `render.yaml` 配置
- **Railway**: 自动检测部署
- **Docker**: 容器化部署
- **传统服务器**: 使用Nginx + Gunicorn

### 环境变量

必需的环境变量：
- `AMAP_API_KEY`: 高德地图API密钥
- `PORT`: 服务端口（默认8000）

可选的环境变量：
- `PYTHON_ENV`: 运行环境（development/production）
- `LOG_LEVEL`: 日志级别（默认info）

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 问题报告

如果您发现bug或有功能建议，请：
1. 查看现有Issues
2. 创建详细的Issue描述
3. 提供复现步骤和环境信息

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目链接**: [https://github.com/JasonRobertDestiny/EkoMeet](https://github.com/JasonRobertDestiny/EkoMeet)
- **问题反馈**: [Issues](https://github.com/JasonRobertDestiny/EkoMeet/issues)
- **功能建议**: [Discussions](https://github.com/JasonRobertDestiny/EkoMeet/discussions)

## 🙏 致谢

- [Eko AI Framework](https://github.com/FellouAI/eko) - 强大的AI框架支持
- [高德地图API](https://lbs.amap.com/) - 精准的地理信息服务
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架
- [Boxicons](https://boxicons.com/) - 精美的图标库

## 📊 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=JasonRobertDestiny/EkoMeet&type=Date)](https://www.star-history.com/#JasonRobertDestiny/EkoMeet&Date)

---

<div align="center">

**如果这个项目对您有帮助，请给它一个⭐️!**

</div>