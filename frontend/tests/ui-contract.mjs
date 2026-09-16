import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const navigation = await readFile(new URL("../app/components/navigation.tsx", import.meta.url), "utf8");
const riskPage = await readFile(new URL("../app/risk/page.tsx", import.meta.url), "utf8");
const marketStatePage = await readFile(new URL("../app/market-overview/page.tsx", import.meta.url), "utf8");
const scannerPage = await readFile(new URL("../app/scanner/page.tsx", import.meta.url), "utf8");
const portfolioPage = await readFile(new URL("../app/portfolio/page.tsx", import.meta.url), "utf8");

for (const panel of ["Market State", "Scanner", "Risk", "Portfolio"]) {
  assert.match(page, new RegExp(panel));
}

assert.match(page, /PAPER MODE/);
assert.match(page, /DATA FEED/);
assert.match(page, /NOT CONNECTED/);
assert.match(page, /RiskEngine → OMS/);
assert.match(page, /No screen action directly invokes broker execution/);
assert.match(page, /Backend is the source of operational truth/);
assert.match(styles, /\.panel-grid/);
assert.match(styles, /@media \(max-width: 560px\)/);

assert.match(navigation, /\["Risk", "\/risk"\]/);
for (const [source, endpoint] of [
  [riskPage, "/api/v1/risk"],
  [marketStatePage, "/api/v1/market-state"],
  [scannerPage, "/api/v1/scanner"],
  [portfolioPage, "/api/v1/portfolio"],
]) {
  assert.match(source, new RegExp(endpoint.replaceAll("/", "\\/")));
  assert.match(source, /cache: "no-store"/);
  assert.match(source, /backend_unreachable/);
  assert.match(source, /available: false/);
  assert.match(source, /data: null/);
}
assert.match(riskPage, /RiskEngine remains the hard pre-trade gate/);
assert.match(marketStatePage, /does not synthesize values/);
assert.match(scannerPage, /never submit orders/);
assert.match(portfolioPage, /cannot create, amend, close, or liquidate/);
