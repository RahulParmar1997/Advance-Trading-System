const panels = [
  {
    title: "Market State",
    eyebrow: "01",
    description: "Session, regime and data freshness",
    status: "Awaiting feed",
    detail: "No live market observation is connected to this view.",
  },
  {
    title: "Scanner",
    eyebrow: "02",
    description: "Evidence-backed candidate opportunities",
    status: "Read only",
    detail: "Candidates appear only when supplied by the backend scanner.",
  },
  {
    title: "Risk",
    eyebrow: "03",
    description: "Pre-trade controls and current guardrails",
    status: "Backend gated",
    detail: "The UI cannot approve, submit, or mutate an order.",
  },
  {
    title: "Portfolio",
    eyebrow: "04",
    description: "PAPER positions, exposure and P&L",
    status: "PAPER",
    detail: "Operational state remains authoritative in the backend.",
  },
] as const;

const navigation = ["Overview", "Market", "Scanner", "Risk", "Portfolio", "Research"];

export default function HomePage() {
  return (
    <main className="terminal-shell">
      <header className="topbar">
        <div>
          <p className="brand">Advance Trading System</p>
          <p className="product-line">Market intelligence terminal</p>
        </div>
        <div className="environment" aria-label="Execution environment">
          <span className="status-dot" aria-hidden="true" />
          PAPER MODE
        </div>
      </header>

      <nav className="nav-strip" aria-label="Primary navigation">
        {navigation.map((item, index) => (
          <span className={index === 0 ? "nav-item active" : "nav-item"} key={item}>
            {item}
          </span>
        ))}
      </nav>

      <section className="hero" aria-labelledby="dashboard-title">
        <div>
          <p className="section-kicker">CONTROL ROOM / OBSERVATIONAL</p>
          <h1 id="dashboard-title">Trading system overview</h1>
          <p className="hero-copy">
            A read-only terminal for market context, scanner evidence, risk state and PAPER portfolio data.
          </p>
        </div>
        <div className="feed-state">
          <span>DATA FEED</span>
          <strong>NOT CONNECTED</strong>
          <small>Live observations will be rendered from backend contracts.</small>
        </div>
      </section>

      <section className="panel-grid" aria-label="Trading system panels">
        {panels.map((panel) => (
          <article className="panel" key={panel.title}>
            <div className="panel-heading">
              <span className="panel-index">{panel.eyebrow}</span>
              <span className="panel-status">{panel.status}</span>
            </div>
            <h2>{panel.title}</h2>
            <p className="panel-description">{panel.description}</p>
            <div className="panel-detail">{panel.detail}</div>
          </article>
        ))}
      </section>

      <section className="safety-banner" aria-label="Execution boundary">
        <div>
          <p className="section-kicker">EXECUTION BOUNDARY</p>
          <strong>RiskEngine → OMS</strong>
        </div>
        <p>Frontend actions remain observational. No screen action directly invokes broker execution.</p>
      </section>

      <footer className="footer">
        <span>Advance Trading System</span>
        <span>Backend is the source of operational truth.</span>
      </footer>
    </main>
  );
}
