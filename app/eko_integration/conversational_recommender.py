"""MeetSpot智能对话推荐系统
基于Eko HumanInteractTool的对话式推荐引擎
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from app.logger import logger
from .eko_meetspot_framework import EkoMeetOrchestrator


class InteractionType(str, Enum):
    """交互类型枚举"""
    CONFIRM = "confirm"
    INPUT = "input"
    SELECT = "select"
    REQUEST_HELP = "request_help"


class ConversationState(BaseModel):
    """对话状态模型"""
    session_id: str
    current_step: str = "initial"
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    locations: List[str] = Field(default_factory=list)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    context_history: List[Dict] = Field(default_factory=list)
    last_interaction: Optional[datetime] = None


class ConversationStep:
    """对话步骤定义"""
    def __init__(self, step_id: str, prompt: str, interaction_type: InteractionType, 
                 options: Optional[List[str]] = None, validator: Optional[Callable] = None):
        self.step_id = step_id
        self.prompt = prompt
        self.interaction_type = interaction_type
        self.options = options or []
        self.validator = validator


class EkoMeetConversationalRecommender:
    """EkoMeet智能对话推荐器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator = EkoMeetOrchestrator(config)
        self.active_sessions: Dict[str, ConversationState] = {}
        self.conversation_flows = self._initialize_conversation_flows()
    
    def _initialize_conversation_flows(self) -> Dict[str, ConversationStep]:
        """初始化对话流程"""
        return {
            "initial": ConversationStep(
                "initial",
                "您好！我是EkoMeet智能推荐助手。请告诉我您想要寻找聚会地点的基本信息。您可以直接描述需求，比如'我们3个人想在北京找个咖啡馆聚会'。",
                InteractionType.INPUT
            ),
            "confirm_locations": ConversationStep(
                "confirm_locations",
                "我理解您提到了以下地点，请确认是否正确：{locations}",
                InteractionType.CONFIRM
            ),
            "gather_preferences": ConversationStep(
                "gather_preferences",
                "请选择您更偏好的聚会场所类型：",
                InteractionType.SELECT,
                ["咖啡馆", "餐厅", "茶馆", "酒吧", "图书馆", "公园", "商场", "其他"]
            ),
            "refine_requirements": ConversationStep(
                "refine_requirements",
                "请告诉我更多具体要求，比如：预算范围、环境偏好、特殊需求等。",
                InteractionType.INPUT
            ),
            "select_budget": ConversationStep(
                "select_budget",
                "请选择您的预算范围：",
                InteractionType.SELECT,
                ["经济实惠（人均50元以下）", "中等消费（人均50-150元）", "高端消费（人均150元以上）", "无预算限制"]
            ),
            "confirm_search": ConversationStep(
                "confirm_search",
                "根据您的需求，我将为您搜索：{summary}。是否开始搜索？",
                InteractionType.CONFIRM
            )
        }
    
    async def start_conversation(self, session_id: str) -> Dict[str, Any]:
        """开始新的对话会话"""
        conversation_state = ConversationState(
            session_id=session_id,
            last_interaction=datetime.now()
        )
        self.active_sessions[session_id] = conversation_state
        
        initial_step = self.conversation_flows["initial"]
        return await self._create_interaction_response(
            session_id, initial_step.prompt, initial_step.interaction_type
        )
    
    async def handle_user_response(self, session_id: str, user_input: Any) -> Dict[str, Any]:
        """处理用户响应"""
        if session_id not in self.active_sessions:
            return {"error": "会话不存在，请重新开始"}
        
        state = self.active_sessions[session_id]
        state.last_interaction = datetime.now()
        
        # 记录用户输入到历史
        state.context_history.append({
            "step": state.current_step,
            "user_input": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # 根据当前步骤处理用户输入
        return await self._process_step_response(session_id, user_input)
    
    async def _process_step_response(self, session_id: str, user_input: Any) -> Dict[str, Any]:
        """处理步骤响应"""
        state = self.active_sessions[session_id]
        current_step = state.current_step
        
        if current_step == "initial":
            return await self._process_initial_input(session_id, user_input)
        elif current_step == "confirm_locations":
            return await self._process_location_confirmation(session_id, user_input)
        elif current_step == "gather_preferences":
            return await self._process_preference_selection(session_id, user_input)
        elif current_step == "refine_requirements":
            return await self._process_requirements_input(session_id, user_input)
        elif current_step == "select_budget":
            return await self._process_budget_selection(session_id, user_input)
        elif current_step == "confirm_search":
            return await self._process_search_confirmation(session_id, user_input)
        else:
            return {"error": "未知的对话步骤"}
    
    async def _process_initial_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """处理初始输入"""
        state = self.active_sessions[session_id]
        
        # 使用NLP解析用户输入，提取地点信息
        extracted_info = await self._extract_info_from_input(user_input)
        
        if extracted_info.get("locations"):
            state.locations = extracted_info["locations"]
            state.user_preferences.update(extracted_info.get("preferences", {}))
            
            # 确认地点信息
            state.current_step = "confirm_locations"
            locations_str = "、".join(state.locations)
            prompt = self.conversation_flows["confirm_locations"].prompt.format(locations=locations_str)
            
            return await self._create_interaction_response(
                session_id, prompt, InteractionType.CONFIRM
            )
        else:
            # 需要更多信息
            return await self._create_interaction_response(
                session_id, 
                "我没有从您的描述中识别出具体地点。请提供参与聚会的人员所在位置，比如'小明在朝阳区，小红在海淀区'。",
                InteractionType.INPUT
            )
    
    async def _process_location_confirmation(self, session_id: str, confirmed: bool) -> Dict[str, Any]:
        """处理地点确认"""
        state = self.active_sessions[session_id]
        
        if confirmed:
            # 进入偏好收集
            state.current_step = "gather_preferences"
            step = self.conversation_flows["gather_preferences"]
            return await self._create_interaction_response(
                session_id, step.prompt, step.interaction_type, step.options
            )
        else:
            # 重新输入地点
            state.current_step = "initial"
            return await self._create_interaction_response(
                session_id,
                "请重新告诉我参与聚会的人员位置信息。",
                InteractionType.INPUT
            )
    
    async def _process_preference_selection(self, session_id: str, selected_type: str) -> Dict[str, Any]:
        """处理偏好选择"""
        state = self.active_sessions[session_id]
        state.user_preferences["venue_type"] = selected_type
        
        # 进入预算选择
        state.current_step = "select_budget"
        step = self.conversation_flows["select_budget"]
        return await self._create_interaction_response(
            session_id, step.prompt, step.interaction_type, step.options
        )
    
    async def _process_budget_selection(self, session_id: str, budget_range: str) -> Dict[str, Any]:
        """处理预算选择"""
        state = self.active_sessions[session_id]
        state.user_preferences["budget"] = budget_range
        
        # 进入需求细化
        state.current_step = "refine_requirements"
        step = self.conversation_flows["refine_requirements"]
        return await self._create_interaction_response(
            session_id, step.prompt, step.interaction_type
        )
    
    async def _process_requirements_input(self, session_id: str, requirements: str) -> Dict[str, Any]:
        """处理需求输入"""
        state = self.active_sessions[session_id]
        state.requirements["additional"] = requirements
        
        # 生成搜索摘要并确认
        summary = self._generate_search_summary(state)
        state.current_step = "confirm_search"
        
        prompt = self.conversation_flows["confirm_search"].prompt.format(summary=summary)
        return await self._create_interaction_response(
            session_id, prompt, InteractionType.CONFIRM
        )
    
    async def _process_search_confirmation(self, session_id: str, confirmed: bool) -> Dict[str, Any]:
        """处理搜索确认"""
        if confirmed:
            return await self._execute_recommendation_search(session_id)
        else:
            # 返回修改需求
            state = self.active_sessions[session_id]
            state.current_step = "refine_requirements"
            return await self._create_interaction_response(
                session_id,
                "请告诉我需要修改哪些要求？",
                InteractionType.INPUT
            )
    
    async def _execute_recommendation_search(self, session_id: str) -> Dict[str, Any]:
        """执行推荐搜索"""
        state = self.active_sessions[session_id]
        
        try:
            # 构建搜索参数
            keywords = self._map_venue_type_to_keywords(state.user_preferences.get("venue_type", "咖啡馆"))
            requirements = self._build_requirements_string(state)
            
            # 执行Eko工作流
            result = await self.orchestrator.execute_workflow(
                locations=state.locations,
                keywords=keywords,
                user_requirements=requirements
            )
            
            if result["success"]:
                # 清理会话
                del self.active_sessions[session_id]
                
                return {
                    "type": "recommendation_result",
                    "success": True,
                    "message": "推荐搜索完成！为您找到了以下聚会地点：",
                    "result": result,
                    "session_completed": True
                }
            else:
                return {
                    "type": "error",
                    "success": False,
                    "message": f"搜索过程中出现错误：{result.get('error', '未知错误')}",
                    "session_id": session_id
                }
        
        except Exception as e:
            logger.error(f"执行推荐搜索时出错: {str(e)}")
            return {
                "type": "error",
                "success": False,
                "message": "系统出现错误，请稍后重试",
                "session_id": session_id
            }
    
    async def _extract_info_from_input(self, user_input: str) -> Dict[str, Any]:
        """从用户输入中提取信息"""
        logger.info(f"开始提取用户输入信息: {user_input}")
        locations = []
        preferences = {}
        
        # 使用更智能的地点提取逻辑
        import re
        
        # 添加调试信息
        logger.info(f"用户输入字符串长度: {len(user_input)}")
        logger.info(f"用户输入字符编码: {[ord(c) for c in user_input[:10]]}")
        
        # 1. 寻找明确的地点模式："人名 + 在 + 地点"
        # 改进的正则表达式，支持更多格式
        person_location_patterns = [
            r'([\u4e00-\u9fff]+)在([\u4e00-\u9fff]+区)',  # 中文字符+在+区
            r'([\u4e00-\u9fff]+)在([\u4e00-\u9fff]+)',     # 中文字符+在+地点
            r'(\S+)在([^，,。\s]+)'                        # 原始模式
        ]
        
        for pattern in person_location_patterns:
            matches = re.findall(pattern, user_input)
            logger.info(f"正则模式 {pattern} 匹配结果: {matches}")
            
            for person, location in matches:
                locations.append(location)
                logger.info(f"提取到地点信息: {person} -> {location}")
            
            if matches:  # 如果找到匹配，跳出循环
                break
        
        # 2. 如果没有找到人名+地点模式，尝试提取包含地理关键词的词组
        if not locations:
            location_keywords = ["区", "路", "街", "大厦", "广场", "商场", "地铁站", "SOHO", "中心"]
            words = user_input.replace('，', ' ').replace(',', ' ').split()
            
            for word in words:
                if any(keyword in word for keyword in location_keywords) and len(word) > 2:
                    locations.append(word)
        
        # 3. 如果仍然没有找到，尝试提取城市+区域信息
        if not locations:
            city_pattern = r'(北京|上海|广州|深圳|杭州|成都|重庆|武汉|西安|南京)([^，,。\s]*区|[^，,。\s]*县)'
            city_matches = re.findall(city_pattern, user_input)
            for city, district in city_matches:
                locations.append(f"{city}{district}")
        
        # 提取场所类型偏好
        venue_mapping = {
            "咖啡": "咖啡馆",
            "餐厅": "餐厅", 
            "饭店": "餐厅",
            "茶": "茶馆",
            "酒吧": "酒吧",
            "图书馆": "图书馆",
            "公园": "公园"
        }
        
        for keyword, venue_type in venue_mapping.items():
            if keyword in user_input:
                preferences["venue_type"] = venue_type
                break
        
        result = {
            "locations": locations,
            "preferences": preferences
        }
        logger.info(f"信息提取结果: {result}")
        return result
    
    def _generate_search_summary(self, state: ConversationState) -> str:
        """生成搜索摘要"""
        summary_parts = []
        
        if state.locations:
            summary_parts.append(f"地点：{', '.join(state.locations)}")
        
        if state.user_preferences.get("venue_type"):
            summary_parts.append(f"类型：{state.user_preferences['venue_type']}")
        
        if state.user_preferences.get("budget"):
            summary_parts.append(f"预算：{state.user_preferences['budget']}")
        
        if state.requirements.get("additional"):
            summary_parts.append(f"特殊要求：{state.requirements['additional']}")
        
        return "；".join(summary_parts)
    
    def _map_venue_type_to_keywords(self, venue_type: str) -> str:
        """将场所类型映射为搜索关键词"""
        mapping = {
            "咖啡馆": "咖啡馆|咖啡厅|cafe",
            "餐厅": "餐厅|饭店|restaurant",
            "茶馆": "茶馆|茶楼|茶室",
            "酒吧": "酒吧|bar|pub",
            "图书馆": "图书馆|书店",
            "公园": "公园|广场",
            "商场": "商场|购物中心|mall"
        }
        return mapping.get(venue_type, "咖啡馆")
    
    def _build_requirements_string(self, state: ConversationState) -> str:
        """构建需求字符串"""
        requirements = []
        
        if state.user_preferences.get("budget"):
            requirements.append(f"预算要求：{state.user_preferences['budget']}")
        
        if state.requirements.get("additional"):
            requirements.append(state.requirements["additional"])
        
        return "；".join(requirements)
    
    async def _create_interaction_response(self, session_id: str, prompt: str, 
                                         interaction_type: InteractionType, 
                                         options: Optional[List[str]] = None) -> Dict[str, Any]:
        """创建交互响应"""
        response = {
            "type": "interaction",
            "session_id": session_id,
            "interaction_type": interaction_type.value,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        }
        
        if options and len(options) > 0:
            # 直接传递字符串列表
            response["options"] = ",".join(str(option) for option in options)
        
        return response
    
    def get_session_state(self, session_id: str) -> Optional[ConversationState]:
        """获取会话状态"""
        return self.active_sessions.get(session_id)
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 30):
        """清理过期会话"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, state in self.active_sessions.items():
            if state.last_interaction:
                time_diff = (current_time - state.last_interaction).total_seconds() / 60
                if time_diff > timeout_minutes:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"清理过期会话: {session_id}")