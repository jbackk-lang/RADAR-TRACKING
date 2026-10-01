# Zegar w czterech pasmach rzeczywistego widma

Przetestowano 4 wcześniej wybrane rzeczywiste ślady i 16 pasm. Zegar był użyty w prognozie choć jednej próbki w **0/16 pasm**. Nie wybrano najlepszego pasma po wyniku: granice były stałe przed testem. To eksploracja na krótkich fragmentach, nie nowa niezależna walidacja.

## Porównanie uczciwe dla tego samego celu

NMSE zawsze dotyczy **całej amplitudy echa**. Prognozy amplitud czterech pasm złożono jako sqrt(sum(amplituda²)). Nie porównujemy błędów normalizowanych wariancją różnych pasm. Mniejsza liczba jest lepsza.

| Ślad | Próbki oceny | Całość: średnia 12 | Całość: monitor | Pasma: średnie 12 | Pasma: monitory | Aktywne zegary |
|---|---:|---:|---:|---:|---:|---:|
| real_person_track_013 | 100 | 0.3089 | 0.3089 | 0.3225 | 0.3225 | 0/4 |
| real_bicycle_track_014 | 20 | 0.9190 | 0.9190 | 0.8985 | 0.8985 | 0/4 |
| real_vehicle_track_025 | 60 | 1.0865 | 1.0865 | 1.0753 | 1.0753 | 0/4 |
| real_uav_track_157 | 100 | 0.4531 | 0.4531 | 0.4580 | 0.4580 | 0/4 |

Różnica między kolumnami „Pasma: średnie” i „Pasma: monitory” pokazuje wkład zegara. Różnica między „Całość: średnia” i „Pasma: średnie” pochodzi z podziału i nieliniowej rekonstrukcji — nie wolno przypisać jej zegarowi.

## Dane i ograniczenia

[Open Radar Initiative](https://github.com/openradarinitiative/open_radar_datasets), Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, CC BY-NC 4.0. Zespolone widma dostarczone przez autorów, nie surowe ADC. Cztery sąsiadujące pasma po 252 biny; dokładne granice Hz są w JSON. Amplituda pasma to pierwiastek jego sumy mocy. Zegar bada modulację pomiędzy klatkami, nie szybki obrót bezpośrednio z impulsów.

Rozruch 100 próbek, identyczne parametry co w poprzedniej próbie rzeczywistej. Brak przyszłych danych w prognozie. Próbki po odmowie zegara pozostają w ocenie jako prognoza średniej z przeszłości. Nagrania mają luki; ich czas nie jest ściskany. Brak niezależnych RPM, brak dowodu poprawy pozycji. Nie ustalono, że pasmo odpowiada korpusowi albo wirnikowi. Nie sprawdzono jeszcze wąskich pasm śledzących poruszający się grzbiet widma. Nie dostrajano tej próby po wyniku.

Kod: run_bands.py, report_bands.py; protokół: BANDS_PROTOCOL.md; wyniki: band_results. Odtwarzanie z repo: `python -m clock_experiment.run_bands`, potem `python -m clock_experiment.report_bands`. Benchmark chroni istniejące wyniki. Sześć testów rekonstrukcji i przyczynowości prognoz przeszło; ponownie obliczono wszystkie główne metryki i sprawdzono hashe danych.

**Wniosek: podział na te cztery pasma nie uruchomił wiarygodnego zegara. Nie wykazano korzyści zegara na tych danych. Nie oznacza to dowodu braku okresowości — podział, długość próbki lub model mogą być nieodpowiednie.**
