"""LLM analyst personas.

Four analysts debate the committee's deterministic output, the way named
analysts debate a deal in ai-hedge-fund: each persona receives the same
structured fact pack (metrics, scorecards, policy gates, scenarios, top and
bottom workstreams) and returns a structured opinion. The deterministic scores
are never altered by the models — the LLM layer argues about the deal, it does
not grade it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..llm import LLMClient, _strip_code_fences, safe_json_loads
from .models import InstitutionalDecision

_SYSTEM_TEMPLATE = (
    "You are {persona}, a member of an institutional real-estate investment committee. "
    "You are given the deterministic underwriting facts for one residential deal. "
    "Ground every claim in the provided numbers; never invent figures. "
    "This is educational decision-support, not financial advice. "
    "Respond with a single JSON object: "
    '{{"thesis": str, "key_points": [str, ...], "questions": [str, ...]}} '
    "with 3-5 key_points and 2-3 questions."
)

PERSONAS: tuple[tuple[str, str], ...] = (
    (
        "Bull Advocate",
        "Make the strongest honest case FOR doing this deal. Lean on the strongest workstreams and scenario upside, and state what must stay true for the bull case to hold.",
    ),
    (
        "Bear Advocate",
        "Make the strongest honest case AGAINST doing this deal. Lean on the weakest workstreams, policy gates, and downside scenarios, and identify the most fragile assumption.",
    ),
    (
        "Risk Officer",
        "Identify the top risks, how they interact, which are mitigable versus structural, and any conditions that should be deal-breakers regardless of price.",
    ),
    (
        "IC Chair",
        "Weigh the bull case, bear case, and risk view. State whether you would ratify, renegotiate, or reject at the current basis, and list the open questions the sponsor must answer before a vote.",
    ),
)


@dataclass(slots=True)
class AnalystOpinion:
    analyst: str
    thesis: str
    key_points: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analyst": self.analyst,
            "thesis": self.thesis,
            "key_points": self.key_points,
            "questions": self.questions,
        }


@dataclass(slots=True)
class LlmReview:
    model: str
    generated_at: str
    opinions: list[AnalystOpinion] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "generated_at": self.generated_at,
            "opinions": [opinion.to_dict() for opinion in self.opinions],
            "errors": self.errors,
        }


def build_fact_pack(decision: InstitutionalDecision) -> dict[str, Any]:
    """Compact, deterministic summary of the decision for analyst prompts."""
    metrics = decision.metrics
    ranked = sorted(decision.findings, key=lambda f: f.score)
    return {
        "property": {
            "name": decision.property.name,
            "market": decision.property.market,
            "type": decision.property.property_type,
            "unit_count": decision.property.unit_count,
            "purchase_price": decision.property.purchase_price,
        },
        "metrics": {
            "noi": round(metrics.noi),
            "cap_rate": round(metrics.cap_rate, 4),
            "cash_on_cash": round(metrics.cash_on_cash_return, 4),
            "dscr": round(metrics.dscr, 2),
            "loan_to_cost": round(metrics.loan_to_cost, 3),
            "break_even_occupancy": round(metrics.break_even_occupancy, 3),
        },
        "committee": {
            "overall_score": decision.overall_score,
            "recommendation": decision.recommendation.value,
            "hard_stops": [result.limit.name for result in decision.hard_stops()],
            "failed_gates": [r.limit.name for r in decision.policy_results if not r.passed],
        },
        "scorecards": {card.category: card.weighted_score() for card in decision.scorecards},
        "weakest_workstreams": [
            {"name": f.agent_name, "score": f.score, "concern": (f.concerns[0] if f.concerns else "")}
            for f in ranked[:5]
        ],
        "strongest_workstreams": [
            {"name": f.agent_name, "score": f.score, "positive": (f.positives[0] if f.positives else "")}
            for f in ranked[-5:]
        ],
        "scenarios": [
            {"name": s.name, "score": s.score, "dscr": round(s.dscr, 2), "cash_flow": round(s.cash_flow_before_tax)}
            for s in decision.scenarios
        ],
        "top_risks": [item.name for item in decision.risk_register[:5]],
    }


def run_llm_analysts(decision: InstitutionalDecision, client: LLMClient) -> LlmReview:
    """Run every analyst persona over the decision fact pack.

    Personas run sequentially so later analysts (IC Chair) can react to earlier
    opinions, mirroring how a committee debate builds on prior speakers.
    """
    import json as _json

    fact_pack = build_fact_pack(decision)
    review = LlmReview(model=client.model, generated_at=datetime.now(timezone.utc).isoformat())
    transcript: list[dict[str, Any]] = []
    for persona, charge in PERSONAS:
        prompt_payload: dict[str, Any] = {"charge": charge, "facts": fact_pack}
        if transcript:
            prompt_payload["prior_opinions"] = transcript
        try:
            raw = client.complete(
                _SYSTEM_TEMPLATE.format(persona=persona),
                _json.dumps(prompt_payload, indent=1),
            )
        except RuntimeError as exc:
            review.errors.append(f"{persona}: {exc}")
            continue
        parsed = safe_json_loads(raw)
        opinion = AnalystOpinion(
            analyst=persona,
            thesis=str(parsed.get("thesis") or _strip_code_fences(raw)[:400] or "No response."),
            key_points=[str(point) for point in parsed.get("key_points", [])][:6],
            questions=[str(question) for question in parsed.get("questions", [])][:4],
        )
        review.opinions.append(opinion)
        transcript.append({"analyst": persona, "thesis": opinion.thesis, "key_points": opinion.key_points})
    return review
