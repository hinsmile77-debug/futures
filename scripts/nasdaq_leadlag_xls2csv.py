"""[MW0601 2026-10-02] 키움 영웅문Global 차트 「엑셀 저장」(.xls = BIFF2) → CSV. 표준 라이브러리만 사용.
사용: python scripts/nasdaq_leadlag_xls2csv.py <in.xls> <out.csv>
"""
# BIFF2 최소 파서: LABEL(0x04) / NUMBER(0x03) / INTEGER(0x02) 셀만 읽는다
import struct, sys, csv
p = sys.argv[1]; out = sys.argv[2]
b = open(p, 'rb').read()
cells = {}
i = 0
while i + 4 <= len(b):
    rt, ln = struct.unpack_from('<HH', b, i); d = b[i+4:i+4+ln]; i += 4 + ln
    if rt in (0x03, 0x04, 0x02) and ln >= 7:
        r, c = struct.unpack_from('<HH', d, 0)
        if rt == 0x03: v = struct.unpack_from('<d', d, 7)[0]
        elif rt == 0x02: v = struct.unpack_from('<H', d, 7)[0]
        else:
            n = d[7]; v = d[8:8+n].decode('cp949', 'replace')
        cells[(r, c)] = v
    if rt == 0x0A: break
R = max(r for r, _ in cells) + 1; C = max(c for _, c in cells) + 1
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    for r in range(R): w.writerow([cells.get((r, c), '') for c in range(C)])
print('rows', R, 'cols', C)
