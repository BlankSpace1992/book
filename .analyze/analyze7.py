# -*- coding: utf-8 -*-
"""Pass 7: classical-vs-modern grammar disambiguation + perspective/time-jump extraction."""
import re, json, statistics as st
from pathlib import Path
from collections import defaultdict, Counter
A = Path(r'D:\Book\.analyze')
raw = (A/'chapters.txt').read_text(encoding='utf-8')
chunks = re.split(r'^===CH(\d+)\t(.*)$', raw, flags=re.M)
chapters = [{'n': int(chunks[i]), 'title': chunks[i+1], 'text': chunks[i+2].strip()}
            for i in range(1, len(chunks), 3)]
CN = re.compile(r'[\u4e00-\u9fff]')
def han(s): return len(CN.findall(s))
HAN = han(raw)
def per10k(c): return round(c/HAN*10000, 1)

print('=== 也：句末语气词 vs 现代副词 ===')
# sentence-final 也 (classical) = 也 immediately before 。！？…” OR at end
fin_ye = len(re.findall(r'也[。！？…”]', raw))
# 也 as "also": 也+verb/adj mid-sentence, or 也 in patterns like 我也没有/也+不
mid_ye = len(re.findall(r'也', raw)) - fin_ye
print('也 total %d | 句末(语气词) %d (%.1f%%) | 句中 %d (%.1f%%)'
      % (len(re.findall(r'也', raw)), fin_ye, 100*fin_ye/len(re.findall(r'也', raw)),
         mid_ye, 100*mid_ye/len(re.findall(r'也', raw))))
ex = []
for c in chapters:
    for m in re.finditer(r'[^。！？\n]{6,60}也[。！？]', c['text']):
        ex.append((c['n'], m.group(0)))
print('  句末也 例:')
for n, s in ex[:80:8][:6]: print('    CH%d %s' % (n, s))

print('\n=== 矣 ===')
fin_yi = len(re.findall(r'矣[。！？…”]', raw))
print('矣 total %d 句末 %d (%.1f%%)' % (len(re.findall(r'矣', raw)), fin_yi,
      100*fin_yi/len(re.findall(r'矣', raw))))
for c in chapters:
    for m in re.finditer(r'[^。！？\n]{4,60}矣[。！？]', c['text']):
        print('    CH%d %s' % (c['n'], m.group(0)))

print('\n=== 之 用法细分 ===')
cats = {
 '之所以(现代连词)': r'之所以',
 '之后/之前/之间/之中/之外/之内/之上/之下(方位/时间词)': r'之[后前间中外汇上下一]',
 'X之Y(的/领属)': r'[\u4e00-\u9fff]之[\u4e00-\u9fff]',
 'V之(代词宾语)': r'(弃|取|杀|闻|知|用|攻|击|得|使|从|与|为|观|听|思|求|待|待|代|效|图|救|迎|立|拒|守|战|伐|灭|定|安)之',
 '所X之Y': r'所[\u4e00-\u9fff]{1,3}之',
}
res = {}
for k, p in cats.items():
    res[k] = len(re.findall(p, raw))
    print('  %-40s %5d  (%.1f/万字)' % (k, res[k], per10k(res[k])))

print('\n=== 文言用法原文例（之/其/乃/遂/皆/焉/哉）===')
for w, pat in [('之(的)', r'[\u4e00-\u9fff]{2}之[\u4e00-\u9fff]{2}'),
               ('其', r'[^。！？\n]{4,40}其[\u4e00-\u9fff]{2}[^。！？\n]{0,30}'),
               ('乃', r'[^。！？\n]{4,40}乃[^。！？\n]{2,40}'),
               ('遂', r'[^。！？\n]{4,40}遂[^。！？\n]{2,40}'),
               ('皆', r'[^。！？\n]{4,40}皆[^。！？\n]{2,40}')]:
    seen = 0
    print('\n [%s]' % w)
    for c in chapters:
        for m in re.finditer(pat, c['text']):
            s = m.group(0).strip()
            if 12 < len(s) < 70:
                print('    CH%d %s' % (c['n'], s)); seen += 1
            if seen >= 5: break
        if seen >= 5: break

print('\n\n=== 视角与人称 ===')
for p, lbl in [(r'(?<![\u4e00-\u9fff])我(?![\u4e00-\u9fff])', '我'),
               (r'我们', '我们'), (r'咱', '咱'), (r'他', '他'), (r'她', '她'),
               (r'(?<![\u4e00-\u9fff])吾', '吾'), (r'朕', '朕'), (r'孤(?![\u4e00-\u9fff])', '孤'),
               (r'刘备(?=[\u4e00-\u9fff])', '刘备(作主语)'),
               (r'玄德', '玄德'), (r'备(?=[\u4e00-\u9fff])', '备(自称)')]:
    c = len(re.findall(p, raw))
    print('  %s\t%d\t%.1f/万字' % (lbl, c, per10k(c)))

print('\n=== 上帝视角/作者旁白检测（预告式句子）===')
NARR = [r'[^。！？\n]{0,30}(殊不知|岂料|不曾想|却不曾想|多年后|后世|史书|历史上|却不知|若是知道|可惜)[^。！？\n]{0,40}',
        r'[^。！？\n]{0,20}(这一切|此[时刻]|与此同[时]|同一时间|另一边|远在)[^。！？\n]{4,50}']
for p in NARR:
    hits = re.findall(p, raw)
    print('  pattern hits:', len(re.findall(p, raw)))
    for m in list(re.finditer(p, raw))[:5]:
        print('     ...%s' % m.group(0)[:88])
json.dump({'ye_final': fin_ye, 'yi_final': fin_yi, 'zhi_cats': res, 'han': HAN},
          open(A/'classical.json','w',encoding='utf-8'), ensure_ascii=False)
print('\nsaved classical.json')
