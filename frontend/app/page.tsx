const panels = [
  ["Market State", "Session, regime and data freshness"],
  ["Scanner", "Evidence-backed candidate opportunities"],
  ["Risk", "Pre-trade controls and current guardrails"],
  ["Portfolio", "PAPER positions, exposure and P&L"],
] as const;

export default function HomePage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 24 }}>
        <p style={{ margin: 0, fontSize: 13, letterSpacing: 1.5, textTransform: "uppercase" }}>Advance Trading System</p>
        <h1 style={{ margin: "10px 0 8px", fontSize: 36 }}>Market intelligence terminal</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>India-focused analytics with PAPER-first execution safety.</p>
      </header>

      <section aria-label="System panels" style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginTop: 28 }}>
        {panels.map(([title, description]) => (
          <article key={title} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 20, background: "#11151a" }}>
            <h2 style={{ fontSize: 18, margin: "0 0 8px" }}>{title}</h2>
            <p style={{ color: "#9ba6b2", lineHeight: 1.5, margin: 0 }}>{description}</p>
          </article>
        ))}
      </section>

      <footer style={{ color: "#697582", fontSize: 13, marginTop: 32 }}>
        UI is observational. Order execution remains behind the backend RiskEngine → OMS boundary.
      </footer>
    </main>
  );
}
