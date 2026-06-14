from __future__ import annotations
from dataclasses import asdict, dataclass, field

@dataclass(slots=True)
class WatchlistItem:
    name: str
    market: str
    reason: str
    target_price: float

@dataclass(slots=True)
class Watchlist:
    items: list[WatchlistItem] = field(default_factory=list)

    def add(self, name: str, market: str, reason: str, target_price: float) -> None:
        self.items.append(WatchlistItem(name, market, reason, target_price))

    def to_dict(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self.items]
