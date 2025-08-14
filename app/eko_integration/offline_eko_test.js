/**
 * 离线版eko集成测试 - 模拟智能推荐
 */

import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';

dotenv.config();

console.log("🚀 启动离线版eko测试");

// 模拟的智能推荐函数
function generateIntelligentRecommendation(query, locations) {
  console.log("🧠 分析用户需求...");
  console.log("📍 处理位置信息...");
  console.log("🔍 搜索附近POI...");
  console.log("⚡ 生成智能推荐...");
  
  const recommendations = [
    {
      name: "星巴克咖啡 (建外SOHO店)",
      address: "北京市朝阳区建外SOHO西区15号楼",
      rating: 4.6,
      distance: 680,
      price_range: "35-60元/人",
      features: ["商务环境", "WiFi", "充电位", "安静"],
      opening_hours: "07:00-22:00",
      phone: "010-58695432",
      recommendation_reason: "距离两地中心位置最近，商务环境优雅，适合商务洽谈",
      parking: "大厦地下停车场，收费标准10元/小时",
      transport: "地铁1号线/10号线国贸站D口步行5分钟"
    },
    {
      name: "COSTA咖啡 (中关村店)",
      address: "北京市海淀区中关村大街19号新中关购物中心",
      rating: 4.4,
      distance: 850,
      price_range: "30-55元/人", 
      features: ["宽敞座位", "WiFi", "安静环境", "窗边位"],
      opening_hours: "08:00-22:00",
      phone: "010-82883344",
      recommendation_reason: "空间宽敞，座位舒适，适合长时间会谈",
      parking: "购物中心停车场，前2小时免费",
      transport: "地铁4号线中关村站A口直达"
    },
    {
      name: "蓝山咖啡 (知春路店)",
      address: "北京市海淀区知春路128号润城商厦",
      rating: 4.3,
      distance: 1200,
      price_range: "25-45元/人",
      features: ["价格实惠", "WiFi", "包厢", "停车方便"],
      opening_hours: "09:00-21:00", 
      phone: "010-82356789",
      recommendation_reason: "性价比高，有独立包厢可预订，停车便利",
      parking: "商厦免费停车场",
      transport: "地铁13号线知春路站C口步行3分钟"
    }
  ];

  // 根据查询内容调整推荐权重
  if (query.includes("商务") || query.includes("洽谈")) {
    recommendations[0].score = 95;
    recommendations[1].score = 88;
    recommendations[2].score = 82;
  } else if (query.includes("便宜") || query.includes("实惠")) {
    recommendations[2].score = 93;
    recommendations[1].score = 85;
    recommendations[0].score = 78;
  } else {
    recommendations[0].score = 90;
    recommendations[1].score = 87;
    recommendations[2].score = 84;
  }

  return recommendations.sort((a, b) => b.score - a.score);
}

// 生成详细的HTML报告
function generateDetailedHTML(recommendations, query, metadata) {
  const timestamp = new Date().toLocaleString();
  
  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MeetSpot 智能推荐报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6; background: #f5f5f5; color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; border-radius: 15px; text-align: center;
            margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .query-section {
            background: white; padding: 25px; border-radius: 10px;
            margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .recommendations { display: grid; gap: 25px; }
        .rec-card {
            background: white; border-radius: 15px; padding: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .rec-card:hover { transform: translateY(-5px); }
        .rec-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            margin-bottom: 20px;
        }
        .rec-name { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }
        .rec-score {
            background: #667eea; color: white; padding: 8px 15px;
            border-radius: 20px; font-weight: bold;
        }
        .rec-rating {
            background: #f39c12; color: white; padding: 5px 12px;
            border-radius: 15px; margin-top: 5px; display: inline-block;
        }
        .rec-info { margin: 15px 0; }
        .info-row { 
            display: flex; margin-bottom: 12px; align-items: flex-start;
        }
        .info-label {
            font-weight: bold; color: #666; min-width: 80px;
            margin-right: 15px;
        }
        .info-value { flex: 1; }
        .features {
            display: flex; flex-wrap: wrap; gap: 8px; margin: 15px 0;
        }
        .feature {
            background: #e8f4f8; color: #2c5aa0; padding: 5px 12px;
            border-radius: 15px; font-size: 0.9rem;
        }
        .reason {
            background: #f8f9fa; padding: 15px; border-radius: 8px;
            border-left: 4px solid #667eea; margin-top: 15px;
        }
        .metadata {
            background: #2c3e50; color: white; padding: 20px;
            border-radius: 10px; margin-top: 30px; text-align: center;
        }
        .footer {
            text-align: center; margin-top: 30px; color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MeetSpot 智能推荐</h1>
            <p>基于AI多Agent协作的智能会面地点推荐系统</p>
        </div>

        <div class="query-section">
            <h3>📝 您的需求</h3>
            <p style="font-size: 1.1rem; margin-top: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                ${query}
            </p>
        </div>

        <div class="recommendations">
            ${recommendations.map((rec, index) => `
                <div class="rec-card">
                    <div class="rec-header">
                        <div>
                            <div class="rec-name">${index + 1}. ${rec.name}</div>
                            <div class="rec-rating">⭐ ${rec.rating}分</div>
                        </div>
                        <div class="rec-score">智能评分: ${rec.score}</div>
                    </div>
                    
                    <div class="rec-info">
                        <div class="info-row">
                            <div class="info-label">📍 地址:</div>
                            <div class="info-value">${rec.address}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">🚶 距离:</div>
                            <div class="info-value">${rec.distance}米</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">💰 价格:</div>
                            <div class="info-value">${rec.price_range}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">🕒 营业:</div>
                            <div class="info-value">${rec.opening_hours}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">📞 电话:</div>
                            <div class="info-value">${rec.phone}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">🚗 停车:</div>
                            <div class="info-value">${rec.parking}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">🚇 交通:</div>
                            <div class="info-value">${rec.transport}</div>
                        </div>
                    </div>

                    <div class="features">
                        ${rec.features.map(feature => `<span class="feature">${feature}</span>`).join('')}
                    </div>

                    <div class="reason">
                        <strong>🎯 推荐理由:</strong> ${rec.recommendation_reason}
                    </div>
                </div>
            `).join('')}
        </div>

        <div class="metadata">
            <h3>🤖 技术信息</h3>
            <p>分析模式: ${metadata.mode} | 处理时间: ${metadata.processingTime}ms | 生成时间: ${timestamp}</p>
            <p>🚀 Powered by MeetSpot × Eko AI Framework</p>
        </div>

        <div class="footer">
            <p>💡 提示: 建议您在前往前致电确认营业时间和位置</p>
            <p>📱 如需导航，建议使用高德地图或百度地图</p>
        </div>
    </div>
</body>
</html>
  `;
}

async function main() {
  const startTime = Date.now();
  
  // 模拟输入
  const testInput = {
    query: `
我需要为团队会议找一个咖啡馆，参与者位置如下：
1. 北京朝阳区望京SOHO
2. 北京海淀区中关村大街

要求：
- 环境安静，适合商务洽谈
- 有WiFi和充电位
- 交通便利，最好有停车位
- 价格适中

请推荐3个合适的地点，包含详细信息。
    `.trim(),
    locations: ["北京朝阳区望京SOHO", "北京海淀区中关村大街"],
    context: {
      workflow_type: "intelligent_recommendation",
      mode: "business_meeting"
    }
  };

  console.log("📝 处理查询:", testInput.query);
  console.log("📍 位置数量:", testInput.locations.length);

  // 生成推荐
  const recommendations = generateIntelligentRecommendation(
    testInput.query, 
    testInput.locations
  );

  const processingTime = Date.now() - startTime;
  console.log(`⏱️  处理完成，耗时: ${processingTime}ms`);

  // 生成HTML报告
  const htmlContent = generateDetailedHTML(recommendations, testInput.query, {
    mode: "Eko智能模式",
    processingTime: processingTime
  });

  // 保存文件
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const htmlFile = `offline_eko_recommendation_${timestamp}.html`;
  const jsonFile = `offline_eko_recommendation_${timestamp}.json`;

  await fs.writeFile(htmlFile, htmlContent, 'utf-8');
  
  const jsonResult = {
    success: true,
    result: "智能推荐已生成",
    task_id: `offline_${Date.now()}`,
    html_url: `./${htmlFile}`,
    recommendations: recommendations,
    metadata: {
      mode: "offline_intelligent",
      processing_time: processingTime,
      recommendations_count: recommendations.length,
      timestamp: new Date().toISOString()
    }
  };

  await fs.writeFile(jsonFile, JSON.stringify(jsonResult, null, 2), 'utf-8');

  console.log(`✅ 推荐完成!`);
  console.log(`📄 HTML报告: ${htmlFile}`);
  console.log(`📄 JSON结果: ${jsonFile}`);
  console.log(`🔗 推荐数量: ${recommendations.length}`);

  // 显示推荐概要
  console.log("\n🏆 推荐排名:");
  recommendations.forEach((rec, index) => {
    console.log(`${index + 1}. ${rec.name} (评分: ${rec.score})`);
  });
}

main().catch(console.error);
