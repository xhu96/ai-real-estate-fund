from __future__ import annotations
from ai_real_estate_fund.report import render_diligence_memo
from ai_real_estate_fund.models import CommitteeDecision

class ReportService:
    def render_markdown(self, decision: CommitteeDecision) -> str:
        return render_diligence_memo(decision)
