import { GeocodeTool } from './dist/index.js';

// 创建工具实例
const geocodeTool = new GeocodeTool();

console.log('🧪 TypeScript工具测试');
console.log('工具名称:', geocodeTool.name);
console.log('工具描述:', geocodeTool.description);
console.log('参数Schema:', JSON.stringify(geocodeTool.parameters, null, 2));

// 简单验证工具实例
console.log('✅ GeocodeTool 创建成功！');
console.log('🎯 TypeScript编译和模块导出都正常工作！');
