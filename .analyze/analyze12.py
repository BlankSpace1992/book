# -*- coding: utf-8 -*-
"""Pass 12: final verification — artifact quantification, quote verification, extremes."""
import re, statistics as st, json
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

orig = Path(r'C:\Users\yu459\Downloads\慢着，请别叫我昭烈帝.txt').read_text(encoding='utf-8')
olines = orig.split('\n')
print('=== 水印/杂质行统计（原始文件）===')
pats = {'最新网址：www.23uswx.la': r'最新网址：www\.23uswx\.la',
        '《慢着…》二三中文…牢记网址': r'《慢着，请别叫我昭烈帝》二三中文',
        '原文在六#9@书/吧看！': r'原文在六#9@书/吧看！',
        '(本章完)': r'\(本章完\)'}
tot_junk = 0
for lbl, p in pats.items():
    c = len(re.findall(p, orig)); tot_junk += c
    print('  %-30s %4d 行' % (lbl, c))
print('  合计杂质行 %d / 总行 %d = %.1f%%' % (tot_junk, len(olines), 100*tot_junk/len(olines)))
rawch = len([ch for ch in orig if not ch.isspace()])
print('  原始非空字符 %d；清理后 %d；差 %.1f%%' % (rawch, 1018899, 100*(rawch-1018899)/rawch))

print('\n=== 引文核验 ===')
def find(pat, limit=2):
    out = []
    for m in re.finditer(pat, raw):
        p = m.start()
        ch = raw.rfind('===CH', 0, p)
        hdr = raw[ch:raw.find('\n', ch)]
        out.append((hdr, raw[max(0,p-60):p+120].replace('\n', '|')))
        if len(out) >= limit: break
    return out
for pat in ['掺扶', '以优击劣', '袖服', '旨有', '朓望']:
    print(' [%s]' % pat)
    for h, s in find(pat): print('   %s ... %s' % (h, s))

print('\n=== 极端章（对话占比）===')
DQ = re.compile(r'“([^”]*)”')
sh = []
for c in chapters:
    t = c['text']; h = han(t)
    if h: sh.append((round(100*sum(han(x) for x in DQ.findall(t))/h, 1), c['n'], c['title'], h))
sh.sort()
print(' 最低 5:', sh[:5])
print(' 最高 5:', sh[-5:])

print('\n=== 极端章（段落数 / 句长）===')
pc = sorted(((len(paras(c)), c['n'], c['title']) for c in chapters))
print(' 段数最少 5:', pc[:5]); print(' 段数最多 5:', pc[-5:])

print('\n=== 每段平均字数×章长关系 ===')
print(' 全书: 27163 段 / 487 章 = %.1f 段/章' % (27163/487))
print(' 平均段 32.97 字（含标点非空白口径）→ 按汉字口径 %.1f 字' % (895637/27163))

print('\n=== 抽样章的精确字数（含标点口径，用于报告）===')
for n in [1,3,5,8,20,30,50]:
    c = by[n]; t = c['text']
    print('  CH%d 《%s》 含标点 %d  汉字 %d  段 %d' % (n, c['title'], len(re.sub(r'\s','',t)), han(t), len(paras(c))))

# hook classification v2 (末句)
print('\n=== 章末钩子二分类（末句）===')
cat = {'A 对话悬念（引号收）':0, 'B 转折/反转词':0, 'C 未完成（…/罢了/而已/才/方）':0, 'D 疑问':0, 'E 感叹定调':0, 'F 平陈述（无标记）':0}
ex2 = {}
for c in chapters:
    ps = paras(c)
    ss = [s for s in re.split(r'(?<=[。！？…”])', ps[-1]) if han(s) > 0]
    s = ss[-1].strip()
    if s.endswith('”'): k = 'A 对话悬念（引号收）'
    elif re.search(r'(只是|可是|然而|不过|不料|岂料|竟然|居然|谁知|却|反而|原来)', s): k = 'B 转折/反转词'
    elif re.search(r'(…|罢了|而已|才|方|尚|还|未|尚未|几乎|险些)', s): k = 'C 未完成（…/罢了/而已/才/方）'
    elif s.endswith('？'): k = 'D 疑问'
    elif s.endswith('！'): k = 'E 感叹定调'
    else: k = 'F 平陈述（无标记）'
    cat[k] += 1
    ex2.setdefault(k, []).append((c['n'], s))
for k, v in sorted(cat.items()):
    print('  %-28s %3d (%.1f%%)' % (k, v, 100*v/487))
    for n, s in ex2[k][:3]: print('       CH%d %s' % (n, s[:95]))
json.dump({'hook_v2': cat}, open(A/'hook2.json','w',encoding='utf-8'), ensure_ascii=False)
