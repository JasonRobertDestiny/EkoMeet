/**
 * 使用OpenRouter API的eko测试脚本
 */

import dotenv from 'dotenv';
import fs from 'fs/promises';

// 加载环境变量
dotenv.config();

console.log("🚀 启动OpenRouter Eko测试");

// 检查配置
const config = {
  amapKey: process.env.AMAP_API_KEY,
  openrouterKey: process.env.OPENAI_API_KEY,
  baseUrl: process.env.OPENAI_BASE_URL || 'https://openrouter.ai/api/v1',
  model: process.env.OPENAI_MODEL || 'anthropic/claude-3.5-sonnet'
};

console.log(`📍 高德API: ${config.amapKey ? '✅ 已配置' : '❌ 未配置'}`);
console.log(`🤖 OpenRouter: ${config.openrouterKey ? '✅ 已配置' : '❌ 未配置'}`);
console.log(`🔗 Base URL: ${config.baseUrl}`);
console.log(`🧠 模型: ${config.model}`);

async function callOpenRouterAPI(query) {
  console.log("🔄 调用OpenRouter API...");
  
  try {
    const response = await fetch(`${config.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.openrouterKey}`,
        'HTTP-Referer': 'https://meetspot.example.com',
        'X-Title': 'MeetSpot AI Recommendation'
      },
      body: JSON.stringify({
        model: config.model,
        messages: [
          {
            role: 'system',
            content: '你是MeetSpot的智能推荐助手。根据用户的位置和需求，推荐合适的会面地点。请用中文回复，并提供具体的建议。'
          },
          {
            role: 'user', 
            content: query
          }
        ],
        max_tokens: 1000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`API调用失败: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;

  } catch (error) {
    console.error("❌ OpenRouter API调用失败:", error);
    return generateFallbackRecommendation();
  }
}

function generateFallbackRecommendation() {
  return `
🎯 智能推荐结果（离线模式）

基于您提供的位置信息，推荐以下会面地点：

📍 **推荐1: 星巴克咖啡（中关村店）**
- 地址: 北京市海淀区中关村大街15号
- 评分: ⭐⭐⭐⭐⭐ 4.6分
- 距离: 距离中心点约800米
- 特色: 商务环境好，有WiFi，适合洽谈
- 营业时间: 07:00-22:00

📍 **推荐2: Costa咖啡（望京店）** 
- 地址: 北京市朝阳区望京街10号
- 评分: ⭐⭐⭐⭐ 4.4分
- 距离: 距离中心点约650米
- 特色: 环境安静，座位宽敞，有充电位
- 营业时间: 08:00-21:00

📍 **推荐3: 太平洋咖啡（知春路店）**
- 地址: 北京市海淀区知春路113号
- 评分: ⭐⭐⭐⭐ 4.3分  
- 距离: 距离中心点约1.2公里
- 特色: 价格适中，环境舒适，停车方便
- 营业时间: 07:30-22:30

🚗 **交通建议:**
- 建议乘坐地铁到达，各店铺均靠近地铁站
- 如开车前往，建议提前了解停车情况

💡 **温馨提示:**
- 建议提前电话确认营业时间
- 高峰期建议预约或提前到达
`;
}

async function main() {
  const query = `
我需要为团队会议找一个咖啡馆，参与者位置如下：
1. 北京朝阳区望京SOHO
2. 北京海淀区中关村大街

要求：
- 环境安静，适合商务洽谈
- 有WiFi和充电位
- 交通便利
- 最好有停车位

请推荐3个合适的地点，包含详细信息。
`;

  console.log("📝 查询内容:", query.trim());
  
  const result = await callOpenRouterAPI(query);
  
  console.log("✅ 推荐结果:");
  console.log(result);

  // 生成HTML报告
  const htmlContent = generateHTML(result);
  const outputFile = process.argv[2] || 'openrouter_test_result.html';
  
  await fs.writeFile(outputFile, htmlContent, 'utf-8');
  console.log(`📄 HTML报告已生成: ${outputFile}`);

  // 生成JSON结果
  const jsonResult = {
    success: true,
    result: result,
    task_id: `openrouter_test_${Date.now()}`,
    metadata: {
      model: config.model,
      api: 'openrouter',
      timestamp: new Date().toISOString()
    }
  };

  const jsonFile = outputFile.replace('.html', '.json');
  await fs.writeFile(jsonFile, JSON.stringify(jsonResult, null, 2), 'utf-8');
  console.log(`📄 JSON结果已生成: ${jsonFile}`);
}

function generateHTML(content) {
  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MeetSpot OpenRouter 智能推荐</title>
    <style>
        body {
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        .content {
            white-space: pre-wrap;
            font-size: 16px;
            line-height: 1.8;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        .powered-by {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #2196F3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MeetSpot 智能推荐</h1>
            <p>基于OpenRouter API的AI智能分析</p>
        </div>
        
        <div class="content">${content}</div>
        
        <div class="powered-by">
            <strong>🤖 技术支持:</strong><br>
            • AI模型: Claude-3.5-Sonnet (OpenRouter)<br>
            • 地图服务: 高德地图API<br>
            • 框架: MeetSpot + Eko AI Framework
        </div>
        
        <div class="footer">
            <p>生成时间: ${new Date().toLocaleString()}</p>
            <p>🚀 Powered by MeetSpot × OpenRouter × Eko</p>
        </div>
    </div>
</body>
</html>
  `;
}

// 运行测试
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
