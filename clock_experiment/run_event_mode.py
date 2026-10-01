import hashlib
import json
from pathlib import Path
import numpy as np
from .event_mode import fit_mode,score_mode

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'mode_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    source=ROOT/'flash_results/summary.json'
    flashes=json.loads(source.read_text()); rows=[]; rng=np.random.default_rng(20261002)
    for row in flashes['runs']:
        path=Path(row['source_path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        with np.load(path) as z:
            t=(z['ts']-z['ts'][0])/1000; frames=z['frames']
        chunks=np.split(np.arange(len(t)),np.flatnonzero(np.diff(frames)!=1)+1)
        split=(len(chunks)+1)//2
        event_times={ci:np.array(sorted(set(e['time_s'] for e in row['events'] if e['chunk']==ci))) for ci in range(len(chunks))}
        train=np.concatenate([event_times[i] for i in range(split)])
        test=np.concatenate([event_times[i] for i in range(split,len(chunks))]) if split<len(chunks) else np.array([])
        result={'name':row['name'],'train_events':len(train),'test_events':len(test),'train_chunks':split,
                'test_chunks':len(chunks)-split,'source_sha256':row['sha256']}
        if min(len(train),len(test))<6:
            result['status']='insufficient_events'; rows.append(result); continue
        f,phase,concentration=fit_mode(train,np.linspace(.1,4.,4096))
        score=score_mode(test,f,phase)
        null=[]
        for repeat in range(999):
            tt=np.concatenate([rng.choice(t[chunks[i]],len(event_times[i]),replace=False) for i in range(split,len(chunks))])
            null.append(score_mode(tt,f,phase))
        p=(1+np.sum(np.asarray(null)>=score))/1000
        result.update({'frequency_hz':f,'phase_rad':phase,'train_concentration':concentration,
                       'heldout_phase_score':score,'p_raw':float(p),'p_bonferroni':float(min(1,4*p)),
                       'status':'candidate_supported' if p*4<.05 and score>0 else 'not_supported'})
        np.savez_compressed(out/(row['name']+'.npz'),train_times=train,test_times=test,null_scores=null)
        rows.append(result)
    data={'protocol_sha256':hashlib.sha256((ROOT/'MODE_PROTOCOL.md').read_bytes()).hexdigest(),
          'flash_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runs':rows}
    (out/'summary.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    lines=[]
    for r in rows:
        if 'frequency_hz' in r:
            with np.load(out/(r['name']+'.npz')) as z:
                assert abs(score_mode(z['test_times'],r['frequency_hz'],r['phase_rad'])-r['heldout_phase_score'])<1e-12
            lines.append(f"| {r['name']} | {r['train_events']}/{r['test_events']} | {r['frequency_hz']:.4f} | {r['heldout_phase_score']:.3f} | {r['p_bonferroni']:.3f} | {r['status']} |")
        else: lines.append(f"| {r['name']} | {r['train_events']}/{r['test_events']} | — | — | — | za mało zdarzeń |")
    text='''# Hipoteza modu: przeniesienie fazy błysków

Rozpatrujemy strukturę jako kandydata na mod, a zdarzenia M/S jako jego możliwe przejawy. Częstość i fazę ustalono na pierwszych ciągłych fragmentach; ocenę wykonano na późniejszych bez ponownego dopasowania. Czasy jednoczesnych błysków z różnych binów policzono tylko raz.

| Ślad | Zdarzenia train/test | Kandydat Hz | Zgodność fazy test | p po korekcie | Ocena |
|---|---:|---:|---:|---:|---|
'''+ '\n'.join(lines)+'''

Zgodność fazy to średni cosinus względem fazy ustalonej wcześniej: +1 oznacza pełną zgodność, 0 brak skupienia w oczekiwanej fazie, -1 przeciwfazę. Kontrola: 999 losowań zdarzeń po rzeczywiście dostępnych klatkach, z zachowaniem liczby zdarzeń w każdym fragmencie i wszystkich luk. Poprawka Bonferroniego dla 4 śladów. Kryterium kandydata: dodatnia zgodność i p<.05 po korekcie. Częstość jest hipotezą dobraną do treningu, nie zmierzonym RPM.

To eksploracyjny test stałej częstości, po wcześniejszym oglądaniu danych. Zdarzenia mogą pochodzić od różnych źródeł; model nie rozdziela ich fizycznie. Niepowodzenie nie wyklucza modu o zmiennej częstości ani innych pasm. Mała liczba zdarzeń ogranicza moc. Sukces też nie utożsamiałby automatycznie M/S z K ani nie dowodził łopat — wymagałby osobnego potwierdzenia fizycznego.

Źródło: Open Radar Initiative, Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, dane CC BY-NC 4.0. Analiza używa zapisanych kandydatów z flash_results, nie zmienia detektora. Protokół: MODE_PROTOCOL.md. Wyniki i losowe kontrole: mode_results. Uruchomienie: `python -m unittest clock_experiment.test_event_mode -v`, `python -m clock_experiment.run_event_mode`.
'''
    (ROOT/'MODE_WYNIK.md').write_text(text,encoding='utf-8')
    print(json.dumps(rows,indent=2))

if __name__=='__main__': main()
