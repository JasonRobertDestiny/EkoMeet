"""
EkoMeet + Eko 集成核心类
支持Python后端与TypeScript eko框架的桥接
"""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from app.logger import logger
from app.config import config
from .eko_tools import (
    GeocodeEkoTool, AmapSearchEkoTool, RouteOptimizerTool, SmartRankingTool
)


@dataclass
class EkoWorkflowResult:
    """Eko工作流执行结果"""
    success: bool
    result: str
    task_id: str
    processing_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EkoMeetBridge:
    """EkoMeet与Eko框架的桥接类"""
    
    def __init__(self):
        self.eko_script_path = Path(__file__).parent / "offline_eko_test.js"  # 使用离线版智能脚本
        self.temp_dir = Path(tempfile.gettempdir()) / "meetspot_eko"
        self.temp_dir.mkdir(exist_ok=True)
        
    async def execute_workflow(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> EkoWorkflowResult:
        """
        执行eko工作流
        
        Args:
            user_request: 用户的自然语言请求
            context: 上下文信息（位置、偏好等）
            
        Returns:
            EkoWorkflowResult: 执行结果
        """
        import time
        start_time = time.time()
        
        try:
            # 准备输入数据
            input_data = {
                "request": user_request,
                "context": context or {},
                "config": {
                    "amap_api_key": config.amap.api_key if config and config.amap else "",
                    "temp_dir": str(self.temp_dir)
                }
            }
            
            # 写入临时文件
            input_file = self.temp_dir / f"input_{int(time.time())}.json"
            output_file = self.temp_dir / f"output_{int(time.time())}.json"
            
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(input_data, f, ensure_ascii=False, indent=2)
            
            # 执行Node.js脚本，传递输入文件路径
            cmd = ["node", str(self.eko_script_path), str(input_file)]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            logger.info(f"工作目录: {self.eko_script_path.parent}")
            logger.info(f"输入文件: {input_file}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.eko_script_path.parent)
            )
            
            stdout, stderr = await process.communicate()
            
            processing_time = time.time() - start_time
            
            # 解码输出用于调试
            output_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
            error_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            logger.info(f"Node.js脚本返回码: {process.returncode}")
            logger.info(f"stdout长度: {len(output_text)}")
            if error_text:
                logger.error(f"stderr内容: {error_text}")
            if output_text:
                logger.info(f"stdout前500字符: {output_text[:500]}")
            
            if process.returncode == 0:
                # 解析输出，获取生成的文件路径
                html_url = None
                
                # 从输出中提取HTML文件名
                import re
                html_match = re.search(r'HTML报告: ([^\s\n]+\.html)', output_text)
                if html_match:
                    html_filename = html_match.group(1)
                    # 将文件移动到workspace目录
                    source_path = self.eko_script_path.parent / html_filename
                    target_dir = Path("workspace/js_src")
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_path = target_dir / html_filename
                    
                    if source_path.exists():
                        import shutil
                        shutil.move(str(source_path), str(target_path))
                        html_url = f"/workspace/js_src/{html_filename}"
                
                return EkoWorkflowResult(
                    success=True,
                    result=f"Eko智能推荐生成成功\n{output_text}",
                    task_id=f"eko_{int(time.time())}",
                    processing_time=processing_time,
                    metadata={
                        "html_url": html_url,
                        "mode": "eko_intelligent",
                        "eko_output": output_text
                    }
                )
            else:
                raise Exception(f"Eko脚本执行失败，返回码: {process.returncode}, stderr: {error_text}")
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Eko workflow执行失败: {e}")
            
            return EkoWorkflowResult(
                success=False,
                result="",
                task_id="",
                processing_time=processing_time,
                error=str(e)
            )
    
    async def simple_recommendation(
        self,
        locations: List[str],
        keywords: str = "咖啡馆",
        user_requirements: str = ""
    ) -> EkoWorkflowResult:
        """
        简单推荐工作流
        兼容现有API格式
        """
        user_request = f"""
        请为以下位置推荐会面地点：
        
        参与者位置：
        {chr(10).join(f"{i+1}. {loc}" for i, loc in enumerate(locations))}
        
        场所类型：{keywords}
        {f"特殊要求：{user_requirements}" if user_requirements else ""}
        
        请提供详细的推荐结果，包括：
        1. 推荐场所列表（至少3个）
        2. 每个场所的详细信息（地址、评分、特色）
        3. 距离各参与者的路程和时间
        4. 推荐理由
        """
        
        context = {
            "workflow_type": "simple_recommendation",
            "locations": locations,
            "keywords": keywords,
            "user_requirements": user_requirements
        }
        
        return await self.execute_workflow(user_request, context)
    
    async def complex_analysis(
        self,
        locations: List[str],
        venue_types: List[str],
        budget_range: Optional[str] = None,
        time_constraints: Optional[str] = None,
        accessibility_needs: Optional[str] = None
    ) -> EkoWorkflowResult:
        """
        复杂分析工作流
        支持多维度分析和推荐
        """
        user_request = f"""
        请进行复杂的会面地点分析和推荐：
        
        参与者位置：
        {chr(10).join(f"{i+1}. {loc}" for i, loc in enumerate(locations))}
        
        场所类型：{', '.join(venue_types)}
        {f"预算范围：{budget_range}" if budget_range else ""}
        {f"时间限制：{time_constraints}" if time_constraints else ""}
        {f"无障碍需求：{accessibility_needs}" if accessibility_needs else ""}
        
        请提供：
        1. 多场景推荐方案（工作日/周末，白天/晚上）
        2. 成本效益分析
        3. 风险评估（交通、天气、人流量）
        4. 替代方案
        5. 详细的可视化报告
        """
        
        context = {
            "workflow_type": "complex_analysis",
            "locations": locations,
            "venue_types": venue_types,
            "budget_range": budget_range,
            "time_constraints": time_constraints,
            "accessibility_needs": accessibility_needs
        }
        
        return await self.execute_workflow(user_request, context)
    
    async def call_multi_agent_tool(self, tool_name: str, params: Dict[str, Any]) -> EkoWorkflowResult:
        """
        调用多智能体工具 - 现在使用Python实现的Eko工具
        
        Args:
            tool_name: 工具名称 (GeocodeTool, POISearchTool, RoutePlanTool, SmartRecommendationTool)
            params: 工具参数
            
        Returns:
            EkoWorkflowResult: 执行结果
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"执行多智能体工具: {tool_name}")
            
            # 根据工具名称调用对应的Python实现
            if tool_name == "GeocodeTool":
                geocode_tool = GeocodeEkoTool()
                result = await geocode_tool.execute(params, {"config": None})
                return EkoWorkflowResult(
                    success=result.success,
                    result=result.result,
                    task_id=f"geocode_{int(time.time())}",
                    processing_time=time.time() - start_time,
                    error=result.error
                )
            elif tool_name == "POISearchTool":
                poi_tool = AmapSearchEkoTool()
                result = await poi_tool.execute(params, {"config": None})
                return EkoWorkflowResult(
                    success=result.success,
                    result=result.result,
                    task_id=f"search_{int(time.time())}",
                    processing_time=time.time() - start_time,
                    error=result.error
                )
            elif tool_name == "RoutePlanTool":
                route_tool = RouteOptimizerTool()
                result = await route_tool.execute(params, {"config": None})
                return EkoWorkflowResult(
                    success=result.success,
                    result=result.result,
                    task_id=f"route_{int(time.time())}",
                    processing_time=time.time() - start_time,
                    error=result.error
                )
            elif tool_name == "SmartRecommendationTool":
                ranking_tool = SmartRankingTool()
                result = await ranking_tool.execute(params, {"config": None})
                return EkoWorkflowResult(
                    success=result.success,
                    result=result.result,
                    task_id=f"ranking_{int(time.time())}",
                    processing_time=time.time() - start_time,
                    error=result.error
                )
            else:
                logger.error(f"未知的工具名称: {tool_name}")
                return EkoWorkflowResult(
                    success=False,
                    result="",
                    task_id="",
                    processing_time=time.time() - start_time,
                    error=f"未知的工具名称: {tool_name}"
                )
                
        except Exception as e:
            logger.error(f"调用多智能体工具异常: {str(e)}")
            return EkoWorkflowResult(
                success=False,
                result="",
                task_id="",
                processing_time=time.time() - start_time,
                error=f"调用多智能体工具异常: {str(e)}"
            )
    
    async def geocode_location(self, address: str) -> EkoWorkflowResult:
        """地理编码工具"""
        return await self.call_multi_agent_tool("GeocodeTool", {"address": address})
    
    async def search_poi(self, keywords: str, location: str, radius: int = 3000, page_size: int = 20) -> EkoWorkflowResult:
        """POI搜索工具"""
        return await self.call_multi_agent_tool("POISearchTool", {
            "keywords": keywords,
            "location": location,
            "radius": radius,
            "page_size": page_size
        })
    
    async def plan_route(self, origin: str, destination: str, strategy: int = 0) -> EkoWorkflowResult:
        """路径规划工具"""
        import time
        start_time = time.time()
        
        try:
            # 使用路径规划工具
            route_tool = RouteOptimizerTool()
            result = await route_tool.execute({
                "origin": origin,
                "destination": destination,
                "strategy": strategy
            }, {"config": None})
            
            return EkoWorkflowResult(
                success=result.success,
                result=result.result,
                task_id=f"plan_route_{int(time.time())}",
                processing_time=time.time() - start_time,
                error=result.error
            )
            
        except Exception as e:
            logger.error(f"路径规划执行失败: {str(e)}")
            return EkoWorkflowResult(
                success=False,
                result="",
                task_id=f"plan_route_error_{int(time.time())}",
                processing_time=time.time() - start_time,
                error=f"路径规划执行失败: {str(e)}"
            )
    
    async def smart_recommend(self, user_location: str, criteria: Dict[str, Any]) -> EkoWorkflowResult:
        """智能推荐工具"""
        import time
        start_time = time.time()
        
        try:
            # 使用智能推荐工具
            ranking_tool = SmartRankingTool()
            result = await ranking_tool.execute({
                "user_location": user_location,
                "criteria": criteria
            }, {"config": None})
            
            return EkoWorkflowResult(
                success=result.success,
                result=result.result,
                task_id=f"smart_recommend_{int(time.time())}",
                processing_time=time.time() - start_time,
                error=result.error
            )
            
        except Exception as e:
            logger.error(f"智能推荐执行失败: {str(e)}")
            return EkoWorkflowResult(
                success=False,
                result="",
                task_id=f"smart_recommend_error_{int(time.time())}",
                processing_time=time.time() - start_time,
                error=f"智能推荐执行失败: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """检查eko集成是否可用"""
        try:
            # 检查Node.js是否可用
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False
                
            # 检查eko脚本是否存在
            return self.eko_script_path.exists()
            
        except Exception:
            return False


# 全局实例
eko_bridge = EkoMeetBridge()


async def get_eko_recommendation(
    user_request: str,
    context: Optional[Dict[str, Any]] = None
) -> EkoWorkflowResult:
    """
    获取eko推荐结果的便捷函数
    """
    if not eko_bridge.is_available():
        return EkoWorkflowResult(
            success=False,
            result="",
            task_id="",
            processing_time=0,
            error="Eko集成不可用"
        )
    
    return await eko_bridge.execute_workflow(user_request, context)
