# Pik czasu powrotu jak w echosondzie

Porównanie na identycznych 64 impulsach I/Q: sygnał surowy, obrót całego I/Q o 180 stopni, obrót samego echa przy tym samym szumie, odjęcie własnej odwróconej kopii oraz filtr dopasowany do znanej obwiedni Gaussa. Odległość z maksimum średniej mocy: R=c*k/(2*fs). Prędkość propagacji jest radarowa; w echosondzie należałoby użyć prędkości dźwięku w danym ośrodku.

100 ziaren dla silnego echa, słabego echa i samego szumu. 20 MHz, 512 próbek, szerokość Gaussa 1.5 próbki, szum zespolony o odchyleniu .15 na składową. Losowa odległość 1100–1300 m zapobiega wnioskowaniu z jednego położenia względem siatki. Bez dopasowania progów po wynikach. Pik blisko prawdy oznacza maksimum w promieniu 3 próbek; to diagnostyka lokalizacji, nie detektor z kontrolowanym prawdopodobieństwem fałszywego alarmu.

Filtr ma jednostkową energię; poziom szumu jest średnią mocy poza oknem +/-15 próbek od prawdy. Odwrócenie samego echa odpowiada zmianie fazy fizycznego sygnału, a odwrócenie całego I/Q operacji po odbiorze. Kopia tego samego szumu nie jest niezależnym pomiarem. Sprawdzamy algebraiczną niezmienność mocy przy odwróceniu fazy i czterokrotną moc po odjęciu odwróconej kopii.

To model syntetyczny: bez zakłóceń impulsowych, wielodrogowości, innych celów, progu wykrywania i zmian sprzętu. Filtr dopasowany nie zwiększa pasma ani fizycznej rozdzielczości. Wyniki nie są integracją z głównym trackerem.
