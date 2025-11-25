import csv
from datetime import datetime

def analyze(path):
    rows=list(csv.DictReader(open(path)))

    in_t10_rows=[r for r in rows if r['in_T10_window']=='True']
    count_in_t10=len(in_t10_rows)
    persistent_in_t10=[r for r in in_t10_rows if r.get('persistent_T8','False')=='True']
    consec_ge3_in_t10=[r for r in in_t10_rows if int(float(r.get('consecutive_periods_above_T8',0)))>=3]
    return count_in_t10, len(persistent_in_t10), len(consec_ge3_in_t10), persistent_in_t10[:5], consec_ge3_in_t10[:5]

if __name__=='__main__':
    path='reports/ragasa_validation/time_summary.csv'
    count_in_t10, n_persistent, n_consec_ge3, persistent_rows, consec_rows = analyze(path)
    print('in_T10 count:', count_in_t10)
    print('persistent_T8 rows in T10:', n_persistent)
    print('consecutive_periods_above_T8 >=3 in T10:', n_consec_ge3)
    if n_persistent>0:
        print('sample persistent rows:', persistent_rows)
    if n_consec_ge3>0:
        print('sample >=3 consec rows:', consec_rows)
