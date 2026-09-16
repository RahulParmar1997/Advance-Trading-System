import { Navigation } from "../components/navigation";

async function getMarketStateView() {
  const baseUrl = process.env.ATS_BACKEND_URL ?? "http://backend:8000";
  try {
    const response = await fetch(`${baseUrl}/api/v1/market-state`, { cache: "no-store" });
    if (!response.ok) return { available: false, reason: `backend_http_${response.status}`, data: null };
    const payload: unknown = await response.json();
    if (!payload || typeof payload !== "object") return { available: false, reason: "invalid_backend_payload", data: null };
    const view = payload as { available?: unknown; reason?: unknown; data?: unknown };
    return {
      available: view.available === true,
      reason: typeof view.reason === "string" ? view.reason : "invalid_backend_payload",
      data: view.available === true ? view.data ?? null : null,
    };
  } catch {
    return { available: false, reason: "backend_unreachable", data: null };
  }
}

export default async function MarketOverviewPage() {
  const marketState = await getMarketStateView();

  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <Navigation />
      <header style={{ borderBottom: "1px solid #242a31", padding: "24px 0 20px" }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Read-only market overview</p>
        <h1 style={{ margin: "8px 0", fontSize: 34 }}>Market State</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Market observations come from the backend contract; the frontend does not synthesize values.</p>
      </header>
      <section aria-label="Market state observation" style={{ marginTop: 28 }}>
        <article style={{ background: "#11151a", border: "1px solid #242a31", borderRadius: 10, padding: 24 }}>
          <p style={{ color: "#697582", fontSize: 12, margin: "0 0 8px", textTransform: "uppercase" }}>Provider state</p>
          <strong>{marketState.available ? "AVAILABLE" : "UNAVAILABLE"}</strong>
          <p style={{ color: "#9ba6b2", lineHeight: 1.5 }}>Reason: {marketState.reason}</p>
          <pre style={{ background: "#0b0e12", borderRadius: 8, overflowX: "auto", padding: 16 }}>{marketState.data === null ? "No market-state observation available." : JSON.stringify(marketState.data, null, 2)}</pre>
        </article>
      </section>
      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 24, padding: 18 }}>
        <strong>Execution boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>
          This route only renders market-state observations. Execution remains a backend RiskEngine → OMS responsibility.
        </p>
      </aside>
    </main>
  );
}
