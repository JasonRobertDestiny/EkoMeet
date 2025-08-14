/**
 * MeetSpot + Eko 核心集成脚本
 * 处理Python后端传入的请求，使用eko框架执行智能工作流
 */

import { Eko, Agent } from "@eko-ai/eko";
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// 获取当前文件目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 简单的环境变量加载
async function loadEnv() {
  try {
    const envPath = path.join(__dirname, '.env');
    const envContent = await fs.readFile(envPath, 'utf-8');
    const envVars = {};
    
    envContent.split('\n').forEach(line => {
      line = line.trim();
      if (line && !line.startsWith('#')) {
        const [key, value] = line.split('=');
        if (key && value) {
          envVars[key.trim()] = value.trim();
        }
      }
    });
    
    return envVars;
  } catch (error) {
    console.warn('无法加载.env文件，使用默认配置');
    return {};
  }
}

// Agent定义
class LocationAgent extends Agent {
  constructor() {
    super({
      name: "LocationAgent",
      description: "处理地理位置相关任务，包括地址解析、坐标转换、距离计算等",
      tools: [
        {
          name: "geocode_address",
          description: "将地址转换为经纬度坐标",
          parameters: {
            type: "object",
            properties: {
              address: { type: "string", description: "地址描述" },
              city: { type: "string", description: "城市名称（可选）" }
            },
            required: ["address"]
          },
          execute: async (args) => {
            // 使用高德地图API进行地理编码
            try {
              const apiKey = process.env.AMAP_API_KEY || "041db813f69a2424f234fade1e3b3605";
              const address = encodeURIComponent(args.address);
              const city = args.city ? encodeURIComponent(args.city) : "";
              
              const url = `https://restapi.amap.com/v3/geocode/geo?key=${apiKey}&address=${address}${city ? `&city=${city}` : ""}`;
              
              const response = await fetch(url);
              const data = await response.json();
              
              if (data.status === "1" && data.geocodes && data.geocodes.length > 0) {
                const geocode = data.geocodes[0];
                return {
                  content: [{
                    type: "text",
                    text: JSON.stringify({
                      address: args.address,
                      location: geocode.location,
                      formatted_address: geocode.formatted_address,
                      district: geocode.district,
                      adcode: geocode.adcode
                    })
                  }]
                };
              } else {
                return {
                  content: [{ type: "text", text: `地理编码失败: ${data.info}` }],
                  isError: true
                };
              }
            } catch (error) {
              return {
                content: [{ type: "text", text: `地理编码异常: ${error.message}` }],
                isError: true
              };
            }
          }
        },
        {
          name: "calculate_center",
          description: "计算多个位置的几何中心点",
          parameters: {
            type: "object",
            properties: {
              locations: {
                type: "array",
                items: { type: "string" },
                description: "位置经纬度数组，格式：['lng,lat', 'lng,lat']"
              }
            },
            required: ["locations"]
          },
          execute: async (args) => {
            const locations = args.locations;
            if (!Array.isArray(locations) || locations.length === 0) {
              return {
                content: [{ type: "text", text: "位置数组为空" }],
                isError: true
              };
            }
            
            // 计算几何中心
            let totalLng = 0, totalLat = 0;
            for (const loc of locations) {
              const [lng, lat] = loc.split(',').map(Number);
              totalLng += lng;
              totalLat += lat;
            }
            
            const centerLng = totalLng / locations.length;
            const centerLat = totalLat / locations.length;
            
            return {
              content: [{
                type: "text",
                text: JSON.stringify({
                  center: `${centerLng},${centerLat}`,
                  count: locations.length
                })
              }]
            };
          }
        }
      ],
      planDescription: "负责处理所有地理位置相关的计算和转换任务"
    });
  }
}

class POISearchAgent extends Agent {
  constructor() {
    super({
      name: "POISearchAgent", 
      description: "搜索和筛选各类场所POI信息",
      tools: [
        {
          name: "search_nearby_pois",
          description: "搜索指定位置附近的POI",
          parameters: {
            type: "object",
            properties: {
              location: { type: "string", description: "中心点坐标 lng,lat" },
              keywords: { type: "string", description: "搜索关键词" },
              radius: { type: "number", description: "搜索半径（米）", default: 2000 },
              types: { type: "string", description: "POI类型编码（可选）" }
            },
            required: ["location", "keywords"]
          },
          execute: async (args) => {
            // 使用高德地图API搜索POI
            try {
              const apiKey = process.env.AMAP_API_KEY || "041db813f69a2424f234fade1e3b3605";
              const location = encodeURIComponent(args.location);
              const keywords = encodeURIComponent(args.keywords);
              const radius = args.radius || 2000;
              const types = args.types ? encodeURIComponent(args.types) : "";
              
              const url = `https://restapi.amap.com/v3/place/around?key=${apiKey}&location=${location}&keywords=${keywords}&radius=${radius}${types ? `&types=${types}` : ""}&sortrule=distance&extensions=all`;
              
              const response = await fetch(url);
              const data = await response.json();
              
              if (data.status === "1" && data.pois && data.pois.length > 0) {
                const pois = data.pois.slice(0, 10).map(poi => ({
                  id: poi.id,
                  name: poi.name,
                  address: poi.address,
                  location: poi.location,
                  distance: parseInt(poi.distance),
                  rating: parseFloat(poi.rating) || 4.0,
                  tel: poi.tel,
                  type: poi.type,
                  business_area: poi.business_area,
                  opening_hours: poi.business_time || "请电话咨询",
                  price_level: "中等" // 高德API不直接提供价格信息
                }));
                
                return {
                  content: [{
                    type: "text",
                    text: JSON.stringify({
                      pois: pois,
                      total: data.count,
                      search_params: args,
                      center_location: args.location
                    })
                  }]
                };
              } else {
                return {
                  content: [{ type: "text", text: `POI搜索失败: ${data.info || '无结果'}` }],
                  isError: true
                };
              }
            } catch (error) {
              return {
                content: [{ type: "text", text: `POI搜索异常: ${error.message}` }],
                isError: true
              };
            }
          }
        }
      ],
      planDescription: "负责搜索和获取POI信息，支持多种场所类型"
    });
  }
}

class RecommendationAgent extends Agent {
  constructor() {
    super({
      name: "RecommendationAgent",
      description: "基于用户需求进行智能推荐和排序",
      tools: [
        {
          name: "rank_recommendations",
          description: "对推荐结果进行智能排序",
          parameters: {
            type: "object", 
            properties: {
              pois: { type: "array", description: "POI列表" },
              user_preferences: { type: "object", description: "用户偏好" },
              center_location: { type: "string", description: "中心位置" }
            },
            required: ["pois"]
          },
          execute: async (args) => {
            const pois = args.pois || [];
            
            // 简单排序算法：综合评分和距离
            const rankedPOIs = pois.map(poi => ({
              ...poi,
              score: (poi.rating * 20 + (2000 - poi.distance) / 20)
            })).sort((a, b) => b.score - a.score);
            
            return {
              content: [{
                type: "text",
                text: JSON.stringify({
                  ranked_pois: rankedPOIs,
                  ranking_criteria: "综合评分 = 用户评分×20 + (2000-距离)/20"
                })
              }]
            };
          }
        }
      ],
      planDescription: "负责对搜索结果进行智能分析和排序，提供个性化推荐"
    });
  }
}

class VisualizationAgent extends Agent {
  constructor() {
    super({
      name: "VisualizationAgent",
      description: "生成可视化推荐结果和详细报告",
      tools: [
        {
          name: "generate_report",
          description: "生成HTML推荐报告",
          parameters: {
            type: "object",
            properties: {
              recommendations: { type: "array", description: "推荐结果" },
              user_locations: { type: "array", description: "用户位置" },
              center_point: { type: "string", description: "中心点" },
              keywords: { type: "string", description: "搜索关键词" }
            },
            required: ["recommendations"]
          },
          execute: async (args, agentContext) => {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `eko_recommendation_${timestamp}.html`;
            
            // 生成HTML内容
            const htmlContent = generateReportHTML(args);
            
            // 保存到workspace目录
            const outputPath = path.join(process.cwd(), 'workspace', 'js_src', filename);
            await fs.mkdir(path.dirname(outputPath), { recursive: true });
            await fs.writeFile(outputPath, htmlContent, 'utf-8');
            
            return {
              content: [{
                type: "text",
                text: JSON.stringify({
                  html_file: filename,
                  html_path: outputPath,
                  url: `/workspace/js_src/${filename}`
                })
              }]
            };
          }
        }
      ],
      planDescription: "负责生成美观的可视化报告和HTML页面"
    });
  }
}

// HTML报告生成函数
function generateReportHTML(data) {
  const { recommendations = [], user_locations = [], center_point = "", keywords = "" } = data;
  
  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eko智能推荐结果 - ${keywords}</title>
    <style>
        body { 
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px;
            text-align: center;
        }
        .powered-by {
            background: rgba(255,255,255,0.1);
            padding: 10px; border-radius: 5px; margin-top: 15px;
            font-size: 0.9em;
        }
        .summary {
            background: white; padding: 25px; border-radius: 10px;
            margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .poi-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px; margin-top: 20px;
        }
        .poi-card {
            background: white; border-radius: 10px; padding: 20px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .poi-card:hover { transform: translateY(-5px); }
        .poi-name { font-size: 1.3em; color: #333; margin-bottom: 10px; font-weight: bold; }
        .poi-rating {
            background: #667eea; color: white; padding: 5px 10px;
            border-radius: 15px; font-size: 0.9em; display: inline-block;
        }
        .poi-info { margin: 10px 0; color: #666; }
        .poi-score { 
            background: #e8f4f8; color: #2c5aa0; padding: 5px 10px;
            border-radius: 5px; font-weight: bold; margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 智能会面地点推荐</h1>
            <p>基于多Agent协作的智能推荐系统</p>
            <div class="powered-by">
                ⚡ Powered by Eko Framework + MeetSpot
            </div>
        </div>
        
        <div class="summary">
            <h3>📍 推荐概况</h3>
            <p><strong>搜索类型:</strong> ${keywords}</p>
            <p><strong>参与位置:</strong> ${user_locations.length} 个</p>
            <p><strong>推荐数量:</strong> ${recommendations.length} 个</p>
            <p><strong>中心坐标:</strong> ${center_point}</p>
        </div>
        
        <div class="poi-grid">
            ${recommendations.map((poi, index) => `
                <div class="poi-card">
                    <div class="poi-name">${index + 1}. ${poi.name || '未知场所'}</div>
                    <div class="poi-rating">⭐ ${poi.rating || 'N/A'}</div>
                    <div class="poi-info">📍 ${poi.address || '地址信息缺失'}</div>
                    <div class="poi-info">🚶 距离中心: ${poi.distance || 'N/A'}米</div>
                    <div class="poi-info">💰 价格水平: ${poi.price_level || '未知'}</div>
                    <div class="poi-info">🕒 营业时间: ${poi.opening_hours || '请电话咨询'}</div>
                    ${poi.score ? `<div class="poi-score">智能评分: ${poi.score.toFixed(1)}</div>` : ''}
                </div>
            `).join('')}
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>🤖 本推荐由Eko多Agent系统智能生成 | 生成时间: ${new Date().toLocaleString()}</p>
        </div>
    </div>
</body>
</html>
  `;
}

// 主函数
async function main() {
  try {
    // 加载环境变量
    const env = await loadEnv();
    Object.assign(process.env, env);
    
    const args = process.argv.slice(2);
    if (args.length < 2) {
      console.error("Usage: node eko_meetspot_core.js <input_file> <output_file>");
      process.exit(1);
    }
    
    const [inputFile, outputFile] = args;
    
    // 读取输入数据
    const inputData = JSON.parse(await fs.readFile(inputFile, 'utf-8'));
    const { request, context = {}, config: inputConfig = {} } = inputData;
    
    // 配置LLM - 使用OpenRouter API
    const llms = {
      default: {
        provider: "openai-compatible",
        model: process.env.EKO_MODEL || "anthropic/claude-3.5-sonnet",
        apiKey: process.env.OPENROUTER_API_KEY || "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",
        config: {
          baseURL: process.env.EKO_BASE_URL || "https://openrouter.ai/api/v1"
        }
      }
    };
    
    // 创建Agent实例
    const agents = [
      new LocationAgent(),
      new POISearchAgent(), 
      new RecommendationAgent(),
      new VisualizationAgent()
    ];
    
    // 创建Eko实例
    const eko = new Eko({ llms, agents });
    
    // 执行工作流
    const result = await eko.run(request);
    
    // 准备输出数据
    const outputData = {
      success: result.success,
      result: result.result,
      task_id: result.taskId,
      error: result.success ? null : result.result,
      metadata: {
        processing_time: Date.now(),
        workflow_type: context.workflow_type || "general",
        agent_count: agents.length
      }
    };
    
    // 写入输出文件
    await fs.writeFile(outputFile, JSON.stringify(outputData, null, 2), 'utf-8');
    
    console.log("Eko workflow completed successfully");
    
  } catch (error) {
    console.error("Eko workflow failed:", error);
    
    // 写入错误结果
    const errorOutput = {
      success: false,
      result: "",
      task_id: "",
      error: error.message || "Unknown error",
      metadata: { error_time: Date.now() }
    };
    
    if (process.argv[3]) {
      await fs.writeFile(process.argv[3], JSON.stringify(errorOutput, null, 2), 'utf-8');
    }
    
    process.exit(1);
  }
}

// 运行主函数
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { LocationAgent, POISearchAgent, RecommendationAgent, VisualizationAgent };
