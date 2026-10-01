import json
import numpy as np
from run_angle import ROOT,digest
from frequency_selector import FrequencySelector

def main():
    selection=json.loads((ROOT/'selector_thresholds.json').read_text(encoding='utf-8'))
    r=json.loads((ROOT/'selector_results.json').read_text(encoding='utf-8'))
    assert r['thresholds_sha256']==digest(ROOT/'selector_thresholds.json')
    assert r['iq_sha256']==digest(ROOT/'selector_iq.npz')
    for name,value in selection['hashes'].items():
        assert digest(ROOT/name)==value
    for row in r['runs']:
        for method,out in row['outcomes'].items():
            detected=out['score']>selection['thresholds'][method]
            localized=abs(np.rad2deg(out['angle']-row['truth']['weak_angle']))<=.25 and abs(out['dr']-row['truth']['dr'])<=.015
            assert out['detected']==bool(detected)
            assert out['weak_correct']==bool(detected and localized and row['kind']=='weak')
    model=FrequencySelector(); replay_count=0
    with np.load(ROOT/'selector_iq.npz',allow_pickle=False) as data:
        for row in r['runs']:
            if row['seed'] not in (0,9,99):
                continue
            out=model.scores(data[row['iq_key']]); replay_count+=1
            for method,value in out.items():
                assert value=={k:row['outcomes'][method][k] for k in value}
    # Descriptive ROC point, calculated after evaluation; never used as deployment threshold.
    roc={}
    controls=[row for row in r['runs'] if row['kind']=='strong_only']
    weak=[row for row in r['runs'] if row['kind']=='weak']
    for method in ('coherent','band_power'):
        threshold=sorted(row['outcomes'][method]['score'] for row in controls)[-6]
        detected=[row for row in weak if row['outcomes'][method]['score']>threshold]
        correct=[]
        for row in detected:
            v=row['outcomes'][method]
            if abs(np.rad2deg(v['angle']-row['truth']['weak_angle']))<=.25 and abs(v['dr']-row['truth']['dr'])<=.015:
                correct.append(row)
        roc[method]=dict(threshold=threshold,false_alarms=sum(row['outcomes'][method]['score']>threshold for row in controls),
                         weak_correct=len(correct),same_range_correct=sum(row['dr']==0 for row in correct))
    analysis=dict(descriptive_equal_false_alarm=roc,notice='Post-hoc ROC on evaluation set, not independently validated thresholds')
    (ROOT/'selector_roc_analysis.json').write_text(json.dumps(analysis,indent=2),encoding='utf-8')
    lines=['# Selektor zgodności fazy i częstotliwości', '',
           '**Wniosek:** zachowanie wspólnej fazy po paśmie pomaga w tym modelu wykrywać słabe echo z innym opóźnieniem. Nie wykazano równie mocnej korzyści dla celu o tej samej odległości. Ustalony próg selektora spójnego nie utrzymał testowego limitu 5% fałszywych alarmów, więc ten wariant pozostaje eksperymentalny.', '',
           '9 częstotliwości, dwa RX, te same I/Q dla obu metod. Słabe echo ma 15% amplitudy silnego (2.25% mocy). Dopasowanie silnego wzorca i jego projekcja, następnie test słabych wzorców. Wzorce z utratą ponad 95% energii są wykluczone. Wspólne ważenie impulsów zachowuje fazę kanałów. Porównanie: selektor spójny po paśmie vs suma mocy dopasowań pasm bez wspólnej fazy.', '',
           '## Progi ustalone przed oceną', '',
           '100 rozwojowych kontroli ustaliło próg 95. percentyla maksimum po wszystkich kandydatach. Później 100 nowych kontroli silny-bez-słabego, 100 pustych i 60 par. Połowa z impulsami. Próg nie był zmieniany po ocenie.', '',
           '| Metoda | Fałszywe alarmy: silny bez słabego / 100 | Puste / 100 | Poprawnie wykryte słabe / 60 | Ta sama odległość / 20 |','|---|---:|---:|---:|---:|']
    for method in ('coherent','band_power'):
        s=r['summary']
        lines.append(f"| {method} | {s['strong_only']['metrics'][method]['detected']} | {s['empty']['metrics'][method]['detected']} | {s['weak']['metrics'][method]['weak_correct']} | {s['weak_by_range']['0.0'][method]} |")
    lines+=['', 'Fałszywe alarmy nie są jednakowe, więc 36 vs 1 poprawnych detekcji nie jest dowodem przewagi przy tym samym ustalonym FPR. Próg z tylko 100 kontroli nie gwarantuje FPR na nowej próbie.', '',
            '## Opisowe porównanie przy równym obserwowanym FPR', '',
            'Dodatkowo po wyniku wyznaczono punkt ROC: próg każdej metody daje 5 alarmów na tych samych 100 testowych kontrolach. Jest to analiza opisowa tej próby, nie niezależna walidacja nowych progów. Nie zapisujemy ich jako konfiguracji detektora.', '',
            '| Metoda | Alarmy / 100 | Poprawne słabe / 60 | Ta sama odległość / 20 |','|---|---:|---:|---:|']
    for method,v in roc.items():
        lines.append(f"| {method} | {v['false_alarms']} | {v['weak_correct']} | {v['same_range_correct']} |")
    lines+=['', 'Korzyść przy różnym opóźnieniu oznacza wykorzystanie informacji o odległości w fazie pasma. Nie utożsamiamy jej z poprawą rozdzielczości kąta. Suma mocy pasm usuwa tę informację i nie jest porównaniem ze wszystkimi standardowymi procesorami radarowymi.', '',
            'Model zakłada jedną zespoloną amplitudę celu po całym paśmie, idealną fazę i znaną wiązkę. Rzeczywisty cel, kanał lub wielodrogowość mogą naruszyć te założenia. Filtr badano tylko przy szumie i impulsach. Nie ma podstaw do deklaracji gotowości sprzętowej.', '',
            f'4 testy przeszły. Ponownie obliczono decyzje 260 testowych scen, sprawdzono hashe i odtworzono {replay_count} zestawów wyników selektora z zapisanych I/Q.', '',
            'Odtwarzanie: python -m unittest test_frequency_selector -v; python report_selector.py. python run_selector.py chroni istniejące progi i wyniki.']
    (ROOT/'WYNIK_SELECTOR.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(roc,indent=2)); print('Verified 260 decisions; I/Q replays:',replay_count)

if __name__=='__main__':
    main()
