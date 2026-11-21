[![3+1 Seam Verification Suite](https://github.com)](https://github.com)

# 3+1 Holographic Seam Theory & Episodic Context Memory (`v2.0`)

**Zero-tuning, conservation-governed temporal segmentation and episodic memory compression for autonomous AI agents and neural time-series.**

## Overview
Modern AI agents and cognitive telemetry pipelines rely on static token limits or fixed surprise thresholds to chunk memory. Static rules fail in two predictable ways:
1. **Flow False Positives:** Mistaking high-velocity, confident execution for an anomaly and slicing mid-thought.
2. **Crisis Fragmentation:** Shattering an acute surprise or reasoning pivot into disconnected single-turn shards.

This repository resolves both bottlenecks using the **3+1 Holographic Seam Architecture**, enforcing an exact 64-bit conservation law:

$$0.3333\text{ (Efficiency)} + 0.3333\text{ (Balance)} + 0.3333\text{ (Change)} + 0.0001\text{ (The Seam)} = 1.0000$$

By isolating an immutable **`0.0001` Seam** (`O`) as the primary read/write boundary between continuous execution (`0.9999`) and discrete episode slicing, the engine compresses routine flow (`MOMENTUM_GLIDE`), dilates subjective resolution during acute surprises (`MODE_A_HARD_STABILIZE`), and seals high-density episodic memory capsules only at genuine structural regime boundaries.

## Verified Benchmark Results

### 1. Neural / Event-Segmentation Benchmark (16-Step Stream)

| Detector Architecture | Ground Truth Cuts | Detected Cuts | Flow False Alarms | Crisis Shards |
| :--- | :---: | :---: | :---: | :---: |
| **Standard Static Threshold Detector** | 1 | 7 | 4 | 3 |
| **`SeamTemporalAnalyzer` (`3+1 Seam v2.0`)** | **1** | **1** | **0** | **0** |

### 2. Autonomous AI Context Memory (`18-Turn Agent Telemetry`)
* **Turns 01–04 (`Init`):** `STEADY_STATE` (`SDI: 1.000 -> 0.972`) — Establishes rolling EMA baseline.
* **Turns 05–10 (`Tool Flow`):** `MOMENTUM_GLIDE` (`SDI: 0.580 - 0.706`) — Compresses subjective time; keeps all 10 tool turns unbroken.
* **Turn 11 (`Conflict/Pivot`):** **Seam Boundary Cut** seals Turns 1–10 into **Episode 1** (`~96 tokens saved`), shifts into `MODE_A_HARD_STABILIZE` (`SDI: 1.814 -> 1.908`), and enforces a `min_episode_turns=3` refractory lock to prevent crisis fragmentation.
* **Turns 14–18 (`Synthesis -> Output Glide`):** Smooth recovery to `STEADY_STATE` (`SDI: 1.070`) and final `MOMENTUM_GLIDE` (`SDI: 0.441`).

## Quickstart
Requires only Python 3.9+ and `numpy`:
```bash
pip install numpy
python seam_time_v2.py
```

## License
MIT License — Open for research, cognitive modeling, and production agentic memory systems.
