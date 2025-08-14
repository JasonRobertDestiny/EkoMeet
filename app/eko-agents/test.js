import { GeocodeTool } from './index.js';
// 创建工具实例
const geocodeTool = new GeocodeTool();
// 模拟AgentContext和ToolCall
const mockAgentContext = {};
const mockToolCall = {};
// 测试地理编码功能
async function testGeocode() {
    console.log('🧪 开始测试地理编码工具...');
    try {
        const result = await geocodeTool.execute({ address: "北京大学", city: "北京" }, mockAgentContext, mockToolCall);
        console.log('✅ 地理编码结果:');
        console.log(JSON.stringify(result, null, 2));
    }
    catch (error) {
        console.error('❌ 测试失败:', error);
    }
}
// 运行测试
if (require.main === module) {
    testGeocode();
}
