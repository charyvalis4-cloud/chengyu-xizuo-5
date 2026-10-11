# -*- coding: utf-8 -*-
import html, re, os, sys
sys.path.insert(0,'.')
from e4 import E, BUTIE
import content5 as C
from gen5 import SEC7, SEC8, split
L="ABCD"
esc=html.escape
N=len(E)
OUT="/home/claude/out5"; os.makedirs(OUT,exist_ok=True)
TITLE="成語習作 第5回（中學生）"

# ---------- 共用：題目資料 (kind, stem, opts, ans, extra) ----------
def mc(stem,opts,a,ansfull=None): return dict(k='mc',stem=stem,opts=opts,a=a,ans=ansfull or L[a])
sections=[]
sections.append(("一、字形測驗","選出符合注音的正確字形（「」內為注音）",[mc(s,o,a,"%s %s"%(L[a],o[a])) for s,o,a in C.ZIXING]))
sections.append(("二、綜合測驗","",[mc(s,o,a) for s,o,a in C.ZONGHE]))
ex=C.TIHUAN_EX
sections.append(("三、成語替換","將「　」內的詞語以適當的成語做替換（直接輸入四字成語）。例：%s ……（%s）"%(ex[0],ex[1]),[dict(k='word',stem=s,answer=w,ans=w) for s,w in C.TIHUAN]))
sections.append(("四、成語運用","",[mc(s,o,a) for s,o,a in C.YUNYONG]))
cl=C.CLOZE; i=0
while '{}' in cl:
    i+=1; cl=cl.replace('{}','（%d）'%i,1)
C.PASSAGE=[cl]
sections.append(("五、出口成章","從下面的成語中選出適當的填入短文的空格（直接輸入四字成語）。成語庫："+"、".join(C.BANK),[dict(k='word',stem="（%d）"%(j+1),answer=w,ans=w) for j,w in enumerate(C.BLANK_ANS)]))
lp=C.LIANPU_EX
sections.append(("六、成語臉譜","依提示選出適當的成語。例：%s：%s → %s"%(lp[0],"、".join(lp[1]),lp[1][lp[2]]),[mc("提示：%s"%h,o,a,"%s %s"%(L[a],o[a])) for h,o,a in C.LIANPU]))
sections.append(("七、例句應用題（每個成語一題）","選出最適合填入□□□□的成語",[mc(s,o,a) for s,o,a in SEC7]))
sections.append(("八、綜合練習題（每個成語一題）","",[mc(s,o,a) for s,o,a in SEC8]))
TOTAL=sum(len(s[2]) for s in sections)

def card_fields(e):
    f=[("解釋",e['jie'],""),("例句",e['li'],"")]
    if e['xs']: f.append(("相似",e['xs'],"s"))
    if e['xf']: f.append(("相反",e['xf'],"o"))
    for k,v in e['extra']: f.append((k,v,"d"))
    if e['name'] in C.NOTES: f.append(("補充",C.NOTES[e['name']],"d"))
    return f

# ======================= 互動版 =======================
def html_mc(i,q):
    h='<div class="q" data-a="%s" data-alt="" data-ans="%s"><p>%d. %s</p><div class="opts">'%(L[q['a']],esc(q['ans']),i,esc(q['stem']))
    for j,o in enumerate(q['opts']): h+='<button type="button" class="opt" data-v="%s">(%s) %s</button>'%(L[j],L[j],esc(o))
    return h+'</div><div class="fb"></div></div>'
def html_fill(i,q):
    parts=q['tpl'].split('{}'); h='<p>%d. '%i
    for j,p in enumerate(parts):
        h+=esc(p)
        if j<len(parts)-1: h+='<input type="text" maxlength="2" size="3" autocomplete="off">'
    return '<div class="q" data-a="%s" data-alt="" data-ans="%s">%s</p><div class="fb"></div></div>'%("|".join(q['answers']),esc(q['ans']),h)
def html_word(i,q):
    return '<div class="q" data-a="%s" data-alt="" data-ans="%s"><p>%d. %s → <input type="text" maxlength="8" size="10" autocomplete="off"></p><div class="fb"></div></div>'%(q['answer'],esc(q['ans']),i,esc(q['stem']))

CSS=open('/home/claude/gs/guwen-site/idioms/xizuo-3/index.html',encoding='utf8').read()
css=CSS[CSS.find('<style>'):CSS.find('</style>')+8]
js=CSS[CSS.find('<script>'):]
js=re.sub(r'T=\d+;','T=%d;'%TOTAL,js,1)
assert 'T=%d;'%TOTAL in js

def build_index():
    h='<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>成語習作 第5回｜互動版</title>\n'+css+'</head>\n'
    h+='<body><main>\n<p><a href="../">← 成語典故</a>　<a href="static.html">講義版（可列印）</a></p><h1>%s</h1>'%TITLE
    h+='<p>%d 個成語學習站（另有 %d 個老師補充成語、年齡篇成語大補帖）、字形測驗、綜合測驗、成語替換、成語運用、出口成章、成語臉譜，以及每個成語各一題的例句應用題與綜合練習題。直接點選或輸入作答。</p>\n'%(N,len(C.EXTRA))
    h+='<nav><a href="#learn">成語學習站</a><a href="#test">實力挑戰</a><a href="#answers">參考答案</a><a href="#dl">下載 Word</a></nav>\n'
    h+='<p>班級：<input size="6"> 座號：<input size="4"> 姓名：<input size="8"></p>\n'
    h+='<div class="bar"><label><input type="radio" name="m" value="live" checked> 即時對答案</label><label><input type="radio" name="m" value="sub"> 交卷模式</label>\n<span id="sc">已作答 0／%d　答對 0</span><button class="btn" id="go" type="button" hidden>交卷送出</button><button class="btn" id="rs" type="button">重新作答</button></div>\n'%TOTAL
    h+='<h2 id="learn">成語學習站（共 %d 個）</h2><div class="grid">'%N
    for i,e in enumerate(E,1):
        h+='<div class="card"><h3><span>%d</span>%s</h3>'%(i,esc(e['name']))
        for k,v,c in card_fields(e):
            if k in ("辨析","典故","歇後語","猜謎","俗諺","補充"): h+='<p class="dn"><b class="k d">%s</b>%s</p>'%(k,esc(v))
            else: h+='<p><b class="k%s">%s</b>%s</p>'%((' '+c) if c else '',k,esc(v))
        h+='</div>'
    h+='</div><h3>★ 老師補充成語</h3><div class="grid">'
    for x in C.EXTRA:
        h+='<div class="card star"><h3><span>★</span>%s</h3><p><b class="k">解釋</b>%s</p>'%(esc(x['name']),esc(x['jie']))
        if x['xs']: h+='<p><b class="k s">相似</b>%s</p>'%esc(x['xs'])
        h+='<p class="dn"><b class="k d">補充</b>講義手寫標註（見上方對應成語）。</p><p class="dn"><b class="k d">備註</b>%s</p></div>'%esc(x['note'])
    h+='</div><h3>成語大補帖：%s</h3><div class="card">'%esc(BUTIE[0])
    for k,v in BUTIE[1]: h+='<p><b class="k">%s</b>%s</p>'%(esc(k),esc(v))
    h+='</div>\n<h2 id="test">實力挑戰</h2>'
    n=0
    for title,note,qs in sections:
        h+='<h3>%s</h3>'%esc(title)
        if note: h+='<p class="nt">%s</p>'%esc(note)
        if title.startswith("五"):
            h+='<div class="card pass">'+''.join('<p>%s</p>'%esc(p) for p in C.PASSAGE)+'</div>'
        for q in qs:
            n+=1
            h+={'mc':html_mc,'fill':html_fill,'word':html_word}[q['k']](n if True else n,q)
    # 題號：各節重新編號
    h=h  # numbering handled below
    return h

# 各節重新編號版本
def build_index2():
    h='<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>成語習作 第5回｜互動版</title>\n'+css+'</head>\n'
    h+='<body><main>\n<p><a href="../">← 成語典故</a>　<a href="static.html">講義版（可列印）</a></p><h1>%s</h1>'%TITLE
    h+='<p>%d 個成語學習站（另有 %d 個老師補充成語、年齡篇成語大補帖）、字形測驗、綜合測驗、成語替換、成語運用、出口成章、成語臉譜，以及每個成語各一題的例句應用題與綜合練習題。直接點選或輸入作答。</p>\n'%(N,len(C.EXTRA))
    h+='<nav><a href="#learn">成語學習站</a><a href="#test">實力挑戰</a><a href="#answers">參考答案</a><a href="#dl">下載 Word</a></nav>\n'
    h+='<p>班級：<input size="6"> 座號：<input size="4"> 姓名：<input size="8"></p>\n'
    h+='<div class="bar"><label><input type="radio" name="m" value="live" checked> 即時對答案</label><label><input type="radio" name="m" value="sub"> 交卷模式</label>\n<span id="sc">已作答 0／%d　答對 0</span><button class="btn" id="go" type="button" hidden>交卷送出</button><button class="btn" id="rs" type="button">重新作答</button></div>\n'%TOTAL
    h+='<h2 id="learn">成語學習站（共 %d 個）</h2><div class="grid">'%N
    for i,e in enumerate(E,1):
        h+='<div class="card"><h3><span>%d</span>%s</h3>'%(i,esc(e['name']))
        for k,v,c in card_fields(e):
            if k in ("辨析","典故","歇後語","猜謎","俗諺","補充"): h+='<p class="dn"><b class="k d">%s</b>%s</p>'%(k,esc(v))
            else: h+='<p><b class="k%s">%s</b>%s</p>'%((' '+c) if c else '',k,esc(v))
        h+='</div>'
    h+='</div><h3>★ 老師補充成語</h3><div class="grid">'
    for x in C.EXTRA:
        h+='<div class="card star"><h3><span>★</span>%s</h3><p><b class="k">解釋</b>%s</p>'%(esc(x['name']),esc(x['jie']))
        if x['xs']: h+='<p class="k-line"><b class="k s">相似</b>%s</p>'%esc(x['xs'])
        h+='<p class="dn"><b class="k d">備註</b>%s</p></div>'%esc(x['note'])
    h+='</div><h3>成語大補帖：%s</h3><div class="card">'%esc(BUTIE[0])
    for k,v in BUTIE[1]: h+='<p><b class="k">%s</b>%s</p>'%(esc(k),esc(v))
    h+='</div>\n<h2 id="test">實力挑戰</h2>'
    for title,note,qs in sections:
        h+='<h3>%s</h3>'%esc(title)
        if note: h+='<p class="nt">%s</p>'%esc(note)
        if title.startswith("五"):
            h+='<div class="card pass">'+''.join('<p>%s</p>'%esc(p) for p in C.PASSAGE)+'</div>'
        for i,q in enumerate(qs,1):
            h+={'mc':html_mc,'fill':html_fill,'word':html_word}[q['k']](i,q)
    h+='<h2 id="answers">參考答案</h2><details><summary>顯示參考答案（老師用）</summary>'+answers_html()+'</details>'
    h+='<h2 id="dl">下載 Word 檔</h2><div class="dl"><a href="xizuo-5-handout.docx">📄 標準版 Word 檔（黑白，適合列印）</a><a href="xizuo-5-handout-color.docx">🎨 彩色版 Word 檔（內容相同，依單元上色）</a></div>\n</main>\n'
    h+=js
    return h

def answer_lines():
    out=[]
    for title,note,qs in sections:
        t=title.split('、',1)[1].split('（')[0]
        if title.startswith('一'): s="　".join("%d.%s"%(i,q['ans']) for i,q in enumerate(qs,1))
        elif title.startswith('三') or title.startswith('六'): s="　".join("%d.%s"%(i,q['ans']) for i,q in enumerate(qs,1))
        else: s="　".join("%d.%s"%(i,q['ans']) for i,q in enumerate(qs,1))
        out.append((t,s))
    return out
NOTE_ANS="註：講義本身沒有附答案，以上為編者依題意解答，請老師核對。六、成語臉譜第 5 題「驚駭」以「毛骨悚然」為答（「戰戰兢兢」較偏向戒慎恐懼）。五、出口成章的空格位置為編者依講義排版辨識，答案以文意判斷。七、八兩節為仿第 1 回自動產生的延伸練習。老師補充成語的解釋，除「鳥盡弓藏」取自講義第 6 回外，均為編者依通行釋義補上。"
def answers_html():
    return ''.join('<p>%s：%s</p>'%(esc(t),esc(s)) for t,s in answer_lines())+'<p class="nt">%s</p>'%esc(NOTE_ANS)

# ======================= 講義版 =======================
def build_static():
    h='<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>成語習作 第5回｜講義版</title>\n'
    h+='<style>body{font:15px/1.7 "Noto Sans TC","Microsoft JhengHei",sans-serif;color:#000;background:#fff;max-width:820px;margin:auto;padding:16px}h1,h2{color:#1f5c5a}.c{break-inside:avoid;margin:8px 0;padding:6px 0;border-bottom:1px solid #ccc}.q{break-inside:avoid;margin:6px 0}.o{margin:0 0 4px 1.5em}.pb{break-before:page}@media print{.np{display:none}}</style></head><body>\n'
    h+='<p class="np"><a href="../">← 成語典故</a>　<a href="./">互動版</a>　<a href="xizuo-5-handout.docx">Word 講義</a>　<a href="xizuo-5-handout-color.docx">Word 講義（彩色版）</a></p>\n'
    h+='<h1>%s</h1><p>班級：＿＿＿＿　座號：＿＿＿＿　姓名：＿＿＿＿＿＿　得分：＿＿＿＿</p>\n<h2>壹、成語學習站</h2>'%TITLE
    for i,e in enumerate(E,1):
        h+='<div class="c"><b>%d %s</b>'%(i,esc(e['name']))
        for k,v,c in card_fields(e): h+='<br>%s：%s'%(k,esc(v))
        h+='</div>'
    h+='<h3>★ 老師補充成語</h3>'
    for x in C.EXTRA:
        h+='<div class="c"><b>★ %s</b><br>解釋：%s'%(esc(x['name']),esc(x['jie']))
        if x['xs']: h+='<br>相似：%s'%esc(x['xs'])
        h+='<br>備註：%s</div>'%esc(x['note'])
    h+='<h3>成語大補帖：%s</h3>'%esc(BUTIE[0])+''.join('<div>%s：%s</div>'%(esc(k),esc(v)) for k,v in BUTIE[1])
    h+='<h2 class="pb">貳、實力挑戰</h2>'
    for title,note,qs in sections:
        h+='<h3>%s</h3>'%esc(title)
        if note: h+='<p>%s</p>'%esc(note)
        if title.startswith("五"): h+=''.join('<p style="text-indent:2em">%s</p>'%esc(p) for p in C.PASSAGE)
        for i,q in enumerate(qs,1):
            if q['k']=='mc':
                h+='<div class="q">（　）%d. %s'%(i,esc(q['stem']))
                h+='<br>'+'　'.join('(%s) %s'%(L[j],esc(o)) for j,o in enumerate(q['opts']))+'</div>' if all(len(o)<=8 for o in q['opts']) else ''.join('<div class="o">(%s) %s</div>'%(L[j],esc(o)) for j,o in enumerate(q['opts']))+'</div>'
            elif q['k']=='fill':
                h+='<div class="q">%d. %s</div>'%(i,esc(q['tpl'].replace('{}','（　）')))
            else:
                h+='<div class="q">%d. %s → （　　　　　　）</div>'%(i,esc(q['stem']))
    h+='<h2 class="pb">參考答案</h2>'+answers_html()+'</body></html>'
    return h

open(OUT+'/index.html','w',encoding='utf8').write(build_index2())
open(OUT+'/static.html','w',encoding='utf8').write(build_static())
import pickle
pickle.dump(dict(sections=sections,TOTAL=TOTAL),open(OUT+'/data.pkl','wb'))
print("TOTAL",TOTAL, [len(s[2]) for s in sections])
