import type { AgentFinding } from '../types';

function scoreClass(score: number): string {
  if (score < 52) return 'score low';
  if (score >= 78) return 'score high';
  return 'score';
}

export function Findings({ findings }: { findings: AgentFinding[] }) {
  const sorted = [...findings].sort((a, b) => a.score - b.score);
  const weakest = sorted.slice(0, 8);
  const rest = sorted.slice(8);
  return (
    <section className="panel reveal">
      <div className="panel-h">
        <div className="t"><h2>Committee findings</h2></div>
        <span className="hint">{findings.length} agents · weakest first</span>
      </div>
      <div className="panel-body flush">
        {weakest.map((f) => (
          <div key={f.agent_name} className="finding-row">
            <span className="name">{f.agent_name}</span>
            <span className={scoreClass(f.score)}>{f.score.toFixed(1)}</span>
            <span className="thesis" title={f.thesis}>{f.concerns[0] ?? f.thesis}</span>
          </div>
        ))}
        {rest.length > 0 && (
          <details className="findings-group">
            <summary>
              <span>All remaining findings</span>
              <span className="meta">{rest.length} agents <span className="chev">›</span></span>
            </summary>
            {rest.map((f) => (
              <div key={f.agent_name} className="finding-row">
                <span className="name">{f.agent_name}</span>
                <span className={scoreClass(f.score)}>{f.score.toFixed(1)}</span>
                <span className="thesis" title={f.thesis}>{f.positives[0] ?? f.thesis}</span>
              </div>
            ))}
          </details>
        )}
      </div>
    </section>
  );
}
