# Minimalna ingerencja — wynik

Wprowadzono nowy kontroler: częściowa korekta oceniana na zwykłej referencji, bez EMA. Przy niepewności maleje o połowę za epizod od ostatniego potwierdzenia; po TTL=2 wygasa. Odrzucenie wyłącza korektę od razu.

Siły wybrane na danych rozwojowych: odległość **25%**, kąt **25%**, prędkość **35%** początkowej kalibracji.

Wybrano najmniejsze siły z ustalonej listy spełniające kryterium MAE ≤ 80% raw w obu scenariuszach rozwojowych. Nie jest to minimum wśród wszystkich możliwych wartości ani gwarancja bezpieczeństwa. Plik selection.json zapisano przed rozpoczęciem oceny. Parametrów nie zmieniono po wyniku.

Ocena: osobne ziarna 200–219, 480 referencji, 1440 pomiarów celów z nowych I/Q. Warianty dostają te same echa. Dodatkowe obserwacje wymagane przez kontroler: 0. Model i trajektorie scenariuszy są znane; test sprawdza nowe realizacje szumu, nie nowy sprzęt.

## Dotychczasowa trajektoria, nowy szum

| Wariant | MAE R [m] | MAE kąta [rad] | MAE v [m/s] |
|---|---:|---:|---:|
| Bez korekty | 18.1836 | 0.02083 | 0.7603 |
| Pełna pamięć | 0.4266 | 0.00163 | 0.2386 |
| Pełna korekta + wygaszanie | 2.6116 | 0.00392 | 0.2846 |
| Częściowa korekta + wygaszanie | 14.1984 | 0.01638 | 0.5816 |

Zmiana MAE częściowej korekty względem surowego pomiaru (wartość ujemna oznacza poprawę):

- range_m: -21.9%.
- bearing_rad: -21.4%.
- radial_velocity_m_s: -23.5%.

| Wariant | Średnia ingerencja R [m] | Kąt [rad] | v [m/s] |
|---|---:|---:|---:|
| Pełna pamięć | 18.2182 | 0.02062 | 0.5807 |
| Pełna korekta + wygaszanie | 15.9409 | 0.01804 | 0.4800 |
| Częściowa korekta + wygaszanie | 3.9852 | 0.00457 | 0.1787 |

Sparowane różnice MAE po 20 ziarnach; bootstrap CI95 z 10000 próbek, bez korekty wielokrotnych porównań. Ujemna różnica oznacza mniejszy błąd pierwszego wariantu. Zdegenerowane CI odległości wynikają ze stałych binów w tym modelu, nie z pewności poza nim.

- minimal minus raw, range_m: -3.985225; CI95 [-3.985225, -3.985225].
- minimal minus raw, bearing_rad: -0.004451; CI95 [-0.004676, -0.004233].
- minimal minus raw, radial_velocity_m_s: -0.178726; CI95 [-0.180153, -0.177376].
- minimal minus memory, range_m: 13.771744; CI95 [13.771744, 13.771744].
- minimal minus memory, bearing_rad: 0.014757; CI95 [0.014090, 0.015314].
- minimal minus memory, radial_velocity_m_s: 0.343011; CI95 [0.341797, 0.344239].
- decay_only minus memory, range_m: 2.185031; CI95 [2.185031, 2.185031].
- decay_only minus memory, bearing_rad: 0.002295; CI95 [0.002147, 0.002412].
- decay_only minus memory, radial_velocity_m_s: 0.045991; CI95 [0.044269, 0.049057].
- minimal minus decay_only, range_m: 11.586713; CI95 [11.586713, 11.586713].
- minimal minus decay_only, bearing_rad: 0.012462; CI95 [0.011942, 0.012903].
- minimal minus decay_only, radial_velocity_m_s: 0.297020; CI95 [0.293884, 0.299100].

## Nagła zmiana instrumentu przy słabej referencji

| Wariant | MAE R [m] | MAE kąta [rad] | MAE v [m/s] |
|---|---:|---:|---:|
| Bez korekty | 11.2422 | 0.01250 | 0.3965 |
| Pełna pamięć | 4.2317 | 0.00512 | 0.2225 |
| Pełna korekta + wygaszanie | 1.9544 | 0.00244 | 0.1499 |
| Częściowa korekta + wygaszanie | 8.8511 | 0.00983 | 0.2883 |

Zmiana MAE częściowej korekty względem surowego pomiaru (wartość ujemna oznacza poprawę):

- range_m: -21.3%.
- bearing_rad: -21.3%.
- radial_velocity_m_s: -27.3%.

| Wariant | Średnia ingerencja R [m] | Kąt [rad] | v [m/s] |
|---|---:|---:|---:|
| Pełna pamięć | 14.5745 | 0.01712 | 0.4156 |
| Pełna korekta + wygaszanie | 12.2973 | 0.01444 | 0.3430 |
| Częściowa korekta + wygaszanie | 3.0743 | 0.00375 | 0.1374 |

Sparowane różnice MAE po 20 ziarnach; bootstrap CI95 z 10000 próbek, bez korekty wielokrotnych porównań. Ujemna różnica oznacza mniejszy błąd pierwszego wariantu. Zdegenerowane CI odległości wynikają ze stałych binów w tym modelu, nie z pewności poza nim.

- minimal minus raw, range_m: -2.391135; CI95 [-2.391135, -2.391135].
- minimal minus raw, bearing_rad: -0.002667; CI95 [-0.002781, -0.002547].
- minimal minus raw, radial_velocity_m_s: -0.108194; CI95 [-0.109018, -0.107313].
- minimal minus memory, range_m: 4.619411; CI95 [4.619411, 4.619411].
- minimal minus memory, bearing_rad: 0.004717; CI95 [0.004257, 0.005138].
- minimal minus memory, radial_velocity_m_s: 0.065735; CI95 [0.065112, 0.066264].
- decay_only minus memory, range_m: -2.277272; CI95 [-2.277272, -2.277272].
- decay_only minus memory, bearing_rad: -0.002674; CI95 [-0.002766, -0.002585].
- decay_only minus memory, radial_velocity_m_s: -0.072687; CI95 [-0.073275, -0.072048].
- minimal minus decay_only, range_m: 6.896683; CI95 [6.896683, 6.896683].
- minimal minus decay_only, bearing_rad: 0.007391; CI95 [0.007010, 0.007738].
- minimal minus decay_only, radial_velocity_m_s: 0.138422; CI95 [0.137650, 0.139087].

Błąd instrumentu znika w epizodzie 4, referencja jest zaszumiona w 4–6. Średni dodatni nadmiar błędu względem raw w tych trzech epizodach (ujemne różnice liczone jako zero):

| Wariant | Nadmiar R [m] | Kąt [rad] | v [m/s] |
|---|---:|---:|---:|
| Pełna pamięć | 14.5745 | 0.01712 | 0.4598 |
| Pełna korekta + wygaszanie | 5.4655 | 0.00642 | 0.1691 |
| Częściowa korekta + wygaszanie | 1.3664 | 0.00160 | 0.0557 |

Udział pomiarów ze szkodą większą niż margines kontrolera:

- Pełna pamięć: R 66.7%, kąt 66.7%, v 66.7%.
- Pełna korekta + wygaszanie: R 66.7%, kąt 66.7%, v 66.7%.
- Częściowa korekta + wygaszanie: R 0.0%, kąt 0.0%, v 58.3%.

| Epizod | Raw R [m] | Pamięć R [m] | Częściowa R [m] | Raw v [m/s] | Pamięć v [m/s] | Częściowa v [m/s] |
|---|---:|---:|---:|---:|---:|---:|
| 4 | 0.8302 | 22.6920 | 3.5629 | 0.0107 | 0.7000 | 0.1243 |
| 5 | 0.8302 | 22.6920 | 2.1965 | 0.0113 | 0.7014 | 0.0647 |
| 6 | 0.8302 | 0.8302 | 0.8302 | 0.0119 | 0.0119 | 0.0119 |
| 7 | 0.8302 | 0.8302 | 0.8302 | 0.0108 | 0.0108 | 0.0108 |

## Wniosek i weryfikacja

Częściowa korekta poprawiła raw o około 21–27% na nowych ziarnach, ale miała większy średni błąd niż pełna pamięć w obu scenariuszach. Po ukrytej zmianie zmniejszyła średni dodatni nadmiar błędu odległości z 14.5745 do 1.3664 m, a prędkości z 0.4598 do 0.0557 m/s względem pełnej pamięci. Nie usunęła szkody całkowicie.

Samo wygaszanie pełnej korekty było lepsze od stale częściowej ingerencji pod względem średniego błędu wszystkich trzech parametrów w obu scenariuszach. W scenariuszu ukrytej zmiany poprawiło też wszystkie trzy MAE względem pełnej pamięci; przy dotychczasowej trajektorii zwiększyło MAE. Dlatego minimalna siła jest wyborem kompromisu, a nie automatycznie najlepszą dokładnością.

Częściowa ingerencja z wygaszaniem zmniejsza koszt nieaktualnej korekty, ale oddaje część poprawy pełnej pamięci, gdy kalibracja jest nadal właściwa. Ocena obejmuje oba efekty. Wynik nie uzasadnia uniwersalnej przewagi ani gwarancji bezpieczeństwa. Bez wiarygodnej referencji nie da się w tym modelu rozstrzygnąć, czy błąd instrumentu zniknął.

10 testów kontrolerów przeszło. Odtworzono 1440 decyzji, błędy 1440 pomiarów, wszystkie średnie scenariuszy i sprawdzono hashe. Dodatkowo analityczna kompensacja zgadzała się z pełnym przetwarzaniem I/Q dla 1440 pomiarów rozwojowych i 1440 nowych pomiarów. To sprawdzenie właściwości tego liniowego modelu, nie walidacja innych modeli.

Odtwarzanie w katalogu minimal_intervention:

`python -m unittest clock_experiment.test_minimal_calibration clock_experiment.test_online_calibration clock_experiment.test_calibration_guard -v`

`python report_minimal.py` — weryfikuje zapisane decyzje i metryki.

`python run_minimal.py` — chroni istniejące selection.json i results.json; kolejny przebieg wymaga osobnej kopii bez tych dwóch plików. Obok musi znajdować się katalog validation z pierwotnymi danymi rozwojowymi.
