"""
Eko集成所需的工具类定义
补充缺失的工具实现
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
import aiohttp
import math
from datetime import datetime
import hashlib
import os
from app.logger import logger


class EkoToolResult:
    """Eko工具执行结果"""
    def __init__(self, success: bool = True, result: Any = None, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.result = result
        self.error = error
        self.metadata = metadata or {}


class EkoTool:
    """Eko风格的工具基类"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        """执行工具逻辑"""
        raise NotImplementedError


class GeocodeEkoTool(EkoTool):
    """地理编码工具"""
    
    def __init__(self):
        super().__init__(
            name="geocode_address",
            description="将地址转换为经纬度坐标",
            parameters={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "地址描述"}
                },
                "required": ["address"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            from app.logger import logger
            address = args.get("address", "")
            config = context.get("config", {})
            
            logger.info(f"GeocodeEkoTool开始处理地址: {address}")
            
            # 调用高德地图地理编码API - 多种方式获取API密钥
            api_key = ""
            
            # 方式1: 从config字典中获取
            if isinstance(config, dict) and config.get("amap_api_key"):
                api_key = config["amap_api_key"]
                logger.info("使用config字典中的API密钥")
            # 方式2: 从config对象的amap属性获取
            elif hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
                api_key = config.amap.api_key
                logger.info("使用config对象中的API密钥")
            # 方式3: 从环境变量获取
            else:
                api_key = os.getenv("AMAP_API_KEY", "")
                logger.info("使用环境变量中的API密钥")
            
            if not api_key:
                logger.error("高德地图API密钥未配置")
                return EkoToolResult(success=False, error="高德地图API密钥未配置")
            
            logger.info(f"API密钥已获取，长度: {len(api_key)}")
            
            url = "https://restapi.amap.com/v3/geocode/geo"
            params = {
                "key": api_key,
                "address": address,
                "output": "json"
            }
            
            logger.info(f"发送地理编码请求: {url}")
            logger.info(f"请求参数: {params}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    logger.info(f"API响应状态码: {response.status}")
                    data = await response.json()
                    logger.info(f"API响应数据: {data}")
                    
                    if data.get("status") == "1" and data.get("geocodes"):
                        location = data["geocodes"][0]["location"].split(",")
                        result = {
                            "address": address,
                            "longitude": float(location[0]),
                            "latitude": float(location[1]),
                            "formatted_address": data["geocodes"][0].get("formatted_address", address)
                        }
                        logger.info(f"地理编码成功: {result}")
                        return EkoToolResult(success=True, result=result)
                    else:
                        error_msg = f"地理编码失败: {data.get('info', '未知错误')}"
                        logger.error(error_msg)
                        return EkoToolResult(success=False, error=error_msg)
        
        except Exception as e:
            logger.error(f"地理编码异常: {str(e)}")
            return EkoToolResult(success=False, error=f"地理编码异常: {str(e)}")


class CenterPointCalculatorTool(EkoTool):
    """中心点计算工具"""
    
    def __init__(self):
        super().__init__(
            name="calculate_center",
            description="计算多个位置的几何中心点",
            parameters={
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "位置对象数组，包含longitude和latitude"
                    }
                },
                "required": ["locations"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            locations = args.get("locations", [])
            
            if not locations:
                return EkoToolResult(success=False, error="位置列表为空")
            
            total_lng = sum(loc["longitude"] for loc in locations)
            total_lat = sum(loc["latitude"] for loc in locations)
            
            center = {
                "longitude": total_lng / len(locations),
                "latitude": total_lat / len(locations),
                "count": len(locations)
            }
            
            return EkoToolResult(success=True, result=center)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"中心点计算异常: {str(e)}")


class DistanceCalculatorTool(EkoTool):
    """距离计算工具"""
    
    def __init__(self):
        super().__init__(
            name="calculate_distance",
            description="计算两点之间的距离",
            parameters={
                "type": "object",
                "properties": {
                    "point1": {"type": "object", "description": "起点坐标"},
                    "point2": {"type": "object", "description": "终点坐标"}
                },
                "required": ["point1", "point2"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            point1 = args["point1"]
            point2 = args["point2"]
            
            # 使用Haversine公式计算距离
            lat1, lng1 = math.radians(point1["latitude"]), math.radians(point1["longitude"])
            lat2, lng2 = math.radians(point2["latitude"]), math.radians(point2["longitude"])
            
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            distance = 6371 * c * 1000  # 转换为米
            
            return EkoToolResult(success=True, result={"distance_meters": distance})
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"距离计算异常: {str(e)}")


class AmapSearchEkoTool(EkoTool):
    """高德地图POI搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="search_nearby_pois",
            description="搜索指定位置附近的POI",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "中心点坐标 lng,lat"},
                    "keywords": {"type": "string", "description": "搜索关键词"},
                    "radius": {"type": "number", "description": "搜索半径（米）", "default": 2000}
                },
                "required": ["location", "keywords"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            config = context.get("config", {})
            
            if hasattr(config, 'amap') and config.amap:
                api_key = config.amap.api_key
            else:
                api_key = os.getenv("AMAP_API_KEY", "")
            
            if not api_key:
                return EkoToolResult(success=False, error="高德地图API密钥未配置")
            
            url = "https://restapi.amap.com/v3/place/around"
            params = {
                "key": api_key,
                "location": args["location"],
                "keywords": args["keywords"],
                "radius": args.get("radius", 2000),
                "output": "json",
                "offset": 20
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "1":
                        pois = []
                        for poi in data.get("pois", []):
                            location_parts = poi.get("location", "0,0").split(",")
                            pois.append({
                                "id": poi.get("id"),
                                "name": poi.get("name"),
                                "address": poi.get("address"),
                                "longitude": float(location_parts[0]) if len(location_parts) > 0 else 0,
                                "latitude": float(location_parts[1]) if len(location_parts) > 1 else 0,
                                "distance": poi.get("distance"),
                                "tel": poi.get("tel"),
                                "type": poi.get("type")
                            })
                        
                        return EkoToolResult(success=True, result=pois)
                    else:
                        return EkoToolResult(success=False, error=f"POI搜索失败: {data.get('info', '未知错误')}")
        
        except Exception as e:
            return EkoToolResult(success=False, error=f"POI搜索异常: {str(e)}")


class POIFilterTool(EkoTool):
    """POI过滤工具"""
    
    def __init__(self):
        super().__init__(
            name="filter_pois",
            description="过滤和初步排序POI",
            parameters={
                "type": "object",
                "properties": {
                    "pois": {"type": "array", "description": "POI列表"},
                    "center": {"type": "object", "description": "中心点坐标"}
                },
                "required": ["pois"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            pois = args.get("pois", [])
            center = args.get("center", {})
            
            # 简单过滤：移除无效POI
            filtered_pois = [
                poi for poi in pois 
                if poi.get("name") and poi.get("address")
            ]
            
            # 按距离排序
            if center:
                for poi in filtered_pois:
                    if poi.get("distance"):
                        poi["distance_meters"] = int(poi["distance"])
                    else:
                        poi["distance_meters"] = 9999
                
                filtered_pois.sort(key=lambda x: x.get("distance_meters", 9999))
            
            return EkoToolResult(success=True, result=filtered_pois[:10])  # 取前10个
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"POI过滤异常: {str(e)}")


class SmartRankingTool(EkoTool):
    """智能排序工具"""
    
    def __init__(self):
        super().__init__(
            name="smart_ranking",
            description="对POI进行智能排序",
            parameters={
                "type": "object",
                "properties": {
                    "pois": {"type": "array", "description": "POI列表"},
                    "preferences": {"type": "object", "description": "用户偏好"}
                },
                "required": ["pois"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            pois = args.get("pois", [])
            preferences = args.get("preferences", {})
            
            # 简单的评分算法
            for poi in pois:
                score = 0
                
                # 距离评分 (越近越好)
                distance = poi.get("distance_meters", 9999)
                if distance < 500:
                    score += 30
                elif distance < 1000:
                    score += 20
                elif distance < 2000:
                    score += 10
                
                # 名称质量评分
                name = poi.get("name", "")
                if any(keyword in name for keyword in ["星巴克", "Costa", "瑞幸"]):
                    score += 20
                
                # 地址完整性评分
                if poi.get("address") and len(poi.get("address", "")) > 10:
                    score += 10
                
                # 联系方式评分
                if poi.get("tel"):
                    score += 5
                
                poi["smart_score"] = score
            
            # 按评分排序
            pois.sort(key=lambda x: x.get("smart_score", 0), reverse=True)
            
            return EkoToolResult(success=True, result=pois)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"智能排序异常: {str(e)}")


class PreferenceAnalyzerTool(EkoTool):
    """偏好分析工具"""
    
    def __init__(self):
        super().__init__(
            name="analyze_preferences",
            description="分析用户偏好",
            parameters={
                "type": "object",
                "properties": {
                    "requirements": {"type": "string", "description": "用户需求描述"},
                    "pois": {"type": "array", "description": "POI列表"}
                },
                "required": ["requirements"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            requirements = args.get("requirements", "")
            
            preferences = {
                "budget_conscious": "便宜" in requirements or "实惠" in requirements,
                "quiet_environment": "安静" in requirements or "不吵" in requirements,
                "parking_needed": "停车" in requirements or "车位" in requirements,
                "wifi_needed": "wifi" in requirements.lower() or "网络" in requirements,
                "business_meeting": "商务" in requirements or "会议" in requirements,
                "high_end": "高档" in requirements or "豪华" in requirements
            }
            
            return EkoToolResult(success=True, result=preferences)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"偏好分析异常: {str(e)}")


class ResultOptimizerTool(EkoTool):
    """结果优化工具"""
    
    def __init__(self):
        super().__init__(
            name="optimize_results",
            description="优化推荐结果",
            parameters={
                "type": "object",
                "properties": {
                    "recommendations": {"type": "array", "description": "推荐列表"},
                    "criteria": {"type": "object", "description": "优化标准"}
                },
                "required": ["recommendations"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            recommendations = args.get("recommendations", [])
            
            # 简单的结果优化：确保多样性
            optimized = []
            seen_names = set()
            
            for rec in recommendations:
                name = rec.get("name", "")
                # 避免重复的连锁店
                base_name = name.split("(")[0].strip()
                if base_name not in seen_names:
                    optimized.append(rec)
                    seen_names.add(base_name)
                
                if len(optimized) >= 5:  # 最多5个推荐
                    break
            
            return EkoToolResult(success=True, result=optimized)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"结果优化异常: {str(e)}")


class HTMLReportGeneratorTool(EkoTool):
    """HTML报告生成工具"""
    
    def __init__(self):
        super().__init__(
            name="generate_html_report",
            description="生成HTML推荐报告",
            parameters={
                "type": "object",
                "properties": {
                    "recommendations": {"type": "array", "description": "推荐列表"},
                    "user_locations": {"type": "array", "description": "用户位置"},
                    "center_point": {"type": "object", "description": "中心点"}
                },
                "required": ["recommendations"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            recommendations = args.get("recommendations", [])
            user_locations = args.get("user_locations", [])
            center_point = args.get("center_point", {})
            
            # 生成HTML内容
            html_content = self._generate_html(recommendations, user_locations, center_point)
            
            # 保存文件
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"eko_recommendation_{timestamp}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}.html"
            
            # 确保目录存在
            workspace_dir = os.path.join(os.getcwd(), "workspace", "js_src")
            os.makedirs(workspace_dir, exist_ok=True)
            
            file_path = os.path.join(workspace_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            result = {
                "html_file": filename,
                "html_path": file_path,
                "url": f"/workspace/js_src/{filename}"
            }
            
            return EkoToolResult(success=True, result=result)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"HTML生成异常: {str(e)}")
    
    def _generate_html(self, recommendations, user_locations, center_point):
        """生成HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Eko智能推荐结果</title>
    <style>
        body {{ 
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1200px; margin: 0 auto; 
            background: white; border-radius: 15px; overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px; text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 2.5rem; }}
        .subtitle {{ margin: 10px 0; opacity: 0.9; }}
        .powered-by {{
            background: rgba(255,255,255,0.1);
            padding: 10px 20px; border-radius: 25px; 
            display: inline-block; margin-top: 20px;
        }}
        .content {{ padding: 40px; }}
        .summary {{
            background: #f8f9fa; padding: 25px; border-radius: 10px;
            margin-bottom: 30px; border-left: 5px solid #667eea;
        }}
        .poi-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px; margin-top: 30px;
        }}
        .poi-card {{
            background: white; border-radius: 15px; padding: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: all 0.3s ease; border: 2px solid transparent;
        }}
        .poi-card:hover {{ 
            transform: translateY(-10px); 
            border-color: #667eea;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        .poi-name {{ 
            font-size: 1.4rem; color: #333; margin-bottom: 15px; 
            font-weight: bold; display: flex; align-items: center;
        }}
        .poi-name::before {{
            content: "📍"; margin-right: 10px; font-size: 1.2rem;
        }}
        .poi-score {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; padding: 8px 15px; border-radius: 20px;
            font-size: 0.9rem; font-weight: bold; float: right;
        }}
        .poi-info {{ 
            margin: 12px 0; color: #666; display: flex; align-items: center;
        }}
        .poi-info i {{ margin-right: 10px; width: 20px; }}
        .distance-badge {{
            background: #e8f4f8; color: #2c5aa0; 
            padding: 6px 12px; border-radius: 15px; 
            font-weight: bold; margin-top: 15px; display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Eko智能推荐</h1>
            <p class="subtitle">基于多Agent协作的智能会面地点推荐</p>
            <div class="powered-by">
                ⚡ Powered by Eko Framework × EkoMeet
            </div>
        </div>
        
        <div class="content">
            <div class="summary">
                <h3>📊 推荐概况</h3>
                <p><strong>推荐场所数量:</strong> {len(recommendations)} 个</p>
                <p><strong>用户位置数量:</strong> {len(user_locations)} 个</p>
                <p><strong>中心坐标:</strong> {center_point.get('longitude', 'N/A')}, {center_point.get('latitude', 'N/A')}</p>
                <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h3>🎯 智能推荐结果</h3>
            <div class="poi-grid">
                {self._generate_poi_cards(recommendations)}
            </div>
            
            <div style="text-align: center; margin-top: 40px; color: #666;">
                <p>🚀 本推荐由Eko多Agent智能系统生成，结合了地理分析、偏好学习和智能排序算法</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_poi_cards(self, recommendations):
        """生成POI卡片HTML"""
        cards = []
        for i, poi in enumerate(recommendations):
            cards.append(f"""
                <div class="poi-card">
                    <div class="poi-name">
                        {i + 1}. {poi.get('name', '未知场所')}
                        <div class="poi-score">评分: {poi.get('smart_score', 0)}</div>
                    </div>
                    <div class="poi-info">
                        <i>📍</i> {poi.get('address', '地址信息缺失')}
                    </div>
                    <div class="poi-info">
                        <i>📞</i> {poi.get('tel', '电话信息缺失')}
                    </div>
                    <div class="poi-info">
                        <i>🏷️</i> {poi.get('type', '类型未知')}
                    </div>
                    <div class="distance-badge">
                        🚶 距离中心: {poi.get('distance_meters', 'N/A')} 米
                    </div>
                </div>
            """)
        return ''.join(cards)


class MapVisualizationTool(EkoTool):
    """地图可视化工具"""
    
    def __init__(self):
        super().__init__(
            name="create_map_visualization",
            description="创建地图可视化",
            parameters={
                "type": "object",
                "properties": {
                    "center": {"type": "object", "description": "中心点"},
                    "pois": {"type": "array", "description": "POI列表"}
                },
                "required": ["center"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            # 简化实现：返回地图配置
            result = {
                "map_config": args,
                "map_type": "amap",
                "zoom_level": 15
            }
            return EkoToolResult(success=True, result=result)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"地图可视化异常: {str(e)}")


class RouteOptimizerTool(EkoTool):
    """路线优化工具"""
    
    def __init__(self):
        super().__init__(
            name="optimize_routes",
            description="优化到达路线",
            parameters={
                "type": "object",
                "properties": {
                    "destinations": {"type": "array", "description": "目的地列表"},
                    "origins": {"type": "array", "description": "起点列表"}
                },
                "required": ["destinations"]
            }
        )
    
    async def execute(self, args: Dict[str, Any], context: Any) -> EkoToolResult:
        try:
            # 简化实现：返回路线建议
            result = {
                "route_suggestions": ["建议使用公共交通", "预计路程15-30分钟"],
                "traffic_status": "正常"
            }
            return EkoToolResult(success=True, result=result)
            
        except Exception as e:
            return EkoToolResult(success=False, error=f"路线优化异常: {str(e)}")
