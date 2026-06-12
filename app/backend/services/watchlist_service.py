from __future__ import annotations
from ai_real_estate_fund.tools.watchlist import Watchlist

class WatchlistService:
    def __init__(self) -> None:
        self.watchlist = Watchlist()

    def add(self, payload: dict) -> list[dict[str, object]]:
        self.watchlist.add(payload["name"], payload["market"], payload.get("reason", "manual"), float(payload.get("target_price", 0)))
        return self.watchlist.to_dict()
