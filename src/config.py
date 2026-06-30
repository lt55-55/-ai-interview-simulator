"""Configuration and API client setup."""

import os
from pathlib import Path

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


def get_client() -> Anthropic:
    """Get Anthropic client, preferring Streamlit secrets then .env."""
    api_key = None
    base_url = None

    # Try Streamlit secrets first (for deployed environment)
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
        base_url = st.secrets.get("ANTHROPIC_BASE_URL")
    except Exception:
        pass

    # Fall back to environment variables
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")
    if not base_url:
        base_url = os.getenv("ANTHROPIC_BASE_URL")

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Set it in .env file or Streamlit secrets."
        )

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    return Anthropic(**kwargs)


# Supported interview roles and their descriptions
ROLES = {
    "AI 应用开发工程师": "利用大模型 API 构建 AI 产品和功能，包括 Agent、RAG、Prompt Engineering",
    "AI 产品经理": "设计 AI 产品功能，定义 Prompt 策略，评估模型效果，协调技术团队",
    "Python 后端开发": "使用 Python 构建后端服务，API 设计，数据库管理，系统架构",
    "前端开发工程师": "使用 React/Vue 构建用户界面，前端性能优化，工程化实践",
    "数据分析师": "使用 Python/SQL 进行数据分析、可视化和业务洞察",
    "网络安全工程师": "安全测试、漏洞分析、安全架构设计、应急响应",
}

# Difficulty levels
DIFFICULTY_LEVELS = ["初级 (实习/应届)", "中级 (1-3年)", "高级 (3-5年)"]
