/**
 * 快速OpenRouter API测试
 */

import dotenv from 'dotenv';
import fs from 'fs/promises';

dotenv.config();

console.log("🚀 快速API测试");

async function quickTest() {
  const config = {
    key: process.env.OPENAI_API_KEY,
    baseUrl: process.env.OPENAI_BASE_URL || 'https://openrouter.ai/api/v1',
    model: process.env.OPENAI_MODEL || 'anthropic/claude-3.5-sonnet'
  };
  
  console.log(`API Key: ${config.key ? config.key.substring(0, 20) + '...' : '未配置'}`);
  console.log(`Base URL: ${config.baseUrl}`);
  console.log(`Model: ${config.model}`);
  
  try {
    console.log("🔄 发送测试请求...");
    
    const requestBody = {
      model: config.model,
      messages: [
        {
          role: 'user',
          content: '请简单介绍一下北京适合商务会谈的咖啡馆，50字以内。'
        }
      ],
      max_tokens: 200,
      temperature: 0.7
    };
    
    console.log("📤 请求体:", JSON.stringify(requestBody, null, 2));
    
    const response = await fetch(`${config.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.key}`,
        'HTTP-Referer': 'https://meetspot.local',
        'X-Title': 'MeetSpot Test'
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log(`📡 响应状态: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ API错误: ${response.status} ${response.statusText}`);
      console.error(`错误详情: ${errorText}`);
      return false;
    }
    
    const data = await response.json();
    console.log("✅ API调用成功!");
    console.log("📝 AI回复:", data.choices[0].message.content);
    
    // 保存结果
    const result = {
      success: true,
      response: data.choices[0].message.content,
      timestamp: new Date().toISOString(),
      usage: data.usage
    };
    
    await fs.writeFile('api_test_result.json', JSON.stringify(result, null, 2));
    console.log("💾 结果已保存到 api_test_result.json");
    
    return true;
    
  } catch (error) {
    console.error("❌ 测试失败:", error.message);
    return false;
  }
}

quickTest().then(success => {
  if (success) {
    console.log("🎉 OpenRouter API测试成功!");
  } else {
    console.log("💡 使用离线模式...");
  }
});
