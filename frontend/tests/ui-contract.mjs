import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");

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
