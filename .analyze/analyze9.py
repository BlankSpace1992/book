# -*- coding: utf-8 -*-
"""Pass 9: verify length accounting; farming/governance passages; in-chapter payoff spacing."""
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

# --- verify CH3 & CH1 accounting
for n in (1, 3, 5, 23):
    c = by[n]
    t = c['text']
    print('CH%d 汉字%d 非空白%d 含标点%d 段数%d'
          % (n, han(t), sum(1 for ch in t if not ch.isspace()),
             len(re.sub(r'\s', '', t)), len(paras(c))))

SRC = Path(r'C:\Users\yu459\Downloads\慢着，请别叫我昭烈帝.txt')
lines = SRC.read_text(encoding='utf-8').split('\n')
CH = re.compile(r'^\s*第\s*([0-9零一二三四五六七八九十百千两]+)\s*章[\s　]*(.*)$')
heads = [(i, l) for i, l in enumerate(lines) if CH.match(l)]
print('\n--- 所有「第三章」出现位置 ---')
for i, l in heads:
    if CH.match(l).group(1) == '三':
        body = ''.join(lines[i+1:i+120])
        print('  line %d | %s | 后续120行汉字约 %d' % (i, l.strip(), han(body)))
print('--- 所有「第一章/第一章」出现位置 ---')
for i, l in heads:
    if CH.match(l).group(1) in ('一','1'):
        body = ''.join(lines[i+1:i+120])
        print('  line %d | %s | 后续120行汉字约 %d' % (i, l.strip(), han(body)))
# duplicate numbers?
from collections import Counter
cnt = Counter(CH.match(l).group(1) for _, l in heads)
dups = {k: v for k, v in cnt.items() if v > 1}
print('重复章号(中文数字):', dups)

# --- farming / governance passages
print('\n\n###### 种田/人治段落样本 ######')
FARM = re.compile(r'(屯田|农具|耕牛|陂池|水车|铁器|度田|均田|仓廪|粮仓|水利|春耕|秋收|赋税|劝课农桑|牛耕|麦种|禾秆|度量衡|造纸|晒盐|冶铁|工坊|坩埚|曲辕|耧车|翻车|水碓|漕运|集市|户籍|乡吏|里正|算赋|口钱|徭役)')
cands = []
for c in chapters:
    ps = paras(c)
    for i, p in enumerate(ps):
        if FARM.search(p) and han(p) >= 30:
            cands.append((c['n'], i, len(ps), p))
print('种田类段落（>=30字）总数 %d，分布于 %d 章' % (len(cands), len(set(x[0] for x in cands))))
from collections import Counter as C2
top = C2(x[0] for x in cands).most_common(10)
print('种田内容最密集的章:', top)
for n, i, tot, p in [x for x in cands if x[0] in (23, 12, 30, 50, 105, 110)][:14]:
    print('\n[CH%d 段%d/%d] %s' % (n, i+1, tot, p[:230]))

# --- in-chapter micro-payoff spacing: reward/reveal beats
print('\n\n###### 章内微兑现间隔（按段落位置） ######')
BEATS = re.compile(r'(喝彩|欢呼|大惊|惊愕|拜服|叹服|神人|奇才|真乃|果然|愿降|请降|归降|拜见|效忠|'
                   r'赏赐|奖赏|加封|拜为|表为|原来|此计|将计就计|不出所料|正中下怀|大喜|欣然|抚掌|'
                   r'大喜过望|心服|默然|无语|惨白|咂舌|啧啧|倒吸)')
gaps_all = []
for c in chapters:
    ps = paras(c)
    idx = [i for i, p in enumerate(ps) if BEATS.search(p)]
    if len(idx) >= 2:
        for a, b in zip(idx, idx[1:]):
            gaps_all.append(b-a)
print('相邻兑现节拍间隔（段数）: n=%d avg %.2f median %s p90 %d' %
      (len(gaps_all), sum(gaps_all)/len(gaps_all), st.median(gaps_all),
       sorted(gaps_all)[int(len(gaps_all)*.9)]))
per_ch_beats = [len([i for i, p in enumerate(paras(c)) if BEATS.search(p)]) for c in chapters]
print('每章节拍数 avg %.2f median %s min %d max %d' %
      (sum(per_ch_beats)/len(per_ch_beats), st.median(per_ch_beats),
       min(per_ch_beats), max(per_ch_beats)))
zero = sum(1 for v in per_ch_beats if v == 0)
print('章节拍=0 的章 %d (%.1f%%)' % (zero, 100*zero/len(chapters)))
avglen = 1018899/len(chapters)
print('折算：平均每 %.0f 字出现一次节拍（章均%.0f字 ÷ 章均%.2f个节拍）'
      % (avglen/(sum(per_ch_beats)/len(per_ch_beats)), avglen, sum(per_ch_beats)/len(per_ch_beats)))
json.dump({'beats': per_ch_beats}, open(A/'beats.json','w',encoding='utf-8'), ensure_ascii=False)
