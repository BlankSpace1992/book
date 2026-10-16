# -*- coding: utf-8 -*-
"""Pass 2: sentence rhythm, paragraphs, dialogue share, classical-function-word density."""
import re, json, statistics as st
from pathlib import Path

A = Path(r'D:\Book\.analyze')
raw = (A/'chapters.txt').read_text(encoding='utf-8')
chunks = re.split(r'^===CH(\d+)\t(.*)$', raw, flags=re.M)
chapters = []
for i in range(1, len(chunks), 3):
    chapters.append({'n': int(chunks[i]), 'title': chunks[i+1], 'text': chunks[i+2].strip()})
print('chapters', len(chapters))

CN = re.compile(r'[\u4e00-\u9fff]')
def han(s): return len(CN.findall(s))

# ---------- sentences ----------
ENDS = '。！？…'
SPLIT = re.compile(r'[。！？]+|…{2,}')
all_sent, chap_sent = [], {}
for c in chapters:
    t = c['text']
    parts = [p for p in SPLIT.split(t) if han(p) > 0]
    all_sent.extend(parts)
    chap_sent[c['n']] = parts
sl = [han(p) for p in all_sent]
print('sentences', len(sl), 'avg sent len', round(sum(sl)/len(sl),2), 'median', st.median(sl))
print('p90', sorted(sl)[int(len(sl)*.9)], 'p99', sorted(sl)[int(len(sl)*.99)], 'max', max(sl))
hist = {}
for v in sl:
    k = ('1-5' if v<=5 else '6-10' if v<=10 else '11-20' if v<=20 else
         '21-30' if v<=30 else '31-50' if v<=50 else '51+')
    hist[k] = hist.get(k,0)+1
tot_s = len(sl)
print('sent len dist', {k: (hist.get(k,0), round(100*hist.get(k,0)/tot_s,1)) for k in
      ['1-5','6-10','11-20','21-30','31-50','51+']})

# ---------- clauses (comma-split) ----------
all_clause = []
for c in chapters:
    for body in c['text'].split('\n'):
        for cl in re.split(r'[，。！？；：、…]+', body):
            h = han(cl)
            if h: all_clause.append(h)
cl = all_clause
print('clauses', len(cl), 'avg clause', round(sum(cl)/len(cl),2), 'median', st.median(cl))
chist = {}
for v in cl:
    k = ('1-2' if v<=2 else '3-4' if v<=4 else '5-8' if v<=8 else '9-12' if v<=12
         else '13-20' if v<=20 else '21+')
    chist[k] = chist.get(k,0)+1
print('clause dist', {k:(chist.get(k,0), round(100*chist.get(k,0)/len(cl),1))
      for k in ['1-2','3-4','5-8','9-12','13-20','21+']})

# ---------- "碎句" run detection: 3+ consecutive clauses each <=4 han ----------
def clause_run_stats(t):
    runs = {'r3':0,'r4':0,'longest':0,'longest_txt':''}
    for line in t.split('\n'):
        segs = re.split(r'([，。！？；：、…]+)', line)
        clauses = segs[0::2]
        seps = segs[1::2]
        run, start, cur = 0, 0, []
        for idx, c in enumerate(clauses):
            h = han(c)
            if 0 < h <= 4:
                if run == 0: start = idx
                run += 1; cur.append(c.strip())
            else:
                if run >= 3:
                    runs['r3'] += 1
                    if run >= 4: runs['r4'] += 1
                    if run > runs['longest']:
                        runs['longest'] = run
                        runs['longest_txt'] = '，'.join(cur)
                run, cur = 0, []
        if run >= 3:
            runs['r3'] += 1
            if run >= 4: runs['r4'] += 1
            if run > runs['longest']:
                runs['longest'] = run; runs['longest_txt'] = '，'.join(cur)
    return runs
agg = {'r3':0,'r4':0,'longest':0,'longest_txt':''}
per_ch = {}
for c in chapters:
    r = clause_run_stats(c['text'])
    per_ch[c['n']] = r
    for k in ('r3','r4'):
        agg[k] += r[k]
    if r['longest'] > agg['longest']:
        agg['longest'] = r['longest']; agg['longest_txt'] = r['longest_txt']
print('short-clause runs(>=3 consecutive <=4han):', agg['r3'], '>=4:', agg['r4'],
      'per chapter avg', round(agg['r3']/len(chapters),2))
print('longest such run', agg['longest'], '|', agg['longest_txt'][:120])

# ---------- paragraphs ----------
para_len, per_ch_para = [], {}
for c in chapters:
    ps = [p for p in c['text'].split('\n') if han(p) > 0]
    per_ch_para[c['n']] = ps
    para_len.extend(han(p) for p in ps)
print('paragraphs', len(para_len), 'avg para', round(sum(para_len)/len(para_len),2),
      'median', st.median(para_len), 'max', max(para_len))
pl = sorted(para_len)
print('para p75', pl[int(len(pl)*.75)], 'p90', pl[int(len(pl)*.9)], 'p99', pl[int(len(pl)*.99)])
ph = {}
for v in para_len:
    k = ('1-10' if v<=10 else '11-20' if v<=20 else '21-40' if v<=40 else '41-60' if v<=60
         else '61-100' if v<=100 else '101-150' if v<=150 else '151+')
    ph[k] = ph.get(k,0)+1
print('para dist', {k:(ph.get(k,0), round(100*ph.get(k,0)/len(para_len),1)) for k in
      ['1-10','11-20','21-40','41-60','61-100','101-150','151+']})
print('avg paras/chapter', round(len(para_len)/len(chapters),1))

# ---------- dialogue ----------
DQ = re.compile(r'“([^”]*)”')
dl_tot, han_tot = 0, 0
per_ch_dl = {}
for c in chapters:
    t = c['text']
    d = sum(han(m) for m in DQ.findall(t))
    dl_tot += d; h = han(t); han_tot += h
    per_ch_dl[c['n']] = (d, h)
print('dialogue han', dl_tot, 'total han', han_tot,
      'dialogue share %', round(100*dl_tot/han_tot,2))
shares = [d/h for d,h in per_ch_dl.values() if h]
print('per-chapter dialogue share: median', round(100*st.median(shares),1),
      'p25', round(100*sorted(shares)[len(shares)//4],1),
      'p75', round(100*sorted(shares)[3*len(shares)//4],1))

# ---------- classical function words ----------
FW = ['之','其','乃','遂','皆','矣','乎','也','焉','耳','哉','夫','盖','尝','既','且','若','故','是以','于是','乎','邪','耶','兮','尔','汝','吾','某','厥','庶']
fw_cnt = {w: 0 for w in set(FW)}
for c in chapters:
    for w in fw_cnt:
        fw_cnt[w] += c['text'].count(w)
print('function-word counts (per 10k han):')
for w, v in sorted(fw_cnt.items(), key=lambda x:-x[1]):
    if v: print('   %s\t%d\t%.1f/万字' % (w, v, v/han_tot*10000))
core = ['之','其','乃','遂','皆','矣','乎','也']
core_tot = sum(fw_cnt[w] for w in core)
print('core8 total', core_tot, '密度 %.1f/万字' % (core_tot/han_tot*10000))
modern = ['的话','时候','什么','怎么','这个','那个','咱们','家伙','咱们','一下','其实','而且','但是','因为','所以','然后','东西','事情','问题','直接','根本','简直','居然','竟然','搞','弄','啥','呗','嘛','喽']
m_cnt = {w:0 for w in set(modern)}
for c in chapters:
    for w in m_cnt:
        m_cnt[w] += c['text'].count(w)
mt = sum(m_cnt.values())
print('modern markers total %d  %.1f/万字' % (mt, mt/han_tot*10000))
for w,v in sorted(m_cnt.items(), key=lambda x:-x[1])[:16]:
    if v: print('   %s\t%d' % (w,v))

json.dump({'sent':{'n':len(sl),'avg':round(sum(sl)/len(sl),3),'median':st.median(sl)},
           'clause':{'avg':round(sum(cl)/len(cl),3),'median':st.median(cl)},
           'para':{'n':len(para_len),'avg':round(sum(para_len)/len(para_len),3),
                   'median':st.median(para_len),'max':max(para_len)},
           'dialogue_pct':round(100*dl_tot/han_tot,2),
           'per_ch_dialogue':{str(k):round(100*v[0]/v[1],2) for k,v in per_ch_dl.items() if v[1]},
           'fw':fw_cnt, 'han_tot':han_tot,
           'per_ch_para_count':{str(k):len(v) for k,v in per_ch_para.items()}},
          open(A/'rhythm.json','w',encoding='utf-8'), ensure_ascii=False)
print('saved rhythm.json')
