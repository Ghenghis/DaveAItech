"""brain_llm.py — LLM abstraction: 4-stage fallback, streaming, JSON mode, caching.

Stage chain (no cloud-provider dependency — local-first):
  1. LiteLLM streaming  (model → heavy-coder / fast-agent / vision via /opt/litellm/config.yaml)
  2. LiteLLM non-stream (same model, no stream)
  3. LiteLLM fast-agent (if HEAVY failed, retry with FAST)
  4. Direct LM Studio   (bypass LiteLLM proxy entirely — final safety net)

No Anthropic SDK dependency. Removed 2026-05-25 per Dave's directive: "anthropic isn't
one of the api keys in the list to be usable". If a cloud provider key (Anthropic/MiniMax/
SiliconFlow/OpenRouter) is rotated and re-enabled later, the LiteLLM config can route
brain aliases through it transparently — no code change required here.
"""
import os, json, re, time, hashlib, threading, urllib.request, urllib.error, sys
from brain_core import LLM_BASE, HEAVY, FAST, VISION
from brain_events import agent_set, emit

# TODO(vision-stage): VISION (imported above) is not wired into any function
# in this module yet. None of the public entry points here (llm/llm_json/
# llm_fast/llm_heavy/llm_chat_direct) accept image/attachment content at all
# today, so there is no request shape yet to route toward VISION. Wiring it
# in for real needs (1) a way for a caller to pass image data into these
# functions (e.g. an `images`/`image_data` kwarg threaded through `llm()`),
# and (2) a stage that, when that argument is present, swaps the model to
# VISION and builds an OpenAI-style multimodal `messages` payload (content
# parts: {"type": "text", ...} + {"type": "image_url", ...}) instead of the
# plain-string `content` built below. That is a real feature addition, not
# a same-shape bugfix, so it is left undone here rather than guessed at —
# brain_graph.py (not in this file) is the natural caller to add the param,
# since it is whatever currently decides a request is image-bearing.


# ── ReAct control-token stream filter ─────────────────────────────────────────
# Defense-in-depth (Wave 2 ReAct leak fix, 2026-05-25):
# Even if a build-keyword prompt slips past is_website_change() narrowing,
# the agent's ReAct scaffolding (THOUGHT: / ACTION: / OBSERVATION: / FINAL:)
# MUST NOT reach the user-visible chat bubble. This filter buffers stream
# tokens line-by-line and:
#   - drops THOUGHT: lines unconditionally (the only valid block opener)
#   - drops ACTION:/OBSERVATION: lines only when they follow a THOUGHT: in
#     the same stream (2026-09-15: narrowed from an unconditional prefix
#     match, which permanently deleted ordinary text that merely happened to
#     start a line with one of those words — see class docstring below)
#   - for FINAL: lines, emits only the body after the marker
#   - passes through everything else unchanged
#
# Used by chat / reply / narrator labels where the assistant text is shown to
# the user. ReAct internal labels ("coder", "asset") should not stream at all
# (brain_graph.py _react now passes stream_label="" for the LLM call), but this
# filter is a belt-and-braces guarantee.

_REACT_DROP_PREFIXES = ("THOUGHT:", "ACTION:", "OBSERVATION:")
_REACT_FINAL_RE      = re.compile(r"\bFINAL\s*:\s*", re.IGNORECASE)


class _ReActStreamFilter:
    """Strip ReAct control tokens from streaming text, line by line.

    Tokens arrive in arbitrary chunks, so we buffer until a newline and then
    classify the line. Partial trailing text (no newline yet) is held until
    either we see more tokens or `flush()` is called. The filter is permissive
    on the wire: only well-formed control-token lines are dropped — normal
    chat text passes through with no change.

    Precision note (2026-09-15 fix): a bare "ACTION:"/"OBSERVATION:" line is
    only ever scaffolding if it appears *inside* a block that this stream
    actually opened with a THOUGHT: line — matching the real ReAct loop order
    documented at the top of this file (THOUGHT -> ACTION -> OBSERVATION ->
    ... -> FINAL). Ordinary assistant text that merely starts a line with one
    of those words (a recipe step, a lab note, a screenplay direction) has no
    preceding THOUGHT: in the same stream, so it is no longer misclassified
    and permanently deleted. THOUGHT: itself is still dropped unconditionally
    as the only valid block opener — a bare "THOUGHT:" line-start is far less
    common in ordinary prose, and this filter is documented as a
    belt-and-braces guarantee against leaked scaffolding, not a guarantee of
    zero false positives.
    """

    __slots__ = ("_buf", "_after_final", "_in_react_block")

    def __init__(self):
        self._buf: str = ""
        self._after_final: bool = False
        self._in_react_block: bool = False

    def feed(self, token: str) -> str:
        """Return the portion of `token` that should be emitted downstream."""
        if not token:
            return ""
        self._buf += token
        out_parts: list[str] = []
        # Emit any complete lines, leave a tail in the buffer for next chunk.
        while True:
            nl = self._buf.find("\n")
            if nl < 0:
                # No complete line yet. If we are past a FINAL: marker and
                # the partial buffer doesn't look like a fresh directive, we
                # can still emit it incrementally so the UI streams cleanly.
                if self._after_final and self._buf and not self._buf.lstrip().startswith(
                        _REACT_DROP_PREFIXES + ("FINAL:",)):
                    out_parts.append(self._buf)
                    self._buf = ""
                break
            line = self._buf[: nl + 1]            # include trailing \n
            self._buf = self._buf[nl + 1:]
            stripped = line.lstrip()
            if stripped.startswith("THOUGHT:"):
                # THOUGHT: is the only valid ReAct block opener — drop it and
                # arm the filter so the ACTION:/OBSERVATION: lines that
                # follow it in a genuine trace are recognized as scaffolding.
                self._in_react_block = True
                self._after_final = False
                continue
            if self._in_react_block and stripped.startswith(("ACTION:", "OBSERVATION:")):
                # Only scaffolding mid-block. A standalone line that merely
                # starts with one of these words, with no THOUGHT: opener
                # earlier in this same stream, falls through to the "normal
                # line" case below instead of being dropped.
                continue
            m = _REACT_FINAL_RE.match(stripped) if stripped else None
            if m:
                body = stripped[m.end():]         # text after "FINAL:"
                out_parts.append(body)
                self._after_final = True
                self._in_react_block = False
                continue
            # Normal line — emit as-is.
            out_parts.append(line)
        return "".join(out_parts)

    def flush(self) -> str:
        """Return any remaining buffered text (called at stream end)."""
        if not self._buf:
            return ""
        stripped = self._buf.lstrip()
        if stripped.startswith("THOUGHT:"):
            self._buf = ""
            return ""
        if self._in_react_block and stripped.startswith(("ACTION:", "OBSERVATION:")):
            self._buf = ""
            return ""
        m = _REACT_FINAL_RE.match(stripped) if stripped else None
        if m:
            body = stripped[m.end():]
            self._buf = ""
            return body
        out = self._buf
        self._buf = ""
        return out

try:
    from litellm import completion as _litellm_completion
    _LITELLM_OK = True
except ImportError:
    _LITELLM_OK = False

# ── Local-direct fallback config (overridable via /opt/agent-brain/.env) ──────
# Used as Stage 4: bypasses LiteLLM proxy and calls LM Studio directly via HTTP.
# Default points at the Tailnet LM Studio endpoint that the brain aliases already use.
LOCAL_DIRECT_URL = os.getenv(
    "LOCAL_LLM_DIRECT_URL",
    "http://127.0.0.1:11434/v1/chat/completions",
)
LOCAL_DIRECT_MODEL = os.getenv(
    "LOCAL_LLM_DIRECT_MODEL",
    "qwen2.5-coder:3b",
)
LOCAL_OLLAMA_CHAT_URL = os.getenv(
    "LOCAL_OLLAMA_CHAT_URL",
    "http://127.0.0.1:11434/api/chat",
)
LOCAL_CHAT_MAX_TOKENS = int(os.getenv("LOCAL_CHAT_MAX_TOKENS", "512"))

# User-facing message shown when EVERY LLM path failed. Friendly, voice-safe (no
# stack traces, no tokens, no URLs).
_NO_LLM_USER_MSG = (
    "I'm having trouble reaching my language model right now. "
    "Please try again in a moment."
)

# ── Simple response cache (LRU-ish, 128 slots) ─────────────────────────────────
_cache: dict = {}
_cache_lock = threading.Lock()
_CACHE_MAX = 128
_CACHE_TTL = 300  # seconds


def _cache_key(model: str, prompt: str, system: str) -> str:
    # NOTE: hash FULL system prompt — quick_reply/invoke splice session
    # history into system prompt after byte 80; truncating caused cross-session
    # cache collisions (Wave 1g finding 2026-05-25). Prompt truncation kept
    # since user msgs are bounded by chat UI.
    sys_hash = hashlib.md5(system.encode(errors='replace')).hexdigest()[:16]
    raw = f"{model}|{sys_hash}|{prompt[:200]}"
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_get(key: str) -> str | None:
    with _cache_lock:
        entry = _cache.get(key)
        if entry and (time.monotonic() - entry["ts"]) < _CACHE_TTL:
            return entry["value"]
    return None


def _cache_put(key: str, value: str):
    with _cache_lock:
        if len(_cache) >= _CACHE_MAX:
            oldest = min(_cache, key=lambda k: _cache[k]["ts"])
            del _cache[oldest]
        _cache[key] = {"value": value, "ts": time.monotonic()}


# ── Core litellm call (single attempt) ────────────────────────────────────────
def _litellm_call(model: str, msgs: list, stream: bool = False,
                  timeout: int = 300, q=None, stream_label: str = "") -> str:
    if not _LITELLM_OK:
        return ""
    if stream:
        collected = []
        reasoning_collected = []
        clean_collected: list[str] = []
        # ReAct sanitizer — strips THOUGHT:/ACTION:/OBSERVATION:/FINAL: prefixes
        # from user-visible token stream. The `collected` buffer still gets the
        # RAW tokens so callers that never activate the filter (q/stream_label
        # empty — e.g. _react's own internal calls, which pass stream_label="")
        # are unaffected. When the filter IS active (chat/reply/narrator
        # labels), `clean_collected` mirrors exactly what was emitted to the
        # client, and the return value below uses that instead of the raw
        # text — so persisting/redisplaying this value can't reintroduce the
        # scaffolding the filter exists to hide.
        react_filter = _ReActStreamFilter() if (q and stream_label) else None
        try:
            r = _litellm_completion(
                model=f"openai/{model}", messages=msgs,
                api_base=LLM_BASE, api_key="local", timeout=timeout,
                stream=True, max_tokens=4096)
            for chunk in r:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta:
                    token = getattr(delta, "content", "") or ""
                    reasoning = getattr(delta, "reasoning_content", "") or ""
                    if token:
                        collected.append(token)
                        if react_filter is not None:
                            clean = react_filter.feed(token)
                            if clean:
                                clean_collected.append(clean)
                                emit(q, "token", token=clean, msg=clean, label=stream_label)
                    elif reasoning:
                        reasoning_collected.append(reasoning)
        except Exception as e:
            # Mid-stream failure: preserve whatever was already streamed to
            # the client instead of discarding it. If any text made it out,
            # the caller (llm()) treats this non-empty return as final and
            # skips regenerating an independent answer via Stage 2.
            sys.stderr.write(
                f"[brain_llm stage1 stream interrupted model={model}: {type(e).__name__}: {e}]\n")
        # Flush any trailing buffered text (last partial line w/o newline).
        if react_filter is not None:
            tail = react_filter.flush()
            if tail:
                clean_collected.append(tail)
                emit(q, "token", token=tail, msg=tail, label=stream_label)
        if react_filter is not None:
            result = "".join(clean_collected).strip()
        else:
            result = "".join(collected).strip()
        if not result:
            result = "".join(reasoning_collected).strip()
        return result
    else:
        r = _litellm_completion(
            model=f"openai/{model}", messages=msgs,
            api_base=LLM_BASE, api_key="local", timeout=timeout,
            max_tokens=4096)
        msg_obj = r.choices[0].message
        text = (msg_obj.content or "").strip()
        if not text:
            text = (getattr(msg_obj, "reasoning_content", "") or "").strip()
        return text


# ── Stage 4: direct local model call (no LiteLLM) ─────────────────────────────
def _local_direct_call(prompt: str, system: str = "", timeout: int = 60,
                       max_tokens: int | None = None, *, q=None,
                       stream_label: str = "") -> str:
    """Final safety net: bypass LiteLLM proxy and call the local model directly.

    Production note (2026-07-31): normal chat must stream visible tokens from
    Ollama's native /api/chat. The VPS model is slow per token; waiting for the
    full response makes the UI look frozen and lets upstream clients time out.
    """
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    token_budget = int(max_tokens or LOCAL_CHAT_MAX_TOKENS)
    should_stream = bool(q is not None and stream_label)

    native_payload = json.dumps({
        "model": LOCAL_DIRECT_MODEL,
        "messages": msgs,
        "stream": should_stream,
        "keep_alive": os.getenv("LOCAL_OLLAMA_KEEP_ALIVE", "10m"),
        "options": {"num_predict": token_budget, "temperature": 0.5},
    }).encode("utf-8")
    collected: list[str] = []
    try:
        req = urllib.request.Request(
            LOCAL_OLLAMA_CHAT_URL,
            data=native_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if should_stream:
                for raw in r:
                    if not raw or not raw.strip():
                        continue
                    try:
                        data = json.loads(raw.decode("utf-8", errors="replace"))
                    except Exception:
                        continue
                    token = ((data.get("message") or {}).get("content")
                             or data.get("response") or "")
                    if token:
                        collected.append(token)
                        emit(q, "token", token=token, msg=token,
                             label=stream_label)
                    if data.get("done"):
                        break
                text = "".join(collected).strip()
            else:
                data = json.loads(r.read().decode("utf-8", errors="replace"))
                text = ((data.get("message") or {}).get("content")
                        or data.get("response") or "").strip()
        if text:
            return text
    except Exception as e:
        partial = "".join(collected).strip()
        if partial:
            sys.stderr.write(
                f"[brain_llm ollama-native stream partial after {type(e).__name__}: {e}]\n")
            return partial
        sys.stderr.write(
            f"[brain_llm ollama-native direct failed: {type(e).__name__}: {e}]\n")

    payload = json.dumps({
        "model": LOCAL_DIRECT_MODEL,
        "messages": msgs,
        "max_tokens": token_budget,
        "temperature": 0.5,
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            LOCAL_DIRECT_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        text = ((data.get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()
        text = text or _NO_LLM_USER_MSG
        if q is not None and stream_label and text:
            emit(q, "token", token=text, msg=text, label=stream_label)
        return text
    except Exception as e:
        sys.stderr.write(f"[brain_llm local-direct fallback failed: {type(e).__name__}: {e}]\n")
        if q is not None and stream_label:
            emit(q, "token", token=_NO_LLM_USER_MSG, msg=_NO_LLM_USER_MSG,
                 label=stream_label)
        return _NO_LLM_USER_MSG


def llm_chat_direct(prompt: str, system: str = "", *, q=None,
                    stream_label: str = "", agent_name: str = "",
                    timeout: int = 75, max_tokens: int = 96) -> str:
    """Fast path for user-facing conversational chat.

    Streams native Ollama tokens into the SSE queue when one is provided. This
    keeps the UI visibly alive even on the current slower VPS model.
    """
    if agent_name:
        agent_set(agent_name, "working", prompt[:60], 50, FAST)
    result = _local_direct_call(prompt, system, timeout=timeout,
                                max_tokens=max_tokens, q=q,
                                stream_label=stream_label)
    result = result or _NO_LLM_USER_MSG
    if agent_name:
        status = "done" if result and result != _NO_LLM_USER_MSG else "error"
        agent_set(agent_name, status, result[:60], 100, FAST)
    return result


# ── Public LLM interface ───────────────────────────────────────────────────────
def llm(model: str, prompt: str, system: str = "", *,
        q=None, stream_label: str = "", agent_name: str = "",
        use_cache: bool = False, timeout: int = 300) -> str:
    """
    4-stage fallback (no Anthropic dependency):
      1. LiteLLM streaming   (model → heavy-coder / fast-agent / vision)
      2. LiteLLM non-stream  (same model, no stream)
      3. LiteLLM fast-agent  (if HEAVY failed, retry with FAST)
      4. Direct LM Studio    (bypass LiteLLM proxy entirely)
    """
    if agent_name:
        agent_set(agent_name, "working", prompt[:60], 50, model)

    if use_cache:
        ck = _cache_key(model, prompt, system)
        cached = _cache_get(ck)
        if cached:
            # Cache hits skip generation entirely, but the client is still
            # waiting on the SSE stream for this turn — emit the cached text
            # through the same queue path a normal response would use so a
            # repeated prompt (llm_fast() enables caching by default) still
            # produces visible output instead of a silent no-op.
            if q is not None and stream_label:
                emit(q, "token", token=cached, msg=cached, label=stream_label)
            if agent_name:
                agent_set(agent_name, "done", cached[:60], 100, model)
            return cached

    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})

    text = ""

    # Stage 1 — litellm streaming
    try:
        text = _litellm_call(model, msgs, stream=True, timeout=timeout,
                             q=q, stream_label=stream_label)
    except Exception as e:
        sys.stderr.write(f"[brain_llm stage1 stream failed model={model}: {type(e).__name__}: {e}]\n")

    # Stage 2 — litellm non-streaming. Use half of Stage 1's timeout (not the
    # full caller-supplied value again) so a stalled-but-connected upstream
    # fails over to the more resilient Stage 3/4 sooner, instead of being able
    # to keep one chat turn in flight for up to 2x the configured timeout.
    if not text:
        try:
            text = _litellm_call(model, msgs, stream=False, timeout=max(1, timeout // 2))
        except Exception as e:
            sys.stderr.write(f"[brain_llm stage2 nonstream failed model={model}: {type(e).__name__}: {e}]\n")

    # Stage 3 — try fast-agent if heavy-coder failed
    if not text and model == HEAVY:
        try:
            text = _litellm_call(FAST, msgs, stream=False, timeout=60)
        except Exception as e:
            sys.stderr.write(f"[brain_llm stage3 fast-retry failed: {type(e).__name__}: {e}]\n")

    # Stage 4 — direct LM Studio fallback (bypasses LiteLLM proxy). Pass
    # q/stream_label through like every earlier stage so this runs as the
    # token-by-token streaming call _local_direct_call was written to provide
    # instead of silently degrading to a fully blocking request, and wrap it
    # in the same try/except pattern as Stages 1-3 so an exception that
    # escapes _local_direct_call's own internal handling degrades to the
    # friendly _NO_LLM_USER_MSG fallback below instead of crashing llm().
    if not text:
        try:
            text = _local_direct_call(prompt, system, timeout=60,
                                      q=q, stream_label=stream_label)
        except Exception as e:
            sys.stderr.write(f"[brain_llm stage4 direct failed: {type(e).__name__}: {e}]\n")

    result = text or _NO_LLM_USER_MSG

    if use_cache and result and result != _NO_LLM_USER_MSG:
        _cache_put(ck, result)

    if agent_name:
        status = "done" if result and result != _NO_LLM_USER_MSG else "error"
        agent_set(agent_name, status, result[:60], 100, model)

    return result


def _extract_json_span(text: str, start: int) -> str | None:
    """Return the substring of `text` beginning at `start` that forms one
    balanced top-level JSON object/array literal (brackets inside quoted
    strings are ignored), or None if the brackets never balance (e.g. a
    truncated response). Used to isolate a JSON value from any trailing
    prose the model tacks on after it.
    """
    opening = text[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def llm_json(model: str, prompt: str, system: str = "", **kwargs) -> dict:
    """LLM call that forces JSON output and parses it."""
    json_sys = (system + "\n\nRespond ONLY with valid JSON. No prose, no markdown."
                if system else "Respond ONLY with valid JSON. No prose, no markdown.")
    raw = llm(model, prompt, json_sys, **kwargs)
    # Extract JSON even when the model appends trailing prose after an
    # otherwise well-formed value (a common LLM habit): a balanced-bracket
    # scan finds exactly where the top-level object/array ends, so trailing
    # content after that point no longer makes json.loads raise on an
    # otherwise-valid blob. Falls back to the old exact-suffix slice (and
    # then to the raw-wrapped dict) if the brackets never balance.
    for start in (raw.find("{"), raw.find("[")):
        if start < 0:
            continue
        for candidate in (_extract_json_span(raw, start), raw[start:]):
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except Exception as e:
                sys.stderr.write(f"[brain_llm llm_json parse failed: {type(e).__name__}]\n")
    # fallback: wrap raw in a dict
    return {"raw": raw}


def llm_fast(prompt: str, system: str = "", **kwargs) -> str:
    # W2: pin English + brevity by default for chat-fast path. Caller-supplied system overrides.
    if not system:
        system = "Respond in English. Be concise and friendly."
    # W3: enable response cache by default for fast path (cache infra already exists, was disabled).
    kwargs.setdefault("use_cache", True)
    return llm(FAST, prompt, system, **kwargs)


def llm_heavy(prompt: str, system: str = "", **kwargs) -> str:
    if not system:
        system = "Respond in English."
    return llm(HEAVY, prompt, system, **kwargs)
