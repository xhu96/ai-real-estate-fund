import type { CommitteeDecision } from '../types';
import { VerdictBadge } from './Badge';

export function MemoViewer({ decision }: { decision: CommitteeDecision }) {
  const metrics = decision.metrics ?? {};
  const pct = (v: unknown) => (v == null ? 'n/a' : `${(Number(v) * 100).toFixed(1)}%`);
  return (
    <section className="verdict" aria-label="Committee verdict">
      <VerdictBadge value={String(decision.recommendation)} large />
      <div className="figure">
        <span className="label">Overall score</span>
        <span className="value">{decision.overall_score.toFixed(1)}<span className="unit">/100</span></span>
      </div>
      <div className="figure">
        <span className="label">Cap rate</span>
        <span className="value">{pct(metrics.cap_rate)}</span>
      </div>
      <div className="figure">
        <span className="label">DSCR</span>
        <span className="value">{metrics.dscr == null ? 'n/a' : `${Number(metrics.dscr).toFixed(2)}x`}</span>
      </div>
      <div className="figure">
        <span className="label">Suggested allocation</span>
        <span className="value">{(decision.suggested_allocation_pct * 100).toFixed(1)}<span className="unit">%</span></span>
      </div>
    </section>
  );
}
