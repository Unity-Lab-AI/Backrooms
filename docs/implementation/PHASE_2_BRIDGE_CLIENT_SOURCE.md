# Phase 2 RimBridge direct-client source review

**Checked:** 2026-09-28. **Scope:** release-shipped RimBridgeServer/GABP source behavior and a bounded read-only QA client. This is static inspection of the staged v2.1.1 assemblies. The client has not been connected to a live bridge; RimWorld has not been launched or tested here.

## Inspected release assemblies

The reviewed files are under `.local/qa/RimBridgeServer-2.1.1/unpacked/RimBridgeServer/1.6/Assemblies/` from the staged v2.1.1 archive. SHA-256 values:

| Assembly | SHA-256 |
| --- | --- |
| `RimBridgeServer.dll` | `BDD0AD19036A3554EFF4ABEB2A5F35E4D13C0E8A4559985BDC13340589F913E0` |
| `Lib.GAB.dll` | `BE3AECCABD93C29271425F146C0EAAD8E37DB66C08F9883A4A5A4A44B9E51014` |
| `Gabp.Runtime.dll` | `D548E8665EFB033E36B5985738D865BCBAF50F9384674D0340B5C5C834FF7696` |

The types below were inspected from those exact local files with ILSpy command-line decompilation to standard output; no decompiled third-party source was saved into the Rimrooms package.

## Source-confirmed startup and endpoint

`RimBridgeServer.RimBridgeStartup` builds the GABP server with `UsePortIfNotSet(5174)`. The fallback applies only when no port was already selected; direct clients must use the port written by the running server, not assume 5174. On a successful standalone start, the exact log prefixes are:

```text
[RimBridge] GABP server running standalone on port {Port}
[RimBridge] Bridge token: {Token}
```

The server logs a different prefix when connected to GABS (`[RimBridge] GABP server connected to GABS on port {Port}`) and logs `[RimBridge] Failed to start server: ...` on start failure. The direct client therefore rejects a log whose latest recognized server-start event is GABS or a startup failure, and requires a token line after the latest standalone line.

`Lib.GAB.Transport.TcpTransport.StartAsync` binds `TcpListener` to `IPAddress.Loopback`; the client fixes the destination to `127.0.0.1` and accepts no host or port override. `TcpConnection.SendMessageAsync` serializes JSON to UTF-8 and frames it with `Content-Length: {UTF-8 byte length}\r\nContent-Type: application/json\r\n\r\n`. The client uses byte framing, caps headers and bodies, and writes JSON with ASCII escaping so its declared byte length is exact.

## Source-confirmed GABP v1 exchange

`Gabp.Runtime.GabpProtocol` defines protocol version `gabp/1`, request/response/event envelope types, and methods `session/hello`, `tools/list`, and `tools/call`. `GabpServer.HandleRequestAsync` permits the session handshake before authentication and rejects other requests until a session is established. `HandleSessionHelloAsync` checks `SessionHelloParams.Token`; the required handshake fields are `token`, `bridgeVersion`, `platform`, and `launchId`. A successful client sequence is therefore:

1. TCP connect to `127.0.0.1:<port parsed from the explicit log>`.
2. Send one `gabp/1` request for `session/hello`; require a matching response ID and no protocol error.
3. Send `tools/list`; extract the returned names and invoke only selected names in the fixed allowlist below.
4. Send `tools/call` with `params.name` and `params.arguments`, sequentially, with unique request IDs.

The concrete request envelopes used by the client are:

```json
{"v":"gabp/1","id":"<uuid>","type":"request","method":"session/hello","params":{"token":"<read from explicit log, never emitted>","bridgeVersion":"RimroomsReadOnlyQA/1","platform":"windows","launchId":"<uuid>"}}
{"v":"gabp/1","id":"<uuid>","type":"request","method":"tools/list","params":{}}
{"v":"gabp/1","id":"<uuid>","type":"request","method":"tools/call","params":{"name":"rimbridge/ping","arguments":{}}}
```

The client reads one response frame at a time, accepts only `gabp/1` response envelopes with the expected ID, and fails closed on malformed frames, authentication/protocol errors, mismatched IDs, oversized data, or timeouts. It does not implement generic GABP methods or accept caller-supplied tool names/arguments.

`RimBridgeServer.LegacyToolExecution.InvokeAlias` represents an operation failure as a normal tool result with `success: false`, `message`, `exception`, and an `operation` snapshot; the GABP envelope itself can still be a successful response. The utility treats `success: false`, `operation.success: false`, and explicit `isError: true`/`is_error: true` result markers as failed calls. The `isError` checks are defensive for a changed result shape; the reviewed legacy bridge path uses `success`.

## First-probe read-only surface

The initial utility intentionally supports only the handshake, `tools/list`, and these two calls. Their names and treatment are confirmed against `RimBridgeServer.RimBridgeTools` in the reviewed release assembly. Calls are made only if the exact tool name appears in the live `tools/list` result.

| CLI selector | Tool | Fixed arguments | Source treatment |
| --- | --- | --- | --- |
| `ping` | `rimbridge/ping` | `{}` | Explicit diagnostic/read-only connectivity probe. |
| `status` | `rimbridge/get_bridge_status` | `{}` | Explicit status/read-only surface. |

There is no CLI parameter for a tool name, raw JSON, arbitrary arguments, endpoint, or remote host. The selector map is the entire call surface. Game information, mod/configuration inventory, logs, and UI captures remain separate follow-up work; no screenshot call is included because this utility captures bounded sanitized JSON only.

Direct mode requires `--select ping`; if the live list omits `rimbridge/ping`, the client stops before invoking other tools. It sends ping before status regardless of selector order. A requested tool missing from the live list or any call-level error produces a nonzero exit status and a sanitized evidence record.

## Client safeguards and evidence limits

The new utility is `tools/qa/rimbridge_readonly.py` (Python 3.10+). It requires an explicit PID for the owner-launched process and an explicit log path; an operator may obtain the PID from the OS after the owner reports launching the QA game, without asking the owner to type it in chat. Before connecting, it uses Windows process-query APIs to confirm the PID is live and its executable basename is `RimWorldWin64.exe` or `RimWorld.exe`; it requires the explicit log file's last-write time not to predate that process start (with a small clock tolerance), and requires its latest recognized bridge start to be standalone with a following token line. It rechecks the same PID and process start immediately before opening the socket. It rejects a log over the read cap when the relevant startup record is not present in its bounded tail. It never scans processes, searches for logs, probes ports, starts processes, edits a profile, or changes game state.

These checks do **not** prove that the supplied log belongs to the supplied process or that the listener on the logged port is owned by that PID. An operator must pair the explicit PID and current log with the same manually launched QA session; after the owner reports launching the game, the operator can read the PID from the OS. A successful token handshake is evidence that a GABP server accepted the log token at the loopback endpoint; it is not process-ownership proof and is not compatibility evidence.

The client reads the credential only to authenticate. It does not print or serialize the token. Evidence records the PID, executable basename, parsed port, token-present boolean, requested selectors, live allowlisted tool availability, and selected read results. A recursive sanitizer redacts token/secret/auth/password fields, the exact local token, bearer strings, and RimBridge token log lines; raw startup logs are never copied. Result depth, strings, arrays, frame sizes, timeouts, and total output size are bounded. Output creation is exclusive so an existing evidence path cannot be overwritten.

For a future owner-operated capture (not run as part of this review), use Python 3.10+ on the Windows test host and an explicit current process/log/output pair, for example:

```powershell
python tools/qa/rimbridge_readonly.py --pid 12345 --log "C:\path\to\Player.log" --output "C:\path\to\capture.json" --connect --select ping --select status
```

Without `--connect`, the command only validates the explicit process/log pairing and writes a preflight record. This source review did not run even that preflight. The client received a Python AST syntax parse only; it was not executed, connected to a listener, tested, or used to start RimWorld. A later owner-run connection must still be recorded as QA evidence and must not be described as a successful Rimrooms profile or feature test.

## Primary sources

- Staged local release source: `.local/qa/RimBridgeServer-2.1.1/unpacked/RimBridgeServer/1.6/Assemblies/RimBridgeServer.dll`, `Lib.GAB.dll`, `Gabp.Runtime.dll` (hashes above).
- [Project bridge setup review](PHASE_2_BRIDGE_SETUP_REVIEW.md).
- [Project test harness plan](../research/RIMBRIDGE_TEST_HARNESS.md).
- [RimBridgeServer release v2.1.1](https://github.com/pardeike/RimBridgeServer/releases/tag/v2.1.1).
- [GABP 1.0 method specification](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/gabp.md).
- [GABP 1.0 transport specification](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/transport.md).
