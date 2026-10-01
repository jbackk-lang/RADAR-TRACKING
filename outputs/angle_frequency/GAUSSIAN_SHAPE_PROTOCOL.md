# Normalny rozkład: kształt echa i szum to osobne pytania

Protokół przed testem: echo nieruchome,64impulsy,20MHz, szum niezależny Gaussa .15 na składową I/Q. Porównanie Gaussa sigma1.5 próbki, Gaussa z ogonem tau8, dwóch Gaussów oddalonych5próbek z amplitudami1/.8 i losową fazą, samego szumu. Jednakowa energia echa, amplituda .65. Średnia zespolona zakłada stabilną fazę; ruch wymaga osobnej kompensacji.

Dopasowanie zespolonego echa do Gaussa z nieznaną amplitudą/fazą, centrum co .25próbki i bankiem szerokości .75,1,1.5,2,3,4,6,8,12próbek. Lokalne okno wokół wybranego piku -32:+48. Środek dopasowanego Gaussa nie jest automatycznie czołem obiektu.

Miara niedopasowania: energia reszty ponad oszacowaną energię szumu, podzielona przez energię sygnału po odjęciu szumu. Szum estymowany ze stałego okna pierwszych64próbek, wolnego od celu w tej symulacji. Próg95.percentyla na100 osobnych Gaussach; próg wykrycia99.percentyla piku/tła na100 osobnych scenach szumu. Test100nowych scen każdego typu. Nie są to formalne p-wartości normalności ani dowód fizycznej polaryzacji.

Skośność i nadmiar kurtozy realnej i urojonej części wygenerowanego szumu zapisane osobno. Prawdziwy szum oddzielony przez generator służy tylko diagnostyce, nie detektorowi. Ponieważ generator używa Gaussa, zgodność jego momentów nie potwierdza takiego rozkładu na sprzęcie.

Jednokanałowe skalarne I/Q nie identyfikuje polaryzacji, kierunku drgań pola ani poprzeczności/podłużności. Rozkład wartości próbek nie jest kształtem impulsu w czasie. Brak ruchu, odbiornikowego ogona i realnych danych. Tracker bez zmian, wynik chroniony.
