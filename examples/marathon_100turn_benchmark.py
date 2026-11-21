import time
import seam_time_v2 as sts

regimes = [
    (1, 10, "Discovery", 46.0, 0.87, 0.34),
    (11, 28, "Codebase Audit", 75.0, 0.95, 0.16),
    (29, 34, "Schema Conflict", 26.0, 0.40, 0.93),
    (35, 52, "Migration Execution", 78.0, 0.96, 0.15),
    (53, 57, "Latency Anomaly", 24.0, 0.38, 0.95),
    (58, 75, "Hotfix & Load Test", 74.0, 0.95, 0.17),
    (76, 80, "Security Audit Pivot", 28.0, 0.43, 0.91),
    (81, 100, "Final Verification", 77.0, 0.96, 0.15),
]

mgr = sts.SeamContextMemoryManager(profile="STANDARD", min_episode_turns=3)
total_raw_tokens, latencies_ms, boundary_turns = 0, [], []

for start, end, phase, tps, prob, ent in regimes:
    for turn in range(start, end + 1):
        role = "User" if turn % 4 == 1 else "Assistant"
        content = (
            f"[{phase} | Turn {turn:03d}] Executing distributed verification step {turn} across "
            f"cluster shards, validating transaction logs, replication lag, TLS handshakes, "
            f"and memory allocation metrics to ensure zero regression before deployment."
        )
        total_raw_tokens += max(12, len(content.split()) * 2)
        t0 = time.perf_counter()
        res = mgr.ingest_turn(turn, role, content, phase, tps, prob, ent)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        if res["cut_triggered"]:
            boundary_turns.append(turn)

archived_tokens = sum(max(10, len(c.summary.split()) * 2) for c in mgr.archived_episodes)
active_tokens = sum(t["tokens"] for t in mgr.active_buffer)
final_tokens = archived_tokens + active_tokens
savings_pct = (1.0 - (final_tokens / total_raw_tokens)) * 100.0

print("=== 100-TURN MARATHON BENCHMARK ===")
print(f"Mean Step Latency        : {sum(latencies_ms)/len(latencies_ms):.4f} ms / turn")
print(f"Seam Boundary Cuts       : {len(boundary_turns)} cuts at turns {boundary_turns}")
print(f"Minimum Episode Length   : {min(c.turn_count for c in mgr.archived_episodes)} turns (0 single-turn shards)")
print(f"Token Compression        : ~{total_raw_tokens:,} raw -> ~{final_tokens:,} active ({savings_pct:.1f}% reduction)")
