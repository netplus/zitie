#!/usr/bin/env python3
"""One-time transfer of actually reviewed B02 evidence and tested renderer edits."""
from pathlib import Path
import json
import shutil
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def put(p,x):(ROOT/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def replace_once(p,old,new):
    f=ROOT/p;t=f.read_text(encoding='utf-8')
    if old not in t:raise ValueError('Unexpected source in '+p)
    f.write_text(t.replace(old,new),encoding='utf-8')

def main():
    b=load('data/B02.json')
    if b['version']=='0.2.1-draft':
        print('v0.2.1 migration already recorded; no changes.');return
    if b['version']!='0.2.0-draft':raise ValueError('Only v0.2.0 may be migrated')
    pron={
      '水':('shuǐ',48,42,'一级1527','水','shuǐ','独立词条'),
      '火':('huǒ',39,33,'一级719','火','huǒ','独立词条'),
      '木':('mù',75,69,'二级1634','木','mù','独立词条'),
      '日':('rì',46,40,'一级1371','日','rì','独立词条'),
      '月':('yuè',53,47,'一级2012','月','yuè','独立词条'),
      '田':('tián',82,76,'二级2277','田','tián','独立词条'),
      '目':('mù',75,69,'二级1635','目光','mùguāng','取首语素；不冒充独立目字条'),
      '手':('shǒu',48,42,'一级1499','手','shǒu','独立词条'),
      '牛':('niú',44,38,'一级1192','牛（名）','niú','采用名词读音'),
      '毛':('máo',74,68,'二级1549','毛','máo','独立词条')}
    assert set(pron)=={e['character'] for e in b['entries']}
    for e in b['entries']:
        p,pdf,printed,num,word,reading,note=pron[e['character']]
        assert e['pinyin']==p
        e['pronunciation_evidence']={'source_id':'S06','pdf_page':pdf,'printed_page':printed,'entry_number':num,'entry':word,'entry_pinyin':reading,'adopted_pinyin':p,'usage':note,'result':'matched','reviewed_at':'2026-09-29'}
        if e['character'] in '日目田':
            e['artwork_override']='data/artwork/terminal-overrides-v1.json'
            e['artwork_notice']='横折收笔按已核笔形作教学整理；不是规范原图。'
    b.update(version='0.2.1-draft',status='content_cross_checked_scope_pending',metadata_review='passed',metadata_review_record='reviews/B02-completion.md',artwork_review={'status':'passed','reviewer':'ChatGPT','date':'2026-09-29','record':'reviews/B02-completion.md','notes':'3个指定横折的末端已定点整理；其余笔画和月字全部原始路径保持不变。'},layout_review={'status':'passed','reviewer':'ChatGPT','date':'2026-09-29','record':'reviews/v0.2.1-layout.md','scope':'已查看前言3页及B02全部10页；B01逐页像素不变。CI产物须与本地已看稿匹配后归档。'},release_eligible=False,remaining_gates=['GF0011—2022全文及目标版主项身份核验'],draft_label='编写稿｜本批内容已复核；2022版部首表范围核验仍待完成。')
    put('data/B02.json',b)
    bs=load('data/batches.json');bs['frozen_batches'][1]['status']=b['status'];put('data/batches.json',bs)
    s=load('sources/catalog.json')
    for src in s['sources']:
        if src['id']=='S06':
            src['reviewed_pdf_pages']=sorted(set(src['reviewed_pdf_pages'])|{x[1] for x in pron.values()})
            src['limits']+=' B02的目取目光首语素，其他九项为独立词条。'
        if src['id']=='S02':
            src['pdf_pages_reviewed']=sorted(set(src['pdf_pages_reviewed'])|set(b['primary_review']['pdf_pages']))
            src['printed_pages_reviewed']=[x-6 for x in src['pdf_pages_reviewed']]
            src['status']='acquired_B01_B02_selected_rows_reviewed'
    put('sources/catalog.json',s)
    shutil.copyfile(ROOT/'build/vectors/ARPHICPL.TXT',ROOT/'data/artwork/ARPHICPL.TXT')
    p='scripts/build_batch.py'
    replace_once(p,'from validate_project import load, validate','from validate_project import load, validate\nfrom apply_artwork import apply_artwork')
    replace_once(p,'W,H = A4',"BOOK = load('data/book-config.json')\nW,H = A4")
    replace_once(p,"text(c,LEFT,43,'依据：GF0023—2020，第'+str(e['primary_printed_page'])+'页；矢量：Hanzi Writer / Arphic PL。',8,color='muted')","artnote='；横折收笔已整理。' if e.get('artwork_override') else '。'\n    text(c,LEFT,43,'依据：GF0023—2020，第'+str(e['primary_printed_page'])+'页；矢量：Hanzi Writer / Arphic PL'+artnote,8,color='muted',width=RIGHT-LEFT)")
    replace_once(p,"'编写中 v0.2｜201主项为全书目标，不代表正文已全部审定。'","'编写中 v'+BOOK['version']+'｜201主项为全书目标，不代表正文已全部审定。'")
    replace_once(p,"d=prepare(json.loads(raw),len(e['stroke_names'])); make_page(c,e,d,i,args.draft,batch)","artwork,audit=apply_artwork(e['character'],raw)\n        d=prepare(artwork,len(e['stroke_names'])); make_page(c,e,d,i,args.draft,batch)")
    replace_once(p,"'sha256':hashlib.sha256(raw).hexdigest(),'practice_cells':32","'sha256':hashlib.sha256(raw).hexdigest(),'artwork_audit':audit,'practice_cells':32")
    replace_once(p,"pre=out/'preface_v0.2.pdf'","pre=out/BOOK['preface_file']")
    replace_once('scripts/build_collection.py','from pathlib import Path','from pathlib import Path\nimport json')
    replace_once('scripts/build_collection.py',"files=['preface_v0.2.pdf','B01_draft_A4.pdf','B02_draft_A4.pdf']","book=json.loads((ROOT/'data/book-config.json').read_text(encoding='utf-8'))\nfiles=[book['preface_file']]+[b+'_draft_A4.pdf' for b in book['built_batches']]")
    p='book/front-matter/preface.md'
    replace_once(p,'编写中 v0.2。','编写中 v0.2.1。')
    replace_once(p,'已完成两部规范的笔顺图对照，读音与部分收笔字形仍待复核。两批按各自复核状态标识，不能把第一批的结论自动套给第二批。','已补齐本页读音出处，并完成日、目、田三个横折收笔的教学整理；月的横折钩保持不变。两批均保留逐项记录，不能将本批结论推广到尚未编写的条目。')
    replace_once(p,'正式制图前，还要把每条笔画路径与所采用的顺序逐一对照。','正式制图前，还要把每条笔画路径与所采用的顺序逐一对照。需整理字体回锋时，保留原始文件及修改记录，明确标注教学字形整理，不冒充规范发布机构的原图。')
    replace_once('.github/workflows/book-checks.yml','python scripts/acquire_vectors.py --batches B01 B02','python scripts/acquire_vectors.py --batches B01 B02\n          python scripts/test_artwork.py')
    p=ROOT/'README.md';t=p.read_text(encoding='utf-8')
    t=t.replace('v0.2.0/','v0.2.1/').replace('preface_v0.2.pdf','preface_v0.2.1.pdf')
    t=t.replace('| B02常见独体形 | 10项笔顺原件对照、10页编写稿 | 读音证据；日、目、田的横折末端字形 |','| B02常见独体形 | 10项笔顺、读音及收笔整理复核完成 | 全书2022版范围门槛 |')
    t=t.replace('[本轮版式与字形问题记录](reviews/v0.2-layout.md)','[第二批收尾复核](reviews/B02-completion.md) · [本轮版式回归](reviews/v0.2.1-layout.md)')
    t=t.replace('python scripts/acquire_vectors.py --batches B01 B02','python scripts/acquire_vectors.py --batches B01 B02\npython scripts/test_artwork.py');p.write_text(t,encoding='utf-8')
    p=ROOT/'CHANGELOG.md';p.write_text('# 版本变更\n\n## v0.2.1 — 2026-09-29\n\nB02十项采用读音原件定位完成；日、目、田第2笔定点整理，月不变。实际检查前言3页和B02十页，B01十页像素回归。新增10项字形整理测试、版本配置和已审PDF归档流程。主项仍20，内容字段补齐增至20，正式发布仍0。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
    p=ROOT/'deliverables/README.md';p.write_text('# PDF版本归档\n\n## v0.2.1：第二批收尾修订\n\n[前言＋前20项，23页](drafts/v0.2.1/B01-B02_with_preface_draft_A4.pdf) · [B02十页](drafts/v0.2.1/B02_draft_A4.pdf) · [前言三页](drafts/v0.2.1/preface_v0.2.1.pdf)\n\n本版补齐B02采用读音，整理日、目、田横折末端；没有新增主项，仍为编写稿。旧版不替换，实际字节以manifest登记为准。\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
    print('Recorded already-reviewed B02 content and tested renderer edits; publication remains blocked.')

if __name__=='__main__':main()
