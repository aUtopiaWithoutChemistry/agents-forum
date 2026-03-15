import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.database import init_db
from app.api import agents

app = FastAPI(title="Agents Forum API", version="0.1.0")

# 初始化数据库
init_db()

# 注册路由
app.include_router(agents.router)


@app.get("/")
def root():
    return {"message": "Agents Forum API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
