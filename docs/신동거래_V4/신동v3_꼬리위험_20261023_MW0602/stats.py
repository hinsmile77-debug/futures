import json,sys
R=json.load(open(sys.argv[1],encoding='utf-8'))
rows,T=R['rows'],R['trades']
PTV=50000;CAP=15_000_000
def st(who,ds):
    tr=[t for t in T if t['who']==who and t['d'] in ds]
    pts=[t['pt'] for t in tr]; w=[p for p in pts if p>0]; l=[p for p in pts if p<=0]
    key='m_pt' if who=='MAIN' else 'ai_pt'
    daily=[r[key] for r in rows if r['d'] in ds]
    cum=0;pk=0;mdd=0
    for x in daily: cum+=x;pk=max(pk,cum);mdd=max(mdd,pk-cum)
    return dict(n=len(tr),win=f"{len(w)}/{len(tr)} ({100*len(w)/max(1,len(tr)):.0f}%)",sum=round(sum(pts),2),avg=round(sum(pts)/max(1,len(tr)),2),
        pf=round(sum(w)/abs(sum(l)),2) if l and sum(l)!=0 else None, avgw=round(sum(w)/max(1,len(w)),2), avgl=round(sum(l)/max(1,len(l)),2),
        posdays=f"{sum(x>0 for x in daily)}/{len(daily)}", best=max(daily), worst=min(daily), mdd=round(mdd,2),
        krw=round(sum(pts)*PTV), ret=round(sum(pts)*PTV/CAP*100,2))
alld=[r['d'] for r in rows]
for name,ds in [('전체 10/07-10/23',alld),('v3 표본 밖 10/19-10/23',[d for d in alld if d>='2026-10-19']),('v3 표본 안 10/07-10/16',[d for d in alld if d<'2026-10-19']),('공식창 10/21-',[d for d in alld if d>='2026-10-21'])]:
    print(name); print(' MAIN',st('MAIN',ds)); print(' AI  ',st('AI',ds))
# 방향 적중
for r in rows:
    print(r['d'],r['act'],'MAIN첫',r['m_first'],r['m_first']==r['act'],'AI장전',r['ai_pm'],r['ai_pm_hit'],'AI익일',r['ai_on'],r['ai_on_hit'])
print('MAIN첫방향 적중', sum(r['m_first']==r['act'] for r in rows), '/', len(rows))
print('AI장전 적중', sum(bool(r['ai_pm_hit']) for r in rows), '/', len(rows))
print('AI익일 적중', sum(bool(r['ai_on_hit']) for r in rows), '/', sum(r['ai_on']!='—' for r in rows))
# per-trade 방향: 진입방향이 그날 실제방향과 같은 비율
for who in ('MAIN','AI'):
    tr=[t for t in T if t['who']==who]; act={r['d']:r['act'] for r in rows}
    print(who,'거래방향=일방향', sum(t['side']==act[t['d']] for t in tr),'/',len(tr))
    for side in ('매수','매도'):
        s=[t['pt'] for t in tr if t['side']==side]; print('  ',side,len(s),round(sum(s),2))
    rs={}
    for t in tr: rs.setdefault(t['rule'],[]).append(t['pt'])
    print('  by rule',{k:(len(v),round(sum(v),2)) for k,v in rs.items()})
    ws={}
    for t in tr: ws.setdefault(t['why'],[]).append(t['pt'])
    print('  by exit',{k:(len(v),round(sum(v),2)) for k,v in ws.items()})
