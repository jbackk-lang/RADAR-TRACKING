# Selektor zgodności fazy i częstotliwości

**Wniosek:** zachowanie wspólnej fazy po paśmie pomaga w tym modelu wykrywać słabe echo z innym opóźnieniem. Nie wykazano równie mocnej korzyści dla celu o tej samej odległości. Ustalony próg selektora spójnego nie utrzymał testowego limitu 5% fałszywych alarmów, więc ten wariant pozostaje eksperymentalny.

9 częstotliwości, dwa RX, te same I/Q dla obu metod. Słabe echo ma 15% amplitudy silnego (2.25% mocy). Dopasowanie silnego wzorca i jego projekcja, następnie test słabych wzorców. Wzorce z utratą ponad 95% energii są wykluczone. Wspólne ważenie impulsów zachowuje fazę kanałów. Porównanie: selektor spójny po paśmie vs suma mocy dopasowań pasm bez wspólnej fazy.

## Progi ustalone przed oceną

100 rozwojowych kontroli ustaliło próg 95. percentyla maksimum po wszystkich kandydatach. Później 100 nowych kontroli silny-bez-słabego, 100 pustych i 60 par. Połowa z impulsami. Próg nie był zmieniany po ocenie.

| Metoda | Fałszywe alarmy: silny bez słabego / 100 | Puste / 100 | Poprawnie wykryte słabe / 60 | Ta sama odległość / 20 |
|---|---:|---:|---:|---:|
| coherent | 13 | 2 | 36 | 4 |
| band_power | 3 | 2 | 1 | 1 |

Fałszywe alarmy nie są jednakowe, więc 36 vs 1 poprawnych detekcji nie jest dowodem przewagi przy tym samym ustalonym FPR. Próg z tylko 100 kontroli nie gwarantuje FPR na nowej próbie.

## Opisowe porównanie przy równym obserwowanym FPR

Dodatkowo po wyniku wyznaczono punkt ROC: próg każdej metody daje 5 alarmów na tych samych 100 testowych kontrolach. Jest to analiza opisowa tej próby, nie niezależna walidacja nowych progów. Nie zapisujemy ich jako konfiguracji detektora.

| Metoda | Alarmy / 100 | Poprawne słabe / 60 | Ta sama odległość / 20 |
|---|---:|---:|---:|
| coherent | 5 | 36 | 4 |
| band_power | 5 | 1 | 1 |

Korzyść przy różnym opóźnieniu oznacza wykorzystanie informacji o odległości w fazie pasma. Nie utożsamiamy jej z poprawą rozdzielczości kąta. Suma mocy pasm usuwa tę informację i nie jest porównaniem ze wszystkimi standardowymi procesorami radarowymi.

Model zakłada jedną zespoloną amplitudę celu po całym paśmie, idealną fazę i znaną wiązkę. Rzeczywisty cel, kanał lub wielodrogowość mogą naruszyć te założenia. Filtr badano tylko przy szumie i impulsach. Nie ma podstaw do deklaracji gotowości sprzętowej.

4 testy przeszły. Ponownie obliczono decyzje 260 testowych scen, sprawdzono hashe i odtworzono 18 zestawów wyników selektora z zapisanych I/Q.

Odtwarzanie: python -m unittest test_frequency_selector -v; python report_selector.py. python run_selector.py chroni istniejące progi i wyniki.
