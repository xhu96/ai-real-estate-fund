import type { InstitutionalDecision } from '../types';
import { VerdictBadge } from './Badge';

const pct = (v: unknown) => (v == null ? null : `${(Number(v) * 100).toFixed(1)}%`);
const mult = (v: unknown) => (v == null ? null : `${Number(v).toFixed(2)}x`);

type FigSpec = { keys: string[]; label: string; fmt: (v: unknown) => string | null; gold?: boolean };
const FIG_SPECS: FigSpec[] = [
  { keys: ['cap_rate', 'going_in_cap_rate'], label: 'Going-in cap', fmt: pct, gold: true },
  { keys: ['stabilized_yield', 'yield_on_cost'], label: 'Yield on cost', fmt: pct },
  { keys: ['dscr'], label: 'DSCR', fmt: mult },
  { keys: ['cash_on_cash', 'cash_on_cash_return'], label: 'Cash-on-cash', fmt: pct },
  { keys: ['irr', 'levered_irr', 'five_year_irr'], label: '5-yr IRR', fmt: pct, gold: true },
  { keys: ['equity_multiple'], label: 'Equity multiple', fmt: mult },
  { keys: ['ltv'], label: 'LTV', fmt: pct },
];

export function VerdictHeader({ decision }: { decision: InstitutionalDecision }) {
  const metrics = decision.metrics ?? {};
  const p = decision.property;
  const meta = [p.market, (p as unknown as { property_type?: string }).property_type].filter(Boolean).join(' · ');
  const hardStops = decision.hard_stops?.length ?? 0;

  const figs: Array<{ label: string; value: string; gold?: boolean }> = [];
  for (const spec of FIG_SPECS) {
    if (figs.length >= 5) break;
    const key = spec.keys.find((k) => metrics[k] != null);
    if (!key) continue;
    const value = spec.fmt(metrics[key]);
    if (value) figs.push({ label: spec.label, value, gold: spec.gold });
  }

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
          {figs.map((f) => (
            <div className="fig" key={f.label}><div className="l">{f.label}</div><div className={`v num${f.gold ? ' gold' : ''}`}>{f.value}</div></div>
          ))}
          <div className="fig"><div className="l">Hard stops</div><div className="v num" style={hardStops ? { color: 'var(--danger)' } : undefined}>{hardStops}</div></div>
        </div>
      </div>
    </section>
  );
}

export function PolicyGates({ decision }: { decision: InstitutionalDecision }) {
  const gates = decision.policy_results ?? [];
  if (gates.length === 0) return null;
  const passed = gates.filter((g) => g.passed).length;
  const severe = (s?: string) => { const v = String(s ?? '').toLowerCase(); return ['hard', 'critical', 'error', 'block', 'stop'].some((k) => v.includes(k)); };

  return (
    <section className="panel reveal">
      <div className="panel-h"><div className="t"><h2>Policy gates</h2></div><span className="hint">{passed} of {gates.length} pass</span></div>
      <div className="panel-b flush gates">
        {gates.map((g, i) => {
          const cls = g.passed ? 'g-pass' : severe(g.limit?.severity) ? 'g-fail' : 'g-warn';
          const glyph = g.passed ? '✓' : severe(g.limit?.severity) ? '✕' : '!';
          return (
            <div className="gate" key={i}>
              <span className={`g-ic ${cls}`} aria-hidden="true">{glyph}</span>
              <div className="g-text">
                <div className="g-name">{g.limit?.name ?? 'Gate'}</div>
                <div className="g-msg">{g.message}{!g.passed && g.remediation ? ` — ${g.remediation}` : ''}</div>
              </div>
              <span className="g-val">{Number.isFinite(Number(g.value)) ? Number(g.value).toFixed(2) : String(g.value)}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

const PERSONA: Record<string, { initials: string; tint: string; color: string }> = {
  bull: { initials: 'BL', tint: 'var(--positive-tint)', color: 'var(--positive)' },
  bear: { initials: 'BR', tint: 'var(--danger-tint)', color: 'var(--danger)' },
  risk: { initials: 'RO', tint: 'var(--neg-tint)', color: 'var(--neg)' },
  chair: { initials: 'IC', tint: 'var(--accent-tint)', color: 'var(--accent)' },
};
function personaOf(name: string) {
  const n = name.toLowerCase();
  if (n.includes('bull')) return PERSONA.bull;
  if (n.includes('bear')) return PERSONA.bear;
  if (n.includes('risk')) return PERSONA.risk;
  if (n.includes('chair')) return PERSONA.chair;
  return { initials: name.slice(0, 2).toUpperCase(), tint: 'var(--surface-3)', color: 'var(--body)' };
}

export function AnalystCommentary({ decision }: { decision: InstitutionalDecision }) {
  const review = decision.llm_review;
  if (!review || review.opinions.length === 0) return null;
  return (
    <section className="panel reveal">
      <div className="panel-h">
        <div className="t"><h2>Analyst debate</h2><span className="hint">{review.model} · scores are never model-generated</span></div>
      </div>
      <div className="debate">
        {review.opinions.map((o) => {
          const p = personaOf(o.analyst);
          return (
            <div className="persona" key={o.analyst}>
              <div className="ph"><span className="av" style={{ background: p.tint, color: p.color }}>{p.initials}</span><span className="pn">{o.analyst}</span></div>
              <div className="pt">{o.thesis}</div>
              {o.key_points.length > 0 && <ul>{o.key_points.slice(0, 3).map((k, i) => <li key={i}>{k}</li>)}</ul>}
              {o.questions.length > 0 && <div className="pq">? {o.questions[0]}</div>}
            </div>
          );
        })}
      </div>
      {review.errors.length > 0 && <div className="error-note" style={{ margin: '0 var(--s5) var(--s5)' }}>{review.errors.join('; ')}</div>}
    </section>
  );
}

export function CommitteeMemo({ decision }: { decision: InstitutionalDecision }) {
  if (!decision.thesis && !decision.bear_case && (decision.next_steps?.length ?? 0) === 0) return null;
  return (
    <section className="panel reveal">
      <div className="panel-h"><div className="t"><h2>IC memo</h2></div><span className="hint">committee synthesis</span></div>
      <div className="panel-b">
        <div className="two-col">
          <div>
            {decision.thesis && <><div className="fieldset-label" style={{ marginTop: 0 }}>Thesis</div><p className="prose">{decision.thesis}</p></>}
            {decision.bear_case && <><div className="fieldset-label">Bear case</div><p className="prose">{decision.bear_case}</p></>}
          </div>
          {(decision.next_steps?.length ?? 0) > 0 && (
            <div>
              <div className="fieldset-label" style={{ marginTop: 0 }}>Next steps</div>
              <ol className="prose" style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 'var(--s2)' }}>
                {decision.next_steps.map((s, i) => <li key={i}>{s}</li>)}
              </ol>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export function Scorecards({ decision }: { decision: InstitutionalDecision }) {
  const cards = (decision.scorecards ?? []) as Array<{ name?: string; category?: string; score?: number }>;
  if (cards.length === 0) return null;
  return (
    <section className="panel">
      <div className="panel-h"><div className="t"><h2>Category scorecards</h2></div><span className="hint">weighted workstream scores</span></div>
      <div className="panel-b">
        {cards.map((card, i) => (
          <div key={i} className="scorecard-row">
            <span className="name">{String(card.name ?? card.category)}</span>
            <span className="scorebar">
              <span className="track"><span className="fill" style={{ width: `${Math.min(Number(card.score ?? 0), 100)}%` }} /></span>
              <span className="val">{Number(card.score ?? 0).toFixed(1)}</span>
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
