<div align="center">

# 🚀 EkoMeet

<img src="docs/logo.png" alt="EkoMeet Logo" width="200"/>

**AI-Powered Meeting Spot Recommendation System**

基于Eko AI框架的智能会面点推荐系统，通过多Agent协作实现自然语言驱动的地点推荐。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Eko Framework](https://img.shields.io/badge/Eko-v3.0--alpha-purple.svg)](https://github.com/FellouAI/eko)

🎯 **AI-Driven Intelligence** | 🤖 **Multi-Agent Architecture** | 🌐 **Natural Language Interface**

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
Frontend (HTML/CSS/JS) 
    ↓
FastAPI Backend
    ↓
Eko AI Framework
    ↓
Multi-Agent System
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

### Main Interface
<img src="docs/show1.png" alt="Main Interface" width="800"/>

### Multi-Venue Selection
<img src="docs/show2.png" alt="Multi-Venue Selection" width="800"/>

### Recommendation Results
<img src="docs/show3.png" alt="Recommendation Results" width="800"/>

### Detailed Information
<img src="docs/show4.png" alt="Detailed Information" width="800"/>

</div>

## 🌟 Features

MeetSpot is an intelligent meeting point recommendation system that calculates optimal meeting locations based on multiple participants' geographical positions and recommends nearby venues.

### ✨ Core Features

- 🎯 **Smart Center Point Calculation**: Calculate geometric center based on multiple locations for fairness
- 🏢 **Multi-Scenario Recommendations**: Search multiple venue types simultaneously (cafes + restaurants + libraries)
- 📍 **Multi-Location Support**: Support 2-10 participant locations
- 🎨 **Intuitive User Interface**: Modern responsive design
- 🚀 **Real-time Recommendations**: Generate personalized recommendations quickly
- 📊 **Intelligent Ranking**: Comprehensive sorting based on ratings, distance, and user requirements

### 🔥 Latest Optimizations

- ✅ **Multi-Scenario Recommendations**: Support simultaneous selection of multiple venue types
- ✅ **Frontend Multi-Selection**: Intuitive venue type selection interface
- ✅ **Smart Ranking Algorithm**: Scenario matching reward mechanism
- ✅ **Performance Monitoring**: Complete performance statistics and health checks
- ✅ **Error Handling**: Robust exception handling mechanism

## 🚀 Quick Start

### Requirements

- Python 3.11+
- Amap (Gaode Map) API Key
- Modern browsers (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/JasonRobertDestiny/MeetSpot.git
cd MeetSpot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
```bash
cp config/config.toml.example config/config.toml
```

Edit `config/config.toml` and add your Amap API key:
```toml
[amap]
api_key = "your_amap_api_key_here"
```

4. **Start Service**
```bash
python web_server.py
```

5. **Access Application**
Open browser and visit: http://127.0.0.1:8000

## 📱 Usage

### Basic Usage

1. **Input Locations**: Add 2-10 participant locations
2. **Select Scenarios**: Choose 1-3 venue types (cafes, restaurants, libraries, etc.)
3. **Set Requirements**: Add special requirements (convenient parking, quiet environment, etc.)
4. **Get Recommendations**: Click search to get intelligent recommendations

### Advanced Features

- **Multi-Scenario Combination**: Search "cafe restaurant" simultaneously for more options
- **Custom Keywords**: Enter special venue types like "escape room"
- **Filter Conditions**: Filter by rating, distance, price
- **Special Requirements**: Support parking, Wi-Fi, private rooms, etc.

## 🏗️ Technology Architecture

### Backend Stack

- **FastAPI**: High-performance web framework
- **Pydantic**: Data validation and settings management
- **aiohttp**: Async HTTP client
- **Amap API**: Geocoding and POI search

### Frontend Stack

- **HTML5 + CSS3**: Responsive design
- **Vanilla JavaScript**: Lightweight interaction
- **Boxicons**: Icon library
- **Modern UI Design**: Gradients and glass effects

### Core Algorithms

- **Geometric Center Calculation**: Multi-point centroid algorithm
- **Intelligent Ranking**: Multi-factor scoring system
- **Scenario Matching**: Keyword matching reward
- **Deduplication Algorithm**: Smart deduplication based on name and address

## 📊 API Documentation

### Main Endpoints

- `GET /` - Homepage redirect
- `POST /api/find_meetspot` - Meeting point recommendation
- `GET /health` - Health check
- `GET /workspace/js_src/{filename}` - Generated recommendation pages

### Request Example

```bash
curl -X POST "http://127.0.0.1:8000/api/find_meetspot" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": ["Beijing University", "Tsinghua University"],
    "keywords": "cafe restaurant",
    "user_requirements": "convenient parking"
  }'
```

### Response Example

```json
{
  "success": true,
  "html_url": "/workspace/js_src/place_recommendation_20250624_12345678.html",
  "locations_count": 2,
  "keywords": "cafe restaurant",
  "processing_time": 0.52
}
```

## 🧪 Testing

Complete test suite included:

```bash
# Run all tests
python test_optimizations.py      # System optimization tests
python test_multi_scenario.py     # Multi-scenario feature tests
python comprehensive_test.py      # Comprehensive feature tests

# Health check
curl http://127.0.0.1:8000/health
```

## 📈 Performance Metrics

- **Response Time**:
  - Single scenario: 0.3-0.4 seconds
  - Dual scenario: 0.5-0.6 seconds
  - Triple scenario: 0.7-0.8 seconds

- **Support Scale**:
  - Locations: 2-10
  - Scenarios: 1-3
  - Concurrent users: 100+

## 🛣️ Roadmap

### v1.1.0 (Planned)
- [ ] User account system
- [ ] History saving
- [ ] Favorites feature
- [ ] Share recommendations

### v1.2.0 (Planned)
- [ ] Machine learning recommendations
- [ ] Real-time traffic information
- [ ] Weather data integration
- [ ] Mobile app

### v2.0.0 (Long-term)
- [ ] AR navigation
- [ ] Voice interaction
- [ ] Internationalization
- [ ] Enterprise features

## 🤝 Contributing

We welcome all forms of contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is open source under the MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Contact

- 📧 Email: Johnrobertdestiny@gmail.com
- 🐛 Bug Reports: [GitHub Issues](https://github.com/JasonRobertDestiny/MeetSpot/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/JasonRobertDestiny/MeetSpot/discussions)

## 🙏 Acknowledgments

- [Amap](https://lbs.amap.com/) - Providing geocoding and POI search services
- [FastAPI](https://fastapi.tiangolo.com/) - Excellent web framework
- [Boxicons](https://boxicons.com/) - Beautiful icon library

---

<div align="center">

**If this project helps you, please give it a ⭐ Star!**

Made with ❤️ by [JasonRobertDestiny](https://github.com/JasonRobertDestiny)

</div>

[![Star History Chart](https://api.star-history.com/svg?repos=JasonRobertDestiny/MeetSpot&type=Date)](https://www.star-history.com/#JasonRobertDestiny/MeetSpot&Date)
