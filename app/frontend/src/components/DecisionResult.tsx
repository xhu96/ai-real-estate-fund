import { CommitteePanel } from './CommitteeGraph';
import { ScenarioStress, ScoreRadar } from './Charts';
import { Findings } from './Findings';
import { AnalystCommentary, CommitteeMemo, PolicyGates, VerdictHeader } from './InstitutionalResults';
import { MemoViewer } from './MemoViewer';
import { RiskRegister } from './RiskRegister';
import { ScenarioTable } from './ScenarioTable';
import type { CommitteeDecision, InstitutionalDecision } from '../types';

/** Tagged decision so each branch carries the right shape — no `any`, no widening casts. */
export type DecisionResultProps =
  | { kind: 'institutional'; decision: InstitutionalDecision }
  | { kind: 'screening'; decision: CommitteeDecision };

/**
 * The full result composition shared by AnalyzeProperty (fresh run) and RunDetail (deep link).
 * Institutional and screening render different panel sets; the wrapping <div> matches the
 * original AnalyzeProperty layout so styling is unchanged.
 */
export function DecisionResult(props: DecisionResultProps) {
  if (props.kind === 'institutional') {
    const decision = props.decision;
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s5)' }}>
        <VerdictHeader decision={decision} />
        <CommitteePanel findings={decision.findings} overallScore={decision.overall_score} recommendation={String(decision.recommendation)} />
        <div className="grid-2">
          <ScoreRadar scorecards={(decision.scorecards ?? []) as Array<{ name?: string; score?: number }>} />
          <ScenarioStress scenarios={decision.scenarios} />
        </div>
        <div className="grid-2b">
          <PolicyGates decision={decision} />
          <RiskRegister risks={decision.risk_register} />
        </div>
        <AnalystCommentary decision={decision} />
        <CommitteeMemo decision={decision} />
        <Findings findings={decision.findings} />
      </div>
    );
  }

  const decision = props.decision;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--s5)' }}>
      <MemoViewer decision={decision} />
      <CommitteePanel findings={decision.findings} overallScore={decision.overall_score} recommendation={String(decision.recommendation)} />
      <div className="grid-2b">
        <ScenarioTable scenarios={decision.scenarios} />
        <RiskRegister risks={decision.risk_register} />
      </div>
      <Findings findings={decision.findings} />
    </div>
  );
}
