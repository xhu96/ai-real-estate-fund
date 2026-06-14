from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .committee import run_institutional_committee
from .institutional.memo import render_institutional_memo
from .production import ProductionReadinessChecker, ProductionSettings, SQLiteAuditLog, render_readiness_markdown, run_health_checks
from .production.release import build_release_manifest
from .data_loader import load_properties, load_property, write_json
from .data_sources import LocalDataProvider
from .investment_committee import run_property_committee
from .report import pct, render_diligence_markdown
from .sensitivity import render_sensitivity_markdown, run_sensitivity


def _add_common_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", type=Path, help="Output path for the generated memo or table")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON instead of markdown")



def compare_command(args: argparse.Namespace) -> None:
    rows = []
    for input_path in args.inputs:
        for prop in load_properties(input_path):
            memo = run_property_committee(prop)
            rows.append(
                {
                    "name": prop.name,
                    "market": prop.market,
                    "recommendation": memo.recommendation.value,
                    "score": memo.overall_score,
                    "allocation_pct": memo.suggested_allocation_pct,
                    "purchase_price": prop.purchase_price,
                    "max_offer_price": round(memo.max_offer_price, 2),
                    "margin_of_safety": round(memo.margin_of_safety, 4),
                    "cap_rate": round(memo.metrics.cap_rate, 4),
                    "cash_on_cash": round(memo.metrics.cash_on_cash_return, 4),
                    "dscr": round(memo.metrics.dscr, 3),
                    "irr": None if memo.metrics.irr is None else round(memo.metrics.irr, 4),
                }
            )
    rows.sort(key=lambda row: row["score"], reverse=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [])
            if rows:
                writer.writeheader()
                writer.writerows(rows)
        print(f"Wrote {args.out}")
        return
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    print("| Rank | Name | Market | Decision | Score | Cap Rate | CoC | DSCR | IRR |")
    print("|---:|---|---|---:|---:|---:|---:|---:|---:|")
    for idx, row in enumerate(rows, 1):
        irr_value = "n/a" if row["irr"] is None else pct(row["irr"])
        print(
            f"| {idx} | {row['name']} | {row['market']} | {row['recommendation']} | "
            f"{row['score']:.1f} | {pct(row['cap_rate'])} | {pct(row['cash_on_cash'])} | "
            f"{row['dscr']:.2f}x | {irr_value} |"
        )


def sensitivity_command(args: argparse.Namespace) -> None:
    prop = load_property(args.input)
    if args.json:
        payload = [{"case": name, **memo.to_dict()} for name, memo in run_sensitivity(prop)]
        text = json.dumps(payload, indent=2) + "\n"
    else:
        text = render_sensitivity_markdown(prop)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)


def _data_provider_from_args(args: argparse.Namespace) -> LocalDataProvider:
    return LocalDataProvider.from_paths(
        market_path=args.market_data,
        rent_comp_path=args.rent_comps,
        sale_comp_path=args.sale_comps,
    )



def committee_v3_command(args: argparse.Namespace) -> None:
    prop = load_property(args.input)
    decision = run_property_committee(
        prop,
        data_provider=_data_provider_from_args(args),
    )
    text = json.dumps(decision.to_dict(), indent=2) + "\n" if args.json else render_diligence_markdown(decision)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)


def institutional_command(args: argparse.Namespace) -> None:
    prop = load_property(args.input)
    llm_client = None
    if getattr(args, "llm", False):
        from .llm import live_client_from_env

        llm_client = live_client_from_env(model=args.llm_model, provider=args.llm_provider)
    decision = run_institutional_committee(
        prop,
        llm_client=llm_client,
        data_provider=_data_provider_from_args(args),
    )
    text = json.dumps(decision.to_dict(), indent=2) + "\n" if args.json else render_institutional_memo(decision)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)


def readiness_command(args: argparse.Namespace) -> None:
    settings = ProductionSettings.from_env()
    checker = ProductionReadinessChecker(root=args.root, settings=settings)
    report = checker.run()
    text = json.dumps(report.to_dict(), indent=2) + "\n" if args.json else render_readiness_markdown(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
    if args.strict and not report.passed:
        raise SystemExit(1)


def health_command(args: argparse.Namespace) -> None:
    report = run_health_checks(ProductionSettings.from_env())
    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2) + "\n")
        return
    print(f"Health: {payload['status']}")
    for check in payload["checks"]:
        print(f"- {check['name']}: {check['status']} — {check['message']}")


def audit_verify_command(args: argparse.Namespace) -> None:
    audit = SQLiteAuditLog(args.db)
    ok, errors = audit.verify_chain()
    payload = {"ok": ok, "errors": errors, "db": str(args.db)}
    if args.json:
        print(json.dumps(payload, indent=2) + "\n")
    else:
        print("Audit chain: " + ("OK" if ok else "BROKEN"))
        for error in errors:
            print(f"- {error}")
    if args.strict and not ok:
        raise SystemExit(1)


def release_manifest_command(args: argparse.Namespace) -> None:
    manifest = build_release_manifest(args.root, version=args.version)
    text = manifest.to_json()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)




def init_example_command(args: argparse.Namespace) -> None:
    example = {
        "name": "Example Duplex",
        "address": "123 Example Ave",
        "market": "Example, TX",
        "property_type": "duplex",
        "purchase_price": 285000,
        "estimated_arv": 330000,
        "monthly_rent": 3700,
        "other_monthly_income": 0,
        "vacancy_rate": 0.06,
        "property_taxes_annual": 5200,
        "insurance_annual": 2100,
        "repairs_annual": 2500,
        "utilities_annual": 600,
        "hoa_annual": 0,
        "capex_annual": 2500,
        "management_rate": 0.08,
        "acquisition_costs": 6500,
        "rehab_budget": 18000,
        "loan_amount": 210000,
        "annual_interest_rate": 0.0725,
        "loan_term_years": 30,
        "holding_period_years": 5,
        "expected_annual_rent_growth": 0.03,
        "expected_annual_expense_growth": 0.03,
        "expected_annual_appreciation": 0.035,
        "selling_cost_rate": 0.06,
        "neighborhood_score": 7,
        "school_score": 6,
        "liquidity_score": 7,
        "crime_risk_score": 4,
        "landlord_friendliness_score": 7,
        "unit_count": 2,
        "square_feet": 1850,
        "bedrooms": 4,
        "bathrooms": 2,
        "year_built": 1948,
        "listing_url": "",
        "source": "manual",
        "notes": "Replace these assumptions with your own diligence inputs.",
    }
    write_json(args.out, example)
    print(f"Wrote {args.out}")


def _add_data_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--market-data", type=Path, help="Optional market snapshot JSON file")
    parser.add_argument("--rent-comps", type=Path, help="Optional rent comps CSV file")
    parser.add_argument("--sale-comps", type=Path, help="Optional sale comps CSV file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-real-estate-fund",
        description="Multi-agent real estate investment committee for rental property underwriting.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    committee_parser = subparsers.add_parser("committee", help="Run the screening investment committee (fast, used by backtests)")
    committee_parser.add_argument("input", type=Path, help="Path to a property JSON file")
    _add_common_output_args(committee_parser)
    _add_data_args(committee_parser)
    committee_parser.set_defaults(func=committee_v3_command)

    institutional_parser = subparsers.add_parser("institutional", help="Run the full institutional investment committee")
    institutional_parser.add_argument("input", type=Path, help="Path to a property JSON file")
    institutional_parser.add_argument("--llm", action="store_true", help="Add LLM analyst commentary (requires an NVIDIA, OpenAI, Anthropic, or Gemini API key)")
    institutional_parser.add_argument("--llm-provider", choices=["nvidia", "openai", "anthropic", "gemini"], help="LLM provider (default: LLM_PROVIDER env, else first configured key)")
    institutional_parser.add_argument("--llm-model", help="Model id, e.g. z-ai/glm-5.1, gpt-4o-mini, claude-sonnet-4-6, gemini-2.5-flash (default: LLM_MODEL env or provider default)")
    _add_common_output_args(institutional_parser)
    _add_data_args(institutional_parser)
    institutional_parser.set_defaults(func=institutional_command)

    compare_parser = subparsers.add_parser("compare", help="Rank multiple property JSON/CSV files")
    compare_parser.add_argument("inputs", type=Path, nargs="+", help="Property JSON or CSV files")
    compare_parser.add_argument("--out", type=Path, help="Output CSV path")
    compare_parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown table")
    compare_parser.set_defaults(func=compare_command)

    sensitivity_parser = subparsers.add_parser("sensitivity", help="Run a standard downside/upside sensitivity table")
    sensitivity_parser.add_argument("input", type=Path, help="Path to a property JSON file")
    _add_common_output_args(sensitivity_parser)
    sensitivity_parser.set_defaults(func=sensitivity_command)

    init_parser = subparsers.add_parser("init-example", help="Write an editable example input file")
    init_parser.add_argument("--out", type=Path, default=Path("property.json"))
    init_parser.set_defaults(func=init_example_command)

    readiness_parser = subparsers.add_parser("readiness", help="Run production-readiness checks for deployment gates")
    readiness_parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to inspect")
    readiness_parser.add_argument("--out", type=Path, help="Optional markdown/JSON output path")
    readiness_parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    readiness_parser.add_argument("--strict", action="store_true", help="Exit non-zero when readiness checks fail")
    readiness_parser.set_defaults(func=readiness_command)

    health_parser = subparsers.add_parser("health", help="Run runtime health checks without starting the API")
    health_parser.add_argument("--json", action="store_true")
    health_parser.set_defaults(func=health_command)

    audit_parser = subparsers.add_parser("audit-verify", help="Verify the append-only audit hash chain")
    audit_parser.add_argument("--db", type=Path, default=Path("data/audit.db"))
    audit_parser.add_argument("--json", action="store_true")
    audit_parser.add_argument("--strict", action="store_true")
    audit_parser.set_defaults(func=audit_verify_command)

    release_parser = subparsers.add_parser("release-manifest", help="Generate a deterministic file-hash manifest for releases")
    release_parser.add_argument("--root", type=Path, default=Path("."))
    release_parser.add_argument("--version", default="0.6.0")
    release_parser.add_argument("--out", type=Path, help="Output JSON path")
    release_parser.set_defaults(func=release_manifest_command)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
