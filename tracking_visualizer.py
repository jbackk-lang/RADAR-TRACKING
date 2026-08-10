"""
Minimal matplotlib visualizer for RadarTracker output.

Not required to run the tracker -- purely for eyeballing results
during development or demos. Uses the Agg backend by default so it
also works headless (e.g. in CI / over SSH); pass show=True with a
GUI-capable backend if you want an interactive window.
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg", force=False)
import matplotlib.pyplot as plt


def plot_frame(points, frame_result, ax=None, show=False, save_path=None):
    """
    points: raw detections for this frame (list of {'x','y','t'}).
    frame_result: the dict returned by RadarTracker.update(points).
    """
    created_ax = ax is None
    if created_ax:
        fig, ax = plt.subplots(figsize=(6, 6))

    if points:
        ax.scatter([p["x"] for p in points], [p["y"] for p in points],
                   c="lightgray", s=15, label="raw detections")

    for track_id, info in frame_result.items():
        color = "red" if info.get("manoeuvre") else "tab:blue"
        ax.scatter([info["x"]], [info["y"]], s=40, c=color)
        ax.annotate(str(track_id), (info["x"], info["y"]))
        pred = info.get("predicted_next")
        if pred:
            ax.plot([info["x"], pred["x"]], [info["y"], pred["y"]],
                    linestyle="--", c="green", alpha=0.6)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("RadarTracker -- single frame\n(gray = raw, blue/red = tracks, dashed = predicted next)")
    ax.legend(loc="upper right", fontsize=8)

    if save_path:
        plt.gcf().savefig(save_path, dpi=120, bbox_inches="tight")
    if show and created_ax:
        plt.show()
    return ax


def plot_history(tracker, ax=None, show=False, save_path=None):
    """Plot the full recorded trajectory (tracker.tracks history buffer,
    limited to `history_len`) of every currently-alive track."""
    created_ax = ax is None
    if created_ax:
        fig, ax = plt.subplots(figsize=(6, 6))

    for track_id, hist in tracker.tracks.items():
        xs = [p["x"] for p in hist]
        ys = [p["y"] for p in hist]
        ax.plot(xs, ys, marker="o", markersize=3, label=f"track {track_id}")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Track trajectories (recent history window)")
    ax.legend(loc="upper right", fontsize=8)

    if save_path:
        plt.gcf().savefig(save_path, dpi=120, bbox_inches="tight")
    if show and created_ax:
        plt.show()
    return ax
