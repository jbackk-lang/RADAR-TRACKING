# RADAR-TRACKING

1. Pobierz punkty z radaru (frame).
2. TRM → usuń punkty bez sąsiadów (fałszywe odbicia).
3. GIA → wyznacz lokalny kierunek ruchu.
4. TIMDR → sprawdź, czy nastąpiła zmiana kierunku / prędkości.
5. Jeśli TIMDR wysoki → obiekt wykonuje manewr.
6. Predictor → przewidź nową pozycję na podstawie GIA.
7. Stabilizer → wygładź trajektorię.
8. Zapisz wynik jako nowy stan trackera.


To jest pełny tracker, ale bez Kalmanów, bez EKF, bez PF —
czysty geometryczny tracker, który jest lekki i szybki.

🧠 3. Minimalny kod (Twoja ulubiona forma — logika, nie wklejanka)
To nie jest ściana kodu — tylko szkic, który możesz wkleić do repo.

python
class RadarTracker:
    def __init__(self):
        self.history = []

    def update(self, points):
        # 1. TRM – filtr spójności
        coherent = trm_filter(points)

        # 2. GIA – kierunek
        direction = gia_direction(coherent)

        # 3. TIMDR – zmiana
        change = timdr_change(coherent)

        # 4. Predykcja
        predicted = predict_next(coherent, direction, change)

        # 5. Stabilizacja
        stable = stabilize(predicted)

        self.history.append(stable)
        return stable
To jest cały tracker.
Reszta to implementacje TRM/GIA/TIMDR, które już masz w repo.

📈 4. Co ten tracker wykrywa?
nagłe skręty (TIMDR)

zmianę prędkości (TIMDR)

fałszywe punkty (TRM)

dominujący kierunek (GIA)

trajektorię obiektu (GIA + predictor)

manewry (TIMDR‑Δ)

punkty krytyczne (TIMDR‑P)

To jest pełny radar‑tracking, który można pokazać każdej firmie od sensorów.
