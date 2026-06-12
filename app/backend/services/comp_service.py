from __future__ import annotations
from ai_real_estate_fund.data_sources import LocalDataProvider

class CompService:
    def comps_for_market(self, market: str) -> dict[str, list[dict]]:
        provider = LocalDataProvider()
        return {
            "rent_comps": [c.to_dict() for c in provider.rent_comps.get(market, [])],
            "sale_comps": [c.to_dict() for c in provider.sale_comps.get(market, [])],
        }
