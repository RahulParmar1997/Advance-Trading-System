type OrderState = "SCANNED" | "CANDIDATE" | "QUALIFIED" | "RISK_CHECK" | "ORDER_PENDING" | "PARTIALLY_FILLED" | "FILLED" | "MANAGED" | "SCALE_OUT" | "EXIT" | "CLOSED";

type PaperOrder = {
  orderId: string;
  instrument: string;
  side: "BUY" | "SELL";
  quantity: number;
  state: OrderState;
  averageFillPrice: number | null;
};

// Read-only backend contract. The frontend has no broker mutation methods.
const orders: PaperOrder[] = [];

const stateOrder: OrderState[] = [
  "SCANNED", "CANDIDATE", "QUALIFIED", "RISK_CHECK", "ORDER_PENDING",
  "PARTIALLY_FILLED", "FILLED", "MANAGED", "SCALE_OUT", "EXIT", "CLOSED",
];

export default function PaperTradingPage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Paper trading</p>
        <h1 style={{ margin: "8px 0" }}>Order & position state</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Observational terminal. Order authority stays in the backend.</p>
      </header>

      <section aria-labelledby="orders-title" style={{ marginTop: 28 }}>
        <h2 id="orders-title">Orders</h2>
        {orders.length === 0 ? (
          <EmptyState message="No PAPER orders available. The UI will not create synthetic orders or fills." />
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse", width: "100%" }}>
              <thead><tr><th>Order</th><th>Instrument</th><th>Side</th><th>Qty</th><th>State</th><th>Avg fill</th></tr></thead>
              <tbody>{orders.map((order) => <tr key={order.orderId}><td>{order.orderId}</td><td>{order.instrument}</td><td>{order.side}</td><td>{order.quantity}</td><td>{order.state}</td><td>{order.averageFillPrice === null ? "—" : order.averageFillPrice.toFixed(2)}</td></tr>)}</tbody>
            </table>
          </div>
        )}
      </section>

      <section aria-labelledby="lifecycle-title" style={{ marginTop: 28 }}>
        <h2 id="lifecycle-title">Canonical lifecycle</h2>
        <ol style={{ color: "#9ba6b2", lineHeight: 1.8 }}>{stateOrder.map((state) => <li key={state}>{state}</li>)}</ol>
      </section>

      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 28, padding: 18 }}>
        <strong>Safety boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>
          No order buttons are exposed here. Any future order action must pass backend RiskEngine → OMS before reaching an execution adapter.
        </p>
      </aside>
    </main>
  );
}

function EmptyState({ message }: { message: string }) {
  return <div style={{ border: "1px solid #242a31", borderRadius: 10, padding: 20, color: "#9ba6b2" }}>{message}</div>;
}
