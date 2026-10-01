# Błyski bez zegara — eksploracja

Te same cztery rzeczywiste ślady co signal_results. Nie stroimy progów po wyniku. Moc abs(spec)^2; dla każdego binu tło = mediana mocy po czasie w obrębie ciągłego fragmentu. Stosunek mocy do tła >=10 (10 dB) oraz do mediany widma danej klatki >=10. Składowe połączone w siatce czas–Doppler (8 sąsiadów), min. 3 piksele, czas trwania <=5 klatek. Luki indeksów klatek rozdzielają fragmenty. Fragmenty krótsze niż 10 klatek pomijane i raportowane. To definicja kandydata na krótki błysk, nie fizyczne rozpoznanie łopaty.

Detektor offline (tło korzysta z całego fragmentu). Czas zdarzenia to czas maksimum; zapis częstotliwości maksimum, zakresu, stosunku do tła i rozmiaru. Odstępy liczymy tylko w obrębie tego samego fragmentu, bez wnioskowania RPM. Rozdzielczość czasowa ograniczona do kadencji dostarczonych widm; szybsze błyski mogą być niewidoczne.

Kontrole: stałe widmo (0 zdarzeń), wstrzyknięty impuls (wykrycie), luka (brak sklejenia); na realnym śladzie niezależne przetasowanie czasu każdego binu, 10 ziaren, te same progi. Przetasowanie zachowuje rozkłady mocy, niszczy lokalną spójność; nie jest skalibrowanym modelem szumu i nie daje prawdopodobieństwa fizycznego błysku. Nie wybieramy najładniejszego śladu: wszystkie cztery mapy w raporcie.

Open Radar Initiative, Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, https://github.com/openradarinitiative/open_radar_datasets ; dane CC BY-NC 4.0. Przetworzone widma, nie surowe I/Q. Brak niezależnych etykiet błysków, obrotów lub łopat.
