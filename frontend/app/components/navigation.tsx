const links = [
  ["Overview", "/market-overview"],
  ["Scanner", "/scanner"],
  ["Risk", "/risk"],
  ["Portfolio", "/portfolio"],
  ["Derivatives", "/derivatives"],
  ["Journal", "/journal"],
  ["Research", "/research"],
] as const;

export function Navigation() {
  return (
    <nav aria-label="Trading terminal navigation" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
      {links.map(([label, href]) => (
        <a key={href} href={href} style={{ border: "1px solid #242a31", borderRadius: 8, padding: "8px 12px", color: "#b7c0ca", fontSize: 13 }}>
          {label}
        </a>
      ))}
    </nav>
  );
}
