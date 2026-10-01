import json
import hashlib
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'soft_results'
    r=json.loads((out/'summary.json').read_text())
    old=json.loads((ROOT/'adaptive_results/summary.json').read_text())
    assert hashlib.sha256((ROOT/'SOFT_PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256']
    for name,h in r['code_sha256'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    for p in r['inputs']: assert hashlib.sha256((ROOT/'adaptive_results'/p['name']).read_bytes()).hexdigest()==p['sha256']
    for row in r['runs']:
        with np.load(out/f"{row['case']}_{row['seed']}_{row['mode']}.npz") as z:
            assert len(z['predicted'])==480
            assert abs(np.sqrt(np.mean((z['predicted']-z['truth'])**2))-row['rmse_m'])<1e-12
            assert np.all((z['weight']>=.02)&(z['weight']<=1))
    table=[]; summary={}
    for case in ('clean','correlated','amplitude_only','position_only'):
        values={m:float(np.mean([x['rmse_m'] for x in r['runs'] if x['case']==case and x['mode']==m])) for m in ('geometry','hybrid')}
        values['standard']=old['summary'][case]['standard']['rmse_m']
        values['hard_gate']=old['summary'][case]['adaptive']['rmse_m']
        summary[case]=values
        table.append(f"| {case} | {values['standard']:.5f} | {values['hard_gate']:.5f} | {values['geometry']:.5f} | {values['hybrid']:.5f} |")
    text='''# Miękkie ważenie amplitudy i geometrii

**Pilotaż syntetyczny, 16 nowych przebiegów; średnie z 2 ziaren.** Sprawdzono te same cztery scenariusze, bez dobierania parametrów po wyniku. Standard i twarde sito są wynikami poprzedniego przebiegu na identycznych danych. Użyto wcześniejszych decyzji zegara: to samo wejście czasu/amplitudy, zweryfikowane hashe; nie powtarzano kosztownego dopasowania.

| Scenariusz | Standard RMSE [m] | Dawne twarde sito [m] | Sama geometria [m] | Geometria + amplituda [m] |
|---|---:|---:|---:|---:|
'''+ '\n'.join(table)+'''

`clean`: brak dodatkowych zakłóceń; `correlated`: wspólny błąd pozycji i amplitudy; `amplitude_only`: błąd tylko amplitudy; `position_only`: błąd tylko pozycji.

## Wniosek z tego przebiegu

Przy wspólnym zakłóceniu hybryda osiąga 14,44 cm RMSE wobec 18,92 cm samej geometrii, ale twarde sito z poprzedniego testu było lepsze (3,29 cm). Przy błędzie samej amplitudy miękka hybryda zachowuje dokładność standardu (1,45 cm), zamiast pogarszać ją do 3,29 cm. Przy błędzie samej pozycji zegar niczego nie dodaje do geometrii. Nie ma jednego zwycięzcy we wszystkich warunkach; ten wariant pozostaje eksperymentalny, nie zastępuje domyślnie trackera ani poprzedniego sita.

## Reguła

Pomiar zgodny z predykcją do 0,12 m zachowuje pełną wagę bez względu na amplitudę. Powyżej progu geometria daje wagę 0,12/dystans. Hybryda dodatkowo podnosi wagę do kwadratu przy ostrzeżeniu amplitudowym. Waga nie spada poniżej 0,02. Żadna klatka nie znika z oceny. Punkt łączący predykcję i pomiar jest estymatą, nie surową obserwacją.

## Ograniczenia

Ręczny próg odpowiada skali tego syntetycznego testu; nie został zweryfikowany dla innych sensorów. Test nie obejmuje prawdziwych manewrów, błędnej asocjacji ani rzeczywistego radaru. Stały ruch i zgodna z zegarem modulacja są ułatwieniem dla modelu. Ten sam błąd amplitudy może mieć inne znaczenie w realnym pomiarze. Wynik nie dowodzi uniwersalnej przewagi zegara nad geometrią. Nowe czasy w JSON wykluczają dopasowanie zegara; dawny koszt zegara podano osobno, więc nie deklarujemy tu przyspieszenia pełnej hybrydy.

Kod: `soft_fusion.py`. Uruchomienie z repo: `python -m clock_experiment.run_soft_fusion`, potem `python -m clock_experiment.report_soft`. Benchmark nie nadpisuje istniejącego podsumowania. Protokół: `SOFT_PROTOCOL.md`. Wszystkie predykcje i wejściowe hashe: `soft_results/`.

Weryfikacja: 11 testów jednostkowych integracji/przełączania/fuzji przeszło; ponownie przeliczono RMSE wszystkich 16 przebiegów i sprawdzono granice wag oraz hashe. Nie jest to ponowne uruchomienie całego historycznego zestawu testów repo.
'''
    (ROOT/'SOFT_WYNIK.md').write_text(text,encoding='utf-8')
    (out/'verification.json').write_text(json.dumps({'runs_verified':16,'hashes_verified':True,'summary':summary},indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
