# Pik odwróconej fazy — wynik eksperymentu

Odwrócenie fazy całego odebranego I/Q o 180° daje dokładnie ten sam pik mocy, szum i odległość. Odjęcie własnej odwróconej kopii zwiększa moc echa i szumu czterokrotnie, bez poprawy ich stosunku. Nie wyławia odległości.

| Metoda | Błąd R, silne echo [m] | Słabe echo: pik blisko prawdy /100 | Moc szumu |
|---|---:|---:|---:|
| Surowe echo | 1.9253 | 4 | 0.04497 |
| Odwrócenie fazy całego I/Q | 1.9253 | 4 | 0.04497 |
| Odwrócenie fazy samego echa | 1.9217 | 6 | 0.04497 |
| Odjęcie własnej odwróconej kopii | 1.9253 | 4 | 0.17987 |
| Filtr dopasowany | 1.9077 | 45 | 0.04496 |

Zmiana 4 na 6 przy odwróceniu samego echa jest małą różnicą realizacji interferencji echa z szumem; nie wykazano systematycznej poprawy. Filtr dopasowany zwiększył lokalny stosunek piku do tła dla silnego echa z 13.51 do 17.71 dB. Nie zwiększa pasma: silne echo pozostaje ograniczone siatką czasu próbkowania.

Odległość liczona jak w echosondzie z czasu powrotu, lecz z prędkością propagacji radaru. W słabym echu błędy R wszystkich prób (łącznie z wyborami szumu) wyniosły 1074.19 m dla surowego I/Q i 591.57 m dla filtra. To sygnał konieczności odrzucania niewiarygodnych pików, a nie gotowy wiarygodny pomiar R.

300 przypadków syntetycznych, 64 impulsy każdy. Uwzględniono 100 przypadków samego szumu: algorytm maksimum zawsze zwraca jakąś odległość nawet bez celu. Nie wyznaczono progu detekcji ani częstości fałszywych alarmów. Brak wielodrogowości i innych celów. Główny tracker nie został zmieniony.

Odtworzenie: `python outputs/angle_frequency/run_echo_peak.py` (chroni istniejące wyniki). Szczegóły: ECHO_PEAK_PROTOCOL.md; wszystkie wyniki: echo_peak_results.json. W każdej próbie sprawdzono niezmienność mocy przy odwróceniu fazy i czterokrotną moc po odjęciu kopii.
