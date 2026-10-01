import hashlib
import json
from pathlib import Path
import numpy as np
from clock_experiment.online_calibration import OnlineCalibration, PARAMS
from clock_experiment.minimal_calibration import MinimalCalibration
from clock_experiment.calibration_guard import CalibrationGuard
from clock_experiment.radar_compensation import simulate, estimate
from clock_experiment.reference_calibration import calibrate, apply_calibration

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'validation/results.json'
KEYS = tuple(PARAMS)
MODES = ('raw','memory','decay_only','minimal')
SCENARIOS = ('new_noise','hidden_change')
GRID = (0.,.1,.2,.25,.35,.5,.75,1.)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def errors(reading,truth):
    out = {k:abs(reading[k]-truth[k]) for k in KEYS}
    out['bearing_rad'] = abs(float(np.angle(np.exp(1j*(reading['bearing_rad']-truth['bearing_rad'])))))
    return out

def corrected_estimate(raw,cal):
    out = dict(raw)
    for key,(parameter,scale,_) in PARAMS.items():
        out[key] -= cal[parameter]/scale
    out['bearing_rad'] = float(np.angle(np.exp(1j*out['bearing_rad'])))
    limit = raw['unambiguous_speed_m_s']
    out['radial_velocity_m_s'] = (out['radial_velocity_m_s']+limit)%(2*limit)-limit
    return out

def mean_errors(rows,modes=MODES):
    return {m:{k:float(np.mean([r['errors'][m][k] for r in rows])) for k in KEYS} for m in modes}

def develop():
    source = json.loads(SOURCE.read_text(encoding='utf-8'))
    # Check analytical replay against saved actual I/Q compensation for both modes.
    lookup = {(d['scenario'],d['seed'],d['step'],d['mode']):d for d in source['decisions']}
    for row in source['runs']:
        for mode in ('memory','online'):
            d = lookup[(row['scenario'],row['seed'],row['step'],mode)]
            replay = corrected_estimate(row['readings']['raw'],d['selected'])
            assert all(np.isclose(replay[k],row['readings'][mode][k],rtol=0,atol=1e-10) for k in KEYS)
    candidates = {}
    for strength in GRID:
        models,chosen = {},{}
        for d in source['decisions']:
            if d['mode'] != 'memory':
                continue
            key = (d['scenario'],d['seed'])
            if key not in models:
                models[key] = MinimalCalibration(d['candidate_before'],{k:strength for k in KEYS})
            cal,_ = models[key].observe(d['step'],d['raw'],d['quality_ok'])
            chosen[(*key,d['step'])] = cal
        candidates[str(strength)] = {}
        for scenario in SCENARIOS:
            rr = [r for r in source['runs'] if r['scenario']==scenario]
            candidates[str(strength)][scenario] = {k:float(np.mean([
                errors(corrected_estimate(r['readings']['raw'],chosen[(scenario,r['seed'],r['step'])]),r['truth'])[k]
                for r in rr])) for k in KEYS}
    raw = {s:source['summary'][s]['mae']['raw'] for s in SCENARIOS}
    strengths,eligible = {},{}
    for k in KEYS:
        eligible[k] = [a for a in GRID if all(candidates[str(a)][s][k] <= .8*raw[s][k] for s in SCENARIOS)]
        strengths[k] = min(eligible[k]) if eligible[k] else 0.
    sources = [ROOT/'PROTOCOL.md',ROOT/'run_minimal.py',*sorted((ROOT/'clock_experiment').glob('*.py'))]
    result = dict(strengths=strengths,eligible=eligible,criterion='MAE <= 0.8 raw in both development scenarios',grid=GRID,
                  development_source_sha256=digest(SOURCE),source_hashes={str(p.relative_to(ROOT)):digest(p) for p in sources},
                  development_mae=candidates,development_raw_mae=raw,analytic_replay_verified_measurements=1440)
    with (ROOT/'selection.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print('Frozen strengths:',strengths,flush=True)
    return result

def evaluate(selection):
    strengths = selection['strengths']
    rows,decisions = [],[]
    changes = [0,.14,.28,.42,.56,.7,.35,0,-.35,-.7,-.7,0]
    for si,scenario in enumerate(SCENARIOS):
        for seed in range(200,220):
            base = 5000000 + si*1000000 + seed*1000
            iq,p,_ = simulate(base,range_m=900,bearing=-.2)
            p['bearing'] += float(np.random.default_rng(base+1).normal(0,.002))
            cal = calibrate(iq,p,900,-.2)
            guard = CalibrationGuard(cal)
            models = dict(memory=OnlineCalibration(cal,adapt=False),
                          decay_only=MinimalCalibration(cal,{k:1. for k in KEYS}),
                          minimal=MinimalCalibration(cal,strengths))
            for step,delta in enumerate(changes):
                state = dict(trigger_samples=0 if step in (9,10) else 3,
                             bearing_bias=0 if step in (9,10) else .025,instrument_speed=.7+delta)
                weak = step in (4,5)
                if scenario=='hidden_change':
                    weak = step in (4,5,6)
                    if step in (4,5,6,7):
                        state = dict(trigger_samples=0,bearing_bias=0.,instrument_speed=0.)
                iq,p,_ = simulate(base+10+step,range_m=1500,bearing=.35,noise=1. if weak else .15,**state)
                p['bearing'] += float(np.random.default_rng(base+30+step).normal(0,.002))
                _,quality = guard.validate(iq,p,1500,.35)
                raw_ref = quality['raw']
                selected = {}
                for mode,model in models.items():
                    selected[mode],d = model.observe(step,raw_ref,quality['quality_ok'])
                    decisions.append(dict(scenario=scenario,seed=seed,step=step,mode=mode,initial=cal,
                                          raw=raw_ref,quality_ok=quality['quality_ok'],selected=selected[mode],**d))
                for target,(distance,bearing,speed) in enumerate(((600.,-.4,0.),(1200.,.1,0.),(1800.,.6,2.))):
                    iq,p,_ = simulate(base+100+step*3+target,range_m=distance,bearing=bearing,speed=speed,**state)
                    truth = dict(range_m=distance,bearing_rad=bearing,radial_velocity_m_s=speed)
                    readings = {'raw':estimate(iq,**p)}
                    for mode,c in selected.items():
                        readings[mode] = apply_calibration(iq,p,c)
                        analytic = corrected_estimate(readings['raw'],c)
                        assert all(np.isclose(analytic[k],readings[mode][k],rtol=0,atol=1e-10) for k in KEYS)
                    rows.append(dict(scenario=scenario,seed=seed,step=step,target=target,truth=truth,readings=readings,
                                     errors={m:errors(v,truth) for m,v in readings.items()}))
            print(scenario,seed,flush=True)
    summaries = {}
    rng = np.random.default_rng(20261002)
    for scenario in SCENARIOS:
        rr = [r for r in rows if r['scenario']==scenario]
        ds = [d for d in decisions if d['scenario']==scenario]
        per_seed = {str(s):mean_errors([r for r in rr if r['seed']==s]) for s in range(200,220)}
        comparisons = {}
        indices = rng.integers(0,20,size=(10000,20))
        for a,b in (('minimal','raw'),('minimal','memory'),('decay_only','memory'),('minimal','decay_only')):
            comparisons[a+' minus '+b] = {}
            for k in KEYS:
                diff = np.array([per_seed[str(s)][a][k]-per_seed[str(s)][b][k] for s in range(200,220)])
                comparisons[a+' minus '+b][k] = dict(mean=float(diff.mean()),ci95=np.quantile(diff[indices].mean(axis=1),[.025,.975]).tolist())
        harm = {m:{k:dict(fraction=float(np.mean([r['errors'][m][k]-r['errors']['raw'][k]>PARAMS[k][2] for r in rr if r['step'] in (4,5,6)])),
                         mean_positive_excess=float(np.mean([max(0.,r['errors'][m][k]-r['errors']['raw'][k]) for r in rr if r['step'] in (4,5,6)])))
                   for k in KEYS} for m in MODES if m!='raw'}
        intervention = {m:{k:float(np.mean([abs(d['selected'][p]/scale) for d in ds if d['mode']==m]))
                          for k,(p,scale,_) in PARAMS.items()} for m in MODES if m!='raw'}
        summaries[scenario] = dict(mae=mean_errors(rr),per_seed=per_seed,comparisons=comparisons,
                                  harm_steps_4_6=harm,mean_intervention=intervention,
                                  per_step={str(s):mean_errors([r for r in rr if r['step']==s]) for s in range(12)})
    result = dict(summary=summaries,runs=rows,decisions=decisions,strengths=strengths,
                  selection_sha256=digest(ROOT/'selection.json'),reference_observations=480,target_measurements=1440,
                  additional_controller_observations=0)
    with (ROOT/'results.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps({s:v['mae'] for s,v in summaries.items()},indent=2))

def main():
    if (ROOT/'results.json').exists() or (ROOT/'selection.json').exists():
        raise SystemExit('Existing results or frozen selection preserved; use a fresh copy for another run')
    selection = develop()
    evaluate(selection)

if __name__=='__main__':
    main()
