type AuditEvent = {
  eventId: string;
  timestamp: string;
  eventType: string;
  entityId: string;
  executionAuthority: false;
  explanation: string;
};

type DecisionEvidence = {
  recordId: string;
  decisionKind: "SCANNER" | "SCORE" | "PROBABILITY" | "RISK";
  decisionId: string;
  observedAt: string;
  explanation: string;
  evidenceCount: number;
  executionAuthority: false;
};

// Read-only contracts. Production records must come from authenticated journal/audit APIs.
const auditEvents: AuditEvent[] = [];
const decisionEvidence: DecisionEvidence[] = [];

export default function JournalPage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Journal</p>
        <h1 style={{ margin: "8px 0" }}>Audit & decision evidence</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Append-only observations for review and research.</p>
      </header>

      <section aria-labelledby="events-title" style={{ marginTop: 28 }}>
        <h2 id="events-title">Audit events</h2>
        {auditEvents.length === 0 ? <EmptyState message="No audit events available from the backend journal." /> : auditEvents.map((event) => (
          <article key={event.eventId} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 16, marginBottom: 12 }}>
            <strong>{event.eventType}</strong><p>{event.explanation}</p><small>{event.timestamp} · {event.entityId}</small>
          </article>
        ))}
      </section>

      <section aria-labelledby="evidence-title" style={{ marginTop: 28 }}>
        <h2 id="evidence-title">Decision evidence</h2>
        {decisionEvidence.length === 0 ? <EmptyState message="No decision evidence available. The UI will not reconstruct or invent historical decisions." /> : decisionEvidence.map((record) => (
          <article key={record.recordId} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 16, marginBottom: 12 }}>
            <strong>{record.decisionKind}</strong><p>{record.explanation}</p><small>{record.observedAt} · evidence: {record.evidenceCount}</small>
          </article>
        ))}
      </section>

      <aside style={{ border: "1px solid #3a3030", borderRadius: 10, marginTop: 28, padding: 18 }}>
        <strong>Audit-only boundary</strong>
        <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>
          Journal records are immutable observations. They cannot authorize, submit, amend, cancel, or mutate orders.
        </p>
      </aside>
    </main>
  );
}

function EmptyState({ message }: { message: string }) {
  return <div style={{ border: "1px solid #242a31", borderRadius: 10, padding: 20, color: "#9ba6b2" }}>{message}</div>;
}
