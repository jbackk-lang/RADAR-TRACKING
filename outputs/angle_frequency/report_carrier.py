import json
import numpy as np
from run_angle import ROOT,digest
from carrier_phase import CASES,TIMES,simulate,estimate

def main():
    r=json.loads((ROOT/'carrier_results.json').read_text(encoding='utf-8'))
    assert digest(ROOT/'carrier_phasors.npz')==r['phasors_sha256']
    for name,value in r['hashes'].items():
        assert digest(ROOT/name)==value
    with np.load(ROOT/'carrier_phasors.npz',allow_pickle=False) as stored:
        for row in r['runs']:
            iq,truth=simulate(row['input_seed'],row['case'])
            out,p=estimate(iq)
            assert truth==row['truth_v'] and out==row['estimates']
            np.testing.assert_array_equal(p,stored[row['phasor_key']])
    for case,s in r['summary'].items():
        rows=[row for row in r['runs'] if row['case']==case]
        for method in ('baseline','carrier'):
            assert s[method+'_v_mae']==float(np.mean([abs(row['estimates'][method+'_v']-row['truth_v']) for row in rows]))
    lines=['# Faza nośnej: dokładniejsza estymacja v i zmiany R','',
           '**Wynik:** spójne dopasowanie fazy po 64 impulsach poprawiło estymację v dla izolowanego echa, także słabego. Nie rozdzieliło słabego celu od dominującego echa i nie usunęło dryfu fazy instrumentu. Bezwzględne R pozostało odczytem z obwiedni.','',
           '120 burstów, 20 ziaren na warunek. Nowy generator uwzględnia fazę propagacji 4πR(t)/lambda i nieznaną stałą fazę rozpraszania. Obie metody mają identyczne I/Q. Bazowa metoda używa różnicy faz kolejnych impulsów w jednym binie. Nowa łączy 7 sąsiednich próbek obwiedni i dopasowuje Doppler spójnie w całym burście. Zysk pochodzi z estymatora i wykorzystania próbek; nie dowodzi nowego efektu fizycznego samej nośnej.','',
           '| Warunki | Bazowy MAE v [m/s] | Spójny MAE v [m/s] | Bazowy MAE deltaR [mm] | Spójny MAE deltaR [mm] |','|---|---:|---:|---:|---:|']
    for case,s in r['summary'].items():
        lines.append(f"| {case} | {s['baseline_v_mae']:.6f} | {s['carrier_v_mae']:.6f} | {s['baseline_delta_mae_mm']:.4f} | {s['carrier_delta_mae_mm']:.4f} |")
    lines+=['','single_slow: v=.04 m/s; single_fast: v=1 m/s; weak_isolated: amplituda .2, v=.04; weak_overlap: ten sam słaby oraz silny nieruchomy cel o R większym o 1 m; weak_overlap_separated_doppler: słaby v=1 i silny v=0; instrument_drift: target v=.04 plus nieskorygowany instrumentalny dryf fazy odpowiadający .02 m/s.','',
            'Ważne: deltaR = v_est × 7.875 ms przy założeniu stałej prędkości. Jej błąd jest przeskalowanym błędem v, nie drugą niezależną poprawą ani pomiarem bezwzględnego R. Nieznana faza rozpraszania i niejednoznaczność fazy uniemożliwiają bezpośrednie zastąpienie odczytu R milimetrowym wynikiem.','',
            'Dla izolowanych ech o amplitudzie 1 błąd bezwzględnego R z maksimum obwiedni pozostaje około .830 m. Dla słabego izolowanego echa wyniósł 2.163 m. Nie dodano poprawki R.','',
            'Nakładające się silne echo dominuje w wybranym maksimum Dopplera: nowy estymator nie ma detektora drugiego maksimum i nie rozwiązuje asocjacji składowych. Nawet różne Dopplery nie pomagają, jeśli algorytm raportuje wyłącznie najsilniejszą składową. Dryf instrumentu jest nierozróżnialny od ruchu bez niezależnej kalibracji; fazowe przetwarzanie go nie usuwa.','',
            'Zysk dla isolated_slow wynosi około 90%, dla isolated_fast 84%, a weak_isolated 97% względem bazowego estymatora w tych danych. Nie dotyczy wszystkich warunków. Brak wielodrogowości, przyspieszania wewnątrz burstu, zmiennej fazy rozpraszania i walidacji realnej. Wyższa efektywność estymacji nie zwiększa fizycznej rozdzielczości pasma ani czasu obserwacji.','',
            '3 testy przeszły. Odtworzono wszystkie 120 pełnych burstów I/Q z generatora, estymaty i zapisane fazory; sprawdzono hashe i MAE v. Odtwarzanie: python -m unittest test_carrier_phase -v; python report_carrier.py. python run_carrier.py chroni istniejące wyniki. Pełne I/Q odtwarza się z zapisanych ziaren; zapisano jedynie wydobyte fazory. Główny tracker i stary generator pozostają bez zmian.']
    (ROOT/'WYNIK_CARRIER.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Verified 120 regenerated I/Q bursts and estimates; report saved.')

if __name__=='__main__':
    main()
