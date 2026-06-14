from __future__ import annotations

import csv
import json
from dataclasses import fields
from pathlib import Path
from statistics import median
from typing import Any, Iterable

from .models import (
    DataQualityReport,
    DiligenceDataBundle,
    EvidenceItem,
    MarketSnapshot,
    PropertyInput,
    RentComp,
    SaleComp,
)


DEFAULT_MARKETS: dict[str, MarketSnapshot] = {
    "San Antonio, TX": MarketSnapshot(
        market="San Antonio, TX",
        rent_growth_yoy=0.035,
        appreciation_yoy=0.032,
        vacancy_rate=0.061,
        property_tax_rate=0.018,
        insurance_rate=0.0065,
        unemployment_rate=0.039,
        population_growth_yoy=0.014,
        job_growth_yoy=0.018,
        landlord_friendliness_score=7.0,
        liquidity_score=7.0,
        crime_risk_score=4.5,
        school_score=6.0,
        source="example_fixture",
        as_of="2025-01-01",
    ),
    "Raleigh, NC": MarketSnapshot(
        market="Raleigh, NC",
        rent_growth_yoy=0.042,
        appreciation_yoy=0.041,
        vacancy_rate=0.055,
        property_tax_rate=0.010,
        insurance_rate=0.0055,
        unemployment_rate=0.034,
        population_growth_yoy=0.020,
        job_growth_yoy=0.025,
        landlord_friendliness_score=6.5,
        liquidity_score=8.0,
        crime_risk_score=3.5,
        school_score=7.0,
        source="example_fixture",
        as_of="2025-01-01",
    ),
    "Cleveland, OH": MarketSnapshot(
        market="Cleveland, OH",
        rent_growth_yoy=0.023,
        appreciation_yoy=0.021,
        vacancy_rate=0.075,
        property_tax_rate=0.021,
        insurance_rate=0.0060,
        unemployment_rate=0.045,
        population_growth_yoy=-0.002,
        job_growth_yoy=0.006,
        landlord_friendliness_score=5.5,
        liquidity_score=5.5,
        crime_risk_score=5.5,
        school_score=5.0,
        source="example_fixture",
        as_of="2025-01-01",
    ),
}


DEFAULT_RENT_COMPS: dict[str, list[RentComp]] = {
    "San Antonio, TX": [
        RentComp("1420 W Ashby Pl", 3600, bedrooms=4, bathrooms=2, square_feet=1850, unit_count=2, distance_miles=0.4, source="example_fixture", confidence=0.74),
        RentComp("811 W Magnolia Ave", 3850, bedrooms=4, bathrooms=2, square_feet=1920, unit_count=2, distance_miles=0.7, source="example_fixture", confidence=0.72),
        RentComp("2506 N Flores St", 3450, bedrooms=4, bathrooms=2, square_feet=1760, unit_count=2, distance_miles=0.9, source="example_fixture", confidence=0.70),
    ],
    "Raleigh, NC": [
        RentComp("608 Oakwood Ave", 5650, bedrooms=8, bathrooms=4, square_feet=3300, unit_count=4, distance_miles=0.8, source="example_fixture", confidence=0.70),
        RentComp("311 New Bern Pl", 5400, bedrooms=8, bathrooms=4, square_feet=3150, unit_count=4, distance_miles=1.1, source="example_fixture", confidence=0.68),
        RentComp("923 Mordecai Dr", 5900, bedrooms=8, bathrooms=4, square_feet=3400, unit_count=4, distance_miles=1.3, source="example_fixture", confidence=0.68),
    ],
    "Cleveland, OH": [
        RentComp("4412 Bridge Ave", 1425, bedrooms=3, bathrooms=1, square_feet=1280, unit_count=1, distance_miles=0.5, source="example_fixture", confidence=0.71),
        RentComp("3329 W 48th St", 1500, bedrooms=3, bathrooms=1, square_feet=1360, unit_count=1, distance_miles=0.9, source="example_fixture", confidence=0.68),
        RentComp("5207 Franklin Blvd", 1325, bedrooms=3, bathrooms=1, square_feet=1190, unit_count=1, distance_miles=1.4, source="example_fixture", confidence=0.66),
    ],
}


DEFAULT_SALE_COMPS: dict[str, list[SaleComp]] = {
    "San Antonio, TX": [
        SaleComp("1518 W French Pl", 315000, square_feet=1820, unit_count=2, bedrooms=4, bathrooms=2, distance_miles=0.5, sale_date="2024-10-14", source="example_fixture", confidence=0.72),
        SaleComp("1002 W Craig Pl", 342000, square_feet=1950, unit_count=2, bedrooms=4, bathrooms=2, distance_miles=0.8, sale_date="2024-11-03", source="example_fixture", confidence=0.73),
        SaleComp("231 E Mistletoe Ave", 298000, square_feet=1750, unit_count=2, bedrooms=4, bathrooms=2, distance_miles=1.0, sale_date="2024-09-22", source="example_fixture", confidence=0.69),
    ],
    "Raleigh, NC": [
        SaleComp("721 N East St", 655000, square_feet=3220, unit_count=4, bedrooms=8, bathrooms=4, distance_miles=1.0, sale_date="2024-08-30", source="example_fixture", confidence=0.69),
        SaleComp("1009 Wake Forest Rd", 710000, square_feet=3440, unit_count=4, bedrooms=8, bathrooms=4, distance_miles=1.4, sale_date="2024-12-01", source="example_fixture", confidence=0.71),
        SaleComp("504 Polk St", 680000, square_feet=3300, unit_count=4, bedrooms=8, bathrooms=4, distance_miles=1.6, sale_date="2024-10-19", source="example_fixture", confidence=0.68),
    ],
    "Cleveland, OH": [
        SaleComp("3902 Walton Ave", 155000, square_feet=1340, unit_count=1, bedrooms=3, bathrooms=1, distance_miles=0.7, sale_date="2024-09-11", source="example_fixture", confidence=0.70),
        SaleComp("4809 Herman Ave", 149000, square_feet=1280, unit_count=1, bedrooms=3, bathrooms=1, distance_miles=1.0, sale_date="2024-10-24", source="example_fixture", confidence=0.67),
        SaleComp("5211 Bridge Ave", 171000, square_feet=1405, unit_count=1, bedrooms=3, bathrooms=1, distance_miles=1.2, sale_date="2024-11-15", source="example_fixture", confidence=0.68),
    ],
}


def _float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def _int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def _allowed_fields(cls: type) -> set[str]:
    return {field.name for field in fields(cls)}


def _filter_row(row: dict[str, Any], cls: type) -> dict[str, Any]:
    allowed = _allowed_fields(cls)
    return {key: value for key, value in row.items() if key in allowed and value not in (None, "")}


def load_market_snapshots(path: Path) -> dict[str, MarketSnapshot]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    snapshots: dict[str, MarketSnapshot] = {}
    for item in payload:
        snapshot = MarketSnapshot(**_filter_row(item, MarketSnapshot))
        snapshots[snapshot.market] = snapshot
    return snapshots


def load_rent_comps(path: Path) -> dict[str, list[RentComp]]:
    comps: dict[str, list[RentComp]] = {}
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            market = row.get("market", "")
            comp = RentComp(
                address=row.get("address", "Unknown"),
                monthly_rent=_float(row.get("monthly_rent")),
                bedrooms=_int(row.get("bedrooms")),
                bathrooms=_float(row.get("bathrooms")),
                square_feet=_float(row.get("square_feet")),
                unit_count=max(1, _int(row.get("unit_count"), 1)),
                distance_miles=_float(row.get("distance_miles")),
                source=row.get("source", "csv"),
                confidence=_float(row.get("confidence"), 0.70),
                notes=row.get("notes", ""),
            )
            comps.setdefault(market, []).append(comp)
    return comps


def load_sale_comps(path: Path) -> dict[str, list[SaleComp]]:
    comps: dict[str, list[SaleComp]] = {}
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            market = row.get("market", "")
            comp = SaleComp(
                address=row.get("address", "Unknown"),
                sale_price=_float(row.get("sale_price")),
                square_feet=_float(row.get("square_feet")),
                unit_count=max(1, _int(row.get("unit_count"), 1)),
                bedrooms=_int(row.get("bedrooms")),
                bathrooms=_float(row.get("bathrooms")),
                distance_miles=_float(row.get("distance_miles")),
                sale_date=row.get("sale_date", ""),
                source=row.get("source", "csv"),
                confidence=_float(row.get("confidence"), 0.70),
                notes=row.get("notes", ""),
            )
            comps.setdefault(market, []).append(comp)
    return comps


class LocalDataProvider:
    """Fixture-backed provider used by default.

    It intentionally avoids scraping or paid APIs. Replace this provider with a
    MLS, property-record, rent-comp, or internal warehouse adapter when you have
    permission and credentials for those data sources.
    """

    def __init__(
        self,
        market_snapshots: dict[str, MarketSnapshot] | None = None,
        rent_comps: dict[str, list[RentComp]] | None = None,
        sale_comps: dict[str, list[SaleComp]] | None = None,
    ) -> None:
        self.market_snapshots = market_snapshots or DEFAULT_MARKETS
        self.rent_comps = rent_comps or DEFAULT_RENT_COMPS
        self.sale_comps = sale_comps or DEFAULT_SALE_COMPS

    @classmethod
    def from_paths(
        cls,
        market_path: Path | None = None,
        rent_comp_path: Path | None = None,
        sale_comp_path: Path | None = None,
    ) -> "LocalDataProvider":
        market_snapshots = load_market_snapshots(market_path) if market_path else None
        rent_comps = load_rent_comps(rent_comp_path) if rent_comp_path else None
        sale_comps = load_sale_comps(sale_comp_path) if sale_comp_path else None
        return cls(market_snapshots=market_snapshots, rent_comps=rent_comps, sale_comps=sale_comps)

    def build_bundle(self, prop: PropertyInput) -> DiligenceDataBundle:
        market_snapshot = self.market_snapshots.get(prop.market) or self._fallback_market(prop)
        rent_comps = list(self.rent_comps.get(prop.market, []))
        sale_comps = list(self.sale_comps.get(prop.market, []))
        evidence = self._evidence_from_property(prop, market_snapshot, rent_comps, sale_comps)
        data_quality = score_data_quality(prop, rent_comps, sale_comps, market_snapshot, evidence)
        return DiligenceDataBundle(
            market_snapshot=market_snapshot,
            rent_comps=rent_comps,
            sale_comps=sale_comps,
            evidence=evidence,
            data_quality=data_quality,
        )

    def _fallback_market(self, prop: PropertyInput) -> MarketSnapshot:
        return MarketSnapshot(
            market=prop.market,
            rent_growth_yoy=prop.expected_annual_rent_growth,
            appreciation_yoy=prop.expected_annual_appreciation,
            vacancy_rate=prop.vacancy_rate,
            landlord_friendliness_score=prop.landlord_friendliness_score,
            liquidity_score=prop.liquidity_score,
            crime_risk_score=prop.crime_risk_score,
            school_score=prop.school_score,
            source="property_assumption_fallback",
        )

    def _evidence_from_property(
        self,
        prop: PropertyInput,
        market: MarketSnapshot,
        rent_comps: list[RentComp],
        sale_comps: list[SaleComp],
    ) -> list[EvidenceItem]:
        evidence = [
            EvidenceItem("property_input", "purchase_price", prop.purchase_price, "assumption", 0.85),
            EvidenceItem("property_input", "monthly_rent", prop.monthly_rent, "assumption", 0.75),
            EvidenceItem("property_input", "rehab_budget", prop.rehab_budget, "assumption", 0.65),
            EvidenceItem("market_snapshot", "market_vacancy_rate", market.vacancy_rate, "market", 0.65, market.as_of),
            EvidenceItem("market_snapshot", "rent_growth_yoy", market.rent_growth_yoy, "market", 0.65, market.as_of),
        ]
        if rent_comps:
            evidence.append(
                EvidenceItem(
                    "rent_comps",
                    "median_monthly_rent",
                    median(comp.monthly_rent for comp in rent_comps),
                    "comp",
                    _avg_confidence(comp.confidence for comp in rent_comps),
                )
            )
        if sale_comps:
            evidence.append(
                EvidenceItem(
                    "sale_comps",
                    "median_sale_price",
                    median(comp.sale_price for comp in sale_comps),
                    "comp",
                    _avg_confidence(comp.confidence for comp in sale_comps),
                )
            )
        return evidence


def _avg_confidence(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def score_data_quality(
    prop: PropertyInput,
    rent_comps: list[RentComp],
    sale_comps: list[SaleComp],
    market: MarketSnapshot,
    evidence: list[EvidenceItem],
) -> DataQualityReport:
    missing: list[str] = []
    warnings: list[str] = []
    critical_checks = {
        "estimated_arv": prop.estimated_arv > 0,
        "rent_comps": len(rent_comps) >= 3,
        "sale_comps": len(sale_comps) >= 3,
        "square_feet": prop.square_feet > 0,
        "unit_count": prop.unit_count > 0,
        "taxes": prop.property_taxes_annual > 0,
        "insurance": prop.insurance_annual > 0,
        "rehab_budget": prop.rehab_budget >= 0,
        "market_snapshot": bool(market.source),
    }
    for name, passed in critical_checks.items():
        if not passed:
            missing.append(name)
    if rent_comps and prop.monthly_rent > 1.15 * median(comp.monthly_rent for comp in rent_comps):
        warnings.append("Subject rent is more than 15% above fixture rent comps; verify lease-up assumptions.")
    if sale_comps and prop.purchase_price > 1.10 * median(comp.sale_price for comp in sale_comps):
        warnings.append("Purchase price is more than 10% above fixture sale comps; confirm condition adjustments.")
    if market.source == "property_assumption_fallback":
        warnings.append("No market fixture found; market data fell back to user-entered assumptions.")
    completeness = 100 * (sum(critical_checks.values()) / len(critical_checks))
    confidence_values = [item.confidence for item in evidence]
    confidence = 100 * (_avg_confidence(confidence_values) if confidence_values else 0.0)
    return DataQualityReport(
        completeness_score=round(completeness, 1),
        confidence_score=round(confidence, 1),
        missing_fields=missing,
        warnings=warnings,
        evidence_count=len(evidence),
    )
