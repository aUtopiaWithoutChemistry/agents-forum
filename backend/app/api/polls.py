from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import Post, PollOption, PollVote, Agent, ActivityLog
from app.models.schemas import PollVoteCreate

router = APIRouter(prefix="/api/polls", tags=["polls"])


@router.get("/{post_id}/options")
def get_poll_options(post_id: int, db: Session = Depends(get_db)):
    """获取投票选项和结果"""
    post = db.query(Post).filter(Post.id == post_id, Post.is_poll == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="Poll not found")

    options = db.query(PollOption).filter(PollOption.post_id == post_id).all()

    result = []
    for opt in options:
        vote_count = db.query(PollVote).filter(PollVote.poll_option_id == opt.id).count()
        voted_agents = [
            v.agent_id for v in
            db.query(PollVote).filter(PollVote.poll_option_id == opt.id).all()
        ]
        result.append({
            "id": opt.id,
            "option_text": opt.option_text,
            "vote_count": vote_count,
            "voted_agents": voted_agents
        })

    return result


@router.post("/{post_id}/vote")
def vote_poll(post_id: int, vote: PollVoteCreate, db: Session = Depends(get_db)):
    """投票"""
    # 验证投票帖存在
    post = db.query(Post).filter(Post.id == post_id, Post.is_poll == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="Poll not found")

    # 验证 agent 存在
    agent = db.query(Agent).filter(Agent.id == vote.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 验证选项存在
    valid_options = db.query(PollOption).filter(PollOption.post_id == post_id).all()
    valid_option_ids = [o.id for o in valid_options]

    voted_options = []
    for opt_id in vote.option_ids:
        if opt_id not in valid_option_ids:
            raise HTTPException(status_code=400, detail=f"Option {opt_id} not found")

        # 检查是否已投票
        existing = db.query(PollVote).filter(
            PollVote.poll_option_id == opt_id,
            PollVote.agent_id == vote.agent_id
        ).first()

        if existing:
            continue  # 已投票，跳过

        new_vote = PollVote(poll_option_id=opt_id, agent_id=vote.agent_id)
        db.add(new_vote)
        voted_options.append(opt_id)

    # 记录 activity
    if voted_options:
        activity = ActivityLog(
            agent_id=vote.agent_id,
            action="vote",
            target_type="post",
            target_id=post_id,
            extra_data=json.dumps({"option_ids": voted_options})
        )
        db.add(activity)

    db.commit()
    return {"message": "Vote recorded", "option_ids": voted_options}
