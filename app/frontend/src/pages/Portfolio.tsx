export function Portfolio() {
  return (
    <>
      <div className="page-head">
        <h1>Portfolio</h1>
        <p>Concentration limits, allocation sizing, and downside exposure across accepted deals.</p>
      </div>
      <section className="panel">
        <div className="empty">
          <h3>No accepted deals yet</h3>
          <p>When a committee run is accepted, its allocation plan lands here. Try the portfolio engine from the CLI: <code>python -m ai_real_estate_fund compare examples/properties.csv</code></p>
        </div>
      </section>
    </>
  );
}
