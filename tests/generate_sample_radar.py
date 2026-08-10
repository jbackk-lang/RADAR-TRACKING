"""
Generates data/sample_radar.npy -- synthetic multi-frame radar detections
for demos and tests. This is NOT real radar data; it is a scripted scene
with two moving targets (each emitting a small cluster of returns per
frame, like a real extended target) plus isolated clutter points, so the
tracker's TRM filter and clustering have something real to reject/merge.

Run: python3 data/generate_sample_radar.py
Produces a numpy structured array with fields:
    frame (int), x (float), y (float), t (float)
Load it back with:
    import numpy as np
    data = np.load("data/sample_radar.npy")
    frame0 = data[data["frame"] == 0]
"""
import os
import random
import numpy as np


def generate(n_frames: int = 12, seed: int = 7):
    rng = random.Random(seed)
    rows = []

    def cluster(cx, cy, t, frame, n=2, spread=0.6):
        for _ in range(n):
            rows.append((
                frame,
                cx + rng.uniform(-spread, spread),
                cy + rng.uniform(-spread, spread),
                float(t),
            ))

    for frame in range(n_frames):
        t = float(frame)

        # Target A: straight line, constant speed
        cluster(2 * t, 0, t, frame)

        # Target B: straight, then a sharp turn around frame 5
        if frame <= 5:
            bx, by = 1.5 * t, 25
        else:
            bx, by = 7.5, 25 + 2.5 * (frame - 5)
        cluster(bx, by, t, frame)

        # Target C: slow curve (gradual turn), starts later
        if frame >= 3:
            angle = 0.25 * (frame - 3)
            cx = 40 - 3 * (frame - 3) * np.cos(angle)
            cy = -10 + 3 * (frame - 3) * np.sin(angle)
            cluster(cx, cy, t, frame)

        # clutter: 1-2 isolated points per frame, no companions
        for _ in range(rng.randint(1, 2)):
            rows.append((frame, rng.uniform(-60, 60), rng.uniform(-60, 60), t))

    dtype = [("frame", "i4"), ("x", "f8"), ("y", "f8"), ("t", "f8")]
    return np.array(rows, dtype=dtype)


if __name__ == "__main__":
    data = generate()
    out_path = os.path.join(os.path.dirname(__file__), "sample_radar.npy")
    np.save(out_path, data)
    print(f"wrote {len(data)} detections across {data['frame'].max() + 1} frames to {out_path}")
