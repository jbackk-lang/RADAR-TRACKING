import json
import numpy as np
from run_angle import ROOT,digest
from stereo_model import CENTER,JointEstimator,simulate
from multiscan_model import MultiScanEstimator

def correct(out,truth):
    return len(out['angles'])==len(truth) and bool(np.all(np.rad2deg(abs(np.sort(out['angles'])-np.sort(truth)))<=.25))

def main():
    path=ROOT/'multiscan_results.json'; iqpath=ROOT/'multiscan_iq.npz'
    if path.exists() or iqpath.exists():
        raise SystemExit('Existing results preserved')
    center=CENTER+np.deg2rad(.037)
    cases=[]
    for sep in (.75,1.5):
        for ratio in (.25,.5,1.):
            for seed in range(5):
                cases.append(dict(kind='pair',sep=sep,ratio=ratio,seed=seed))
    for kind in ('single','disappear','appear'):
        for seed in range(10):
            cases.append(dict(kind=kind,sep=.75,ratio=.5,seed=seed))
    models=(JointEstimator(2),MultiScanEstimator(2)); rows=[]; arrays={}
    for ci,case in enumerate(cases):
        scans=[]; truth=[]
        for step in range(4):
            pair=case['kind']=='pair' or (case['kind']=='disappear' and step<3) or (case['kind']=='appear' and step==3)
            truth=[center-np.deg2rad(case['sep']/2)]
            if pair:
                truth.append(center+np.deg2rad(case['sep']/2))
            rng=np.random.default_rng(17000000+ci*10+step)
            amplitudes=[rng.uniform(.8,1.2)*np.exp(1j*rng.uniform(-np.pi,np.pi))]
            if pair:
                amplitudes.append(case['ratio']*rng.uniform(.8,1.2)*np.exp(1j*rng.uniform(-np.pi,np.pi)))
            scans.append(simulate(18000000+ci*10+step,truth,amplitudes,2))
        key=f'case_{ci}'; arrays[key]=np.array(scans)
        proposal=models[1].propose(scans[:3])
        multi=models[1].confirm(proposal,scans[3])
        single=models[0].fit(scans[3])
        rows.append(dict(**case,iq_key=key,truth_fourth=truth,proposal=proposal,multi=multi,single=single,
                         multi_correct=correct(multi,truth),single_correct=correct(single,truth)))
    summary={}
    for kind in ('pair','single','disappear','appear'):
        rr=[r for r in rows if r['kind']==kind]
        summary[kind]=dict(cases=len(rr),multi_correct=sum(r['multi_correct'] for r in rr),
                           single_correct=sum(r['single_correct'] for r in rr),
                           multi_uncertain=sum(r['multi']['state']=='uncertain' for r in rr),
                           multi_false_pair=sum(r['multi']['count']==2 for r in rr if len(r['truth_fourth'])==1),
                           single_false_pair=sum(r['single']['count']==2 for r in rr if len(r['truth_fourth'])==1))
    with iqpath.open('xb') as f:
        np.savez_compressed(f,**arrays)
    result=dict(summary=summary,runs=rows,iq_sha256=digest(iqpath),
                hashes={p.name:digest(p) for p in (ROOT/'MULTISCAN_PROTOCOL.md',ROOT/'multiscan_model.py',ROOT/'run_multiscan.py',ROOT/'stereo_model.py')})
    with path.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    lines=['# Wspólny model trzech skanów, potwierdzenie na czwartym','',
           'Stałe kąty, zmienne zespolone amplitudy i fazy; 60 sekwencji, 240 skanów, dwa kanały. Czwarty skan nie służy do dobierania kątów wieloskanowego modelu. Niezależny wariant bazowy dopasowuje wyłącznie skan 4.','',
           '| Warunki | Przypadki | Wieloskanowy poprawny | Jeden skan poprawny | Odmowy wieloskanowego |','|---|---:|---:|---:|---:|']
    for kind,s in summary.items():
        lines.append(f"| {kind} | {s['cases']} | {s['multi_correct']} | {s['single_correct']} | {s['multi_uncertain']} |")
    lines+=['','Poprawność: liczba celów zgodna z prawdą skanu 4 i wszystkie kąty z błędem <=.25°. Odmowa oznacza brak potwierdzonych kątów, nie usunięcie toru. Przy zaniku lub pojawieniu celu założenie stałych celów nie jest spełnione. To osobne kontrole ograniczeń pamięci, nie dane do strojenia.','',
            'Nie wykazujemy uniwersalnej przewagi. Model wieloskanowy wykorzystuje więcej danych i zna idealny model wiązki. Brak ruchu, wielodrogowości, błędów synchronizacji i rzeczywistego sprzętu. Pojawienie nowego celu wymaga uruchomienia nowego dopasowania, nie samego potwierdzania starych kątów.','',
            'Odtwarzanie: python run_multiscan.py w osobnej kopii bez multiscan_results.json i multiscan_iq.npz. Surowe I/Q zapisane; wyniki chronione przed nadpisaniem.']
    (ROOT/'WYNIK_MULTISCAN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
