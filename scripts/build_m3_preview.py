#!/usr/bin/env python3
"""Build all M3 teaching modules as an engineering preview, never a release."""
import argparse
import hashlib
import io
import json
import math
import re
import subprocess
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from apply_artwork import apply_artwork
from build_batch import LEFT, RIGHT, setup_fonts, prepare, make_entry_pages, grid, glyph, reviewed_stroke_names
from build_book_matter import page_count, stroke_count
from m3_model import ROOT, CONFIG, M3Edition, authorize, digest, display_entry, read_model
from m3_migration import RECORD as MIGRATION_RECORD, read_migrations
from verify_m2_closeout import load, require

W, H = A4
L, R = 42, W - 42


def line(c, x, y, value, size=11, font='M3Body', width=None):
    value = str(value)
    face = pdfmetrics.getFont(font).face
    missing = [ch for ch in value if not ch.isspace() and not face.charToGlyph.get(ord(ch))]
    require(not missing, 'Missing glyph: ' + ''.join(missing))
    require(width is None or pdfmetrics.stringWidth(value, font, size) <= width, 'Text exceeds fixed width')
    c.setFont(font, size); c.drawString(x, y, value)


def wrap_lines(value, width, size):
    """Keep closing punctuation off line starts and technical tokens intact."""
    result=[]
    for explicit in value.split('\n'):
        tokens=[]; opening=''
        for token in re.findall(r'[A-Za-z0-9]+(?:[./—-][A-Za-z0-9]+)*|.', explicit):
            if token in '（《【“‘':
                opening+=token; continue
            token=opening+token; opening=''
            if token in '，。、；：！？）》】”’' and tokens:
                tokens[-1]+=token
            else:
                tokens.append(token)
        if opening: tokens.append(opening)
        groups=[]; current=[]
        for token in tokens:
            require(pdfmetrics.stringWidth(token,'M3Body',size)<=width,'Unbreakable token exceeds width')
            if current and pdfmetrics.stringWidth(''.join(current)+token,'M3Body',size)>width:
                groups.append(current);current=[token]
            else: current.append(token)
        groups.append(current)
        # Avoid a final orphan fragment while keeping punctuation/token groups intact.
        minimum=min(6*size,width/2)
        while len(groups)>1 and len(groups[-2])>1 and pdfmetrics.stringWidth(''.join(groups[-1]),'M3Body',size)<minimum:
            if pdfmetrics.stringWidth(groups[-2][-1]+''.join(groups[-1]),'M3Body',size)>width:break
            groups[-1].insert(0,groups[-2].pop())
        result.extend(''.join(group) for group in groups)
    return result


def paragraph(c, x, y, value, width=R-L, size=12, leading=21):
    lines=wrap_lines(value,width,size)
    require(y - max(0, len(lines)-1)*leading >= 60, 'Page overflow; paginate instead of truncating')
    for text in lines:
        line(c, x, y, text, size, width=width); y -= leading
    return y


def header(c, title, subtitle=''):
    c.setFillColorRGB(.68, .18, .21)
    line(c, L, H-52, title, 23, width=R-L)
    c.setFillColorRGB(.22, .23, .24)
    if subtitle:
        paragraph(c, L, H-77, subtitle, size=10, leading=15)
    c.setStrokeColorRGB(.80, .66, .68); c.line(L, H-96, R, H-96)


def new_canvas(path):
    return canvas.Canvas(str(path) if isinstance(path, Path) else path, pagesize=A4, pageCompression=1, invariant=1)


def guidance(path, content):
    c = new_canvas(path)
    for page in content['pages']:
        header(c, page['title'], page['subtitle'])
        y = H-132
        for section in page['sections']:
            c.setFillColorRGB(.68, .18, .21)
            line(c, L, y, section['heading'], 15, width=R-L); y -= 25
            c.setFillColorRGB(.18, .19, .20)
            y = paragraph(c, L, y, section['text'], size=13, leading=22) - 23
        c.setFillColorRGB(.38, .38, .38)
        paragraph(c, L, y, page['closing'], size=11, leading=18)
        c.showPage()
    c.save()


def pair_pages(path, pair, model, art):
    config, scope, policy, batches, by_id = model
    targets = [by_id[t['main_id']] for t in pair['targets']]
    c = new_canvas(path); chars = [e['character'] for _, e in targets]
    header(c, '对照观察：' + ' / '.join(chars), '先分别读笔顺，再比较；两个字不要套用彼此的轮廓。')
    for j, (batch, entry) in enumerate(targets):
        authorize(ROOT, policy, batch, entry, pair['required_fields'])
        data = art[entry['main_id']]; n = len(data[0])
        require(n <= 6, 'Pair row needs pagination')
        y = 626 - j*211
        grid(c, L, y, 72); glyph(c, data, L, y, 72, color='ink')
        line(c, L+88, y+46, f"{entry['character']}  {n}画", 18)
        paragraph(c, L+88, y+18, '看这一组自己的起笔、收笔和笔画之间的位置。', width=R-L-88, size=11, leading=17)
        names = reviewed_stroke_names(entry, n)
        require(names and len(names) == n, 'Pair requires adopted names')
        for k in range(n):
            x = L+k*79
            line(c, x, y-20, f'{k+1} {names[k]}', 9, width=74)
            grid(c, x, y-104, 70); glyph(c, data, x, y-104, 70, step=k)
    paragraph(c, L, 266, '对照以后，说一说：哪一笔最容易看错？再回到这个字自己的示范核对。', size=13)
    paragraph(c, L, 197, '下一页试着独立写。写完再返回本页，对照检查。', size=11, leading=19)
    c.showPage()
    header(c, '独立回忆：' + ' / '.join(chars), '先书空，再独立写；本页不提供笔画序号、笔名或描写答案。')
    cell = (RIGHT-LEFT-7*6)/8
    for row in range(4):
        y = 599-row*(cell+40)
        line(c, L, y+cell+13, ('先写：' if row % 2 == 0 else '再写：') + chars[row//2], 13)
        for col in range(8):
            grid(c, LEFT+col*(cell+6), y, cell)
    paragraph(c, L, 229, '写完再看示范，先检查有没有漏写或顺序错误，再比较长短和位置。', size=12)
    paragraph(c, L, 170, '自查记录：________________________________________________', size=11)
    c.showPage(); c.save()


def migration_pages(path, record, whole_art, timeline, component_art):
    """Whole-character steps stay 1..N even for interleaved enclosures."""
    from build_batch import Pen, COL
    from fontTools.svgLib.path import parse_path
    from reportlab.lib.colors import HexColor

    def position_picture(c, x, y, size):
        strokes, (a,b,d,e) = whole_art
        scale=.81*size/max(d-a,e-b)
        c.saveState();c.translate(x+size/2-(a+d)*scale/2,y+size/2-(b+e)*scale/2);c.scale(scale,scale)
        for i,stroke in enumerate(strokes,1):
            c.setFillColor(HexColor(COL['red' if i in record['indices'] else 'previous']))
            p=c.beginPath();parse_path(stroke,Pen(p));c.drawPath(p,stroke=0,fill=1)
        c.restoreState()

    c=new_canvas(path);n=record['stroke_count']
    for part,steps in enumerate(timeline,1):
        header(c,'在整字中找部件：'+record['component']+' → '+record['whole_character'],
               f"{record['id']} · 第{part}/{len(timeline)}页｜按整字顺序连续看，不把部件抽出重排。")
        line(c,L,712,'本次部件',11)
        grid(c,L,620,80);glyph(c,component_art,L,620,80,color='ink')
        line(c,166,724,'位置图：红色为部件',10)
        grid(c,166,610,104);position_picture(c,166,610,104)
        line(c,293,710,f"整字{record['whole_character']}：共{n}笔",14)
        paragraph(c,293,683,'部件对应整字第'+'、'.join(map(str,record['indices']))+'笔。',
                  width=R-293,size=11,leading=17)
        paragraph(c,293,639,record['teaching_note'],width=R-293,size=11,leading=17)
        c.setFillColorRGB(.68,.18,.21);line(c,L,583,'01  看完整整字笔顺',14)
        c.setFillColorRGB(.22,.23,.24)
        line(c,L,562,f"本页第{steps[0]['step']}—{steps[-1]['step']}笔；红色是新写的一笔，深灰是此前笔画。",10)
        size=86;count=len(steps)
        xs=[(LEFT+RIGHT-size)/2] if count==1 else [LEFT+i*(RIGHT-LEFT-size)/(count-1) for i in range(count)]
        for x,step in zip(xs,steps):
            line(c,x+4,540,f"第{step['step']}笔",11)
            grid(c,x,443,size);glyph(c,whole_art,x,443,size,step=step['step']-1)
            c.setFillColorRGB(*((.68,.18,.21) if step['is_target_component'] else (.40,.40,.40)))
            line(c,x+4,428,'本次部件' if step['is_target_component'] else '整字其余笔',9)
            c.setFillColorRGB(.22,.23,.24)
        c.setFillColorRGB(.68,.18,.21);line(c,L,409,'02  写完整整字，不只写部件',14)
        c.setFillColorRGB(.22,.23,.24)
        line(c,L,393,'第1行描红，第2行描淡字；后两行看范字，再独立写。',10)
        cell=(RIGHT-LEFT-7*6)/8
        for row in range(4):
            y=326-row*(cell+13)
            for col in range(8):
                x=LEFT+col*(cell+6);grid(c,x,y,cell)
                if row<2 or col==0:glyph(c,whole_art,x,y,cell,color=['trace','pale','ink','ink'][row])
        paragraph(c,L,92,'自查：'+record['teaching_note'],size=10,leading=13)
        line(c,L,57,f"依据：GF0023—2020，原印第{record['source_row']['printed_page']}页；本例不认定正式附形。",8.5)
        line(c,L,44,'绘图：Hanzi Writer / Arphic PL；字体造型不用于判定细笔名。',8)
        c.showPage()
    c.save()
    require(len(PdfReader(path).pages)==len(timeline),'Migration continuation mismatch')


def appendix(path, by_id, nav, variants, sources, policy, config):
    c = new_canvas(path); labels = []
    def start(title, subtitle=''):
        labels.append(title); header(c, title, subtitle)
    entries = [by_id[mid][1] for mid in sorted(by_id)]
    for off in range(0, 201, 34):
        start(f'201主项索引 {off//34+1}/6', '序号用于定位；附形、比较与回忆页不重复计入201个主项。')
        y=H-124
        for e in entries[off:off+34]:
            mid=e['main_id']; first,last=nav[mid]
            line(c,L,y,f"{mid:03d}    {e['character']}    {by_id[mid][0]['batch_id']}    第{first}—{last}页",11);y-=18
        c.showPage()
    for legacy, group, count in [(False, variants['items'], 16),(True,variants['items'][:27],14)]:
        for off in range(0,len(group),count):
            start('原27项对应表' if legacy else '教学附形与位置变体', '以下是教学候选导航，不是GF0011—2022正式附形清单。')
            y=H-124
            for v in group[off:off+count]:
                line(c,L,y,f"{v['id']}    {v['parent']} → {v['form']}    例：{v['example']}    {v['position']}",12,width=R-L);y-=38
            c.showPage()
    start('来源与采用范围', '以下是来源导航；逐项支持范围、原页位置及哈希仍以仓库证据记录为准。')
    y=H-127
    for source in sources['sources']:
        label = source['id'] + '  ' + (source.get('publication_id') or source.get('title') or '')
        y=paragraph(c,L,y,label,size=10,leading=15)-10
    y-=8
    paragraph(c,L,y,'规范原页审读、绘图材料核对和版式检查分别进行。Hanzi Writer只提供绘图材料；机器检查不能代替原件阅读。转载同一文献不算另一份独立出版物。',size=11,leading=18)
    c.showPage()
    start('当前工作数据与未决范围', '这是本次工程预览的数据，不反向改写旧PDF的发布快照。')
    y=H-133
    names={'exact_2022_item_fields':'2022精确身份字段','fine_stroke_names':'细笔画名称','position_migration':'位置迁移','pronunciation':'采用读音','component_name':'部件名称','structure':'结构'}
    for rule in policy['rules']:
        text=names[rule['field']]+'：'+str(len(rule['main_ids']))+'项保留证据限制。'
        y=paragraph(c,L,y,text,size=13,leading=22)-14
    remaining={rule['field']:len(rule['main_ids']) for rule in policy['rules']}
    pronunciation=[e['field_status']['pronunciation'] for b,e in by_id.values() if b['batch_id'] not in ('B01','B02','B03')]
    reviewed=sum(s.startswith('reviewed') for s in pronunciation)
    na=sum(s.startswith('not_applicable') for s in pronunciation)
    paragraph(c,L,y-10,f"上述集合有重叠，不能相加当作不同主项数量。当前整字迁移为{201-remaining['position_migration']}项已核、{remaining['position_migration']}项保留阻塞；B04—B21的{len(pronunciation)}项读音为{reviewed}项已核、{na}项不适用、{remaining['pronunciation']}项保留阻塞。",size=12,leading=22)
    paragraph(c,L,226,'M2本周期审计结束仍保留来源阻塞。新来源取得、某字段采用、教学显示验收和正式发布是不同的步骤。来源问题继续开放；未取得不等于原件不存在。',size=11,leading=19)
    c.showPage()
    start('按字段限制教学用途', '未核字段不作为答案，已有可靠证据的无关字段仍可练习。')
    y=H-132
    notes=[('精确身份','没有核实2022正式逐项表，不作正式主形、附形、名称和编码声明。'),
           ('细笔画名称','14项未决时只用序号，不出细笔名问答。不能由粗粒度数字笔顺推导细笔名。'),
           ('读音','9项待核时不强配拼音；34项不适用另行保留。词中目标语素证据不扩展为全部读音。'),
           ('位置迁移','屮、毋暂不新增已核迁移示范。部件独写不等于它在完整字中的书写时序。'),
           ('名称与结构','28项名称、37项结构保留限制；不能用一般定义或外形猜测补成标准答案。')]
    for heading,text in notes:
        line(c,L,y,heading,15);y-=25;y=paragraph(c,L,y,text,size=12,leading=21)-25
    paragraph(c,L,y,'儿童页面中简化的技术说明在这里集中保留；原教学提示与审读记录仍存于各批数据。这个预览没有删除或升级任何规范结论。',size=11,leading=19)
    c.showPage()
    start('版本与待完成验收', M3Edition().label+'；不是冻结候选，不是正式交付。')
    y=H-133
    for text in ['历史v0.4.0、v0.4.1及所有候选稿保留原字节、清单和审读记录。',
                 '本预览包含分层说明、201主项练习、六组比较／回忆及六例整字迁移。',
                 '六例迁移共10页，均保留完整整字步骤；它们另计，不增加201主项覆盖数。',
                 'M3结束须冻结完整候选及其源码、配置、字体环境、页码映射和PDF哈希。',
                 'Q1尚未开始。未来须对最终同一份PDF逐页复核，修改后更新哈希并检查受影响页。',
                 '本次检查不代表实物打印，不允许由工程预览自动升级为正式v0.5.0。']:
        y=paragraph(c,L,y,text,size=13,leading=23)-28
    c.showPage(); c.save()
    return labels


def build(args):
    model = read_model(); config, scope, policy, batches, by_id = model
    edition=M3Edition(); out=ROOT/'build'/('v'+edition.identifier);out.mkdir(parents=True,exist_ok=True)
    setup_fonts(args.font,args.latin_font)
    pdfmetrics.registerFont(TTFont('M3Body',args.variant_font,subfontIndex=0))
    art={}; decisions=[]; records=[]; files=[]
    guide=load(ROOT,config['guidance']);guidance(out/'guidance.pdf',guide)
    files.append(('guidance',out/'guidance.pdf'))
    for batch in batches:
        path=out/(batch['batch_id']+'.pdf'); c=new_canvas(path); pn=1
        for entry in batch['entries']:
            raw=(ROOT/'build/vectors'/f'{ord(entry["character"]):04X}.json').read_bytes()
            data,audit=apply_artwork(entry['character'],raw)
            art[entry['main_id']]=prepare(data,stroke_count(entry))
            shown,decision=display_entry(ROOT,policy,batch,entry);decisions.append(decision)
            pages=make_entry_pages(c,shown,art[entry['main_id']],pn,'candidate',batch,edition=edition)
            records.append({'main_id':entry['main_id'],'character':entry['character'],'batch':batch['batch_id'],
                            'local_start':pn,'pages':pages,'vector_sha256':hashlib.sha256(raw).hexdigest()})
            pn+=pages
        c.save();files.append(('batch',path))
    for pair in scope['comparison_pairs']:
        path=out/(pair['id']+'.pdf');pair_pages(path,pair,model,art);files.append(('pair',path))
    migrations=read_migrations(model)
    for record,whole_art,timeline in migrations:
        path=out/(record['id']+'.pdf')
        migration_pages(path,record,whole_art,timeline,art[record['main_id']])
        files.append(('migration',path))
    # Count generated components before constructing page references.
    guide_pages=len(PdfReader(out/'guidance.pdf').pages)
    require(guide_pages==2,'Guidance must remain two complete pages')
    toc_count=math.ceil((len(files)-1+1)/16); cursor=guide_pages+toc_count+1; nav={}; toc=[]; section=[]
    for kind,path in files[1:]:
        count=len(PdfReader(path).pages);label=path.stem
        if kind=='batch':
            rows=[r for r in records if r['batch']==label]
            for row in rows:
                start=cursor+row['local_start']-1;nav[row['main_id']]=(start,start+row['pages']-1)
            title=label+'  '+''.join(r['character'] for r in rows)
        elif kind=='pair':
            pair=next(p for p in scope['comparison_pairs'] if p['id']==label)
            title=label+'  '+' / '.join(t['character'] for t in pair['targets'])+'：比较与回忆'
        else:
            record=next(r for r,_,_ in migrations if r['id']==label)
            title=label+'  '+record['component']+' → '+record['whole_character']+'：完整整字迁移'
        toc.append((title,cursor));section.append({'kind':kind,'id':label,'start':cursor,'pages':count});cursor+=count
    back_start=cursor
    labels=appendix(out/'appendix.pdf',by_id,nav,load(ROOT,'data/variants.json'),load(ROOT,'sources/catalog.json'),policy,config)
    require(len(PdfReader(out/'appendix.pdf').pages)==len(labels),'Appendix labels mismatch')
    toc.append(('卷末索引与来源说明',back_start)); files.append(('appendix',out/'appendix.pdf'))
    links=[];c=new_canvas(out/'contents.pdf')
    # Keep complete learning sections together instead of stranding two rows on page 3.
    toc_groups=[toc[:11],toc[11:21],toc[21:]]
    require(len(toc_groups)==toc_count and all(len(g)<=16 for g in toc_groups),'TOC grouping overflow')
    subtitles=['主项练习 B01—B11；点击目录或使用PDF书签跳转。',
               '主项练习 B12—B21；复杂字的续页按实际生成页数编排。',
               '比较、回忆、整字迁移与卷末说明；新增页面单独计数。']
    for idx,rows in enumerate(toc_groups):
        header(c,'目录与学习导航',subtitles[idx])
        y=H-129
        for title,page in rows:
            line(c,L,y,title,11,width=R-L-55);line(c,R-43,y,str(page),11)
            links.append({'page':guide_pages+idx,'target':page-1,'rect':[L,y-4,R,y+15]});y-=33
        c.showPage()
    c.save();require(len(toc)<=toc_count*16,'TOC overflow')
    ordered=[files[0][1],out/'contents.pdf']+[path for _,path in files[1:]]
    writer=PdfWriter()
    for path in ordered:writer.append(str(path))
    total=len(writer.pages)
    # One multipage overlay shares one font subset and one stable reader.
    # Per-page temporary readers can alias translation caches and bloat the PDF.
    buf=io.BytesIO();stamp=new_canvas(buf)
    recall_starts={s['start']:s['start'] for s in section if s['kind']=='pair'}
    migration_links=[]
    for sec in section:
        if sec['kind']=='migration':
            record=next(r for r,_,_ in migrations if r['id']==sec['id'])
            for i in range(sec['start']-1,sec['start']-1+sec['pages']):
                migration_links.append({'page':i,'target':nav[record['main_id']][0]-1,'case':record['id'],
                                        'rect':[L,22,R,39]})
    migration_returns={x['page']:x for x in migration_links}
    for i in range(total):
        line(stamp,L,15,f'{edition.label}    {i+1}/{total}',8,width=R-L)
        if i in recall_starts:
            line(stamp,L,94,f'返回示范：第{recall_starts[i]}页（写完再点击）',11)
        if i in migration_returns:
            target=migration_returns[i]['target']+1
            line(stamp,L,29,f'回到主项示范：第{target}页（整字与部件时序分开核对）',9)
        stamp.showPage()
    stamp.save();buf.seek(0);overlay=PdfReader(buf)
    for i,page in enumerate(writer.pages):
        page.merge_page(overlay.pages[i])
    bookmarks=[]
    for title,target in [('学生说明',0),('辅导者说明',1),('目录',2)]+[(t,p-1) for t,p in toc]:
        parent=writer.add_outline_item(title,target);bookmarks.append({'title':title,'page':target+1})
        bid=title[:3]
        if bid in config['batches']:
            for row in records:
                if row['batch']==bid:
                    label=f"ID{row['main_id']:03d} {row['character']}"
                    writer.add_outline_item(label,nav[row['main_id']][0]-1,parent=parent)
                    bookmarks.append({'title':label,'page':nav[row['main_id']][0]})
    for link in links:writer.add_annotation(link['page'],Link(rect=link['rect'],target_page_index=link['target']))
    for s in section:
        if s['kind']=='pair':
            target=s['start']-1;writer.add_annotation(s['start'],Link(rect=(L,80,R,110),target_page_index=target))
    for rec in migration_links:
        writer.add_annotation(rec['page'],Link(rect=rec['rect'],target_page_index=rec['target']))
    # Use explicit page objects, not numeric pseudo-destinations, for local links.
    for page in writer.pages:
        for annotation in page.get('/Annots', []):
            dest=annotation.get_object().get('/Dest')
            if dest is not None and isinstance(dest[0], int):
                dest[0]=writer.pages[int(dest[0])].indirect_reference
    writer.add_metadata({'/Title':'循序渐进汉字部首字帖｜'+edition.label,'/Subject':'All M3 modules integrated; candidate freeze and Q1 pending'})
    pdf=out/f'zitie-v{edition.identifier}.pdf'
    for page in writer.pages:
        page.compress_content_streams()
    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    with pdf.open('wb') as f:writer.write(f)
    input_paths=[CONFIG,config['guidance'],'data/m3_scope.json','data/teaching-source-policy.json','sources/catalog.json']
    input_paths += [f'data/{bid}.json' for bid in config['batches']]
    input_paths += ['scripts/m3_model.py','scripts/build_m3_preview.py','scripts/build_batch.py',
                    'scripts/m3_migration.py',MIGRATION_RECORD]
    input_paths += list(dict.fromkeys(r['evidence'] for r,_,_ in migrations))
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())
    meta={'schema_version':1,'version':edition.identifier,'status':'engineering_preview','candidate_frozen':False,
          'release_eligible':False,'Q1_completed':False,'source_commit':source,'source_dirty':dirty,
          'pdf':pdf.name,'sha256':digest(pdf),'bytes':pdf.stat().st_size,'pages':total,
          'main_count':len(records),'practice_pages':sum(r['pages'] for r in records),'comparison_pages':6,'recall_pages':6,
          'migration_pages':sum(len(t) for _,_,t in migrations),'migration_case_count':len(migrations),
          'migration_records':[{'id':r['id'],'main_id':r['main_id'],'whole_character':r['whole_character'],
                                'indices':r['indices'],'vector_sha256':r['vector_sha256'],'timeline':t}
                               for r,_,t in migrations],
          'migration_links':migration_links,'missing_modules':config['missing_modules'],'guide_pages':guide_pages,'toc_pages':toc_count,
          'appendix_start':back_start,'appendix_labels':labels,'main_navigation':nav,'sections':section,
          'bookmarks':bookmarks,'toc_links':links,'decisions':decisions,'entries':records,
          'input_sha256':{p:digest(ROOT/p) for p in input_paths},
          'fonts':[{'name':Path(p).name,'sha256':digest(p)} for p in (args.font,args.latin_font,args.variant_font)],
          'visual_review':'pending','physical_print_test':False}
    (out/'generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:meta[k] for k in ('version','pages','main_count','comparison_pages','recall_pages','missing_modules','sha256')},ensure_ascii=False,indent=2))
    return meta


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--font',default='/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf')
    p.add_argument('--latin-font',default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    p.add_argument('--variant-font',default='/usr/share/fonts/truetype/arphic/uming.ttc')
    build(p.parse_args())
