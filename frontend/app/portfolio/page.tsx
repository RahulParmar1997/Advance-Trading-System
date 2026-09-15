type Position = {
  instrument: string;
  side: "LONG" | "SHORT";
  quantity: number;
  averagePrice: number | null;
  markPrice: number | null;
  realizedPnl: number | null;
  unrealizedPnl: number | null;
  exposure: number | null;
};

type PortfolioRisk = {
  netExposure: number | null;
  grossExposure: number | null;
  dailyPnl: number | null;
  riskState: "CLEAR" | "BLOCKED" | "UNAVAILABLE";
};

// Read-only backend contracts. Production values must come from authenticated portfolio/risk APIs.
const positions: Position[] = [];
const risk: PortfolioRisk = {
  netExposure: null,
  grossExposure: null,
  dailyPnl: null,
  riskState: "UNAVAILABLE",
};

function display(value: number | null): string {
  return value === null ? "—" : value.toFixed(2);
}

export default function PortfolioPage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Portfolio</p>
        <h1 style={{ margin: "8px 0" }}>Positions & risk</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Read-only state from the portfolio and risk boundaries.</p>
      </header>

      <section aria-label="Portfolio risk metrics" style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", marginTop: 28 }}>
        <Metric title="Net exposure" value={display(risk.netExposure)} />
        <Metric title="Gross exposure" value={display(risk.grossExposure)} />
        <Metric title="Daily P&L" value={display(risk.dailyPnl)} />
        <Metric title="Risk state" value={risk.riskState} />
      </section>

      <section aria-labelledby="positions-title" style={{ marginTop: 28 }}>
        <h2 id="positions-title">Open positions</h2>
        {positions.length === 0 ? (
          <div style={{ border: "1px solid #242a31", borderRadius: 10, padding: 20, color: "#9ba6b2" }}>
            No position observations available. The UI will not infer holdings or P&L from market prices.
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse", width: "100%" }}>
              <thead><tr><th>Instrument</th><th>Side</th><th>Qty</th><th>Avg</th><th>Mark</th><th>Realized</th><th>Unrealized</th><th>Exposure</th></tr></thead>
              <tbody>{positions.map((position) => <tr key={position.instrument}><td>{position.instrument}</td><td>{position.side}</td><td>{position.quantity}</td><td>{display(position.averagePrice)}</td><td>{display(position.markPrice)}</td><td>{display(position.realizedPnl)}</td><td>{display(position.unrealizedPnl)}</td><td>{display(position.exposure)}</td></tr>)}</tbody>
            </table>
          </div>
        )}
      </section>

      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 28, padding: 18 }}>
        <strong>Execution boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>This page cannot create, amend, close, or liquidate a position. Execution authority remains backend-only through RiskEngine → OMS.</p>
      </aside>
    </main>
  );
}

function Metric({ title, value }: { title: string; value: string }) {
  return <article style={{ background: "#11151a", border: "1px solid #242a31", borderRadius: 10, padding: 20 }}><p style={{ color: "#697582", fontSize: 12, margin: "0 0 8px", textTransform: "uppercase" }}>{title}</p><p style={{ fontSize: 21, margin: 0 }}>{value}</p></article>;
}
