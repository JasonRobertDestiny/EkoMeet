"""
将Eko功能集成到现有FastAPI中
支持传统模式和Eko智能模式
"""

import asyncio
import time
from typing import Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from app.logger import logger
from .eko_meetspot_bridge import eko_bridge, EkoWorkflowResult


class EkoRecommendationRequest(BaseModel):
    """Eko推荐请求模型"""
    natural_language_query: str
    locations: Optional[List[str]] = None
    context: Optional[Dict] = None
    mode: str = "intelligent"  # intelligent, simple, complex


class EkoRecommendationResponse(BaseModel):
    """Eko推荐响应模型"""
    success: bool
    mode: str
    processing_time: float
    result: Optional[str] = None
    html_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None
    fallback_used: bool = False


async def handle_eko_recommendation(request: EkoRecommendationRequest) -> EkoRecommendationResponse:
    """
    处理Eko推荐请求
    支持智能模式和传统模式的自动降级
    """
    start_time = time.time()
    
    try:
        # 检查Eko可用性
        if not eko_bridge.is_available():
            logger.warning("Eko不可用，降级到传统模式")
            return await _fallback_to_traditional_mode(request, start_time)
        
        # 执行Eko工作流
        if request.mode == "simple" and request.locations:
            # 简单模式：兼容现有API
            result = await eko_bridge.simple_recommendation(
                locations=request.locations,
                keywords=request.context.get("keywords", "咖啡馆") if request.context else "咖啡馆",
                user_requirements=request.context.get("user_requirements", "") if request.context else ""
            )
        elif request.mode == "complex":
            # 复杂模式：多维度分析
            result = await eko_bridge.complex_analysis(
                locations=request.locations or [],
                venue_types=request.context.get("venue_types", ["咖啡馆"]) if request.context else ["咖啡馆"],
                budget_range=request.context.get("budget_range") if request.context else None,
                time_constraints=request.context.get("time_constraints") if request.context else None,
                accessibility_needs=request.context.get("accessibility_needs") if request.context else None
            )
        else:
            # 智能模式：自然语言处理
            result = await eko_bridge.execute_workflow(
                user_request=request.natural_language_query,
                context=request.context
            )
        
        processing_time = time.time() - start_time
        
        # 解析HTML URL
        html_url = None
        if result.success and result.metadata:
            html_url = result.metadata.get("html_url")
        
        return EkoRecommendationResponse(
            success=result.success,
            mode=request.mode,
            processing_time=processing_time,
            result=result.result,
            html_url=html_url,
            error=result.error,
            metadata=result.metadata,
            fallback_used=False
        )
        
    except Exception as e:
        logger.error(f"Eko推荐处理失败: {e}")
        # 自动降级到传统模式
        return await _fallback_to_traditional_mode(request, start_time)


async def _fallback_to_traditional_mode(request: EkoRecommendationRequest, start_time: float) -> EkoRecommendationResponse:
    """
    降级到传统推荐模式
    """
    try:
        # 导入传统推荐器
        from app.tool.meetspot_recommender import CafeRecommender
        
        # 从自然语言中提取位置信息（简单解析）
        locations = request.locations or _extract_locations_from_query(request.natural_language_query)
        
        if not locations:
            raise HTTPException(status_code=400, detail="无法从请求中提取位置信息")
        
        # 使用传统推荐器
        recommender = CafeRecommender()
        result = await recommender.execute(
            locations=locations,
            keywords=_extract_keywords_from_query(request.natural_language_query),
            user_requirements=_extract_requirements_from_query(request.natural_language_query)
        )
        
        processing_time = time.time() - start_time
        
        # 解析HTML文件路径
        html_url = None
        if hasattr(result, 'output') and result.output:
            import re
            html_match = re.search(r'HTML页面:\s*([^\s\n]+\.html)', result.output)
            if html_match:
                html_filename = html_match.group(1)
                html_url = f"/workspace/js_src/{html_filename}"
        
        return EkoRecommendationResponse(
            success=True,
            mode="fallback_traditional",
            processing_time=processing_time,
            result=result.output if hasattr(result, 'output') else str(result),
            html_url=html_url,
            error=None,
            metadata={"fallback_reason": "eko_unavailable"},
            fallback_used=True
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return EkoRecommendationResponse(
            success=False,
            mode="fallback_failed",
            processing_time=processing_time,
            result=None,
            html_url=None,
            error=str(e),
            metadata={"fallback_reason": "both_modes_failed"},
            fallback_used=True
        )


def _extract_locations_from_query(query: str) -> List[str]:
    """
    从自然语言查询中提取位置信息
    这是一个简化版本，实际应该使用更复杂的NLP
    """
    import re
    
    # 简单的位置模式匹配
    patterns = [
        r'位置[：:]\s*([^。]+)',
        r'地点[：:]\s*([^。]+)', 
        r'地址[：:]\s*([^。]+)',
        r'(\d+)\.\s*([^。\n]+)',  # 编号列表
    ]
    
    locations = []
    for pattern in patterns:
        matches = re.findall(pattern, query)
        for match in matches:
            if isinstance(match, tuple):
                locations.extend([m.strip() for m in match if m.strip()])
            else:
                locations.append(match.strip())
    
    # 去重并过滤
    unique_locations = []
    for loc in locations:
        if loc and len(loc) > 2 and loc not in unique_locations:
            unique_locations.append(loc)
    
    return unique_locations[:10]  # 最多10个位置


def _extract_keywords_from_query(query: str) -> str:
    """
    从查询中提取关键词
    """
    keywords_map = {
        "咖啡": "咖啡馆",
        "咖啡馆": "咖啡馆",
        "餐厅": "餐厅",
        "饭店": "餐厅", 
        "图书馆": "图书馆",
        "书店": "图书馆",
        "商场": "商场",
        "购物": "商场",
        "公园": "公园",
        "电影院": "电影院",
        "影院": "电影院",
        "篮球": "篮球场",
        "健身": "健身房",
        "KTV": "KTV",
        "博物馆": "博物馆"
    }
    
    for keyword, venue_type in keywords_map.items():
        if keyword in query:
            return venue_type
    
    return "咖啡馆"  # 默认


def _extract_requirements_from_query(query: str) -> str:
    """
    从查询中提取用户需求
    """
    requirements = []
    
    requirement_patterns = {
        "停车": ["停车", "车位", "停车场"],
        "安静": ["安静", "不吵", "安静"],
        "WiFi": ["wifi", "网络", "上网"],
        "充电": ["充电", "电源", "插座"],
        "商务": ["商务", "洽谈", "会议"],
        "环境好": ["环境", "装修", "氛围"],
        "便宜": ["便宜", "实惠", "经济"],
        "高档": ["高档", "豪华", "档次"]
    }
    
    for req, keywords in requirement_patterns.items():
        if any(keyword in query for keyword in keywords):
            requirements.append(req)
    
    return "，".join(requirements)
