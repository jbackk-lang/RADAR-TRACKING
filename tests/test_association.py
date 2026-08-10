import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.association import hungarian_associate


def euclid(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def test_simple_one_to_one_match():
    track_ids = ["A", "B"]
    track_pos = {"A": (0, 0), "B": (10, 10)}
    detections = [(0.5, 0.5), (10.5, 10.5)]
    assignments, unmatched_d, unmatched_t = hungarian_associate(
        track_ids, detections,
        cost_fn=lambda i, j: euclid(track_pos[track_ids[i]], detections[j]),
        gate_threshold=5.0,
    )
    assert assignments == {"A": 0, "B": 1}
    assert unmatched_d == []
    assert unmatched_t == []


def test_gating_rejects_far_pairs():
    track_ids = ["A"]
    track_pos = {"A": (0, 0)}
    detections = [(100, 100)]
    assignments, unmatched_d, unmatched_t = hungarian_associate(
        track_ids, detections,
        cost_fn=lambda i, j: euclid(track_pos[track_ids[i]], detections[j]),
        gate_threshold=5.0,
    )
    assert assignments == {}
    assert unmatched_d == [0]
    assert unmatched_t == ["A"]


def test_no_tracks_all_detections_unmatched():
    assignments, unmatched_d, unmatched_t = hungarian_associate(
        [], [(0, 0), (1, 1)], cost_fn=lambda i, j: 0.0, gate_threshold=5.0
    )
    assert assignments == {}
    assert unmatched_d == [0, 1]
    assert unmatched_t == []


def test_no_detections_all_tracks_unmatched():
    assignments, unmatched_d, unmatched_t = hungarian_associate(
        ["A", "B"], [], cost_fn=lambda i, j: 0.0, gate_threshold=5.0
    )
    assert assignments == {}
    assert unmatched_d == []
    assert unmatched_t == ["A", "B"]


def test_hungarian_finds_lower_total_cost_than_greedy():
    """
    Classic assignment-problem example where greedy (process tracks in
    a fixed order, each claiming its own best still-available
    detection) locks in a choice that is locally fine for the first
    track but starves a later track of any good alternative --
    producing a higher TOTAL cost than the jointly optimal assignment
    Hungarian finds.

    Cost matrix (rows = tracks A, B; columns = detections 0, 1):
            d0   d1
        A:   1    2
        B:   1    3

    Greedy (A first): A grabs d0 (cost 1, its own closest). B is left
    with d1 (cost 3). Total = 4.
    Hungarian (global optimum): A -> d1 (cost 2), B -> d0 (cost 1).
    Total = 3 -- strictly better, even though A does not get its own
    single closest match.
    """
    costs = {("A", 0): 1, ("A", 1): 2, ("B", 0): 1, ("B", 1): 3}
    track_ids = ["A", "B"]
    detections = [0, 1]

    assignments, _, _ = hungarian_associate(
        track_ids, detections,
        cost_fn=lambda i, j: costs[(track_ids[i], detections[j])],
        gate_threshold=10.0,
    )
    total = sum(costs[(tid, j)] for tid, j in assignments.items())
    assert assignments == {"A": 1, "B": 0}
    assert total == 3


def test_greedy_would_have_taken_the_worse_total():
    """Same cost matrix as above, showing what a naive greedy
    (order-dependent, each track claims its own best still-available
    detection) actually produces -- worse total cost than Hungarian."""
    costs = {("A", 0): 1, ("A", 1): 2, ("B", 0): 1, ("B", 1): 3}
    track_ids = ["A", "B"]
    detections = [0, 1]

    available = list(detections)
    greedy = {}
    for tid in track_ids:
        best_j = min(available, key=lambda j: costs[(tid, j)])
        greedy[tid] = best_j
        available.remove(best_j)

    total_greedy = sum(costs[(tid, j)] for tid, j in greedy.items())
    assert greedy == {"A": 0, "B": 1}
    assert total_greedy == 4  # strictly worse than Hungarian's 3
