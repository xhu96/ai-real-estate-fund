import { useCallback, useEffect, useMemo, useState } from 'react';
import { Network, AlertTriangle } from 'lucide-react';
import { getRoster } from '../api/client';
import type { CommitteeRoster, RosterAgent, RosterCategory } from '../types';

/** Sum the weights of a category's agents — shown in each <summary> as the category's pull. */
function categoryWeight(cat: RosterCategory): number {
  return cat.agents.reduce((sum, a) => sum + a.weight, 0);
}

/** A single agent: a summary row (name · weight · focus) that expands to positive/concern/action + citations. */
function AgentRow({ agent }: { agent: RosterAgent }) {
  return (
    <details className="findings-group">
      <summary>
        <span style={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0 }}>
          <span>{agent.name}</span>
          {agent.focus_components.length > 0 && (
            <span className="hint" style={{ fontWeight: 400, whiteSpace: 'normal' }}>
              {agent.focus_components.join(' · ')}
            </span>
          )}
        </span>
        <span className="meta">
          <span className="num" style={{ color: 'var(--ink)', fontWeight: 600 }}>{agent.weight.toFixed(2)}</span>
          <span className="chev">›</span>
        </span>
      </summary>
      <div style={{ padding: 'var(--s4) var(--s5)', display: 'grid', gap: 'var(--s3)' }}>
        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--muted)' }}>{agent.role}</p>
        <dl className="def-rows">
          <div className="def-row"><dt><span className="sev low">Supports</span></dt><dd style={{ fontWeight: 400, color: 'var(--body)', textAlign: 'left' }}>{agent.positive}</dd></div>
          <div className="def-row"><dt><span className="sev high">Concern</span></dt><dd style={{ fontWeight: 400, color: 'var(--body)', textAlign: 'left' }}>{agent.concern}</dd></div>
          <div className="def-row"><dt><span className="sev medium">Action</span></dt><dd style={{ fontWeight: 400, color: 'var(--body)', textAlign: 'left' }}>{agent.action}</dd></div>
        </dl>
        {agent.sources.length > 0 && (
          <div>
            <div className="fieldset-label" style={{ margin: '0 0 var(--s2)' }}>Citations</div>
            <ul style={{ margin: 0, paddingLeft: '1.1em', display: 'grid', gap: 4 }}>
              {agent.sources.map((src, i) => (
                <li key={i} className="hint" style={{ fontFamily: 'var(--font)', whiteSpace: 'normal', lineHeight: 1.5 }}>{src}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </details>
  );
}

/** One expandable category: summary shows label + count + summed weight; body is the agent table. */
function CategorySection({ cat }: { cat: RosterCategory }) {
  const weight = categoryWeight(cat);
  return (
    <details className="findings-group">
      <summary>
        <span>{cat.label}</span>
        <span className="meta">
          {cat.count} workstream{cat.count === 1 ? '' : 's'} · weight <span className="num">{weight.toFixed(2)}</span>
          <span className="chev">›</span>
        </span>
      </summary>
      <div className="panel-b flush">
        <table className="table">
          <thead>
            <tr>
              <th>Agent</th>
              <th className="num">Weight</th>
              <th>Focus components</th>
            </tr>
          </thead>
          <tbody>
            {cat.agents.map((agent) => (
              <tr key={agent.name}>
                <td colSpan={3} style={{ padding: 0 }}>
                  <AgentRow agent={agent} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

export function Committee() {
  const [roster, setRoster] = useState<CommitteeRoster | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setError(null);
    setRoster(null);
    getRoster().then(setRoster).catch((e: unknown) => {
      setError(e instanceof Error ? e.message : 'Failed to load the committee roster.');
    });
  }, []);
  useEffect(() => { load(); }, [load]);

  const totalWeight = useMemo(() => {
    if (!roster) return 0;
    return roster.categories.reduce((sum, c) => sum + categoryWeight(c), 0);
  }, [roster]);

  return (
    <>
      <div className="page-head">
        <h1>Committee</h1>
        <p>
          {roster ? roster.total : 77} deterministic, config-driven diligence workstreams across 8 categories.
          Each agent carries a <b>weight</b> that sets its pull on the blended score — the number is the interface.
          The committee is fully deterministic: no LLM touches the score. Four optional LLM analysts
          (bull, bear, risk, chair) can <i>debate</i> the result, but they never change it — see a deal's institutional
          analysis to read the debate.
        </p>
      </div>

      {error ? (
        <section className="panel">
          <div className="empty">
            <AlertTriangle className="ic" aria-hidden="true" />
            <h3>Couldn't load the roster</h3>
            <div className="error-note" role="alert" style={{ marginInline: 'auto', maxWidth: '52ch', textAlign: 'left' }}>{error}</div>
            <div className="btn-row"><button className="primary" onClick={load}>Retry</button></div>
          </div>
        </section>
      ) : roster === null ? (
        <section className="panel" aria-busy="true">
          <div className="skeleton"><div className="line w40" /><div className="line w70" /><div className="line" /><div className="line w70" /><div className="line w40" /></div>
        </section>
      ) : roster.categories.length === 0 ? (
        <section className="panel">
          <div className="empty">
            <Network className="ic" aria-hidden="true" />
            <h3>No workstreams configured</h3>
            <p>The roster came back empty. Check the backend configuration and try again.</p>
            <div className="btn-row"><button className="primary" onClick={load}>Reload</button></div>
          </div>
        </section>
      ) : (
        <div className="grid-2">
          <section className="panel reveal">
            <div className="panel-h">
              <div className="t"><Network className="ic" style={{ width: 16, height: 16, color: 'var(--muted)' }} aria-hidden="true" /><h2>Workstreams by category</h2></div>
              <span className="hint">expand to drill in</span>
            </div>
            <div className="panel-b flush">
              {roster.categories.map((cat) => (
                <CategorySection key={cat.key} cat={cat} />
              ))}
            </div>
          </section>

          <section className="panel reveal">
            <div className="panel-h">
              <div className="t"><h2>Composition</h2></div>
              <span className="hint">{roster.total} workstreams</span>
            </div>
            <div className="panel-b">
              <dl className="def-rows">
                {roster.categories.map((cat) => (
                  <div key={cat.key} className="def-row"><dt>{cat.label}</dt><dd>{cat.count}</dd></div>
                ))}
                <div className="def-row" style={{ borderTop: '2px solid var(--border)' }}>
                  <dt className="strong" style={{ fontWeight: 600, color: 'var(--ink)' }}>Total</dt>
                  <dd>{roster.total}</dd>
                </div>
              </dl>
              <div className="def-rows" style={{ marginTop: 'var(--s4)' }}>
                <div className="def-row"><dt>Summed weight</dt><dd className="num">{totalWeight.toFixed(2)}</dd></div>
                <div className="def-row"><dt>LLM analysts</dt><dd>4</dd></div>
              </div>
              <p className="hint" style={{ marginTop: 'var(--s4)', whiteSpace: 'normal', fontFamily: 'var(--font)', lineHeight: 1.5 }}>
                Weights set each agent's pull on the blended score. The analysts debate; they never set the score.
              </p>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
