# Nakładanie I/Q i dwa kanały — wynik

**Wniosek:** wspólne dopasowanie zespolonych ech rozdziela większość badanych par. Drugi kanał przy rozstawie lambda/2 nie wykazał dodatkowej przewagi w tym małym eksperymencie. Nie wynika z tego, że stereoskopia jest nieskuteczna dla innych rozstawów i warunków.

Dwa cele w tej samej komórce R/v nakładano koherentnie, uwzględniając fazy 0, pi/2 i pi oraz różne amplitudy. Model dobiera jeden lub dwa cele przez BIC, dopasowując wspólnie kąty i zespolone amplitudy. 180 par i 20 pojedynczych celów. Łączna energia sygnału jest taka sama dla 1 i 2 kanałów; dwa kanały mają więcej próbek szumu.

| Wariant | Poprawnie rozdzielone pary / 180 | Fałszywie rozdzielone pojedyncze / 20 | MAE przy wyborze dwóch [°] |
|---|---:|---:|---:|
| 1 kanał(y) | 168 | 0 | 0.0609 |
| 2 kanał(y) | 164 | 0 | 0.0636 |

Poprawne rozdzielenie oznacza wybór dwóch celów i błąd każdego kąta <=.25°. MAE w tabeli jest warunkowe: pomija przypadki, w których wybrano jeden cel. Nie przedstawia całkowitego kosztu nieudanych rozdzieleń.

| Separacja | 1 kanał: poprawne / 60 | 2 kanały: poprawne / 60 |
|---|---:|---:|
| 0.75° | 49 | 47 |
| 1.5° | 59 | 57 |
| 3.0° | 60 | 60 |

| Amplituda drugiego / pierwszego | 1 kanał: poprawne / 45 | 2 kanały: poprawne / 45 |
|---|---:|---:|
| 0.25 | 37 | 35 |
| 0.5 | 42 | 43 |
| 1.0 | 44 | 44 |
| 2.0 | 45 | 42 |

Sparowane przypadki: tylko dwa kanały poprawne — 6; tylko jeden kanał poprawny — 10. Próba jest mała; nie ogłaszamy przewagi żadnej liczby kanałów.

Przy rozstawie lambda/2 i kącie około 1.2 rad różnica faz między kierunkami oddalonymi o .75° wynosi około .015 rad. To niewielka dodatkowa informacja przy badanym szumie .05 na składową. Jest to interpretacja geometryczna wynikająca z modelu; nie odrębny dowód przyczyny wyniku. Większy rozstaw może zwiększyć czułość, ale wprowadza niejednoznaczności fazy, których ten test nie bada.

Ograniczenia: dopasowanie zna idealny model wiązki i fazy, kanały są idealnie skalibrowane i zsynchronizowane, cele nieruchome, bez wielodrogowości. Obserwujemy cały skan ±6°, nie pojedynczą próbkę. Badane kąty ograniczono do ±5° wokół kierunku 1.2 rad. R/v nie zmieniano ani nie testowano ponownie.

4 testy przeszły. Odtworzono 400 dopasowań z zapisanych surowych I/Q (200 scen × 2 warianty); sprawdzono metryki poprawnego rozdzielenia i hashe.

Odtwarzanie: python -m unittest test_stereo_model -v oraz python report_stereo.py. python run_stereo.py chroni istniejące wyniki; do ponownego przebiegu użyj świeżej kopii bez stereo_results.json i stereo_iq.npz.
