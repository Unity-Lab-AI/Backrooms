#!/usr/bin/env python3
"""Owner-operated, direct-mode read-only RimBridgeServer evidence client.

Requires an explicit PID for the owner-launched RimWorld process and current log path. It never discovers,
starts, configures, or controls a process, and only calls fixed read surfaces.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import socket
import sys
import time
import uuid


PROTOCOL_VERSION = "gabp/1"
CLIENT_VERSION = "RimroomsReadOnlyQA/2"
MAX_LOG_BYTES = 32 * 1024 * 1024
MAX_HEADER_BYTES = 8 * 1024
MAX_FRAME_BYTES = 1024 * 1024
MAX_EVIDENCE_BYTES = 1024 * 1024
MAX_EVENTS_PER_RESPONSE = 20
MAX_COLLECTION_ITEMS = 512  # Includes every entry in the 296-entry QA profile.
MAX_SANITIZED_NODES = 50000

STANDALONE_RE = re.compile(
    r"^\[RimBridge\] GABP server running standalone on port (\d+)\s*$"
)
GABS_RE = re.compile(
    r"^\[RimBridge\] GABP server connected to GABS on port (\d+)\s*$"
)
FAILED_RE = re.compile(r"^\[RimBridge\] Failed to start server:")
TOKEN_RE = re.compile(r"^\[RimBridge\] Bridge token:\s*(\S+)\s*$")
BEARER_RE = re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/-]+=*")
BRIDGE_TOKEN_LINE_RE = re.compile(
    r"(?im)(\[RimBridge\]\s+Bridge token:\s*)\S+"
)
SECRET_KEY_RE = re.compile(
    r"(?i)(token|authorization|secret|password|credential|api[_-]?key)"
)

# Fixed startup observations only; no caller-supplied tool names or arguments.
READ_TOOLS = {
    "ping": ("rimbridge/ping", {}),
    "status": ("rimbridge/get_bridge_status", {}),
    "game": ("rimworld/get_game_info", {}),
    "mods": ("rimworld/get_mod_configuration_status", {}),
    "logs": ("rimbridge/list_logs", {"limit": 50, "minimumLevel": "warning", "afterSequence": 0}),
}


class ClientError(Exception):
    """Expected fail-closed validation or protocol error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def inspect_process(pid: int) -> tuple[str, float]:
    """Return executable basename and process start Unix time on Windows."""
    if os.name != "nt":
        raise ClientError("Windows process identity checks are required; no connection attempted")
    if pid <= 0:
        raise ClientError("PID must be a positive owner-provided process ID")

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
    ]
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        raise ClientError("Could not query the supplied PID; verify it is live and accessible")
    try:
        image = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(image))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, image, ctypes.byref(size)):
            raise ClientError("Could not read executable identity for the supplied PID")
        creation, exit_time, kernel_time, user_time = FILETIME(), FILETIME(), FILETIME(), FILETIME()
        if not kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel_time),
            ctypes.byref(user_time),
        ):
            raise ClientError("Could not read start time for the supplied PID")
        ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        started_unix = ticks / 10_000_000 - 11_644_473_600
        basename = Path(image.value[: size.value]).name
        if basename.casefold() not in {"rimworldwin64.exe", "rimworld.exe"}:
            raise ClientError("The supplied PID is not a recognized RimWorld executable")
        return basename, started_unix
    finally:
        kernel32.CloseHandle(handle)


def read_active_endpoint(log_path: Path, process_started_unix: float) -> tuple[int, str]:
    """Parse only a recent, explicit standalone startup and following token."""
    try:
        resolved = log_path.expanduser().resolve(strict=True)
        stat = resolved.stat()
    except OSError:
        raise ClientError("The explicit log path does not identify a readable existing file") from None
    if not resolved.is_file():
        raise ClientError("The explicit log path is not a regular file")
    if stat.st_mtime < process_started_unix - 5:
        raise ClientError("The explicit log predates the supplied process; refusing a stale-log attach")
    try:
        with resolved.open("rb") as stream:
            stream.seek(max(0, stat.st_size - MAX_LOG_BYTES))
            raw = stream.read(MAX_LOG_BYTES + 1)
    except OSError:
        raise ClientError("Could not read the explicit log path") from None
    if len(raw) > MAX_LOG_BYTES:
        raw = raw[-MAX_LOG_BYTES:]
    text = raw.decode("utf-8", errors="replace")
    if len(raw) == MAX_LOG_BYTES and "[RimBridge]" not in text:
        raise ClientError("The bounded log tail has no bridge startup record; refusing attach")

    lines = text.splitlines()
    events: list[tuple[int, str, int | None]] = []
    for index, line in enumerate(lines):
        standalone = STANDALONE_RE.match(line)
        gabs = GABS_RE.match(line)
        if standalone:
            events.append((index, "standalone", int(standalone.group(1))))
        elif gabs:
            events.append((index, "gabs", int(gabs.group(1))))
        elif FAILED_RE.match(line):
            events.append((index, "failed", None))
    if not events:
        raise ClientError("No recognized current RimBridge startup line was found in the explicit log")
    event_index, event_kind, port = events[-1]
    if event_kind != "standalone" or port is None:
        raise ClientError("The latest bridge start is not standalone; direct attach was refused")
    if not 1 <= port <= 65535:
        raise ClientError("The logged bridge port is outside the valid TCP port range")

    token = None
    for line in lines[event_index + 1 :]:
        match = TOKEN_RE.match(line)
        if match:
            token = match.group(1)
            break
    if not token:
        raise ClientError("No token follows the latest standalone start; direct attach was refused")
    return port, token


def request_envelope(method: str, params: dict) -> tuple[str, bytes]:
    request_id = str(uuid.uuid4())
    message = {
        "v": PROTOCOL_VERSION,
        "id": request_id,
        "type": "request",
        "method": method,
        "params": params,
    }
    body = json.dumps(message, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_FRAME_BYTES:
        raise ClientError("Request exceeds the configured frame limit")
    header = (
        f"Content-Length: {len(body)}\r\n"
        "Content-Type: application/json\r\n\r\n"
    ).encode("ascii")
    return request_id, header + body


def read_frame(sock: socket.socket, buffer: bytearray, deadline: float) -> dict:
    def receive() -> None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ClientError("Bridge response timed out")
        sock.settimeout(remaining)
        try:
            data = sock.recv(65536)
        except (socket.timeout, TimeoutError):
            raise ClientError("Bridge response timed out") from None
        except OSError:
            raise ClientError("Bridge connection failed while reading a response") from None
        if not data:
            raise ClientError("Bridge closed the connection before completing a response")
        buffer.extend(data)
        if len(buffer) > MAX_HEADER_BYTES + MAX_FRAME_BYTES + 65536:
            raise ClientError("Bridge sent data beyond the configured frame limit")

    while b"\r\n\r\n" not in buffer:
        if len(buffer) > MAX_HEADER_BYTES:
            raise ClientError("Bridge response headers exceed the configured limit")
        receive()
    split = buffer.index(b"\r\n\r\n")
    if split > MAX_HEADER_BYTES:
        raise ClientError("Bridge response headers exceed the configured limit")
    header_bytes = bytes(buffer[:split])
    try:
        header_text = header_bytes.decode("ascii")
    except UnicodeDecodeError:
        raise ClientError("Bridge response headers are not ASCII") from None
    headers: dict[str, str] = {}
    for line in header_text.split("\r\n"):
        if ":" not in line:
            raise ClientError("Bridge response contains a malformed header")
        name, value = line.split(":", 1)
        key = name.strip().casefold()
        if key in headers:
            raise ClientError("Bridge response contains a duplicate header")
        headers[key] = value.strip()
    try:
        body_length = int(headers["content-length"])
    except (KeyError, ValueError):
        raise ClientError("Bridge response has no valid Content-Length") from None
    if not 0 <= body_length <= MAX_FRAME_BYTES:
        raise ClientError("Bridge response body exceeds the configured frame limit")
    content_type = headers.get("content-type", "").split(";", 1)[0].strip().casefold()
    if content_type != "application/json":
        raise ClientError("Bridge response is not application/json")
    body_start = split + 4
    frame_end = body_start + body_length
    while len(buffer) < frame_end:
        receive()
    body = bytes(buffer[body_start:frame_end])
    del buffer[:frame_end]
    try:
        message = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ClientError("Bridge response is not valid UTF-8 JSON") from None
    if not isinstance(message, dict) or message.get("v") != PROTOCOL_VERSION:
        raise ClientError("Bridge response has an unsupported GABP envelope")
    return message


def exchange(sock: socket.socket, buffer: bytearray, method: str, params: dict, timeout: float) -> dict:
    request_id, frame = request_envelope(method, params)
    try:
        sock.sendall(frame)
    except OSError:
        raise ClientError("Bridge connection failed while sending a request") from None
    deadline = time.monotonic() + timeout
    ignored_events = 0
    while True:
        message = read_frame(sock, buffer, deadline)
        if message.get("type") == "event":
            ignored_events += 1
            if ignored_events > MAX_EVENTS_PER_RESPONSE:
                raise ClientError("Too many unsolicited bridge events during one request")
            continue
        if message.get("type") != "response" or message.get("id") != request_id:
            raise ClientError("Bridge response type or request ID did not match")
        if message.get("error") is not None:
            raise ClientError("Bridge returned a protocol or tool error")
        if "result" not in message:
            raise ClientError("Bridge response has no result field")
        return message["result"]


def sanitize(value, token: str, depth: int = 0, budget: list[int] | None = None,
             truncations: list[int] | None = None):
    if budget is None:
        budget = [MAX_SANITIZED_NODES]
    if truncations is None:
        truncations = [0]
    budget[0] -= 1
    if budget[0] < 0:
        truncations[0] += 1
        return "[truncated: evidence item budget]"
    if depth >= 8:
        truncations[0] += 1
        return "[truncated: maximum depth]"
    if isinstance(value, dict):
        cleaned = {}
        items = list(value.items())
        for key, item in items[:100]:
            safe_key = str(key)
            if token:
                safe_key = safe_key.replace(token, "[redacted]")
            safe_key = BRIDGE_TOKEN_LINE_RE.sub(r"\1[redacted]", safe_key)
            safe_key = BEARER_RE.sub(r"\1[redacted]", safe_key)
            if len(safe_key) > 200:
                truncations[0] += 1
                safe_key = safe_key[:200]
            if SECRET_KEY_RE.search(safe_key):
                cleaned[safe_key] = "[redacted]"
            else:
                cleaned[safe_key] = sanitize(item, token, depth + 1, budget, truncations)
        if len(items) > 100:
            truncations[0] += 1
            cleaned["_truncated_fields"] = len(items) - 100
        return cleaned
    if isinstance(value, (list, tuple)):
        cleaned = [sanitize(item, token, depth + 1, budget, truncations)
                   for item in value[:MAX_COLLECTION_ITEMS]]
        if len(value) > MAX_COLLECTION_ITEMS:
            truncations[0] += 1
            cleaned.append({"_truncated_items": len(value) - MAX_COLLECTION_ITEMS})
        return cleaned
    if isinstance(value, str):
        text = value
        if token:
            text = text.replace(token, "[redacted]")
        text = BRIDGE_TOKEN_LINE_RE.sub(r"\1[redacted]", text)
        text = BEARER_RE.sub(r"\1[redacted]", text)
        if len(text) > 2048:
            truncations[0] += 1
            text = text[:2048] + "[truncated]"
        return text
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return sanitize(str(value), token, depth, budget, truncations)


def sanitized_result(result, token: str) -> dict:
    truncations = [0]
    cleaned = sanitize(result, token, truncations=truncations)
    return {"result": cleaned, "evidence_truncations": truncations[0]}


def tool_result_failed(result) -> bool:
    """Recognize shipped legacy failures and common explicit tool error flags."""
    if not isinstance(result, dict):
        return False
    if result.get("isError") is True or result.get("is_error") is True or result.get("IsError") is True:
        return True
    if result.get("success") is False:
        return True
    operation = result.get("operation")
    return isinstance(operation, dict) and operation.get("success", operation.get("Success")) is False


def collect(port: int, token: str, selectors: list[str], timeout: float) -> dict:
    evidence = {
        "status": "connecting",
        "captured_at_utc": utc_now(),
        "endpoint": {"host": "127.0.0.1", "port": port},
        "authentication_token_present": True,
        "protocol": PROTOCOL_VERSION,
        "client": CLIENT_VERSION,
        "selected_reads": selectors,
        "limitations": [
            "Caller-supplied PID and log pairing cannot be proven by this client.",
            "A successful handshake is not Rimrooms compatibility evidence.",
            "Read results are sequential observations, not an atomic game snapshot.",
            "Warnings are the latest 50 retained journal entries, not the entire startup log.",
        ],
        "calls": [],
    }
    buffer = bytearray()
    try:
        try:
            conn = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        except (OSError, socket.timeout, TimeoutError):
            raise ClientError("Could not connect to the logged loopback port") from None
        with conn:
            conn.settimeout(timeout)
            handshake = exchange(
                conn,
                buffer,
                "session/hello",
                {
                    "token": token,
                    "bridgeVersion": CLIENT_VERSION,
                    "platform": "windows",
                    "launchId": str(uuid.uuid4()),
                },
                timeout,
            )
            session_capture = sanitized_result(handshake, token)
            evidence["session"] = session_capture["result"]
            evidence["evidence_truncations"] = session_capture["evidence_truncations"]
            listed = exchange(conn, buffer, "tools/list", {}, timeout)
            raw_tools = listed.get("tools") if isinstance(listed, dict) else listed
            if not isinstance(raw_tools, list):
                raise ClientError("Live tools/list response has an unrecognized shape")
            live_names = {
                tool.get("name")
                for tool in raw_tools
                if isinstance(tool, dict) and isinstance(tool.get("name"), str)
            }
            available = sorted(name for name, _args in READ_TOOLS.values() if name in live_names)
            evidence["available_allowlisted_tools"] = available
            evidence["requested_tools_missing_from_live_list"] = [
                READ_TOOLS[key][0] for key in selectors if READ_TOOLS[key][0] not in live_names
            ]
            if "rimbridge/ping" not in live_names:
                evidence["status"] = "failed"
                evidence["error"] = "Required rimbridge/ping tool is absent from live tools/list"
                return evidence
            call_failed = False
            # Keep the connectivity ping first even if CLI selectors were reversed.
            ordered_selectors = [key for key in READ_TOOLS if key in selectors]
            for selector in ordered_selectors:
                tool_name, arguments = READ_TOOLS[selector]
                if tool_name not in live_names:
                    continue
                try:
                    result = exchange(
                        conn,
                        buffer,
                        "tools/call",
                        {"name": tool_name, "arguments": arguments},
                        timeout,
                    )
                    capture = sanitized_result(result, token)
                    evidence["evidence_truncations"] += capture["evidence_truncations"]
                    if tool_result_failed(result):
                        evidence["calls"].append(
                            {
                                "selector": selector,
                                "tool": tool_name,
                                "error": "Tool result reports failure",
                                **capture,
                            }
                        )
                        evidence["error"] = "A selected read call reported failure; see its sanitized call record"
                        call_failed = True
                        break
                    evidence["calls"].append(
                        {"selector": selector, "tool": tool_name, **capture}
                    )
                except ClientError as error:
                    evidence["calls"].append(
                        {"selector": selector, "tool": tool_name, "error": str(error)}
                    )
                    evidence["error"] = "A selected read call failed; see its sanitized call record"
                    call_failed = True
                    break
        incomplete = (evidence["requested_tools_missing_from_live_list"]
                      or evidence["evidence_truncations"] > 0)
        evidence["status"] = "partial" if incomplete else "complete"
        if call_failed:
            evidence["status"] = "failed"
    except ClientError as error:
        evidence["status"] = "failed"
        evidence["error"] = str(error)
    return evidence


def write_evidence(path: Path, evidence: dict) -> None:
    payload = json.dumps(evidence, ensure_ascii=True, indent=2).encode("utf-8") + b"\n"
    if len(payload) > MAX_EVIDENCE_BYTES:
        raise ClientError("Sanitized evidence exceeds the configured output-size limit")
    try:
        with path.expanduser().open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload.decode("utf-8"))
    except FileExistsError:
        raise ClientError("Evidence output already exists; choose a new output path") from None
    except OSError:
        raise ClientError("Could not create the explicit evidence output path") from None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", required=True, type=int, help="explicit PID for the owner-launched RimWorld process")
    parser.add_argument("--log", required=True, type=Path, help="explicit current RimWorld Player.log path")
    parser.add_argument("--output", required=True, type=Path, help="new JSON evidence path; never overwritten")
    parser.add_argument("--connect", action="store_true", help="opt in to direct read-only localhost attach")
    parser.add_argument(
        "--select",
        action="append",
        choices=tuple(READ_TOOLS),
        help="fixed read-only query; repeat to select multiple",
    )
    parser.add_argument("--timeout", type=float, default=3.0, help="per-request timeout in seconds (1 to 10)")
    args = parser.parse_args(argv)
    if not 1.0 <= args.timeout <= 10.0:
        parser.error("--timeout must be between 1 and 10 seconds")
    if args.connect and (not args.select or "ping" not in args.select):
        parser.error("--connect requires --select ping; other fixed read selectors are optional")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    evidence = {
        "status": "preflight_failed",
        "captured_at_utc": utc_now(),
        "client": CLIENT_VERSION,
        "limitations": [
            "Caller-supplied PID and log pairing cannot be proven by this client.",
            "No process discovery, log discovery, port scan, process launch, profile change, or game mutation is performed.",
        ],
    }
    token = ""
    try:
        output_resolved = args.output.expanduser().resolve(strict=False)
        log_resolved = args.log.expanduser().resolve(strict=False)
        if output_resolved == log_resolved:
            raise ClientError("Evidence output path must differ from the supplied log path")
        if output_resolved.exists():
            raise ClientError("Evidence output already exists; choose a new output path")
        exe, process_started = inspect_process(args.pid)
        port, token = read_active_endpoint(args.log, process_started)
        evidence.update(
            {
                "process": {"pid": args.pid, "executable": exe},
                "endpoint": {"host": "127.0.0.1", "port": port},
                "authentication_token_present": bool(token),
                "selected_reads": args.select or [],
            }
        )
        if args.connect:
            current_exe, current_started = inspect_process(args.pid)
            if current_exe.casefold() != exe.casefold() or abs(current_started - process_started) > 0.05:
                raise ClientError("The supplied PID changed after preflight; refusing the attach")
            evidence.update(collect(port, token, args.select, args.timeout))
            evidence["process"] = {"pid": args.pid, "executable": exe}
        else:
            evidence["status"] = "preflight_only"
            evidence["note"] = "No socket was opened; pass --connect to opt in to fixed read-only calls."
        write_evidence(args.output, evidence)
        print(f"{evidence['status']}: sanitized evidence saved to {args.output}")
        return 0 if evidence["status"] in {"complete", "preflight_only"} else 2
    except ClientError as error:
        evidence["error"] = str(error)
        try:
            write_evidence(args.output, evidence)
            print(f"refused: sanitized preflight record saved to {args.output}", file=sys.stderr)
        except ClientError:
            print(f"refused: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # Never emit exception text that might contain a credential.
        evidence["error"] = f"Unexpected {type(error).__name__}; details omitted"
        try:
            write_evidence(args.output, evidence)
            print(f"failed: sanitized error record saved to {args.output}", file=sys.stderr)
        except ClientError:
            print("failed: unexpected error; details omitted", file=sys.stderr)
        return 2
    finally:
        token = ""


if __name__ == "__main__":
    raise SystemExit(main())
