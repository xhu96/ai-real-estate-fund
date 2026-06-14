function sevClass(v: unknown): string {
  const s = String(v).toLowerCase();
  if (s.startsWith('h') || s === '3' || s === 'critical' || s === 'severe') return 'high';
  if (s.startsWith('m') || s === '2' || s === 'moderate') return 'medium';
  return 'low';
}
const cap = (v: unknown) => { const s = String(v); return s.charAt(0).toUpperCase() + s.slice(1); };

export function RiskRegister({ risks }: { risks: Array<Record<string, unknown>> }) {
  if (!risks || risks.length === 0) return null;
  return (
    <section className="panel reveal">
      <div className="panel-h">
        <div className="t"><h2>Risk register</h2></div>
        <span className="hint">{risks.length} tracked</span>
      </div>
      <div className="panel-b flush">
        <table className="table">
          <thead>
            <tr><th>Risk</th><th>Severity</th><th>Likelihood</th><th>Mitigation</th></tr>
          </thead>
          <tbody>
            {risks.map((r, i) => (
              <tr key={i}>
                <td className="strong">{String(r.name ?? r.risk ?? '—')}</td>
                <td><span className={`sev ${sevClass(r.severity)}`}>{cap(r.severity)}</span></td>
                <td>{cap(r.probability ?? r.likelihood ?? '—')}</td>
                <td>{String(r.mitigation ?? r.mitigant ?? '—')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
