# -*- coding: utf-8 -*-
"""Pass 8: opener/closer samples, time jumps, scene transitions, pacing, farming passages."""
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

# ---------- A. sampled openers & closers ----------
SAMPLE = [1, 3, 5, 8, 10, 12, 15, 17, 18, 20, 21, 24, 27, 29, 30, 32, 35, 37, 41, 43, 45, 48, 50]
print('###### 抽样章：开头首段 + 结尾末段 ######')
for n in SAMPLE:
    c = by.get(n)
    if not c: continue
    ps = paras(c)
    print('\n===== CH%d 《%s》 字数%d 段数%d =====' % (n, c['title'], han(c['text']), len(ps)))
    print('[首段] %s' % ps[0][:200])
    if len(ps) > 1: print('[次段] %s' % ps[1][:150])
    print('[末段] ...%s' % ps[-1][-220:])
    if len(ps) > 2: print('[倒二] ...%s' % ps[-2][-150:])

# ---------- B. time jumps ----------
print('\n\n###### 时间跳跃开场（纪年/季节/时长） ######')
TIME = re.compile(r'(次年|翌年|明年|数月后|半月后|旬日后|十日后|三日后|数日后|次日|翌日|是夜|是日|'
                  r'转眼|不知不觉|又过|过了[一二三四五六七八九十数]|入[秋冬春夏]|[秋冬春夏]去[秋冬春夏]来|'
                  r'初平[一二三四五六七八九]年|建安[一二三四五六七八九十]+年|兴平[一二]年)')
tj = []
for c in chapters:
    ps = paras(c)
    if not ps: continue
    f = ps[0]
    m = TIME.search(f[:30])
    if m and m.start() <= 12:
        tj.append((c['n'], m.group(1), f[:110]))
print('时间跳跃型开场 共 %d 章 (%.1f%%)' % (len(tj), 100*len(tj)/len(chapters)))
for n, k, s in tj[:22]: print('  CH%d [%s] %s' % (n, k, s))

# ---------- C. scene transitions ----------
print('\n\n###### 场景/视角切换词 ######')
TR = [('与此同时', r'与此同时'), ('同一时间', r'同一时间'), ('另一边', r'另一边'),
      ('此时此刻', r'此时此刻'), ('视线转', r'(视线|镜头)转'), ('远在', r'远在'),
      ('却说', r'却说'), ('且说', r'且说'), ('话分两头', r'话分两头'), ('与此同时', r'与此同[时]'),
      ('而此刻', r'而此刻'), ('此刻', r'此刻')]
for lbl, p in TR:
    c = len(re.findall(p, raw))
    print('  %-8s %d' % (lbl, c))
print('\n切换实例:')
shown = 0
for c in chapters:
    for m in re.finditer(r'(与此同时|同一时间|另一边|话分两头|视线转|镜头转|却说|且说)[^。！？\n]{0,60}[。！？]', c['text']):
        print('  CH%d %s' % (c['n'], m.group(0)))
        shown += 1
        break
    if shown >= 12: break

# ---------- D. 章末钩子：末句形态统计 ----------
print('\n\n###### 章末末句形态 ######')
forms = {'对话收尾(引号结束)': 0, '陈述句(。)': 0, '问句(？)': 0, '感叹(！)': 0, '省略号(…/……)': 0}
lasts = []
for c in chapters:
    ps = paras(c)
    if not ps: continue
    ss = [s for s in re.split(r'(?<=[。！？…”])', ps[-1]) if han(s) > 0]
    if not ss: continue
    s = ss[-1].strip()
    lasts.append((c['n'], s))
    if s.endswith('”'): forms['对话收尾(引号结束)'] += 1
    elif s.endswith('…') or s.endswith('……'): forms['省略号(…/……)'] += 1
    elif s.endswith('？'): forms['问句(？)'] += 1
    elif s.endswith('！'): forms['感叹(！)'] += 1
    else: forms['陈述句(。)'] += 1
print(forms, 'total', len(lasts))
ll = [han(s) for _, s in lasts]
print('末句字数 avg %.1f median %s p90 %d max %d' % (sum(ll)/len(ll), st.median(ll),
      sorted(ll)[int(len(ll)*.9)], max(ll)))
# last para length
lp = [han(paras(c)[-1]) for c in chapters if paras(c)]
print('末段字数 avg %.1f median %s min %d max %d' % (sum(lp)/len(lp), st.median(lp), min(lp), max(lp)))
onesent = sum(1 for c in chapters if paras(c) and len([s for s in re.split(r'(?<=[。！？…”])', paras(c)[-1]) if han(s)>0]) == 1)
print('末段为单句的章数 %d (%.1f%%)' % (onesent, 100*onesent/len(chapters)))

# ask/ellipsis/negation hooks
hookpat = {'疑问道句': r'(？$|？”$)', '提示下章': r'(明日|来日|他日|不日|下[一]?步|接下来|不久|即将|就要|恐怕|怕是要|迟早|终[将究])',
           '转折词': r'(只是|可是|然而|不过|却|反[倒而]|岂料|不料|竟然|居然|谁知)',
           '未完成感(…/罢了/而已)': r'(…|罢了|而已|足矣|便是|即可)'}
for lbl, p in hookpat.items():
    cnt = sum(1 for _, s in lasts if re.search(p, s))
    print('  末句含[%s]: %d (%.1f%%)' % (lbl, cnt, 100*cnt/len(lasts)))
any_hook = sum(1 for _, s in lasts if re.search(r'(？|…|只是|可是|然而|不过|却|恐怕|将至|竟|居然|谁知|不料|明日|即将|要变|不好|坏了)', s))
print('  末句含任一钩子标记: %d (%.1f%%)' % (any_hook, 100*any_hook/len(lasts)))

# ---------- E. 爽点/兑现节奏 ----------
print('\n\n###### 爽点/微兑现标记与间隔 ######')
SAT = [('群体反应', r'(喝彩|欢呼|哗然|震动|大惊|惊愕|哗然一片|面面相觑|瞪目结舌|目瞪口呆|拜服|叹服|心服)'),
       ('惊叹评价', r'(神人|奇才|大才|真乃|果然|英雄|了得|不凡|深不可测|名不虚传|相见恨晚)'),
       ('打脸/反转', r'(面色惨白|哑口无言|无言以对|冷汗|如遭雷击|瘫坐|脸色一[变白]|气[得极]|恼羞成怒)'),
       ('收服/投效', r'(愿降|请降|归降|投[效奔靠]|拜见|效忠|唯.{0,3}之命是从|甘为)'),
       ('封赏/得利', r'(赏赐|奖赏|赐[爵酒金]|加封|拜为|表为|任命|升[迁为]|岁[入俸]|得[到粮地])'),
       ('计谋揭示', r'(原来|此计|之计|早有准备|早有预谋|将计就计|果然如此|不出所料|正中下怀)')]
per_ch = {}
for c in chapters:
    hits = {}
    for lbl, p in SAT:
        v = len(re.findall(p, c['text']))
        if v: hits[lbl] = v
    per_ch[c['n']] = hits
allhit = {n: sum(h.values()) for n, h in per_ch.items()}
vals = list(allhit.values())
print('每章爽点标记数 avg %.1f median %s min %d max %d' % (sum(vals)/len(vals), st.median(vals), min(vals), max(vals)))
zero = [n for n, v in allhit.items() if v == 0]
print('零标记章 %d (%.1f%%)' % (len(zero), 100*len(zero)/len(chapters)))
for lbl, _ in SAT:
    tot = sum(h.get(lbl, 0) for h in per_ch.values())
    chs = sum(1 for h in per_ch.values() if h.get(lbl, 0) > 0)
    print('  %-8s 总%d次  出现于%d章(%.1f%%)  平均每章%.2f次' % (lbl, tot, chs, 100*chs/len(chapters), tot/len(chapters)))
# spacing in chars: avg chapter length / hits per chapter
avg = 1018899/len(chapters)
print('平均兑现间隔 ≈ %.0f 字/次（章均%.0f字 ÷ 章均%.1f个标记）' % (avg/(sum(vals)/len(vals)), avg, sum(vals)/len(vals)))

# intra-chapter position of sat markers
pos = []
for c in chapters:
    ps = paras(c)
    for i, p in enumerate(ps):
        if any(re.search(pt, p) for _, pt in SAT):
            pos.append(i/max(len(ps)-1, 1))
print('爽点标记在章内位置分布（0=开头,1=结尾）: avg %.2f median %.2f' % (sum(pos)/len(pos), st.median(pos)))
for lo in [0, .2, .4, .6, .8]:
    cnt = sum(1 for v in pos if lo <= v < lo+.2)
    print('   位置 %.0f-%.0f%%: %d (%.1f%%)' % (lo*100, (lo+.2)*100, cnt, 100*cnt/len(pos)))

json.dump({'close_forms': forms, 'sat': {str(k): v for k, v in per_ch.items()},
           'timejump_chapters': len(tj), 'lastsent': lasts[:60]},
          open(A/'pacing.json','w',encoding='utf-8'), ensure_ascii=False)
print('\nsaved pacing.json')
