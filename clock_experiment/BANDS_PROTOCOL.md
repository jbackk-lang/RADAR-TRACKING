# Zegar w pasmach widma — pilot na realnym radarze

Stały podział 1008 binów fftshift na 4 równe, sąsiadujące pasma (po 252 biny), bez wyboru pasma według wyniku. Cztery ślady z poprzedniego signal_results, dokładnie te same wejścia i hashe. To badanie eksploracyjne po wcześniejszych wynikach, nie nowy holdout.

W każdym paśmie amplituda sqrt(sum(abs(spec)^2)), osobny SignalClockMonitor, identyczne granice .1..4 Hz i dryf -.02..02 Hz/s. Prognoza w t używa danych przed t. Pierwsze 100 próbek to rozruch. Wszystkie pozostałe próbki oceniane, także fallback. Przewidywane amplitudy pasm ograniczamy od dołu do 0 i rekonstruujemy pełną amplitudę przez sqrt(sum(predicted_band_amplitude^2)). Dzięki temu wszystkie główne metryki odnoszą się do tego SAMEGO celu: całej amplitudy, a nie nieporównywalnych wariancji różnych pasm.

Odniesienia: wcześniejszy monitor całego widma (weryfikujemy wejścia i prognozy), średnia 12 poprzednich pełnych amplitud oraz rekonstrukcja ze średnich 12 poprzednich amplitud pasm. Ta ostatnia izoluje wpływ samego podziału na pasma od zegara. Raportujemy pokrycie zegarem każdego pasma, czasy nowych obliczeń, wszystkie pasma. Nie przypisujemy pasm korpusowi/łopatom bez niezależnej walidacji. Nie śledzimy przesuwających się pasm w tym pilocie.

Źródło: Open Radar Initiative, Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, https://github.com/openradarinitiative/open_radar_datasets ; dane CC BY-NC 4.0. Widma przetworzone, nie surowe ADC. Krótkie ślady z lukami, brak RPM i niezależnego odniesienia pozycji. Wynik dotyczy tylko prognozy amplitudy. Żadnego strojenia po nowych wynikach.
