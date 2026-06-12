from __future__ import annotations
from .schemas import ListingRecord, MarketRecord, PropertyRecord

class FixtureDataClient:
    """A local stand-in for MLS, rent-comps, property-record, and macro feeds."""

    def search_listings(self, market: str) -> list[ListingRecord]:
        return [
            ListingRecord("fx-1", "100 Example Ave", market, 325000, 3350, 4, 2, 1850),
            ListingRecord("fx-2", "200 Demo St", market, 415000, 4300, 6, 3, 2400),
        ]

    def market_record(self, market: str) -> MarketRecord:
        return MarketRecord(market, 0.012, 0.018, 0.061, 0.035)

    def property_record(self, address: str) -> PropertyRecord:
        return PropertyRecord("fixture-parcel", address, 1978, 280000, 5900)
