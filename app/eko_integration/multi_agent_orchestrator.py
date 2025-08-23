from typing import List, Dict, Any, Optional, Tuple
import asyncio
import json
from dataclasses import dataclass
from enum import Enum

from app.eko_integration.eko_meetspot_framework import EkoMeetOrchestrator
from app.logger import logger

class AgentType(Enum):
    LOCATION = "location"
    POI_SEARCH = "poi_search"
    RECOMMENDATION = "recommendation"
    VISUALIZATION = "visualization"

@dataclass
class AgentTask:
    """智能体任务定义"""
    agent_type: AgentType
    task_id: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None  # type: ignore  # 依赖的任务ID
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class LocationInfo:
    """位置信息"""
    address: str
    latitude: float
    longitude: float
    formatted_address: str
    confidence: str

@dataclass
class POIInfo:
    """POI信息"""
    id: str
    name: str
    type: str
    address: str
    location: Dict[str, float]
    distance: float
    rating: Optional[str] = None
    cost: Optional[str] = None
    business_area: Optional[str] = None

class MultiAgentOrchestrator:
    """多智能体协调器"""
    
    def __init__(self, eko_orchestrator: EkoMeetOrchestrator):
        self.eko_orchestrator = eko_orchestrator
        self.tasks: Dict[str, AgentTask] = {}
        self.task_results: Dict[str, Any] = {}
        
    async def execute_recommendation_workflow(
        self, 
        addresses: List[str],
        keywords: str = "咖啡厅",
        radius: int = 1000,
        recommendation_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行完整的推荐工作流"""
        try:
            logger.info(f"开始执行多智能体推荐工作流: {addresses}, 关键词: {keywords}")
            
            # 步骤1: 地理编码 - 将地址转换为坐标
            location_tasks = []
            for i, address in enumerate(addresses):
                task = AgentTask(
                    agent_type=AgentType.LOCATION,
                    task_id=f"geocode_{i}",
                    input_data={"address": address}
                )
                location_tasks.append(task)
                self.tasks[task.task_id] = task
            
            # 并行执行地理编码
            geocode_results = await self._execute_location_agent_batch(location_tasks)
            
            # 步骤2: 计算中心点
            if len(geocode_results) > 1:
                center_point = self._calculate_center_point(geocode_results)
            else:
                center_point = geocode_results[0]
            
            logger.info(f"计算得到中心点: {center_point.latitude}, {center_point.longitude}")
            
            # 步骤3: POI搜索
            poi_task = AgentTask(
                agent_type=AgentType.POI_SEARCH,
                task_id="poi_search",
                input_data={
                    "keywords": keywords,
                    "location": f"{center_point.longitude},{center_point.latitude}",
                    "radius": radius
                },
                dependencies=[task.task_id for task in location_tasks]
            )
            self.tasks[poi_task.task_id] = poi_task
            
            poi_results = await self._execute_poi_search_agent(poi_task)
            
            # 步骤4: 智能推荐
            recommendation_task = AgentTask(
                agent_type=AgentType.RECOMMENDATION,
                task_id="smart_recommendation",
                input_data={
                    "pois": poi_results,
                    "criteria": recommendation_criteria or {},
                    "center_point": {
                        "latitude": center_point.latitude,
                        "longitude": center_point.longitude
                    },
                    "original_addresses": addresses
                },
                dependencies=[poi_task.task_id]
            )
            self.tasks[recommendation_task.task_id] = recommendation_task
            
            recommendations = await self._execute_recommendation_agent(recommendation_task)
            
            # 组装最终结果
            workflow_result = {
                "success": True,
                "center_point": {
                    "latitude": center_point.latitude,
                    "longitude": center_point.longitude,
                    "address": center_point.formatted_address
                },
                "original_locations": [
                    {
                        "address": loc.address,
                        "latitude": loc.latitude,
                        "longitude": loc.longitude
                    } for loc in geocode_results
                ],
                "search_criteria": {
                    "keywords": keywords,
                    "radius": radius,
                    "recommendation_criteria": recommendation_criteria
                },
                "recommendations": recommendations,
                "workflow_metadata": {
                    "total_candidates": len(poi_results),
                    "final_recommendations": len(recommendations.get("recommendations", [])),
                    "execution_time": "calculated",
                    "agents_used": ["LocationAgent", "POISearchAgent", "RecommendationAgent"]
                }
            }
            
            logger.info(f"多智能体工作流执行完成，推荐了 {len(recommendations.get('recommendations', []))} 个场所")
            return workflow_result
            
        except Exception as e:
            logger.error(f"多智能体工作流执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_metadata": {
                    "agents_used": [],
                    "execution_failed_at": "workflow_orchestration"
                }
            }
    
    async def _execute_location_agent_batch(self, tasks: List[AgentTask]) -> List[LocationInfo]:
        """批量执行地理编码任务"""
        results = []
        
        # 并行执行所有地理编码任务
        geocode_coroutines = []
        for task in tasks:
            coroutine = self._execute_single_geocode(task)
            geocode_coroutines.append(coroutine)
        
        geocode_results = await asyncio.gather(*geocode_coroutines, return_exceptions=True)
        
        for i, result in enumerate(geocode_results):
            if isinstance(result, Exception):
                tasks[i].status = "failed"
                tasks[i].error = str(result)
                logger.error(f"地理编码任务失败: {tasks[i].input_data['address']}, 错误: {result}")
            else:
                tasks[i].status = "completed"
                if isinstance(result, dict):
                    tasks[i].result = result
                else:
                    tasks[i].result = {"data": result}
                results.append(result)
        
        if not results:
            raise Exception("所有地理编码任务都失败了")
        
        return results
    
    async def _execute_single_geocode(self, task: AgentTask) -> LocationInfo:
        """执行单个地理编码任务"""
        try:
            # 调用Eko的地理编码工具
            geocode_method = getattr(self.eko_orchestrator, 'execute_geocode', None)
            if not geocode_method:
                raise Exception("地理编码方法不可用")
            
            result = await geocode_method(
                address=task.input_data["address"]
            )
            
            if not result.get("success"):
                raise Exception(f"地理编码失败: {result.get('error', '未知错误')}")
            
            location_data = result["result"]
            return LocationInfo(
                address=task.input_data["address"],
                latitude=location_data["location"]["latitude"],
                longitude=location_data["location"]["longitude"],
                formatted_address=location_data["address"],
                confidence=location_data.get("confidence", "medium")
            )
            
        except Exception as e:
            logger.error(f"地理编码执行错误: {str(e)}")
            raise
    
    def _calculate_center_point(self, locations: List[LocationInfo]) -> LocationInfo:
        """计算多个位置的中心点"""
        if len(locations) == 1:
            return locations[0]
        
        # 计算平均经纬度
        total_lat = sum(loc.latitude for loc in locations)
        total_lng = sum(loc.longitude for loc in locations)
        
        center_lat = total_lat / len(locations)
        center_lng = total_lng / len(locations)
        
        # 生成中心点描述
        addresses = [loc.address for loc in locations]
        center_description = f"中心点 (基于 {', '.join(addresses[:2])}{'等地' if len(addresses) > 2 else ''})"
        
        return LocationInfo(
            address=center_description,
            latitude=center_lat,
            longitude=center_lng,
            formatted_address=center_description,
            confidence="calculated"
        )
    
    async def _execute_poi_search_agent(self, task: AgentTask) -> List[Dict[str, Any]]:
        """执行POI搜索任务"""
        try:
            task.status = "running"
            
            # 调用Eko的POI搜索工具
            poi_search_method = getattr(self.eko_orchestrator, 'execute_poi_search', None)
            if not poi_search_method:
                raise Exception("POI搜索方法不可用")
            
            result = await poi_search_method(
                keywords=task.input_data["keywords"],
                location=task.input_data["location"],
                radius=task.input_data["radius"]
            )
            
            if not result.get("success"):
                raise Exception(f"POI搜索失败: {result.get('error', '未知错误')}")
            
            poi_data = result["result"]
            pois = poi_data.get("pois", [])
            
            task.status = "completed"
            task.result = pois
            
            logger.info(f"POI搜索完成，找到 {len(pois)} 个候选场所")
            return pois
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"POI搜索执行错误: {str(e)}")
            raise
    
    async def _execute_recommendation_agent(self, task: AgentTask) -> Dict[str, Any]:
        """执行智能推荐任务"""
        try:
            task.status = "running"
            
            # 调用Eko的智能推荐工具
            smart_recommendation_method = getattr(self.eko_orchestrator, 'execute_smart_recommendation', None)
            if not smart_recommendation_method:
                raise Exception("智能推荐方法不可用")
            
            result = await smart_recommendation_method(
                pois=task.input_data["pois"],
                criteria=task.input_data["criteria"]
            )
            
            if not result.get("success"):
                raise Exception(f"智能推荐失败: {result.get('error', '未知错误')}")
            
            recommendation_data = result["result"]
            
            task.status = "completed"
            task.result = recommendation_data
            
            logger.info(f"智能推荐完成，生成 {len(recommendation_data.get('recommendations', []))} 个推荐")
            return recommendation_data
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"智能推荐执行错误: {str(e)}")
            raise
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "agent_type": task.agent_type.value,
            "status": task.status,
            "error": task.error,
            "has_result": task.result is not None
        }
    
    def get_all_tasks_status(self) -> Dict[str, Any]:
        """获取所有任务状态"""
        return {
            task_id: self.get_task_status(task_id) 
            for task_id in self.tasks.keys()
        }
    
    def clear_completed_tasks(self):
        """清理已完成的任务"""
        completed_tasks = [
            task_id for task_id, task in self.tasks.items() 
            if task.status in ["completed", "failed"]
        ]
        
        for task_id in completed_tasks:
            del self.tasks[task_id]
        
        logger.info(f"清理了 {len(completed_tasks)} 个已完成的任务")