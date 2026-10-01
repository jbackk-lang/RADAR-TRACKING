"""Small scene recognition demo with standard CV or TIMDR prediction."""
import json
import numpy as np
from .scene_model import recognize_scene


def run_scene_demo(model='cv', scenario='diverging'):
    if model not in ('cv', 'timdr'):
        raise ValueError('model must be cv or timdr')
    if scenario not in ('diverging', 'parallel', 'rotating'):
        raise ValueError('unknown scenario')
    rng = np.random.default_rng(20261001)
    times = np.arange(12) * .5
    center = np.column_stack([500 + 3 * times, .5 * times])
    velocity = np.tile([3., .5], (len(times), 1))
    if scenario == 'rotating':
        offsets = 2 * np.column_stack([np.cos(.5 * times), np.sin(.5 * times)])
        changes = np.column_stack([-np.sin(.5 * times), np.cos(.5 * times)])
        positions = np.stack([center - offsets, center + offsets], axis=1)
        velocities = np.stack([velocity - changes, velocity + changes], axis=1)
    else:
        positions = np.stack([center + [0., -2.], center + [0., 2.]], axis=1)
        velocities = np.stack([velocity, velocity], axis=1)
        if scenario == 'diverging':
            positions[:, 1] += times[:, None] * [1.5, 1.]
            velocities[:, 1] += [1.5, 1.]
    doppler = np.sum(positions * velocities, axis=2) / np.linalg.norm(positions, axis=2)
    positions += rng.normal(0, .12, positions.shape)
    doppler += rng.normal(0, .15, doppler.shape)
    swaps = rng.integers(0, 2, len(times)).astype(bool)
    positions[swaps] = positions[swaps, ::-1]
    doppler[swaps] = doppler[swaps, ::-1]
    result = recognize_scene(positions, doppler, times, use_timdr=model == 'timdr')
    # Keep terminal output compact; full diagnostics remain available from the API.
    output = dict(model=model, scenario=scenario, **{k: v for k, v in result.items() if k != 'association'})
    print(json.dumps(output, indent=2))
    return result
