import { useMemo, useState } from 'react';
import { FlaskConical } from 'lucide-react';
import { runBacktest } from '../api/client';
import { VerdictBadge } from '../components/Badge';
import type { BacktestResult, BacktestTrade } from '../types';

/** Backend defaults for POST /research/backtest — pre-fill the config form with these. */
const DEFAULTS = {
  min_score: 65,
  starting_equity: 1_000_000,
  max_positions: 10,
  allocation_per_deal: 0.1,
};

type Config = typeof DEFAULTS;

const fmtMoney = (n: number) => `$${Math.round(n).toLocaleString()}`;
const fmtPct = (n: number) => `${(n * 100).toFixed(1)}%`;
const irrLabel = (v: number | null) => (v == null ? 'n/a' : fmtPct(v));

/** Tiny inline-SVG bar comparing average model score (0–100) vs hit rate (0–1 → %). */
function ModelVsHit({ result }: { result: BacktestResult }) {
  const rows: Array<{ label: string; pct: number; cls: string; display: string }> = [
    { label: 'Avg model score', pct: Math.max(0, Math.min(100, result.average_model_score)), cls: 'buy', display: result.average_model_score.toFixed(1) },
    { label: 'Hit rate', pct: Math.max(0, Math.min(100, result.hit_rate * 100)), cls: 'negotiate', display: fmtPct(result.hit_rate) },
  ];
  return (
    <section className="panel reveal">
      <div className="panel-h"><div className="t"><h2>Model conviction vs. outcome</h2></div><span className="hint">0–100</span></div>
      <div className="panel-b scn">
        {rows.map((r) => (
          <div key={r.label} className="srow">
            <span className="lab">{r.label}</span>
            <div className="bar-track"><div className={`bar-fill ${r.cls}`} style={{ width: `${r.pct}%` }} /></div>
            <span className="sval">{r.display}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function ResearchLab() {
  const [config, setConfig] = useState<Config>(DEFAULTS);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setField = (key: keyof Config, value: string) =>
    setConfig((prev) => ({ ...prev, [key]: value === '' ? 0 : Number(value) }));

  async function run() {
    setError(null);
    setBusy(true);
    setResult(null);
    try {
      const res = await runBacktest(config);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Backtest failed.');
    } finally {
      setBusy(false);
    }
  }

  const trades = useMemo<BacktestTrade[]>(() => result?.trades ?? [], [result]);

  return (
    <>
      <div className="page-head">
        <h1>Research lab</h1>
        <p>Replay the screening committee over a historical deal panel: which deals it would have bought, and how the modeled conviction lines up against realized returns.</p>
      </div>

      <section className="panel reveal">
        <div className="panel-h"><div className="t"><h2>Backtest configuration</h2></div></div>
        <div className="panel-b">
          <div className="form-grid">
            <label className="field">
              <span>Min score</span>
              <input inputMode="decimal" value={String(config.min_score)} onChange={(e) => setField('min_score', e.target.value)} />
            </label>
            <label className="field">
              <span>Starting equity ($)</span>
              <input inputMode="decimal" value={String(config.starting_equity)} onChange={(e) => setField('starting_equity', e.target.value)} />
            </label>
            <label className="field">
              <span>Max positions</span>
              <input inputMode="decimal" value={String(config.max_positions)} onChange={(e) => setField('max_positions', e.target.value)} />
            </label>
            <label className="field">
              <span>Allocation per deal (0–1)</span>
              <input inputMode="decimal" value={String(config.allocation_per_deal)} onChange={(e) => setField('allocation_per_deal', e.target.value)} />
            </label>
          </div>
          <div className="btn-row">
            <button className="primary" type="button" disabled={busy} onClick={run}>
              {busy ? 'Running backtest…' : 'Run backtest'}
            </button>
          </div>
          {error && <div className="error-note" role="alert">{error}</div>}
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
            <div className="kpi"><div className="l">Deals selected</div><div className="v">{result.selected_count}</div><div className="d">of {trades.length} in panel</div></div>
            <div className="kpi"><div className="l">Hit rate</div><div className="v accent">{fmtPct(result.hit_rate)}</div><div className="d">selected deals that delivered</div></div>
            <div className="kpi"><div className="l">Avg realized IRR</div><div className="v gold">{fmtPct(result.average_realized_irr)}</div><div className="d">across selected</div></div>
            <div className="kpi"><div className="l">Ending equity</div><div className="v">{fmtMoney(result.ending_equity)}</div><div className="d">from {fmtMoney(config.starting_equity)}</div></div>
          </div>

          <ModelVsHit result={result} />

          <section className="panel reveal">
            <div className="panel-h">
              <div className="t"><h2>Trades</h2></div>
              <span className="hint">{result.selected_count} selected · avg model score {result.average_model_score.toFixed(1)}</span>
            </div>
            {trades.length === 0 ? (
              <div className="empty">
                <FlaskConical className="ic" aria-hidden="true" />
                <h3>No trades in this panel</h3>
                <p>No historical deals were available to replay. Adjust the configuration and run again.</p>
              </div>
            ) : (
              <div className="panel-b flush">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Deal</th><th>Selected</th><th className="num">Model score</th><th>Verdict</th>
                      <th className="num">Expected IRR</th><th className="num">Realized IRR</th><th className="num">Equity ×</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.map((t, i) => (
                      <tr key={`${t.deal_name}-${i}`} style={t.selected ? { background: 'var(--accent-tint)' } : undefined}>
                        <td className="strong">{t.deal_name}</td>
                        <td>{t.selected ? <span className="sev low">Selected</span> : <span className="hint">—</span>}</td>
                        <td className="num">{t.score.toFixed(1)}</td>
                        <td><VerdictBadge value={String(t.recommendation)} /></td>
                        <td className="num">{irrLabel(t.expected_irr)}</td>
                        <td className="num">{fmtPct(t.realized_irr)}</td>
                        <td className="num">{t.realized_equity_multiple.toFixed(2)}×</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </>
  );
}
