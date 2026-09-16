import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const navigation = await readFile(new URL("../app/components/navigation.tsx", import.meta.url), "utf8");
const riskPage = await readFile(new URL("../app/risk/page.tsx", import.meta.url), "utf8");

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
assert.match(riskPage, /\/api\/v1\/risk/);
assert.match(riskPage, /cache: "no-store"/);
assert.match(riskPage, /backend_unreachable/);
assert.match(riskPage, /RiskEngine remains the hard pre-trade gate/);
