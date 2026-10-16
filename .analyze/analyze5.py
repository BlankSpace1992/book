# -*- coding: utf-8 -*-
"""Pass 5: correct speaker attribution via verb-suffix split + nearby-name fallback."""
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

# ---- build character name whitelist from raw frequency of 2-4 char name candidates
NAME_HINT = ['刘备','曹操','袁绍','吕布','孙策','孙权','荀彧','荀攸','诸葛亮','关羽','张飞','张辽',
 '赵云','贾诩','郭嘉','董卓','刘表','刘璋','袁术','陶谦','公孙瓒','鲁肃','周瑜','太史慈','庞统',
 '法正','李典','于禁','乐进','许褚','典韦','陈宫','陈群','田丰','沮授','张昭','诸葛瑾','司马懿',
 '曹仁','夏侯惇','夏侯渊','满宠','崔琰','孙乾','糜竺','毛玠','高柔','管亥','韩牧','刘和','赵震',
 '阴氏','西门','曹豹','张纮','刘晔','黄忠','魏延','马超','韩遂','张鲁','刘虞','朱儁','皇甫嵩',
 '卢植','何进','蔡邕','孔融','郑玄','管宁','邴原','王烈','徐庶','石韬','孟建','刘琦','刘琮',
 '刘禅','甘氏','糜氏','刘硕','焦和','张邈','陈登','陈珪','臧霸','孙观','尹礼','吴敦','昌豨',
 '刘备笑','简雍','孙乾','张裔','伊籍','马良','马谡','蒋琬','费祎','董和','刘巴','黄权','李严',
 '孟达','刘封','关平','关兴','张苞','曹丕','曹植','曹彰','曹洪','曹纯','曹休','曹真','夏侯尚',
 '张郃','高览','审配','逢纪','许攸','郭图','颜良','文丑','张燕','公孙度','公孙康','士燮','张津',
 '刘繇','王朗','严白虎','许贡','陈瑀','朱治','程普','黄盖','韩当','蒋钦','周泰','吕蒙','陆逊',
 '张纮','张温','步骘','诸葛诞','刘岱','桥瑁','王匡','鲍信','张杨','于夫罗','刘豹','轲比能','蹋顿']
WHITE = [n for n in set(NAME_HINT) if n in raw]
WHITE.sort(key=len, reverse=True)
print('whitelist size', len(WHITE))

VERBS = ['沉声道','正色道','拱手道','点头道','摇头道','低声道','大声声道','笑道','说道','问道','答道',
 '叹道','喝道','骂道','回道','应道','言道','劝道','叫道','又说','道','问','答','曰','说','喊']
VRE = re.compile('(' + '|'.join(sorted(VERBS, key=len, reverse=True)) + ')$')

# pattern 1: NAME + filler + VERB：“...”
PAT1 = re.compile(r'([\u4e00-\u9fff]{2,10})：“([^”]{1,400})”')
attrib = defaultdict(list)   # name -> [(ch, line)]
unattr = []
for c in chapters:
    t = c['text']
    for m in PAT1.finditer(t):
        pre, said = m.group(1), m.group(2)
        # split pre into name + verb by scanning longest whitelist name at the end
        nm = None
        for cand in WHITE:
            if pre.endswith(cand):
                nm = cand; break
        if nm is None:
            # try: pre ends with verb, name precedes it
            mm = VRE.search(pre)
            stem = pre[:mm.start()] if mm else pre
            for cand in WHITE:
                if stem.endswith(cand):
                    nm = cand; break
        if nm is None:
            unattr.append((c['n'], pre, said))
            continue
        if 1 <= han(said) <= 400:
            attrib[nm].append((c['n'], said, pre))
print('attributed utterances', sum(len(v) for v in attrib.values()),
      'unattributed', len(unattr))
rows = sorted(((len(v), k) for k, v in attrib.items()), reverse=True)
print('\n人物\t台词数\t均长\t中位\t≤6字%')
for n, k in rows[:26]:
    L = [han(s) for _, s, _ in attrib[k]]
    print('  %s\t%d\t%.1f\t%s\t%d%%' % (k, n, sum(L)/len(L), st.median(L),
          100*sum(1 for v in L if v <= 6)//len(L)))

MK = ['我','吾','孤','臣','也','乎','吧','呢','！','？','…','呵','哈哈','某','俺','岂','莫','必','请']
print('\n=== 语言标记（千字频）===')
print('人物\t' + '\t'.join(MK))
out = {}
for n, k in rows[:16]:
    txt = ''.join(s for _, s, _ in attrib[k]); hh = han(txt)
    d = {x: round(txt.count(x)/hh*1000, 1) for x in MK}
    out[k] = {'n': n, 'per1k': d,
              'avg': round(sum(han(s) for _, s, _ in attrib[k])/n, 1),
              'samples': [(c, s) for c, s, _ in attrib[k][:40]]}
    print('%s\t%s' % (k, '\t'.join(str(d[x]) for x in MK)))

print('\n=== 台词样本（用于报告引用）===')
for k in ['刘备','曹操','张飞','关羽','荀彧','郭嘉','吕布','袁绍','孙权','贾诩','诸葛亮','鲁肃','董卓','阴氏','张昭','赵云','周瑜','司马懿','庞统','黄忠']:
    if k in attrib:
        print('\n[%s] n=%d' % (k, len(attrib[k])))
        for c, s, _ in attrib[k][:7]:
            print('   CH%d: %s' % (c, s[:110]))
json.dump(out, open(A/'voices.json','w',encoding='utf-8'), ensure_ascii=False)
json.dump([(c, p, s) for c, p, s in unattr[:40]], open(A/'unattr.json','w',encoding='utf-8'), ensure_ascii=False)
print('\nsaved voices.json')
