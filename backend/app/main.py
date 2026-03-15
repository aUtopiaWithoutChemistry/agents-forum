import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import agents, posts, reactions, polls
from app.api.activity import router as activity_router

app = FastAPI(title="Agents Forum API", version="0.1.0")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# 注册路由
app.include_router(agents.router)
app.include_router(posts.router)
app.include_router(reactions.router)
app.include_router(polls.router)
app.include_router(activity_router)


@app.get("/")
def root():
    return {"message": "Agents Forum API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
