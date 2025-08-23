import sys
import os
import time
import asyncio
import re
import json
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 创建通用的Result类
class Result:
    """通用的结果类"""
    def __init__(self, output):
        self.output = output
        
    def __str__(self):
        return str(self.output)

# 数据模型定义
class ApiEkoRecommendationRequest(BaseModel):
    query: str
    locations: Optional[List[str]] = None
    
class ApiEkoRecommendationResponse(BaseModel):
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    
class ConversationStartRequest(BaseModel):
    user_input: str
    
class ConversationResponseRequest(BaseModel):
    session_id: str
    user_input: str
    
class ConversationResponse(BaseModel):
    session_id: str
    message: str
    type: str = "message"

class LocationRequest(BaseModel):
    locations: List[str]
    venue_types: Optional[List[str]] = ["咖啡馆"]
    user_requirements: Optional[str] = ""

class EkoMeetRequest(BaseModel):
    locations: List[str]
    keywords: Optional[str] = "咖啡馆"
    place_type: Optional[str] = ""
    user_requirements: Optional[str] = ""
    theme: Optional[str] = ""

class EkoSmartRequest(BaseModel):
    """Eko智能推荐请求"""
    query: str
    locations: Optional[List[str]] = None
    mode: str = "intelligent"
    context: Optional[Dict] = None

# 导入应用模块
try:
    from app.config import config
    from app.tool.meetspot_recommender import CafeRecommender
    from app.logger import logger
    print("✅ 成功导入所有必要模块")
    config_available = True
except ImportError as e:
    print(f"⚠️ 导入模块警告: {e}")
    config = None
    config_available = False
    CafeRecommender = None
    # 创建备用logger
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# 尝试导入Eko集成模块
eko_available = False
try:
    from app.eko_integration.api_integration import handle_eko_recommendation as _handle_eko
    from app.eko_integration.api_integration import EkoRecommendationRequest as EkoApiRequest
    
    async def handle_eko_recommendation(request: ApiEkoRecommendationRequest) -> ApiEkoRecommendationResponse:
        try:
            # 转换为Eko API所需的格式
            eko_request = EkoApiRequest(
                natural_language_query=request.query,
                locations=request.locations,
                context=None,
                mode="intelligent"
            )
            
            result = await _handle_eko(eko_request)
            
            # 处理返回结果
            if isinstance(result, dict):
                return ApiEkoRecommendationResponse(
                    success=result.get('success', False),
                    result=result.get('result'),
                    error=result.get('error')
                )
            else:
                # 如果返回的是对象，尝试访问属性
                return ApiEkoRecommendationResponse(
                    success=getattr(result, 'success', False),
                    result=getattr(result, 'result', None),
                    error=getattr(result, 'error', None)
                )
        except Exception as e:
            return ApiEkoRecommendationResponse(
                success=False,
                error=f"Eko处理错误: {str(e)}"
            )
    
    eko_available = True
    print("✅ Eko集成模块导入成功")
except ImportError as e:
    print(f"⚠️ Eko集成模块导入失败: {e}")
    eko_available = False
    
    async def handle_eko_recommendation(request: ApiEkoRecommendationRequest) -> ApiEkoRecommendationResponse:
        return ApiEkoRecommendationResponse(
            success=False,
            error="Eko integration not available"
        )

# 尝试导入对话式推荐模块
conversational_available = False
_init_conv = None
_start_conv = None
_handle_resp = None
_get_status = None
_cancel_conv = None
_get_stats = None

try:
    from app.eko_integration.conversational_api import (
        initialize_conversational_api as _init_conv,
        start_conversation_endpoint as _start_conv,
        handle_response_endpoint as _handle_resp,
        get_status_endpoint as _get_status,
        cancel_conversation_endpoint as _cancel_conv,
        get_stats_endpoint as _get_stats
    )
    
    conversational_available = True
    print("✅ 对话式推荐模块导入成功")
except ImportError as e:
    print(f"⚠️ 对话式推荐模块导入失败: {e}")
    conversational_available = False
    # 确保所有变量都是None
    _init_conv = None
    _start_conv = None
    _handle_resp = None
    _get_status = None
    _cancel_conv = None
    _get_stats = None

# 根据导入结果创建包装函数
if (conversational_available and _init_conv is not None and 
    _start_conv is not None and _handle_resp is not None and
    _get_status is not None and _cancel_conv is not None and _get_stats is not None):
    # 创建包装函数来避免类型冲突
    def initialize_conversational_api(config):
        return _init_conv(config)  # type: ignore
        
    async def start_conversation_endpoint(request):
        return await _start_conv(request)  # type: ignore
        
    async def handle_response_endpoint(request):
        return await _handle_resp(request)  # type: ignore
        
    async def get_status_endpoint(session_id):
        return await _get_status(session_id)  # type: ignore
        
    async def cancel_conversation_endpoint(session_id):
        return await _cancel_conv(session_id)  # type: ignore
        
    async def get_stats_endpoint():
        return await _get_stats()  # type: ignore
else:
    # 如果导入失败，创建默认的占位函数
    def initialize_conversational_api(config):
        pass
        
    async def start_conversation_endpoint(request):
        return {"error": "Conversational API not available"}
        
    async def handle_response_endpoint(request):
        return {"error": "Conversational API not available"}
        
    async def get_status_endpoint(session_id):
        return {"error": "Conversational API not available"}
        
    async def cancel_conversation_endpoint(session_id):
        return {"error": "Conversational API not available"}
        
    async def get_stats_endpoint():
        return {"error": "Conversational API not available"}

# 在Vercel环境下创建最小化配置类
if not config_available:
    class MinimalConfig:
        class AMapSettings:
            def __init__(self, api_key):
                self.api_key = api_key

        def __init__(self):
            amap_key = os.getenv("AMAP_API_KEY", "")
            if amap_key:
                self.amap = self.AMapSettings(amap_key)
            else:
                self.amap = None

    if os.getenv("AMAP_API_KEY"):
        config = MinimalConfig()
        config_available = True
        print("✅ 创建最小化配置（仅高德地图）")

# 在Vercel环境下创建最小化推荐器
if not CafeRecommender and os.getenv("AMAP_API_KEY"):
    try:
        import hashlib
        from datetime import datetime

        class MinimalCafeRecommender:
            """最小化推荐器，专为Vercel环境设计"""

            def __init__(self):
                self.api_key = os.getenv("AMAP_API_KEY")
                self.base_url = "https://restapi.amap.com/v3"

            async def execute(self, locations, keywords="咖啡馆", place_type="", user_requirements=""):
                """执行推荐"""
                try:
                    # 简化的推荐逻辑
                    result_html = await self._generate_recommendations(
                        locations, keywords, user_requirements
                    )

                    # 生成HTML文件
                    html_filename = f"place_recommendation_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}.html"
                    html_path = f"workspace/js_src/{html_filename}"

                    # 确保目录存在
                    os.makedirs("workspace/js_src", exist_ok=True)

                    # 写入HTML文件
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(result_html)

                    return Result(f"生成的推荐页面：{html_path}\nHTML页面: {html_filename}")

                except Exception as e:
                    return Result(f"推荐失败: {str(e)}")

            async def _generate_recommendations(self, locations, keywords, user_requirements):
                """生成推荐HTML"""
                html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EkoMeet 推荐结果</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .locations {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
        .result {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 EkoMeet 推荐结果</h1>
        <p>基于Eko AI的智能会面地点推荐</p>
    </div>

    <div class="locations">
        <h3>📍 您的位置信息</h3>
        <p><strong>位置:</strong> {', '.join(locations)}</p>
        <p><strong>需求:</strong> {keywords}</p>
        {f'<p><strong>特殊要求:</strong> {user_requirements}</p>' if user_requirements else ''}
    </div>

    <div class="result">
        <h3>💡 推荐建议</h3>
        <p>由于在简化模式下运行，推荐功能已简化。建议您:</p>
        <ul>
            <li>选择位置中心点附近的{keywords}</li>
            <li>考虑交通便利性和停车条件</li>
            <li>选择环境舒适、适合交流的场所</li>
        </ul>
    </div>

    <div class="result">
        <h3>⚠️ 注意事项</h3>
        <p>当前运行在简化模式下。如需完整功能，请在本地环境运行或配置完整的环境变量。</p>
    </div>
</body>
</html>
                """
                return html_content

        CafeRecommender = MinimalCafeRecommender
        print("✅ 创建最小化推荐器")

    except Exception as e:
        print(f"❌ 创建最小化推荐器失败: {e}")
        CafeRecommender = None

# 环境变量配置
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
AMAP_SECURITY_JS_CODE = os.getenv("AMAP_SECURITY_JS_CODE", "")

# 创建FastAPI应用
app = FastAPI(
    title="EkoMeet",
    description="EkoMeet会面点推荐服务 - 基于Eko AI的智能推荐系统",
    version="1.0.0"
)

# 设置请求编码
@app.middleware("http")
async def add_charset_middleware(request, call_next):
    """确保请求使用UTF-8编码"""
    if request.method in ["POST", "PUT", "PATCH"] and "application/json" in request.headers.get("content-type", ""):
        body = await request.body()
        if body:
            try:
                decoded_body = body.decode('utf-8')
                request._body = decoded_body.encode('utf-8')
            except UnicodeDecodeError:
                try:
                    decoded_body = body.decode('gbk')
                    request._body = decoded_body.encode('utf-8')
                except UnicodeDecodeError:
                    pass
    
    response = await call_next(request)
    
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    
    return response

# 初始化对话式推荐API
if conversational_available and config_available:
    try:
        amap_api_key = os.getenv("AMAP_API_KEY", "")
        if not amap_api_key and config and hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
            amap_api_key = config.amap.api_key
        
        print(f"🔑 使用的AMAP API密钥长度: {len(amap_api_key)}")
        
        conversational_config = {
            "amap_api_key": amap_api_key,
            "llm_config": getattr(config, 'llm', None) if config else None,
            "session_timeout_minutes": 30
        }
        initialize_conversational_api(conversational_config)
        print("✅ 对话式推荐API初始化成功")
    except Exception as e:
        print(f"⚠️ 对话式推荐API初始化失败: {e}")
        conversational_available = False

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
try:
    workspace_dir = "workspace"
    js_src_dir = os.path.join(workspace_dir, "js_src")
    os.makedirs(js_src_dir, exist_ok=True)

    if os.path.exists(workspace_dir):
        app.mount("/workspace", StaticFiles(directory=workspace_dir), name="workspace")
        print("✅ 挂载 /workspace 静态文件")

    if os.path.exists("public"):
        app.mount("/public", StaticFiles(directory="public"), name="public")
        print("✅ 挂载 /public 静态文件")

    if os.path.exists("docs"):
        app.mount("/docs-static", StaticFiles(directory="docs"), name="docs-static")
        print("✅ 挂载 /docs 静态文件")
except Exception as e:
    print(f"⚠️ 静态文件挂载失败: {e}")

@app.get("/")
async def read_root():
    """根路径 - 返回主页"""
    try:
        html_file = "public/index.html"
        if os.path.exists(html_file):
            return FileResponse(html_file)

        return {
            "message": "🎯 EkoMeet API - 基于Eko AI的智能会面地点推荐服务",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "timestamp": time.time()
        }
    except Exception as e:
        return {"message": "EkoMeet API", "error": str(e)}

@app.get("/health")
async def health_check():
    """健康检查和配置状态"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "config": {
            "amap_configured": bool(AMAP_API_KEY or (config and hasattr(config, 'amap') and config.amap)),
            "full_features": config_available,
            "minimal_mode": not config_available and bool(AMAP_API_KEY),
            "eko_available": eko_available
        }
    }

@app.get("/config")
async def get_config():
    """获取当前配置状态（不暴露敏感信息）"""
    amap_key = ""
    if config and hasattr(config, 'amap') and config.amap and hasattr(config.amap, 'api_key'):
        amap_key = config.amap.api_key
    else:
        amap_key = AMAP_API_KEY

    return {
        "amap_api_key_configured": bool(amap_key),
        "amap_api_key_length": len(amap_key) if amap_key else 0,
        "config_loaded": bool(config),
        "full_features_available": bool(config)
    }

@app.get("/api/config/siliconflow-key")
async def get_siliconflow_key():
    """为前端Eko助手提供硅基流动API密钥"""
    try:
        siliconflow_key = os.getenv("SILICONFLOW_API_KEY", "")
        
        if not siliconflow_key:
            if config:
                siliconflow_key = getattr(config, 'siliconflow_api_key', '')
        
        if not siliconflow_key:
            return JSONResponse(
                status_code=404,
                content={"error": "SiliconFlow API key not configured"}
            )
        
        return {
            "apiKey": siliconflow_key,
            "baseUrl": os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
            "model": os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-72B-Instruct"),
            "configured": True
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve SiliconFlow API key: {str(e)}"}
        )

@app.post("/api/find_ekomeet")
async def find_ekomeet(request: EkoMeetRequest):
    """EkoMeet 会面点推荐 API"""
    start_time = time.time()
    
    try:
        if not request.locations or len(request.locations) < 2:
            raise HTTPException(status_code=400, detail="至少需要2个地点")
        
        if len(request.locations) > 10:
            raise HTTPException(status_code=400, detail="最多支持10个地点")
        
        if not request.keywords or not request.keywords.strip():
            request.keywords = "咖啡馆"
        
        logger.info(f"开始处理推荐请求: {len(request.locations)}个地点, 关键词: {request.keywords}")
        
        if CafeRecommender is None:
            raise HTTPException(status_code=503, detail="推荐服务不可用")
            
        recommender = CafeRecommender()
        
        execute_params = {
            "locations": request.locations,
            "keywords": request.keywords,
            "user_requirements": request.user_requirements or "",
            "place_type": request.place_type or ""
        }
        
        if hasattr(request, 'theme') and request.theme:
            execute_params["theme"] = request.theme
        
        result = await recommender.execute(**execute_params)
        
        if hasattr(result, 'output') and result.output:
            if ("HTML页面:" in result.output or "生成的推荐页面" in result.output or 
                "已为您找到" in result.output):
                
                lines = result.output.split('\n')
                html_filename = None
                for line in lines:
                    if "HTML页面:" in line:
                        html_filename = line.split("HTML页面:")[-1].strip()
                        break
                    elif "生成的推荐页面:" in line:
                        html_filename = line.split("生成的推荐页面:")[-1].strip()
                        break
                
                if html_filename:
                    processing_time = time.time() - start_time
                    logger.info(f"推荐完成，耗时: {processing_time:.2f}秒")
                    
                    return {
                        "success": True,
                        "html_url": f"/workspace/js_src/{html_filename}",
                        "processing_time": processing_time,
                        "locations_count": len(request.locations),
                        "keywords": request.keywords,
                        "status": "completed",
                        "details": "推荐生成成功",
                        "recommendation_type": "standard"
                    }
        
        return {
            "success": False,
            "error": "推荐结果处理失败",
            "details": result.output if hasattr(result, 'output') else str(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"推荐处理异常: {str(e)}, 耗时: {processing_time:.2f}秒")
        
        return {
            "success": False,
            "error": str(e),
            "processing_time": processing_time,
            "status": "error"
        }

@app.post("/api/eko/recommend")
async def eko_smart_recommend(request: EkoSmartRequest):
    """Eko智能推荐API"""
    try:
        if not eko_available:
            return {
                "success": False,
                "error": "Eko智能推荐功能不可用",
                "fallback_suggestion": "请使用标准推荐功能 /api/find_ekomeet"
            }
        
        eko_request = ApiEkoRecommendationRequest(
            query=request.query,
            locations=request.locations
        )
        
        result = await handle_eko_recommendation(eko_request)
        
        if result.success:
            return {
                "success": True,
                "result": result.result,
                "processing_time": 0.5,
                "recommendation_type": "eko_intelligent"
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "fallback_available": True
            }
            
    except Exception as e:
        logger.error(f"Eko智能推荐错误: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "fallback_available": True
        }

# 对话式推荐端点
if conversational_available:
    @app.post("/api/conversation/start")
    async def start_conversation(request: ConversationStartRequest):
        """开始对话式推荐"""
        return await start_conversation_endpoint(request)

    @app.post("/api/conversation/respond")
    async def handle_conversation_response(request: ConversationResponseRequest):
        """处理对话响应"""
        return await handle_response_endpoint(request)

    @app.get("/api/conversation/status/{session_id}")
    async def get_conversation_status(session_id: str):
        """获取对话状态"""
        return await get_status_endpoint(session_id)

    @app.delete("/api/conversation/{session_id}")
    async def cancel_conversation(session_id: str):
        """取消对话"""
        return await cancel_conversation_endpoint(session_id)

    @app.get("/api/conversation/stats")
    async def get_conversation_stats():
        """获取对话统计"""
        return await get_stats_endpoint()