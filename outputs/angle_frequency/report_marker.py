import json
import numpy as np
from run_angle import ROOT,digest
from marker_sync import estimate_delay,calibrate_zero
from sync_calibration import simulate,read_angle

def main():
    r=json.loads((ROOT/'marker_results.json').read_text(encoding='utf-8'))
    params=json.loads((ROOT/'marker_parameters.json').read_text(encoding='utf-8'))
    assert digest(ROOT/'marker_parameters.json')==r['parameters_sha256']
    for name,expected in r['hashes'].items():
        assert digest(ROOT/name)==expected
    for p in params:
        delay=estimate_delay(p['echo_marks'],p['encoder_marks'])
        refs=[simulate(28000000+p['seed']*10+i,1.2,1.,p['truth_delay'],np.deg2rad(.12)) for i in range(6)]
        assert calibrate_zero(refs,[1.2]*6,delay)==p['calibration']
    for row in r['runs']:
        delay=estimate_delay(row['echo_marks'],row['encoder_marks'])
        assert delay==row['delay_s']
        ci=('constant','variable','clock_change').index(row['condition']); ti=(.4,1.2,2.).index(row['theta'])
        cal=params[row['seed']]['calibration']
        data=simulate(29000000+row['seed']*100+ci*10+ti,row['theta'],1.,row['truth_delay'],np.deg2rad(.12),row['condition']!='constant')
        raw=read_angle(data)
        values=dict(raw=raw,angle_only=raw-cal['angle_only_rad'],marker_frozen=read_angle(data,cal['delay_s'],cal['zero_rad']),
                    marker_current=read_angle(data,delay,cal['zero_rad']))
        assert values==row['angles']
        assert row['errors_deg']=={m:float(np.rad2deg(abs(v-row['theta']))) for m,v in values.items()}
    lines=['# Jedna prędkość: czas ze znacznika, zero z reflektora','',
           '**Wynik:** niezależne znaczniki rozdzielają przesunięcie zegarów i zero enkodera bez zmiany nominalnej prędkości obrotu. Przy stabilnym czasie sama poprawka kąta jest równie dobra; przewaga aktualizowanych znaczników pojawia się przy zmianie przesunięcia zegara.','',
           'Kalibracja przy jednej nominalnej prędkości 1 obr/s: 60 obserwacji reflektora, 10 ziaren. Ocena na 90 nowych echach celów. Każdy zestaw ma 8 niezależnych elektronicznych znaczników, z szumem odczytu 20 us na zegar. Nie są to nowe emisje radarowe, ale są dodatkową informacją instrumentalną.','',
           '| Warunki | Raw MAE [°] | Tylko kąt [°] | Zamrożony znacznik [°] | Bieżące znaczniki [°] |','|---|---:|---:|---:|---:|']
    for name,s in r['summary'].items():
        lines.append(f"| {name} | {s['raw']['mae_deg']:.4f} | {s['angle_only']['mae_deg']:.4f} | {s['marker_frozen']['mae_deg']:.4f} | {s['marker_current']['mae_deg']:.4f} |")
    lines+=['',f"Średni błąd estymacji opóźnienia ze znaczników: {r['marker_delay_mae_us']:.2f} us.",'',
            'constant: stały obrót i zegary; variable: chwilowa prędkość ±5% przy niezmienionej nominalnej prędkości; clock_change: taki sam obrót i zmiana przesunięcia czasu o ±.5 ms po kalibracji. Każdy skan dostaje nowe znaczniki; zero enkodera pozostaje zamrożone.','',
            'Przy tej samej stałej prędkości kalibracja jednego łącznego błędu kąta także działa, choć nie identyfikuje jego przyczyn. Znaczniki dostarczają brakującego niezależnego pomiaru czasu. Nie przypisujemy tej niejednoznaczności rezonansowi mechanicznemu ani nie twierdzimy, że znaczniki tłumią drgania.','',
            'Założenie sprzętowe: zdarzenie znacznika musi reprezentować właściwe punkty czasowe obu torów. Różnica opóźnień przewodów, rejestracji i przetwarzania echa wymaga osobnego pomiaru; sama zgodność zegarów jej nie gwarantuje. Nie wykonano pomiarów sprzętowych, testu wielodrogowości ani integracji z filtrem impulsów. Błędna geometria reflektora nadal może wprowadzić zły zero_bias. R/v bez zmian.','',
            '3 testy przeszły. Ponownie odtworzono 10 kalibracji z referencji, 90 wyników celów i wszystkie opóźnienia ze znaczników; sprawdzono hashe. python -m unittest test_marker_sync -v; python report_marker.py. python run_marker.py chroni istniejące parametry i wyniki.']
    (ROOT/'WYNIK_MARKER.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Verified 10 calibrations and 90 target/marker results; report saved.')

if __name__=='__main__':
    main()
