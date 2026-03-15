from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models.models import User, Agent


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    # 完全公开的路径（不需要任何认证）
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
    ]

    # 认证相关的路径
    AUTH_PATHS = [
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/verify",
    ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # CORS preflight must pass through
        if method == "OPTIONS":
            response = await call_next(request)
            return response

        # 完全公开的路径
        if path in self.PUBLIC_PATHS or path.startswith("/docs"):
            response = await call_next(request)
            return response

        # 认证相关的路径
        if path in self.AUTH_PATHS:
            response = await call_next(request)
            return response

        # 读取操作公开
        if method == "GET":
            response = await call_next(request)
            return response

        # 写入操作需要认证
        api_key = request.headers.get("X-API-Key")
        agent_id = request.headers.get("X-Agent-ID")

        # 认证用户或 Agent
        if api_key:
            # 人类用户认证
            db = next(get_db())
            try:
                user = db.query(User).filter(User.api_key == api_key).first()
                if user and user.is_active:
                    request.state.user = user
                    request.state.auth_type = "user"
                else:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid API key"}
                    )
            finally:
                db.close()
        elif agent_id:
            # Agent 认证
            db = next(get_db())
            try:
                agent = db.query(Agent).filter(Agent.id == agent_id).first()
                if agent:
                    request.state.agent = agent
                    request.state.auth_type = "agent"
                else:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid Agent ID"}
                    )
            finally:
                db.close()
        else:
            # 需要认证但没有提供
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required: provide X-API-Key or X-Agent-ID"}
            )

        response = await call_next(request)
        return response
