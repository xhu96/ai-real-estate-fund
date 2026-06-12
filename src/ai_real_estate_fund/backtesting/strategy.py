from __future__ import annotations
from .models import BacktestConfig
from ..models import CommitteeDecision

class ScoreThresholdStrategy:
    def __init__(self, config: BacktestConfig) -> None:
        self.config = config

    def should_select(self, decision: CommitteeDecision) -> bool:
        return decision.overall_score >= self.config.min_score and decision.recommendation.value != "PASS"
