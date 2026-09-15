type OptionRow = {
  strike: number;
  callIv: number | null;
  callDelta: number | null;
  putIv: number | null;
  putDelta: number | null;
};

type FuturesBasis = {
  symbol: string;
  futuresPrice: number | null;
  spotPrice: number | null;
  basis: number | null;
  basisPercent: number | null;
};

// Read-only contracts. Production values must come from an authenticated backend analytics API.
const optionRows: OptionRow[] = [];
const futures: FuturesBasis[] = [];

function display(value: number | null): string {
  return value === null ? "—" : value.toFixed(2);
}

export default function DerivativesPage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Derivatives</p>
        <h1 style={{ margin: "8px 0" }}>Options & futures analytics</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Greeks, implied volatility and basis are analytics only.</p>
      </header>

      <section style={{ marginTop: 28 }} aria-labelledby="option-chain-title">
        <h2 id="option-chain-title">Option chain</h2>
        {optionRows.length === 0 ? (
          <EmptyState message="Waiting for an authenticated option-chain feed. No strikes or Greeks are fabricated." />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse", width: "100%" }}>
              <thead><tr><th>Strike</th><th>Call IV</th><th>Call Δ</th><th>Put IV</th><th>Put Δ</th></tr></thead>
              <tbody>{optionRows.map((row) => <tr key={row.strike}><td>{row.strike}</td><td>{display(row.callIv)}</td><td>{display(row.callDelta)}</td><td>{display(row.putIv)}</td><td>{display(row.putDelta)}</td></tr>)}</tbody>
            </table>
          </div>
        )}
      </section>

      <section style={{ marginTop: 28 }} aria-labelledby="futures-title">
        <h2 id="futures-title">Futures basis</h2>
        {futures.length === 0 ? (
          <EmptyState message="Waiting for authenticated spot/futures observations. No basis values are inferred." />
        ) : (
          <div style={{ display: "grid", gap: 12 }}>{futures.map((row) => <article key={row.symbol} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 18 }}><strong>{row.symbol}</strong><p>Basis: {display(row.basis)} ({display(row.basisPercent)}%)</p></article>)}</div>
        )}
      </section>

      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 28, padding: 18 }}>
        <strong>Execution boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>This dashboard cannot submit, amend, cancel, or authorize orders. Execution remains behind RiskEngine → OMS.</p>
      </aside>
    </main>
  );
}

function EmptyState({ message }: { message: string }) {
  return <div style={{ border: "1px solid #242a31", borderRadius: 10, padding: 20, color: "#9ba6b2" }}>{message}</div>;
}
