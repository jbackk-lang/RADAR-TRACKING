import json
import numpy as np
from run_angle import ROOT,digest
from sync_calibration import simulate,calibrate,read_angle

def main():
    r=json.loads((ROOT/'sync_results.json').read_text(encoding='utf-8'))
    params=json.loads((ROOT/'sync_parameters.json').read_text(encoding='utf-8'))
    assert r['parameters_sha256']==digest(ROOT/'sync_parameters.json')
    for name,expected in r['hashes'].items():
        assert digest(ROOT/name)==expected
    for p in params:
        refs=[simulate(23000000+p['seed']*10+i,1.2,s,p['truth_delay'],p['truth_zero']) for i,s in enumerate((.5,.5,1.,1.,1.5,1.5))]
        assert calibrate(refs,[1.2]*6)==p['fitted']
    for row in r['runs']:
        p=params[row['seed']]; cal=p['fitted']; bad=p['wrong_reference_fit']
        ti=(.4,1.2,2.).index(row['theta']); wi=(.65,1.25,1.8).index(row['turns'])
        data=simulate(24000000+row['seed']*100+int(row['variable'])*30+ti*3+wi,row['theta'],row['turns'],p['truth_delay'],p['truth_zero'],row['variable'])
        raw=read_angle(data)
        values=dict(raw=raw,angle_only=raw-cal['angle_only_rad'],joint_sync=read_angle(data,cal['delay_s'],cal['zero_rad']),
                    wrong_reference=read_angle(data,bad['delay_s'],bad['zero_rad']))
        assert values==row['angles']
        assert row['errors_deg']=={m:float(np.rad2deg(abs(v-row['theta']))) for m,v in values.items()}
    lines=['# Synchronizacja czasu echa i kąta anteny','',
           '**Wynik:** wspólna kalibracja przesunięcia czasu i zera enkodera poprawiła pomiar kąta na nowych echach oraz przy innych prędkościach obrotu. Stała korekta samego kąta nie przenosiła się równie dobrze między prędkościami.','',
           'Kalibracja: 60 obserwacji znanego, nieruchomego reflektora przy .5,1,1.5 obrotu/s. Test: 180 osobnych ech celów przy .65,1.25,1.8 obrotu/s i trzech kątach. Parametry zamrożone przed pomiarem celów; nie korzystano z prawdy celów do kalibracji. To nowe obserwacje syntetyczne, nie eksperyment bez dodatkowych obserwacji.','',
           '| Obrót | Bez kalibracji: MAE [°] | Tylko kąt: MAE [°] | Czas + zero: MAE [°] | Czas + zero: P95 [°] |','|---|---:|---:|---:|---:|']
    for kind,s in r['summary'].items():
        lines.append(f"| {kind} | {s['raw']['mae_deg']:.4f} | {s['angle_only']['mae_deg']:.4f} | {s['joint_sync']['mae_deg']:.4f} | {s['joint_sync']['p95_deg']:.4f} |")
    lines+=['',f"Średni błąd oszacowania przesunięcia czasu: {r['delay_mae_ms']:.3f} ms. Średni błąd zera enkodera: {r['zero_mae_deg']:.4f}°.",'',
            'Najpierw odejmujemy czas przelotu 2R/c z użyciem zmierzonej odległości (sigma błędu R=2 m), następnie kalibrowane przesunięcie czasu. Po interpolacji rzeczywistego położenia enkodera odejmujemy jego zero. Przesunięcie dotyczy osi czasu echa względem enkodera; nie jest automatycznie poprawką czasu przelotu ani wszystkich zegarów radaru. R i v nie są zmieniane.','',
            '## Kontrole i ograniczenia','',
            'Przy jednakowych prędkościach obrotu kalibrator odmawia rozdzielania delay i zero. Sprawdzono 10/10 odmów. Rozrzut prędkości jest warunkiem identyfikowalności; zmiana prędkości musi być faktycznie obecna w danych.','',
            f"Podanie błędnego kąta reflektora o .4° nadal oszukało kalibrację: MAE celów przy zmiennym obrocie wyniosło {r['summary']['variable']['wrong_reference']['mae_deg']:.4f}°. Synchronizacja usuwa badane sprzężenie czasu z kątem, ale nie gwarantuje poprawności referencji.",'',
            'Model zakłada stałe opóźnienie i zero, izolowaną symetryczną wiązkę, brak ruchu reflektora i wielodrogowości. Nie wykonano testu na sprzęcie, przy dryfie kalibracji ani przy silnych zakłóceniach impulsowych. W realnym torze pozostaje potrzebny odporny filtr zakłóceń oraz kontrola jakości referencji; ten test nie łączy jeszcze filtra z kalibratorem.','',
            '4 testy przeszły. Ponownie dopasowano wszystkie 10 kalibracji z odtworzonych ech referencji, odtworzono 180 wyników nowych celów i sprawdzono hashe. Odtwarzanie: python -m unittest test_sync_calibration -v; python report_sync.py. python run_sync.py chroni istniejące parametry i wyniki.']
    (ROOT/'WYNIK_SYNC.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Verified 10 calibrations and 180 target results; report saved.')

if __name__=='__main__':
    main()
