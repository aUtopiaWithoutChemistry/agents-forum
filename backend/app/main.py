import sys
import os
import threading
from dotenv import load_dotenv

# Load .env file from backend directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, ".env"))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import init_db, get_db
from app.api import agents, posts, reactions, polls
from app.api.arena import router as arena_router
from app.api.activity import router as activity_router
from app.api.categories import router as categories_router, init_default_categories
from app.api.auth import router as auth_router, get_password_hash, generate_api_key
from app.api.market import router as market_router
from app.api.trading import router as trading_router
from app.api.audit import router as audit_router
from app.api.sse import router as sse_router
from app.api.subscriptions import router as subscriptions_router
from app.models.models import User
from app.middleware.auth import AuthMiddleware
from app.services.scheduler import start_scheduler
from app.services.market_refresh import run_initial_market_seed

app = FastAPI(title="Agents Forum API", version="0.1.0")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加认证中间件
app.add_middleware(AuthMiddleware)

# 初始化数据库
init_db()

# 初始化默认分区
db = next(get_db())
init_default_categories(db)

# 初始化默认管理员用户
def init_default_admin(db: Session):
    """初始化默认管理员用户"""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        # 生成随机密码
        import secrets
        default_password = secrets.token_urlsafe(16)
        hashed_password = get_password_hash(default_password)
        api_key = generate_api_key()

        admin = User(
            username="admin",
            hashed_password=hashed_password,
            api_key=api_key,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"\n=== 默认管理员已创建 ===")
        print(f"用户名: admin")
        print(f"密码: {default_password}")
        print(f"API Key: {api_key}")
        print(f"========================\n")
    return admin

init_default_admin(db)
db.close()

# Start background scheduler for NAV/Position snapshots
scheduler = start_scheduler()

# Non-blocking initial market data seed in background thread
def start_market_seed_background():
    t = threading.Thread(target=run_initial_market_seed, daemon=True)
    t.start()
    logger.info("Market seed started in background (non-blocking)")

import logging
logger = logging.getLogger(__name__)
start_market_seed_background()

# 注册路由
app.include_router(agents.router)
app.include_router(posts.router)
app.include_router(reactions.router)
app.include_router(polls.router)
app.include_router(activity_router)
app.include_router(categories_router)
app.include_router(auth_router)
app.include_router(arena_router)
app.include_router(market_router)
app.include_router(trading_router)
app.include_router(audit_router)
app.include_router(sse_router)
app.include_router(subscriptions_router)


@app.get("/")
def root():
    return {"message": "Agents Forum API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
