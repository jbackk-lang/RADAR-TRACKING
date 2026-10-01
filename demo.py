"""
End-to-end demo: loads data/sample_radar.npy, runs it through
RadarTracker frame by frame, prints a per-frame summary, and saves two
visualizations (the last frame, and full trajectories) to demo_output/.

Run: python3 demo.py
"""
import os
import argparse
import numpy as np

from core.radar_tracker import RadarTracker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene-model', choices=('cv', 'timdr'),
                        help='Run experimental scene recognition with CV or TIMDR prediction')
    parser.add_argument('--scene', choices=('diverging', 'parallel', 'rotating'), default='diverging')
    args = parser.parse_args()
    if args.scene_model:
        from core.scene_demo import run_scene_demo
        run_scene_demo(args.scene_model, args.scene)
        return
    from visualizer.tracking_visualizer import plot_frame, plot_history
    here = os.path.dirname(__file__)
    data = np.load(os.path.join(here, "data", "sample_radar.npy"))
    n_frames = int(data["frame"].max()) + 1

    tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=1, gate_chi2=30.0)

    last_points, last_result = [], {}
    for frame_idx in range(n_frames):
        frame_rows = data[data["frame"] == frame_idx]
        points = [{"x": float(r["x"]), "y": float(r["y"]), "t": float(r["t"])} for r in frame_rows]

        result = tracker.update(points)
        tracker.prune_stale(current_t=points[0]["t"] if points else frame_idx, max_age=4)

        manoeuvring = [tid for tid, info in result.items() if info["manoeuvre"]]
        print(f"frame {frame_idx:2d}: {len(points):2d} raw -> {len(result)} tracks alive"
              + (f"  MANOEUVRING: {manoeuvring}" if manoeuvring else ""))

        last_points, last_result = points, result

    out_dir = os.path.join(here, "demo_output")
    os.makedirs(out_dir, exist_ok=True)
    plot_frame(last_points, last_result, save_path=os.path.join(out_dir, "last_frame.png"))
    plot_history(tracker, save_path=os.path.join(out_dir, "trajectories.png"))
    print(f"\nsaved visualizations to {out_dir}/")


if __name__ == "__main__":
    main()
