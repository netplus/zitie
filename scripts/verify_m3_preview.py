#!/usr/bin/env python3
"""M3 model, navigation, no-answer and font-text regression; not visual QA."""
import argparse
import copy
import io
import json
import unittest
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import IndirectObject
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from build_batch import LEFT, RIGHT, reviewed_stroke_names
from build_book_matter import stroke_count
from build_m3_preview import paragraph, new_canvas, wrap_lines
from m3_model import ROOT, CONFIG, M3Edition, authorize, digest, display_entry, read_model, validate_config
from verify_m2_closeout import require
from m3_migration import read_migrations, sequence_pages

OUT=ROOT/'build/v0.5.0-dev2'


def validate_metadata(m):
    require(m['schema_version']==1 and m['version']=='0.5.0-dev2','Wrong version')
    require(m['status']=='engineering_preview','Not an engineering preview')
    for key in ('candidate_frozen','release_eligible','Q1_completed'):
        require(m[key] is False,'Premature approval: '+key)
    require(m['missing_modules']==[] and m['migration_pages']==10 and m['migration_case_count']==6,
            'All six whole-character cases and ten pages are required')
    require(len(m['migration_records'])==6 and len(m['migration_links'])==10, 'Missing migration integration')
    require(m['main_count']==201 and m['practice_pages']==258,'Wrong main coverage')
    require(m['comparison_pages']==m['recall_pages']==6,'Wrong supplementary counts')
    require(sorted(map(int,m['main_navigation']))==list(range(1,202)),'Missing main navigation')
    require(Path(m['pdf']).name==m['pdf'],'Unsafe PDF path')
    return True


def verify(directory=OUT, *, metadata=None, edition=None):
    directory=Path(directory); m=metadata if metadata is not None else json.loads((directory/'generation.json').read_text())
    edition=edition or M3Edition(); is_candidate=edition.identifier=='0.5.0-rc1'
    if is_candidate:
        from m3_candidate import validate_metadata as validate_candidate
        validate_candidate(m)
    else:
        validate_metadata(m)
    require(digest(directory/m['pdf'])==m['sha256'],'PDF bytes changed')
    require((directory/m['pdf']).stat().st_size==m['bytes'],'PDF size changed')
    require(m['bytes']<10_000_000,'Unexpected PDF bloat')
    for path,sha in m['input_sha256'].items():require(digest(ROOT/path)==sha,'Generation input changed: '+path)
    config,scope,policy,batches,by_id=read_model()
    r=PdfReader(directory/m['pdf']);texts=[p.extract_text() or '' for p in r.pages]
    require(len(texts)==m['pages']==299,'Unannounced page count change')
    for i,p in enumerate(r.pages):
        require(abs(float(p.mediabox.width)-595.2756)<.1 and abs(float(p.mediabox.height)-841.8898)<.1,'Not A4')
        require(f'{i+1}/{len(texts)}' in texts[i] and edition.label in texts[i],'Missing real folio/preview label')
    require('看一笔，写一笔' in texts[0] and '陪孩子看懂，再练稳' in texts[1],'Guidance missing')
    if is_candidate:
        require('通过最后验收前不作为正式版' in ''.join(texts[1].split())
                and 'Q1尚未完成' in ''.join(texts[-1].split()), 'Candidate publication limits hidden')
        require(not any(bad in '\n'.join(texts) for bad in ('工程预览','-dev2','候选也尚未冻结','不是冻结候选')),
                'Stale engineering wording in candidate')
    else:
        require('候选也尚未冻结' in ''.join(texts[1].split()) and 'Q1尚未开始' in ''.join(texts[-1].split()),'Publication limits hidden')
    expected_bookmarks={x['title']:x['page'] for x in m['bookmarks']}
    actual={}
    def walk(items):
        for item in items:
            if isinstance(item,list):walk(item)
            else:actual[item.title]=r.get_destination_page_number(item)+1
    walk(r.outline)
    require(actual==expected_bookmarks,'Bookmark target mismatch')
    def destination_page(annotation):
        dest=annotation.get('/Dest')
        require(dest and isinstance(dest[0],IndirectObject),'Local link must reference a page object')
        refs={p.indirect_reference.idnum:i for i,p in enumerate(r.pages)}
        require(dest[0].idnum in refs,'Link target is not a page in this PDF')
        return refs[dest[0].idnum]
    for rec in m['toc_links']:
        annots=[a.get_object() for a in r.pages[rec['page']].get('/Annots',[])]
        require(any(destination_page(a)==rec['target'] for a in annots),'Missing TOC jump')
    for mid,(batch,entry) in by_id.items():
        shown,decision=display_entry(ROOT,policy,batch,entry)
        start,end=m['main_navigation'][str(mid)]
        require(end-start+1==(stroke_count(entry)+5)//6,'Wrong continuation count')
        for pn in range(start,end+1):
            text=texts[pn-1]
            if decision['pronunciation']!='adopted':
                require(shown['reading_note'] in text,'Missing explicit reading restriction')
            else:require(shown['pinyin'] in text,'Adopted pinyin not rendered')
            if decision['fine_names']=='ordinal_only':
                require('第1笔' in text or '第7笔' in text,'Ordinal labels missing')
        require(decision==next(d for d in m['decisions'] if d['main_id']==mid),'Field-decision log mismatch')
    cell=(RIGHT-LEFT-7*6)/8
    for section,pair in zip([s for s in m['sections'] if s['kind']=='pair'],scope['comparison_pairs']):
        pi=section['start'];comp=texts[pi-1];recall=texts[pi]
        require('对照观察' in comp and '独立回忆' in recall,'Pair/recall missing')
        require(f'返回示范：第{pi}页（写完再点击）' in recall,'Return label/font mapping corrupted')
        require(any(destination_page(a.get_object())==pi-1 for a in r.pages[pi].get('/Annots',[])),
                'Recall return destination wrong')
        operations=r.pages[pi].get_contents().operations
        cells=[v for v,op in operations if op==b're' and abs(float(v[2])-cell)<.01 and abs(float(v[3])-cell)<.01]
        require(len(cells)==32,'Recall cells missing or resized')
        require(not any(op in (b'f',b'f*',b'B',b'B*') for _,op in operations),'Recall contains filled stroke answers')
        for target in pair['targets']:
            batch,e=by_id[target['main_id']];names=reviewed_stroke_names(e,stroke_count(e))
            for i,name in enumerate(names,1):require(f'{i} {name}' in comp,'Pair steps/names missing')
            answer_text='\n'.join(l for l in recall.splitlines() if not l.startswith('返回示范'))
            require(not any(name in answer_text for name in names),'Recall leaks fine-name answers')
    migrations=read_migrations((config,scope,policy,batches,by_id))
    sections=[x for x in m['sections'] if x['kind']=='migration']
    require(len(sections)==6, 'Missing migration navigation')
    for section,(record,art,timeline),migration_meta in zip(sections,migrations,m['migration_records']):
        require(section['id']==migration_meta['id']==record['id'], 'Migration order changed')
        require(section['pages']==len(timeline) and migration_meta['timeline']==timeline, 'Whole sequence not preserved')
        require(migration_meta['indices']==record['indices'] and migration_meta['vector_sha256']==record['vector_sha256'], 'Migration evidence/rendering mismatch')
        for offset,steps in enumerate(timeline):
            page_index=section['start']-1+offset;text=texts[page_index]
            require('在整字中找部件' in text and record['component']+' → '+record['whole_character'] in text,'Migration heading missing')
            for step in steps:require(f"第{step['step']}笔" in text,'Missing full-character step')
            require(f"原印第{record['source_row']['printed_page']}页" in text,'Missing source-page label')
            ops=r.pages[page_index].get_contents().operations
            cells=[v for v,op in ops if op==b're' and abs(float(v[2])-cell)<.01 and abs(float(v[3])-cell)<.01]
            require(len(cells)==32,'Migration practice cells missing or resized')
            require('不只写部件' in text,'Whole-character practice instruction missing')
            baseline=[]
            def instruction_position(value,cm,tm,font,size):
                if '第1行描红' in value:baseline.append(tm[5]+cm[5])
            r.pages[page_index].extract_text(visitor_text=instruction_position)
            require(len(baseline)==1 and baseline[0]>326+cell+5, 'Instruction overlaps first practice row')
    for rec in m['migration_links']:
        require(any(destination_page(a.get_object())==rec['target'] for a in r.pages[rec['page']].get('/Annots',[])),
                'Migration return destination wrong')
    require('199项已核' in texts[-3] and '128项已核' in texts[-3],'Current statistics missing')
    return {'kind':('M3_candidate_preflight_not_visual_QA' if is_candidate else 'M3_engineering_preflight_not_visual_QA'),'pages':len(texts),'main_items':201,
            'practice_pages':258,'comparison_pages':6,'recall_pages':6,'bookmarks':len(actual),
            'toc_links':len(m['toc_links']),'migration_pages':m['migration_pages'],
            'migration_cases':m['migration_case_count'],'migration_return_links':len(m['migration_links']),'candidate_frozen':False,'Q1_completed':False}


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config,cls.scope,cls.policy,cls.batches,cls.by_id=read_model()

    def test_all_201_adapters(self):
        for b,e in self.by_id.values():
            original=copy.deepcopy(e);display_entry(ROOT,self.policy,b,e);self.assertEqual(e,original)
    def test_wrong_version(self):
        c=copy.deepcopy(self.config);c['version']='0.4.1'
        with self.assertRaises(ValueError):validate_config(c)
    def test_frozen_config_rejected(self):
        c=copy.deepcopy(self.config);c['candidate_frozen']=True
        with self.assertRaises(ValueError):validate_config(c)
    def test_release_config_rejected(self):
        c=copy.deepcopy(self.config);c['release_eligible']=True
        with self.assertRaises(ValueError):validate_config(c)
    def test_geometry_rejected(self):
        c=copy.deepcopy(self.config);c['layout']['columns']=7
        with self.assertRaises(ValueError):validate_config(c)
    def test_missing_batch_rejected(self):
        c=copy.deepcopy(self.config);c['batches'].pop()
        with self.assertRaises(ValueError):validate_config(c)
    def test_unknown_module(self):
        c=copy.deepcopy(self.config);c['modules'].append('automatic_answers')
        with self.assertRaises(ValueError):validate_config(c)
    def test_missing_migration_configuration(self):
        c=copy.deepcopy(self.config);c['migration_artwork']='missing.json'
        with self.assertRaises(ValueError):validate_config(c)
    def test_no_positive_order(self):
        b,e=self.by_id[149];e=copy.deepcopy(e);e['field_status']['stroke_order']='pending'
        with self.assertRaises(ValueError):display_entry(ROOT,self.policy,b,e)
    def test_no_positive_names(self):
        b,e=self.by_id[149];e=copy.deepcopy(e);e['field_status']['fine_stroke_names']='pending'
        with self.assertRaises(ValueError):display_entry(ROOT,self.policy,b,e)
    def test_wrong_adopted_sound(self):
        b,e=self.by_id[149];e=copy.deepcopy(e);e['pinyin']='mǎi'
        with self.assertRaises(ValueError):display_entry(ROOT,self.policy,b,e)
    def test_missing_evidence_file(self):
        b,e=self.by_id[149];e=copy.deepcopy(e);e['stroke_order_review']['evidence']='missing.json'
        with self.assertRaises(ValueError):display_entry(ROOT,self.policy,b,e)
    def test_early_no_cross_review(self):
        b,e=self.by_id[1];e=copy.deepcopy(e);e['cross_evidence']['result']='pending'
        with self.assertRaises(ValueError):display_entry(ROOT,self.policy,b,e)
    def test_early_wrong_reading(self):
        b,e=self.by_id[1];e=copy.deepcopy(e);e['pinyin']='yì'
        with self.assertRaises(ValueError):display_entry(ROOT,self.policy,b,e)
    def test_stale_blocked_sound_suppressed(self):
        b,e=self.by_id[201];e=copy.deepcopy(e);e['pinyin']='invented'
        shown,decision=display_entry(ROOT,self.policy,b,e)
        self.assertIsNone(shown['pinyin']);self.assertEqual(decision['pronunciation'],'blocked')
    def test_na_sound_suppressed(self):
        b,e=self.by_id[19];e=copy.deepcopy(e);e['pinyin']='invented'
        self.assertEqual(display_entry(ROOT,self.policy,b,e)[1]['pronunciation'],'not_applicable')
    def test_blocked_names_ordinal(self):
        b,e=self.by_id[55];shown,decision=display_entry(ROOT,self.policy,b,e)
        self.assertEqual(decision['fine_names'],'ordinal_only');self.assertIsNone(shown['stroke_names'])
    def test_blocked_name_quiz(self):
        b,e=self.by_id[55]
        with self.assertRaises(ValueError):authorize(ROOT,self.policy,b,e,['fine_stroke_names'])
    def test_blocked_migration(self):
        b,e=self.by_id[55]
        with self.assertRaises(ValueError):authorize(ROOT,self.policy,b,e,['position_migration'])
    def test_2022_not_promoted(self):
        b,e=self.by_id[149]
        with self.assertRaises(ValueError):authorize(ROOT,self.policy,b,e,['exact_2022_item_fields'])
    def test_unknown_field(self):
        b,e=self.by_id[1]
        with self.assertRaises(ValueError):authorize(ROOT,self.policy,b,e,['invented'])
    def test_six_comparison_dependencies(self):
        for p in self.scope['comparison_pairs']:
            for t in p['targets']:
                b,e=self.by_id[t['main_id']];self.assertTrue(authorize(ROOT,self.policy,b,e,p['required_fields']))
    def test_punctuation_wrap(self):
        pdfmetrics.registerFont(TTFont('M3Body','/usr/share/fonts/truetype/arphic/uming.ttc',subfontIndex=0))
        original='名称、结构、位置迁移分别使用自己的证据。'
        lines=wrap_lines(original,120,12)
        self.assertEqual(''.join(lines),original)
        self.assertFalse(any(l and l[0] in '，。、；：！？）》】' for l in lines))
    def test_overflow_fails_instead_of_ellipsis(self):
        pdfmetrics.registerFont(TTFont('M3Body','/usr/share/fonts/truetype/arphic/uming.ttc',subfontIndex=0))
        with self.assertRaises(ValueError):paragraph(new_canvas(io.BytesIO()),42,62,'测试'*100,width=30)


class MetadataTests(unittest.TestCase):
    def setUp(self):self.m=json.loads((OUT/'generation.json').read_text())
    def reject(self,k,v):
        self.m[k]=v
        with self.assertRaises(ValueError):validate_metadata(self.m)
    def test_valid(self):self.assertTrue(validate_metadata(self.m))
    def test_rc_promotion(self):self.reject('candidate_frozen',True)
    def test_release(self):self.reject('release_eligible',True)
    def test_Q1(self):self.reject('Q1_completed',True)
    def test_wrong_mode(self):self.reject('status','release_candidate')
    def test_missing_migration_module(self):self.reject('missing_modules',['whole_character_migration'])
    def test_incomplete_migration_pages(self):self.reject('migration_pages',6)
    def test_inflated_main(self):self.reject('main_count',213)
    def test_missing_recall(self):self.reject('recall_pages',5)
    def test_bad_path(self):self.reject('pdf','../output.pdf')
    def test_missing_navigation(self):
        self.m['main_navigation'].pop('1')
        with self.assertRaises(ValueError):validate_metadata(self.m)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');args=p.parse_args()
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
