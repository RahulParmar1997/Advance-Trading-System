type ScannerCandidate = {
  instrument: string;
  timeframeSeconds: number;
  rule: string;
  matched: boolean;
  score: number | null;
  explanation: string;
};

// Read-only boundary: production values must be supplied by a backend scanner API.
const candidates: ScannerCandidate[] = [];

export default function ScannerPage() {
  return (
    <main style={{ margin: "0 auto", maxWidth: 1200, padding: 32 }}>
      <header style={{ borderBottom: "1px solid #242a31", paddingBottom: 20 }}>
        <p style={{ margin: 0, fontSize: 12, letterSpacing: 1.4, textTransform: "uppercase" }}>Scanner</p>
        <h1 style={{ margin: "8px 0" }}>Evidence-backed opportunities</h1>
        <p style={{ color: "#9ba6b2", margin: 0 }}>Candidates are observations, not execution instructions.</p>
      </header>

      <section aria-label="Scanner candidates" style={{ marginTop: 24 }}>
        {candidates.length === 0 ? (
          <div style={{ border: "1px solid #242a31", borderRadius: 10, padding: 24 }}>
            <strong>No scanner observations available</strong>
            <p style={{ color: "#9ba6b2", lineHeight: 1.5, marginBottom: 0 }}>
              Waiting for an authenticated backend scanner feed. The UI intentionally does not fabricate candidates,
              probabilities, scores, or market data.
            </p>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 12 }}>
            {candidates.map((candidate) => (
              <article key={`${candidate.instrument}-${candidate.timeframeSeconds}-${candidate.rule}`} style={{ border: "1px solid #242a31", borderRadius: 10, padding: 18 }}>
                <strong>{candidate.instrument}</strong>
                <p>{candidate.rule}</p>
                <small>{candidate.explanation}</small>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
