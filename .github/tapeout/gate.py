#!/usr/bin/env python3
"""Tape-out gate CI runner: "CI for chips".

On every push to a pull request that touches package/, this script:
  1. sets pending commit statuses (tapeout/gate + one per AI specialist),
  2. ingests the PR head's package/*.md into the Vectara corpus as a new revision,
  3. continues the PR's own Vectara gate session (one session per PR = the review loop's memory),
  4. waits for the 7 AI specialists' verdict (fire-and-poll), reads the structured report,
  5. checks every quote word for word against the files at the PR head (one correction turn if any fail),
  6. asks the io-built helper for a plain-English summary and the CI plain writer for per-problem comments,
  7. publishes: statuses, a PR review with inline comments on the exact lines, "Fixed in <sha>" replies on
     resolved threads, a sticky summary comment, and the report JSON (workflow artifact).

    python3 .github/tapeout/gate.py review  --pr 3 [--sha <head sha>]      # one review round
    python3 .github/tapeout/gate.py explain --pr 3 --comment-id 123 --kind issue|review
    python3 .github/tapeout/gate.py release --pr 3 [--skip-deployment]      # after merge: fab + retro PR
    python3 .github/tapeout/gate.py republish --pr 3 --report out/report.json  # re-render only (debug)

Environment: GITHUB_TOKEN, GITHUB_REPOSITORY (owner/name), VECTARA_API_KEY, VECTARA_BASE_URL,
optional RUN_URL (link for the statuses). Secrets are read from the environment only and never printed.
Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
import base64
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vectara_api as v  # noqa: E402

# --------------------------------------------------------------------------------------------------
# Vectara resources (the gate agents are frozen; the CI only calls them)
# --------------------------------------------------------------------------------------------------
CORPUS = "rsp_kst_tapeout"
PROJECT_CODE = "KST"
PROJECT_NAME = "ALX-5100 KESTREL"
GATE_KEY = "rsp_kst_gate"
GATE_SCHEMA = "rsp_kst_gate_report"
IO_EXPLAINER = "rsp_io_report_explainer"      # built by io (Vectara's assistant)
PLAIN_WRITER = "rsp_ci_plain_writer"          # CI comment writer (setup_plain_writer.py)
PLAIN_SCHEMA = "rsp_ci_plain_comments"
RETRO_KEY = "rsp_kst_retro"
RETRO_SCHEMA = "rsp_kst_retro_report"

AREAS = ["spec", "verification", "timing", "cdc", "power", "ip_errata", "governance"]
AREA_LABEL = {"spec": "spec", "verification": "verification", "timing": "timing", "cdc": "cdc",
              "power": "power", "ip_errata": "ip-errata", "governance": "governance"}
AREA_PLAIN = {
    "spec": ("Spec", "do all the design documents agree with each other?"),
    "verification": ("Testing", "was the design tested enough before sign-off?"),
    "timing": ("Timing", "are signals fast enough, at every temperature and voltage?"),
    "cdc": ("Clock crossings", "do signals pass safely between parts running on different clocks?"),
    "power": ("Power", "does every part of the chip get enough clean power?"),
    "ip_errata": ("Bought-in parts", "are third-party blocks the right, bug-fixed versions?"),
    "governance": ("Sign-off", "is every sign-off actually signed and up to date?"),
}
AREA_RULE_PREFIX = [("CHK-PV-02", "spec"), ("CHK-PV-01", "governance"), ("CHK-SPEC", "spec"),
                    ("CHK-VER", "verification"), ("CHK-STA", "timing"), ("CHK-CDC", "cdc"), ("CHK-PI", "power"),
                    ("CHK-IP", "ip_errata"), ("CHK-GOV", "governance"), ("CHK-DFT", "governance")]
RESPIN_PLAIN = {"full_mask": "remake the chip almost from scratch", "metal_only": "a wiring-only redo",
                "none": "no redo"}
SUMMARY_MARK = "<!-- tapeout-gate-summary -->"
STATE_RE = re.compile(r"<!-- tapeout-state:([A-Za-z0-9+/=]+) -->")
FIND_MARK = "<!-- tapeout:finding:{} -->"
FIND_RE = re.compile(r"<!-- tapeout:finding:(.+?) -->")
CORRECTION_PREFIX = "Quote check before publishing"

LOG_LINES: list[str] = []


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    LOG_LINES.append(line)
    print(line, flush=True)


# --------------------------------------------------------------------------------------------------
# GitHub REST / GraphQL (token from the environment)
# --------------------------------------------------------------------------------------------------
class GH:
    def __init__(self, repo: str, token: str):
        self.repo, self.__token = repo, token
        self.api = os.environ.get("GITHUB_API_URL", "https://api.github.com")

    def req(self, method: str, path: str, body=None, *, accept: str = "application/vnd.github+json",
            ok404: bool = False):
        url = path if path.startswith("http") else f"{self.api}{path}"
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(5):
            r = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": f"Bearer {self.__token}", "Accept": accept,
                "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "tapeout-gate-ci",
                **({"Content-Type": "application/json"} if data else {})})
            try:
                with urllib.request.urlopen(r, timeout=60) as resp:
                    raw = resp.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                txt = e.read().decode("utf-8", "replace")
                if e.code == 404 and ok404:
                    return None
                if e.code in (502, 503, 504) or (e.code == 403 and "rate limit" in txt.lower()):
                    time.sleep(5 * (attempt + 1))
                    continue
                raise RuntimeError(f"GitHub {method} {path} -> {e.code}: {txt[:400]}") from None
            except (urllib.error.URLError, TimeoutError) as e:
                time.sleep(5 * (attempt + 1))
                last = e
        raise RuntimeError(f"GitHub {method} {path} failed after retries: {last}")  # noqa: F821

    def r(self, method: str, sub: str, body=None, **kw):
        return self.req(method, f"/repos/{self.repo}{sub}", body, **kw)

    def pages(self, sub: str, per_page: int = 100):
        out, page = [], 1
        while True:
            sep = "&" if "?" in sub else "?"
            got = self.r("GET", f"{sub}{sep}per_page={per_page}&page={page}") or []
            out += got
            if len(got) < per_page:
                return out
            page += 1

    def graphql(self, query: str, variables: dict) -> dict:
        res = self.req("POST", f"{self.api}/graphql", {"query": query, "variables": variables})
        if res.get("errors"):
            raise RuntimeError(f"GraphQL: {json.dumps(res['errors'])[:400]}")
        return res["data"]

    def status(self, sha: str, context: str, state: str, desc: str, url: str | None = None):
        body = {"state": state, "context": context, "description": desc[:140]}
        if url:
            body["target_url"] = url
        return self.r("POST", f"/statuses/{sha}", body)


# --------------------------------------------------------------------------------------------------
# Package files at the PR head, corpus documents
# --------------------------------------------------------------------------------------------------
_ROW = re.compile(r"^\|[ \t]*(Doc ID|Title|Revision|Owner)[ \t]*\|[ \t]*([^|\n]+?)[ \t]*\|[ \t]*$", re.M)


def fetch_files(gh: GH, sha: str) -> dict[str, str]:
    tree = gh.r("GET", f"/git/trees/{sha}?recursive=1")
    out = {}
    for t in tree.get("tree") or []:
        p = t.get("path", "")
        if t.get("type") == "blob" and re.fullmatch(r"(package|rulebook)/[^/]+\.md", p):
            blob = gh.r("GET", f"/git/blobs/{t['sha']}")
            out[p] = base64.b64decode(blob["content"]).decode("utf-8")
    return out


def build_docs(files: dict[str, str], rev_label: str) -> list[dict]:
    docs = []
    for path in sorted(files):
        text = files[path]
        if path.endswith("README.md"):
            continue
        fields: dict[str, str] = {}
        for k, val in _ROW.findall(text[:3000]):
            fields.setdefault(k, val)
        stem = Path(path).stem
        slug = re.sub(r"^\d+_", "", stem)
        shared = path.startswith("rulebook/")
        rev = "shared" if shared else rev_label
        docs.append({"id": f"{PROJECT_CODE.lower()}_{rev}_{stem}", "path": path, "text": text, "shared": shared,
                     "revision_field": fields.get("Revision", ""),
                     "metadata": {"project": PROJECT_CODE, "revision": rev, "doc_type": slug,
                                  "doc_id": fields.get("Doc ID", slug), "package_doc_id": fields.get("Doc ID", slug),
                                  "title": fields.get("Title", slug.replace("_", " "))}})
    return docs


def package_letter(docs: list[dict]) -> str:
    """The package's own revision letter ("B (supersedes A)" -> "B"), as the documents state it."""
    letters = [m.group(1) for d in docs if not d["shared"]
               for m in [re.match(r"\s*([A-Z])\b", d["revision_field"] or "")] if m]
    return max(set(letters), key=letters.count) if letters else ""


def revision_filter(rev: str) -> str:
    return f"doc.project = '{PROJECT_CODE}' AND doc.revision IN ('{rev}','shared')"


def ingest(c: v.Client, docs: list[dict]) -> None:
    for d in docs:
        if d["shared"]:
            continue  # the rulebook is already in the corpus as revision 'shared'
        t0 = time.time()
        c.index_markdown(CORPUS, d["id"], d["text"], d["metadata"], title=d["metadata"]["title"])
        log(f"  indexed {d['id']} ({len(d['text'])} B, {time.time() - t0:.1f}s)")


# --------------------------------------------------------------------------------------------------
# Quote verification (same normalization as the project's run_review.py)
# --------------------------------------------------------------------------------------------------
_DASHES = str.maketrans({c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"})
_QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'})
_SEP_ROW = re.compile(r"^\s*\|?[\s:\-|]+\|?\s*$")
_ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).translate(_DASHES).translate(_QUOTES)
    s = s.replace("\u00a0", " ").replace("°", " ")
    s = re.sub(r"(?i)<br\s*/?>", " ", s)
    s = re.sub(r"(?m)^\s*#{1,6}\s+", "", s)
    s = s.replace("**", "").replace("`", "").replace("|", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\.+\s*", ".", s)
    return s.strip().lower()


def _norm_lines(text: str) -> list[str]:
    return [n for n in (normalize(l) for l in text.splitlines() if not _SEP_ROW.match(l)) if n]


class Grounder:
    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.flat = {d["path"]: " ".join(_norm_lines(d["text"])) for d in docs}
        self.lines = {d["path"]: [normalize(l) for l in d["text"].splitlines()] for d in docs}

    def resolve(self, document: str) -> dict | None:
        s = str(document or "").lower()
        for d in self.docs:
            if Path(d["path"]).stem.lower() in s:
                return d
        hits = [d for d in self.docs if d["metadata"]["doc_id"].lower() in s]
        if hits:
            return max(hits, key=lambda d: len(d["metadata"]["doc_id"]))
        for d in self.docs:
            if d["metadata"]["title"].lower() in s:
                return d
        return None

    def quote_in(self, quote: str, path: str) -> bool:
        flat = self.flat[path]
        q = " ".join(_norm_lines(quote))
        if not q:
            return False
        if q in flat:
            return True
        parts = [normalize(p) for l in quote.splitlines() if not _SEP_ROW.match(l) for p in _ELLIPSIS.split(l)]
        parts = [p for p in parts if len(p) >= 3]
        return bool(parts) and all(p in flat for p in parts) and sum(len(p) for p in parts) >= 12

    def check(self, ev: dict) -> dict:
        doc = self.resolve(ev.get("document", ""))
        quote = ev.get("quote", "")
        res = {"document": ev.get("document", ""), "path": None, "verified": False, "lines": []}
        cands = ([doc] if doc else []) + [d for d in self.docs if d is not doc]
        for d in cands:
            if self.quote_in(quote, d["path"]):
                res.update(path=d["path"], verified=True, lines=self.locate(quote, d["path"]),
                           where="cited document" if d is doc else "other document")
                return res
        if doc:
            res["path"] = doc["path"]
        return res

    def locate(self, quote: str, path: str) -> list[int]:
        """1-based file lines that carry the quote (table header rows dropped when data rows match)."""
        lines = self.lines[path]
        qlines = [l for l in quote.splitlines() if l.strip() and not _SEP_ROW.match(l)]
        hits = []
        for i, ql in enumerate(qlines):
            parts = sorted((normalize(p) for p in _ELLIPSIS.split(ql)), key=len, reverse=True)
            part = parts[0] if parts else ""
            if len(part) < 3:
                continue
            for n, fl in enumerate(lines, 1):
                if fl and part in fl:
                    hits.append((i, n))
                    break
        if not hits:
            return []
        is_table = all(l.strip().startswith("|") for l in qlines)
        if is_table and len(hits) > 1:
            hits = [h for h in hits if h[0] > 0] or hits  # drop the header row
        nums = sorted({n for _, n in hits})
        return nums

    def closest(self, quote: str, path: str | None) -> str:
        """The file line most similar to the failing quote (for the correction turn)."""
        if not path:
            return ""
        raw = [d for d in self.docs if d["path"] == path][0]["text"].splitlines()
        target = normalize(quote.splitlines()[-1] if quote.strip() else quote)
        best, score = "", 0.0
        for l in raw:
            if len(l.strip()) < 8 or _SEP_ROW.match(l):
                continue
            s = difflib.SequenceMatcher(None, target, normalize(l)).ratio()
            if s > score:
                best, score = l.strip(), s
        return best

    def annotate(self, report: dict) -> dict:
        tot = ok = 0
        failing = []
        for f in report.get("findings") or []:
            checks = [self.check(e) for e in f.get("evidence") or []]
            f["_checks"] = checks
            for e, ch in zip(f.get("evidence") or [], checks):
                tot += 1
                ok += int(ch["verified"])
                if not ch["verified"]:
                    failing.append({"finding": f.get("id"), "document": e.get("document"), "quote": e.get("quote"),
                                    "closest": self.closest(e.get("quote", ""), ch["path"])})
        return {"quotes_total": tot, "quotes_verified": ok, "failing": failing}


# --------------------------------------------------------------------------------------------------
# Vectara turns
# --------------------------------------------------------------------------------------------------
def engineer_message(round_no: int, letter: str, prev_letter: str, prev_findings: list[dict]) -> str:
    """Same wording as the project's run_review.py loop mode (the measured engineer message)."""
    trr = f"TRR-{round_no}"
    if not prev_findings and round_no == 1:
        return (f"{trr}: the ALX-5100 KESTREL (project code KST) tape-out package revision {letter} is released "
                f"for the tape-out readiness review. Please run the ALD-QA-CHK-007 gate on revision {letter} and "
                "give me the GO / NO_GO decision with cited findings and the respin exposure.")
    lines = [" | ".join([f["id"], f.get("title", ""), ", ".join(f.get("rule_ids") or []), f.get("status", "")])
             for f in prev_findings]
    prev_block = "\n".join(f"- {l}" for l in lines) if lines else "- none"
    return (f"{trr}: package rev {letter} is released for review. The block owners have updated the package since "
            f"the revision {prev_letter} gate review; the documents carry their revision history and the ECO log "
            f"lists the changes. Please re-run the gate on revision {letter}: tell me what closed, what is still "
            "open and whether anything new came in, and give me the GO / NO_GO decision.\n\n"
            f"Previously open findings from the revision {prev_letter} gate report (id | title | rule IDs | status):\n"
            f"{prev_block}")


def run_turn(c: v.Client, agent: str, session: str, text: str, *, entry_step: str | None = None,
             max_wait: float = 2400) -> list[dict]:
    """One turn, fire-and-poll; never re-sends a turn that may have landed (it would merge)."""
    before = (c.newest_event(agent, session) or {}).get("id")
    try:
        return c.send_and_wait(agent, session, text, entry_step=entry_step, mode="poll", fire_timeout_s=5,
                               poll=5, max_wait=max_wait)
    except v.TurnError as e:
        log(f"  turn error on {agent}: {str(e)[:300]}")
        return c.events_since(agent, session, before)
    except Exception as e:  # noqa: BLE001
        log(f"  turn transport problem on {agent}: {type(e).__name__}: {str(e)[:200]}; resuming the poll")
        try:
            return c.wait_for_turn(agent, session, before, poll=5, max_wait=max_wait, raise_on_error=False)
        except Exception as e2:  # noqa: BLE001
            log(f"  poll failed: {type(e2).__name__}: {str(e2)[:200]}")
            return c.events_since(agent, session, before)


def one_shot(c: v.Client, agent: str, text: str, schema: str | None = None, max_wait: float = 600):
    s = c.create_session(agent, None, {})
    ev = run_turn(c, agent, s["key"], text, max_wait=max_wait)
    return (v.last_structured_output(ev, schema) if schema else v.final_text(ev)), s["key"]


def report_for_llm(rep: dict) -> dict:
    keep = ["project", "revision", "gate", "summary", "findings", "total_cost_exposure_usd", "closed_since_previous",
            "questions_for_engineer"]
    out = {k: rep.get(k) for k in keep}
    out["findings"] = [{k: val for k, val in f.items() if not k.startswith("_")} for f in rep.get("findings") or []]
    return out


def io_summary(c: v.Client, rep: dict, sched: dict) -> tuple[str, str]:
    payload = {**report_for_llm(rep), "schedule_exposure": sched}
    msg = ("Here is a tape-out readiness report from our review agent. Please explain it for a non-engineer.\n\n"
           + json.dumps(payload, indent=1))
    try:
        text, _ = one_shot(c, IO_EXPLAINER, msg, max_wait=300)
        if text and text.strip():
            return text.strip(), IO_EXPLAINER
    except Exception as e:  # noqa: BLE001
        log(f"  io explainer failed: {type(e).__name__}: {str(e)[:200]}")
    return (rep.get("summary") or "").strip(), "gate summary (io helper unavailable)"


def plain_comments(c: v.Client, rep: dict) -> dict:
    payload = {k: rep.get(k) for k in ("gate", "summary", "closed_since_previous")}
    payload["findings"] = [{k: f.get(k) for k in ("id", "title", "status", "rule_ids", "evidence", "reasoning",
                                                  "recommended_fix", "block")} for f in rep.get("findings") or []]
    try:
        out, _ = one_shot(c, PLAIN_WRITER, json.dumps(payload), PLAIN_SCHEMA, max_wait=300)
        return out or {}
    except Exception as e:  # noqa: BLE001
        log(f"  plain writer failed: {type(e).__name__}: {str(e)[:200]}")
        return {}


def specialist_stats(c: v.Client, events: list[dict]) -> dict:
    """Documents opened and checks run by the 7 specialists (their sub-sessions persist)."""
    docs, lambdas, searches, calls = set(), 0, 0, 0
    for r in v.sub_agent_results(events):
        sk = r.get("session_key")
        tool = str(r.get("tool") or "")
        agent = "rsp_kst_" + ("spec_consistency" if tool.startswith("spec") else tool.replace("_review", ""))
        if not sk:
            continue
        calls += 1
        try:
            sev = c.list_events(agent, sk)
        except Exception:  # noqa: BLE001
            continue
        for e in sev:
            if e.get("type") != "tool_input":
                continue
            name = e.get("tool_configuration_name")
            ti = e.get("tool_input") or {}
            if name == "read_document":
                docs.add(str(ti.get("document_id") or ti.get("doc_id") or ""))
            elif name == "search_package":
                searches += 1
            else:
                lambdas += 1
    return {"specialists": calls, "documents_read": len({d for d in docs if d}), "calculator_checks": lambdas,
            "searches": searches}


# --------------------------------------------------------------------------------------------------
# State carried between pushes (hidden in the sticky summary comment)
# --------------------------------------------------------------------------------------------------
def find_summary(gh: GH, pr: int) -> dict | None:
    for cm in gh.pages(f"/issues/{pr}/comments"):
        if SUMMARY_MARK in (cm.get("body") or ""):
            return cm
    return None


def load_state(comment: dict | None) -> dict:
    if comment:
        m = STATE_RE.search(comment.get("body") or "")
        if m:
            return json.loads(base64.b64decode(m.group(1)).decode())
    return {"v": 1, "rounds": [], "findings": {}, "closed": {}}


def session_key(repo: str, pr: int) -> str:
    short = re.sub(r"[^a-z0-9]+", "_", repo.split("/")[-1].lower()).strip("_")
    return f"rsp_ci_{short}_pr{pr}"


def area_of(f: dict) -> str:
    for r in f.get("rule_ids") or []:
        for pre, area in AREA_RULE_PREFIX:
            if r.startswith(pre):
                return area
    return {"errata": "ip_errata", "process": "governance", "other": "governance"}.get(f.get("category"),
                                                                                     f.get("category") or "governance")


def money(x) -> str:
    x = float(x or 0)
    if x >= 1e6:
        return f"${x / 1e6:.1f}M".replace(".0M", "M")
    if x >= 1e3:
        return f"${x / 1e3:.0f}K"
    return f"${x:.0f}"


def schedule(rep: dict) -> dict:
    weeks = [float(f["schedule_impact_weeks"]) for f in rep.get("findings") or []
             if isinstance(f.get("schedule_impact_weeks"), (int, float)) and f.get("respin_type") not in (None, "none")]
    w = max(weeks) if weeks else 0.0
    return {"weeks": w, "months": round(w / (52 / 12), 1)}


def fmt_dur(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s"


# --------------------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------------------
def md_quote(q: str) -> str:
    lines = [l.rstrip() for l in str(q or "").strip().splitlines() if l.strip()]
    if len(lines) >= 2 and all(l.lstrip().startswith("|") for l in lines) and not _SEP_ROW.match(lines[1]):
        ncol = lines[0].strip().strip("|").count("|") + 1
        lines.insert(1, "|" + "---|" * ncol)
    if len(lines) == 1 and lines[0].lstrip().startswith("|"):
        ncol = lines[0].strip().strip("|").count("|") + 1
        lines = ["|" + " |" * ncol, "|" + "---|" * ncol] + lines  # a lone table row still renders as a table
    return "\n".join("> " + l for l in lines)


def blob_link(repo: str, sha: str, path: str, lines: list[int]) -> str:
    anchor = f"#L{lines[0]}" + (f"-L{lines[-1]}" if len(lines) > 1 and lines[-1] != lines[0] else "") if lines else ""
    return f"https://github.com/{repo}/blob/{sha}/{path}{anchor}"


def finding_comment(f: dict, p: dict, ev_idx: int, round_no: int, sha: str, repo: str) -> str:
    ev = (f.get("evidence") or [])[ev_idx]
    ch = f["_checks"][ev_idx]
    title = p.get("plain_title") or f.get("title")
    badge = ""
    if f.get("status") == "new" and round_no > 1:
        cause = p.get("caused_by_change")
        badge = (f"**🆕 New in this push**" + (f" · introduced by {cause}" if cause else "") + "\n\n")
    head = "🛑" if f.get("blocking") else "⚠️"
    rt = f.get("respin_type") or "none"
    wk = f.get("schedule_impact_weeks")
    cost = (f"**{money(f.get('cost_exposure_usd'))}** ({RESPIN_PLAIN.get(rt, rt)})"
            + (f" and about **{wk:g} weeks** of delay" if isinstance(wk, (int, float)) and wk else ""))
    body = [FIND_MARK.format(f["id"]), f"### {head} {title}", "", badge + (p.get("what_is_wrong") or f.get("title", ""))]
    body += ["", f"**Why it blocks:** {p.get('why_it_blocks') or 'The rulebook marks this rule as blocking.'}"]
    if p.get("analogy"):
        body += [f"*Think of it like this:* {p['analogy']}"]
    body += ["", f"**If it reaches the factory:** {cost}",
             f"**Rule:** {', '.join('`' + r + '`' for r in f.get('rule_ids') or [])} · **Owner:** {f.get('owner') or 'not named in the package'}",
             "", md_quote(ev.get("quote", "")), "",
             f"<sub>✓ quote verified word for word in `{ch['path']}`"
             + (f" (line {ch['lines'][0]})" if ch.get("lines") else "") + " · reply `/tapeout explain` to ask the reviewer</sub>"]
    others = [(e, c) for i, (e, c) in enumerate(zip(f.get("evidence") or [], f["_checks"])) if i != ev_idx]
    det = [f"**Engineering title:** {f.get('title')}", "", f"**Reasoning:** {f.get('reasoning', '')}", "",
           f"**Recommended fix:** {f.get('recommended_fix', '')}"]
    if others:
        det += ["", "**Other evidence:**"]
        for e, c2 in others:
            loc = (f"[`{c2['path']}`" + (f" L{c2['lines'][0]}" if c2.get("lines") else "") + f"]({blob_link(repo, sha, c2['path'], c2.get('lines') or [])})") \
                if c2.get("verified") else f"`{e.get('document')}` (⚠ quote not found)"
            q = re.sub(r"\s+", " ", str(e.get("quote", "")))[:220]
            det += [f"- {loc}: “{q}”"]
    body += ["", "<details><summary>Engineering details</summary>", "", *det, "", "</details>"]
    return "\n".join(body)


def pick_evidence(f: dict, p: dict) -> int | None:
    """Index of the evidence to anchor the inline comment: the writer's 'fix here' pick if it is a verified
    quote in a package file, else the first such quote."""
    checks = f["_checks"]
    ok = [i for i, c in enumerate(checks) if c["verified"] and c["path"] and c["path"].startswith("package/") and c["lines"]]
    pick = p.get("fix_here_evidence_index")
    if isinstance(pick, int) and pick in ok:
        return pick
    return ok[0] if ok else None


# --------------------------------------------------------------------------------------------------
# review
# --------------------------------------------------------------------------------------------------
def cmd_review(a, gh: GH) -> int:
    pr = gh.r("GET", f"/pulls/{a.pr}")
    if (pr.get("head") or {}).get("repo", {}).get("full_name") != gh.repo:
        log("PR comes from a fork: the gate does not run with secrets on fork PRs")
        return 0
    sha = a.sha or pr["head"]["sha"]
    sha7 = sha[:7]
    run_url = os.environ.get("RUN_URL") or pr["html_url"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t_all = time.time()

    gh.status(sha, "tapeout/gate", "pending", "AI review board: 7 specialists reading the tape-out package…", run_url)
    for area in AREAS:
        name, _ = AREA_PLAIN[area]
        gh.status(sha, f"tapeout/{AREA_LABEL[area]}", "pending", f"AI {name.lower()} specialist reviewing…", run_url)

    summary_cm = find_summary(gh, a.pr)
    state = load_state(summary_cm)
    round_no = len(state["rounds"]) + 1
    files = fetch_files(gh, sha)
    rev_label = f"ci-{re.sub(r'[^a-z0-9]+', '-', gh.repo.split('/')[-1].lower())}-pr{a.pr}-{sha7}"
    docs = build_docs(files, rev_label)
    pkg = [d for d in docs if not d["shared"]]
    if not pkg:
        gh.status(sha, "tapeout/gate", "error", "No package/*.md documents in this commit", run_url)
        return 1
    letter = package_letter(docs) or rev_label
    log(f"PR #{a.pr} round {round_no} @ {sha7}: {len(pkg)} package docs (package revision {letter}), corpus revision {rev_label}")

    c = v.Client(turn_timeout=900)
    ingest(c, docs)
    skey = session_key(gh.repo, a.pr)
    doc_index = "; ".join(f"{d['id']} | {d['metadata']['doc_id']} | {d['metadata']['title']}" for d in docs)
    prev_letter = state["rounds"][-1]["letter"] if state["rounds"] else ""
    md = {"project": PROJECT_NAME, "project_code": PROJECT_CODE, "revision": letter,
          "previous_revision": prev_letter, "rev_filter": revision_filter(rev_label), "doc_index": doc_index,
          "rsp_run": f"ci_{gh.repo.split('/')[-1]}_pr{a.pr}", "ci_commit": sha7}
    if c.get_session(GATE_KEY, skey):
        c.patch_session_metadata(GATE_KEY, skey, md)
        log(f"continuing gate session {skey} (loop memory), metadata -> {rev_label}")
    else:
        c.create_session(GATE_KEY, skey, md, tti_minutes=10080, if_exists="reuse")
        log(f"created gate session {skey}")
    status = (c.get_session(GATE_KEY, skey) or {}).get("status")
    if status == "running":
        log("gate session busy; waiting for it to finish first")
        c.wait_for_turn(GATE_KEY, skey, None, poll=10, max_wait=1800, raise_on_error=False)

    prev_findings = [{"id": k, **val} for k, val in state["findings"].items()]
    msg = engineer_message(round_no, letter, prev_letter, prev_findings)
    t0 = time.time()
    events = run_turn(c, GATE_KEY, skey, msg)
    rep = v.last_structured_output(events, GATE_SCHEMA)
    gate_wall = time.time() - t0
    if not rep:
        errs = [e for e in events if e.get("type") == "error"]
        gh.status(sha, "tapeout/gate", "error", "The AI review did not finish; re-run the job", run_url)
        for area in AREAS:
            gh.status(sha, f"tapeout/{AREA_LABEL[area]}", "error", "No verdict (review did not finish)", run_url)
        (out / "events.json").write_text(json.dumps(events, indent=1))
        log(f"no gate report ({len(events)} events, errors: {json.dumps(errs)[:300]})")
        return 1
    log(f"gate: {rep.get('gate')} · {len(rep.get('findings') or [])} findings · {gate_wall:.0f}s")

    grounder = Grounder(docs)
    g = grounder.annotate(rep)
    corrected, correction = 0, None
    if g["failing"]:
        log(f"  {len(g['failing'])} quote(s) not found word for word; sending ONE correction turn")
        lines = [f"- finding {x['finding']}, document {x['document']}: quoted “{x['quote']}”"
                 + (f"; the closest line actually in that document is “{x['closest']}”" if x["closest"] else "")
                 for x in g["failing"]]
        cmsg = (f"{CORRECTION_PREFIX}: {len(g['failing'])} evidence quote(s) in your revision {letter} report "
                "do not appear word for word in the cited documents:\n" + "\n".join(lines) +
                "\n\nRe-issue the complete gate report for this revision with the same findings, verdicts, costs and "
                "statuses, replacing each failing quote with the exact text from the document (copy it character "
                "for character), or dropping that evidence item if no exact text supports it.")
        cev = run_turn(c, GATE_KEY, skey, cmsg, entry_step="report", max_wait=900)
        rep2 = v.last_structured_output(cev, GATE_SCHEMA)
        if rep2 and rep2.get("gate") == rep.get("gate"):
            g2 = grounder.annotate(rep2)
            corrected = max(0, len(g["failing"]) - len(g2["failing"]))
            correction = {"failing_before": g["failing"], "failing_after": g2["failing"], "corrected": corrected}
            if len(g2["failing"]) <= len(g["failing"]):
                rep, g = rep2, g2
            log(f"  correction turn: {corrected} corrected, {len(g['failing'])} still unverified")
        else:
            correction = {"failing_before": g["failing"], "failing_after": g["failing"], "corrected": 0,
                          "note": "correction turn returned no usable report; original kept"}
            log("  correction turn returned no usable report; keeping the original")

    stats = specialist_stats(c, events)
    sched = schedule(rep)
    plain = plain_comments(c, rep)
    io_text, io_src = io_summary(c, rep, sched)
    log(f"plain writer: {len(plain.get('findings') or [])} findings; io summary from {io_src}")

    result = {"pr": a.pr, "sha": sha, "round": round_no, "rev_label": rev_label, "letter": letter,
              "session": skey, "gate_wall_s": round(gate_wall, 1), "stats": stats, "grounding": g,
              "correction": correction, "schedule": sched, "plain": plain, "io_summary": io_text, "io_source": io_src,
              "report": json.loads(json.dumps(rep))}
    for f in result["report"].get("findings") or []:
        f.pop("_checks", None)
    (out / "report.json").write_text(json.dumps(result, indent=1))
    rep_with_checks = rep  # still carries _checks
    publish(gh, a.pr, sha, round_no, letter, rep_with_checks, plain, g, corrected, stats, sched, io_text, io_src,
            state, summary_cm, run_url, gate_wall, time.time() - t_all)
    log(f"published round {round_no} in {time.time() - t_all:.0f}s total")
    return 0


def publish(gh: GH, pr_no: int, sha: str, round_no: int, letter: str, rep: dict, plain: dict, g: dict,
            corrected: int, stats: dict, sched: dict, io_text: str, io_src: str, state: dict,
            summary_cm: dict | None, run_url: str, gate_wall: float, total_wall: float) -> None:
    sha7 = sha[:7]
    pf = {x.get("id"): x for x in plain.get("findings") or []}
    pc = {x.get("id"): x for x in plain.get("closed") or []}
    findings = rep.get("findings") or []
    blocking = [f for f in findings if f.get("blocking")]
    usd = rep.get("total_cost_exposure_usd") or 0
    go = rep.get("gate") == "GO"

    # ---- threads from earlier rounds
    threads = {}
    try:
        owner, name = gh.repo.split("/")
        data = gh.graphql("""query($o:String!,$n:String!,$pr:Int!){repository(owner:$o,name:$n){pullRequest(number:$pr){
            reviewThreads(first:100){nodes{id isResolved comments(first:1){nodes{databaseId body}}}}}}}""",
                          {"o": owner, "n": name, "pr": pr_no})
        for t in data["repository"]["pullRequest"]["reviewThreads"]["nodes"]:
            cm = (t["comments"]["nodes"] or [{}])[0]
            m = FIND_RE.search(cm.get("body") or "")
            if m:
                threads[m.group(1)] = {"thread": t["id"], "resolved": t["isResolved"], "comment_id": cm["databaseId"]}
    except Exception as e:  # noqa: BLE001
        log(f"  could not list review threads: {e}")

    prev = state["findings"]
    # The gate reuses finding ids across rounds; if it renamed one it still calls still_open, map it back by rule.
    used = {f["id"] for f in findings if f["id"] in prev}
    for f in findings:
        if f["id"] not in prev and f.get("status") == "still_open":
            for pid, pv in prev.items():
                if pid not in used and set(pv.get("rule_ids") or []) & set(f.get("rule_ids") or []):
                    log(f"  mapping renamed finding {f['id']} -> {pid}")
                    f["id"] = pid
                    used.add(pid)
                    break
    cur_ids = {f["id"] for f in findings}
    closed_rows = []
    closed_by_gate = {c.get("id"): c for c in rep.get("closed_since_previous") or []}
    for fid, pv in prev.items():
        if fid in cur_ids:
            continue
        cl = closed_by_gate.get(fid)
        how = (pc.get(fid) or {}).get("how_fixed") or (cl or {}).get("how_closed") or "No longer reported by the review."
        closed_rows.append({"id": fid, "title": (pc.get(fid) or {}).get("plain_title") or pv.get("plain_title") or pv.get("title"),
                            "how": how, "area": pv.get("area")})
        th = threads.get(fid)
        if th:
            try:
                gh.r("POST", f"/pulls/{pr_no}/comments/{th['comment_id']}/replies",
                     {"body": f"✅ **Fixed in `{sha7}`** — {how}\n\n<sub>Confirmed by the AI review board in round {round_no}; resolving this thread.</sub>"})
                if not th["resolved"]:
                    gh.graphql("mutation($t:ID!){resolveReviewThread(input:{threadId:$t}){thread{isResolved}}}",
                               {"t": th["thread"]})
            except Exception as e:  # noqa: BLE001
                log(f"  reply/resolve failed for {fid}: {e}")
        state["closed"][fid] = sha7

    # ---- inline comments: new findings get a comment on their line; still-open ones a reply on their thread
    review_comments, unanchored, comment_for = [], [], {}
    for f in findings:
        p = pf.get(f["id"], {})
        th = threads.get(f["id"])
        if th and f["id"] in prev:
            try:
                gh.r("POST", f"/pulls/{pr_no}/comments/{th['comment_id']}/replies",
                     {"body": f"⏳ **Still open in `{sha7}`** — {p.get('what_is_wrong') or f.get('title')}\n\n"
                              f"<sub>Round {round_no} of the AI review board. Still blocking: {money(f.get('cost_exposure_usd'))} at risk.</sub>"})
                if th["resolved"]:
                    gh.graphql("mutation($t:ID!){unresolveReviewThread(input:{threadId:$t}){thread{isResolved}}}",
                               {"t": th["thread"]})
            except Exception as e:  # noqa: BLE001
                log(f"  still-open reply failed for {f['id']}: {e}")
            comment_for[f["id"]] = th["comment_id"]
            continue
        idx = pick_evidence(f, p)
        if idx is None:
            unanchored.append(f)
            continue
        ch = f["_checks"][idx]
        ln = ch["lines"]
        rc = {"path": ch["path"], "line": ln[-1], "side": "RIGHT",
              "body": finding_comment(f, p, idx, round_no, sha, gh.repo)}
        if len(ln) > 1 and ln[-1] - ln[0] == len(ln) - 1 and len(ln) <= 6:
            rc.update(start_line=ln[0], start_side="RIGHT")
        review_comments.append((f, rc))

    n_new = sum(1 for f in findings if f["id"] not in prev and round_no > 1)
    n_still = sum(1 for f in findings if f["id"] in prev)
    if go:
        rbody = (f"## ✅ Round {round_no}: GO — no blocking problems\n\nThe AI review board found nothing that blocks "
                 f"tape-out in `{sha7}`." + (f" {len(closed_rows)} problem(s) fixed since the last round." if closed_rows else "")
                 + "\n\nThe review board (people) makes the final call.")
    else:
        bits = [f"**{len(blocking)} blocking problem{'s' if len(blocking) != 1 else ''}**", f"**{money(usd)} at risk**"]
        if round_no > 1:
            bits.append(f"✅ {len(closed_rows)} fixed · ⏳ {n_still} still open · 🆕 {n_new} new")
        rbody = (f"## 🛑 Round {round_no}: STOP — not ready for the factory\n\n" + " · ".join(bits)
                 + "\n\nEach problem is pinned to the exact line that proves it. The summary comment has the full table.")
    if unanchored:
        rbody += "\n\n**Problems without a line in this PR** (their evidence is in the rulebook):\n" + "\n".join(
            f"- 🛑 {(pf.get(f['id']) or {}).get('plain_title') or f.get('title')}" for f in unanchored)
    review = None
    payload = {"commit_id": sha, "event": "COMMENT", "body": rbody, "comments": [rc for _, rc in review_comments]}
    try:
        review = gh.r("POST", f"/pulls/{pr_no}/reviews", payload)
    except Exception as e:  # noqa: BLE001
        log(f"  review with inline comments failed ({str(e)[:200]}); retrying one comment at a time")
        review = gh.r("POST", f"/pulls/{pr_no}/reviews", {"commit_id": sha, "event": "COMMENT", "body": rbody,
                                                         "comments": []})
        for f, rc in review_comments:
            try:
                gh.r("POST", f"/pulls/{pr_no}/comments", {"commit_id": sha, **rc})
            except Exception as e2:  # noqa: BLE001
                log(f"  inline comment for {f['id']} failed: {str(e2)[:200]}")
    # top-level comment per finding: keep the thread already tracked (still open), else the newest comment
    comment_urls = {}
    try:
        for cm in gh.pages(f"/pulls/{pr_no}/comments"):
            m = FIND_RE.search(cm.get("body") or "")
            if m and not cm.get("in_reply_to_id"):
                fid = m.group(1)
                if fid not in comment_for or fid not in prev:
                    comment_for[fid] = cm["id"]
                    comment_urls[fid] = cm["html_url"]
                elif cm["id"] == comment_for[fid]:
                    comment_urls[fid] = cm["html_url"]
    except Exception:  # noqa: BLE001
        pass

    # ---- statuses
    for area in AREAS:
        name, _ = AREA_PLAIN[area]
        af = [f for f in findings if area_of(f) == area and f.get("blocking")]
        verdict = (rep.get("area_status") or {}).get(area, "FAIL" if af else "PASS")
        if af:
            t = (pf.get(af[0]["id"]) or {}).get("plain_title") or af[0].get("title")
            desc = f"{len(af)} blocking: {t}" + (f" (+{len(af) - 1} more)" if len(af) > 1 else "")
            gh.status(sha, f"tapeout/{AREA_LABEL[area]}", "failure", desc,
                      comment_urls.get(af[0]["id"]) or run_url)
        elif verdict == "FAIL":
            gh.status(sha, f"tapeout/{AREA_LABEL[area]}", "failure", f"AI {name.lower()} specialist: a rule fails", run_url)
        else:
            gh.status(sha, f"tapeout/{AREA_LABEL[area]}", "success", f"AI {name.lower()} specialist: no blocking problems", run_url)

    # ---- sticky summary
    state["rounds"].append({"round": round_no, "sha": sha7, "letter": letter, "gate": rep.get("gate"),
                            "blocking": len(blocking), "usd": usd, "weeks": sched["weeks"],
                            "fixed": len(closed_rows), "new": n_new, "still": n_still,
                            "quotes": f"{g['quotes_verified']}/{g['quotes_total']}", "secs": round(gate_wall)})
    state["findings"] = {f["id"]: {"title": f.get("title"), "plain_title": (pf.get(f["id"]) or {}).get("plain_title"),
                                   "rule_ids": f.get("rule_ids"), "status": f.get("status"), "area": area_of(f),
                                   "comment_id": comment_for.get(f["id"])} for f in findings}
    body = summary_body(gh.repo, pr_no, sha, round_no, rep, pf, closed_rows, g, corrected, stats, sched, io_text,
                        io_src, state, comment_urls, run_url, gate_wall)
    if summary_cm:
        cm = gh.r("PATCH", f"/issues/comments/{summary_cm['id']}", {"body": body})
    else:
        cm = gh.r("POST", f"/issues/{pr_no}/comments", {"body": body})
    gate_desc = ("GO: no blocking problems · people make the final call" if go else
                 f"STOP: {len(blocking)} blocking problem{'s' if len(blocking) != 1 else ''} · {money(usd)} at risk")
    gh.status(sha, "tapeout/gate", "success" if go else "failure", gate_desc, cm.get("html_url") or run_url)


def summary_body(repo, pr_no, sha, round_no, rep, pf, closed_rows, g, corrected, stats, sched, io_text, io_src,
                 state, comment_urls, run_url, gate_wall) -> str:
    sha7 = sha[:7]
    findings = rep.get("findings") or []
    blocking = [f for f in findings if f.get("blocking")]
    usd = rep.get("total_cost_exposure_usd") or 0
    go = rep.get("gate") == "GO"
    L = [SUMMARY_MARK]
    if go:
        L += ["# ✅ GO — ready for the factory", "",
              f"**No blocking problems in `{sha7}`.** The AI review board recommends tape-out; the review board (people) makes the final call."]
    else:
        L += ["# 🛑 STOP — not ready for the factory", "",
              f"**{len(blocking)} blocking problem{'s' if len(blocking) != 1 else ''} · {money(usd)} at risk if this ships as is"
              + (f" · about {sched['months']:g} months of delay" if sched["weeks"] else "") + "**"]
    L += ["", f"> Reviewed by **7 AI specialists** in **{fmt_dur(gate_wall)}** · {stats.get('documents_read') or 16} documents read · "
              f"{len(rep.get('rule_results') or {}) or 38} rulebook checks · {stats.get('calculator_checks', 0)} calculator checks · "
              f"**{g['quotes_verified']}/{g['quotes_total']} quotes verified ✓**"
              + (f" ({corrected} corrected by the agent)" if corrected else "")
              + f" · round {round_no} · commit `{sha7}`", ""]
    if round_no > 1:
        last = state["rounds"][-1]
        L += [f"**Since the last push:** ✅ {last['fixed']} fixed · ⏳ {last['still']} still open · 🆕 {last['new']} new", ""]
    if findings or closed_rows:
        L += ["| | Problem | Area | Status | If it reaches the factory | Owner |", "|---|---|---|---|---|---|"]
        for f in findings:
            p = pf.get(f["id"]) or {}
            t = p.get("plain_title") or f.get("title")
            link = comment_urls.get(f["id"])
            st = {"new": "🆕 New" if round_no > 1 else "Open", "still_open": "⏳ Still open"}.get(f.get("status"), "Open")
            if f["id"] in (state.get("closed") or {}) and f.get("status") != "still_open":
                st = "🔁 Re-opened"
            wk = f.get("schedule_impact_weeks")
            cost = money(f.get("cost_exposure_usd")) + (f" · {wk:g} wk" if isinstance(wk, (int, float)) and wk else "")
            L.append(f"| {'🛑' if f.get('blocking') else '⚠️'} | {'[' + t + '](' + link + ')' if link else t} | "
                     f"{AREA_PLAIN[area_of(f)][0]} | {st} | {cost} | {(f.get('owner') or '—').replace('|', '/')} |")
        for c in closed_rows:
            L.append(f"| ✅ | ~~{c['title']}~~ | {AREA_PLAIN.get(c.get('area') or '', ('—',))[0]} | Fixed in `{sha7}` | — | — |")
        L += [""]
        if len(blocking) > 1:
            L += [f"<sub>One factory redo would fix every problem at once, so the money at risk is the biggest single redo "
                  f"({money(usd)}), not the sum.</sub>", ""]
    L += ["### The 7 AI specialists", "", "| Specialist | Checks | Verdict |", "|---|---|---|"]
    for area in AREAS:
        name, q = AREA_PLAIN[area]
        n = sum(1 for f in findings if area_of(f) == area and f.get("blocking"))
        verdict = (rep.get("area_status") or {}).get(area, "PASS")
        L.append(f"| {name} | {q} | {'🛑 ' + str(n) + ' blocking' if n else ('🛑 rule fails' if verdict == 'FAIL' else '✅ pass')} |")
    L += ["", "### In plain English", "", io_text.strip(), "",
          f"<sub>Written by `{io_src}`" + (", a companion agent built with io (Vectara's AI assistant)" if io_src == IO_EXPLAINER else "")
          + " from the review board's report.</sub>", ""]
    if len(state["rounds"]) > 1:
        L += ["### Review history", "", "| Round | Commit | Verdict | Blocking | At risk | Fixed | New | Quotes |",
              "|---|---|---|---|---|---|---|---|"]
        for r in state["rounds"]:
            L.append(f"| {r['round']} | `{r['sha']}` | {'✅ GO' if r['gate'] == 'GO' else '🛑 STOP'} | {r['blocking']} | "
                     f"{money(r['usd'])} | {r['fixed']} | {r['new']} | {r['quotes']} ✓ |")
        L += [""]
    qs = rep.get("questions_for_engineer") or []
    tech = [f"**Gate summary (engineering):** {rep.get('summary', '')}", ""]
    if qs:
        tech += ["**Questions for the engineers:**", *[f"- {q}" for q in qs], ""]
    acc = rep.get("reviewed_and_accepted") or []
    if acc:
        tech += ["**Looked suspicious but checked out fine:**", *[f"- {x.get('item')}: {x.get('why_acceptable')}" for x in acc[:8]], ""]
    L += ["<details><summary>Engineering details</summary>", "", *tech, "</details>", "",
          "---",
          f"<sub>🤖 Tape-out gate = Vectara agent `rsp_kst_gate` (7 specialist sub-agents in parallel, 13 calculator tools, "
          f"rulebook ALD-QA-CHK-007, 38 rules) · this PR's review session remembers earlier rounds · "
          f"[run log]({run_url}) · Ask: comment `/tapeout explain <problem>` · The AI flags and recommends; people decide. "
          f"All chip data is fictional.</sub>",
          f"<!-- tapeout-state:{base64.b64encode(json.dumps(state).encode()).decode()} -->"]
    return "\n".join(L)


# --------------------------------------------------------------------------------------------------
# explain (ChatOps)
# --------------------------------------------------------------------------------------------------
def cmd_explain(a, gh: GH) -> int:
    pr = gh.r("GET", f"/pulls/{a.pr}")
    if (pr.get("head") or {}).get("repo", {}).get("full_name") != gh.repo:
        return 0
    if a.kind == "review":
        cm = gh.r("GET", f"/pulls/comments/{a.comment_id}")
    else:
        cm = gh.r("GET", f"/issues/comments/{a.comment_id}")
    if cm.get("author_association") not in ("OWNER", "MEMBER", "COLLABORATOR"):
        log("ignoring /tapeout from a non-member")
        return 0
    text = (cm.get("body") or "").strip()
    m = re.match(r"/tapeout\s+explain\s*(.*)", text, re.S | re.I)
    if not m:
        return 0
    q = m.group(1).strip()
    react = "/pulls/comments" if a.kind == "review" else "/issues/comments"
    try:
        gh.r("POST", f"{react}/{a.comment_id}/reactions", {"content": "eyes"})
    except Exception:  # noqa: BLE001
        pass
    state = load_state(find_summary(gh, a.pr))
    target = None
    if a.kind == "review":  # asked inside a finding's thread: that finding
        top = cm.get("in_reply_to_id") or cm["id"]
        try:
            tb = gh.r("GET", f"/pulls/comments/{top}").get("body") or ""
            mm = FIND_RE.search(tb)
            target = mm.group(1) if mm else None
        except Exception:  # noqa: BLE001
            pass
    if not target and q:
        best, score = None, 0.0
        for fid, f in state["findings"].items():
            hay = " ".join(str(x or "") for x in (fid, f.get("title"), f.get("plain_title"))).lower()
            s = difflib.SequenceMatcher(None, q.lower(), hay).ratio() + (1.0 if q.lower() in hay else 0)
            if s > score:
                best, score = fid, s
        target = best if score >= 0.3 else None
    f = state["findings"].get(target) if target else None
    subject = (f"finding {target} ({f.get('title')})" if f else f"this: {q or 'the latest gate report'}")
    msg = (f"A team member asks on pull request #{a.pr}: \"{q or 'explain'}\". Please explain {subject} in plain "
           "English for a software developer who knows nothing about chips: what is wrong, why it blocks tape-out, "
           "and what fixing it involves. At most 150 words; include one short exact quote from the package.")
    c = v.Client(turn_timeout=900)
    skey = session_key(gh.repo, a.pr)
    if not c.get_session(GATE_KEY, skey):
        answer = "No review has run on this pull request yet, so there is nothing to explain."
    else:
        if (c.get_session(GATE_KEY, skey) or {}).get("status") == "running":
            c.wait_for_turn(GATE_KEY, skey, None, poll=10, max_wait=1800, raise_on_error=False)
        ev = run_turn(c, GATE_KEY, skey, msg, max_wait=600)
        answer = (v.final_text(ev) or "").strip() or "The reviewer did not answer; please try again."
    who = (cm.get("user") or {}).get("login", "")
    reply = (f"🤖 **Tape-out reviewer** (same review session as this PR's gate, so it remembers every round)\n\n{answer}"
             f"\n\n<sub>Asked by @{who}" + (f" about `{target}`" if target else "") + " · the AI explains and recommends; people decide.</sub>")
    if a.kind == "review":
        top = cm.get("in_reply_to_id") or cm["id"]
        gh.r("POST", f"/pulls/{a.pr}/comments/{top}/replies", {"body": reply})
    else:
        quoted = "\n".join("> " + l for l in text.splitlines())
        gh.r("POST", f"/issues/{a.pr}/comments", {"body": quoted + "\n\n" + reply})
    log(f"answered /tapeout explain on PR #{a.pr} ({target})")
    return 0


# --------------------------------------------------------------------------------------------------
# release (after merge): deployment to the "fab" environment + retro agent -> rulebook PR
# --------------------------------------------------------------------------------------------------
def one_line(x, n: int = 220) -> str:
    t = re.sub(r"\s+", " ", str(x or "")).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def gate_reports_by_round(c: v.Client, skey: str) -> list[dict]:
    ev = list(reversed(c.list_events(GATE_KEY, skey)))
    rounds, cur = [], None
    for e in ev:
        if e.get("type") == "input_message":
            txt = " ".join(str(m.get("content", "")) for m in e.get("messages") or [] if isinstance(m, dict)) \
                or str(e.get("content") or "")
            if re.match(r"\s*TRR-\d+:", txt):
                cur = {"input": txt, "report": None}
                rounds.append(cur)
        elif e.get("type") == "structured_output" and e.get("schema_name") == GATE_SCHEMA and cur is not None:
            cur["report"] = e.get("content")
    return [r["report"] for r in rounds if r["report"]]


def compact_report(rep: dict) -> dict:
    keys = ["id", "title", "category", "severity", "blocking", "status", "block", "rule_ids", "evidence", "reasoning",
            "respin_type", "cost_exposure_usd", "schedule_impact_weeks", "recommended_fix", "owner"]
    rules = rep.get("rule_results") or {}
    return {"project": rep.get("project"), "revision": rep.get("revision"), "gate": rep.get("gate"),
            "summary": rep.get("summary"), "blocking_open_count": rep.get("blocking_open_count"),
            "total_cost_exposure_usd": rep.get("total_cost_exposure_usd"), "area_status": rep.get("area_status"),
            "findings": [{k: f.get(k) for k in keys} for f in rep.get("findings") or []],
            "closed_since_previous": rep.get("closed_since_previous") or [],
            "reviewed_and_accepted": rep.get("reviewed_and_accepted") or [],
            "questions_for_engineer": rep.get("questions_for_engineer") or [],
            "rule_results_not_pass": {k: r for k, r in rules.items() if (r or {}).get("verdict") != "PASS"},
            "rule_results_pass_count": sum(1 for r in rules.values() if (r or {}).get("verdict") == "PASS")}


def retro_message(reports: list[dict]) -> str:
    revs = [str(r.get("revision") or f"round {i + 1}") for i, r in enumerate(reports)]
    parts = [
        "Retrospective request. The Tape-out Gate reviewed the tape-out package of ALX-5100 KESTREL (project code "
        "KST) revision by revision in one review session: "
        + ", ".join(f"revision {r} at TRR-{i + 1}" for i, r in enumerate(revs))
        + ". Below is each revision's gate report as JSON, in review order. rule_results_not_pass lists every "
        "checklist rule whose verdict was not PASS in that revision.",
        "Produce the retrospective: finding lineage, the rules that caught each finding and their origin, where "
        "the package's own summaries disagreed with its evidence, lessons, proposed checklist amendments written "
        "in the checklist's own style, and proposed evaluation scenarios."]
    for i, (r, rep) in enumerate(zip(revs, reports)):
        parts.append(f"Gate report, revision {r} (TRR-{i + 1}):\n```json\n" + json.dumps(compact_report(rep), indent=1) + "\n```")
    return "\n\n".join(parts)


def amendment_markdown(retro: dict, pr_no: int, merge_sha: str) -> str:
    L = [f"# Proposed rulebook amendments after tape-out PR #{pr_no}", "",
         f"Proposed by the retrospective agent `{RETRO_KEY}` after the KESTREL package was released to the factory "
         f"(merge `{merge_sha[:7]}`). It read every gate report of the PR's review rounds plus the rulebook, the "
         "respin post-mortems and the errata. **Nothing here is in force until a person approves this PR.**", ""]
    if retro.get("loop_summary"):
        L += ["## What happened in the review loop", "", str(retro["loop_summary"]), ""]
    if retro.get("lessons"):
        L += ["## Lessons", ""]
        for x in retro["lessons"]:
            L.append(f"- {x.get('lesson') if isinstance(x, dict) else x}")
        L += [""]
    L += ["## Proposed amendments to ALD-QA-CHK-007", ""]
    for am in retro.get("proposed_amendments") or []:
        rid = am.get("proposed_rule_id") or am.get("target_rule_id") or ""
        L += [f"### {am.get('id')}: {str(am.get('kind', '')).replace('_', ' ')} `{rid}` ({am.get('area', '')})", "",
              "| Rule ID | Area | Requirement | Threshold | Blocking | Origin |", "|---|---|---|---|---|---|",
              f"| {rid} | {am.get('area', '')} | {str(am.get('rule_text', '')).replace('|', '/')} | "
              f"{str(am.get('threshold', '')).replace('|', '/')} | {'Yes' if am.get('blocking') else 'No'} | "
              f"{str(am.get('origin', '')).replace('|', '/')} |", "",
              f"**Why:** {am.get('rationale', '')}", ""]
        if am.get("false_alarm_guard"):
            L += [f"**Guard against false alarms:** {am['false_alarm_guard']}", ""]
        if am.get("change_history_entry"):
            L += [f"**Change-history row:** `{am['change_history_entry']}`", ""]
    L += ["---", "<sub>🤖 Opened by the tape-out CI bot. The AI proposes; the checklist owner decides.</sub>"]
    return "\n".join(L)


def cmd_release(a, gh: GH) -> int:
    pr = gh.r("GET", f"/pulls/{a.pr}")
    if not pr.get("merged"):
        log("PR not merged; nothing to release")
        return 0
    if (pr.get("head") or {}).get("repo", {}).get("full_name") != gh.repo:
        return 0
    merge_sha = pr["merge_commit_sha"]
    if not a.skip_deployment:
        dep = gh.r("POST", "/deployments", {"ref": merge_sha, "environment": "fab", "auto_merge": False,
                                            "required_contexts": [], "description": f"Tape-out of PR #{a.pr}"})
        gh.r("POST", f"/deployments/{dep['id']}/statuses",
             {"state": "success", "environment": "fab", "description": "Released to the factory (fictional)",
              "log_url": pr["html_url"]})
        log(f"deployment {dep['id']} to environment fab: success")
    c = v.Client(turn_timeout=900)
    skey = session_key(gh.repo, a.pr)
    reports = gate_reports_by_round(c, skey)
    log(f"retro over {len(reports)} gate report(s) from session {skey}")
    if not reports:
        return 0
    t0 = time.time()
    retro, rk = one_shot(c, RETRO_KEY, retro_message(reports), RETRO_SCHEMA, max_wait=900)
    log(f"retro agent: {time.time() - t0:.0f}s, {len((retro or {}).get('proposed_amendments') or [])} amendments")
    if not retro:
        return 1
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / "retro.json").write_text(json.dumps(retro, indent=1))
    branch = f"tapeout-bot/rulebook-after-pr{a.pr}"
    base = gh.r("GET", "/git/ref/heads/main")["object"]["sha"]
    if gh.r("GET", f"/git/ref/heads/{branch}", ok404=True) is None:
        gh.r("POST", "/git/refs", {"ref": f"refs/heads/{branch}", "sha": base})
    path = f"rulebook/amendments/after-pr{a.pr}.md"
    existing = gh.r("GET", f"/contents/{path}?ref={branch}", ok404=True)
    gh.r("PUT", f"/contents/{path}", {"message": f"Rulebook: amendments proposed by the retro agent after #{a.pr}",
                                      "content": base64.b64encode(amendment_markdown(retro, a.pr, merge_sha).encode()).decode(),
                                      "branch": branch, **({"sha": existing["sha"]} if existing else {})})
    ams = retro.get("proposed_amendments") or []
    body = ("## 📘 The tape-out gate learned something\n\n"
            f"After #{a.pr} was released to the factory, the retrospective agent (`{RETRO_KEY}`) re-read every review "
            f"round and the company's past failures, and proposes **{len(ams)} rulebook change{'s' if len(ams) != 1 else ''}** "
            "so the next chip gets caught earlier:\n\n"
            + "\n".join(f"- **{am.get('id')}** {str(am.get('kind', '')).replace('_', ' ')} "
                        f"`{am.get('proposed_rule_id') or am.get('target_rule_id')}`: {one_line(am.get('rationale'))}"
                        for am in ams)
            + "\n\n**A person must approve this.** The AI proposes; the checklist owner decides.\n\n"
            f"<sub>Retro session `{rk}` · {time.time() - t0:.0f}s</sub>")
    prs = gh.r("GET", f"/pulls?head={gh.repo.split('/')[0]}:{branch}&state=open") or []
    if prs:
        gh.r("PATCH", f"/pulls/{prs[0]['number']}", {"body": body})
        url = prs[0]["html_url"]
    else:
        url = gh.r("POST", "/pulls", {"title": f"📘 Rulebook: {len(ams)} amendments proposed after tape-out #{a.pr}",
                                      "head": branch, "base": "main", "body": body})["html_url"]
    gh.r("POST", f"/issues/{a.pr}/comments",
         {"body": f"🏭 **Released to the factory.** Tape-out of `{merge_sha[:7]}` is recorded as a deployment to "
                  f"the `fab` environment.\n\n📘 The retro agent proposed {len(ams)} rulebook amendment(s) from this "
                  f"PR's review rounds: {url} (needs a human approval)."})
    log(f"rulebook PR: {url}")
    return 0


def cmd_republish(a, gh: GH) -> int:
    """Debug: re-render a saved round without calling the gate (state from the sticky comment is NOT advanced
    past the saved round: pass --state-from-scratch to start clean)."""
    res = json.loads(Path(a.report).read_text())
    pr = gh.r("GET", f"/pulls/{a.pr}")
    sha = a.sha or res["sha"]
    files = fetch_files(gh, sha)
    docs = build_docs(files, res["rev_label"])
    rep = res["report"]
    g = Grounder(docs).annotate(rep)
    summary_cm = find_summary(gh, a.pr)
    state = load_state(summary_cm)
    if a.pop_round and state["rounds"]:
        state["rounds"].pop()
    publish(gh, a.pr, sha, len(state["rounds"]) + 1, res["letter"], rep, res["plain"], g,
            (res.get("correction") or {}).get("corrected", 0), res["stats"], res["schedule"], res["io_summary"],
            res["io_source"], state, summary_cm, os.environ.get("RUN_URL") or pr["html_url"], res["gate_wall_s"], 0)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["review", "explain", "release", "republish"])
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--sha")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--out", default="tapeout-out")
    ap.add_argument("--comment-id", type=int)
    ap.add_argument("--kind", choices=["issue", "review"], default="issue")
    ap.add_argument("--skip-deployment", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--pop-round", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not (a.repo and token):
        raise SystemExit("GITHUB_REPOSITORY/--repo and GITHUB_TOKEN are required")
    gh = GH(a.repo, token)
    try:
        return {"review": cmd_review, "explain": cmd_explain, "release": cmd_release,
                "republish": cmd_republish}[a.command](a, gh)
    finally:
        Path(a.out).mkdir(parents=True, exist_ok=True)
        with open(Path(a.out) / "run.log", "a", encoding="utf-8") as fh:
            fh.write("\n".join(LOG_LINES) + "\n")


if __name__ == "__main__":
    sys.exit(main())
