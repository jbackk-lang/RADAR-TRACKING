# TIMDR odporny na szum i odstęp czasu

Dodano `core/timdr_robust.py`: odporne dopasowanie liniowej lub kwadratowej trajektorii, uwzględnienie sigma pomiaru oraz skręt w rad/s i zmiana prędkości w m/s². Model manewru musi poprawić dopasowanie ponad karę złożoności i próg. Pojedynczy błąd pozycji ma ograniczony wpływ przez IRLS. Wynik pozostaje heurystyczny; confidence jest wskaźnikiem wsparcia modelu, nie skalibrowanym prawdopodobieństwem.

4800 nowych historii:6rodzin ruchu,4sposoby próbkowania,2poziomy szumu,po100ziaren. Tylko wcześniejsze punkty danego okna, ocena końca historii. Progi i parametry zapisano przed przebiegiem.

| Warunki | Fałszywy manewr: legacy | Fałszywy manewr: robust | Wykryte manewry: legacy | Wykryte manewry: robust |
|---|---:|---:|---:|---:|
| Sigma .12m | 35.75% | 0% | 26.00% | 100% |
| Sigma .6m | 53.625% | 3.00% | 49.375% | 100% |

Fałszywy manewr oznacza stały ruch lub stały ruch z jednym błędnym punktem (równe udziały), nie częstość wszystkich alarmów prawdziwego radaru. Wykrywanie obejmuje dość wyraźny skręt, przyspieszenie, skręt90stopni i zawracanie. Kryterium alarmu TIMDR>.5, bez strojenia po wynikach. Nowa kombinacja składowych ma inną skalę niż średnia legacy; porównanie dotyczy tych dwóch kompletnych wariantów przy ustalonym punkcie działania, nie osobnych składowych ani pełnej charakterystyki ROC.

Mediana rozrzutu wyniku między próbkowaniami dla bezszumowych manewrów:legacy .315,robust0. Nowy wynik w tych manewrach nasycał się, co także zmniejsza rozrzut; nie dowodzi to dokładnego oszacowania każdej szybkości skrętu. Parametry używają fizycznego czasu, lecz różna liczba próbek nadal wpływa na statystyczną moc wyboru modelu.

Zapisane kryterium operatora spełnione. Założono właściwą sigma; zaniżenie jej lub niestandardowe zakłócenia mogą ponownie wywoływać fałszywe manewry. Minimum5punktów:wcześniej model zgłasza `insufficient` i score0. Wynik0 nie jest dowodem braku manewru. Stała prędkość otrzymuje model liniowy; składowa R liczy tylko dodatnią zgodność zmian ponad wybrany model.

Dotychczasowy operator i domyślne zachowanie `RadarTracker()` zachowane. Nowy wariant dostępny przez `RadarTracker(timdr_variant='robust', position_sigma=...)`; sigma w metrach na składową położenia powinna odpowiadać punktom faktycznie przekazywanym operatorowi, również po grupowaniu. `use_timdr=False` nadal wyłącza adaptację.

## Kontrola zastosowania w trackerze

100sekwencji demo,po25dla4scen,4obiekty i40klatek. Identyczne detekcje i pozostałe ustawienia. Legacy i robust:MAE dopasowanych pozycji0.204759m,braki0%,zmianyID0,4identyfikatory na sekwencję. Kryterium niepogorszenia spełnione. Różnica operatora nie przełożyła się tutaj na poprawę śledzenia; sceny były wystarczająco łatwe dla obu. Porównanie nie obejmuje bardzo bliskich obiektów, zaników i błędnych dopasowań. Wyniki robust_tracker_results.json, odtworzenie `python outputs/angle_frequency/check_robust_tracker.py`.

Po obu testach zastosowano wariant jako opcję „TIMDR odporny” w demo przeglądarkowym. Pozostałe opcje:CV i dotychczasowy TIMDR. Demo ustawia sigma.18m zgodnie z generatorem pojedynczych detekcji; grupowane centroidy mają inną niepewność, więc jest to ostrożne uproszczenie, nie kalibracja sprzętu. Dwupunktowy `core.scene_model` nadal używa pierwotnego operatora; nie przenosimy wyników trackera automatycznie na semantyczną interpretację sceny.

Sześć nowych testów przeszło, w tym pojedynczy błąd, próbkowanie, przyspieszenie, zawracanie i walidacja danych.55dostępnych funkcji testowych repo przeszło; wcześniejszy moduł real-data pozostaje niedostępny przez brak data/validate_on_real_trips.py. Nie instalowano pytest; funkcje wykonano bezpośrednio.

To radarowa, praktyczna adaptacja TIMDR, nie walidacja całego formalizmu GIA-TIMDR. Brak realnego sprzętu, szumu skorelowanego i niezależnej estymacji sigma. Protokół TIMDR_ROBUST_PROTOCOL.md; wyniki timdr_robust_results.json; uruchomienie `python outputs/angle_frequency/run_timdr_robust.py`. Wyniki kompaktowe JSON i chronione przed nadpisaniem.
