type BacktestRun = {
  runId: string;
  strategyVersion: string;
  datasetVersion: string;
  startedAt: string;
  completedAt: string;
  status: "COMPLETED" | "FAILED" | "RUNNING";
};

type PerformanceMetrics = {
  totalReturn: number;
  maxDrawdown: number;
  sharpeRatio: number;
  tradeCount: number;
  winRate: number;
  transactionCost: number;
};

type ValidationResult = {
  validationId: string;
  method: "WALK_FORWARD" | "OOS" | "MONTE_CARLO" | "COST_SENSITIVITY" | "CAPACITY" | "REGIME";
  observations: number;
  passed: boolean;
  notes: string;
};

// Production values must be loaded from authenticated research APIs. No synthetic metrics.
const runs: BacktestRun[] = [];
const metricsByRun: Record<string, PerformanceMetrics> = {};
const validations: ValidationResult[] = [];

export default function ResearchPage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Research</p>
        <h1 style={{ margin: "8px 0" }}>Backtest & validation</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Read-only research results with explicit dataset, strategy and validation provenance.</p>
      </header>

      <section aria-labelledby="runs-title" style={{ marginTop: 28 }}>
        <h2 id="runs-title">Backtest runs</h2>
        {runs.length === 0 ? <EmptyState message="No backtest runs are available from the research backend." /> : runs.map((run) => {
          const metrics = metricsByRun[run.runId];
          return <article key={run.runId} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 16, marginBottom: 12 }}>
            <strong>{run.runId}</strong><p>{run.strategyVersion} · dataset {run.datasetVersion} · {run.status}</p>
            <small>{run.startedAt} → {run.completedAt}</small>
            {metrics && <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 16 }}>
              <Metric label="Return" value={`${metrics.totalReturn}%`} /><Metric label="Max drawdown" value={`${metrics.maxDrawdown}%`} /><Metric label="Sharpe" value={metrics.sharpeRatio.toFixed(2)} />
              <Metric label="Trades" value={String(metrics.tradeCount)} /><Metric label="Win rate" value={`${metrics.winRate}%`} /><Metric label="Transaction cost" value={`${metrics.transactionCost}%`} />
            </div>}
          </article>;
        })}
      </section>

      <section aria-labelledby="validation-title" style={{ marginTop: 28 }}>
        <h2 id="validation-title">Validation</h2>
        {validations.length === 0 ? <EmptyState message="No validation results are available. The UI will not manufacture performance or probability claims." /> : validations.map((result) => (
          <article key={result.validationId} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 16, marginBottom: 12 }}>
            <strong>{result.method}</strong><p>{result.notes}</p><small>{result.observations} observations · {result.passed ? "PASS" : "FAIL"}</small>
          </article>
        ))}
      </section>

      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 28, padding: 18 }}>
        <strong>Research-only boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>
          Backtests, validation metrics and research conclusions do not authorize live or paper orders. Execution remains behind the backend RiskEngine → OMS boundary.
        </p>
      </aside>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div style={{ border: "1px solid #242a31", borderRadius: 8, padding: 12 }}><small style={{ color: "#9ba6b2" }}>{label}</small><div style={{ marginTop: 5, fontSize: 18 }}>{value}</div></div>;
}

function EmptyState({ message }: { message: string }) {
  return <div style={{ border: "1px solid #242a31", borderRadius: 10, padding: 20, color: "#9ba6b2" }}>{message}</div>;
}
