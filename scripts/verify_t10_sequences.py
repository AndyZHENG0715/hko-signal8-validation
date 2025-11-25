import csv
from datetime import datetime

def analyze(path):
    rows=list(csv.DictReader(open(path)))
    consec=0
    seqs=[]
    current_start=None
    for r in rows:
        t=datetime.strptime(r['datetime'],'%Y-%m-%d %H:%M:%S')
        val=(r['t10_meets_t8_coverage']=='True')
        if val:
            if current_start is None:
                current_start=t
            consec+=1
        else:
            if consec>0:
                seqs.append((current_start, consec))
            consec=0
            current_start=None
    if consec>0:
        seqs.append((current_start, consec))
    return seqs

if __name__=='__main__':
    path='reports/ragasa_validation/t10_analysis.csv'
    seqs=analyze(path)
    print('sequences (start,count):')
    for s,c in seqs:
        print(s.strftime('%Y-%m-%d %H:%M'), c)
    print('any >=3?', any(c>=3 for _,c in seqs))
