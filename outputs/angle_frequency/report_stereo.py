import json
import numpy as np
from run_angle import ROOT,digest
from stereo_model import JointEstimator

def main():
    r=json.loads((ROOT/'stereo_results.json').read_text(encoding='utf-8'))
    assert digest(ROOT/'stereo_iq.npz')==r['iq_sha256']
    for name,expected in r['hashes'].items():
        assert digest(ROOT/name)==expected
    models={n:JointEstimator(int(n)) for n in ('1','2')}
    with np.load(ROOT/'stereo_iq.npz',allow_pickle=False) as data:
        for row in r['runs']:
            for n,out in row['outcomes'].items():
                replay=models[n].fit(data[out['iq_key']])
                assert replay['count']==out['count']
                np.testing.assert_allclose(replay['angles'],out['angles'],atol=1e-12)
                if row['kind']=='pair' and out['count']==2:
                    e=np.rad2deg(abs(np.array(out['angles'])-row['truth']))
                    assert out['resolved']==bool(np.all(e<=.25))
                    assert np.isclose(out['matched_mae_deg'],e.mean())
    lines=['# Nakładanie I/Q i dwa kanały — wynik','',
           '**Wniosek:** wspólne dopasowanie zespolonych ech rozdziela większość badanych par. Drugi kanał przy rozstawie lambda/2 nie wykazał dodatkowej przewagi w tym małym eksperymencie. Nie wynika z tego, że stereoskopia jest nieskuteczna dla innych rozstawów i warunków.','',
           'Dwa cele w tej samej komórce R/v nakładano koherentnie, uwzględniając fazy 0, pi/2 i pi oraz różne amplitudy. Model dobiera jeden lub dwa cele przez BIC, dopasowując wspólnie kąty i zespolone amplitudy. 180 par i 20 pojedynczych celów. Łączna energia sygnału jest taka sama dla 1 i 2 kanałów; dwa kanały mają więcej próbek szumu.','',
           '| Wariant | Poprawnie rozdzielone pary / 180 | Fałszywie rozdzielone pojedyncze / 20 | MAE przy wyborze dwóch [°] |','|---|---:|---:|---:|']
    for n,s in r['summary'].items():
        a=s['all_pairs']
        pairs=[row for row in r['runs'] if row['kind']=='pair']
        assert a['resolved']==sum(row['outcomes'][n]['resolved'] for row in pairs)
        lines.append(f"| {n} kanał(y) | {a['resolved']} | {s['false_split_single']} | {a['mae_when_two_selected_deg']:.4f} |")
    lines+=['','Poprawne rozdzielenie oznacza wybór dwóch celów i błąd każdego kąta <=.25°. MAE w tabeli jest warunkowe: pomija przypadki, w których wybrano jeden cel. Nie przedstawia całkowitego kosztu nieudanych rozdzieleń.','',
            '| Separacja | 1 kanał: poprawne / 60 | 2 kanały: poprawne / 60 |','|---|---:|---:|']
    for separation in ('0.75','1.5','3.0'):
        lines.append(f"| {separation}° | {r['summary']['1']['by_separation'][separation]['resolved']} | {r['summary']['2']['by_separation'][separation]['resolved']} |")
    lines+=['','| Amplituda drugiego / pierwszego | 1 kanał: poprawne / 45 | 2 kanały: poprawne / 45 |','|---|---:|---:|']
    for ratio in ('0.25','0.5','1.0','2.0'):
        lines.append(f"| {ratio} | {r['summary']['1']['by_ratio'][ratio]['resolved']} | {r['summary']['2']['by_ratio'][ratio]['resolved']} |")
    lines+=['',f"Sparowane przypadki: tylko dwa kanały poprawne — {r['comparison']['only_two_rx_resolved']}; tylko jeden kanał poprawny — {r['comparison']['only_one_rx_resolved']}. Próba jest mała; nie ogłaszamy przewagi żadnej liczby kanałów.",'',
            'Przy rozstawie lambda/2 i kącie około 1.2 rad różnica faz między kierunkami oddalonymi o .75° wynosi około .015 rad. To niewielka dodatkowa informacja przy badanym szumie .05 na składową. Jest to interpretacja geometryczna wynikająca z modelu; nie odrębny dowód przyczyny wyniku. Większy rozstaw może zwiększyć czułość, ale wprowadza niejednoznaczności fazy, których ten test nie bada.','',
            'Ograniczenia: dopasowanie zna idealny model wiązki i fazy, kanały są idealnie skalibrowane i zsynchronizowane, cele nieruchome, bez wielodrogowości. Obserwujemy cały skan ±6°, nie pojedynczą próbkę. Badane kąty ograniczono do ±5° wokół kierunku 1.2 rad. R/v nie zmieniano ani nie testowano ponownie.','',
            '4 testy przeszły. Odtworzono 400 dopasowań z zapisanych surowych I/Q (200 scen × 2 warianty); sprawdzono metryki poprawnego rozdzielenia i hashe.','',
            'Odtwarzanie: python -m unittest test_stereo_model -v oraz python report_stereo.py. python run_stereo.py chroni istniejące wyniki; do ponownego przebiegu użyj świeżej kopii bez stereo_results.json i stereo_iq.npz.']
    (ROOT/'WYNIK_STEREO.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Verified 400 fits from stored I/Q; report saved.')

if __name__=='__main__':
    main()
