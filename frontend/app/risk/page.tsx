import { Navigation } from "../components/navigation";

async function getRiskView() {
  const baseUrl = process.env.ATS_BACKEND_URL ?? "http://backend:8000";
  try {
    const response = await fetch(`${baseUrl}/api/v1/risk`, { cache: "no-store" });
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

export default async function RiskPage() {
  const risk = await getRiskView();

  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <Navigation />
      <header style={{ borderBottom: "1px solid #242a31", padding: "24px 0 20px" }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Risk</p>
        <h1 style={{ margin: "8px 0", fontSize: 34 }}>Risk guardrails</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Read-only observations from the backend risk boundary.</p>
      </header>
      <section aria-label="Risk observation" style={{ marginTop: 28 }}>
        <article style={{ background: "#11151a", border: "1px solid #242a31", borderRadius: 10, padding: 24 }}>
          <p style={{ color: "#697582", fontSize: 12, margin: "0 0 8px", textTransform: "uppercase" }}>Provider state</p>
          <strong>{risk.available ? "AVAILABLE" : "UNAVAILABLE"}</strong>
          <p style={{ color: "#9ba6b2", lineHeight: 1.5 }}>Reason: {risk.reason}</p>
          <pre style={{ background: "#0b0e12", borderRadius: 8, overflowX: "auto", padding: 16 }}>{risk.data === null ? "No risk observation available." : JSON.stringify(risk.data, null, 2)}</pre>
        </article>
      </section>
      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 24, padding: 18 }}>
        <strong>Execution boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>This page cannot approve or submit orders. RiskEngine remains the hard pre-trade gate and OMS remains the execution workflow.</p>
      </aside>
    </main>
  );
}
