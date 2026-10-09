#!/usr/bin/env python3
"""Build a non-release A4 print-check packet using exact published v0.5.1 pages.

Page 1 is a newly authored printer-calibration and recording sheet; pages 2-11
are unchanged vector page imports from the published PDF. No paper-test result
is inferred. This QA copy does not supersede the 299-page published edition.
"""
from __future__ import annotations
import argparse
import hashlib
import io
from pathlib import Path

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("deliverables/releases/v0.5.1/zitie-v0.5.1-A4.pdf")
OUTPUT = Path("qa/print/v0.5.1/v051-print-acceptance-samples-A4.pdf")
SOURCE_SHA256 = "7fb6c7227258903828098c29368f0412a7b8621260d3d5f8ad91f45beba5eb90"
SOURCE_PAGES = (1, 2, 6, 34, 263, 264, 265, 284, 292, 299)
CJK_FONT = Path("/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf")
MILLIMETRE = 72.0 / 25.4
A4_SIZE = (A4[0], A4[1])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calibration_page() -> bytes:
    assert CJK_FONT.is_file(), "The public repo must not contain a source font"
    pdfmetrics.registerFont(TTFont("PrintQAKaiti", str(CJK_FONT)))
    b = io.BytesIO()
    c = canvas.Canvas(b, pagesize=A4, invariant=1, pageCompression=1)
    w, h = A4
    c.setTitle("v0.5.1 印刷代表页验收与尺寸校准")
    c.setAuthor("netplus/zitie QA - no physical test performed")

    def txt(y, content, size=10, x=36, fill=colors.black):
        c.setFont("PrintQAKaiti", size)
        c.setFillColor(fill)
        c.drawString(x, y, content)

    txt(h-48, "《循序渐进汉字部首字帖》v0.5.1 实物打印验收", 16)
    txt(h-76, "本页只提供打印设置与记录栏，不能替代真实打印与纸面检查。", 9)
    txt(h-93, "后续10页依次对应原书：1、2、6、34、263、264、265、284、292、299。", 9)

    txt(h-122, "打印设置：A4纸；100% / 实际大小；关闭“适应页面”与自动缩放。", 10)
    txt(h-139, "应记录：打印机、驱动/软件、单双面、纸张类型、色彩模式和实际结果。", 9)
    txt(h-164, "尺寸校准：纸面测量下方黑色校准线，应约为100 mm（建议偏差不超过1 mm）。", 9)
    x0, y0, length = 56, h-214, 100*MILLIMETRE
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.2)
    c.line(x0,y0,x0+length,y0)
    for i in range(0,101,10):
        x=x0+i*MILLIMETRE
        c.line(x,y0-5,x,y0+6)
        if i in (0,50,100):
            txt(y0+12, f"{i} mm", 8, x=max(36, x-15))
    txt(y0-24, "实测校准线：________ mm      打印比例：________ %", 9)

    txt(h-280, "色彩/灰度区分参考：当前笔（红）  以前笔（灰）  淡描红  黑色正文", 9)
    for j,col in enumerate((colors.HexColor("#C93434"),colors.HexColor("#666666"),colors.HexColor("#D3D3D3"),colors.black)):
        c.setFillColor(col);c.setStrokeColor(colors.HexColor("#777777"))
        c.rect(56+j*85,h-315,70,19,fill=1,stroke=1)
    txt(h-337, "纸上应能清晰区分红色当前笔与灰色旧笔，淡字不能淡到难以识别。", 9)

    txt(h-374, "代表页检查项目（均须在纸张上确认）", 11)
    checks = [
        "A4原始比例；格线长度与位置，无截边/异常缩放",
        "1/2/292/299页：说明、版本、中文标点、字体不缺字",
        "6/34/263页：田字格、逐笔颜色、描红深浅与完整度",
        "264/265/284页：比较、回忆、整字迁移与复杂布局",
        "红/灰及单色打印下笔画和淡灰范字可辨性",
        "装订留白、拼音、来源标记、页眉和页脚",
    ]
    for n, line in enumerate(checks):
        y=h-399-n*25
        c.setStrokeColor(colors.black);c.setLineWidth(.75);c.rect(56,y-2,10,10,fill=0,stroke=1)
        txt(y, line, 9, 77)
    txt(h-566, "设备/驱动：_________________________________________________________", 9)
    txt(h-590, "色彩/纸张：_________________________________________________________", 9)
    txt(h-614, "实际检查日期：__________________  记录人员：____________________", 9)
    txt(h-638, "结论（勾选）：通过 [   ]    有问题 [   ]    尚未打印 [   ]", 9)
    txt(h-665, "问题/页码：_________________________________________________________", 9)
    txt(h-686, "__________________________________________________________________", 9)
    txt(h-725, "源文件SHA256（只读校验）：", 8)
    c.setFont("Helvetica", 7)
    c.drawString(36,h-741,SOURCE_SHA256)
    txt(h-768, "此包仅供打印测试；正式交付仍为299页v0.5.1原PDF。", 8)
    c.save()
    return b.getvalue()


def build(repo: Path=ROOT, dest: Path | None=None) -> dict:
    repo=Path(repo)
    src=repo/SOURCE
    out=Path(dest) if dest is not None else repo/OUTPUT
    if src.resolve()==out.resolve():raise ValueError("Must never overwrite official PDF")
    if digest(src)!=SOURCE_SHA256:raise ValueError("Published v0.5.1 bytes changed")
    out.parent.mkdir(parents=True,exist_ok=True)
    source=fitz.open(src)
    result=fitz.open()
    try:
        if len(source)!=299:raise ValueError("Unexpected source page count")
        calibration=fitz.open(stream=calibration_page(),filetype="pdf")
        try:result.insert_pdf(calibration,from_page=0,to_page=0)
        finally:calibration.close()
        for n in SOURCE_PAGES:
            result.insert_pdf(source,from_page=n-1,to_page=n-1,links=False,annots=False)
        result.set_metadata({"title":"v0.5.1 QA print samples (not a new book release)",
            "subject":"Pages: "+",".join(map(str,SOURCE_PAGES)),
            "keywords":"A4;100percent;physical-print-pending;sha256:"+SOURCE_SHA256,
            "creator":"netplus/zitie print QA helper"})
        result.save(out,garbage=4,deflate=True,no_new_id=True)
    finally:
        result.close();source.close()
    return {"source_sha256":SOURCE_SHA256,"sample_pages":list(SOURCE_PAGES),
            "sheet_pages":1+len(SOURCE_PAGES),"size":out.stat().st_size,
            "sha256":digest(out),"physical_print_test_performed":False,
            "official_publication_replaced":False,"path":str(out)}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=ROOT)
    ap.add_argument("--output",type=Path,default=None)
    args=ap.parse_args()
    import json
    print(json.dumps(build(args.repo,args.output),ensure_ascii=False,indent=2))
