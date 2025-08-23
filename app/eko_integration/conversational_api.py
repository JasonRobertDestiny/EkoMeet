"""对话式推荐API接口
集成HumanInteractTool功能到FastAPI
"""

import uuid
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.logger import logger
from .conversational_recommender import EkoMeetConversationalRecommender, InteractionType


class ConversationStartRequest(BaseModel):
    """开始对话请求"""
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    class Config:
        # 确保UTF-8编码
        str_strip_whitespace = True
        validate_assignment = True

class ConversationResponseRequest(BaseModel):
    """用户响应请求"""
    session_id: str
    user_input: str
    interaction_type: Optional[str] = None
    
    class Config:
        # 确保UTF-8编码
        str_strip_whitespace = True
        validate_assignment = True


class ConversationResponse(BaseModel):
    """对话响应"""
    success: bool
    session_id: str
    type: str  # interaction, recommendation_result, error
    message: Optional[str] = None
    prompt: Optional[str] = None
    interaction_type: Optional[str] = None
    options: Optional[list] = None
    result: Optional[Dict[str, Any]] = None
    session_completed: bool = False
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationalRecommendationAPI:
    """对话式推荐API管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.recommender = EkoMeetConversationalRecommender(config)
        self.active_conversations: Dict[str, str] = {}  # session_id -> user_id mapping
    
    async def start_conversation(self, request: ConversationStartRequest) -> ConversationResponse:
        """开始新的对话会话"""
        try:
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 记录用户会话映射
            if request.user_id:
                self.active_conversations[session_id] = request.user_id
            
            # 启动对话
            result = await self.recommender.start_conversation(session_id)
            
            return ConversationResponse(
                success=True,
                session_id=session_id,
                type=result.get("type", "interaction"),
                prompt=result.get("prompt"),
                interaction_type=result.get("interaction_type"),
                options=result.get("options"),
                metadata={
                    "started_at": result.get("timestamp"),
                    "user_id": request.user_id
                }
            )
            
        except Exception as e:
            logger.error(f"启动对话会话失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"启动对话失败: {str(e)}")
    
    async def handle_user_response(self, request: ConversationResponseRequest) -> ConversationResponse:
        """处理用户响应"""
        try:
            # 验证会话存在
            if not self.recommender.get_session_state(request.session_id):
                raise HTTPException(status_code=404, detail="会话不存在或已过期")
            
            # 处理用户输入
            result = await self.recommender.handle_user_response(
                request.session_id, 
                request.user_input
            )
            
            if "error" in result:
                return ConversationResponse(
                    success=False,
                    session_id=request.session_id,
                    type="error",
                    error=result["error"]
                )
            
            # 构建响应
            response = ConversationResponse(
                success=result.get("success", True),
                session_id=request.session_id,
                type=result.get("type", "interaction"),
                message=result.get("message"),
                prompt=result.get("prompt"),
                interaction_type=result.get("interaction_type"),
                options=result.get("options"),
                result=result.get("result"),
                session_completed=result.get("session_completed", False)
            )
            
            # 如果会话完成，清理映射
            if response.session_completed and request.session_id in self.active_conversations:
                del self.active_conversations[request.session_id]
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"处理用户响应失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"处理响应失败: {str(e)}")
    
    async def get_conversation_status(self, session_id: str) -> Dict[str, Any]:
        """获取对话状态"""
        try:
            state = self.recommender.get_session_state(session_id)
            if not state:
                raise HTTPException(status_code=404, detail="会话不存在")
            
            return {
                "session_id": session_id,
                "current_step": state.current_step,
                "locations": state.locations,
                "preferences": state.user_preferences,
                "requirements": state.requirements,
                "last_interaction": state.last_interaction.isoformat() if state.last_interaction else None,
                "history_count": len(state.context_history)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取对话状态失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")
    
    async def cancel_conversation(self, session_id: str) -> Dict[str, Any]:
        """取消对话会话"""
        try:
            state = self.recommender.get_session_state(session_id)
            if not state:
                raise HTTPException(status_code=404, detail="会话不存在")
            
            # 清理会话
            if session_id in self.recommender.active_sessions:
                del self.recommender.active_sessions[session_id]
            
            if session_id in self.active_conversations:
                del self.active_conversations[session_id]
            
            return {
                "success": True,
                "message": "会话已取消",
                "session_id": session_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"取消对话失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"取消对话失败: {str(e)}")
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        return len(self.recommender.active_sessions)
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 30) -> int:
        """清理过期会话"""
        initial_count = len(self.recommender.active_sessions)
        self.recommender.cleanup_expired_sessions(timeout_minutes)
        
        # 同步清理API映射
        active_session_ids = set(self.recommender.active_sessions.keys())
        expired_mappings = [sid for sid in self.active_conversations.keys() 
                          if sid not in active_session_ids]
        
        for session_id in expired_mappings:
            del self.active_conversations[session_id]
        
        cleaned_count = initial_count - len(self.recommender.active_sessions)
        logger.info(f"清理了 {cleaned_count} 个过期会话")
        
        return cleaned_count


# 全局API实例
conversational_api: Optional[ConversationalRecommendationAPI] = None


def initialize_conversational_api(config: Dict[str, Any]) -> ConversationalRecommendationAPI:
    """初始化对话式推荐API"""
    global conversational_api
    conversational_api = ConversationalRecommendationAPI(config)
    return conversational_api


def get_conversational_api() -> ConversationalRecommendationAPI:
    """获取对话式推荐API实例"""
    if conversational_api is None:
        raise RuntimeError("对话式推荐API未初始化")
    return conversational_api


# FastAPI路由处理函数
async def start_conversation_endpoint(request: ConversationStartRequest) -> ConversationResponse:
    """开始对话端点"""
    api = get_conversational_api()
    return await api.start_conversation(request)


async def handle_response_endpoint(request: ConversationResponseRequest) -> ConversationResponse:
    """处理响应端点"""
    api = get_conversational_api()
    return await api.handle_user_response(request)


async def get_status_endpoint(session_id: str) -> Dict[str, Any]:
    """获取状态端点"""
    api = get_conversational_api()
    return await api.get_conversation_status(session_id)


async def cancel_conversation_endpoint(session_id: str) -> Dict[str, Any]:
    """取消对话端点"""
    api = get_conversational_api()
    return await api.cancel_conversation(session_id)


async def get_stats_endpoint() -> Dict[str, Any]:
    """获取统计信息端点"""
    api = get_conversational_api()
    return {
        "active_sessions": api.get_active_sessions_count(),
        "total_conversations": len(api.active_conversations)
    }