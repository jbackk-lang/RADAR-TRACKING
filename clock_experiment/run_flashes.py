import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .flashes import detect

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'flash_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    sources=json.loads((ROOT/'signal_results/summary.json').read_text())['runs']
    sources=[r for r in sources if r['source']=='Open Radar']
    fig,axes=plt.subplots(len(sources),1,figsize=(12,11),squeeze=False)
    rows=[]; rng=np.random.default_rng(20261001)
    for ax,source in zip(axes[:,0],sources):
        path=Path(source['input_path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==source['input_sha256']
        with np.load(path,allow_pickle=False) as z:
            p=np.abs(z['spec'].astype(complex))**2
            t=(z['ts']-z['ts'][0])/1000.; frames=z['frames']
            f=(np.arange(p.shape[1])-p.shape[1]//2)*float(z['prf'])/p.shape[1]
        events,ratio,skipped=detect(p,t,frames,f)
        chunks=np.split(np.arange(len(t)),np.flatnonzero(np.diff(frames)!=1)+1)
        null=[]
        for repeat in range(10):
            shuffled=p.copy()
            for ix in chunks:
                for j in range(p.shape[1]): shuffled[ix,j]=p[rng.permutation(ix),j]
            null.append(len(detect(shuffled,t,frames,f)[0]))
        intervals=[]
        for ci in range(len(chunks)):
            # Simultaneous components are one occurrence for intervals only.
            tt=sorted(set(e['time_s'] for e in events if e['chunk']==ci))
            intervals.extend(np.diff(tt).tolist())
        row={'name':source['name'],'source_path':str(path),'sha256':source['input_sha256'],
             'events':events,'count':len(events),'shuffled_counts':null,'skipped_frames':skipped,
             'within_chunk_intervals_s':intervals,'median_frame_interval_s':float(np.median(np.diff(t)[np.diff(frames)==1]))}
        rows.append(row)
        ax.set_facecolor('#dddddd')
        for ix in chunks:
            if len(ix)<2: continue
            ax.pcolormesh(t[ix],f/1000,10*np.log10(np.maximum(ratio[ix].T,1e-12)),
                          vmin=0,vmax=25,cmap='viridis',shading='nearest',rasterized=True)
        if events:
            ax.scatter([e['time_s'] for e in events],[e['doppler_hz']/1000 for e in events],
                       facecolors='none',edgecolors='red',s=35,linewidths=.8)
        ax.set_title(f"{source['name']}: {len(events)} candidates; shuffled counts {min(null)}–{max(null)}")
        ax.set_ylabel('Doppler (kHz)'); ax.set_xlabel('Elapsed time (s); grey = gaps')
        print(row['name'],row['count'],null,flush=True)
    fig.suptitle('Real radar: candidate flashes (red); colour = 0–25 dB above temporal median')
    fig.tight_layout(rect=(0,0,1,.97)); fig.savefig(out/'maps.png',dpi=150); plt.close(fig)
    result={'protocol_sha256':hashlib.sha256((ROOT/'FLASH_PROTOCOL.md').read_bytes()).hexdigest(),
             'runs':rows,'scope':'Offline flash candidates, no blade labels or RPM inference'}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    table='\n'.join(f"| {r['name']} | {r['count']} | {min(r['shuffled_counts'])}–{max(r['shuffled_counts'])} | {r['median_frame_interval_s']:.3f} |" for r in rows)
    report='''# Błyski bez zegara na rzeczywistym radarze

Wykrywamy krótkie, połączone obszary mocy co najmniej 10 dB ponad lokalnym tłem czasu i medianą widma klatki. Każdy kandydat ma >=3 piksele i trwa <=5 klatek. To detektor eksploracyjny offline: tło korzysta z całego fragmentu. Brak dopasowania zegara i prognozowania.

| Ślad | Kandydaci | Przetasowane kontrole: liczba | Mediana odstępu klatek [s] |
|---|---:|---:|---:|
'''+table+'''

![Mapy wszystkich czterech śladów](flash_results/maps.png)

Czerwone obwódki wskazują maksima kandydatów; kolor to nadwyżka mocy nad medianą czasową danego binu (0–25 dB). Szare pola oznaczają brak danych, nie ciszę radaru. Zapisane fragmenty są krótkie i rozdzielone dużymi lukami.

Przetasowanie czasu niezależnie w każdym binie służy kontroli lokalnej spójności. Nie jest fizycznym modelem szumu, a jego wyniki nie są prawdopodobieństwem fałszywego alarmu. Różna liczba zdarzeń nie dowodzi łopat ani obrotów. Parametr 10 dB jest przyjętą definicją, nie progiem skalibrowanym na etykietach.

Źródło: [Open Radar Initiative](https://github.com/openradarinitiative/open_radar_datasets), Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, CC BY-NC 4.0. To dostarczone przetworzone widma Dopplera. Rozdzielczość w czasie jest ograniczona odstępem klatek; krótkie błyski wewnątrz klatki mogą być nierozróżnialne. Nie ma niezależnych etykiet błysków ani RPM.

Szczegóły każdego zdarzenia (czas maksimum, zakres częstotliwości, długość, moc względem tła) i odstępy w obrębie ciągłych fragmentów: flash_results/summary.json. Nie łączymy odstępów przez luki, nie przeliczamy ich na RPM. Nie wybieramy najlepszego wyniku z czterech śladów.

Uruchomienie: `python -m unittest clock_experiment.test_flashes -v`; `python -m clock_experiment.run_flashes`. Wyniki chronione przed nadpisaniem. Protokół: FLASH_PROTOCOL.md; kod: flashes.py. Testy stałego pola, wstrzykniętego błysku i rozdzielenia luk powinny przejść przed badaniem realnym.
'''
    (ROOT/'FLASH_WYNIK.md').write_text(report,encoding='utf-8')

if __name__=='__main__': main()
