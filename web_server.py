#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EkoMeet Local Development Server
=================================

This is the main entry point for local development.
It imports and runs the FastAPI application from api/index.py.

For production deployment on Railway, this file serves as the main entry point.
"""

import sys
import os
import locale
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 设置UTF-8编码
if sys.platform.startswith('win'):
    # Windows系统设置
    import codecs
    import io
    from typing import cast
    
    # 安全地处理stdout和stderr的编码设置
    # 使用类型转换来避免类型检查器错误
    try:
        if hasattr(sys.stdout, 'buffer'):
            stdout_buffer = getattr(sys.stdout, 'buffer', None)
            if stdout_buffer is not None:
                sys.stdout = codecs.getwriter('utf-8')(stdout_buffer)
        
        if hasattr(sys.stderr, 'buffer'):
            stderr_buffer = getattr(sys.stderr, 'buffer', None)
            if stderr_buffer is not None:
                sys.stderr = codecs.getwriter('utf-8')(stderr_buffer)
    except (AttributeError, io.UnsupportedOperation, TypeError):
        # 如果上述方法失败，使用环境变量方式
        pass
    
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Main entry point for development and production server"""
    try:
        # Import the FastAPI app from api/index.py
        from api.index import app
        import uvicorn
        
        # Get port from environment variable (Railway sets PORT automatically)
        port = int(os.environ.get("PORT", 8000))
        
        # Detect if running in production (Railway sets RAILWAY_ENVIRONMENT)
        is_production = os.environ.get("RAILWAY_ENVIRONMENT") is not None
        
        if is_production:
            print("🚀 启动 EkoMeet 生产服务器 (Railway)...")
            print(f"📍 服务端口: {port}")
        else:
            print("🚀 启动 EkoMeet 本地开发服务器...")
            print(f"📍 服务地址: http://localhost:{port}")
        
        print("📚 API文档: /docs")
        print("🔧 健康检查: /health")
        print("=" * 50)
        
        # Run the server with production-optimized settings
        uvicorn.run(
            "api.index:app", 
            host="0.0.0.0", 
            port=port,
            reload=not is_production,  # Disable reload in production
            log_level="info",
            access_log=True,
            # 确保UTF-8编码
            loop="asyncio"
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()