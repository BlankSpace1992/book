# -*- coding: utf-8 -*-
"""Pass 6: precise, verified dialogue attribution (local window + verb adjacency)."""
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

NAME_HINT = ['刘备','曹操','袁绍','吕布','孙策','孙权','荀彧','荀攸','诸葛亮','关羽','张飞','张辽',
 '赵云','贾诩','郭嘉','董卓','刘表','刘璋','袁术','陶谦','公孙瓒','鲁肃','周瑜','太史慈','庞统',
 '法正','李典','于禁','乐进','许褚','典韦','陈宫','陈群','田丰','沮授','张昭','诸葛瑾','司马懿',
 '曹仁','夏侯惇','夏侯渊','满宠','崔琰','孙乾','糜竺','毛玠','高柔','管亥','韩牧','刘和','赵震',
 '阴氏','西门','曹豹','张纮','刘晔','黄忠','魏延','马超','韩遂','张鲁','刘虞','朱儁','皇甫嵩',
 '卢植','何进','蔡邕','孔融','郑玄','管宁','邴原','王烈','徐庶','石韬','孟建','刘琦','刘琮',
 '刘禅','甘氏','糜氏','刘硕','焦和','张邈','陈登','陈珪','臧霸','孙观','尹礼','吴敦','昌豨',
 '简雍','张裔','伊籍','马良','马谡','蒋琬','费祎','董和','刘巴','黄权','李严','孟达','刘封',
 '关平','关兴','张苞','曹丕','曹植','曹彰','曹洪','曹纯','曹休','曹真','夏侯尚','张郃','高览',
 '审配','逢纪','许攸','郭图','颜良','文丑','张燕','公孙度','士燮','刘繇','王朗','严白虎',
 '陈瑀','朱治','程普','黄盖','韩当','蒋钦','周泰','吕蒙','陆逊','步骘','刘岱','王匡','鲍信',
 '张杨','轲比能','蹋顿','贾琮','刘焉','刘虞','董承','伏完','王子服','吴硕','种辑','吉平','吉本',
 '韦晃','金祎','耿纪','荀悦','钟繇','王粲','陈琳','杨修','丁仪','丁廙','刘勋','张勋','乔蕤',
 '雷薄','陈兰','纪灵','张闿','曹宏','笮融','薛礼','孙贲','吴景','徐琨','孙静','孙翊','孙匡']
WHITE = sorted(set(n for n in NAME_HINT if n in raw), key=len, reverse=True)
SET = set(WHITE)

# verb list, longest first
VERBS = ['沉声道','正色道','拱手道','点头道','摇头道','低声道','大声道','笑道','说道','问道','答道',
 '叹道','喝道','骂道','回道','应道','言道','劝道','叫道','又道','又说','反问道','道','问','答',
 '曰','说','喊','嚷嚷','吩咐','嘟囔','念叨']
VL = sorted(VERBS, key=len, reverse=True)

PAT = re.compile(r'：“([^”]{1,400})”')
res = defaultdict(list)
for c in chapters:
    t = c['text']
    for m in PAT.finditer(t):
        said = m.group(1)
        # window before the colon
        w = t[max(0, m.start()-24):m.start()]
        nm = None
        # 1) name immediately followed by (optional marker) + verb, verb at window end
        for v in VL:
            if w.endswith(v):
                stem = w[:-len(v)]
                # nearest whitelist name at the end of stem
                for cand in WHITE:
                    if stem.endswith(cand):
                        nm = cand; break
                if nm is None:
                    for cand in WHITE:
                        if cand in stem[-8:]:
                            nm = cand; break
                break
        # 2) fallback: nearest name anywhere in the 24-char window
        if nm is None:
            best, bi = None, -1
            for cand in WHITE:
                i = w.rfind(cand)
                if i > bi: best, bi = cand, i
            if bi >= 0 and bi + 2 >= len(w) - 12:
                nm = best
        if nm is None:
            # 3) look further back in the same paragraph (speaker established earlier)
            ps = t.rfind('\n', 0, m.start())
            para = t[ps+1:m.start()]
            for cand in WHITE:
                i = para.rfind(cand)
                if i >= 0 and len(para) - i < 30:
                    nm = cand; break
        if nm:
            res[nm].append((c['n'], said, w[-16:]))
print('total quotes', len(PAT.findall(raw)), 'attributed', sum(len(v) for v in res.values()))

rows = sorted(((len(v), k) for k, v in res.items()), reverse=True)
print('\n人物\t台词\t均长\t中位\t短台词(<=6)%')
for n, k in rows[:30]:
    L = [han(s) for _, s, _ in res[k]]
    print('  %s\t%d\t%.1f\t%s\t%d%%' % (k, n, sum(L)/len(L), st.median(L),
          100*sum(1 for v in L if v <= 6)//len(L)))

out = {}
MK = ['我','吾','孤','臣','也','乎','吧','呢','！','？','…','呵','岂','莫','请','敢','愿','必','某']
print('\n=== 千字频语言标记 ===')
print('人物\t' + '\t'.join(MK))
for n, k in rows[:18]:
    txt = ''.join(s for _, s, _ in res[k]); hh = han(txt)
    d = {x: round(txt.count(x)/hh*1000, 1) for x in MK}
    out[k] = {'n': n, 'avg': round(sum(han(s) for _, s, _ in res[k])/n, 1), 'per1k': d}
    print('%s\t%s' % (k, '\t'.join(str(d[x]) for x in MK)))

print('\n=== 台词样本（供报告引用核对）===')
for k in ['刘备','曹操','张飞','关羽','荀彧','郭嘉','吕布','袁绍','孙权','贾诩','诸葛亮','鲁肃',
          '董卓','阴氏','张昭','赵云','周瑜','司马懿','庞统','黄忠','孙策','糜竺','简雍','田丰',
          '沮授','陈宫','许攸','刘表','陶谦','公孙瓒','刘璋','管亥','典韦','许褚','乐进','于禁']:
    if k in res and len(res[k]) >= 3:
        print('\n[%s] n=%d 均长%.1f' % (k, len(res[k]),
              sum(han(s) for _, s, _ in res[k])/len(res[k])))
        for c, s, ctx in res[k][:8]:
            print('   CH%d: %s   <<%s' % (c, s[:100], ctx))
json.dump({'stats': out,
           'samples': {k: [(c, s) for c, s, _ in v] for k, v in res.items() if len(v) >= 3}},
          open(A/'voices2.json','w',encoding='utf-8'), ensure_ascii=False)
print('\nsaved voices2.json')
