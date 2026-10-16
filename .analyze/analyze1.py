# -*- coding: utf-8 -*-
"""Pass 1: framework stats for the benchmark novel."""
import re, json, statistics as st
from pathlib import Path

SRC = Path(r'C:\Users\yu459\Downloads\慢着，请别叫我昭烈帝.txt')
OUT = Path(r'D:\Book\.analyze')
OUT.mkdir(parents=True, exist_ok=True)

raw = SRC.read_text(encoding='utf-8')
lines = raw.split('\n')
print('raw bytes', SRC.stat().st_size)
print('total lines', len(lines))
print('raw chars', len(raw))

CH = re.compile(r'^\s*第\s*([0-9零一二三四五六七八九十百千两]+)\s*章[\s　]*(.*)$')
CN = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'两':2}
def cn2int(s):
    s = s.strip()
    if s.isdigit(): return int(s)
    total, unit = 0, 1
    num = 0
    for ch in reversed(s):
        if ch in CN:
            num = CN[ch]
        elif ch == '十':
            unit = 10 if unit < 10 else unit
            num = 1 if num == 0 else num
            total += num * unit
            unit *= 10 if unit == 10 else 1
            num = 0
        elif ch == '百':
            unit = 100
            total += max(num,1) * unit
            unit = 1000
            num = 0
        elif ch == '千':
            unit = 1000
            total += max(num,1) * unit
            unit = 10000
            num = 0
    return total + num

# chapter boundaries
heads = []
for i, ln in enumerate(lines):
    m = CH.match(ln)
    if m:
        n = cn2int(m.group(1))
        heads.append((i, n, m.group(2).strip()))
print('heading matches', len(heads))
print('first 5', heads[:5])
print('last 5', heads[-5:])

# strict sequence check
nums = [h[1] for h in heads]
seq = [i for i in range(1, len(nums)+1) if nums[i-1] != i]
print('non-sequential positions (first 20):', seq[:20])

# watermark / junk lines
junk = re.compile(r'(最新网址|www\.|23uswx|请记住本站|手机版|笔趣阁|章节错误|内容严重缺失|加入书签|推荐票|求月票|天才一秒|记住网址)')
junk_hits = {}
for ln in lines:
    t = ln.strip()
    if t and junk.search(t):
        junk_hits[t[:60]] = junk_hits.get(t[:60], 0) + 1
print('junk-line kinds', len(junk_hits), 'total junk lines', sum(junk_hits.values()))
for k, v in sorted(junk_hits.items(), key=lambda x: -x[1])[:12]:
    print('  ', v, '|', k)

# build chapters
chapters = []
for idx, (li, n, title) in enumerate(heads):
    end = heads[idx+1][0] if idx+1 < len(heads) else len(lines)
    body = lines[li+1:end]
    clean = []
    for ln in body:
        t = ln.strip()
        if not t: continue
        if junk.search(t): continue
        clean.append(t)
    chapters.append({'n': n, 'title': title, 'lines': clean,
                     'text': '\n'.join(clean)})
print('chapters built', len(chapters))

def cjk_count(s):
    return sum(1 for c in s if not c.isspace())

tot = sum(cjk_count(c['text']) for c in chapters)
print('total chars (non-space, junk removed)', tot)

lens = [cjk_count(c['text']) for c in chapters]
order = sorted(range(len(lens)), key=lambda i: lens[i])
print('avg', round(tot/len(lens),1), 'median', st.median(lens),
      'min', min(lens), 'max', max(lens))
print('stdev', round(st.pstdev(lens),1))
print('shortest 5:', [(chapters[i]['n'], chapters[i]['title'], lens[i]) for i in order[:5]])
print('longest 5:', [(chapters[i]['n'], chapters[i]['title'], lens[i]) for i in order[-5:]])
qs = st.quantiles(lens, n=10)
print('deciles', [round(q) for q in qs])
buckets = [('<1500',0),('1500-1999',0),('2000-2499',0),('2500-2999',0),
           ('3000-3499',0),('3500-3999',0),('4000-4999',0),('>=5000',0)]
def bk(v):
    if v<1500: return '<1500'
    if v<2000: return '1500-1999'
    if v<2500: return '2000-2499'
    if v<3000: return '2500-2999'
    if v<3500: return '3000-3499'
    if v<4000: return '3500-3999'
    if v<5000: return '4000-4999'
    return '>=5000'
bd = {}
for v in lens: bd[bk(v)] = bd.get(bk(v),0)+1
print('buckets', {k: bd.get(k,0) for k,_ in buckets})
print('in 2000-4000 pct',
      round(100*sum(1 for v in lens if 2000<=v<4000)/len(lens),1))

# punctuation
punct = {}
for c in chapters:
    for ch in c['text']:
        if ch in '，。！？；：、“”‘’《》（）—…·':
            punct[ch] = punct.get(ch,0)+1
print('punct counts', sorted(punct.items(), key=lambda x:-x[1]))
print(',/。 ratio', round(punct.get('，',0)/max(punct.get('。',1),1),3))

json.dump({'tot':tot,'n':len(chapters),'lens':lens,
           'titles':[c['title'] for c in chapters],
           'nums':[c['n'] for c in chapters]},
          open(OUT/'basic.json','w',encoding='utf-8'), ensure_ascii=False)
# persist cleaned chapters for later passes
with open(OUT/'chapters.txt','w',encoding='utf-8') as fh:
    for c in chapters:
        fh.write('===CH%d\t%s\n' % (c['n'], c['title']))
        fh.write(c['text']+'\n')
print('saved', OUT/'chapters.txt')
