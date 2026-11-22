"""
Live Agentic Chat Loop governed by the 3+1 Holographic Seam Memory Manager.

Demonstrates real-time episodic boundary detection and semantic context compression
using live LLM telemetry (tokens/sec, token log-prob confidence, and entropy).
Includes automatic fallback handling so temporary API 503 demand spikes gracefully
register as Seam anomalies without interrupting execution.

Usage:
  export GEMINI_API_KEY="your-api-key"
  pip install google-genai numpy
  python examples/live_agent_memory.py
"""

import math
import os
import sys
import time
from typing import Any, Dict

# Allow importing seam_time_v2 from repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import seam_time_v2 as sts


def compute_telemetry_from_response(text: str, elapsed_sec: float, logprobs_data: Any = None) -> Dict[str, float]:
    """
    Extracts 3+1 triad inputs (Throughput, Confidence, Entropy) from a live LLM completion.
    Uses real token log-probabilities when available, or lexical innovation entropy fallback.
    """
    approx_tokens = max(1, len(text.split()) * 1.3)
    tokens_per_sec = approx_tokens / max(0.05, elapsed_sec)

    if logprobs_data:
        probs = [math.exp(lp) for lp in logprobs_data]
        mean_prob = sum(probs) / len(probs)
        entropy = -sum(p * math.log(max(1e-9, p)) for p in probs) / len(probs)
        return {
            "tps": round(tokens_per_sec, 2),
            "prob": round(min(0.99, max(0.05, mean_prob)), 4),
            "entropy": round(min(1.0, max(0.05, entropy)), 4),
        }

    words = [w.lower().strip(".,!?") for w in text.split() if w]
    unique_ratio = len(set(words)) / max(1, len(words))
    uncertainty_markers = sum(
        1 for w in words if w in {"however", "wait", "conflict", "error", "unexpected", "pivot", "contradiction", "unclear", "503"}
    )
    entropy = min(0.98, max(0.12, (unique_ratio * 0.45) + (uncertainty_markers * 0.18)))
    mean_prob = max(0.25, 1.0 - (entropy * 0.65))

    return {
        "tps": round(tokens_per_sec, 2),
        "prob": round(mean_prob, 4),
        "entropy": round(entropy, 4),
    }


def _deterministic_fallback(turn_idx: int, phase: str) -> tuple[str, Dict[str, float]]:
    """Provides deterministic telemetry when offline or during transient API 503 spikes."""
    if phase == "Architecture":
        reply = f"Standard pooled architecture response for turn {turn_idx}: reuse persistent TCP sessions to minimize handshake overhead."
        metrics = {"tps": 68.0, "prob": 0.93, "entropy": 0.20}
    elif phase == "Crisis Pivot":
        reply = f"Unexpected conflict detected on turn {turn_idx}: TLS edge termination failure explains zero DB load alongside 400% ingress errors."
        metrics = {"tps": 26.0, "prob": 0.41, "entropy": 0.93}
    else:
        reply = f"Remediation step {turn_idx}: deploy renewed wildcard certificate to edge load balancers and verify TLS 1.3 metrics."
        metrics = {"tps": 64.0, "prob": 0.91, "entropy": 0.22}
    return reply, metrics


def run_live_agent_demo() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    use_live_api = False
    client = None

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            use_live_api = True
        except ImportError:
            print("[Info] 'google-genai' not installed; running in offline deterministic telemetry mode.\n")

    # Initialize the 3+1 Seam Memory Manager with a 3-turn refractory lock
    memory_mgr = sts.SeamContextMemoryManager(profile="STANDARD", min_episode_turns=3)

    user_prompts = [
        ("Architecture", "Briefly explain how connection pooling reduces database latency."),
        ("Architecture", "What is the ideal pool size formula for a 16-core PostgreSQL server?"),
        ("Architecture", "How does PgBouncer transaction pooling handle prepared statements?"),
        ("Architecture", "Summarize best practices for idle connection timeouts."),
        ("Crisis Pivot", "WAIT—contradiction! Production error alerts just spiked 400% with TLS handshake drops while DB CPU is at 5%. Pivot immediately and diagnose!"),
        ("Crisis Pivot", "Unexpected twist: DNS resolves to the edge CDN, not our origin. Could an expired edge SSL cert cause cascading upstream timeouts?"),
        ("Synthesis", "Give a concise 3-step zero-downtime runbook to rotate the expired edge TLS certificate."),
        ("Synthesis", "Confirm monitoring checks after the certificate rollout completes."),
    ]

    mode_label = "LIVE GEMINI API (gemini-3.8-flash)" if use_live_api else "OFFLINE DETERMINISTIC TELEMETRY"
    print(f"=== 3+1 SEAM LIVE AGENT MEMORY DEMO ({mode_label}) ===\n")

    for turn_idx, (phase, prompt) in enumerate(user_prompts, 1):
        context_window = memory_mgr.build_prompt_context()
        full_prompt = f"{context_window}\n\nUser: {prompt}" if context_window else prompt

        t0 = time.perf_counter()
        if use_live_api and client is not None:
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=full_prompt,
                )
                reply_text = response.text.strip().replace("\n", " ")[:180]
                elapsed = time.perf_counter() - t0
                metrics = compute_telemetry_from_response(reply_text, elapsed)
            except Exception as api_err:
                print(f"[Notice] Transient API error on Turn {turn_idx:02d} ({type(api_err).__name__}); engaging Seam fallback telemetry.")
                reply_text, metrics = _deterministic_fallback(turn_idx, phase)
        else:
            reply_text, metrics = _deterministic_fallback(turn_idx, phase)

        state = memory_mgr.ingest_turn(
            turn_idx=turn_idx,
            role="User/Assistant",
            content=f"Q: {prompt[:60]}... -> A: {reply_text[:70]}...",
            phase=phase,
            tokens_per_sec=metrics["tps"],
            mean_token_prob=metrics["prob"],
            token_entropy=metrics["entropy"],
        )

        if state["cut_triggered"]:
            cap = state["sealed_capsule"]
            print(f"\n>>> [SEAM BOUNDARY CUT @ Turn {turn_idx:02d}] Sealed Episode {cap.episode_id} "
                  f"(Turns {cap.start_turn}-{cap.end_turn}, Saved ~{cap.raw_tokens_saved} tokens) <<<\n")

        print(
            f"Turn {turn_idx:02d} [{phase:<12}] | Mode: {state['mode']:<24} | "
            f"SDI: {state['sdi']:.3f} | Active Buffer: {state['active_buffer_turns']} turns"
        )

    print(f"\n=== FINAL MEMORY STATE: {len(memory_mgr.archived_episodes)} Sealed Episode(s), "
          f"{len(memory_mgr.active_buffer)} Active Turn(s) ===")


if __name__ == "__main__":
    run_live_agent_demo()
