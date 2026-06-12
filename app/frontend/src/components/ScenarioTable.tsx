import { VerdictBadge } from './Badge';

export function ScenarioTable({ scenarios }: { scenarios: Array<Record<string, unknown>> }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Scenarios</h2>
        <span className="hint">Same deal under stressed assumptions</span>
      </div>
      <div className="panel-body flush">
        <table className="table">
          <thead>
            <tr><th>Case</th><th className="num">Score</th><th className="num">DSCR</th><th className="num">Cash flow</th><th>Verdict</th></tr>
          </thead>
          <tbody>
            {scenarios.map((s, i) => (
              <tr key={i}>
                <td className="strong">{String(s.name)}</td>
                <td className="num">{Number(s.score ?? 0).toFixed(1)}</td>
                <td className="num">{s.dscr == null ? 'n/a' : `${Number(s.dscr).toFixed(2)}x`}</td>
                <td className="num">{s.cash_flow_before_tax == null ? 'n/a' : `$${Math.round(Number(s.cash_flow_before_tax)).toLocaleString()}`}</td>
                <td><VerdictBadge value={String(s.recommendation)} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
