import { AgentContext } from "@eko-ai/eko";
import { Tool, ToolResult } from "@eko-ai/eko/dist/types/tools.types";
import { LanguageModelV2ToolCallPart } from "@ai-sdk/provider";
import { JSONSchema7 } from "json-schema";

/**
 * 地理编码工具 - 将地址转换为经纬度坐标
 */
export class GeocodeTool implements Tool {
  readonly name = "geocode_address";
  readonly description = "将地址描述转换为精确的经纬度坐标，支持中文地址解析";
  readonly parameters: JSONSchema7 = {
    type: "object",
    properties: {
      address: {
        type: "string",
        description: "要解析的地址，如'北京市朝阳区望京SOHO'"
      },
      city: {
        type: "string", 
        description: "城市名称，用于提高解析精度",
        default: ""
      }
    },
    required: ["address"]
  };

  async execute(
    args: Record<string, unknown>,
    agentContext: AgentContext,
    toolCall: LanguageModelV2ToolCallPart
  ): Promise<ToolResult> {
    try {
      const { address, city = "" } = args;
      
      // 从环境变量获取高德API密钥
      const apiKey = process.env.AMAP_API_KEY || "041db813f69a2424f234fade1e3b3605";
      
      if (!apiKey) {
        return {
          content: [{
            type: "text",
            text: "高德地图API密钥未配置"
          }],
          isError: true
        };
      }

      // 调用高德地图地理编码API
      const url = `https://restapi.amap.com/v3/geocode/geo`;
      const params = new URLSearchParams({
        key: apiKey,
        address: address as string,
        city: city as string
      });

      const response = await fetch(`${url}?${params}`);
      const data = await response.json();

      if (data.status === "1" && data.geocodes?.length > 0) {
        const geocode = data.geocodes[0];
        const [lng, lat] = geocode.location.split(',').map(Number);
        
        const result = {
          address: geocode.formatted_address,
          location: {
            latitude: lat,
            longitude: lng
          },
          level: geocode.level,
          confidence: geocode.confidence || "high"
        };
        
        return {
          content: [{
            type: "text",
            text: JSON.stringify(result, null, 2)
          }]
        };
      } else {
        return {
          content: [{
            type: "text", 
            text: `地址解析失败: ${data.info || '未知错误'}`
          }],
          isError: true
        };
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        content: [{
          type: "text",
          text: `地理编码错误: ${errorMessage}`
        }],
        isError: true
      };
    }
  }
}
