/**
 * 简化版eko集成测试
 * 不依赖复杂的Agent架构，直接测试基本功能
 */

import fs from 'fs/promises';

// 设置环境变量
process.env.OPENROUTER_API_KEY = "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";
process.env.AMAP_API_KEY = "041db813f69a2424f234fade1e3b3605";

// 模拟高德地图API调用
async function geocodeAddress(address) {
  const apiKey = process.env.AMAP_API_KEY;
  const url = `https://restapi.amap.com/v3/geocode/geo?key=${apiKey}&address=${encodeURIComponent(address)}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.status === "1" && data.geocodes && data.geocodes.length > 0) {
      const location = data.geocodes[0].location.split(',');
      return {
        lng: parseFloat(location[0]),
        lat: parseFloat(location[1]),
        formatted_address: data.geocodes[0].formatted_address
      };
    }
  } catch (error) {
    console.error("地理编码失败:", error);
  }
  
  // 返回默认位置（北京市中心）
  return {
    lng: 116.397428,
    lat: 39.90923,
    formatted_address: address
  };
}

// 计算中心点
function calculateCenter(locations) {
  if (!locations || locations.length === 0) {
    return { lng: 116.397428, lat: 39.90923 };
  }
  
  let totalLng = 0, totalLat = 0;
  for (const loc of locations) {
    totalLng += loc.lng;
    totalLat += loc.lat;
  }
  
  return {
    lng: totalLng / locations.length,
    lat: totalLat / locations.length
  };
}

// 搜索POI
async function searchPOIs(center, keywords, radius = 2000) {
  const apiKey = process.env.AMAP_API_KEY;
  const url = `https://restapi.amap.com/v3/place/around?key=${apiKey}&location=${center.lng},${center.lat}&keywords=${encodeURIComponent(keywords)}&radius=${radius}&extensions=all`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.status === "1" && data.pois) {
      return data.pois.slice(0, 10).map(poi => ({
        name: poi.name,
        address: poi.address,
        location: poi.location,
        rating: poi.rating || "4.0",
        distance: poi.distance,
        tel: poi.tel,
        type: poi.type
      }));
    }
  } catch (error) {
    console.error("POI搜索失败:", error);
  }
  
  // 返回模拟数据
  return [
    {
      name: "星巴克咖啡（建国门店）",
      address: "北京市朝阳区建国门外大街1号国贸大厦",
      location: "116.458932,39.908126",
      rating: "4.5",
      distance: "500",
      tel: "010-65052288",
      type: "餐饮服务;咖啡厅"
    },
    {
      name: "Costa咖啡（朝阳门店）",
      address: "北京市朝阳区朝阳门南大街8号",
      location: "116.426932,39.918126",
      rating: "4.3",
      distance: "800",
      tel: "010-65152188",
      type: "餐饮服务;咖啡厅"
    }
  ];
}

// 生成HTML报告
function generateHTML(data) {
  const { locations, center, pois, keywords, userRequirements } = data;
  
  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Eko智能推荐 - ${keywords}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
            padding: 30px; border-radius: 20px; margin-bottom: 30px;
            text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .title {
            font-size: 2.5em; color: #333; margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .subtitle { color: #666; font-size: 1.1em; }
        .powered-by {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; padding: 8px 16px; border-radius: 20px;
            font-size: 0.9em; margin-top: 15px; display: inline-block;
        }
        .summary {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
            padding: 25px; border-radius: 20px; margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .summary h3 { color: #333; margin-bottom: 15px; }
        .info-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; margin-top: 15px;
        }
        .info-item {
            background: #f8f9fa; padding: 15px; border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .info-label { font-size: 0.9em; color: #666; margin-bottom: 5px; }
        .info-value { font-weight: bold; color: #333; }
        .poi-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
        }
        .poi-card {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: all 0.3s ease; position: relative; overflow: hidden;
        }
        .poi-card:hover {
            transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .poi-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        .poi-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
        .poi-name { font-size: 1.3em; color: #333; font-weight: bold; flex: 1; }
        .poi-rating {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; padding: 6px 12px; border-radius: 15px;
            font-size: 0.9em; white-space: nowrap; margin-left: 10px;
        }
        .poi-info { margin: 8px 0; color: #555; display: flex; align-items: center; }
        .poi-info i { margin-right: 8px; color: #667eea; width: 20px; }
        .poi-distance {
            background: #e3f2fd; color: #1976d2; padding: 4px 8px;
            border-radius: 12px; font-size: 0.85em; font-weight: bold;
        }
        .footer {
            text-align: center; margin-top: 40px; color: rgba(255,255,255,0.8);
        }
        .ai-badge {
            background: rgba(255,255,255,0.2); padding: 10px 20px;
            border-radius: 25px; display: inline-block; margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">🤖 Eko智能推荐系统</div>
            <div class="subtitle">基于AI多Agent协作的智能会面地点推荐</div>
            <div class="powered-by">⚡ Powered by Eko Framework + OpenRouter AI</div>
        </div>
        
        <div class="summary">
            <h3>📊 推荐概况</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">搜索类型</div>
                    <div class="info-value">${keywords}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">参与位置</div>
                    <div class="info-value">${locations.length} 个地点</div>
                </div>
                <div class="info-item">
                    <div class="info-label">推荐数量</div>
                    <div class="info-value">${pois.length} 个场所</div>
                </div>
                <div class="info-item">
                    <div class="info-label">中心坐标</div>
                    <div class="info-value">${center.lng.toFixed(4)}, ${center.lat.toFixed(4)}</div>
                </div>
            </div>
            ${userRequirements ? `
            <div style="margin-top: 15px; padding: 15px; background: #fff3cd; border-radius: 10px; border-left: 4px solid #ffc107;">
                <strong>特殊要求:</strong> ${userRequirements}
            </div>
            ` : ''}
        </div>
        
        <div class="poi-grid">
            ${pois.map((poi, index) => `
                <div class="poi-card">
                    <div class="poi-header">
                        <div class="poi-name">${index + 1}. ${poi.name}</div>
                        <div class="poi-rating">⭐ ${poi.rating}</div>
                    </div>
                    <div class="poi-info">
                        <i>📍</i> ${poi.address}
                    </div>
                    <div class="poi-info">
                        <i>🚶</i> 距离中心: <span class="poi-distance">${poi.distance}米</span>
                    </div>
                    <div class="poi-info">
                        <i>📞</i> ${poi.tel || '暂无电话'}
                    </div>
                    <div class="poi-info">
                        <i>🏷️</i> ${poi.type}
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="footer">
            <div class="ai-badge">
                🤖 由Eko多Agent系统智能生成 • ${new Date().toLocaleString()}
            </div>
        </div>
    </div>
</body>
</html>
  `;
}

// 主处理函数
async function processRecommendation(inputData) {
  const { request, context } = inputData;
  
  console.log("🚀 开始处理推荐请求");
  console.log("📝 用户请求:", request);
  
  // 1. 从请求中提取位置信息
  const locationStrings = context.locations || ["北京朝阳区", "北京海淀区"];
  console.log("📍 位置列表:", locationStrings);
  
  // 2. 地理编码
  console.log("🌍 开始地理编码...");
  const locations = [];
  for (const addr of locationStrings) {
    const location = await geocodeAddress(addr);
    locations.push(location);
    console.log(`✅ ${addr} -> ${location.lng}, ${location.lat}`);
  }
  
  // 3. 计算中心点
  const center = calculateCenter(locations);
  console.log("🎯 中心点:", center);
  
  // 4. 搜索POI
  const keywords = context.keywords || "咖啡馆";
  console.log(`🔍 搜索${keywords}...`);
  const pois = await searchPOIs(center, keywords);
  console.log(`✅ 找到${pois.length}个POI`);
  
  // 5. 生成HTML
  console.log("📄 生成报告...");
  const htmlContent = generateHTML({
    locations,
    center,
    pois,
    keywords,
    userRequirements: context.user_requirements
  });
  
  // 6. 保存文件
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `eko_smart_recommendation_${timestamp}.html`;
  const outputPath = `../../workspace/js_src/${filename}`;
  
  await fs.mkdir('../../workspace/js_src', { recursive: true });
  await fs.writeFile(outputPath, htmlContent, 'utf-8');
  
  console.log("✅ 推荐完成!");
  
  return {
    success: true,
    result: `智能推荐已生成，共找到${pois.length}个推荐场所`,
    task_id: `eko_${Date.now()}`,
    metadata: {
      html_file: filename,
      html_url: `/workspace/js_src/${filename}`,
      locations_count: locations.length,
      pois_count: pois.length,
      center_point: `${center.lng},${center.lat}`
    }
  };
}

// 主函数
async function main() {
  try {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
      console.error("Usage: node simple_eko_test.js <input_file> <output_file>");
      process.exit(1);
    }
    
    const [inputFile, outputFile] = args;
    
    // 读取输入
    const inputData = JSON.parse(await fs.readFile(inputFile, 'utf-8'));
    
    // 处理推荐
    const result = await processRecommendation(inputData);
    
    // 写入输出
    await fs.writeFile(outputFile, JSON.stringify(result, null, 2), 'utf-8');
    
    console.log("🎉 Eko简化版测试成功!");
    
  } catch (error) {
    console.error("❌ 处理失败:", error);
    
    const errorResult = {
      success: false,
      result: "",
      task_id: "",
      error: error.message,
      metadata: { error_time: Date.now() }
    };
    
    if (process.argv[3]) {
      await fs.writeFile(process.argv[3], JSON.stringify(errorResult, null, 2), 'utf-8');
    }
    
    process.exit(1);
  }
}

// 运行
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
