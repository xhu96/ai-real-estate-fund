type Scorecard = { name?: string; category?: string; score?: number | string };
type Scenario = Record<string, unknown>;

const verdictKey = (v: unknown) => ({ BUY: 'buy', NEGOTIATE: 'negotiate', WATCHLIST: 'watchlist', PASS: 'pass' }[String(v).toUpperCase()] ?? 'watchlist');

function shortLabel(s: string): string {
  const clean = s.replace(/scorecard|score/gi, '').trim();
  return clean.length > 12 ? clean.slice(0, 11) + '…' : clean;
}

export function ScoreRadar({ scorecards }: { scorecards: Scorecard[] }) {
  const data = scorecards
    .map((c) => ({ name: String(c.name ?? c.category ?? ''), score: Math.max(0, Math.min(100, Number(c.score ?? 0))) }))
    .filter((d) => d.name);
  if (data.length < 3) return null;

  const cx = 180, cy = 150, rR = 112;
  const pt = (i: number, f: number) => {
    const a = (i / data.length) * Math.PI * 2 - Math.PI / 2;
    return [cx + Math.cos(a) * rR * f, cy + Math.sin(a) * rR * f] as const;
  };
  const dataPoly = data.map((d, i) => pt(i, d.score / 100).join(',')).join(' ');

  return (
    <section className="panel">
      <div className="panel-h"><div className="t"><h2>Scorecard by domain</h2></div><span className="hint">0–100</span></div>
      <div className="panel-b">
        <svg className="radar" viewBox="0 0 360 300" role="img" aria-label={`Radar of committee scores across ${data.length} domains.`}>
          {[0.25, 0.5, 0.75, 1].map((f) => (
            <polygon key={f} points={data.map((_, i) => pt(i, f).join(',')).join(' ')} fill="none" stroke="var(--border)" strokeWidth={1} opacity={0.55} />
          ))}
          {data.map((d, i) => {
            const [x, y] = pt(i, 1);
            const [lx, ly] = pt(i, 1.16);
            return (
              <g key={d.name}>
                <line x1={cx} y1={cy} x2={x} y2={y} stroke="var(--border)" strokeWidth={1} opacity={0.5} />
                <text x={lx} y={ly} textAnchor="middle" dominantBaseline="middle" fontSize={10} fill="var(--muted)" fontFamily="var(--mono)">{shortLabel(d.name)}</text>
              </g>
            );
          })}
          <polygon points={dataPoly} fill="var(--accent)" fillOpacity={0.16} stroke="var(--accent)" strokeWidth={2} />
          {data.map((d, i) => { const [x, y] = pt(i, d.score / 100); return <circle key={d.name} cx={x} cy={y} r={2.6} fill="var(--accent)" />; })}
        </svg>
        <div className="radar-tags">
          {data.map((d) => <span key={d.name}><b>{d.score.toFixed(0)}</b> {shortLabel(d.name)}</span>)}
        </div>
      </div>
    </section>
  );
}

export function ScenarioStress({ scenarios }: { scenarios: Scenario[] }) {
  if (!scenarios || scenarios.length === 0) return null;
  const num = (v: unknown) => (v == null ? null : Number(v));
  return (
    <section className="panel">
      <div className="panel-h"><div className="t"><h2>Scenario stress</h2></div><span className="hint">score under stressed assumptions</span></div>
      <div className="panel-b scn">
        {scenarios.map((s, i) => {
          const score = Math.max(0, Math.min(100, num(s.score) ?? 0));
          const dscr = num(s.dscr);
          const k = verdictKey(s.recommendation);
          return (
            <div key={i}>
              <div className="srow">
                <span className="lab">{String(s.name ?? `Case ${i + 1}`)}</span>
                <div className="bar-track"><div className={`bar-fill ${k}`} style={{ width: `${score}%` }} /></div>
                <span className="sval">{score.toFixed(1)}</span>
              </div>
              <div className="ends" style={{ display: 'flex', gap: 'var(--s4)', marginLeft: 110, marginTop: 4, fontSize: 'var(--text-xs)', color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
                <span>DSCR {dscr == null ? 'n/a' : `${dscr.toFixed(2)}x`}</span>
                {s.cash_flow_before_tax != null && <span>CF ${Math.round(Number(s.cash_flow_before_tax)).toLocaleString()}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
