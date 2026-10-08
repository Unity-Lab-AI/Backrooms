#!/usr/bin/env node
'use strict';
/**
 * post-tool-stream-log.cjs — PostToolUse:Bash. Feeds the stream overlay's script log.
 *
 * Owner: "a script log only showing the scripts u run with no pi and no names and nothing
 * personal of ours". From each Bash command this keeps ONLY:
 *   - script file basenames  (letters, digits, - and _ then .py/.cjs/.ps1/.sh)
 *   - RimBridge command names (rimworld/<snake_case>)
 * Never the path, never an argument, never free text. Inline code (python - <<EOF) logs nothing.
 * Appends {id, ts, items} to .claude/.stream-log.jsonl (gitignored). Never blocks, never fails
 * the tool call: any error is swallowed.
 */
const fs = require('fs');
const path = require('path');

const LOG = path.join(__dirname, '..', '.stream-log.jsonl');
const KEEP = 400;
// Plumbing that would only add noise to the log.
const SKIP = new Set(['bridge.py']);

function items(cmd) {
  const out = [];
  const seen = new Set();
  const add = (s) => { if (!seen.has(s) && !SKIP.has(s)) { seen.add(s); out.push(s); } };
  // Heredoc bodies are inline code, not scripts we ran: cut them off before matching.
  const head = cmd.split(/<<-?\s*['"]?\w+['"]?/)[0];
  for (const m of head.matchAll(/(?:^|[\s/\\"'])([A-Za-z0-9_-]{1,40}\.(?:py|cjs|ps1|sh))(?=[\s"';|&)]|$)/g)) add(m[1]);
  for (const m of head.matchAll(/\brimworld\/([a-z_]{2,48})\b/g)) add('rimworld/' + m[1]);
  return out;
}

let raw = '';
process.stdin.on('data', (c) => { raw += c; });
process.stdin.on('end', () => {
  try {
    const j = JSON.parse(raw || '{}');
    const cmd = String((j.tool_input && j.tool_input.command) || '');
    const found = items(cmd);
    if (!found.length) return;
    let rows = [];
    try { rows = fs.readFileSync(LOG, 'utf8').split('\n').filter(Boolean); } catch (e) { /* first line */ }
    let last = 0;
    if (rows.length) { try { last = JSON.parse(rows[rows.length - 1]).id || 0; } catch (e) { last = rows.length; } }
    rows.push(JSON.stringify({ id: last + 1, ts: Date.now(), items: found }));
    if (rows.length > KEEP) rows = rows.slice(rows.length - KEEP);
    fs.writeFileSync(LOG, rows.join('\n') + '\n');
  } catch (e) { /* the log is cosmetic: never disturb the tool call */ }
});
