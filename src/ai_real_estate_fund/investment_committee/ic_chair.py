from __future__ import annotations
from .base import CommitteeAgent, average_prior

class InvestmentCommitteeChairAgent(CommitteeAgent):
    name = "Investment Committee Chair Agent"
    role = "Synthesizes the committee debate into final governance-ready concerns and actions."
    weight = 0.90
    category = "committee"

    def analyze(self, prop, metrics, data, prior_findings):
        score = average_prior(prior_findings, 50)
        top = sorted(prior_findings, key=lambda f: f.score, reverse=True)[:3]
        bottom = sorted(prior_findings, key=lambda f: f.score)[:3]
        positives = [f"{f.agent_name}: {f.positives[0]}" for f in top if f.positives]
        concerns = [f"{f.agent_name}: {f.concerns[0]}" for f in bottom if f.concerns]
        return self.finding(score=score, confidence=0.82, thesis=f"Committee chair synthesizes {len(prior_findings)} prior findings into a governance score of {score:.1f}.", positives=positives, concerns=concerns, evidence=[self.metric("prior_finding_count", len(prior_findings)), self.metric("weighted_committee_score", round(score,1))], actions=["Assign owners and deadlines to every unresolved diligence item before final IC approval."])
