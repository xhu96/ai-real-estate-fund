# Methodology Sources

Each diligence workstream in `src/ai_real_estate_fund/institutional/agents/specs.py` carries a `sources` tuple citing the published standard or reference its thresholds and review language are grounded in. Sources are cited **by name only** — no copyrighted text is reproduced anywhere in this repository. Facts, formulas, and published thresholds are not copyrightable; their expression is, and stays out.

## Public, freely accessible standards (primary)

These are the load-bearing citations — anyone can verify them without buying anything.

| Source | What it grounds | Where |
|---|---|---|
| Fannie Mae Multifamily Underwriting Standards (Form 4660) | Debt workstream floors: Tier 2 conventional minimum **1.25x underwritten DSCR / 80% max LTV** | [mfguide.fanniemae.com](https://mfguide.fanniemae.com/node/2721) |
| Fannie Mae Multifamily Selling & Servicing Guide, Part V | Lease audit (§401), Property Condition Assessment (§404), replacement reserve (§406), insurance (Ch. 5) review scopes | [mfguide.fanniemae.com](https://mfguide.fanniemae.com) |
| Freddie Mac Multifamily Seller/Servicer Guide | Debt and reserve practice; replacement reserves at the greater of the engineer's recommendation or **$250/unit/year** | [mf.freddiemac.com](https://mf.freddiemac.com/lenders/guide) |
| HUD Mortgagee Letter 2025-03 (MAP Guide loan sizing) | FHA market-rate multifamily sizing: **1.15x DSCR / 87% LTV-LTC** (relaxed from 1.176x/85%) | [hud.gov](https://www.hud.gov/sites/dfiles/OCHCO/documents/2025-03hsgml.pdf) |
| IRS Publication 527 — Residential Rental Property | Tax treatment assumptions for rental property (incl. 27.5-year residential depreciation) | [irs.gov](https://www.irs.gov/publications/p527) |
| USPAP — Uniform Standards of Professional Appraisal Practice | Appraisal-review workstream scope | [appraisalfoundation.org](https://www.appraisalfoundation.org) |
| ASTM E1527-21 | Phase I Environmental Site Assessment scope | [astm.org](https://www.astm.org/e1527-21.html) |
| U.S. Census Bureau — Housing Vacancies & Homeownership (HVS), Building Permits Survey, population estimates | Vacancy, market-rent context, supply-pipeline and demographic workstreams | [census.gov](https://www.census.gov) |
| U.S. Bureau of Labor Statistics | Job-growth and wage-growth workstreams | [bls.gov](https://www.bls.gov) |
| Federal Reserve SR 11-7 — Supervisory Guidance on Model Risk Management | Data-quality, source-reliability, and model-risk workstreams | [federalreserve.gov](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) |

## Reference texts (further reading)

Standard texts whose published methodology informs committee-level workstreams. Cited by title; obtain through a library or purchase.

Citations are chapter-level so they can be checked against any edition's table of contents.

- Geltner, Miller, Clayton & Eichholtz — *Commercial Real Estate Analysis and Investments*: ch. 6 market analysis; ch. 10 DCF/NPV; ch. 17–19 mortgage analysis and underwriting; ch. 27 real options; ch. 30 leases.
- Linneman & Kirsch — *Real Estate Finance & Investments: Risks and Opportunities*, 5th ed.: ch. 5 property-level pro forma; ch. 7 due diligence; ch. 8 metro growth; ch. 9 cap rates; ch. 14–15 debt decisions; ch. 18 exit strategies; ch. 26 cycles.
- Hartzell & Baum — *Real Estate Investment and Finance* (Wiley, 2020): ch. 3 market fundamentals and rent; ch. 4 asset pricing and portfolio theory; ch. 11–12 fund structures; ch. 15 building the portfolio; ch. 17 performance measurement and attribution.
- Gallinelli — *What Every Real Estate Investor Needs to Know About Cash Flow*: the 37 calculations (Part II), cited per measure (e.g., Calc 7 vacancy/credit loss, Calc 22 operating expense ratio, Calc 23 debt coverage, Calc 26 LTV).
- Appraisal Institute — *The Appraisal of Real Estate*, 15th ed. (valuation standards).

## How sources are used

The `sources` field documents *why a workstream looks at what it looks at* and where its threshold logic comes from. The memo's "Methodology Sources" appendix lists the deduplicated set. When changing a workstream's weight, focus components, or bands, update its citation — uncited threshold changes should be treated as review findings.

Numbers above were verified against the linked documents in June 2026; lender standards change, so re-verify before relying on them.
