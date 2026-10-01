"""Local browser demo. Start with python web_demo.py; no extra dependencies."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs
import webbrowser
import numpy as np
from core.radar_tracker import RadarTracker

ROOT = Path(__file__).resolve().parent
SCENES = ('mixed', 'crossing', 'formation', 'turning')


def build_demo(model='timdr', scene='mixed', count=8, seed=20261002):
    if model not in ('cv', 'timdr', 'robust') or scene not in SCENES or count not in (4, 8, 12):
        raise ValueError('Invalid demo selection')
    rng = np.random.default_rng(seed)
    tracker = RadarTracker(d_max=1.2, k_min=1, gate_chi2=30., smoothing=.7,
                           use_timdr=model != 'cv',
                           timdr_variant='robust' if model == 'robust' else 'legacy',
                           position_sigma=.18)
    frames = []
    for frame in range(40):
        t = frame * .5
        truth = []
        for j in range(count):
            col, row = j % 4, j // 4
            if scene == 'formation':
                x, y = 10 + col * 10 + .9 * t, -20 + row * 16 + .25 * t
            elif scene == 'crossing':
                x = 10 + col * 13 + (1 if j % 2 == 0 else -1) * .9 * t
                y = -20 + row * 17 + (1 if j % 2 else -1) * .5 * t
            elif scene == 'turning':
                x = 10 + col * 12 + 6 * np.sin(.14 * t + j * .25)
                y = -20 + row * 17 + 6 * (1 - np.cos(.14 * t + j * .25))
            elif j % 3 == 0:
                x, y = 10 + col * 12 + .9 * t, -20 + row * 17 + .12 * t
            elif j % 3 == 1:
                x, y = 10 + col * 12 + .7 * t, -20 + row * 17 + .18 * max(0, t - 7) ** 1.4
            else:
                x = 10 + col * 12 + 3 * np.sin(.18 * t)
                y = -20 + row * 17 + .5 * t
            truth.append(dict(id=j + 1, x=float(x), y=float(y)))
        # Three echoes per simulated object; truth IDs are not supplied to tracker.
        points = [dict(x=o['x'] + float(rng.normal(0, .18)),
                       y=o['y'] + float(rng.normal(0, .18)), t=t)
                  for o in truth for _ in range(3)]
        rng.shuffle(points)
        result = tracker.update(points)
        tracker.prune_stale(t, 2.)
        tracks = [dict(id=tid, x=info['x'], y=info['y'],
                       score=info['timdr']['TIMDR'], manoeuvre=info['manoeuvre'],
                       predicted=info['predicted_next']) for tid, info in result.items()]
        frames.append(dict(t=t, points=points, tracks=tracks, truth=truth))
    # Convert any numpy scalar returned by the core without exposing internals.
    return json.loads(json.dumps(dict(model=model, scene=scene, objects=count, frames=frames),
                                 default=lambda x: x.item()))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/api/demo':
            query = parse_qs(url.query)
            try:
                result = build_demo(query.get('model', ['timdr'])[0],
                                    query.get('scene', ['mixed'])[0],
                                    int(query.get('count', ['8'])[0]))
                self.send_bytes(200, json.dumps(result).encode(), 'application/json')
            except (ValueError, TypeError):
                self.send_bytes(400, b'{"error":"Invalid selection"}', 'application/json')
            return
        files = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}
        if url.path not in files:
            self.send_bytes(404, b'Not found', 'text/plain')
            return
        path = ROOT / 'web' / files[url.path]
        content_type = {'html': 'text/html', 'js': 'text/javascript', 'css': 'text/css'}[path.suffix[1:]]
        self.send_bytes(200, path.read_bytes(), content_type)

    def send_bytes(self, code, content, content_type):
        self.send_response(code)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-open', action='store_true')
    args = parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        url = f'http://127.0.0.1:{server.server_port}'
        print(f'Radar demo: {url} (Ctrl+C to stop)', flush=True)
        if not args.no_open:
            threading.Timer(.5, lambda: webbrowser.open(url)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
