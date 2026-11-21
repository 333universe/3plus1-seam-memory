import numpy as np
import seam_time_v2 as sts


def test_64bit_conservation():
    kernel = sts.FractalSeamKernel(profile="STANDARD")
    for _ in range(50):
        rep = kernel.step({"E": 0.45, "B": 0.35, "C": 0.1999})
        assert abs(sum(kernel.weights.values()) - 1.0) < 1e-12


def test_seam_quarantine_reset():
    kernel = sts.FractalSeamKernel(profile="STANDARD")
    # Perturb the 0.0001 Seam beyond its +/- 1% integrity tolerance
    rep = kernel.step({"E": 0.3333, "B": 0.3333, "C": 0.3333}, seam_perturbation=0.00005)
    assert rep["mode"] == "HOLOGRAPHIC_QUARANTINE_RESET"
    assert abs(kernel.weights["O"] - 0.0001) < 1e-12


def test_episodic_memory_no_single_turn_shards():
    mgr = sts.SeamContextMemoryManager(min_episode_turns=3)
    # 5 flow turns followed by 3 shock turns
    for i in range(1, 6):
        mgr.ingest_turn(i, "Assistant", f"Tool step {i}", "Tool Flow", 75.0, 0.95, 0.16)
    for i in range(6, 9):
        mgr.ingest_turn(i, "User", f"Shock event {i}", "Conflict", 25.0, 0.40, 0.94)

    assert len(mgr.archived_episodes) == 1
    assert mgr.archived_episodes[0].start_turn == 1
    assert mgr.archived_episodes[0].end_turn == 5
    assert mgr.archived_episodes[0].turn_count == 5


if __name__ == "__main__":
    test_64bit_conservation()
    test_seam_quarantine_reset()
    test_episodic_memory_no_single_turn_shards()
    print("ALL REPOSITORY UNIT TESTS PASSED!")

