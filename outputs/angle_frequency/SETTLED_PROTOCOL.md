# Kalibracja z łagodnym rozruchem i po ustaleniu obrotu

Porównanie rozruchu skokowego z płynnym profilem prędkości 10u^3-15u^4+6u^5 przez 1 s i odczekaniem 2 s po rampie przed obserwacją reflektora. Model skrętnego drgania anteny względem wału: q''+2*zeta*wr*q'+wr^2*q=.5*przyspieszenie napędu, zeta=.06, częstotliwość własna 12..19.2 Hz (10 ziaren). Enkoder mierzy wał, wiązka kierunek wału+q. To jawny model sprężystego mocowania, nie dane realne ani identyfikacja rzeczywistego rezonansu.

Reflektor 1.2 rad. 3 prędkości .5,1,1.5 obr/s, 2 próbki na prędkość, 10 ziaren na strategię (120 nowych obserwacji referencji). Strategia skokowa zbiera pierwszy obrót; łagodna pierwszy pełny przejazd przez referencję po 3 s. Znany kąt referencji uwzględnia pełne obroty. Opóźnienie 2 ms, zero enkodera .12°, szum I/Q .1 i enkodera .02°. Zamrozić kalibracje, ocenić je na 90 osobnych ustalonych skanach (.65,1.25,1.8 obr/s, kąty .4,1.2,2). Ten sam test dla obu kalibracji; bez strojenia.

Raportować największe drganie podczas rozruchu i przy obserwacji oraz MAE kąta na późniejszych celach. Nie nazywać wygaszonego drgania brakiem wzbudzenia: profile płynne także mogą wzbudzać układ. Docelowo próbkowanie kalibracji wymaga obserwowanej stabilności napędu, a dopuszczalne rampy i częstotliwości muszą pochodzić z charakterystyki sprzętu. R/v bez zmian. Wyniki chronione przed nadpisaniem.
