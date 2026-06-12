import { useState } from 'react';
import { apiBase } from '../api/client';
import { DEFAULT_MODELS, PROVIDERS, loadRunSettings, saveRunSettings } from '../components/SettingsStore';

export function Settings() {
  const [base, setBase] = useState(localStorage.getItem('aref.apiBase') ?? '');
  const [run, setRun] = useState(loadRunSettings());
  const [saved, setSaved] = useState(false);

  function save() {
    if (base.trim()) localStorage.setItem('aref.apiBase', base.trim());
    else localStorage.removeItem('aref.apiBase');
    saveRunSettings(run);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <>
      <div className="page-head">
        <h1>Settings</h1>
        <p>Saved in this browser. API keys stay on the server in <code>.env</code> — they are never entered or stored here.</p>
      </div>
      <section className="panel">
        <div className="panel-head"><h2>Connection</h2></div>
        <div className="panel-body">
          <div className="form-grid">
            <label className="field">
              <span>API base URL</span>
              <input placeholder={apiBase()} value={base} onChange={(e) => setBase(e.target.value)} />
            </label>
          </div>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Default run options</h2><span className="hint">used on the Analyze page</span></div>
        <div className="panel-body">
          <div className="form-grid">
            <label className="field">
              <span>Committee</span>
              <select value={run.engine} onChange={(e) => setRun({ ...run, engine: e.target.value as typeof run.engine })}>
                <option value="institutional">Institutional (77 workstreams)</option>
                <option value="screening">Screening (29 agents)</option>
              </select>
            </label>
            <label className="field">
              <span>LLM provider</span>
              <select value={run.llmProvider} onChange={(e) => setRun({ ...run, llmProvider: e.target.value, llmModel: '' })}>
                {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>
            <label className="field">
              <span>Model</span>
              <input placeholder={DEFAULT_MODELS[run.llmProvider]} value={run.llmModel} onChange={(e) => setRun({ ...run, llmModel: e.target.value })} />
            </label>
            <label className="field checkbox">
              <span>LLM debate on by default</span>
              <span className="check-row">
                <input type="checkbox" checked={run.llmEnabled} onChange={(e) => setRun({ ...run, llmEnabled: e.target.checked })} />
                <em>requires a provider key in .env</em>
              </span>
            </label>
          </div>
          <div className="btn-row">
            <button className="primary" type="button" onClick={save}>Save settings</button>
            {saved && <span className="hint" role="status">Saved.</span>}
          </div>
        </div>
      </section>
    </>
  );
}
