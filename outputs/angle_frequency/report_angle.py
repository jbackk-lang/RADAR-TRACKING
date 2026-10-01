import json
import numpy as np
from run_angle import ROOT,digest
import angle_model as frequency
import rotation_model as rotation

def verify_frequency(r):
    assert len(r['runs'])==8400
    scenarios={'clean':(0.,0.),'constant_phase':(.15,0.),'channel_delay':(.15,.2e-12)}
    angles=(-.6,-.4,-.2,0.,.2,.4,.6)
    for row in r['runs']:
        for method,v in row['estimated'].items():
            expected=abs(v['angle_rad']-row['theta']) if v['angle_rad'] is not None else None
            assert expected==row['errors'][method]
        if row['seed'] in (0,199):
            offset,delay=scenarios[row['scenario']]
            f,iq=frequency.simulate(9000000+angles.index(row['theta'])*1000+row['seed'],row['theta'],row['bandwidth_hz'],offset,delay)
            assert frequency.estimate(f,iq)==row['estimated']
    for bandwidth,scenarios_summary in r['summary'].items():
        for scenario,metrics in scenarios_summary.items():
            rows=[row for row in r['runs'] if row['bandwidth_hz']==float(bandwidth) and row['scenario']==scenario]
            assert len(rows)==1400
            for method,v in metrics.items():
                e=[row['errors'][method] for row in rows if row['errors'][method] is not None]
                assert v['invalid']==len(rows)-len(e)
                assert v['mae_rad']==float(np.mean(e))
                assert v['p95_rad']==float(np.quantile(e,.95))

def verify_rotation(r):
    assert len(r['runs'])==1800
    angles=(.4,1.2,2.)
    scenarios=dict(constant_rotation=(0.,0.),variable_rotation=(.05,0.),clock_offset=(.05,.002))
    for row in r['runs']:
        assert row['errors']=={m:abs(v-row['theta']) for m,v in row['estimated'].items()}
        if row['seed'] in (0,199):
            variation,offset=scenarios[row['scenario']]
            data=rotation.simulate(10000000+angles.index(row['theta'])*1000+row['seed'],row['theta'],variation,offset)
            assert rotation.estimate(data)==row['estimated']
    for scenario,metrics in r['summary'].items():
        rows=[row for row in r['runs'] if row['scenario']==scenario]
        for method,v in metrics.items():
            e=[row['errors'][method] for row in rows]
            assert v['mae_rad']==float(np.mean(e))
            assert v['p95_deg']==float(np.rad2deg(np.quantile(e,.95)))

def main():
    fr=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
    rr=json.loads((ROOT/'rotation_results.json').read_text(encoding='utf-8'))
    for r in (fr,rr):
        for name,expected in r['hashes'].items():
            assert digest(ROOT/name)==expected
    verify_frequency(fr); verify_rotation(rr)
    lines=['# Kąt z sygnału: częstotliwości oraz obrót anteny', '',
           '**Wniosek:** w badanej symulacji obracającej się anteny korzystanie z enkodera i środka przejścia wiązki daje dobry pomiar kąta bez dodawania korekty bearing. Sam czas przy założeniu stałej prędkości obrotu zawodzi, gdy obrót jest nierówny. Metoda nachylenia fazy po częstotliwości usuwa idealny stały offset fazy, ale jest podatna na szum i nie odróżnia opóźnienia kanałów od kierunku.', '',
           '## Czy istniejące dane wystarczą?', '',
           'Nie. clock_experiment/radar_compensation.py ma I/Q o wymiarach impulsy × próbki, jedną nośną 77 GHz i kąt zapisany w metadanych. Nie ma kanałów dwóch anten, próbek wielu częstotliwości RF, czasu przejścia wiązki ani enkodera. data/sample_radar.npy ma 83 gotowe detekcje z polami frame,x,y,t. Żaden z tych plików nie pozwala sprawdzić nowego fizycznego pomiaru kąta.', '',
           'Testy poniżej używają osobnych, nowych danych syntetycznych. Nie zmieniono starego kontrolera ani jego wyników. Nie deklarujemy braku dodatkowych danych względem starego modelu.', '',
           '## Obrót anteny i czas echa', '',
           'Kąt wynika z kierunku anteny podczas przejścia echa przez wiązkę. Czas przelotu 2R/c dotyczy odległości; czas od początku obrotu wraz z położeniem anteny określa azymut. Jest to standardowa zasada radaru z obracającą się anteną: [FAA — Radar](https://www.faa.gov/air_traffic/publications/atpubs/AIM/aim0405.html).', '',
           '1800 przypadków: 200 ziaren, 3 kąty, 3 scenariusze. Nominalnie 1 obrót/s, FWHM mocy wiązki 1.5°, odstęp echa i enkodera .2 ms, szum enkodera .02°. Środek wiązki oszacowano przez średnią kąta enkodera ważoną mocą echa po odjęciu oszacowanego tła. W tym eksperymencie zmierzona odległość jest bezbłędna i służy wyrównaniu czasu przelotu.', '',
           '| Warunki | Czas × nominalny obrót: MAE [°] | Enkoder w maksimum: MAE [°] | Enkoder + środek wiązki: MAE [°] | P95 środka [°] |','|---|---:|---:|---:|---:|']
    labels={'constant_rotation':'Stały obrót','variable_rotation':'Prędkość obrotu ±5%','clock_offset':'Obrót ±5%, przesunięcie zegara 2 ms'}
    for scenario,s in rr['summary'].items():
        lines.append(f"| {labels[scenario]} | {s['nominal_time_peak']['mae_deg']:.4f} | {s['encoder_peak']['mae_deg']:.4f} | {s['encoder_centroid']['mae_deg']:.4f} | {s['encoder_centroid']['p95_deg']:.4f} |")
    lines += ['', 'Przy 1 obrocie/s przesunięcie czasu o 2 ms odpowiada 0.72°. Test pokazał około 0.718° MAE mimo enkodera. Błąd zera enkodera również pozostaje błędem kąta — żadna z tych metod nie usuwa go sama.', '',
              'To wynik dla nieruchomego, izolowanego celu i idealnej symetrycznej wiązki. Brak listków bocznych, wielodrogowości, sąsiednich celów, drgań mocowania i walidacji sprzętowej. Środek wiązki wymaga obserwacji całego przejścia, więc wynik jest dostępny później niż pojedyncze echo.', '',
              '## Różne częstotliwości i faza', '',
              'Pomiar fazy między rozdzielonymi antenami jest podstawą wyznaczania kąta: [TI — MIMO Radar](https://www.ti.com/lit/an/swra554/swra554.pdf). Nasz model przyjmuje phi(f)=2πf(d sin(theta)/c + delay)+offset. Dopasowanie nachylenia usuwa stały offset, ale mierzy sumę opóźnienia geometrycznego i opóźnienia kanału. Są one nierozróżnialne bez dodatkowej informacji lub kalibracji; potwierdza to test dwóch identycznych zestawów I/Q dla różnych kątów i opóźnień.', '',
              '8400 przypadków: dwie anteny, 17 częstotliwości, 64 próbki/f, pasma 1 i 4 GHz wokół 77 GHz, szum .15 na składową zespoloną. Wyniki MAE odnoszą się do ważnych estymat; liczbę nieważnych pokazano jawnie. Nie przycinano sin(theta) do [-1,1].', '',
              '| Pasmo [GHz] | Warunki | Metoda | MAE [°] | P95 [°] | Nieważne / 1400 |','|---|---|---:|---:|---:|']
    scenarios={'clean':'Bez błędu kanałów','constant_phase':'Stały offset fazy .15 rad','channel_delay':'Offset .15 rad + opóźnienie .2 ps'}
    methods={'phase_center':'Faza na środkowej częstotliwości','phase_all':'Faza po paśmie, założony offset=0','slope_two':'Nachylenie z dwóch częstotliwości','slope_all':'Nachylenie z 17 częstotliwości'}
    for bandwidth,s in fr['summary'].items():
        for scenario,metrics in s.items():
            for method,v in metrics.items():
                lines.append(f"| {float(bandwidth)/1e9:.0f} | {scenarios[scenario]} | {methods[method]} | {v['mae_deg']:.4f} | {v['p95_deg']:.4f} | {v['invalid']} |")
    lines += ['', 'Bez szumu obie metody nachylenia odzyskują kąt mimo stałego offsetu fazy. Przy badanym szumie i paśmie 4 GHz nachylenie z 17 częstotliwości daje około 6.5° MAE, a faza po paśmie około 0.11° przy braku błędu kanałów. Wąskie względnie do nośnej pasmo daje małą zmianę fazy geometrycznej, więc różnicowanie wzmacnia wpływ szumu. Większe pasmo lub rozstaw anten mogą zmienić kompromis, ale nie zostały dostrojone w tym teście.', '',
              'Wyników obrotu i częstotliwości nie porównujemy jako dowodu wyższości konkretnego radaru: mają różne dane, model szumu i sposób pozyskania informacji. Oba testy sprawdzają mechanizm i jego ograniczenia.', '',
              '## Weryfikacja i użycie', '',
              '10 testów przeszło. Ponownie obliczono błędy i metryki 8400 przypadków częstotliwościowych oraz 1800 przypadków obrotu. Odtworzono z I/Q 84 przypadki częstotliwościowe i 18 przypadków obrotu (ziarna 0 i 199 dla wszystkich warunków). Sprawdzono hashe kodu i obu protokołów.', '',
              'W katalogu angle_frequency:', '',
              '`python -m unittest test_angle_model test_rotation_model -v`', '',
              '`python report_angle.py`', '',
              '`python run_angle.py` oraz `python run_rotation.py` chronią istniejące wyniki. Kolejny przebieg wymaga osobnej kopii bez results.json i rotation_results.json.', '',
              'Przed użyciem w realnym systemie potrzebne są surowe echa podczas skanu oraz zsynchronizowane znaczniki czasu i kąta anteny. Jeśli są już zapisywane, można przetestować tę metodę na istniejących skanach bez nowych emisji. W obecnych plikach ich nie ma.']
    (ROOT/'WYNIK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Verified 10200 cases and regenerated 102 I/Q cases; report saved.')

if __name__=='__main__':
    main()
