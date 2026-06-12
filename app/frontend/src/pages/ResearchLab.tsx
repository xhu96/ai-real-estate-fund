export function ResearchLab() {
  return (
    <>
      <div className="page-head">
        <h1>Research</h1>
        <p>Backtesting and historical-deal simulation over the screening committee.</p>
      </div>
      <section className="panel">
        <div className="empty">
          <h3>Backtests run from the CLI</h3>
          <p>Replay the committee over a historical deal panel: <code>python -m ai_real_estate_fund.backtesting.cli --examples examples/properties.csv</code>. Results land in this workspace in a future release.</p>
        </div>
      </section>
    </>
  );
}
