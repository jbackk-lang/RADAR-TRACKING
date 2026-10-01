# Informacja ze spadku i całego kształtu echa

Protokół przed przebiegiem: porównanie surowego maksimum, dopasowania Gaussa z podpróbkowym czasem, dopasowania całego echa z założonym ogonem tau=8 próbek i dopasowania z bankiem tau=0,2,4,8,12. Amplituda i faza są nieznane; korelacja usuwa je jako parametry nuisance. 16 impulsów, 20 MHz, Gauss sigma1.5, ogon przyczynowy wykładniczy. Normalizacja daje tę samą odebraną energię każdego echa — izoluje informację o kształcie, nie dowodzi wzrostu odbicia. Dopasowanie opóźnienia krok .1 próbki w oknie od surowego piku -8 do +2 próbek; nie korzysta z prawdy. Taki lokalny wybór może zawieść, gdy maksimum pochodzi od szumu.

Próg dla każdej metody zamrożony na 160 osobnych scenach szumu (99. percentyl, higher). Test: 100 nowych pustych scen i po 100: Gauss, ogon tau8, zmieniony ogon tau12, ogon tau8 dodatkowo rozmyty odbiornikiem tau6. Odbiornik rozmywa tylko echo w tej uproszczonej diagnozie; szum jest dodawany po filtrze. Nie jest to pełny model kolorowego szumu instrumentu. Znany filtr odbiornika nie jest odejmowany: badamy szkodę niezidentyfikowanego ogona.

MAE i bias wyłącznie wśród wykryć; poprawna lokalizacja oznacza błąd <7.5 m. Wszystkie wykrycia, odrzucenia i fałszywe alarmy zapisane osobno. Parametry i progi nie zmieniane po wynikach. Bank modeli ma większy koszt i wymaga własnego progu ze względu na przeszukiwanie.

Sam wykładniczy spadek A*exp(-(t-t0)/tau) nie identyfikuje t0 przy nieznanej amplitudzie A: przesunięcie t0 można pochłonąć w A. Dlatego testujemy narastanie i spadek razem. Bez sprzętu, ruchu, wielodrogowości i impulsowych zakłóceń. Główny tracker bez zmian. Plik wyniku chroniony przed nadpisaniem.
