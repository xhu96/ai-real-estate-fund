from __future__ import annotations
from ai_real_estate_fund.tools.watchlist import Watchlist
from ..models.schemas import WatchlistPayload

class WatchlistService:
    def __init__(self) -> None:
        self.watchlist = Watchlist()

    def add(self, body: WatchlistPayload) -> list[dict[str, object]]:
        self.watchlist.add(body.name, body.market, body.reason, float(body.target_price))
        return self.watchlist.to_dict()
