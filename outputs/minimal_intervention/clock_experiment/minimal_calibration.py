"""Partial, reference-confirmed correction with decay from confirmation time."""
import numpy as np
from .online_calibration import OnlineCalibration, PARAMS


class MinimalCalibration(OnlineCalibration):
    def __init__(self, initial, strengths, ttl=2., decay=.5):
        if set(strengths) != set(PARAMS):
            raise ValueError('One strength per measurement required')
        if any(not np.isfinite(v) or not 0 <= v <= 1 for v in strengths.values()):
            raise ValueError('Strengths must be finite and in [0,1]')
        if not np.isfinite(decay) or not 0 <= decay <= 1:
            raise ValueError('Decay must be finite and in [0,1]')
        proposal = dict(initial)
        for key, (parameter, _, _) in PARAMS.items():
            value = proposal[parameter]
            if not np.isfinite(value):
                raise ValueError('Finite calibration required')
            if key == 'bearing_rad':
                value = float(np.angle(np.exp(1j*value)))
            proposal[parameter] = strengths[key]*value
        super().__init__(proposal, adapt=False, ttl=ttl)
        self.strengths = dict(strengths)
        self.decay = decay

    def observe(self, time, raw, quality, known_range=1500., known_bearing=.35):
        selected, decision = super().observe(time, raw, quality, known_range, known_bearing)
        factors = {}
        for key, (parameter, _, _) in PARAMS.items():
            state = decision['states'][key]
            factor = 1. if state == 'confirmed' else 0.
            if state == 'uncertain':
                age = time - self.confirmed[key][1]
                factor = self.decay**age
                selected[parameter] *= factor
            decision['applied'][key] = selected[parameter]
            factors[key] = factor
        decision['decay_factors'] = factors
        decision['strengths'] = dict(self.strengths)
        return selected, decision
