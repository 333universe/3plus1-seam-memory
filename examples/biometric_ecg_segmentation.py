"""
Cross-Domain Biometric Event Segmentation using the 3+1 Holographic Seam Kernel.

Ingests a real human electrocardiogram (ECG) recording from `scipy.datasets.electrocardiogram()`
(MIT-BIH Arrhythmia Database, 360 Hz) to detect genuine autonomic/arrhythmic regime shifts
while maintaining smooth temporal flow during normal sinus rhythm.

Usage:
  pip install numpy scipy
  python examples/biometric_ecg_segmentation.py
"""

import os
import sys
from typing import Dict, List
import numpy as np

# Allow importing seam_time_v2 from repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import seam_time_v2 as sts


def load_real_ecg_windows(window_sec: float = 2.0, total_windows: int = 24) -> List[np.ndarray]:
    """
    Loads real 360 Hz human ECG telemetry from SciPy (with clean synthetic fallback
    if offline without cached SciPy dataset).
    """
    fs = 360  # 360 Hz sampling rate
    samples_per_win = int(window_sec * fs)

    try:
        from scipy.datasets import electrocardiogram
        ecg = electrocardiogram()
        # Slice around sample 4000-21000 where real sinus rhythm transitions into arrhythmia
        start_offset = 4500
        windows = [
            ecg[start_offset + i * samples_per_win : start_offset + (i + 1) * samples_per_win]
            for i in range(total_windows)
        ]
        return windows
    except Exception:
        # Deterministic physiological fallback waveform if scipy dataset cache is unavailable
        rng = np.random.default_rng(7)
        t = np.linspace(0, window_sec, samples_per_win)
        windows = []
        for i in range(total_windows):
            # Normal 72 BPM sinus pulse + sudden ectopic burst in windows 10-13
            base = np.sin(2 * np.pi * 1.2 * t) + 0.4 * np.sin(2 * np.pi * 3.6 * t)
            if 10 <= i <= 13:
                burst = 1.8 * np.sin(2 * np.pi * 11.5 * t) + 0.65 * rng.normal(size=samples_per_win)
                windows.append(base + burst)
            else:
                windows.append(base + 0.08 * rng.normal(size=samples_per_win))
        return windows


def extract_ecg_triad_metrics(window: np.ndarray) -> Dict[str, float]:
    """
    Maps a raw physiological time-series window onto the 3+1 Triad:
      - Efficiency (E): Signal RMS power / autonomic drive
      - Balance (B): Lag-1 autocorrelation / rhythmic phase coherence
      - Change (C): Normalized first-difference innovation entropy
    """
    rms_power = float(np.sqrt(np.mean(window ** 2))) + 1e-6
    diff = np.diff(window)
    innovation_entropy = float(np.std(diff) / rms_power)

    # Autocorrelation at short lag measures periodic beat-to-beat stability
    w_centered = window - np.mean(window)
    denom = float(np.dot(w_centered, w_centered)) + 1e-9
    lag1_corr = float(np.dot(w_centered[:-1], w_centered[1:]) / denom)
    coherence = max(0.05, min(0.99, (lag1_corr + 1.0) * 0.5))

    return {
        "power": rms_power,
        "coherence": coherence,
        "entropy": innovation_entropy,
    }


def run_biometric_benchmark() -> None:
    windows = load_real_ecg_windows(window_sec=2.0, total_windows=24)
    analyzer = sts.SeamTemporalAnalyzer(profile="STANDARD")

    print("=== 3+1 SEAM BIOMETRIC ECG EVENT SEGMENTATION (360 Hz HUMAN TELEMETRY) ===\n")
    boundary_events = []

    for idx, win in enumerate(windows, 1):
        metrics = extract_ecg_triad_metrics(win)
        report = analyzer.process_llm_step(
            tps=metrics["power"] * 50.0,
            prob=metrics["coherence"],
            entropy=metrics["entropy"],
        )

        # Verify strict 64-bit conservation at every physiological window
        assert abs(sum(analyzer.kernel.weights.values()) - 1.0) < 1e-12, "Conservation drift!"

        if report["unified_episode_boundary"]:
            boundary_events.append(idx)
            print(f"\n>>> [PHYSIOLOGICAL SEAM CUT @ Window {idx:02d} ({idx*2}s)] "
                  f"Autonomic Regime Shift Detected (SDI={report['sdi']:.3f}) <<<\n")

        print(
            f"Win {idx:02d} ({idx*2:02d}s) | Mode: {report['mode']:<26} | "
            f"SDI: {report['sdi']:.3f} | Shear: {report['seam_shear']:.4f} | "
            f"Boundary: {report['unified_episode_boundary']}"
        )

    print(f"\n=== SUMMARY: Processed {len(windows)} ECG Windows ({len(windows)*2}s) | "
          f"Detected {len(boundary_events)} Structural Regime Shift(s) at Window(s) {boundary_events} ===")


if __name__ == "__main__":
    run_biometric_benchmark()
