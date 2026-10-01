"""Verify saved adaptive experiment and produce a report, without retuning."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent

def main():
    folder=ROOT/'adaptive_results'
    r=json.loads((folder/'summary.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/'ADAPTIVE_PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256']
    for name,digest in r['code_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    lines=[]
    for row in r['runs']:
        with np.load(folder/f"{row['case']}_{row['seed']}_{row['mode']}.npz",allow_pickle=False) as z:
            err=float(np.sqrt(np.mean((z['predicted']-z['truth'])**2)))
            assert abs(err-row['rmse_m'])<1e-12
            assert int(np.sum(~z['keep']))==row['rejected_frames']
            assert len(z['predicted'])==480
            assert np.all(np.isfinite(z['predicted']))
    s=r['summary']
    for case,methods in s.items():
        for mode,v in methods.items():
            lines.append(f"| {case} | {mode} | {v['rmse_m']:.5f} | {v['seconds']:.2f} | {v['fit_calls']:.1f} | {v['rejected_frames']:.1f} |")
    text='''# Adaptacyjny zegar i sito przed RADAR-TRACKING

Zaimplementowano trzy warianty: standard; zegar i sito z regularnym dopasowaniem; adaptacyjne przełączanie do standardu po stabilizacji amplitudy. Po przełączeniu tani monitor wciąż sprawdza amplitudę. Przy jej niezgodności sito wraca natychmiast, a dopasowanie zegara ma ograniczoną częstość.

**To pilot syntetyczny, nie test na prawdziwym radarze.** Sito amplitudowe odrzuca detekcję, jeśli jej amplituda odbiega od przewidywanej. To nowa opcjonalna warstwa przed trackerem; istniejące geometryczne TRM pozostaje włączone we wszystkich wariantach. Amplituda musi pochodzić od tego samego obiektu, nie rozwiązano asocjacji amplitud wielu obiektów.

## Wyniki

Średnia z dwóch ziaren; 480 klatek w każdym przebiegu. RMSE obejmuje także odrzucone klatki: zamiast znikać z oceny, otrzymują predykcję geometryczną trackera. Czas obejmuje cały przebieg, w tym dopasowania; pojedynczy pomiar na wariant, więc jest orientacyjny.

| Scenariusz | Wariant | RMSE pozycji [m] | Czas [s] | Dopasowania zegara | Odrzucone klatki |
|---|---|---:|---:|---:|---:|
'''+ '\n'.join(lines)+'''

Scenariusze: `clean` — bez dodatkowych zakłóceń; `correlated` — błąd amplitudy i pozycji jednocześnie; `amplitude_only` — błąd amplitudy przy poprawnej pozycji; `position_only` — błąd pozycji bez ostrzeżenia w amplitudzie.

## Jak interpretować

Warstwa może pomóc tylko przy odpowiednim związku między jakością amplitudy i pozycji. Sama niezgodność amplitudy nie dowodzi złej pozycji. Kontrola amplitude_only pokazuje koszt odrzucania poprawnych detekcji; position_only pokazuje ograniczenie obserwowalności. Nie wolno wybierać wyłącznie korzystnego scenariusza i deklarować ogólnej poprawy.

Generator okresowości należy do rodziny modelu zegara; granice wyszukiwania podano z góry. Sprawdzono mały zbiór z pojedynczym, wolno poruszającym się obiektem. To nie pomiar obrotów wirnika, nie wyznaczanie prędkości postępowej z błysku, nie dowód skuteczności na dronach. Nie dostrajano parametrów po wynikach.

Monitor i sito są przyczynowe: decyzja dla bieżącej próbki używa dopasowania z przeszłości. Sam optymalizator pracuje na minionym oknie i może zatrzymać obsługę strumienia na kilka sekund. Mały łączny koszt lub przepustowość nie oznacza gwarancji czasu rzeczywistego. Zegar wygasa, żeby stara prognoza nie była używana bez końca.

## Odtwarzanie i testy

Z katalogu repo: `python -m unittest clock_experiment.test_track_clock clock_experiment.test_adaptive -v`; `python -m clock_experiment.run_adaptive`; `python -m clock_experiment.report_adaptive`. Benchmark chroni istniejący summary.json przed nadpisaniem. Protokół: ADAPTIVE_PROTOCOL.md; kod: adaptive.py i run_adaptive.py. Wszystkie 24 przebiegi i predykcje zapisano w adaptive_results.

Siedem testów jednostkowych integracji i przełączania przeszło. W tym etapie pełny pytest był niedostępny z powodu odmowy odczytu jego lokalnych plików; nie przedstawiamy poprzednich 44 testów jako ponownego uruchomienia obecnej wersji. Rdzenia geometrycznego nie zmieniono. Wcześniej ujawniony brak data.validate_on_real_trips w repo bazowym pozostaje osobnym ograniczeniem.
'''
    correlated=s['correlated']; clean=s['clean']; negative=s['amplitude_only']
    conclusion=(f"\nNajważniejszy wynik: przy wspólnym zakłóceniu amplitudy i pozycji RMSE wynosi "
                f"{correlated['standard']['rmse_m']:.4f} m (standard), "
                f"{correlated['always']['rmse_m']:.4f} m (stałe dopasowanie) i "
                f"{correlated['adaptive']['rmse_m']:.4f} m (adaptacyjne). "
                f"W spokojnym sygnale liczba dopasowań spada z {clean['always']['fit_calls']:.1f} "
                f"do {clean['adaptive']['fit_calls']:.1f}. Jednak przy błędzie samej amplitudy "
                f"wariant adaptacyjny ma RMSE {negative['adaptive']['rmse_m']:.4f} m wobec "
                f"{negative['standard']['rmse_m']:.4f} m standardu. "
                "**Nie ma podstaw do domyślnego włączenia sita amplitudy dla dowolnego radaru.**\n")
    text=text.replace('## Wyniki',conclusion+'\n## Wyniki',1)
    (ROOT/'ADAPTIVE_WYNIK.md').write_text(text,encoding='utf-8')
    (folder/'verification.json').write_text(json.dumps({'runs_verified':len(r['runs']),
        'all_frames_scored':True,'code_and_protocol_hashes_match':True},indent=2))
    cases=list(s); x=np.arange(len(cases)); fig,axes=plt.subplots(1,2,figsize=(12,4.7))
    for j,(mode,color) in enumerate([('standard','#808080'),('always','#d88c25'),('adaptive','#167ea8')]):
        for ax,key in zip(axes,('rmse_m','seconds')):
            ax.bar(x+(j-1)*.24,[s[c][mode][key] for c in cases],.24,label=mode,color=color)
    for ax in axes:
        ax.set_xticks(x,cases,rotation=15); ax.legend()
    axes[0].set_ylabel('Position RMSE (m)'); axes[1].set_ylabel('Total runtime (s)')
    fig.suptitle('Synthetic switching pilot: means of 2 seeds, not real radar')
    fig.tight_layout(); fig.savefig(ROOT/'adaptive_comparison.png',dpi=160); plt.close(fig)
    print('Verified',len(r['runs']),'runs. Report saved.')

if __name__=='__main__': main()
