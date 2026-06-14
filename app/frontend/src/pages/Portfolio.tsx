import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { PieChart, AlertTriangle } from 'lucide-react';
import { optimizeRuns, recentAnalyses } from '../api/client';
import { VerdictBadge } from '../components/Badge';
import type { AllocationCandidate, CommitteeDecision, PortfolioOptimizeResult } from '../types';

/** Backend defaults for POST /portfolio/optimize-runs — pre-fill the constraint form with these. */
const DEFAULTS = {
  total_equity_budget: 1_500_000,
  max_single_asset_pct: 0.2,
  max_market_pct: 0.35,
  min_score: 60,
  min_risk_score: 55,
  reserve_rate: 0.05,
};

type Constraints = typeof DEFAULTS;

const fmtMoney = (n: number) => `$${Math.round(n).toLocaleString()}`;
const fmtPct = (n: number) => `${(n * 100).toFixed(1)}%`;

/** The first plan note mentioning this candidate, else a generic rejection reason. */
function rejectionReason(c: AllocationCandidate, notes: string[]): string {
  const hit = notes.find((n) => n.toLowerCase().includes(c.name.toLowerCase()));
  if (hit) return hit;
  if (c.score < DEFAULTS.min_score) return `Score ${c.score.toFixed(1)} below threshold`;
  return 'Excluded by constraints or budget';
}

export function Portfolio() {
  const [runs, setRuns] = useState<CommitteeDecision[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [constraints, setConstraints] = useState<Constraints>(DEFAULTS);
  const [result, setResult] = useState<PortfolioOptimizeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoadError(null);
    setRuns(null);
    recentAnalyses().then(setRuns).catch((e: unknown) => {
      setLoadError(e instanceof Error ? e.message : 'Failed to load saved runs.');
    });
  }, []);
  useEffect(() => { load(); }, [load]);

  const setField = (key: keyof Constraints, value: string) =>
    setConstraints((prev) => ({ ...prev, [key]: value === '' ? 0 : Number(value) }));

  async function optimize() {
    if (!runs || runs.length === 0) return;
    setRunError(null);
    setBusy(true);
    setResult(null);
    try {
      const res = await optimizeRuns({
        total_equity_budget: constraints.total_equity_budget,
        run_ids: runs.map((r) => r.run_id),
        max_single_asset_pct: constraints.max_single_asset_pct,
        max_market_pct: constraints.max_market_pct,
        min_score: constraints.min_score,
        min_risk_score: constraints.min_risk_score,
        reserve_rate: constraints.reserve_rate,
      });
      setResult(res);
    } catch (e) {
      setRunError(e instanceof Error ? e.message : 'Optimization failed.');
    } finally {
      setBusy(false);
    }
  }

  const markets = useMemo(() => {
    if (!result) return [];
    const total = result.plan.selected.reduce((s, c) => s + c.required_equity, 0);
    const byMarket = new Map<string, number>();
    for (const c of result.plan.selected) byMarket.set(c.market, (byMarket.get(c.market) ?? 0) + c.required_equity);
    return [...byMarket.entries()]
      .map(([market, equity]) => ({ market, equity, share: total > 0 ? equity / total : 0 }))
      .sort((a, b) => b.equity - a.equity);
  }, [result]);

  return (
    <>
      <div className="page-head">
        <h1>Portfolio</h1>
        <p>Size an allocation plan across your saved runs under concentration limits and score thresholds — selected vs. rejected, equity committed, reserves, and market mix.</p>
      </div>

      <section className="panel reveal">
        <div className="panel-h">
          <div className="t"><h2>Allocation constraints</h2></div>
          {runs && <span className="hint">{runs.length} run{runs.length === 1 ? '' : 's'} considered</span>}
        </div>
        <div className="panel-b">
          {loadError ? (
            <div className="empty">
              <AlertTriangle className="ic" aria-hidden="true" />
              <h3>Couldn't load runs</h3>
              <div className="error-note" role="alert" style={{ marginInline: 'auto', maxWidth: '52ch', textAlign: 'left' }}>{loadError}</div>
              <div className="btn-row"><button className="primary" onClick={load}>Retry</button></div>
            </div>
          ) : runs === null ? (
            <div className="skeleton"><div className="line w40" /><div className="line w70" /><div className="line w40" /></div>
          ) : runs.length === 0 ? (
            <div className="empty">
              <PieChart className="ic" aria-hidden="true" />
              <h3>No runs to optimize yet</h3>
              <p>The optimizer sizes a plan across your saved committee runs. Analyze a deal first, then come back to build an allocation.</p>
              <div className="btn-row"><Link className="btn btn-primary" to="/analyze">Analyze a deal</Link></div>
            </div>
          ) : (
            <>
              <div className="form-grid">
                <label className="field">
                  <span>Total equity budget ($)</span>
                  <input inputMode="decimal" value={String(constraints.total_equity_budget)} onChange={(e) => setField('total_equity_budget', e.target.value)} />
                </label>
                <label className="field">
                  <span>Max single asset (0–1)</span>
                  <input inputMode="decimal" value={String(constraints.max_single_asset_pct)} onChange={(e) => setField('max_single_asset_pct', e.target.value)} />
                </label>
                <label className="field">
                  <span>Max per market (0–1)</span>
                  <input inputMode="decimal" value={String(constraints.max_market_pct)} onChange={(e) => setField('max_market_pct', e.target.value)} />
                </label>
                <label className="field">
                  <span>Min score</span>
                  <input inputMode="decimal" value={String(constraints.min_score)} onChange={(e) => setField('min_score', e.target.value)} />
                </label>
                <label className="field">
                  <span>Min risk score</span>
                  <input inputMode="decimal" value={String(constraints.min_risk_score)} onChange={(e) => setField('min_risk_score', e.target.value)} />
                </label>
                <label className="field">
                  <span>Reserve rate (0–1)</span>
                  <input inputMode="decimal" value={String(constraints.reserve_rate)} onChange={(e) => setField('reserve_rate', e.target.value)} />
                </label>
              </div>
              <div className="btn-row">
                <button className="primary" type="button" disabled={busy} onClick={optimize}>
                  {busy ? 'Optimizing…' : 'Optimize allocation'}
                </button>
                <span className="hint">across all {runs.length} run{runs.length === 1 ? '' : 's'}</span>
              </div>
              {runError && <div className="error-note" role="alert">{runError}</div>}
            </>
          )}
        </div>
      </section>

      {busy && (
        <section className="panel" aria-busy="true">
          <div className="skeleton"><div className="line w40" /><div className="line w70" /><div className="line" /><div className="line w70" /></div>
        </section>
      )}

      {result && !busy && (
        <>
          <div className="kpi-grid">
            <div className="kpi"><div className="l">Deals selected</div><div className="v">{result.plan.selected.length}</div><div className="d">of {result.candidates.length} considered</div></div>
            <div className="kpi"><div className="l">Equity committed</div><div className="v gold">{fmtMoney(result.plan.equity_used)}</div><div className="d">of {fmtMoney(result.budget)} budget</div></div>
            <div className="kpi"><div className="l">Reserves</div><div className="v">{fmtMoney(result.plan.reserves)}</div><div className="d">held back</div></div>
            <div className="kpi"><div className="l">Markets</div><div className="v accent">{markets.length}</div><div className="d">in the selected book</div></div>
          </div>

          <section className="panel reveal">
            <div className="panel-h">
              <div className="t"><h2>Selected</h2></div>
              <span className="hint">{result.plan.selected.length} deal{result.plan.selected.length === 1 ? '' : 's'}</span>
            </div>
            {result.plan.selected.length === 0 ? (
              <div className="panel-b"><p className="hint">No deals cleared the constraints at this budget.</p></div>
            ) : (
              <div className="panel-b flush">
                <table className="table">
                  <thead><tr><th>Property</th><th>Market</th><th className="num">Score</th><th className="num">Risk</th><th className="num">Required equity</th><th>Verdict</th></tr></thead>
                  <tbody>
                    {result.plan.selected.map((c, i) => (
                      <tr key={`${c.name}-${i}`}>
                        <td className="strong">{c.name}</td>
                        <td>{c.market}</td>
                        <td className="num">{c.score.toFixed(1)}</td>
                        <td className="num">{c.risk_score.toFixed(1)}</td>
                        <td className="num">{fmtMoney(c.required_equity)}</td>
                        <td><VerdictBadge value={String(c.recommendation)} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {markets.length > 0 && (
            <section className="panel reveal">
              <div className="panel-h"><div className="t"><h2>Market concentration</h2></div><span className="hint">share of committed equity</span></div>
              <div className="panel-b scn">
                {markets.map((m) => (
                  <div key={m.market} className="srow">
                    <span className="lab">{m.market}</span>
                    <div className="bar-track"><div className="bar-fill buy" style={{ width: `${Math.min(100, m.share * 100)}%` }} /></div>
                    <span className="sval">{fmtPct(m.share)}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="panel reveal">
            <div className="panel-h">
              <div className="t"><h2>Rejected</h2></div>
              <span className="hint">{result.plan.rejected.length} deal{result.plan.rejected.length === 1 ? '' : 's'}</span>
            </div>
            {result.plan.rejected.length === 0 ? (
              <div className="panel-b"><p className="hint">Every considered deal made the book.</p></div>
            ) : (
              <div className="panel-b flush">
                <table className="table">
                  <thead><tr><th>Property</th><th>Market</th><th className="num">Score</th><th>Reason</th></tr></thead>
                  <tbody>
                    {result.plan.rejected.map((c, i) => (
                      <tr key={`${c.name}-${i}`}>
                        <td className="strong">{c.name}</td>
                        <td>{c.market}</td>
                        <td className="num">{c.score.toFixed(1)}</td>
                        <td style={{ color: 'var(--muted)' }}>{rejectionReason(c, result.plan.notes)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {result.plan.notes.length > 0 && (
            <section className="panel reveal">
              <div className="panel-h"><div className="t"><h2>Optimizer notes</h2></div></div>
              <div className="panel-b">
                <ul className="prose" style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 'var(--s2)' }}>
                  {result.plan.notes.map((n, i) => <li key={i}>{n}</li>)}
                </ul>
              </div>
            </section>
          )}
        </>
      )}
    </>
  );
}
