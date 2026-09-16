import { Navigation } from "../components/navigation";

async function getPortfolioView() {
  const baseUrl = process.env.ATS_BACKEND_URL ?? "http://backend:8000";
  try {
    const response = await fetch(`${baseUrl}/api/v1/portfolio`, { cache: "no-store" });
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

export default async function PortfolioPage() {
  const portfolio = await getPortfolioView();

  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <Navigation />
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Portfolio</p>
        <h1 style={{ margin: "8px 0" }}>Positions & risk</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Read-only state from the backend portfolio boundary.</p>
      </header>

      <section aria-label="Portfolio observation" style={{ marginTop: 28 }}>
        <article style={{ background: "#11151a", border: "1px solid #242a31", borderRadius: 10, padding: 24 }}>
          <p style={{ color: "#697582", fontSize: 12, margin: "0 0 8px", textTransform: "uppercase" }}>Provider state</p>
          <strong>{portfolio.available ? "AVAILABLE" : "UNAVAILABLE"}</strong>
          <p style={{ color: "#9ba6b2", lineHeight: 1.5 }}>Reason: {portfolio.reason}</p>
          <pre style={{ background: "#0b0e12", borderRadius: 8, overflowX: "auto", padding: 16 }}>{portfolio.data === null ? "No portfolio observation available." : JSON.stringify(portfolio.data, null, 2)}</pre>
        </article>
      </section>

      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 28, padding: 18 }}>
        <strong>Execution boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>
          This page cannot create, amend, close, or liquidate a position. Execution authority remains backend-only through RiskEngine → OMS.
        </p>
      </aside>
    </main>
  );
}
