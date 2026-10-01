import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'band_results'; r=json.loads((out/'summary.json').read_text())
    assert hashlib.sha256((ROOT/'BANDS_PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256']
    lines=[]; active=0; bands=0
    for row in r['runs']:
        assert hashlib.sha256(Path(row['input_path']).read_bytes()).hexdigest()==row['input_sha256']
        with np.load(out/(row['name']+'.npz')) as z:
            denominator=max(float(np.var(z['observed'])),1e-12)
            for m,value in row['nmse'].items():
                assert np.isclose(np.mean((z[m]-z['observed'])**2)/denominator,value,rtol=1e-12)
        n=sum(b['clock_fraction']>0 for b in row['bands']); active+=n; bands+=len(row['bands'])
        s=row['nmse']
        lines.append(f"| {row['name']} | {row['scored_samples']} | {s['full_mean12']:.4f} | {s['full_clock']:.4f} | {s['bands_mean12']:.4f} | {s['bands_clock']:.4f} | {n}/4 |")
    text=f'''# Zegar w czterech pasmach rzeczywistego widma

Przetestowano {len(r['runs'])} wcześniej wybrane rzeczywiste ślady i {bands} pasm. Zegar był użyty w prognozie choć jednej próbki w **{active}/{bands} pasm**. Nie wybrano najlepszego pasma po wyniku: granice były stałe przed testem. To eksploracja na krótkich fragmentach, nie nowa niezależna walidacja.

## Porównanie uczciwe dla tego samego celu

NMSE zawsze dotyczy **całej amplitudy echa**. Prognozy amplitud czterech pasm złożono jako sqrt(sum(amplituda²)). Nie porównujemy błędów normalizowanych wariancją różnych pasm. Mniejsza liczba jest lepsza.

| Ślad | Próbki oceny | Całość: średnia 12 | Całość: monitor | Pasma: średnie 12 | Pasma: monitory | Aktywne zegary |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(lines)+'''

Różnica między kolumnami „Pasma: średnie” i „Pasma: monitory” pokazuje wkład zegara. Różnica między „Całość: średnia” i „Pasma: średnie” pochodzi z podziału i nieliniowej rekonstrukcji — nie wolno przypisać jej zegarowi.

## Dane i ograniczenia

[Open Radar Initiative](https://github.com/openradarinitiative/open_radar_datasets), Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, CC BY-NC 4.0. Zespolone widma dostarczone przez autorów, nie surowe ADC. Cztery sąsiadujące pasma po 252 biny; dokładne granice Hz są w JSON. Amplituda pasma to pierwiastek jego sumy mocy. Zegar bada modulację pomiędzy klatkami, nie szybki obrót bezpośrednio z impulsów.

Rozruch 100 próbek, identyczne parametry co w poprzedniej próbie rzeczywistej. Brak przyszłych danych w prognozie. Próbki po odmowie zegara pozostają w ocenie jako prognoza średniej z przeszłości. Nagrania mają luki; ich czas nie jest ściskany. Brak niezależnych RPM, brak dowodu poprawy pozycji. Nie ustalono, że pasmo odpowiada korpusowi albo wirnikowi. Nie sprawdzono jeszcze wąskich pasm śledzących poruszający się grzbiet widma. Nie dostrajano tej próby po wyniku.

Kod: run_bands.py, report_bands.py; protokół: BANDS_PROTOCOL.md; wyniki: band_results. Odtwarzanie z repo: `python -m clock_experiment.run_bands`, potem `python -m clock_experiment.report_bands`. Benchmark chroni istniejące wyniki. Sześć testów rekonstrukcji i przyczynowości prognoz przeszło; ponownie obliczono wszystkie główne metryki i sprawdzono hashe danych.
'''
    if active==0:
        text+='\n**Wniosek: podział na te cztery pasma nie uruchomił wiarygodnego zegara. Nie wykazano korzyści zegara na tych danych. Nie oznacza to dowodu braku okresowości — podział, długość próbki lub model mogą być nieodpowiednie.**\n'
    (ROOT/'BANDS_WYNIK.md').write_text(text,encoding='utf-8')
    (out/'verification.json').write_text(json.dumps({'tracks_verified':len(r['runs']),'active_bands':active,'metrics_and_inputs_verified':True},indent=2))
    print('\n'.join(lines)); print('Active bands:',active)

if __name__=='__main__': main()
