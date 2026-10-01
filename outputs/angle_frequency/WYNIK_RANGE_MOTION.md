# Widmo ruchu i doprecyzowanie odległości

300 testowych scen po zamrożeniu progów na 100 osobnych scenach szumu. Doppler oszacowany z I/Q, bez prawdziwej prędkości. Osobny model 3 GHz, 512 impulsów, 32 kHz PRF; nie zmiana radaru77GHz. R odniesione do środka okna pomiarowego.

| Ruch | MAE R: niespójne dopasowanie [m] | MAE R: wyrównanie fazy [m] | MAE R: faza + migracja [m] | MAE v [m/s] |
|---|---:|---:|---:|---:|
| Nieruchomy | 0.424 | 0.367 | 0.367 | 0.039 |
| 30 m/s | 0.442 | 0.330 | 0.330 | 0.039 |
| 600 m/s | 0.473 | 0.406 | 0.404 | 0.039 |
| 100 m/s, przyspieszenie 3000 m/s² | 0.449 | 1.248 | 1.155 | 12.089 |

W każdym wierszu powyższe trzy metody poprawnie wykryły60/60 scen. Przy30m/s wyrównanie fazy zmniejszyło MAE R o około25%; dodanie wyrównania migracji nie przyniosło mierzalnego zysku w tej siatce. Przy600m/s łączny zysk wobec niespójnego dopasowania około15%; dodatkowa migracja wobec samej fazy jedynie0.6%. Bez wyrównania fazy sumowanie zespolone poprawnie wykryło4/60 przy30m/s i0/60 przy600m/s. Niespójne sumowanie mocy stanowi mocniejszy punkt odniesienia niż takie błędne sumowanie.

Przy przyspieszeniu model stałej prędkości pogorszył R ponad dwukrotnie. Nie należy stosować kompensacji ruchu bez oceny zgodności modelu. Test nie obejmował dopasowania przyspieszenia ani automatycznego wyboru między modelami ruchu.

Nowe60 pustych scen: niespójna metoda0 alarmów, sumowanie niewyrównane2, faza0, faza+migracja0. Mała próba i progi rozwojowe nie gwarantują braku alarmów. MAE R warunkowe wśród wykryć. 600m/s to scenariusz diagnostyczny; migracja około9.58m podczas okna15.97ms, przy30m/s około.48m. Przyspieszenie również diagnostyczne, nie typowy ruch naziemny.

Kontrole bezszumowe dla0,+30,-30,600m/s: znak i wartość Dopplera oraz R w środku okna. Brak rzeczywistych danych, wielodrogowości, obrotu, ogona i rozmiaru obiektu. Nie wykazano, że ruch skraca rezonansowy ogon. Główny tracker bez zmian.

Protokół RANGE_MOTION_PROTOCOL.md, wszystkie decyzje range_motion_results.json. Odtworzenie: `python outputs/angle_frequency/run_range_motion.py`; wyniki chronione przed nadpisaniem.

## Czoło echa jako osobna hipoteza

Użytkownik wskazał, że interesuje go czoło, a reszta echa może być opisem obiektu. Dla rozciągłego celu należy osobno zdefiniować odległość najbliższej wykrywalnej powierzchni i odległość środka. Czoło bywa słabe i zaszumione; nie wolno utożsamiać pierwszej próbki ponad próg z dokładnym początkiem. Ogon nie jest sam w sobie kierunkiem przestrzennym, a jego pochodzenie nie ogranicza się do drgań cząsteczek. Ten test dotyczył punktowego echa i nie walidował jeszcze estymatora czoła rozciągłego obiektu.
