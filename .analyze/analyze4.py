# -*- coding: utf-8 -*-
"""Pass 4: fixed speaker attribution + quantitative opener typing + pacing/hook scan."""
import re, json, statistics as st
from pathlib import Path
from collections import defaultdict
A = Path(r'D:\Book\.analyze')
raw = (A/'chapters.txt').read_text(encoding='utf-8')
chunks = re.split(r'^===CH(\d+)\t(.*)$', raw, flags=re.M)
chapters = [{'n': int(chunks[i]), 'title': chunks[i+1], 'text': chunks[i+2].strip()}
            for i in range(1, len(chunks), 3)]
CN = re.compile(r'[\u4e00-\u9fff]')
def han(s): return len(CN.findall(s))
def paras(c): return [p for p in c['text'].split('\n') if han(p) > 0]
DQ = re.compile(r'“([^”]*)”')

# ---------- speaker attribution ----------
VERBS = ('说道','问道','答道','笑道','叹道','喝道','骂道','回道','应道','言道','劝道','叫道',
         '沉声道','正色道','拱手道','点头道','摇头道','低声道','大声道','又说','说道',
         '道','问','答','曰','说','喊','嚷嚷')
NAME = r'[\u4e00-\u9fff]{2,4}'
spk = defaultdict(list)
for c in chapters:
    for m in re.finditer(r'(' + NAME + r')([\u4e00-\u9fff]{0,8}?)(' + '|'.join(VERBS) + r')：“([^”]+)”',
                         c['text']):
        nm = re.sub(r'(连忙|急忙|忙|又|也|却|便|遂|方才|随即|当即|先行|反过来)$', '', m.group(1))
        nm = re.sub(r'^(只见|只听|于是|随后|接着|然后)', '', nm)
        if len(nm) < 2: continue
        said = m.group(4)
        if 1 <= han(said) <= 300:
            spk[nm].append((c['n'], said))
rows = sorted(((len(v), k) for k, v in spk.items()), reverse=True)
print('=== 带姓名标签的台词统计（前 24 位）===')
print('人物\t台词数\t平均字数\t中位\t≤6字占比')
stats = {}
for n, k in rows[:24]:
    L = [han(s) for _, s in spk[k]]
    txt = ''.join(s for _, s in spk[k]); hh = han(txt)
    short = round(100*sum(1 for v in L if v <= 6)/len(L))
    stats[k] = {'n': n, 'avg': round(sum(L)/len(L),1), 'med': st.median(L), 'short6': short,
                'excl': round(txt.count('！')/hh*1000,1), 'q': round(txt.count('？')/hh*1000,1),
                'ellip': round(txt.count('…')/hh*1000,1), 'wo': round(txt.count('我')/hh*1000,1),
                'wu': round(txt.count('吾')/hh*1000,1), 'gu': round(txt.count('孤')/hh*1000,1),
                'chen': round(txt.count('臣')/hh*1000,1), 'ye': round(txt.count('也')/hh*1000,1),
                'hu': round(txt.count('乎')/hh*1000,1), 'ba': round(txt.count('吧')/hh*1000,1),
                'ne': round(txt.count('呢')/hh*1000,1)}
    print('  %s\t%d\t%.1f\t%s\t%d%%' % (k, n, sum(L)/len(L), st.median(L), short))
print('\n=== 语言标记（千字频）===')
hdr = ['我','吾','孤','臣','也','乎','吧','呢','！','？','…']
print('人物\t' + '\t'.join(hdr))
for k in list(stats)[:14]:
    s = stats[k]
    print('%s\t%s' % (k, '\t'.join(str(s[x]) for x in
          ['wo','wu','gu','chen','ye','hu','ba','ne','excl','q','ellip'])))
print('\n=== 逐角色台词样本 ===')
for k in ['刘备','曹操','关羽','张飞','袁绍','诸葛亮','荀彧','吕布','孙权','贾诩','郭嘉','赵云','鲁肃','周瑜','董卓','阴氏','曹仁','司马懿','庞统','张昭']:
    if k in spk and len(spk[k]) >= 5:
        print('\n[%s] n=%d' % (k, len(spk[k])))
        for n, s in spk[k][:6]: print('   CH%d: %s' % (n, s[:80]))

json.dump({'stats': stats,
           'samples': {k: [(n, s) for n, s in v[:60]] for k, v in spk.items() if len(v) >= 5}},
          open(A/'speakers.json','w',encoding='utf-8'), ensure_ascii=False)

# ---------- opener typing (whole first line, regex) ----------
print('\n\n=== 开场定量分类 ===')
cats = defaultdict(int); ex = defaultdict(list)
RE_TIME_HEAD = re.compile(r'^(东汉|初平|建安|光和|中平|兴平|建武|延熹|永汉|次年|翌日|次日|是[日夜]|这日|当日|次日|旬日|数月|转眼|入[夜秋])')
RE_DATE = re.compile(r'^[\u4e00-\u9fff]{2,4}(元年|二年|三年|四年|五年|六年|七年|八年|九年|十年|年)[，,]')
RE_PLACE = re.compile(r'^[\u4e00-\u9fff]{2,5}(县|郡|城|州|关|营|宫|府|堂|门|亭|驿|渡|塞|道|坞|邑)[，,]?')
RE_DIALOG = re.compile(r'^[“「]')
RE_PERSON = re.compile(r'^(刘备|曹操|袁绍|吕布|孙策|孙权|荀彧|诸葛亮|关羽|张飞|张辽|赵云|贾诩|郭嘉|董卓|刘表|刘璋|袁术|陶谦|公孙瓒|鲁肃|周瑜|太史慈|庞统|法正|李典|于禁|乐进|许褚|典韦|陈宫|陈群|田丰|沮授|张昭|诸葛瑾|司马懿|曹仁|夏侯惇|夏侯渊|荀攸|满宠|崔琰|孙乾|糜竺|毛玠|高柔|管亥|韩牧|刘和|赵震|阴氏|西门|曹豹|张纮|刘晔|蒋干|黄忠|魏延|马超|韩遂|张鲁|刘虞|朱儁|皇甫嵩|卢植|何进|蔡邕|孔融|郑玄|管宁|邴原|王烈|徐庶|石韬|孟建|诸葛亮|刘琦|刘琮|刘禅|吴氏|孙氏|甘氏|糜氏)')
RE_TRANS = re.compile(r'^(与此同时|同一时间|此时此刻|话分两头|且说|却说|另一边|远方|而在|与此同[时]|视线|镜头|再说|远在|数百里|千里之[外外]|长安|洛阳|许[都县]|邺城|江东|荆州|益州|幽州|凉州|交州|扬州|徐州|青州|兖州|豫州|司隶|并州|冀州)')
RE_ABSTRACT = re.compile(r'^(所谓|自古|从来|任何人|天下|世人|后世|历史|一个人|有些|很多|这[是些]|那[是些]|若[是要]|大[凡抵]|一[个切]|须知|常言)')
for c in chapters:
    ps = paras(c)
    if not ps: continue
    f = ps[0]
    if RE_DIALOG.match(f): k = '对话开场'
    elif RE_DATE.match(f) or RE_TIME_HEAD.match(f): k = '纪年/时间戳'
    elif RE_TRANS.match(f): k = '异地/平行场景切换'
    elif RE_PLACE.match(f[:8]): k = '地名定位'
    elif RE_PERSON.match(f): k = '人物直接动作'
    elif RE_ABSTRACT.match(f): k = '议论/箴言'
    else: k = '其他（承接叙述）'
    cats[k] += 1
    if len(ex[k]) < 4: ex[k].append((c['n'], f[:100]))
tot = sum(cats.values())
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    print('  %s: %d (%.1f%%)' % (k, v, 100*v/tot))
    for n, s in ex[k][:2]: print('      CH%d %s' % (n, s))
print('\n   首行字数 avg %.1f median %s' % (
    sum(han(paras(c)[0]) for c in chapters)/len(chapters),
    st.median([han(paras(c)[0]) for c in chapters])))
json.dump({'open_cats': dict(cats)}, open(A/'openers.json','w',encoding='utf-8'), ensure_ascii=False)
