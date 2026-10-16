# -*- coding: utf-8 -*-
"""Pass 10: pull full farming/governance scene for quotes + template-phrase & AI-ish density."""
import re, json, statistics as st
from pathlib import Path
A = Path(r'D:\Book\.analyze')
raw = (A/'chapters.txt').read_text(encoding='utf-8')
chunks = re.split(r'^===CH(\d+)\t(.*)$', raw, flags=re.M)
chapters = [{'n': int(chunks[i]), 'title': chunks[i+1], 'text': chunks[i+2].strip()}
            for i in range(1, len(chunks), 3)]
by = {c['n']: c for c in chapters}
CN = re.compile(r'[\u4e00-\u9fff]')
def han(s): return len(CN.findall(s))
def paras(c): return [p for p in c['text'].split('\n') if han(p) > 0]
HAN = han(raw)

for n, lo, hi in [(102, 12, 34), (101, 14, 34)]:
    print('\n########## CH%d 《%s》 段%d-%d ##########' % (n, by[n]['title'], lo, hi))
    ps = paras(by[n])
    for i in range(lo, min(hi, len(ps))):
        print('  [%d] %s' % (i+1, ps[i][:210]))

print('\n\n########## 度田 / 人治 片段 ##########')
G = re.compile(r'(度田|清查田亩|均田|户籍|豪强|坞壁|兼并|佃户|部曲|赈济|常平仓|义仓|劝农|垦荒|招抚流民)')
got = 0
for c in chapters:
    ps = paras(c)
    for i, p in enumerate(ps):
        if G.search(p) and han(p) >= 45 and got < 12:
            print('\n[CH%d] %s' % (c['n'], p[:250])); got += 1
    if got >= 12: break

# --- template / AI-ish phrase density (compare against nothing, just report) ---
print('\n\n########## 套话与高频短语 ##########')
CL = ['深吸一口气','不由自主','嘴角','眼中闪过','一丝','不禁','心中一凛','脸色一变','微微一笑',
      '不置可否','意味深长','若有深意','沉默片刻','良久','缓缓','淡淡','顿时','随即','瞬间']
for w in CL:
    c = raw.count(w)
    print('  %-8s %4d  (%.1f/万字)' % (w, c, c/HAN*10000))
# over-used connective openings per paragraph
print('\n段落首字高频:')
from collections import Counter
first2 = Counter()
for c in chapters:
    for p in paras(c):
        first2[p[:2]] += 1
for k, v in first2.most_common(25): print('  %s\t%d' % (k, v))
# sentence-initial 刘备 frequency
nb = len(re.findall(r'(?m)^刘备', raw))
print('\n段首为「刘备」的段数: %d (%.1f%% of 27163段)' % (nb, 100*nb/27163))
