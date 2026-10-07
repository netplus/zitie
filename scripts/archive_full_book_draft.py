#!/usr/bin/env python3
"""Archive the verified P7 full-book research draft and register exact bytes."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build/B01-B21_with_preface_draft_A4.pdf'
DEST=ROOT/'deliverables/drafts/v0.3.0/B01-B21_with_preface_draft_A4.pdf'
MANIFEST=ROOT/'deliverables/manifest.json'
REVIEW_REL='reviews/v0.3.0-full-book-draft-ci.md'
REVIEW=ROOT/REVIEW_REL

if not BUILD.is_file():
    raise FileNotFoundError(BUILD)

data=BUILD.read_bytes()
sha=hashlib.sha256(data).hexdigest()
pages=len(PdfReader(str(BUILD)).pages)
if pages != 261:
    raise ValueError(f'Expected 261-page full-book draft, got {pages}')

source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
run_id=os.environ.get('GITHUB_RUN_ID')
if not run_id or not run_id.isdigit():
    raise ValueError('GITHUB_RUN_ID is required for archival provenance')

manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
path_rel=DEST.relative_to(ROOT).as_posix()
existing=next((x for x in manifest['artifacts'] if x['path']==path_rel),None)

if existing:
    if existing['sha256'] != sha or existing['bytes'] != len(data) or existing['pages'] != pages:
        raise ValueError('Existing v0.3.0 archive differs from rebuilt draft; use a new version instead of overwriting')
    print('Archive already registered with identical bytes:',path_rel)
    raise SystemExit(0)

DEST.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(BUILD,DEST)

review=f"""# v0.3.0 全书编写稿 CI 归档记录

日期：2026-10-07  
状态：draft，非正式release。

- 文件：`{path_rel}`
- 页数：{pages}
- 字节数：{len(data)}
- SHA256：`{sha}`
- source commit：`{source_commit}`
- workflow run：`{run_id}`
- P6全书layout review：`reviews/P6-full-book-layout-review-20261007.md`

本记录只说明该PDF由目标源码在CI中实际生成、通过结构预检并永久归档。
内容层/P6已有review不因归档自动升级为正式发布；GF0011—2022既有
`source_blocked_fail_closed` 与其它 `conflict_fail_closed` 均保持。
P7的目录/索引/附形回归/最终逐页QA、manifest终审、目标HEAD CI和正式release仍需继续。
"""
REVIEW.write_text(review,encoding='utf-8')

manifest['artifacts'].append({
    'path':path_rel,
    'title':'《循序渐进汉字部首字帖》全书编写稿',
    'version':'0.3.0',
    'status':'draft',
    'batch':'B01-B21',
    'pages':pages,
    'bytes':len(data),
    'sha256':sha,
    'source_commit':source_commit,
    'workflow_run_id':int(run_id),
    'review_record':REVIEW_REL,
    'layout_review_record':'reviews/P6-full-book-layout-review-20261007.md',
    'release_eligible':False
})
MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'path':path_rel,'pages':pages,'bytes':len(data),'sha256':sha,'source_commit':source_commit,'workflow_run_id':int(run_id)},ensure_ascii=False))
