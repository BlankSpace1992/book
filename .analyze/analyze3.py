# -*- coding: utf-8 -*-
"""Pass 3: function-word usage contexts, opener/closer taxonomy, speaker voice, pacing."""
import re, json, statistics as st, random
from pathlib import Path
A = Path(r'D:\Book\.analyze')
raw = (A/'chapters.txt').read_text(encoding='utf-8')
chunks = re.split(r'^===CH(\d+)\t(.*)$', raw, flags=re.M)
chapters = [{'n': int(chunks[i]), 'title': chunks[i+1], 'text': chunks[i+2].strip()}
            for i in range(1, len(chunks), 3)]
CN = re.compile(r'[\u4e00-\u9fff]')
def han(s): return len(CN.findall(s))
def paras(c): return [p for p in c['text'].split('\n') if han(p) > 0]
DQ = re.compile(r'“([^”]*)”')
OUT = {}

# ---- 1. classical function words: sentence-final vs medial, in dialogue vs narration ----
print('=== 文言虚词用法采样 ===')
for w in ['也','矣','乎','耳','哉','焉']:
    fin = med = 0; ex_fin, ex_med = [], []
    for c in chapters:
        for s in re.split(r'(?<=[。！？…])', c['text']):
            n = s.count(w)
            if not n: continue
            if s.rstrip('”').rstrip().endswith(w):
                fin += n
                if len(ex_fin) < 4 and 20 < len(s) < 130: ex_fin.append((c['n'], s.strip()))
            else:
                med += n
                if len(ex_med) < 4 and 15 < len(s) < 130: ex_med.append((c['n'], s.strip()))
    print('\n--%s-- 句末 %d / 句中 %d' % (w, fin, med))
    for n, s in ex_fin[:3]: print('   [句末 CH%d] %s' % (n, s[:90]))
    for n, s in ex_med[:3]: print('   [句中 CH%d] %s' % (n, s[:90]))
    OUT['fw_%s' % w] = {'final': fin, 'medial': med}

# 之 usage types
print('\n=== 之 用法 ===')
pat_zhisuo = len(re.findall(r'之所以', raw))
pat_zhihou = len(re.findall(r'之后', raw))
pat_zhijian = len(re.findall(r'之间', raw))
pat_zhizhong = len(re.findall(r'之中', raw))
print(' 之所以 %d / 之后 %d / 之间 %d / 之中 %d' % (pat_zhisuo, pat_zhihou, pat_zhijian, pat_zhizhong))
zhi_other = []
for c in chapters:
    for m in re.finditer(r'.{6}之(?!后|间|中|前|外|所|上|下|内|一|时|类|余|曰|子|人).{6}', c['text']):
        zhi_other.append((c['n'], m.group(0)))
print(' classical 之 (宾语前置/的) 样本:', len(zhi_other))
for n, s in zhi_other[:6]: print('   CH%d: %s' % (n, s))
OUT['zhi_other'] = len(zhi_other)

# density of 也/矣 in dialogue vs narration
d_ye = n_ye = d_han = n_han = 0
for c in chapters:
    for ln in c['text'].split('\n'):
        is_d = '“' in ln
        d = sum(han(x) for x in DQ.findall(ln))
        if is_d and d:
            d_ye += ln.count('也') + ln.count('矣'); d_han += han(ln)
        else:
            n_ye += ln.count('也') + ln.count('矣'); n_han += han(ln)
print('\n也+矣 密度: 对话行 %.1f/万字  叙述行 %.1f/万字' % (d_ye/d_han*10000, n_ye/n_han*10000))
OUT['ye_dialogue_density'] = round(d_ye/d_han*10000,1)
OUT['ye_narration_density'] = round(n_ye/n_han*10000,1)

# ---- 2. chapter openers ----
print('\n=== 开场类型 ===')
cat = {'时间起':0,'地点起':0,'人物动作起':0,'对话起':0,'承接上章起':0,'议论/背景起':0,'其他':0}
open_samples = {}
TIME = re.compile(r'(^|[，。])(次[日年]|翌日|次日|当[日夜]|是夜|是日|这[一]?日|数月|旬日|半月|转眼|入[夜秋冬夏春]|第[二三四五]天|如[今今]|翌晨|天明|黄昏|傍晚|晨|午后|晚[间上])')
PLACE = re.compile(r'^[\u4e00-\u9fff]{1,4}[县郡城州关营地宫府堂宫门]')
for c in chapters:
    ps = paras(c)
    if not ps: continue
    first = ps[0]
    k = '其他'
    if first.startswith('“') or first.startswith('「'): k = '对话起'
    elif TIME.search(first[:14]): k = '时间起'
    elif PLACE.match(first[:6]): k = '地点起'
    elif first.startswith(('却说','话分两头','上回','且说','却说')): k = '承接上章起'
    elif re.match(r'^(刘备|曹操|袁绍|吕布|孙策|孙权|荀彧|诸葛亮|关[羽张]|张[飞辽]|赵[云]|贾诩|郭嘉|董卓|刘[表璋]|袁术|曹仁|夏侯|司马|鲁肃|周瑜|太史|庞统|法正|李典|于禁|乐进|许褚|典韦|陈[宫群]|田丰|沮授|张昭|诸葛瑾)', first[:4]):
        k = '人物动作起'
    elif re.match(r'^(汉|东|初|自|当|其时|如今|所谓|纵观|自桓|昔)', first[:3]): k = '议论/背景起'
    cat[k] += 1
    open_samples.setdefault(k, []).append((c['n'], first[:110]))
print(cat)
for k, v in open_samples.items():
    print('\n[%s] 例 %d 例之一:' % (k, len(v)))
    for n, s in v[:3]: print('   CH%d %s' % (n, s))
OUT['open_cat'] = cat

# ---- 3. chapter closers ----
print('\n=== 收尾类型 ===')
close_cat = {'问句钩':0,'反转/意外':0,'预告危机':0,'情绪落点':0,'对话收':0,'升华/定调':0,'其他':0}
close_samples = {}
NEWCH = re.compile(r'(竟然|居然|竟是|原来|谁知|不料|岂料|却是|却是|想不到|万万没想到|却见|只听|却听)')
CRISIS = re.compile(r'(将至|来了|杀来|报！|急报|大势|恐怕|怕是要|要变|危险|来不及|必须|只能|不得|坏了|糟了|不好)')
QUESTION = re.compile(r'[？?]$')
for c in chapters:
    ps = paras(c)
    if not ps: continue
    last = ps[-1]
    k = '其他'
    if QUESTION.search(last): k = '问句钩'
    elif NEWCH.search(last): k = '反转/意外'
    elif CRISIS.search(last): k = '预告危机'
    elif last.endswith('”'): k = '对话收'
    elif re.search(r'(只是|可是|然而|但|却|而此刻|此时此刻|同一时间|与此同[时]|远[方在]|另一[边头]|不[远知])', last[-45:]): k = '反转/意外'
    elif re.search(r'(罢了|而已|足矣|足矣|足|幸[运好]|如此|甚好|足够|罢了)', last[-20:]): k = '情绪落点'
    elif re.search(r'(必[将然定]|终[将究]|迟早|有朝一日|来日|他日|天下|苍生|汉室|大[汉业事])', last): k = '升华/定调'
    else: k = '情绪落点'
    close_cat[k] += 1
    close_samples.setdefault(k, []).append((c['n'], last[-140:]))
print(close_cat)
for k, v in close_samples.items():
    print('\n[%s] %d 例' % (k, len(v)))
    for n, s in v[:2]: print('   CH%d ...%s' % (n, s))
OUT['close_cat'] = close_cat

# hook presence: last paragraph is a "turn"
hook = sum(v for k, v in close_cat.items() if k in ('问句钩','反转/意外','预告危机'))
print('\n硬钩子(问句/反转/危机) 占比 %.1f%%' % (100*hook/len(chapters)))
OUT['hard_hook_pct'] = round(100*hook/len(chapters),1)

# ---- 4. closing line length ----
cl = [han(paras(c)[-1]) for c in chapters if paras(c)]
print('章末段字数 avg %.1f median %s min %d max %d' % (sum(cl)/len(cl), st.median(cl), min(cl), max(cl)))
last_sent = []
for c in chapters:
    ps = paras(c)
    if not ps: continue
    ss = [s for s in re.split(r'(?<=[。！？…”])', ps[-1]) if han(s)>0]
    if ss: last_sent.append(han(ss[-1]))
print('末句字数 avg %.1f median %s' % (sum(last_sent)/len(last_sent), st.median(last_sent)))

# ---- 5. speaker voice ----
print('\n=== 人物口吻（按说话人统计）===')
SPK = re.compile(r'([\u4e00-\u9fff]{2,3})([^“”]{0,12}?)(说道|道|问|问[道]|答|答[道]|笑[道]|叹[道]|喝道|骂道|回道|应[道]|言[道]|曰)：“([^”]+)”')
from collections import defaultdict
sp = defaultdict(list)
for c in chapters:
    for m in SPK.finditer(c['text']):
        name, mid, vb, said = m.group(1), m.group(2), m.group(3), m.group(4)
        if 2 <= han(said) <= 200: sp[name].append((c['n'], said))
rows = []
for name, arr in sp.items():
    if len(arr) < 25: continue
    L = [han(s) for _, s in arr]
    rows.append((len(arr), name, round(sum(L)/len(L),1), st.median(L)))
rows.sort(reverse=True)
print('说话人\t次数\t均句长\t中位')
for r in rows[:22]: print('  %s\t%d\t%.1f\t%s' % (r[1], r[0], r[2], r[3]))
OUT['speakers'] = [{'name':r[1],'n':r[0],'avg':r[2],'med':r[3]} for r in rows[:40]]

# voice markers per top speaker
print('\n=== 各角色语言标记 ===')
marks = {'我':0,'某':0,'俺':0,'吾':0,'孤':0,'臣':0,'也':0,'乎':0,'呵':0,'哈':0,'！':0,'？':0,'…':0,'了':0,'呢':0,'吧':0}
for r in rows[:10]:
    name = r[1]; arr = sp[name]
    txt = ''.join(s for _, s in arr)
    hh = han(txt)
    line = []
    for mk in marks:
        cnt = txt.count(mk)
        line.append('%s%.1f' % (mk, cnt/hh*1000))
    print('  %s (n=%d) 千字频: %s' % (name, r[0], ' '.join(line)))
    print('     样本: ' + ' | '.join(s[:34] for _, s in arr[:3]))
json.dump(OUT, open(A/'pass3.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nsaved pass3.json')
