# Czy echo ma normalny kształt?

Sprawdzono osobno kształt impulsu i statystykę szumu. Rozkład normalny wartości szumu nie oznacza, że echo ma obwiednię Gaussa.

| Scena | Wykryte /100 | Zgodne z pojedynczym Gaussem /100 | Mediana niedopasowania | MAE centrum dopasowania [m] |
|---|---:|---:|---:|---:|
| Gauss | 100 | 93 | 0.000 | 0.555 |
| Echo z ogonem | 100 | 4 | 0.090 | 28.883 |
| Dwa odbicia | 100 | 0 | 0.359 | 7.285 |
| Brak celu | 0 | 0 | — | — |

100 osobnych Gaussów ustaliło próg niedopasowania,100 osobnych pustych scen ustaliło próg wykrycia;400 nowych scen testowych. Zgodność oznacza przejście progu rozwojowego, nie formalny test normalności.93/100 potwierdza także ryzyko odrzucenia dobrego prostego echa.4/100 ogonów zaakceptowano błędnie jako zgodne.0/100 alarmów w szumie nie jest gwarancją zera.

Pojedynczy Gauss dobrze doprecyzował centrum zwykłego echa, ale jego dopasowanie do ogona przesuwało czas o około29m. W dwóch odbiciach dopasowany środek również nie musi oznaczać czoła. Niedopasowanie pomaga skierować echo do banku innych kształtów lub odrzucić niewiarygodną odległość. Nie można z samego niedopasowania rozstrzygnąć, czy przyczyną jest obiekt, odbiornik, zakłócenie czy wielodrogowość.

W szumie zapisano mean/std/skew/excess_kurtosis osobno dla części realnej i urojonej. Generator z definicji używa szumu Gaussa; zgodne momenty nie dowodzą normalności rzeczywistych zakłóceń. Detektor nie korzysta z prawdziwego wydzielonego szumu, tylko z okna bez celu założonego w symulacji.

I/Q jest skalarnym zapisem sygnału po odbiorze. Te dane nie wystarczają do ustalenia polaryzacji pionowej/poziomej ani kierunku drgań pola. Kształt impulsu w czasie i poprzeczność fali to różne własności. Potrzebne są odpowiednie pomiary składowych pola lub kanały polaryzacyjne.

Kontrole bezszumowego centrum, szerokości i niezmienności na globalną fazę przeszły. Protokół GAUSSIAN_SHAPE_PROTOCOL.md, pełne wyniki gaussian_shape_results.json. Odtworzenie: `python outputs/angle_frequency/run_gaussian_shape.py`; chroni istniejące wyniki. Echo nieruchome, koherentne, bez sprzętu i rzeczywistych zakłóceń. Tracker bez zmian.
