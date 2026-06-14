import type { CommitteeDecision } from '../types';
import { VerdictBadge } from './Badge';

const pct = (v: unknown) => (v == null ? 'n/a' : `${(Number(v) * 100).toFixed(1)}%`);

export function MemoViewer({ decision }: { decision: CommitteeDecision }) {
  const metrics = decision.metrics ?? {};
  const p = decision.property;
  const meta = [p.market].filter(Boolean).join(' · ');
  return (
    <section className={`verdict reveal ${String(decision.recommendation).toLowerCase()}`} aria-label="Committee verdict">
      <div className="score-disc">
        <div className="cap">Overall</div>
        <div className="big">{decision.overall_score.toFixed(1)}</div>
        <div className="cap">of 100</div>
      </div>
      <div>
        <div className="head">
          <VerdictBadge value={String(decision.recommendation)} large />
          <h1>{p.name}</h1>
          {meta && <span className="addr">· {meta}</span>}
        </div>
        <div className="figs">
          <div className="fig"><div className="l">Going-in cap</div><div className="v num gold">{pct(metrics.cap_rate)}</div></div>
          <div className="fig"><div className="l">DSCR</div><div className="v num">{metrics.dscr == null ? 'n/a' : `${Number(metrics.dscr).toFixed(2)}x`}</div></div>
          <div className="fig"><div className="l">Suggested allocation</div><div className="v num">{(decision.suggested_allocation_pct * 100).toFixed(1)}<small>%</small></div></div>
        </div>
      </div>
    </section>
  );
}
