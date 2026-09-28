# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 리포트 md → PDF (Chrome/Edge 헤드리스 인쇄).

md 의 `![..](x.svg)` 차트를 본문에 **인라인**으로 넣어 한 파일로 만든다(외부 파일 참조 없음).
py37_32 의 matplotlib/PIL 은 DLL 오류로 못 쓰므로 브라우저 인쇄를 쓴다.
"""
import os
import re
import subprocess
import tempfile

import markdown

BROWSERS = (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")

CSS = """
@page { size: A4 landscape; margin: 10mm 9mm; }
body { font-family: 'Malgun Gothic', sans-serif; font-size: 10.5px; color: #1f2328; line-height: 1.45; }
h1 { font-size: 19px; border-bottom: 2px solid #1f2328; padding-bottom: 4px; margin: 0 0 6px; }
h2 { font-size: 14px; margin: 14px 0 6px; padding: 3px 8px; background: #f0f3f6; border-left: 4px solid #0969da; }
h3 { font-size: 12px; margin: 10px 0 4px; }
blockquote { margin: 4px 0; padding: 2px 10px; color: #59636e; border-left: 3px solid #d1d9e0; }
table { border-collapse: collapse; width: 100%; margin: 4px 0 8px; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #d1d9e0; padding: 3px 5px; text-align: left; vertical-align: top; }
th { background: #f6f8fa; }
code { background: #f6f8fa; padding: 0 3px; border-radius: 3px; }
svg { width: 100%; height: auto; }
.chart { page-break-inside: avoid; }
ul { margin: 4px 0; padding-left: 18px; }
"""


def md_to_pdf(md_path: str, pdf_path: str = None) -> str:
    md_path = os.path.abspath(md_path)
    pdf_path = pdf_path or os.path.splitext(md_path)[0] + ".pdf"
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    body = markdown.markdown(text, extensions=["tables"])
    # ![..](x.svg) → 인라인 SVG
    def _inline(m):
        p = os.path.join(os.path.dirname(md_path), m.group(1))
        if not os.path.exists(p):
            return m.group(0)
        with open(p, encoding="utf-8") as f:
            return '<div class="chart">%s</div>' % f.read()
    body = re.sub(r'<p><img alt="[^"]*" src="([^"]+\.svg)"\s*/?></p>', _inline, body)
    html = '<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (CSS, body)
    exe = next((b for b in BROWSERS if os.path.exists(b)), None)
    if exe is None:
        raise RuntimeError("Chrome/Edge 없음 — PDF 인쇄 불가")
    fd, tmp = tempfile.mkstemp(suffix=".html")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)
    try:
        subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        "--print-to-pdf=%s" % pdf_path, "file:///" + tmp.replace("\\", "/")],
                       check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.remove(tmp)
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF 가 만들어지지 않았다: %s" % pdf_path)
    return pdf_path
