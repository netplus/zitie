#!/usr/bin/env python3
"""Record the issues found by actually inspecting v0.2 pages, then rebuild for recheck."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'scripts/build_batch.py';s=p.read_text()
s=s.replace('SimpleDocTemplate, Paragraph, Spacer','SimpleDocTemplate, Paragraph, Spacer, KeepTogether')
old="story.append(Paragraph(html.escape(block).replace('\\n','<br/>'),style))"
new="paragraph=Paragraph(html.escape(block).replace('\\n','<br/>'),style)\n        story.append(KeepTogether([paragraph]) if block.startswith('本字帖采用A4') else paragraph)"
if old in s:s=s.replace(old,new)
elif new not in s:raise ValueError('Unexpected renderer baseline')
p.write_text(s,encoding='utf-8')
p=R/'book/front-matter/preface.md';s=p.read_text().replace('已完成两部规范的笔顺图对照，读音等字段仍待补齐。','已完成两部规范的笔顺图对照，读音与部分收笔字形仍待复核。')
p.write_text(s,encoding='utf-8')
p=R/'data/B02.json';b=json.loads(p.read_text())
b['artwork_review']={'status':'sequence_matched_terminal_shape_pending','reviewer':'ChatGPT','date':'2026-09-29','record':'reviews/v0.2-layout.md','notes':'42笔的累积顺序与已核原件相符；日、目、田的横折末端存在容易被理解为钩的楷体回锋，正式用稿前需单独解决。'}
b['draft_label']='编写稿｜笔顺原件已核；读音与部分收笔字形仍待复核。'
b['remaining_gates']=['读音逐项证据','日、目、田的横折收笔形态','GF0011—2022全文及目标版主项身份核验']
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
