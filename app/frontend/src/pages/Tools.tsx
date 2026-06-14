import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, GitCompareArrows, Gauge } from 'lucide-react';
import { fetchComps, runCalibration, runDrift } from '../api/client';
import type { CalibrationBin, CompsResult, DriftResult, RentComp, SaleComp } from '../types';

/** Markets with fixture comps on file (LocalDataProvider). Surfaced as a datalist + empty-state hint. */
const KNOWN_MARKETS = ['San Antonio, TX', 'Raleigh, NC', 'Cleveland, OH'] as const;

const fmtMoney = (n: number) => `$${Math.round(n).toLocaleString()}`;
const fmtPct = (n: number) => `${(n * 100).toFixed(1)}%`;
const fmtMiles = (n: number) => `${n.toFixed(1)} mi`;
const fmtConf = (n: number) => `${Math.round(n * 100)}%`;

/** Parse a comma/whitespace-separated list of finite numbers; returns null on the first bad token. */
function parseNumbers(raw: string): number[] | null {
  const tokens = raw.split(/[,\s]+/).map((t) => t.trim()).filter((t) => t.length > 0);
  const out: number[] = [];
  for (const t of tokens) {
    const n = Number(t);
    if (!Number.isFinite(n)) return null;
    out.push(n);
  }
  return out;
}

/** Parse a list of booleans accepting true/false, t/f, yes/no, 1/0; returns null on the first bad token. */
function parseBooleans(raw: string): boolean[] | null {
  const tokens = raw.split(/[,\s]+/).map((t) => t.trim().toLowerCase()).filter((t) => t.length > 0);
  const out: boolean[] = [];
  for (const t of tokens) {
    if (t === 'true' || t === 't' || t === 'yes' || t === 'y' || t === '1') out.push(true);
    else if (t === 'false' || t === 'f' || t === 'no' || t === 'n' || t === '0') out.push(false);
    else return null;
  }
  return out;
}

// ---------------------------------------------------------------------------
// a) Market comps
// ---------------------------------------------------------------------------
function MarketComps() {
  const [market, setMarket] = useState('San Antonio, TX');
  const [result, setResult] = useState<CompsResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState<string | null>(null);

  async function lookup() {
    const trimmed = market.trim();
    if (!trimmed) { setError('Enter a market to look up.'); return; }
    setError(null);
    setBusy(true);
    setResult(null);
    try {
      const res = await fetchComps(trimmed);
      setResult(res);
      setSearched(trimmed);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Comp lookup failed.');
    } finally {
      setBusy(false);
    }
  }

  const isEmpty = result !== null && result.rent_comps.length === 0 && result.sale_comps.length === 0;

  return (
    <section className="panel reveal">
      <div className="panel-h">
        <div className="t"><h2>Market comps</h2></div>
        <span className="hint">rent &amp; sale comps on file</span>
      </div>
      <div className="panel-b">
        <div className="form-grid">
          <label className="field">
            <span>Market</span>
            <input
              list="comps-markets"
              value={market}
              placeholder="San Antonio, TX"
              onChange={(e) => setMarket(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); void lookup(); } }}
            />
            <datalist id="comps-markets">
              {KNOWN_MARKETS.map((m) => <option key={m} value={m} />)}
            </datalist>
          </label>
        </div>
        <div className="btn-row">
          <button className="primary" type="button" disabled={busy} onClick={lookup}>
            {busy ? 'Looking up comps…' : 'Look up comps'}
          </button>
          <span className="hint">on file: {KNOWN_MARKETS.join(' · ')}</span>
        </div>
        {error && <div className="error-note" role="alert">{error}</div>}
      </div>

      {busy && (
        <div className="panel-b" aria-busy="true">
          <div className="skeleton"><div className="line w40" /><div className="line w70" /><div className="line" /><div className="line w70" /></div>
        </div>
      )}

      {result && !busy && isEmpty && (
        <div className="empty">
          <Building2 className="ic" aria-hidden="true" />
          <h3>No comps on file for that market</h3>
          <p>Try San Antonio, TX. Comps are available for {KNOWN_MARKETS.join(', ')}.</p>
        </div>
      )}

      {result && !busy && !isEmpty && (
        <>
          <div className="panel-h" style={{ borderTop: '1px solid var(--border)' }}>
            <div className="t"><h2>Rent comps</h2></div>
            <span className="hint">{searched} · {result.rent_comps.length} on file</span>
          </div>
          {result.rent_comps.length === 0 ? (
            <div className="panel-b"><p className="hint">No rent comps for {searched}.</p></div>
          ) : (
            <div className="panel-b flush">
              <table className="table">
                <thead>
                  <tr>
                    <th>Address</th><th className="num">Beds / baths</th><th className="num">Sqft</th>
                    <th className="num">Monthly rent</th><th className="num">Distance</th><th className="num">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {result.rent_comps.map((c: RentComp, i) => (
                    <tr key={`${c.address}-${i}`}>
                      <td className="strong">{c.address}</td>
                      <td className="num">{c.bedrooms} / {c.bathrooms}</td>
                      <td className="num">{c.square_feet.toLocaleString()}</td>
                      <td className="num">{fmtMoney(c.monthly_rent)}</td>
                      <td className="num">{fmtMiles(c.distance_miles)}</td>
                      <td className="num">{fmtConf(c.confidence)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="panel-h" style={{ borderTop: '1px solid var(--border)' }}>
            <div className="t"><h2>Sale comps</h2></div>
            <span className="hint">{searched} · {result.sale_comps.length} on file</span>
          </div>
          {result.sale_comps.length === 0 ? (
            <div className="panel-b"><p className="hint">No sale comps for {searched}.</p></div>
          ) : (
            <div className="panel-b flush">
              <table className="table">
                <thead>
                  <tr>
                    <th>Address</th><th className="num">Beds / baths</th><th className="num">Sqft</th>
                    <th className="num">Sale price</th><th className="num">Distance</th><th className="num">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {result.sale_comps.map((c: SaleComp, i) => (
                    <tr key={`${c.address}-${i}`}>
                      <td className="strong">{c.address}</td>
                      <td className="num">{c.bedrooms} / {c.bathrooms}</td>
                      <td className="num">{c.square_feet.toLocaleString()}</td>
                      <td className="num">{fmtMoney(c.sale_price)}</td>
                      <td className="num">{fmtMiles(c.distance_miles)}</td>
                      <td className="num">{fmtConf(c.confidence)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// b) Model validation — calibration
// ---------------------------------------------------------------------------
const CALIBRATION_SAMPLE = {
  scores: '20, 35, 48, 55, 62, 70, 78, 85, 90, 96',
  outcomes: '0, 0, 0, 1, 0, 1, 1, 1, 1, 1',
};

/** Color a bin's reliability bar by how well-populated it is, reusing the verdict palette. */
function binBarClass(count: number): string {
  if (count === 0) return 'watchlist';
  return 'buy';
}

function Calibration() {
  const [scoresRaw, setScoresRaw] = useState('');
  const [outcomesRaw, setOutcomesRaw] = useState('');
  const [bins, setBins] = useState<CalibrationBin[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function loadSample() {
    setScoresRaw(CALIBRATION_SAMPLE.scores);
    setOutcomesRaw(CALIBRATION_SAMPLE.outcomes);
    setError(null);
    setBins(null);
  }

  async function run() {
    const scores = parseNumbers(scoresRaw);
    const outcomes = parseBooleans(outcomesRaw);
    if (scores === null) { setError('Scores must be comma-separated numbers (0–100).'); return; }
    if (outcomes === null) { setError('Outcomes must be true/false or 1/0, comma-separated.'); return; }
    if (scores.length === 0 || outcomes.length === 0) { setError('Enter both scores and outcomes.'); return; }
    if (scores.length !== outcomes.length) {
      setError(`Scores and outcomes must have the same length — got ${scores.length} score${scores.length === 1 ? '' : 's'} and ${outcomes.length} outcome${outcomes.length === 1 ? '' : 's'}.`);
      return;
    }
    setError(null);
    setBusy(true);
    setBins(null);
    try {
      const res = await runCalibration(scores, outcomes);
      setBins(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Calibration failed.');
    } finally {
      setBusy(false);
    }
  }

  const populated = useMemo(() => (bins ?? []).filter((b) => b.count > 0).length, [bins]);

  return (
    <section className="panel reveal">
      <div className="panel-h">
        <div className="t"><h2>Model validation — calibration</h2></div>
        <span className="hint">do high scores deliver?</span>
      </div>
      <div className="panel-b">
        <div className="form-grid">
          <label className="field">
            <span>Scores (0–100, comma-separated)</span>
            <input value={scoresRaw} placeholder="62, 70, 85, 90" onChange={(e) => setScoresRaw(e.target.value)} />
          </label>
          <label className="field">
            <span>Outcomes (true/false or 1/0)</span>
            <input value={outcomesRaw} placeholder="0, 1, 1, 1" onChange={(e) => setOutcomesRaw(e.target.value)} />
          </label>
        </div>
        <div className="btn-row">
          <button className="primary" type="button" disabled={busy} onClick={run}>
            {busy ? 'Running calibration…' : 'Run calibration'}
          </button>
          <button className="secondary" type="button" disabled={busy} onClick={loadSample}>Load sample</button>
        </div>
        {error && <div className="error-note" role="alert">{error}</div>}
      </div>

      {busy && (
        <div className="panel-b" aria-busy="true">
          <div className="skeleton"><div className="line w40" /><div className="line w70" /><div className="line" /></div>
        </div>
      )}

      {bins && !busy && bins.length === 0 && (
        <div className="empty">
          <Gauge className="ic" aria-hidden="true" />
          <h3>No bins to show</h3>
          <p>The sample was empty. Load the example or enter scores and outcomes, then run again.</p>
        </div>
      )}

      {bins && !busy && bins.length > 0 && (
        <>
          <div className="panel-b scn">
            {bins.map((b, i) => (
              <div key={`${b.low}-${i}`} className="srow">
                <span className="lab">{b.low.toFixed(0)}–{b.high.toFixed(0)}</span>
                <div className="bar-track"><div className={`bar-fill ${binBarClass(b.count)}`} style={{ width: `${Math.min(100, b.success_rate * 100)}%` }} /></div>
                <span className="sval">{b.count === 0 ? '—' : fmtPct(b.success_rate)}</span>
              </div>
            ))}
          </div>
          <div className="panel-b flush">
            <table className="table">
              <thead><tr><th>Score range</th><th className="num">Count</th><th className="num">Success rate</th></tr></thead>
              <tbody>
                {bins.map((b, i) => (
                  <tr key={`row-${b.low}-${i}`}>
                    <td className="strong">{b.low.toFixed(0)}–{b.high.toFixed(0)}</td>
                    <td className="num">{b.count}</td>
                    <td className="num">{b.count === 0 ? <span className="hint">—</span> : fmtPct(b.success_rate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="panel-b"><p className="hint">{populated} of {bins.length} bins populated. Reliability rises left-to-right when the model is well calibrated.</p></div>
        </>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// c) Model validation — drift (PSI)
// ---------------------------------------------------------------------------
const DRIFT_SAMPLE = {
  expected: '10, 12, 14, 16, 18, 20, 22, 24, 26, 28',
  actual: '11, 13, 15, 22, 25, 28, 30, 31, 33, 35',
};

/** Map a PSI value to a plain-language stability band + a reused severity color class. */
function psiBand(psi: number): { label: string; sev: 'low' | 'medium' | 'high' } {
  if (psi < 0.1) return { label: 'Stable', sev: 'low' };
  if (psi <= 0.25) return { label: 'Moderate shift', sev: 'medium' };
  return { label: 'Significant shift', sev: 'high' };
}

function Drift() {
  const [expectedRaw, setExpectedRaw] = useState('');
  const [actualRaw, setActualRaw] = useState('');
  const [result, setResult] = useState<DriftResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function loadSample() {
    setExpectedRaw(DRIFT_SAMPLE.expected);
    setActualRaw(DRIFT_SAMPLE.actual);
    setError(null);
    setResult(null);
  }

  async function run() {
    const expected = parseNumbers(expectedRaw);
    const actual = parseNumbers(actualRaw);
    if (expected === null) { setError('Expected must be comma-separated numbers.'); return; }
    if (actual === null) { setError('Actual must be comma-separated numbers.'); return; }
    if (expected.length === 0 || actual.length === 0) { setError('Enter both an expected and an actual distribution.'); return; }
    setError(null);
    setBusy(true);
    setResult(null);
    try {
      const res = await runDrift(expected, actual);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Drift calculation failed.');
    } finally {
      setBusy(false);
    }
  }

  const band = result ? psiBand(result.psi) : null;

  return (
    <section className="panel reveal">
      <div className="panel-h">
        <div className="t"><h2>Model validation — drift (PSI)</h2></div>
        <span className="hint">expected vs. actual distribution</span>
      </div>
      <div className="panel-b">
        <div className="form-grid">
          <label className="field">
            <span>Expected (comma-separated)</span>
            <input value={expectedRaw} placeholder="10, 12, 14, 16" onChange={(e) => setExpectedRaw(e.target.value)} />
          </label>
          <label className="field">
            <span>Actual (comma-separated)</span>
            <input value={actualRaw} placeholder="11, 13, 15, 22" onChange={(e) => setActualRaw(e.target.value)} />
          </label>
        </div>
        <div className="btn-row">
          <button className="primary" type="button" disabled={busy} onClick={run}>
            {busy ? 'Computing PSI…' : 'Run drift'}
          </button>
          <button className="secondary" type="button" disabled={busy} onClick={loadSample}>Load sample</button>
          <span className="hint">&lt; 0.1 stable · 0.1–0.25 moderate · &gt; 0.25 significant</span>
        </div>
        {error && <div className="error-note" role="alert">{error}</div>}
      </div>

      {busy && (
        <div className="panel-b" aria-busy="true">
          <div className="skeleton"><div className="line w40" /><div className="line w70" /></div>
        </div>
      )}

      {result && !busy && band && (
        <div className="panel-b">
          <div className="kpi-grid">
            <div className="kpi">
              <div className="l">Population Stability Index</div>
              <div className="v accent">{result.psi.toFixed(3)}</div>
              <div className="d"><span className={`sev ${band.sev}`}>{band.label}</span></div>
            </div>
          </div>
          <p className="hint" style={{ marginTop: 'var(--s4)' }}>
            PSI under 0.1 means the distributions agree (stable). 0.1–0.25 is a moderate shift worth watching. Above 0.25 is a significant shift — the model is seeing inputs unlike what it was tuned on.
          </p>
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
export function Tools() {
  return (
    <>
      <div className="page-head">
        <h1>Tools</h1>
        <p>
          <Link to="/analyze">Analyze</Link> runs the committee, <Link to="/portfolio">Portfolio</Link> sizes
          allocations, <Link to="/research">Research lab</Link> backtests. The tools below run on their own —
          look up market comps and validate the model without a full workflow.
        </p>
      </div>

      <MarketComps />
      <Calibration />
      <Drift />

      <section className="panel reveal">
        <div className="panel-h"><div className="t"><h2><GitCompareArrows className="ic" aria-hidden="true" style={{ verticalAlign: '-2px', marginRight: 6 }} />About these tools</h2></div></div>
        <div className="panel-b">
          <p className="hint">
            Each tool calls a single backend endpoint and shows the raw result — no run is saved. Comps read the
            local fixture provider; calibration and drift are pure functions over the numbers you supply.
          </p>
        </div>
      </section>
    </>
  );
}
