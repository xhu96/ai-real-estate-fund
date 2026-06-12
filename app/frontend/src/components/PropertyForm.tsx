import { useState } from 'react';
import type { PropertyInput } from '../types';
import { DEFAULT_MODELS, PROVIDERS, loadRunSettings, saveRunSettings, type RunSettings } from './SettingsStore';

const fullExample = { name: 'Sunbelt Duplex', address: '123 Main St', market: 'San Antonio, TX', property_type: 'duplex', purchase_price: 285000, estimated_arv: 330000, monthly_rent: 3700, other_monthly_income: 0, vacancy_rate: 0.06, property_taxes_annual: 5200, insurance_annual: 2100, repairs_annual: 2500, utilities_annual: 600, hoa_annual: 0, capex_annual: 2500, management_rate: 0.08, acquisition_costs: 6500, rehab_budget: 18000, loan_amount: 210000, annual_interest_rate: 0.0725, loan_term_years: 30, holding_period_years: 5, expected_annual_rent_growth: 0.03, expected_annual_expense_growth: 0.03, expected_annual_appreciation: 0.035, selling_cost_rate: 0.06, neighborhood_score: 7, school_score: 6, liquidity_score: 7, crime_risk_score: 4, landlord_friendliness_score: 7, unit_count: 2, square_feet: 1850, bedrooms: 4, bathrooms: 2, year_built: 1948 } as unknown as PropertyInput;

type FieldSpec = { key: string; label: string; numeric?: boolean };
const groups: Array<{ title: string; fields: FieldSpec[]; advanced?: boolean }> = [
  { title: 'Property', fields: [
    { key: 'name', label: 'Property name' }, { key: 'address', label: 'Address' }, { key: 'market', label: 'Market' },
    { key: 'property_type', label: 'Type (e.g. duplex)' }, { key: 'unit_count', label: 'Units', numeric: true },
    { key: 'square_feet', label: 'Square feet', numeric: true }, { key: 'year_built', label: 'Year built', numeric: true },
  ]},
  { title: 'Income', fields: [
    { key: 'monthly_rent', label: 'Monthly rent ($)', numeric: true },
    { key: 'other_monthly_income', label: 'Other income ($/mo)', numeric: true },
    { key: 'vacancy_rate', label: 'Vacancy rate (0–1)', numeric: true },
  ]},
  { title: 'Financing', fields: [
    { key: 'purchase_price', label: 'Purchase price ($)', numeric: true },
    { key: 'loan_amount', label: 'Loan amount ($)', numeric: true },
    { key: 'annual_interest_rate', label: 'Interest rate (decimal)', numeric: true },
    { key: 'loan_term_years', label: 'Loan term (years)', numeric: true },
    { key: 'acquisition_costs', label: 'Closing costs ($)', numeric: true },
    { key: 'rehab_budget', label: 'Rehab budget ($)', numeric: true },
  ]},
  { title: 'Operating expenses (annual)', advanced: true, fields: [
    { key: 'property_taxes_annual', label: 'Property taxes ($)', numeric: true },
    { key: 'insurance_annual', label: 'Insurance ($)', numeric: true },
    { key: 'repairs_annual', label: 'Repairs ($)', numeric: true },
    { key: 'utilities_annual', label: 'Utilities ($)', numeric: true },
    { key: 'hoa_annual', label: 'HOA ($)', numeric: true },
    { key: 'capex_annual', label: 'Capex reserve ($)', numeric: true },
    { key: 'management_rate', label: 'Management rate (0–1)', numeric: true },
  ]},
  { title: 'Growth & exit', advanced: true, fields: [
    { key: 'holding_period_years', label: 'Hold (years)', numeric: true },
    { key: 'expected_annual_rent_growth', label: 'Rent growth (0–1)', numeric: true },
    { key: 'expected_annual_expense_growth', label: 'Expense growth (0–1)', numeric: true },
    { key: 'expected_annual_appreciation', label: 'Appreciation (0–1)', numeric: true },
    { key: 'selling_cost_rate', label: 'Selling costs (0–1)', numeric: true },
    { key: 'estimated_arv', label: 'After-repair value ($)', numeric: true },
  ]},
  { title: 'Market scores (1–10)', advanced: true, fields: [
    { key: 'neighborhood_score', label: 'Neighborhood', numeric: true },
    { key: 'school_score', label: 'Schools', numeric: true },
    { key: 'liquidity_score', label: 'Liquidity', numeric: true },
    { key: 'crime_risk_score', label: 'Crime risk', numeric: true },
    { key: 'landlord_friendliness_score', label: 'Landlord friendliness', numeric: true },
  ]},
];

export function PropertyForm({ onSubmit, busy }: { onSubmit: (payload: PropertyInput, settings: RunSettings) => void; busy: boolean }) {
  const [form, setForm] = useState<Record<string, unknown>>(fullExample as unknown as Record<string, unknown>);
  const [settings, setSettings] = useState<RunSettings>(loadRunSettings());

  const updateSettings = (patch: Partial<RunSettings>) => {
    const next = { ...settings, ...patch };
    setSettings(next);
    saveRunSettings(next);
  };
  const update = (spec: FieldSpec, value: string) =>
    setForm({ ...form, [spec.key]: spec.numeric ? (value === '' ? undefined : Number(value)) : value });

  const renderFields = (specs: FieldSpec[]) => (
    <div className="form-grid">
      {specs.map((spec) => (
        <label key={spec.key} className="field">
          <span>{spec.label}</span>
          <input value={form[spec.key] == null ? '' : String(form[spec.key])} inputMode={spec.numeric ? 'decimal' : undefined} onChange={(event) => update(spec, event.target.value)} />
        </label>
      ))}
    </div>
  );

  const basics = groups.filter((g) => !g.advanced);
  const advanced = groups.filter((g) => g.advanced);

  return (
    <form className="panel" onSubmit={(event) => { event.preventDefault(); onSubmit(form as unknown as PropertyInput, settings); }}>
      <div className="panel-head">
        <h2>Analyze a property</h2>
        <span className="hint">{settings.engine === 'institutional' ? 'Institutional committee · 77 workstreams' : 'Screening committee · 29 agents'}</span>
      </div>
      <div className="panel-body">
        {basics.map((group, index) => (
          <div key={group.title}>
            <div className="fieldset-label" style={index === 0 ? { marginTop: 0 } : undefined}>{group.title}</div>
            {renderFields(group.fields)}
          </div>
        ))}
        <details className="advanced">
          <summary>More assumptions <span className="hint">expenses, growth, market scores</span></summary>
          {advanced.map((group) => (
            <div key={group.title}>
              <div className="fieldset-label">{group.title}</div>
              {renderFields(group.fields)}
            </div>
          ))}
        </details>

        <div className="fieldset-label">Run options</div>
        <div className="run-options">
          <label className="field">
            <span>Committee</span>
            <select value={settings.engine} onChange={(e) => updateSettings({ engine: e.target.value as RunSettings['engine'] })}>
              <option value="institutional">Institutional (77 workstreams)</option>
              <option value="screening">Screening (29 agents, persisted)</option>
            </select>
          </label>
          {settings.engine === 'institutional' && (
            <>
              <label className="field checkbox">
                <span>LLM analyst debate</span>
                <span className="check-row">
                  <input type="checkbox" checked={settings.llmEnabled} onChange={(e) => updateSettings({ llmEnabled: e.target.checked })} />
                  <em>bull / bear / risk / chair</em>
                </span>
              </label>
              {settings.llmEnabled && (
                <>
                  <label className="field">
                    <span>Provider</span>
                    <select value={settings.llmProvider} onChange={(e) => updateSettings({ llmProvider: e.target.value, llmModel: '' })}>
                      {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </label>
                  <label className="field">
                    <span>Model</span>
                    <input placeholder={DEFAULT_MODELS[settings.llmProvider]} value={settings.llmModel} onChange={(e) => updateSettings({ llmModel: e.target.value })} />
                  </label>
                </>
              )}
            </>
          )}
        </div>

        <div className="btn-row">
          <button className="primary" disabled={busy}>{busy ? 'Running committee…' : 'Run committee'}</button>
          <button type="button" className="secondary" disabled={busy} onClick={() => setForm(fullExample as unknown as Record<string, unknown>)}>Reset to example</button>
        </div>
      </div>
    </form>
  );
}
