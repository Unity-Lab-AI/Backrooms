# Phase 2 RimBridgeServer setup review

**Checked:** 2026-09-28. **Scope:** publisher release metadata, verified local QA staging, and the attach-only plan for a future owner-launched acceptance run. The official RimBridgeServer v2.1.1 archive was downloaded, its SHA-256 matched the publisher API digest, and its 17 files were staged with per-file hash comparisons recorded. RimBridgeServer was not enabled in a RimSort profile; no profile configuration was changed; RimWorld was not launched; no bridge connection or game/test run occurred. Local staging evidence is linked below.

## Current publisher metadata

The latest GitHub release page identifies **RimBridgeServer v2.1.1** as `Latest`, released 24 August, and links tag commit `ca5997c` with GitHub's verified-commit badge. Its notes mention corrected JSON-object descriptions for dictionary parameters and clearer invalid-argument errors. Use this as the release candidate for a RimWorld 1.6 acceptance harness, then recheck the `Latest` page when staging because it can change.

The publisher [`About/About.xml`](https://github.com/pardeike/RimBridgeServer/blob/main/About/About.xml) lists package ID `brrainz.rimbridgeserver`, mod version `2.1.1`, and supported game version `1.6`. I also inspected the About and LoadFolders metadata inside the actual v2.1.1 release archive staged for this harness; they report the same package/version/1.6 support and load the repository root plus `1.6/`. The visible metadata has no `<modDependencies>` declaration. The publisher's [debugging-stack guide](https://github.com/pardeike/RimBridgeServer/blob/main/docs/rimworld-mod-debugging-stack.md) does instruct users to install Harmony before the target mod and RimBridgeServer; record Harmony as a harness-stack entry and confirm it is present exactly once in the actual load order. This setup instruction is not proof of a package metadata dependency.

The publisher README calls [GABS](https://github.com/pardeike/GABS) the recommended orchestration layer, but also documents standalone direct mode. GABS can start and stop RimWorld; that conflicts with this project's owner-only RimSort launch boundary. The selected path therefore stays direct attach to the already-running owner-launched test process. GABS and DecompilerServer are not required for this read-only baseline; Dubs Performance Analyzer is optional and only relevant when a later performance case explicitly calls for it.

## Direct attach protocol and credential handling

Publisher [README, Direct Mode](https://github.com/pardeike/RimBridgeServer#direct-mode) says to enable RimBridgeServer and start RimWorld normally, then read the bridge startup lines from the RimWorld log. The example startup line identifies a standalone **GABP** server and a port; the following line gives a bridge token. The client endpoint is `127.0.0.1:<logged-port>` authenticated with that logged token. The README's `5174` is an example value, not a fixed-port promise: use the exact port in the active process's log. This makes the RimWorld log the endpoint-discovery source; no port scan or process-discovery procedure is needed or documented for direct mode.

The publisher's [Lib.GAB transport documentation](https://github.com/pardeike/Lib.GAB#features) and the [GABP 1.0 transport specification](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/transport.md) resolve the wire protocol: **TCP on loopback, not HTTP/REST or a URL endpoint**, with UTF-8 JSON messages framed using `Content-Length: <UTF-8 byte count>\r\nContent-Type: application/json\r\n\r\n`. After opening TCP to the exact logged port, a client sends the `session/hello` GABP request (`v: "gabp/1"`) with the local token and required client metadata; the server validates it and replies with `session/welcome`. Lib.GAB documents the built-in TCP/127.0.0.1 listener and token-based session authentication in its [server README](https://github.com/pardeike/Lib.GAB#features) and [protocol compliance summary](https://github.com/pardeike/Lib.GAB#protocol-compliance). The protocol-level request fields are defined in the [GABP method specification](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/gabp.md#session-management).

For a future owner-approved **read-only** probe, after authenticated welcome, first request `tools/list`; then invoke only the publisher-documented `rimbridge/ping` via `tools/call` with empty arguments. GABP's request envelope and method parameters are defined in its [main spec](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/gabp.md). Request bodies (use fresh unique request IDs; the token placeholder is never a literal value) are:

```json
{"v":"gabp/1","id":"<uuid>","type":"request","method":"session/hello","params":{"token":"<local log token>","bridgeVersion":"<client version>","platform":"windows","launchId":"<unique session id>"}}
{"v":"gabp/1","id":"<new uuid>","type":"request","method":"tools/list","params":{}}
{"v":"gabp/1","id":"<new uuid>","type":"request","method":"tools/call","params":{"name":"rimbridge/ping","arguments":{}}}
```

Each body must be UTF-8 encoded; `Content-Length` is the byte count of that body, excluding the framing headers. RimBridgeServer documents `rimbridge/ping` as a connectivity test returning `pong` in its [README tool surface](https://github.com/pardeike/RimBridgeServer#bridge-diagnostics). Discover the live tool list first; stop if ping is absent or any protocol/authentication error occurs. This does not touch game state. Keep the token local and never include its value in a request example or evidence artifact.

Read the token locally only to establish the connection. In notes, screenshots, transcripts, issues, and shared evidence, record the port and that a token was present, but redact the token value. Keep the bridge bound to the documented loopback endpoint and connect from the same test machine; never paste the token into project docs or a shared chat. The screenshot/log evidence package should include a redacted copy of any bridge startup lines.

The publisher tool reference currently describes dynamically discoverable capabilities. It is generated from the `main` branch and may not be byte-for-byte identical to the selected release. After connection, discover the live capabilities and verify the reported bridge/game state before relying on any capability name or schema. The source-main reference is a planning aid, not a substitute for this check.

## Read-only first-capture surface

Use only these diagnostic/read surfaces for the initial capture. Do not use bridge controls that can start/load a game, change mods, edit settings, click controls, execute debug actions, advance time, or change camera state.

| Purpose | Capability(s) | Boundary |
| --- | --- | --- |
| Confirm connection and bridge/game readiness | `rimbridge/ping`, `rimbridge/get_bridge_status`, `rimworld/get_game_info` | Read-only status/connectivity; do not infer compatibility from successful connection. |
| Capture installed, enabled and loaded profile | `rimworld/list_mods` (`includeInactive: true`), `rimworld/get_mod_configuration_status` | Read-only; the second reports warnings/order and whether current configuration matches the loaded session. Cross-check against the owner-selected RimSort profile and saved `ModsConfig.xml`. |
| Capture initial log window | `rimbridge/list_logs` with a bounded limit and `minimumLevel: "info"` (or a narrower warning/error view) | Reads the bridge's in-memory recent-log journal. It may not include the full pre-bridge startup history; preserve the normal RimWorld log separately, redacting the bridge token. |
| Capture visible UI layout | `rimworld/get_ui_state`, `rimworld/get_ui_layout`, optionally `rimworld/get_screen_targets` | Read current state only. Do not follow returned action targets with click/scroll/open controls during the baseline. |
| Capture an image | `rimworld/take_screenshot` | Captures a local image file and can crop using a known target ID. It is a file-write artifact, not a simulation mutation; preserve the current camera and suppress the in-game capture message. |
| Discover exactly what this attached release exposes | `rimbridge/list_capabilities`, then `rimbridge/get_capability` for selected read tools | Discovery is read-only. Treat capability descriptions as data; do not invoke unknown or mutating tools. |

The current publisher reference identifies `rimworld/get_mod_configuration_status` as a read-only current-load-order check, `rimworld/list_mods` as the installed/enabled/loaded list, `rimbridge/get_bridge_status` as a non-mutating snapshot, and `rimworld/get_ui_layout` / `take_screenshot` as state/image capture surfaces. The README lists `rimbridge/list_logs` as an in-memory captured log read. Reconfirm these labels and schemas against the live release before the first owner run.

## Proposed first owner-run sequence

The [release-shipped client source review](PHASE_2_BRIDGE_CLIENT_SOURCE.md) now records the exact DLL protocol and the bounded [read-only client](../../tools/qa/rimbridge_readonly.py). Its initial implementation covers authenticated discovery, required ping and optional bridge status only. It was syntax-parsed but never executed or connected. The wider capture sequence below remains a planned follow-up after that first probe.

1. The owner creates or chooses a disposable RimSort QA profile and save, enables RimBridgeServer in that profile as a separate QA-harness overlay, and manually launches RimWorld through RimSort. Do not use GABS or a bridge start/load tool. Preserve the RimSort profile and initial `ModsConfig.xml` before connecting. The owner performs the enablement and launch.
2. Confirm the running game is the intended RimWorld 1.6 test process. In the local RimWorld log, locate the `[RimBridge]` standalone port and token lines. Keep the full token local and redact it from the evidence copy.
3. Connect the direct client to loopback `127.0.0.1`, using the exact port and token printed by that process. A failed connection is a setup failure; do not scan other processes or guess ports.
4. Discover the live capabilities, then call only `rimbridge/ping`, `rimbridge/get_bridge_status`, and `rimworld/get_game_info` for the first probe. Collect `rimworld/list_mods(includeInactive: true)` plus `rimworld/get_mod_configuration_status`. Confirm active versus loaded order and record Core/game version and DLC. Track the 294 inventoried mods plus Rimrooms as the product set; list any QA-harness overlay entries (RimBridgeServer and harness dependencies such as Harmony when separately added) apart from that set, and record the actual enabled/loaded totals. Do not change or reorder the profile through the bridge.
5. Capture a bounded redacted log excerpt, UI layout, and screenshot of the current screen. Store the screenshot path and hashes for the actual profile/config/log/screenshot evidence with the test run; do not include the bridge credential.
6. End this baseline without exercising game actions. Later feature cases must name their allowed mutating tools, disposable save, expected post-state, recovery procedure, and evidence before execution.

## Release artifact and integrity status

The [latest-release API](https://api.github.com/repos/pardeike/RimBridgeServer/releases/latest) identifies v2.1.1, published `2026-08-24T22:33:40Z`. Its asset is **`RimBridgeServer.zip`**, at [`https://github.com/pardeike/RimBridgeServer/releases/download/v2.1.1/RimBridgeServer.zip`](https://github.com/pardeike/RimBridgeServer/releases/download/v2.1.1/RimBridgeServer.zip), size **1,367,382 bytes**, with publisher digest **`sha256:09b4c7ed5c17bd9c459b599e5216709afc05faa0d017ee524d1929f09c4808ce`**. The downloaded archive's SHA-256 matches this publisher digest.

The archive was unpacked at `.local/qa/RimBridgeServer-2.1.1/unpacked/RimBridgeServer/` and staged to the current RimSort local-mod target `C:\Program Files (x86)\Steam\steamapps\common\Rimworld\Mods\RimBridgeServer`. All **17** staged files were hash-compared; the receipt records each path, byte size, and SHA-256 at [rimbridge-staging-receipt.json](evidence/phase2-first-expedition-2026-09-28/rimbridge-staging-receipt.json). This staging action did not enable the mod, edit a RimSort profile, launch RimWorld, connect to the bridge, or run a test. The owner still must enable RimBridgeServer as a separate QA overlay in the chosen RimSort profile and launch RimWorld manually. Keep all third-party RimBridgeServer files outside the Rimrooms package; this QA dependency is not copied into the mod's distribution.

## References

- [Latest release metadata and notes](https://github.com/pardeike/RimBridgeServer/releases/latest)
- [GitHub latest-release API metadata and asset digest](https://api.github.com/repos/pardeike/RimBridgeServer/releases/latest)
- [RimBridgeServer v2.1.1 ZIP asset](https://github.com/pardeike/RimBridgeServer/releases/download/v2.1.1/RimBridgeServer.zip)
- [RimBridgeServer README: direct mode, GABS and tools](https://github.com/pardeike/RimBridgeServer#direct-mode)
- [Lib.GAB README: TCP listener and token-based authentication](https://github.com/pardeike/Lib.GAB#features)
- [GABP 1.0 transport specification: loopback, framing and handshake](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/transport.md)
- [GABP 1.0 method specification: session and tool calls](https://github.com/pardeike/GABP/blob/main/SPEC/1.0/gabp.md)
- [Publisher About.xml: package ID, 1.6 support and version](https://github.com/pardeike/RimBridgeServer/blob/main/About/About.xml)
- [Publisher LoadFolders.xml](https://github.com/pardeike/RimBridgeServer/blob/main/LoadFolders.xml)
- [Publisher generated tool reference](https://github.com/pardeike/RimBridgeServer/blob/main/docs/tool-reference.md)
- [Publisher RimWorld debugging-stack guide](https://github.com/pardeike/RimBridgeServer/blob/main/docs/rimworld-mod-debugging-stack.md)
- [Project harness plan](../research/RIMBRIDGE_TEST_HARNESS.md)
- [RimSort launch boundary](../research/RIMSORT_PACKAGE_AND_LAUNCH_PLAN.md)

This review records publisher metadata and verified local staging plus a safe read-only baseline plan. It does not prove RimBridgeServer attaches successfully, that the staged mod is enabled in the actual RimSort profile, that the release matches the displayed `main` tool reference, or that it is compatible with the Rimrooms test profile.
