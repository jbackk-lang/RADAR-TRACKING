# Faza nośnej: dokładniejsza estymacja v i zmiany R

**Wynik:** spójne dopasowanie fazy po 64 impulsach poprawiło estymację v dla izolowanego echa, także słabego. Nie rozdzieliło słabego celu od dominującego echa i nie usunęło dryfu fazy instrumentu. Bezwzględne R pozostało odczytem z obwiedni.

120 burstów, 20 ziaren na warunek. Nowy generator uwzględnia fazę propagacji 4πR(t)/lambda i nieznaną stałą fazę rozpraszania. Obie metody mają identyczne I/Q. Bazowa metoda używa różnicy faz kolejnych impulsów w jednym binie. Nowa łączy 7 sąsiednich próbek obwiedni i dopasowuje Doppler spójnie w całym burście. Zysk pochodzi z estymatora i wykorzystania próbek; nie dowodzi nowego efektu fizycznego samej nośnej.

| Warunki | Bazowy MAE v [m/s] | Spójny MAE v [m/s] | Bazowy MAE deltaR [mm] | Spójny MAE deltaR [mm] |
|---|---:|---:|---:|---:|
| single_slow | 0.012180 | 0.001251 | 0.0959 | 0.0098 |
| single_fast | 0.010019 | 0.001590 | 0.0789 | 0.0125 |
| weak_isolated | 0.221165 | 0.005653 | 1.7417 | 0.0445 |
| weak_overlap | 0.036088 | 0.038511 | 0.2842 | 0.3033 |
| weak_overlap_separated_doppler | 0.959740 | 1.000069 | 7.5579 | 7.8755 |
| instrument_drift | 0.019066 | 0.020121 | 0.1501 | 0.1585 |

single_slow: v=.04 m/s; single_fast: v=1 m/s; weak_isolated: amplituda .2, v=.04; weak_overlap: ten sam słaby oraz silny nieruchomy cel o R większym o 1 m; weak_overlap_separated_doppler: słaby v=1 i silny v=0; instrument_drift: target v=.04 plus nieskorygowany instrumentalny dryf fazy odpowiadający .02 m/s.

Ważne: deltaR = v_est × 7.875 ms przy założeniu stałej prędkości. Jej błąd jest przeskalowanym błędem v, nie drugą niezależną poprawą ani pomiarem bezwzględnego R. Nieznana faza rozpraszania i niejednoznaczność fazy uniemożliwiają bezpośrednie zastąpienie odczytu R milimetrowym wynikiem.

Dla izolowanych ech o amplitudzie 1 błąd bezwzględnego R z maksimum obwiedni pozostaje około .830 m. Dla słabego izolowanego echa wyniósł 2.163 m. Nie dodano poprawki R.

Nakładające się silne echo dominuje w wybranym maksimum Dopplera: nowy estymator nie ma detektora drugiego maksimum i nie rozwiązuje asocjacji składowych. Nawet różne Dopplery nie pomagają, jeśli algorytm raportuje wyłącznie najsilniejszą składową. Dryf instrumentu jest nierozróżnialny od ruchu bez niezależnej kalibracji; fazowe przetwarzanie go nie usuwa.

Zysk dla isolated_slow wynosi około 90%, dla isolated_fast 84%, a weak_isolated 97% względem bazowego estymatora w tych danych. Nie dotyczy wszystkich warunków. Brak wielodrogowości, przyspieszania wewnątrz burstu, zmiennej fazy rozpraszania i walidacji realnej. Wyższa efektywność estymacji nie zwiększa fizycznej rozdzielczości pasma ani czasu obserwacji.

3 testy przeszły. Odtworzono wszystkie 120 pełnych burstów I/Q z generatora, estymaty i zapisane fazory; sprawdzono hashe i MAE v. Odtwarzanie: python -m unittest test_carrier_phase -v; python report_carrier.py. python run_carrier.py chroni istniejące wyniki. Pełne I/Q odtwarza się z zapisanych ziaren; zapisano jedynie wydobyte fazory. Główny tracker i stary generator pozostają bez zmian.
