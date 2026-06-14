import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LineChart, Layers, AlertTriangle } from 'lucide-react';
import { recentAnalyses, getRoster } from '../api/client';
import { RunRow } from '../components/RunRow';
import type { CommitteeDecision, CommitteeRoster } from '../types';

export function Dashboard() {
  const navigate = useNavigate();
  const [runs, setRuns] = useState<CommitteeDecision[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [roster, setRoster] = useState<CommitteeRoster | null>(null);
  const [rosterError, setRosterError] = useState<string | null>(null);
  const load = useCallback(() => {
    setError(null);
    setRuns(null);
    recentAnalyses().then(setRuns).catch((e: unknown) => {
      setError(e instanceof Error ? e.message : 'Failed to load saved runs.');
    });
  }, []);
  useEffect(() => { load(); }, [load]);

  // The committee composition is loaded independently so a roster failure never blocks the KPIs or run table.
  useEffect(() => {
    setRosterError(null);
    getRoster().then(setRoster).catch((e: unknown) => {
      setRosterError(e instanceof Error ? e.message : 'Failed to load committee composition.');
    });
  }, []);

  const kpis = useMemo(() => {
    if (!runs || runs.length === 0) return null;
    const scores = runs.map((r) => r.overall_score).sort((a, b) => a - b);
    const median = scores[Math.floor(scores.length / 2)];
    const buySide = runs.filter((r) => ['BUY', 'NEGOTIATE'].includes(String(r.recommendation))).length;
    const passed = runs.filter((r) => String(r.recommendation) === 'PASS').length;
    return {
      reviewed: runs.length,
      median,
      buyRate: Math.round((buySide / runs.length) * 100),
      passRate: Math.round((passed / runs.length) * 100),
    };
  }, [runs]);

  return (
    <>
      <div className="page-head" style={{ flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between', gap: 'var(--s4)', flexWrap: 'wrap' }}>
        <div>
          <h1>Overview</h1>
          <p>A 77-workstream investment committee for rental real estate — scores, policy gates, scenario stress, and an auditable memo. Deterministic by design: the analysts debate, but they never set the score.</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/analyze')}><LineChart className="ic" strokeWidth={2.2} aria-hidden="true" /> Analyze a deal</button>
      </div>

      <div className="kpi-grid">
        <div className="kpi"><div className="l">Deals reviewed</div><div className="v">{kpis ? kpis.reviewed : '—'}</div><div className="d">persisted committee runs</div></div>
        <div className="kpi"><div className="l">Median score</div><div className="v gold">{kpis ? kpis.median.toFixed(1) : '—'}</div><div className="d">across saved runs</div></div>
        <div className="kpi"><div className="l">Buy-side rate</div><div className="v accent">{kpis ? `${kpis.buyRate}%` : '—'}</div><div className="d">buy or negotiate</div></div>
        <div className="kpi"><div className="l">Workstreams</div><div className="v">77</div><div className="d">+ 4 LLM analysts</div></div>
      </div>

      <div className="grid-2">
        <section className="panel">
          <div className="panel-h">
            <div className="t"><h2>Recent verdicts</h2></div>
            {runs && runs.length > 0 && <span className="hint">latest {Math.min(runs.length, 6)}</span>}
          </div>
          {error ? (
            <div className="empty">
              <AlertTriangle className="ic" aria-hidden="true" />
              <h3>Couldn't load runs</h3>
              <div className="error-note" role="alert" style={{ marginInline: 'auto', maxWidth: '52ch', textAlign: 'left' }}>{error}</div>
              <div className="btn-row"><button className="primary" onClick={load}>Retry</button></div>
            </div>
          ) : runs === null ? (
            <div className="skeleton"><div className="line w70" /><div className="line w40" /><div className="line w70" /></div>
          ) : runs.length === 0 ? (
            <div className="empty">
              <LineChart className="ic" aria-hidden="true" />
              <h3>No deals analyzed yet</h3>
              <p>Run the committee on a sample deal to watch the scoring, the constellation, scenarios, and the risk register come together.</p>
              <div className="btn-row"><button className="primary" onClick={() => navigate('/analyze')}>Run your first deal</button></div>
            </div>
          ) : (
            <div className="panel-b flush">
              <table className="table">
                <thead><tr><th>Property</th><th>Market</th><th className="num">Score</th><th>Verdict</th></tr></thead>
                <tbody>
                  {runs.slice(0, 6).map((run) => (
                    <RunRow key={run.run_id} run={run} />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-h">
            <div className="t"><Layers className="ic" style={{ width: 16, height: 16, color: 'var(--muted)' }} aria-hidden="true" /><h2>Committee composition</h2></div>
            <span className="hint">{roster ? `${roster.total} workstreams` : '77 workstreams'}</span>
          </div>
          <div className="panel-b">
            {rosterError ? (
              <p className="hint" style={{ whiteSpace: 'normal', fontFamily: 'var(--font)', lineHeight: 1.5 }}>
                Composition unavailable right now — <Link to="/committee">view the committee</Link> for the full roster.
              </p>
            ) : roster === null ? (
              <div className="skeleton" style={{ padding: 0 }}><div className="line w70" /><div className="line w40" /><div className="line w70" /><div className="line w40" /></div>
            ) : (
              <dl className="def-rows">
                {roster.categories.map((cat) => (
                  <div key={cat.key} className="def-row"><dt>{cat.label}</dt><dd>{cat.count}</dd></div>
                ))}
              </dl>
            )}
            <div className="btn-row" style={{ marginTop: 'var(--s4)' }}>
              <Link to="/committee">View all {roster ? roster.total : 77} workstreams →</Link>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
