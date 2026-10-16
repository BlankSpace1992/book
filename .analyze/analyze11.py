# -*- coding: utf-8 -*-
import re
from pathlib import Path
raw = Path(r"D:\Book\.analyze\chapters.txt").read_text(encoding="utf-8")
hits = list(re.finditer(r"原文", raw))
print("原文 出现次数:", len(hits))
for m in hits[:6]:
    p = m.start()
    print("  ...", raw[max(0, p-90):p+90].replace("\n", "|"))
print()
for pat in ["掺扶", "以优击劣", "袖服", "旨有", "朓望", "惟", "@"]:
    print("  %s: %d" % (pat, raw.count(pat)))
for m in list(re.finditer(r".{50}@.{50}", raw))[:6]:
    print("   @样本:", m.group(0).replace("\n", "|"))
# does the raw file (with junk) contain something my cleaning stripped?
orig = Path(r"C:\Users\yu459\Downloads\慢着，请别叫我昭烈帝.txt").read_text(encoding="utf-8")
oi = list(re.finditer(r"原文", orig))
print("\n原文件「原文」出现:", len(oi))
for m in oi[:4]:
    p = m.start(); print("  ...", orig[max(0,p-100):p+100].replace("\n", "|"))
