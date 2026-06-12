export function RiskRegister({ risks }: { risks: Array<Record<string, unknown>> }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Risk register</h2>
        <span className="hint">{risks.length} tracked risks</span>
      </div>
      <div className="panel-body flush">
        <table className="table">
          <thead>
            <tr><th>Risk</th><th>Severity</th><th>Probability</th><th>Mitigation</th></tr>
          </thead>
          <tbody>
            {risks.map((r, i) => (
              <tr key={i}>
                <td className="strong">{String(r.name)}</td>
                <td>{String(r.severity)}</td>
                <td>{String(r.probability)}</td>
                <td>{String(r.mitigation)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
