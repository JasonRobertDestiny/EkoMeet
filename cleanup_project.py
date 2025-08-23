#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EkoMeet项目文件清理脚本
自动清理临时文件、日志文件和过期的推荐结果页面
"""

import os
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path

def cleanup_logs(logs_dir="logs", keep_days=7):
    """清理过期的日志文件"""
    print(f"🧹 清理 {keep_days} 天前的日志文件...")
    
    if not os.path.exists(logs_dir):
        print(f"   日志目录 {logs_dir} 不存在，跳过")
        return
    
    cutoff_time = datetime.now() - timedelta(days=keep_days)
    cleaned_count = 0
    
    for log_file in glob.glob(os.path.join(logs_dir, "*.log")):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_time:
                os.remove(log_file)
                cleaned_count += 1
                print(f"   删除: {os.path.basename(log_file)}")
        except (OSError, PermissionError) as e:
            print(f"   跳过 {os.path.basename(log_file)}: {e}")
    
    print(f"   清理完成，删除了 {cleaned_count} 个日志文件")

def cleanup_workspace(workspace_dir="workspace", keep_files=5):
    """清理工作空间中的推荐结果文件，只保留最新的几个"""
    print(f"🧹 清理工作空间，保留最新的 {keep_files} 个文件...")
    
    js_src_dir = os.path.join(workspace_dir, "js_src")
    if not os.path.exists(js_src_dir):
        print(f"   工作空间目录 {js_src_dir} 不存在，跳过")
        return
    
    # 获取所有推荐结果文件
    html_files = glob.glob(os.path.join(js_src_dir, "place_recommendation_*.html"))
    
    if len(html_files) <= keep_files:
        print(f"   当前只有 {len(html_files)} 个文件，无需清理")
        return
    
    # 按修改时间排序
    html_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # 删除多余的文件
    files_to_delete = html_files[keep_files:]
    cleaned_count = 0
    
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            cleaned_count += 1
            print(f"   删除: {os.path.basename(file_path)}")
        except OSError as e:
            print(f"   跳过 {os.path.basename(file_path)}: {e}")
    
    print(f"   清理完成，删除了 {cleaned_count} 个推荐结果文件")

def cleanup_cache_files():
    """清理Python缓存文件"""
    print("🧹 清理Python缓存文件...")
    
    cleaned_count = 0
    for root, dirs, files in os.walk("."):
        # 删除 __pycache__ 目录
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                cleaned_count += 1
                print(f"   删除: {pycache_path}")
            except OSError as e:
                print(f"   跳过 {pycache_path}: {e}")
        
        # 删除 .pyc 文件
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    print(f"   删除: {file_path}")
                except OSError as e:
                    print(f"   跳过 {file_path}: {e}")
    
    print(f"   清理完成，删除了 {cleaned_count} 个缓存文件")

def show_project_structure():
    """显示项目核心文件结构"""
    print("\n📁 EkoMeet 项目核心文件结构:")
    
    core_structure = {
        "🎯 核心服务": [
            "web_server.py",
            "api/index.py"
        ],
        "🧠 AI推荐引擎": [
            "app/tool/meetspot_recommender.py",
            "app/eko_integration/"
        ],
        "⚙️ 配置与工具": [
            "app/config.py",
            "app/logger.py",
            "app/schema.py",
            "app/tool/base.py",
            "app/tool/tool_collection.py"
        ],
        "🌐 前端界面": [
            "public/index.html",
            "public/eko-assistant.js"
        ],
        "📝 配置文件": [
            ".env",
            "config/config.toml",
            "requirements.txt"
        ]
    }
    
    for category, files in core_structure.items():
        print(f"\n{category}:")
        for file_path in files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    file_count = len([f for f in os.listdir(file_path) if f.endswith(('.py', '.js'))])
                    print(f"   ✅ {file_path} ({file_count} 个文件)")
                else:
                    size = os.path.getsize(file_path) / 1024
                    print(f"   ✅ {file_path} ({size:.1f}KB)")
            else:
                print(f"   ❌ {file_path} (缺失)")

def main():
    """主函数"""
    print("🚀 EkoMeet 项目清理开始...")
    print("=" * 50)
    
    # 切换到项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # 执行清理任务
        cleanup_cache_files()
        cleanup_logs()
        cleanup_workspace()
        
        print("\n" + "=" * 50)
        print("✅ 项目清理完成！")
        
        # 显示项目结构
        show_project_structure()
        
    except Exception as e:
        print(f"❌ 清理过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
