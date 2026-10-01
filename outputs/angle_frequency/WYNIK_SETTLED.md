# Kalibracja po łagodnym rozruchu

Jawny model drgań skrętnych anteny względem wału. Płynna rampa prędkości przez 1 s; obserwacja po dodatkowych 2 s. Porównanie ze skokowym rozruchem i obserwacją pierwszego przejścia wiązki. Enkoder mierzy wał, więc drganie mocowania może wprowadzać błąd kąta wiązki.

| Strategia | Kalibracje przyjęte / 10 | Średnie maksimum drgań przy rozruchu [°] | Przy obserwacji [°] | MAE późniejszych celów [°] |
|---|---:|---:|---:|---:|
| step_early | 4 | 1.7158 | 0.917198 | 0.4300 |
| gentle_settled | 10 | 0.0376 | 0.000000 | 0.0373 |

Łagodna rampa ogranicza wzbudzenie w tym modelu, a czekanie ogranicza drganie podczas pomiaru. To nie dowód całkowitego braku rezonansu. Stałe czasy 1 s i 2 s są parametrami testu, nie uniwersalnymi ustawieniami napędu.

Realna kalibracja wymaga zmierzonej charakterystyki napędu, ramp o ograniczonym przyspieszeniu i zrywie, wyboru prędkości poza rezonansami oraz potwierdzenia ustalenia obrotu z odczytów/czujnika drgań. Sama stabilność enkodera wału może nie ujawnić drgań anteny. Odmowa kalibracji jest lepsza niż wymuszanie parametrów.

Obie strategie korzystają z różnych nowych obserwacji referencji, ale tych samych osobnych ustalonych ech celów. Wynik dotyczy modelu, nie sprzętu. Nie testowano wielodrogowości, filtra impulsów ani ruchu reflektora. R/v nie zmieniono. Odtwarzanie: python run_settled.py w świeżej kopii bez settled_results.json.
