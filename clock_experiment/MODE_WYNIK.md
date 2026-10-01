# Hipoteza modu: przeniesienie fazy błysków

Rozpatrujemy strukturę jako kandydata na mod, a zdarzenia M/S jako jego możliwe przejawy. Częstość i fazę ustalono na pierwszych ciągłych fragmentach; ocenę wykonano na późniejszych bez ponownego dopasowania. Czasy jednoczesnych błysków z różnych binów policzono tylko raz.

| Ślad | Zdarzenia train/test | Kandydat Hz | Zgodność fazy test | p po korekcie | Ocena |
|---|---:|---:|---:|---:|---|
| real_person_track_013 | 17/16 | 1.7943 | 0.190 | 0.564 | not_supported |
| real_bicycle_track_014 | 9/6 | 0.1000 | -0.303 | 1.000 | not_supported |
| real_vehicle_track_025 | 21/9 | 0.1000 | -0.441 | 1.000 | not_supported |
| real_uav_track_157 | 8/10 | 0.2619 | 0.355 | 0.944 | not_supported |

Zgodność fazy to średni cosinus względem fazy ustalonej wcześniej: +1 oznacza pełną zgodność, 0 brak skupienia w oczekiwanej fazie, -1 przeciwfazę. Kontrola: 999 losowań zdarzeń po rzeczywiście dostępnych klatkach, z zachowaniem liczby zdarzeń w każdym fragmencie i wszystkich luk. Poprawka Bonferroniego dla 4 śladów. Kryterium kandydata: dodatnia zgodność i p<.05 po korekcie. Częstość jest hipotezą dobraną do treningu, nie zmierzonym RPM.

To eksploracyjny test stałej częstości, po wcześniejszym oglądaniu danych. Zdarzenia mogą pochodzić od różnych źródeł; model nie rozdziela ich fizycznie. Niepowodzenie nie wyklucza modu o zmiennej częstości ani innych pasm. Mała liczba zdarzeń ogranicza moc. Sukces też nie utożsamiałby automatycznie M/S z K ani nie dowodził łopat — wymagałby osobnego potwierdzenia fizycznego.

Źródło: Open Radar Initiative, Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, dane CC BY-NC 4.0. Analiza używa zapisanych kandydatów z flash_results, nie zmienia detektora. Protokół: MODE_PROTOCOL.md. Wyniki i losowe kontrole: mode_results. Uruchomienie: `python -m unittest clock_experiment.test_event_mode -v`, `python -m clock_experiment.run_event_mode`.
