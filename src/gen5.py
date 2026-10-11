# -*- coding: utf-8 -*-
import random, re
from e4 import E
import content5 as C
L="ABCD"
names=[e['name'] for e in E]
def split(s): return [x for x in re.split(r'[\s　]+',s) if x]

# ---- 第七節 例句應用題 ----
RISK={"一手遮天":["欲蓋彌彰","銷聲匿跡"],"欲蓋彌彰":["一手遮天","文過飾非"],"文過飾非":["欲蓋彌彰"],"游手好閒":["無病呻吟"],"趨炎附勢":["毛遂自薦"],"侃侃而談":["調嘴弄舌"],"調嘴弄舌":["侃侃而談"]}
def related(e):
    r=set(split(e['xs'])+split(e['xf']))
    for k,v in e['extra']:
        r|=set(re.findall(r'[一-鿿]{4}',v)) if k=="辨析" else set()
    r|=set(RISK.get(e['name'],[]))
    return r
rng=random.Random(2026104)
SEC7=[]
for i,e in enumerate(E):
    assert e['name'] in e['li'], e['name']
    stem=e['li'].replace(e['name'],'□□□□',1)
    rel=related(e)
    pool=[n for n in names if n!=e['name'] and n not in rel and n not in stem]
    d=rng.sample(pool,3)
    pos=rng.randrange(4)
    opts=d[:]; opts.insert(pos,e['name'])
    SEC7.append((stem,opts,pos))
# ---- 第八節 綜合練習題 ----
SEC8=[]
for i,e in enumerate(E):
    n=i+1
    xf=split(e['xf']); xs=split(e['xs'])
    rel=related(e)
    pool=[x for x in names if x!=e['name'] and x not in rel]
    if n%2==0 and xf:
        ans=xf[0]; d=[x for x in rng.sample(pool,3)]
        pos=rng.randrange(4); opts=d[:]; opts.insert(pos,ans)
        SEC8.append(("下列哪一個成語，與「%s」的意思相反？"%e['name'],opts,pos))
    elif n%2==0 and xs:
        ans=xs[0]; d=rng.sample(pool,3)
        pos=rng.randrange(4); opts=d[:]; opts.insert(pos,ans)
        SEC8.append(("下列哪一個成語，與「%s」的意思相近？"%e['name'],opts,pos))
    else:
        others=[x for x in E if x['name']!=e['name'] and x['jie']!=e['jie']]
        d=[o['jie'] for o in rng.sample(others,3)]
        pos=rng.randrange(4); opts=d[:]; opts.insert(pos,e['jie'])
        SEC8.append(("「%s」的意思是："%e['name'],opts,pos))
if __name__=="__main__":
    for q in SEC7: print(q[0],'|',q[1],L[q[2]])
    print()
    for q in SEC8[:14]: print(q[0],'|',[o[:14] for o in q[1]],L[q[2]])
