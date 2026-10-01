# Błysk energii jako odpowiedź reflektora

Wariant energy_flash dodany po poleceniu użytkownika: echo o takiej samej całkowitej energii jak odniesienie, skompresowane do Gaussa sigma .5 próbki. Wyższa moc szczytowa nie oznacza dodatkowej energii. Model dotyczy specjalnego, sterowanego reflektora z magazynowaniem energii i zmianą kształtu odpowiedzi; nie jest pasywnym liniowym rezonansem ani dowodem, że dowolny cel to zrobi.

Znana zwłoka odpowiedzi 12 próbek (600 ns) jest odejmowana od estymaty R. Bez jej odjęcia pojawiłby się błąd 89.938 m. Jej błąd 50 ns oznacza błąd R 7.495 m. Zakładamy idealnie stabilną, znaną zwłokę i pełny zwrot założonej energii, bez strat magazynowania; wynik jest korzystną granicą modelową. Krótszy impuls potrzebuje szerszego pasma: nie uzyskujemy poprawy za darmo. Sigma .5 przy 20 MHz zbliża się do ograniczeń próbkowania; to dyskretny model bazowy, nie gotowa realizacja RF.

Próg automatyczny ustalony na osobnych 300 scenach szumu, test 600 scen jak w WAVE_METHODS_PROTOCOL.md. Polecenie: `python outputs/angle_frequency/run_wave_methods.py --flash`, plik wave_flash_results.json. Warianty wcześniejsze pozostają zachowane. Oceniono idealnie znaną odpowiedź specjalnego celu, nie zmianę istniejącego radaru.
