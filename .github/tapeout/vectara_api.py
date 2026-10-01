"""Small stdlib-only client for the Vectara apiv2 on staging (respin-agent hackathon).

Every helper uses a request shape that the recon agents ran on staging (see docs/api-notes/*.md and
docs/API-NOTES.md). Helpers whose shape comes only from the spec say so in their docstring.

Environment (read when a Client is constructed, never at import):
    VECTARA_API_KEY   or VECTARA_API_KEY_STAGING   -- sent as the x-api-key header, never logged
    VECTARA_BASE_URL  or VECTARA_BASE_URL_STAGING  -- default https://api.vectara.dev
    VECTARA_API_DEBUG=1                            -- log "METHOD path -> status (secs)" to stderr

Transport behaviour:
    * TCP keepalive on every socket. From the dev laptop a connection that carries no bytes for about
      60 s is dropped silently; keepalive packets keep long agent turns alive (verified at 86 s).
    * Retries with backoff on 429 / 502 / 503 / 504 and on transient network errors. Retry-After is
      honoured when present (the identity-provider 429 on POST /v2/agents sends none).
    * Agent turns (POST .../events, A2A send) are never blindly re-sent: a re-sent input is merged into
      the running turn on staging. On 429 we re-send only if no new event appeared; on a network error or
      a 5xx we poll the session instead (fire-and-poll).
    * Simulations and evaluations are created at most once: a POST whose response was lost (network error,
      429, 502/503/504) is followed by a lookup (scenario/agent, time window, name/metadata) and the object is
      adopted if it landed; only a miss re-POSTs (_create_once).
    * Long A2A turns: a2a_send(blocking=False) + a2a_wait_task() (A2A v0.3 configuration.blocking=false, then
      GET .../v1/tasks/{id}), so a review longer than the ~300 s server limit on a blocking send still returns.
    * Errors raise VectaraError carrying status, method, path and the parsed response body.

Python 3.10+, no third-party dependencies.

    source ~/.secrets.work && python3 platform/vectara_api.py      # read-only smoke test
"""

from __future__ import annotations

import base64
import http.client
import json
import mimetypes
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from math import comb
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

DEFAULT_BASE_URL = "https://api.vectara.dev"
RETRY_STATUSES = (429, 502, 503, 504)
TERMINAL_SIM_STATES = ("completed", "cancelled", "failed")
TERMINAL_EVAL_STATES = ("completed", "error", "cancelled")
TERMINAL_JOB_STATES = ("completed", "failed", "aborted")
# A2A v0.3 states after which a task makes no further progress on its own (the spec spells CANCELLED the UK way).
A2A_DONE_STATES = ("TASK_STATE_COMPLETED", "TASK_STATE_FAILED", "TASK_STATE_CANCELLED", "TASK_STATE_REJECTED",
                   "TASK_STATE_INPUT_REQUIRED", "TASK_STATE_AUTH_REQUIRED")
# ssl.SSLError (SSLEOFError, SSLZeroReturnError while reading a long response body) is an OSError, not a
# ConnectionError/URLError, so it must be listed explicitly or it escapes retries and fire-and-poll.
_NETWORK_ERRORS = (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError,
                   http.client.HTTPException, ssl.SSLError)


# --------------------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------------------

class VectaraError(Exception):
    """A non-2xx response. `body` is the parsed JSON (or text); it never contains request headers."""

    def __init__(self, status: int, method: str, path: str, body: Any):
        self.status, self.method, self.path, self.body = status, method, path, body
        self.request_id = body.get("request_id") if isinstance(body, dict) else None
        super().__init__(str(self))

    @property
    def messages(self) -> list[str]:
        b = self.body if isinstance(self.body, dict) else {}
        out = list(b.get("messages") or [])
        out += [f"{k}: {v}" for k, v in (b.get("field_errors") or {}).items()]
        return out or [str(self.body)[:500]]

    def __str__(self) -> str:
        return f"{self.method} {self.path} -> HTTP {self.status}: {'; '.join(self.messages)[:1500]}"


class VectaraNetworkError(Exception):
    """No HTTP response at all (DNS failure, reset, read timeout) after the allowed retries."""

    def __init__(self, method: str, path: str, cause: BaseException):
        self.method, self.path, self.cause = method, path, cause
        super().__init__(f"{method} {path} -> network error {type(cause).__name__}: {cause}")


class TurnError(VectaraError):
    """An agent turn finished with a persisted `error` event (seen when polling instead of waiting)."""


class TurnNotStarted(Exception):
    """No event appeared after a turn POST for `grace` seconds while the session was not running: the input
    never reached the backend (e.g. a load-balancer 5xx or a lost POST). Safe to re-POST once."""


# --------------------------------------------------------------------------------------------------
# Keepalive transport (verified fix for the ~60 s silent-drop on the laptop network path)
# --------------------------------------------------------------------------------------------------

def _enable_keepalive(sock: socket.socket, idle: int = 15, interval: int = 15, count: int = 8) -> None:
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, "TCP_KEEPALIVE"):  # macOS
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, idle)
        if hasattr(socket, "TCP_KEEPIDLE"):  # Linux
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, idle)
        if hasattr(socket, "TCP_KEEPINTVL"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval)
        if hasattr(socket, "TCP_KEEPCNT"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, count)
    except OSError:
        pass


class _KAHTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        super().connect()
        _enable_keepalive(self.sock)


class _KAHTTPConnection(http.client.HTTPConnection):
    def connect(self):
        super().connect()
        _enable_keepalive(self.sock)


class _KAHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_KAHTTPSConnection, req, context=self._context)


class _KAHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_KAHTTPConnection, req)


# --------------------------------------------------------------------------------------------------
# Multipart and SSE helpers
# --------------------------------------------------------------------------------------------------

def build_multipart(fields: Iterable[tuple]) -> tuple[bytes, str]:
    """fields: (name, value, content_type=None, filename=None). value is str or bytes.

    Every part carries its own Content-Type when given. Staging needs `application/json` on the
    `messages` part of an agent upload and on the `metadata` part of upload_file.
    """
    boundary = "----rsp" + uuid.uuid4().hex
    out: list[bytes] = []
    for f in fields:
        name, value = f[0], f[1]
        ctype = f[2] if len(f) > 2 else None
        filename = f[3] if len(f) > 3 else None
        disp = f'form-data; name="{name}"'
        if filename is not None:
            disp += f'; filename="{filename}"'
        out.append(f"--{boundary}\r\nContent-Disposition: {disp}\r\n".encode())
        if ctype:
            out.append(f"Content-Type: {ctype}\r\n".encode())
        out.append(b"\r\n")
        out.append(value if isinstance(value, bytes) else str(value).encode())
        out.append(b"\r\n")
    out.append(f"--{boundary}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


def iter_sse(resp) -> Iterator[tuple[str, dict]]:
    """Parse an SSE body (`event:`/`data:` lines, no space after the colon, blank line ends a frame)."""
    event, buf = None, []
    for raw in resp:
        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        if not line:
            if buf:
                data_txt = "\n".join(buf)
                try:
                    data = json.loads(data_txt)
                except ValueError:
                    data = {"raw": data_txt}
                yield (event or (data.get("type") if isinstance(data, dict) else None) or "message"), data
            event, buf = None, []
        elif line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            buf.append(line[5:].lstrip())
    if buf:
        try:
            yield event or "message", json.loads("\n".join(buf))
        except ValueError:
            pass


def _q(segment: str) -> str:
    return urllib.parse.quote(str(segment), safe="")


def _ts(value: Any) -> float | None:
    """Epoch seconds of a server timestamp such as "2026-09-30T04:35:35.881Z" (None if absent/unparseable)."""
    if not isinstance(value, str) or not value:
        return None
    s = value.strip().replace("Z", "+00:00")
    # Python 3.10's fromisoformat takes only 3 or 6 fractional digits: pad/truncate any other width to 6.
    s = re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], s, count=1)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt.timestamp() if dt.tzinfo else dt.replace(tzinfo=timezone.utc).timestamp()


def _meta_contains(have: Any, want: dict | None) -> bool:
    """True if every key of `want` is in `have` with an equal value (the platform adds keys such as
    __simulation__, so equality of the whole map is too strict)."""
    if not want:
        return True
    return isinstance(have, dict) and all(have.get(k) == v for k, v in want.items())


# --------------------------------------------------------------------------------------------------
# Markdown -> structured document (the converter used for the verified ingestion runs)
# --------------------------------------------------------------------------------------------------

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def split_markdown_sections(md: str) -> list[tuple[int, str | None, str]]:
    """Split markdown into (level, heading, body) sections, one per heading. Tables stay inline."""
    secs: list[tuple[int, str | None, str]] = []
    cur: list[Any] = [0, None, []]
    for line in md.splitlines():
        m = _HEADING.match(line)
        if m:
            if cur[1] is not None or any(l.strip() for l in cur[2]):
                secs.append((cur[0], cur[1], "\n".join(cur[2]).strip()))
            cur = [len(m.group(1)), m.group(2).strip(), []]
        else:
            cur[2].append(line)
    secs.append((cur[0], cur[1], "\n".join(cur[2]).strip()))
    return secs


def markdown_to_structured(doc_id: str, md: str, metadata: dict, title: str | None = None) -> dict:
    """Build a `type: structured` document body: one section per heading, section id = int.

    Each section also gets metadata.section_title (declare it as a `part` filter attribute to filter).
    """
    sections = []
    for i, (_lvl, heading, body) in enumerate(split_markdown_sections(md), start=1):
        if not body and not heading:
            continue
        sec: dict[str, Any] = {"id": i, "text": body or (heading or ""),
                               "metadata": {"section_title": heading or ""}}
        if heading:
            sec["title"] = heading
        sections.append(sec)
    doc: dict[str, Any] = {"type": "structured", "id": doc_id, "metadata": metadata, "sections": sections}
    if title:
        doc["title"] = title
    return doc


# --------------------------------------------------------------------------------------------------
# Event helpers (pure functions over lists of agent events)
# --------------------------------------------------------------------------------------------------

def structured_outputs(events: list[dict], schema_name: str | None = None) -> list[dict]:
    """All structured_output contents (already parsed dicts), oldest first, optionally by schema_name."""
    return [e.get("content") for e in events if e.get("type") == "structured_output"
            and (schema_name is None or e.get("schema_name") == schema_name)]


def last_structured_output(events: list[dict], schema_name: str | None = None) -> dict | None:
    """The final report. Pass schema_name: a triage step emits its own structured_output first.
    Events must be oldest first (as returned by send_and_wait / events_since)."""
    outs = structured_outputs(events, schema_name)
    return outs[-1] if outs else None


def final_text(events: list[dict]) -> str | None:
    """Content of the last agent_output event (default output parser)."""
    for e in reversed(events):
        if e.get("type") == "agent_output":
            return e.get("content")
    return None


def turn_errors(events: list[dict]) -> list[dict]:
    return [e for e in events if e.get("type") == "error"]


def tool_calls(events: list[dict]) -> list[dict]:
    """Join tool_input and tool_output on tool_call_id. `output` is unwrapped when output_wrapped."""
    inputs = {e.get("tool_call_id"): e for e in events if e.get("type") == "tool_input"}
    calls = []
    for e in events:
        if e.get("type") != "tool_output":
            continue
        inp = inputs.get(e.get("tool_call_id"), {})
        out = e.get("tool_output")
        if e.get("output_wrapped") and isinstance(out, dict) and "content" in out:
            out = out["content"]
        calls.append({"tool_call_id": e.get("tool_call_id"), "name": e.get("tool_configuration_name"),
                      "tool_type": inp.get("tool_type"), "input": inp.get("tool_input"),
                      "overrides": e.get("resolved_argument_overrides"), "error": bool(e.get("error")),
                      "output": out})
    return calls


def sub_agent_results(events: list[dict]) -> list[dict]:
    """Parent-side sub_agent tool outputs; sub_agent_response is a JSON string when the sub-agent
    uses a structured parser, so it is parsed here when possible."""
    res = []
    for c in tool_calls(events):
        out = c["output"] if isinstance(c["output"], dict) else {}
        if c["tool_type"] != "sub_agent" and "sub_agent_response" not in out:
            continue
        raw = out.get("sub_agent_response")
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else raw
        except ValueError:
            parsed = raw
        res.append({"tool": c["name"], "session_key": out.get("session_key"), "error": c["error"],
                    "response": parsed, "raw": out})
    return res


# --------------------------------------------------------------------------------------------------
# pass^k (client-side; the platform returns counts only) -- verified against real verdict rows
# --------------------------------------------------------------------------------------------------

def _pass_k(c: int, n: int, k: int) -> float | None:
    return None if n == 0 or k > n else comb(c, k) / comb(n, k)


def criterion_pass_k(verdicts: list[dict], k: int | None = None) -> dict:
    """{(rubric_key, criterion, scenario_key): {n, passed, pass_rate, k, pass_k}}. Non-ok rows fail."""
    groups: dict[tuple, list] = defaultdict(list)
    for r in verdicts:
        if r.get("scenario_key") is not None:
            groups[(r["rubric_key"], r["criterion"], r["scenario_key"])].append(r)
    out = {}
    for key, rows in groups.items():
        if all(r["status"] == "ok" and "passed" not in r for r in rows):
            continue  # measurement criterion (binary without pass_if)
        n = len(rows)
        c = sum(1 for r in rows if r["status"] == "ok" and r.get("passed") is True)
        kk = k or n
        out[key] = {"n": n, "passed": c, "pass_rate": c / n, "k": kk, "pass_k": _pass_k(c, n, kk)}
    return out


def scenario_pass_k(verdicts: list[dict], k: int | None = None, criteria: set | None = None) -> dict:
    """A run (session) passes only if every checked criterion passed. criteria: {(rubric, criterion)}."""
    ok_by_session: dict[str, bool] = defaultdict(lambda: True)
    scen_of: dict[str, str] = {}
    for r in verdicts:
        if r.get("scenario_key") is None:
            continue
        if criteria is not None and (r["rubric_key"], r["criterion"]) not in criteria:
            continue
        if r["status"] == "ok" and "passed" not in r:
            continue
        scen_of[r["session_key"]] = r["scenario_key"]
        ok_by_session[r["session_key"]] &= (r["status"] == "ok" and r.get("passed") is True)
    by_scen: dict[str, list] = defaultdict(list)
    for s, sk in scen_of.items():
        by_scen[sk].append(ok_by_session[s])
    return {sk: {"n": len(v), "passed": sum(v), "k": k or len(v), "pass_k": _pass_k(sum(v), len(v), k or len(v))}
            for sk, v in by_scen.items()}


# --------------------------------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------------------------------

class Client:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, *, timeout: float = 120,
                 turn_timeout: float = 900, max_retries: int = 5, backoff_base: float = 5,
                 backoff_cap: float = 60, log: Callable[[str], None] | None = None):
        key = api_key or os.environ.get("VECTARA_API_KEY") or os.environ.get("VECTARA_API_KEY_STAGING")
        if not key:
            raise RuntimeError("No Vectara API key: set VECTARA_API_KEY_STAGING (e.g. `source ~/.secrets.work`)")
        self.__key = key
        self.base_url = (base_url or os.environ.get("VECTARA_BASE_URL")
                         or os.environ.get("VECTARA_BASE_URL_STAGING") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout, self.turn_timeout = timeout, turn_timeout
        self.max_retries, self.backoff_base, self.backoff_cap = max_retries, backoff_base, backoff_cap
        self._debug = os.environ.get("VECTARA_API_DEBUG") not in (None, "", "0")
        self._log_fn = log or (lambda m: print(m, file=sys.stderr, flush=True))
        self._opener = urllib.request.build_opener(_KAHTTPSHandler(), _KAHTTPHandler())

    def __repr__(self) -> str:
        return f"Client(base_url={self.base_url!r})"

    # ---------------------------------------------------------------- transport
    def _log(self, msg: str) -> None:
        self._log_fn("[vectara_api] " + msg.replace(self.__key, "[REDACTED]"))

    def _redact(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return obj.replace(self.__key, "[REDACTED]")
        if isinstance(obj, dict):
            return {k: self._redact(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._redact(v) for v in obj]
        return obj

    def _url(self, path: str, params: dict | None) -> str:
        url = self.base_url + path
        if params:
            clean = {k: ("true" if v is True else "false" if v is False else v)
                     for k, v in params.items() if v is not None}
            if clean:
                url += ("&" if "?" in url else "?") + urllib.parse.urlencode(clean, quote_via=urllib.parse.quote)
        return url

    def _backoff(self, attempt: int) -> float:
        return min(self.backoff_cap, self.backoff_base * (2 ** attempt))

    @staticmethod
    def _retry_after(headers) -> float | None:
        ra = headers.get("Retry-After") if headers is not None else None
        try:
            return min(120.0, float(ra)) if ra else None
        except ValueError:
            return None

    @staticmethod
    def _parse(content: bytes) -> Any:
        if not content:
            return None
        txt = content.decode("utf-8", errors="replace")
        try:
            return json.loads(txt)
        except ValueError:
            return txt

    def _open(self, method: str, path: str, *, params=None, data=None, content_type=None, headers=None,
              accept="application/json", timeout=None):
        hdrs = {"x-api-key": self.__key, "Accept": accept, "User-Agent": "rsp-vectara-api/1.0"}
        if content_type:
            hdrs["Content-Type"] = content_type
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(self._url(path, params), data=data, method=method, headers=hdrs)
        return self._opener.open(req, timeout=timeout or self.timeout)

    def call(self, method: str, path: str, body: Any = None, *, params: dict | None = None,
             data: bytes | None = None, content_type: str | None = None, headers: dict | None = None,
             timeout: float | None = None, allow: tuple = (), retry_statuses: tuple = RETRY_STATUSES,
             retry_network: bool = True, max_retries: int | None = None, raw: bool = False) -> tuple[int, Any]:
        """Send one request. Returns (status, parsed body); 204 -> None; raw=True returns bytes.

        Raises VectaraError for a non-2xx status that is not in `allow`, VectaraNetworkError when no
        response arrives after the allowed retries.
        """
        if body is not None:
            data, content_type = json.dumps(body).encode(), "application/json"
        attempts = (self.max_retries if max_retries is None else max_retries) + 1
        for attempt in range(attempts):
            t0 = time.time()
            try:
                with self._open(method, path, params=params, data=data, content_type=content_type,
                                headers=headers, accept="*/*" if raw else "application/json",
                                timeout=timeout) as r:
                    status, content, rh = r.status, r.read(), r.headers
            except urllib.error.HTTPError as e:
                status, rh = e.code, e.headers
                try:
                    content = e.read()
                except Exception:  # noqa: BLE001
                    content = b""
            except _NETWORK_ERRORS as e:
                if retry_network and attempt < attempts - 1:
                    wait = self._backoff(attempt)
                    self._log(f"{method} {path}: network error {type(e).__name__}: {e}; retry in {wait:.0f}s")
                    time.sleep(wait)
                    continue
                raise VectaraNetworkError(method, path, e) from e
            if self._debug:
                self._log(f"{method} {path} -> {status} ({time.time() - t0:.1f}s)")
            if status in retry_statuses and attempt < attempts - 1:
                wait = self._retry_after(rh) or self._backoff(attempt)
                self._log(f"{method} {path}: HTTP {status}; retry {attempt + 1}/{attempts - 1} in {wait:.0f}s")
                time.sleep(wait)
                continue
            if 200 <= status < 300:
                return status, (content if raw else self._parse(content))
            parsed = self._redact(self._parse(content))
            if status in allow:
                return status, parsed
            raise VectaraError(status, method, path, parsed)
        raise AssertionError("unreachable")

    def request(self, method: str, path: str, body: Any = None, **kw) -> Any:
        """Like call() but returns only the body."""
        return self.call(method, path, body, **kw)[1]

    def paginate(self, path: str, items_key: str, params: dict | None = None, limit: int = 100,
                 max_pages: int = 1000) -> Iterator[dict]:
        """Yield items across pages. Stops on an empty/missing page_key, an empty page or a repeated
        page_key (the artifacts list returns a non-empty page_key even on its only page)."""
        seen: set[str] = set()
        page_key = None
        for _ in range(max_pages):
            p = dict(params or {})
            p["limit"] = limit
            if page_key:
                p["page_key"] = page_key
            body = self.request("GET", path, params=p) or {}
            items = body.get(items_key) or []
            yield from items
            pk = (body.get("metadata") or {}).get("page_key")
            if not pk or not items or pk in seen:
                return
            seen.add(pk)
            page_key = pk

    def _delete(self, path: str, params: dict | None = None) -> bool:
        """DELETE; True if deleted (2xx), False if it was already gone (404)."""
        status, _ = self.call("DELETE", path, params=params, allow=(404,))
        return status != 404

    def _get_or_none(self, path: str, params: dict | None = None) -> dict | None:
        status, body = self.call("GET", path, params=params, allow=(404,))
        return None if status == 404 else body

    def _create_once(self, what: str, path: str, body: dict, find: Callable[[float], dict | None], *,
                     attempts: int = 3, settle_s: float = 10) -> dict:
        """POST an object that has no client-chosen key (simulation, evaluation) without ever creating it twice.

        The POST itself is never retried blindly. After a network error, a 429 or a 502/503/504 the object may
        or may not exist, so `find(t_fire)` looks for it (twice, `settle_s` apart, in case the list lags). A hit
        is adopted and returned; only a miss re-POSTs, up to `attempts` POSTs in all. Any other status raises at
        once. If the lookup itself fails, the error is raised rather than risking a second object."""
        last: Exception | None = None
        for attempt in range(attempts):
            t_fire = time.time()
            try:
                return self.request("POST", path, body, retry_statuses=(), retry_network=False, max_retries=0)
            except VectaraNetworkError as e:
                last = e
            except VectaraError as e:
                if e.status not in RETRY_STATUSES:
                    raise
                last = e
            self._log(f"POST {path} ({what}): {str(last)[:200]}; looking it up before any retry")
            for probe in range(2):
                time.sleep(settle_s)
                found = find(t_fire)
                if found:
                    self._log(f"POST {path} ({what}): the first POST had landed; adopted the existing object")
                    return found
            if attempt < attempts - 1:
                wait = self._backoff(attempt)
                self._log(f"POST {path} ({what}): not found after {2 * settle_s:.0f}s; re-POST in {wait:.0f}s")
                time.sleep(wait)
        assert last is not None
        raise last

    # ---------------------------------------------------------------- jobs
    def wait_job(self, job_id: str, poll: float = 3, max_wait: float = 600) -> dict:
        deadline = time.time() + max_wait
        while True:
            job = self.request("GET", f"/v2/jobs/{_q(job_id)}")
            if job.get("state") in TERMINAL_JOB_STATES:
                if job.get("state") != "completed":
                    raise RuntimeError(f"job {job_id} ended in state {job.get('state')}: {job}")
                return job
            if time.time() > deadline:
                raise TimeoutError(f"job {job_id} still {job.get('state')} after {max_wait}s")
            time.sleep(poll)

    # ================================================================== CORPORA
    def get_corpus(self, key: str) -> dict | None:
        return self._get_or_none(f"/v2/corpora/{_q(key)}")

    def create_corpus(self, key: str, filter_attributes: list[dict] | None = None, name: str | None = None,
                      description: str | None = None) -> dict:
        """filter_attributes level must be "document" or "part" ("doc" is a 400 on staging)."""
        body: dict[str, Any] = {"key": key, "name": name or key}
        if description:
            body["description"] = description
        if filter_attributes:
            body["filter_attributes"] = filter_attributes
        return self.request("POST", "/v2/corpora", body)

    def create_or_get_corpus(self, key: str, filter_attributes: list[dict] | None = None,
                             name: str | None = None, description: str | None = None,
                             sync_filter_attributes: bool = True) -> dict:
        """GET; create on 404. If it exists and lacks a requested attribute, replace the attribute list
        (async job, ~35 s; existing documents become filterable on the new attribute)."""
        corpus = self.get_corpus(key)
        if corpus is None:
            status, body = self.call("POST", "/v2/corpora", {
                "key": key, "name": name or key, **({"description": description} if description else {}),
                **({"filter_attributes": filter_attributes} if filter_attributes else {})}, allow=(409,))
            return body if status != 409 else self.get_corpus(key)
        if sync_filter_attributes and filter_attributes:
            have = {(a.get("name"), a.get("level")) for a in corpus.get("filter_attributes") or []}
            want = {(a.get("name"), a.get("level")) for a in filter_attributes}
            if not want <= have:
                self.replace_filter_attributes(key, filter_attributes, wait=True)
                corpus = self.get_corpus(key)
        return corpus

    def replace_filter_attributes(self, key: str, filter_attributes: list[dict], wait: bool = True) -> dict:
        res = self.request("POST", f"/v2/corpora/{_q(key)}/replace_filter_attributes",
                           {"filter_attributes": filter_attributes})
        return self.wait_job(res["job_id"]) if wait and res and res.get("job_id") else res

    def delete_corpus(self, key: str) -> bool:
        return self._delete(f"/v2/corpora/{_q(key)}")

    def filter_attribute_stats(self, key: str) -> dict:
        """Counts are per PART, not per document."""
        return self.request("GET", f"/v2/corpora/{_q(key)}/filter_attribute_stats")

    def index_document(self, corpus: str, doc: dict, replace: bool = True) -> dict:
        """POST a core/structured document. Identical re-POST = 201 no-op; changed content = 409, in
        which case (replace=True) the document is deleted and re-added. Searchable on return."""
        path = f"/v2/corpora/{_q(corpus)}/documents"
        status, body = self.call("POST", path, doc, allow=(409,) if replace else ())
        if status == 409:
            self.delete_document(corpus, doc["id"])
            body = self.request("POST", path, doc)
        return body

    def index_markdown(self, corpus: str, doc_id: str, md: str, metadata: dict, title: str | None = None,
                       replace: bool = True) -> dict:
        """Recommended ingestion: structured doc, one section per heading, tables inline."""
        return self.index_document(corpus, markdown_to_structured(doc_id, md, metadata, title), replace)

    def upload_file(self, corpus: str, file: str | Path | bytes, metadata: dict | None = None, *,
                    doc_id: str | None = None, filename: str | None = None, content_type: str | None = None,
                    chunking_strategy: dict | None = None, replace: bool = True) -> dict:
        """Multipart upload_file. The doc id is the file part's filename (extension included) unless
        doc_id is given (sent as the `filename` form field). Note: .md uploads lose table newlines.
        On 409 (content OR metadata changed) the doc is deleted and re-uploaded when replace=True."""
        if isinstance(file, (str, Path)):
            p = Path(file)
            file_bytes, filename = p.read_bytes(), filename or p.name
        else:
            file_bytes, filename = file, filename or (doc_id or "upload.bin")
        ctype = content_type or mimetypes.guess_type(filename)[0] or (
            "text/markdown" if filename.endswith(".md") else "application/octet-stream")
        fields: list[tuple] = []
        if metadata is not None:
            fields.append(("metadata", json.dumps(metadata), "application/json"))
        if chunking_strategy is not None:
            fields.append(("chunking_strategy", json.dumps(chunking_strategy), "application/json"))
        if doc_id:
            fields.append(("filename", doc_id, "text/plain"))
        fields.append(("file", file_bytes, ctype, filename))
        data, ct = build_multipart(fields)
        path = f"/v2/corpora/{_q(corpus)}/upload_file"
        status, body = self.call("POST", path, data=data, content_type=ct, allow=(409,) if replace else ())
        if status == 409:
            self.delete_document(corpus, doc_id or filename)
            data, ct = build_multipart(fields)
            body = self.request("POST", path, data=data, content_type=ct)
        return body

    def get_document(self, corpus: str, doc_id: str) -> dict | None:
        return self._get_or_none(f"/v2/corpora/{_q(corpus)}/documents/{_q(doc_id)}")

    def list_documents(self, corpus: str, metadata_filter: str | None = None, limit: int = 100) -> list[dict]:
        """Document-level filters only, e.g. "doc.revision = 'A' AND doc.doc_type = 'timing_signoff'"."""
        return list(self.paginate(f"/v2/corpora/{_q(corpus)}/documents", "documents",
                                  {"metadata_filter": metadata_filter}, limit=limit))

    def delete_document(self, corpus: str, doc_id: str) -> bool:
        return self._delete(f"/v2/corpora/{_q(corpus)}/documents/{_q(doc_id)}")

    def bulk_delete_documents(self, corpus: str, document_ids: list[str] | None = None,
                              metadata_filter: str | None = None) -> dict:
        """Synchronous bulk delete. Non-existent ids are counted in deleted_count. Prefer ids over a
        filter (filter-based delete is best-effort through the search index)."""
        if not document_ids and not metadata_filter:
            raise ValueError("bulk_delete_documents needs document_ids or metadata_filter")
        params: dict[str, Any] = {"async": "false"}
        if document_ids:
            params["document_ids"] = ",".join(document_ids)
        if metadata_filter:
            params["metadata_filter"] = metadata_filter
        return self.request("DELETE", f"/v2/corpora/{_q(corpus)}/documents", params=params)

    def patch_document_metadata(self, corpus: str, doc_id: str, metadata: dict) -> dict:
        """Merges into the document metadata; filters see it immediately."""
        return self.request("PATCH", f"/v2/corpora/{_q(corpus)}/documents/{_q(doc_id)}", {"metadata": metadata})

    def query(self, corpus: str, query: str, metadata_filter: str | None = None, limit: int = 10, *,
              sentences_before: int = 2, sentences_after: int = 2, full_document: bool = False,
              max_by: str | None = None, lexical_interpolation: float | None = None) -> list[dict]:
        """Search one corpus, generation disabled. Returns search_results. full_document=True with
        max_by="doc.id" returns each matching document's whole text once."""
        ctx: dict[str, Any] = ({"full_document_context": True} if full_document
                               else {"sentences_before": sentences_before, "sentences_after": sentences_after})
        search: dict[str, Any] = {"limit": limit, "context_configuration": ctx}
        if metadata_filter:
            search["metadata_filter"] = metadata_filter
        if max_by:
            search["max_by"] = max_by
        if lexical_interpolation is not None:
            search["lexical_interpolation"] = lexical_interpolation
        body = self.request("POST", f"/v2/corpora/{_q(corpus)}/query",
                            {"query": query, "search": search, "generation": {"enabled": False}})
        return (body or {}).get("search_results", [])

    # ================================================================== TOOLS (lambda)
    def list_tools(self, type: str | None = None, tool_server_id: str | None = None,
                   filter: str | None = None) -> list[dict]:
        """`filter` matches title/description, NOT name."""
        return list(self.paginate("/v2/tools", "tools",
                                  {"type": type, "tool_server_id": tool_server_id, "filter": filter}))

    def get_tool(self, tool_id: str) -> dict | None:
        return self._get_or_none(f"/v2/tools/{_q(tool_id)}")

    def find_lambda_by_name(self, name: str) -> dict | None:
        for t in self.paginate("/v2/tools", "tools", {"type": "lambda"}):
            if t.get("name") == name:
                return t
        return None

    get_tool_by_name = find_lambda_by_name

    def test_lambda_code(self, code: str, test_input: dict | None = None, timeout_seconds: int | None = None,
                         check: bool = True) -> dict:
        """Dry run (creates nothing). Returns 200 even for invalid code; check=True raises on
        validation.status != valid or execution.success false."""
        body: dict[str, Any] = {"language": "python", "code": code}
        if test_input is not None:
            body["test_input"] = test_input
        if timeout_seconds:
            body["timeout_seconds"] = timeout_seconds
        res = self.request("POST", "/v2/tools/test", body)
        if check:
            val = res.get("validation") or {}
            if val.get("status") != "valid":
                raise ValueError(f"lambda code invalid: {val.get('errors')}")
            ex = res.get("execution")
            if test_input is not None and ex is not None and not ex.get("success"):
                raise ValueError(f"lambda execution failed: {(ex.get('error') or {}).get('message')}")
        return res

    def upsert_lambda(self, name: str, code: str, description: str, *, title: str | None = None,
                      timeout_s: int = 30, tool_configurations: dict | None = None) -> dict:
        """Create or update a lambda tool by name (found client-side). Returns the Tool; use ["id"].
        The tol_ id is stable across PATCH, and a PATCH applies to existing agents immediately."""
        body: dict[str, Any] = {"type": "lambda", "title": title or name, "description": description,
                                "code": code, "execution_configuration": {"max_execution_time_seconds": timeout_s}}
        if tool_configurations is not None:
            body["tool_configurations"] = tool_configurations
        existing = self.find_lambda_by_name(name)
        if existing is None:
            status, res = self.call("POST", "/v2/tools", {**body, "name": name, "language": "python"},
                                    allow=(409,))
            if status != 409:
                return res
            existing = self.find_lambda_by_name(name)
            if existing is None:
                raise VectaraError(409, "POST", "/v2/tools", res)
        return self.request("PATCH", f"/v2/tools/{_q(existing['id'])}", body)

    def test_tool(self, tool_id: str, input: dict, timeout_seconds: int | None = None) -> dict:
        """Run a stored tool. Body field is `input` here (not test_input). Returns {type: success|error,...}."""
        body: dict[str, Any] = {"input": input}
        if timeout_seconds:
            body["timeout_seconds"] = timeout_seconds
        return self.request("POST", f"/v2/tools/{_q(tool_id)}/test", body)

    def delete_tool(self, tool_id: str) -> bool:
        """409 while any agent references it: delete agents first."""
        return self._delete(f"/v2/tools/{_q(tool_id)}")

    def delete_lambda_by_name(self, name: str) -> bool:
        t = self.find_lambda_by_name(name)
        return self.delete_tool(t["id"]) if t else False

    # ================================================================== AGENTS
    def list_agents(self, filter: str | None = None, limit: int = 50, max_pages: int = 20) -> list[dict]:
        """Rate-limit prone on staging (429 from the identity provider). Prefer get_agent for existence."""
        return list(self.paginate("/v2/agents", "agents", {"filter": filter}, limit=limit, max_pages=max_pages))

    def get_agent(self, key: str) -> dict | None:
        return self._get_or_none(f"/v2/agents/{_q(key)}")

    def upsert_agent(self, body: dict) -> dict:
        """POST; on 409 PUT the full body minus key (PUT replaces everything and resets omitted fields,
        and cannot create). Sub-agents referenced by sub_agent tools must already exist."""
        key = body["key"]
        status, res = self.call("POST", "/v2/agents", body, allow=(409,))
        if status != 409:
            return res
        return self.request("PUT", f"/v2/agents/{_q(key)}", {k: v for k, v in body.items() if k != "key"})

    def patch_agent(self, key: str, patch: dict) -> dict:
        """Merges tool_configurations/steps maps (null deletes a key); metadata is replaced."""
        return self.request("PATCH", f"/v2/agents/{_q(key)}", patch)

    def delete_agent(self, key: str) -> bool:
        """Also deletes the agent's sessions and artifacts."""
        return self._delete(f"/v2/agents/{_q(key)}")

    def list_llms(self) -> list[dict]:
        return list(self.paginate("/v2/llms", "llms"))

    # ---------------------------------------------------------------- instructions (inline is simpler)
    def find_instruction_by_name(self, name: str) -> dict | None:
        for i in self.paginate("/v2/instructions", "instructions", {"filter": f"^{re.escape(name)}$"}):
            if i.get("name") == name:
                return i
        return None

    def upsert_instruction(self, name: str, template: str, template_type: str = "text",
                           description: str | None = None) -> dict:
        """Returns the instruction (use ["id"], ins_N). Each PATCH bumps version; an unpinned
        {type: reference, id} follows the latest version."""
        existing = self.find_instruction_by_name(name)
        body: dict[str, Any] = {"type": "initial", "template": template, "template_type": template_type}
        if description:
            body["description"] = description
        if existing:
            return self.request("PATCH", f"/v2/instructions/{_q(existing['id'])}", body)
        return self.request("POST", "/v2/instructions", {**body, "name": name})

    def delete_instruction(self, instruction_id: str) -> bool:
        return self._delete(f"/v2/instructions/{_q(instruction_id)}")

    # ================================================================== SESSIONS
    def create_session(self, agent: str, key: str | None = None, metadata: dict | None = None, *,
                       name: str | None = None, tti_minutes: int | None = None,
                       if_exists: str = "error") -> dict:
        """if_exists: "error" (409 raises), "reuse" (return existing) or "replace" (delete + create)."""
        body: dict[str, Any] = {}
        if key:
            body["key"] = key
            body["name"] = name or key
        elif name:
            body["name"] = name
        if metadata is not None:
            body["metadata"] = metadata
        if tti_minutes is not None:
            body["tti_minutes"] = tti_minutes
        path = f"/v2/agents/{_q(agent)}/sessions"
        status, res = self.call("POST", path, body, allow=(409,) if key and if_exists != "error" else ())
        if status == 409:
            if if_exists == "reuse":
                return self.get_session(agent, key)
            self.delete_session(agent, key)
            res = self.request("POST", path, body)
        return res

    def get_session(self, agent: str, session: str) -> dict | None:
        return self._get_or_none(f"/v2/agents/{_q(agent)}/sessions/{_q(session)}")

    def patch_session_metadata(self, agent: str, session: str, metadata: dict) -> dict:
        """REPLACES the whole metadata map: send every key."""
        return self.request("PATCH", f"/v2/agents/{_q(agent)}/sessions/{_q(session)}", {"metadata": metadata})

    def delete_session(self, agent: str, session: str) -> bool:
        return self._delete(f"/v2/agents/{_q(agent)}/sessions/{_q(session)}")

    def list_sessions(self, agent: str, metadata_filter: str | None = None) -> list[dict]:
        """metadata_filter syntax: "revision = 'B'" (no doc. prefix)."""
        return list(self.paginate(f"/v2/agents/{_q(agent)}/sessions", "sessions",
                                  {"metadata_filter": metadata_filter}, limit=50))

    def list_events(self, agent: str, session: str, limit: int = 100, max_events: int | None = None,
                    include_hidden: bool = False) -> list[dict]:
        """Events NEWEST FIRST (max page size 100)."""
        out = []
        for e in self.paginate(f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/events", "events",
                               {"include_hidden": True if include_hidden else None}, limit=min(limit, 100)):
            out.append(e)
            if max_events and len(out) >= max_events:
                break
        return out

    def get_event(self, agent: str, session: str, event_id: str) -> dict:
        return self.request("GET", f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/events/{_q(event_id)}")

    def newest_event(self, agent: str, session: str) -> dict | None:
        body = self.request("GET", f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/events", params={"limit": 1})
        evs = (body or {}).get("events") or []
        return evs[0] if evs else None

    def events_since(self, agent: str, session: str, before_event_id: str | None) -> list[dict]:
        """Events newer than before_event_id, OLDEST FIRST (None = whole session)."""
        out = []
        for e in self.paginate(f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/events", "events"):
            if before_event_id and e.get("id") == before_event_id:
                break
            out.append(e)
        out.reverse()
        return out

    @staticmethod
    def _input_body(text: str | None, messages: list | None, entry_step: str | None, stream: bool) -> dict:
        if messages is None:
            if text is None:
                raise ValueError("text or messages required")
            messages = [{"type": "text", "content": text}]
        body: dict[str, Any] = {"type": "input_message", "messages": messages, "stream_response": stream}
        if entry_step:
            body["entry_step"] = entry_step
        return body

    def _post_turn(self, agent: str, session: str, before: str | None, *, data: bytes, content_type: str,
                   headers: dict | None = None, timeout: float | None = None, allow: tuple = (),
                   accept: str = "application/json", stream: bool = False):
        """POST a turn without ever double-sending. Retries 429 only while no new event has appeared.
        Returns (status, body) or, for stream=True, the open response. Network errors propagate."""
        path = f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/events"
        for attempt in range(self.max_retries + 1):
            if stream:
                try:
                    return 200, self._open("POST", path, data=data, content_type=content_type, headers=headers,
                                           accept="text/event-stream", timeout=timeout or self.turn_timeout)
                except urllib.error.HTTPError as e:
                    status, rh, parsed = e.code, e.headers, self._redact(self._parse(e.read()))
            else:
                status, parsed = self.call("POST", path, data=data, content_type=content_type, headers=headers,
                                           timeout=timeout or self.turn_timeout, retry_statuses=(),
                                           retry_network=False, max_retries=0, allow=allow + (429,))
                rh = None
                if status != 429:
                    return status, parsed
            if status != 429 or attempt >= self.max_retries:
                raise VectaraError(status, "POST", path, parsed)
            newest = self.newest_event(agent, session)
            if newest and newest.get("id") != before:
                return 429, None  # the input landed; caller polls instead of re-sending
            wait = self._retry_after(rh) or self._backoff(attempt)
            self._log(f"POST {path}: HTTP 429 before the turn started; retry in {wait:.0f}s")
            time.sleep(wait)
        raise AssertionError("unreachable")

    def wait_for_turn(self, agent: str, session: str, before_event_id: str | None, *, poll: float = 3,
                      max_wait: float = 1800, raise_on_error: bool = True,
                      fired_at: float | None = None, not_started_grace: float = 90) -> list[dict]:
        """Fire-and-poll completion: session status == stopped AND a newer event than before_event_id
        exists AND the newest event is not the input itself. Returns the turn's events oldest first.

        With fired_at (time.time() of the POST): if the session is still stopped/unstarted and no event
        newer than before_event_id exists `not_started_grace` seconds after the POST, raise TurnNotStarted
        instead of spinning until max_wait."""
        deadline = time.time() + max_wait
        while True:
            s = self.get_session(agent, session) or {}
            if fired_at is not None and s.get("status") in ("stopped", "unstarted") and \
                    time.time() - fired_at > not_started_grace:
                newest = self.newest_event(agent, session)
                if (newest or {}).get("id") == before_event_id:
                    raise TurnNotStarted(f"no event in {agent}/{session} {time.time() - fired_at:.0f}s after the "
                                         "turn POST; the input never landed")
            if s.get("status") == "stopped":
                newest = self.newest_event(agent, session)
                if newest and newest.get("id") != before_event_id and \
                        newest.get("type") not in ("input_message", "artifact_upload"):
                    events = self.events_since(agent, session, before_event_id)
                    if raise_on_error and turn_errors(events):
                        err = turn_errors(events)[-1]
                        raise TurnError(400, "TURN", f"/v2/agents/{agent}/sessions/{session}",
                                        {"messages": err.get("messages") or [str(err)]})
                    return events
            if time.time() > deadline:
                raise TimeoutError(f"turn in {agent}/{session} not finished after {max_wait}s")
            time.sleep(poll)

    def send_and_wait(self, agent: str, session: str, text: str | None = None, *,
                      messages: list | None = None, entry_step: str | None = None, mode: str = "sync",
                      fire_timeout_s: int = 5, poll: float = 3, max_wait: float = 1800) -> list[dict]:
        """Send one input and return that turn's events, OLDEST FIRST.

        mode="sync": blocking POST over a keepalive socket; on 5xx / network error / read timeout it
                     falls back to polling (the turn keeps running server-side).
        mode="poll": POST with Request-Timeout (504 expected and harmless), then poll.
        A turn that fails validation (e.g. 400 strict-schema, 422 template/eager-ref) raises VectaraError.
        Never call this concurrently on one session: staging merges overlapping inputs.
        """
        before = (self.newest_event(agent, session) or {}).get("id")
        data = json.dumps(self._input_body(text, messages, entry_step, False)).encode()
        headers = {"Request-Timeout": str(fire_timeout_s)} if mode == "poll" else None
        for fire in range(2):  # a second POST only after TurnNotStarted (no input landed)
            t_fire = time.time()
            try:
                status, body = self._post_turn(agent, session, before, data=data,
                                               content_type="application/json", headers=headers,
                                               allow=(502, 503, 504),
                                               timeout=fire_timeout_s + 60 if mode == "poll" else None)
                if status == 201 and body is not None:
                    return body.get("events", [])
            except VectaraNetworkError as e:
                self._log(f"turn POST lost ({type(e.cause).__name__}); polling session {session}")
            try:
                return self.wait_for_turn(agent, session, before, poll=poll, max_wait=max_wait,
                                          fired_at=t_fire)
            except TurnNotStarted as e:
                if fire:
                    raise
                self._log(f"{e}; re-posting once")
        raise AssertionError("unreachable")

    def stream_turn(self, agent: str, session: str, text: str | None = None, *, messages: list | None = None,
                    entry_step: str | None = None, timeout: float | None = None) -> Iterator[tuple[str, dict]]:
        """Yield (event_type, data) SSE frames until `end`. tool_activity frames (sub-agent inner
        events) exist only here. structured_output frames carry the parsed content."""
        before = (self.newest_event(agent, session) or {}).get("id")
        data = json.dumps(self._input_body(text, messages, entry_step, True)).encode()
        status, resp = self._post_turn(agent, session, before, data=data, content_type="application/json",
                                       stream=True, timeout=timeout)
        if resp is None:
            return
        with resp:
            for ev, frame in iter_sse(resp):
                yield ev, frame
                if ev == "end":
                    return

    def stream_and_wait(self, agent: str, session: str, text: str | None = None, *,
                        messages: list | None = None, entry_step: str | None = None,
                        on_event: Callable[[str, dict], None] | None = None, max_wait: float = 1800) -> dict:
        """Stream a turn (live frames to on_event), then read the persisted events. If the stream dies
        (network), fall back to polling. Returns {"frames": [...], "events": [...oldest first]}."""
        before = (self.newest_event(agent, session) or {}).get("id")
        frames: list[tuple[str, dict]] = []
        data = json.dumps(self._input_body(text, messages, entry_step, True)).encode()
        try:
            status, resp = self._post_turn(agent, session, before, data=data, content_type="application/json",
                                           stream=True)
            if resp is not None:
                with resp:
                    for ev, frame in iter_sse(resp):
                        frames.append((ev, frame))
                        if on_event:
                            on_event(ev, frame)
                        if ev == "end":
                            break
        except (VectaraNetworkError, *_NETWORK_ERRORS) as e:  # type: ignore[misc]
            self._log(f"stream lost ({type(e).__name__}); polling session {session}")
        events = self.wait_for_turn(agent, session, before, max_wait=max_wait)
        return {"frames": frames, "events": events}

    def upload_and_send(self, agent: str, session: str, files: list, text: str, *, stream: bool = False,
                        max_wait: float = 1800) -> list[dict]:
        """Multipart turn: upload files as session artifacts + a text message. files: paths or
        (filename, bytes, content_type) tuples. Returns the turn's events oldest first (the first is
        artifact_upload with artifact ids). The agent must read artifacts with artifact_read/grep."""
        fields: list[tuple] = [("messages", json.dumps([{"type": "text", "content": text}]), "application/json")]
        for f in files:
            if isinstance(f, (str, Path)):
                p = Path(f)
                fields.append(("files", p.read_bytes(), mimetypes.guess_type(p.name)[0] or
                               ("text/markdown" if p.suffix == ".md" else "application/octet-stream"), p.name))
            else:
                fields.append(("files", f[1], f[2] if len(f) > 2 else "application/octet-stream", f[0]))
        data, ct = build_multipart(fields)
        before = (self.newest_event(agent, session) or {}).get("id")
        try:
            status, body = self._post_turn(agent, session, before, data=data, content_type=ct,
                                           allow=(502, 503, 504))
            if status == 201 and body is not None:
                return body.get("events", [])
        except VectaraNetworkError as e:
            self._log(f"upload turn POST lost ({type(e.cause).__name__}); polling session {session}")
        return self.wait_for_turn(agent, session, before, max_wait=max_wait)

    def interrupt(self, agent: str, session: str) -> dict:
        """Stops a running turn (its events end with session_interrupted)."""
        return self.request("POST", f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/events", {"type": "interrupt"})

    # ---------------------------------------------------------------- artifacts
    def list_artifacts(self, agent: str, session: str, metadata_filter: str | None = None) -> list[dict]:
        """e.g. metadata_filter="tool = 'artifact_create'" for agent-created files."""
        return list(self.paginate(f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/artifacts", "artifacts",
                                  {"metadata_filter": metadata_filter}))

    def get_artifact(self, agent: str, session: str, artifact_id: str) -> dict:
        """Artifact with `data` (base64); see artifact_bytes for raw content."""
        return self.request("GET", f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/artifacts/{_q(artifact_id)}")

    def artifact_bytes(self, agent: str, session: str, artifact_id: str) -> bytes:
        return self.call("GET", f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/artifacts/{_q(artifact_id)}/content",
                         raw=True)[1]

    @staticmethod
    def decode_artifact(artifact: dict) -> bytes:
        return base64.b64decode(artifact.get("data") or "")

    # ================================================================== EVALS
    def upsert_scenario(self, body: dict) -> dict:
        """POST; on 409 PUT (full replace; omitting `expected` clears it)."""
        status, res = self.call("POST", "/v2/scenarios", body, allow=(409,))
        if status != 409:
            return res
        return self.request("PUT", f"/v2/scenarios/{_q(body['key'])}", {k: v for k, v in body.items() if k != "key"})

    def upsert_rubric(self, body: dict) -> dict:
        """POST; on 409 PUT {name, criteria}. Condition syntax is NOT validated at create."""
        status, res = self.call("POST", "/v2/rubrics", body, allow=(409,))
        if status != 409:
            return res
        return self.request("PUT", f"/v2/rubrics/{_q(body['key'])}", {k: v for k, v in body.items() if k != "key"})

    def get_scenario(self, key: str) -> dict | None:
        return self._get_or_none(f"/v2/scenarios/{_q(key)}")

    def get_rubric(self, key: str) -> dict | None:
        return self._get_or_none(f"/v2/rubrics/{_q(key)}")

    def delete_scenario(self, key: str) -> bool:
        return self._delete(f"/v2/scenarios/{_q(key)}")

    def delete_rubric(self, key: str) -> bool:
        return self._delete(f"/v2/rubrics/{_q(key)}")

    def create_simulation(self, scenario_key: str, target_agent: str, simulator_agent: str,
                          session_metadata: dict | None = None, timeout_seconds: int = 600, *,
                          known_ids: Iterable[str] = ()) -> dict:
        """One simulation = one run (202). The simulator agent needs a simulator_action tool.
        timeout_seconds 60..3600.

        Created at most once (_create_once): a lost response is followed by find_simulation(). A simulation
        carries no caller key and repeats of one scenario can carry identical metadata, so pass `known_ids`
        (every simulation id the caller already recorded) to keep an earlier repeat from being adopted."""
        target: dict[str, Any] = {"agent_key": target_agent}
        if session_metadata:
            target["session_metadata"] = session_metadata
        known = set(known_ids)
        return self._create_once(
            f"simulation of {scenario_key}", "/v2/simulations",
            {"scenario_key": scenario_key, "target_agent": target, "simulator_agent": {"agent_key": simulator_agent},
             "timeout_seconds": timeout_seconds},
            lambda t_fire: self.find_simulation(scenario_key, target_agent, simulator_agent, since=t_fire,
                                                session_metadata=session_metadata, exclude_ids=known))

    def find_simulation(self, scenario_key: str, target_agent: str, simulator_agent: str | None = None, *,
                        since: float, session_metadata: dict | None = None, exclude_ids: Iterable[str] = (),
                        skew_s: float = 300, max_pages: int = 4) -> dict | None:
        """The newest simulation of `scenario_key` on `target_agent` created at or after `since - skew_s` (epoch
        seconds; the slack covers laptop/server clock skew), whose id is not in `exclude_ids` and whose target
        session metadata contains `session_metadata` (the Simulation object itself has no metadata, so the target
        session is read). None if there is none. Used to detect a POST that landed although its response was
        lost; read-only."""
        excluded = set(exclude_ids)
        hits = []
        for sim in self.paginate("/v2/simulations", "simulations", {"scenario_key": scenario_key}, limit=50,
                                 max_pages=max_pages):
            created = _ts(sim.get("created_at"))
            if created is None or created < since - skew_s or sim.get("simulation_id") in excluded:
                continue
            if sim.get("target_agent_key") != target_agent or \
                    (simulator_agent and sim.get("simulator_agent_key") != simulator_agent):
                continue
            if session_metadata:
                sess = self.get_session(target_agent, sim.get("target_session_key") or "") or {}
                if not _meta_contains(sess.get("metadata"), session_metadata):
                    continue
            hits.append((created, sim))
        if len(hits) > 1:
            self._log(f"find_simulation({scenario_key}): {len(hits)} candidates in the window; taking the newest")
        return max(hits, key=lambda h: h[0])[1] if hits else None

    def get_simulation(self, sim_id: str) -> dict:
        return self.request("GET", f"/v2/simulations/{_q(sim_id)}")

    def wait_simulation(self, sim_id: str, poll: float = 5, max_wait: float = 3900) -> dict:
        deadline = time.time() + max_wait
        while True:
            sim = self.get_simulation(sim_id)
            if sim.get("status") in TERMINAL_SIM_STATES:
                return sim
            if time.time() > deadline:
                raise TimeoutError(f"simulation {sim_id} still {sim.get('status')} after {max_wait}s")
            time.sleep(poll)

    def wait_simulations(self, sim_ids: list[str], poll: float = 5, max_wait: float = 3900) -> list[dict]:
        deadline, done = time.time() + max_wait, {}
        while True:
            for sid in sim_ids:
                if sid not in done:
                    sim = self.get_simulation(sid)
                    if sim.get("status") in TERMINAL_SIM_STATES:
                        done[sid] = sim
            if len(done) == len(sim_ids):
                return [done[s] for s in sim_ids]
            if time.time() > deadline:
                raise TimeoutError(f"{len(sim_ids) - len(done)} simulations still running after {max_wait}s")
            time.sleep(poll)

    def list_simulations(self, scenario_key: str | None = None) -> list[dict]:
        return list(self.paginate("/v2/simulations", "simulations", {"scenario_key": scenario_key}))

    def delete_simulation(self, sim_id: str) -> bool:
        return self._delete(f"/v2/simulations/{_q(sim_id)}")

    def cancel_simulation(self, sim_id: str, reason: str = "cancelled by rsp script") -> dict:
        """SPEC ONLY (not run on staging)."""
        return self.request("POST", f"/v2/simulations/{_q(sim_id)}/cancel", {"reason": reason})

    @staticmethod
    def metadata_session_filter(expression: str) -> dict:
        """e.g. "rsp_run = 'r1'" or "\"__simulation__.scenario_key\" = 'rsp_kx7_revA'"."""
        return {"type": "metadata", "expression": expression}

    @staticmethod
    def keys_session_filter(session_keys: list[str]) -> dict:
        """Target session keys only: a simulator session key fails the whole evaluation."""
        return {"type": "keys", "session_keys": session_keys}

    def create_evaluation(self, agent_key: str, rubric_keys: list[str], session_filter: dict | None = None, *,
                          name: str | None = None, judge_agent_key: str | None = None,
                          max_sessions: int | None = None, metadata: dict | None = None) -> dict:
        """Create only after every simulation completed (selection resolves once, at create).
        Omit judge_agent_key for agt_system_judge.

        Created at most once (_create_once): a lost response is followed by find_evaluation() on the same
        agent, name, rubric keys, session filter and metadata. Give every evaluation a unique `name` (or
        `metadata`) so the lookup can tell it from earlier ones."""
        body: dict[str, Any] = {"agent_key": agent_key, "rubric_keys": rubric_keys}
        for k, v in (("name", name), ("session_filter", session_filter), ("judge_agent_key", judge_agent_key),
                     ("max_sessions", max_sessions), ("metadata", metadata)):
            if v is not None:
                body[k] = v
        return self._create_once(
            f"evaluation {name or ''}".strip(), "/v2/evaluations", body,
            lambda t_fire: self.find_evaluation(agent_key, since=t_fire, name=name, rubric_keys=rubric_keys,
                                                session_filter=session_filter, metadata=metadata))

    def find_evaluation(self, agent_key: str, *, since: float, name: str | None = None,
                        rubric_keys: list[str] | None = None, session_filter: dict | None = None,
                        metadata: dict | None = None, skew_s: float = 300, max_pages: int = 4) -> dict | None:
        """The newest evaluation of `agent_key` created at or after `since - skew_s` whose name, rubric keys,
        session filter and metadata match the given ones (each only when given). Read-only; see find_simulation."""
        hits = []
        for ev in self.paginate("/v2/evaluations", "evaluations", {"agent_key": agent_key}, limit=50,
                                max_pages=max_pages):
            created = _ts(ev.get("created_at"))
            if created is None or created < since - skew_s:
                continue
            if name is not None and ev.get("name") != name:
                continue
            if rubric_keys is not None and sorted(ev.get("rubric_keys") or []) != sorted(rubric_keys):
                continue
            if session_filter is not None and ev.get("session_filter") not in (None, session_filter):
                continue  # list rows may omit it; compare only when present
            if not _meta_contains(ev.get("metadata"), metadata):
                continue
            hits.append((created, ev))
        if len(hits) > 1:
            self._log(f"find_evaluation({name}): {len(hits)} candidates in the window; taking the newest")
        return max(hits, key=lambda h: h[0])[1] if hits else None

    def get_evaluation(self, eval_id: str) -> dict:
        return self.request("GET", f"/v2/evaluations/{_q(eval_id)}")

    def wait_evaluation(self, eval_id: str, poll: float = 5, max_wait: float = 1800,
                        raise_on_error: bool = True) -> dict:
        deadline = time.time() + max_wait
        while True:
            ev = self.get_evaluation(eval_id)
            st = ev.get("status")
            if st in TERMINAL_EVAL_STATES:
                if raise_on_error and st == "error":
                    raise RuntimeError(f"evaluation {eval_id} error: {ev.get('end_reason')}")
                return ev
            if time.time() > deadline:
                raise TimeoutError(f"evaluation {eval_id} still {st} after {max_wait}s")
            time.sleep(poll)

    def list_verdicts(self, eval_id: str, **filters) -> list[dict]:
        """filters: rubric_key, criterion, session_key, passed, status, source."""
        return list(self.paginate(f"/v2/evaluations/{_q(eval_id)}/verdicts", "verdicts", filters))

    def evaluation_summary(self, eval_id: str) -> list[dict]:
        """Counts per (rubric, criterion); pass rate = passed_count / scored_count. No pass^k."""
        return (self.request("GET", f"/v2/evaluations/{_q(eval_id)}/summary") or {}).get("summaries", [])

    def session_verdicts(self, agent: str, session: str, **filters) -> list[dict]:
        return list(self.paginate(f"/v2/agents/{_q(agent)}/sessions/{_q(session)}/verdicts", "verdicts", filters))

    def list_evaluations(self, agent_key: str | None = None, status: str | None = None) -> list[dict]:
        return list(self.paginate("/v2/evaluations", "evaluations", {"agent_key": agent_key, "status": status}))

    def cancel_evaluation(self, eval_id: str) -> dict:
        return self.request("POST", f"/v2/evaluations/{_q(eval_id)}/cancel", {})

    def delete_evaluation(self, eval_id: str) -> bool:
        return self._delete(f"/v2/evaluations/{_q(eval_id)}")

    def run_eval_suite(self, scenario_keys: list[str], target_agent: str, simulator_agent: str,
                       rubric_keys: list[str], *, k: int = 3, run_id: str | None = None,
                       session_metadata: dict[str, dict] | None = None, timeout_seconds: int = 1800,
                       judge_agent_key: str | None = None, log: Callable[[str], None] | None = None) -> dict:
        """k simulations per scenario (all tagged rsp_run=<run_id>), wait, ONE evaluation over the run,
        wait, fetch verdicts, compute pass^k. session_metadata: per-scenario extra target metadata."""
        say = log or self._log
        run_id = run_id or "rsp_" + time.strftime("%Y%m%d%H%M%S")
        sims = []
        for sk in scenario_keys:
            for i in range(k):
                meta = {"rsp_run": run_id, "repeat": i, **((session_metadata or {}).get(sk) or {})}
                sims.append(self.create_simulation(sk, target_agent, simulator_agent, meta, timeout_seconds,
                                                   known_ids=[s["simulation_id"] for s in sims]))
        say(f"run {run_id}: started {len(sims)} simulations")
        finished = self.wait_simulations([s["simulation_id"] for s in sims], max_wait=timeout_seconds + 300)
        bad = [s for s in finished if s.get("status") != "completed"]
        if bad:
            say(f"run {run_id}: {len(bad)} simulations not completed: "
                f"{[(s['simulation_id'], s.get('status'), s.get('end_reason')) for s in bad]}")
        ev = self.create_evaluation(target_agent, rubric_keys,
                                    self.metadata_session_filter(f"rsp_run = '{run_id}'"),
                                    name=f"{run_id} eval", judge_agent_key=judge_agent_key,
                                    metadata={"rsp_run": run_id})
        ev = self.wait_evaluation(ev["id"])
        verdicts = self.list_verdicts(ev["id"])
        return {"run_id": run_id, "simulations": finished, "evaluation": ev, "verdicts": verdicts,
                "summary": self.evaluation_summary(ev["id"]),
                "criterion_pass_k": criterion_pass_k(verdicts, k), "scenario_pass_k": scenario_pass_k(verdicts, k)}

    # ================================================================== A2A
    def a2a_card(self, agent_key: str) -> dict:
        return self.request("GET", f"/v2/agents/{_q(agent_key)}/.well-known/agent-card.json")

    @staticmethod
    def _a2a_result(task: dict) -> dict:
        texts = [p["text"] for a in (task.get("artifacts") or []) for p in a.get("parts", []) if "text" in p]
        return {"task_id": task.get("id"), "context_id": task.get("contextId"),
                "state": (task.get("status") or {}).get("state"), "text": "\n".join(texts), "task": task}

    def a2a_send(self, agent_key: str, text: str, context_id: str | None = None, data: dict | None = None,
                 timeout: float | None = None, blocking: bool = True) -> dict:
        """A2A v0.3 send. Returns {task_id, context_id (= session key), state, text, task, send_s}.

        blocking=True waits for the turn; on staging a turn longer than about 300 s returns HTTP 504 "Agent loop
        timed out" while the turn keeps running. blocking=False sends configuration.blocking=false (A2A v0.3
        MessageSendConfiguration): the task comes back SUBMITTED/WORKING and a2a_wait_task() polls it. If the
        server ignores the flag, the call simply blocks as before; callers can tell from `state` and `send_s`.
        With a structured output parser the task has no artifacts (text == ""): read the session's
        structured_output event instead. A hook that fires leaves state TASK_STATE_WORKING."""
        content: list[dict] = [{"text": text}]
        if data is not None:
            content.append({"data": {"data": data}})
        msg: dict[str, Any] = {"messageId": str(uuid.uuid4()), "role": "ROLE_USER", "content": content}
        if context_id:
            msg["contextId"] = context_id
        body: dict[str, Any] = {"message": msg}
        if not blocking:
            body["configuration"] = {"blocking": False}
        t0 = time.time()
        res = self.request("POST", f"/v2/agents/{_q(agent_key)}/v1/message:send", body,
                           timeout=timeout or self.turn_timeout, retry_statuses=(), retry_network=False)
        # no blind re-POST of message:send (turns are never sent twice; the caller decides after reading
        # the contextId session)
        out = self._a2a_result((res or {}).get("task") or {})
        out["send_s"] = round(time.time() - t0, 1)
        return out

    def a2a_get_task(self, agent_key: str, task_id: str, history_length: int | None = None) -> dict:
        """A2A v0.3 tasks/get: GET /v2/agents/{key}/v1/tasks/{task_id}. Staging returns the bare Task
        ({id, contextId, status, artifacts, history}); a {"task": ...} wrapper is unwrapped too."""
        res = self.request("GET", f"/v2/agents/{_q(agent_key)}/v1/tasks/{_q(task_id)}",
                           params={"historyLength": history_length})
        task = res.get("task") if isinstance(res, dict) and isinstance(res.get("task"), dict) else res
        return self._a2a_result(task or {})

    def a2a_wait_task(self, agent_key: str, task_id: str, *, poll: float = 5, max_wait: float = 1800,
                      stopped_grace: float = 90, on_poll: Callable[[dict], None] | None = None) -> dict:
        """Poll tasks/get until the task reaches a state in A2A_DONE_STATES. Returns a2a_get_task()'s dict plus
        `polls`, `wait_s` and `via` ("task" or "session_stopped").

        A task can stay TASK_STATE_WORKING after its turn ended (seen when a hook fires), so once the task's
        session (contextId) has been `stopped` for `stopped_grace` seconds the last task snapshot is returned with
        via="session_stopped"; the caller then reads the session events. Raises TimeoutError after max_wait."""
        t0, polls, stopped_since = time.time(), 0, None
        while True:
            res = self.a2a_get_task(agent_key, task_id, history_length=1)
            polls += 1
            res.update(polls=polls, wait_s=round(time.time() - t0, 1), via="task")
            if on_poll:
                on_poll(res)
            if res.get("state") in A2A_DONE_STATES:
                return res
            ctx = res.get("context_id")
            status = ((self.get_session(agent_key, ctx) or {}).get("status")) if ctx else None
            if status == "stopped":
                stopped_since = stopped_since or time.time()
                if time.time() - stopped_since >= stopped_grace:
                    res["via"] = "session_stopped"
                    return res
            else:
                stopped_since = None
            if time.time() - t0 > max_wait:
                raise TimeoutError(f"A2A task {task_id} still {res.get('state')} after {max_wait:.0f}s")
            time.sleep(poll)

    # ================================================================== HHEM
    def factual_consistency(self, generated_text: str, source_texts: list[str],
                            model_name: str | None = None) -> float:
        """HHEM score 0..1 (>= 0.5 treat as grounded). Empty sources give a meaningless 0.26 on staging,
        so they are rejected here."""
        sources = [s for s in (source_texts or []) if s and s.strip()]
        if not sources:
            raise ValueError("factual_consistency needs at least one non-empty source text")
        body: dict[str, Any] = {"generated_text": generated_text, "source_texts": sources}
        if model_name:
            body["model_parameters"] = {"model_name": model_name}
        return float(self.request("POST", "/v2/evaluate_factual_consistency", body)["score"])

    # ================================================================== STRETCH (hooks, memory, schedules, MCP)
    def upsert_hook(self, key: str, name: str, spec: dict, description: str | None = None,
                    metadata: dict | None = None) -> dict:
        """POST /v2/hooks; on 409 PUT (409-on-duplicate is assumed, not observed)."""
        body: dict[str, Any] = {"name": name, "spec": spec}
        if description:
            body["description"] = description
        if metadata:
            body["metadata"] = metadata
        status, res = self.call("POST", "/v2/hooks", {"key": key, **body}, allow=(409,))
        return res if status != 409 else self.request("PUT", f"/v2/hooks/{_q(key)}", body)

    def delete_hook(self, key: str) -> bool:
        """409 while an agent lists it: patch_agent(key, {"hooks": []}) first."""
        return self._delete(f"/v2/hooks/{_q(key)}")

    def get_memory(self, agent: str) -> dict:
        return self.request("GET", f"/v2/agents/{_q(agent)}/memory")

    def set_memory(self, agent: str, content: str, updated_by: str = "rsp_script",
                   expected_version: int | None = None) -> dict:
        """Full replace (not append). 409 if expected_version is stale."""
        if expected_version is None:
            expected_version = (self.get_memory(agent).get("metadata") or {}).get("memory_version", 0)
        return self.request("PATCH", f"/v2/agents/{_q(agent)}/memory",
                            {"content": content, "updated_by": updated_by, "expected_version": expected_version})

    def create_schedule(self, agent: str, body: dict) -> dict:
        """Minimum interval 1 h; there is no run-now endpoint."""
        return self.request("POST", f"/v2/agents/{_q(agent)}/schedules", body)

    def delete_schedule(self, agent: str, key: str) -> bool:
        return self._delete(f"/v2/agents/{_q(agent)}/schedules/{_q(key)}")

    def create_tool_server(self, name: str, uri: str, transport: str = "streamable-http",
                           description: str | None = None, headers: dict | None = None) -> dict:
        """The URI must be publicly reachable (internal/unresolvable hosts are a 400)."""
        body: dict[str, Any] = {"name": name, "type": "mcp", "uri": uri, "transport": transport}
        if description:
            body["description"] = description
        if headers:
            body["headers"] = headers
        return self.request("POST", "/v2/tool_servers", body)

    def delete_tool_server(self, server_id: str) -> bool:
        return self._delete(f"/v2/tool_servers/{_q(server_id)}")


_default: Client | None = None


def client() -> Client:
    """Process-wide default client built from the environment."""
    global _default
    if _default is None:
        _default = Client()
    return _default


def _smoke() -> int:
    """Read-only: list rsp_ agents (one page) and print only a count and keys."""
    c = Client()
    t0 = time.time()
    agents = c.list_agents(filter="rsp_", limit=50, max_pages=1)
    print(f"base_url={c.base_url} rsp_ agents on first page: {len(agents)} ({time.time() - t0:.1f}s)")
    for a in agents:
        print(f"  {a.get('key')}  model={((a.get('model') or {}).get('name'))}")
    return 0


if __name__ == "__main__":
    sys.exit(_smoke())
