#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from sqlalchemy import delete

import sys


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, init_db  # noqa: E402
from app.models.models import (  # noqa: E402
    Agent,
    ArenaAgentProfile,
    ArenaAgentScore,
    ArenaAsset,
    ArenaEventMention,
    ArenaMarketEvent,
    ArenaPortfolioPosition,
    ArenaPriceBar,
    ArenaSeason,
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def upsert_agent(db, payload: dict) -> None:
    agent = db.query(Agent).filter(Agent.id == payload["id"]).first()
    if not agent:
        agent = Agent(
            id=payload["id"],
            name=payload["name"],
            description=payload.get("description"),
            avatar_url=payload.get("avatar_url"),
        )
        db.add(agent)
        return
    agent.name = payload["name"]
    agent.description = payload.get("description")
    agent.avatar_url = payload.get("avatar_url")


def import_season(db, payload: dict, replace_existing: bool) -> str:
    season_data = payload["season"]
    season_id = season_data["id"]

    existing = db.query(ArenaSeason).filter(ArenaSeason.id == season_id).first()
    if existing and replace_existing:
        db.execute(delete(ArenaEventMention).where(ArenaEventMention.event_id.in_(
            db.query(ArenaMarketEvent.id).filter(ArenaMarketEvent.season_id == season_id)
        )))
        db.execute(delete(ArenaMarketEvent).where(ArenaMarketEvent.season_id == season_id))
        db.execute(delete(ArenaPriceBar).where(ArenaPriceBar.season_id == season_id))
        db.execute(delete(ArenaPortfolioPosition).where(ArenaPortfolioPosition.season_id == season_id))
        db.execute(delete(ArenaAgentScore).where(ArenaAgentScore.season_id == season_id))
        db.execute(delete(ArenaAgentProfile).where(ArenaAgentProfile.season_id == season_id))
        db.execute(delete(ArenaSeason).where(ArenaSeason.id == season_id))
        db.flush()
        existing = None

    if existing and not replace_existing:
        raise ValueError(f"Season {season_id} already exists. Pass --replace to overwrite it.")

    season = ArenaSeason(**season_data)
    db.add(season)

    for asset_data in payload.get("assets", []):
        asset = db.query(ArenaAsset).filter(ArenaAsset.symbol == asset_data["symbol"]).first()
        if not asset:
            db.add(ArenaAsset(**asset_data))
        else:
            asset.name = asset_data["name"]
            asset.sector = asset_data.get("sector")
            asset.market = asset_data.get("market", asset.market)

    for agent_data in payload.get("agents", []):
        upsert_agent(db, agent_data)

    for profile in payload.get("profiles", []):
        db.add(ArenaAgentProfile(**profile))

    for bar in payload.get("price_bars", []):
        db.add(ArenaPriceBar(**bar))

    for event_data in payload.get("events", []):
        mentions = event_data.pop("mentions", [])
        event = ArenaMarketEvent(**event_data)
        db.add(event)
        db.flush()
        for mention in mentions:
            db.add(
                ArenaEventMention(
                    event_id=event.id,
                    symbol=mention["symbol"],
                    relevance=mention.get("relevance", 1.0),
                )
            )

    for position in payload.get("positions", []):
        db.add(ArenaPortfolioPosition(**position))

    for score in payload.get("scores", []):
        db.add(ArenaAgentScore(**score))

    db.commit()
    return season_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Import historical arena data from a JSON season manifest.")
    parser.add_argument("manifest", type=Path, help="Path to season manifest JSON")
    parser.add_argument("--replace", action="store_true", help="Replace an existing season with the same id")
    args = parser.parse_args()

    manifest = args.manifest.resolve()
    if not manifest.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest}")

    payload = load_json(manifest)
    init_db()

    db = SessionLocal()
    try:
        season_id = import_season(db, payload, args.replace)
        print(f"Imported season: {season_id}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
