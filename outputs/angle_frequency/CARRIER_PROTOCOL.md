# Nośna: obwiednia, faza i Doppler

Osobny model impulsowy I/Q: carrier=77 GHz, fs=20 MHz, PRF=8 kHz, 64 impulsy × 512 próbek. R=1200 m, gaussian obwiedni sigma=1.5 próbki, szum .15 na składową. Faza echa = stała nieznana faza rozpraszania + 4*pi*R(t)/lambda. Nie zmieniamy starego generatora, który nie kodował fazy początkowej z R.

120 burstów: 20 ziaren × single_slow (amplituda1, v=.04), single_fast (1,v=1), weak_isolated (.2,v=.04), weak_overlap (.2,v=.04 + silny1,v=0, R+1m), weak_overlap_separated_doppler (.2,v=1 + silny1,v=0,R+1m), instrument_drift (1,v=.04 + wspólny dryf fazy równoważny .02m/s). Losowe, stałe fazy rozpraszania celu i silnego zakłócającego echa. Prawda wyłącznie do oceny.

Obwiednia wskazuje bin R. Bazowy v: dotychczasowa różnica faz kolejnych impulsów w najsilniejszym binie. Nowy: wydobyć zespolony sygnał przez ważoną sumę 7 próbek wokół maksimum obwiedni; dopasować fazę narastającą liniowo przez maksimum widma Dopplera (FFT4096, interpolacja paraboliczna maksimum). Zero padding interpoluje widmo, nie zwiększa fizycznej rozdzielczości. Nie odejmujemy nieznanego dryfu instrumentu na podstawie prawdy.

R bezwzględne nadal z obwiedni; faza rozpraszania nie jest znana. DeltaR w stałym ruchu = v_est * czas między pierwszym i ostatnim impulsem, więc nie jest niezależną metryką od v. Nie ogłaszać poprawy bezwzględnego R ani rozdzielenia dwóch celów na podstawie fazy dominującej mieszaniny. Raportować wszystkie przypadki, także silny cel i dryf. Brak strojenia po wyniku. Zachować seed, surowe estymaty, wydobyte fazory i hashe; pełne I/Q odtwarzać z generatora. R/v starego pipeline'u nie zmieniono.
