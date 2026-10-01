import json
import numpy as np
from angle_model import C
from run_angle import ROOT,digest
from sync_calibration import calibrate,read_angle,simulate

def motion(turns,natural_hz,gentle):
    dt=.0002; t=np.arange(0,6.,dt); omega=2*np.pi*turns
    u=np.minimum(t,1.)
    velocity=omega*(10*u**3-15*u**4+6*u**5) if gentle else np.full(len(t),omega)
    acceleration=np.diff(np.r_[0.,velocity])/dt
    shaft=np.cumsum(velocity)*dt
    q=np.zeros(len(t)); speed=0.; wr=2*np.pi*natural_hz
    for i in range(1,len(t)):
        force=.5*acceleration[i]
        if not gentle and i==1:
            force+=.5*acceleration[0]
        speed+=dt*(force-2*.06*wr*speed-wr**2*q[i-1])
        q[i]=q[i-1]+dt*speed
    return t,shaft,q

def reference(seed,turns,natural_hz,gentle):
    t,shaft,q=motion(turns,natural_hz,gentle)
    known=1.2
    if gentle:
        after=float(np.interp(3.,t,shaft+q))
        known+=2*np.pi*max(0,int(np.ceil((after-known)/(2*np.pi))))
    nearest=int(np.argmin(abs(shaft+q-known)))
    mask=abs(t-t[nearest])<.06
    rng=np.random.default_rng(seed)
    power=np.exp(-4*np.log(2)*((shaft[mask]+q[mask]-known)/np.deg2rad(1.5))**2)
    iq=np.sqrt(power)+.1*(rng.normal(size=mask.sum())+1j*rng.normal(size=mask.sum()))
    encoder_mask=(t>=t[mask].min()-.02)&(t<=t[mask].max()+.02)
    data=dict(echo_time=t[mask]+2*1500/C+.002,iq=iq,encoder_time=t[encoder_mask],
              encoder_angle=shaft[encoder_mask]+np.deg2rad(.12)+np.deg2rad(.02)*rng.normal(size=encoder_mask.sum()),
              measured_range_m=1500.,nominal_omega=2*np.pi*turns)
    return data,known,dict(startup_peak_deg=float(np.rad2deg(abs(q).max())),
                          observation_peak_deg=float(np.rad2deg(abs(q[mask]).max())))

def main():
    path=ROOT/'settled_results.json'
    if path.exists():
        raise SystemExit('Existing results preserved')
    fits=[]; rows=[]
    for seed in range(10):
        hz=12+.8*seed
        for gentle in (False,True):
            refs=[]; known=[]; vibrations=[]
            for i,turns in enumerate((.5,.5,1.,1.,1.5,1.5)):
                data,k,v=reference(25000000+seed*10+i,turns,hz,gentle)
                refs.append(data); known.append(k); vibrations.append(v)
            try:
                cal=calibrate(refs,known)
            except ValueError as e:
                fits.append(dict(seed=seed,gentle=gentle,accepted=False,reason=str(e),vibrations=vibrations)); continue
            fits.append(dict(seed=seed,gentle=gentle,accepted=True,calibration=cal,vibrations=vibrations))
            for ti,theta in enumerate((.4,1.2,2.)):
                for wi,turns in enumerate((.65,1.25,1.8)):
                    data=simulate(26000000+seed*10+ti*3+wi,theta,turns,.002,np.deg2rad(.12),False)
                    value=read_angle(data,cal['delay_s'],cal['zero_rad'])
                    rows.append(dict(seed=seed,gentle=gentle,theta=theta,turns=turns,angle=value,
                                     error_deg=float(np.rad2deg(abs(value-theta)))))
    summary={}
    for gentle in (False,True):
        ff=[f for f in fits if f['gentle']==gentle]; rr=[r for r in rows if r['gentle']==gentle]
        summary['gentle_settled' if gentle else 'step_early']=dict(accepted=sum(f['accepted'] for f in ff),
            calibrations=len(ff),target_cases=len(rr),target_mae_deg=float(np.mean([r['error_deg'] for r in rr])) if rr else None,
            mean_startup_peak_deg=float(np.mean([v['startup_peak_deg'] for f in ff for v in f['vibrations']])),
            mean_observation_peak_deg=float(np.mean([v['observation_peak_deg'] for f in ff for v in f['vibrations']])))
    result=dict(summary=summary,fits=fits,runs=rows,hashes={p.name:digest(p) for p in (ROOT/'SETTLED_PROTOCOL.md',ROOT/'run_settled.py',ROOT/'sync_calibration.py')})
    with path.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    lines=['# Kalibracja po łagodnym rozruchu','',
           'Jawny model drgań skrętnych anteny względem wału. Płynna rampa prędkości przez 1 s; obserwacja po dodatkowych 2 s. Porównanie ze skokowym rozruchem i obserwacją pierwszego przejścia wiązki. Enkoder mierzy wał, więc drganie mocowania może wprowadzać błąd kąta wiązki.','',
           '| Strategia | Kalibracje przyjęte / 10 | Średnie maksimum drgań przy rozruchu [°] | Przy obserwacji [°] | MAE późniejszych celów [°] |','|---|---:|---:|---:|---:|']
    for name,s in summary.items():
        mae=f"{s['target_mae_deg']:.4f}" if s['target_mae_deg'] is not None else 'brak'
        lines.append(f"| {name} | {s['accepted']} | {s['mean_startup_peak_deg']:.4f} | {s['mean_observation_peak_deg']:.6f} | {mae} |")
    lines+=['','Łagodna rampa ogranicza wzbudzenie w tym modelu, a czekanie ogranicza drganie podczas pomiaru. To nie dowód całkowitego braku rezonansu. Stałe czasy 1 s i 2 s są parametrami testu, nie uniwersalnymi ustawieniami napędu.','',
            'Realna kalibracja wymaga zmierzonej charakterystyki napędu, ramp o ograniczonym przyspieszeniu i zrywie, wyboru prędkości poza rezonansami oraz potwierdzenia ustalenia obrotu z odczytów/czujnika drgań. Sama stabilność enkodera wału może nie ujawnić drgań anteny. Odmowa kalibracji jest lepsza niż wymuszanie parametrów.','',
            'Obie strategie korzystają z różnych nowych obserwacji referencji, ale tych samych osobnych ustalonych ech celów. Wynik dotyczy modelu, nie sprzętu. Nie testowano wielodrogowości, filtra impulsów ani ruchu reflektora. R/v nie zmieniono. Odtwarzanie: python run_settled.py w świeżej kopii bez settled_results.json.']
    (ROOT/'WYNIK_SETTLED.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
