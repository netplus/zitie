#!/usr/bin/env python3
"""Validate structure and publication gates; never certify stroke-order truth."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

def expand(catalog):
    rows = []
    for group in catalog['groups']:
        for glyph in group['glyphs']:
            rows.append({'main_id':len(rows)+1, 'glyph':glyph, 'strokes':group['strokes']})
    return rows

def entry_stroke_count(entry):
    if isinstance(entry.get('stroke_count'), int):
        return entry['stroke_count']
    if isinstance(entry.get('stroke_names'), list):
        return len(entry['stroke_names'])
    review=entry.get('fine_stroke_names_review') or {}
    if isinstance(review.get('adjudicated_names'), list):
        return len(review['adjudicated_names'])
    if isinstance(entry.get('stroke_names_candidate'), list):
        return len(entry['stroke_names_candidate'])
    raise AssertionError(entry['character'] + ': no reviewed stroke-count source')

def entry_order_code(entry):
    for value in (
        entry.get('order_code'),
        entry.get('order_code_candidate'),
        (entry.get('stroke_order_review') or {}).get('order_code'),
        (entry.get('stroke_order_secondary_locator') or {}).get('derived_order_code'),
    ):
        if isinstance(value, str) and value:
            return value
    return None

def validate(catalog, batches, variants, batch):
    rows = expand(catalog)
    chars = [r['glyph'] for r in rows]
    assert len(chars) == catalog['expected_main_count'] == 201, 'Main count must be 201'
    assert len(set(chars)) == 201, 'Duplicate main radical'
    assert catalog['target_edition'] == 'GF0011—2022', 'Unexpected target edition'
    assert catalog['baseline_publication'] == 'GF0011—2009', 'Do not relabel the old baseline'
    ids = {r['glyph']:r['main_id'] for r in rows}
    assert ids['一'] == 1 and ids['人'] == 12 and ids['巾'] == 40 and ids['龠'] == 201
    assert '二' not in ids and '入' not in ids, 'Subordinate/example is not a main entry'
    selected = []
    for b in batches['frozen_batches']:
        gs = list(b['main_glyphs'])
        assert len(gs) == (1 if b['id'] == 'B21' else 10), 'Invalid batch size'
        assert all(g in ids for g in gs), 'Batch contains non-main character'
        selected.extend(gs)
    assert len(selected) == len(set(selected)), 'Main entry counted twice across batches'
    assert len(selected) + batches['remaining_plan']['main_count'] == 201
    assert len(batches['frozen_batches']) + len(batches['remaining_plan']['batch_ids']) == 21
    vs = variants['items']
    assert len({v['id'] for v in vs}) == len(vs), 'Duplicate variant ID'
    assert all(v['parent'] in ids for v in vs), 'Unknown parent for variant'
    declared = next((b for b in batches['frozen_batches'] if b['id'] == batch['batch_id']), None)
    assert declared is not None, 'Unknown batch ID'
    assert ''.join(e['character'] for e in batch['entries']) == declared['main_glyphs']
    for e in batch['entries']:
        count=entry_stroke_count(e)
        code=entry_order_code(e)
        if code is not None:
            assert len(code) == count, e['character'] + ': stroke count mismatch'
            assert set(code) <= set('12345'), 'Invalid stroke category code'
        if 'primary_pdf_page' in e and 'primary_printed_page' in e:
            assert e['primary_pdf_page'] - e['primary_printed_page'] == 6
        review=e.get('stroke_order_review') or {}
        if review.get('pdf_page') is not None and review.get('printed_page') is not None:
            assert review['pdf_page'] >= review['printed_page'] > 0
    if batch['release_eligible']:
        assert catalog['target_edition_status'] == 'fulltext_verified'
        assert batch['cross_review']['status'] == 'passed' and batch['cross_review']['source_id']
        assert batch['metadata_review'] == 'passed'
        assert batch['artwork_review']['status'] == 'passed' and batch['artwork_review']['reviewer']
        assert batch['layout_review']['status'] == 'passed' and batch['layout_review']['reviewer']
    return {'main_index_count':len(rows), 'frozen_batch_count':len(batches['frozen_batches']),
            'variant_candidates':len(vs), batch['batch_id']+'_primary_checked':len(batch['entries']),
            batch['batch_id']+'_cross_checked':len(batch['entries']) if (batch.get('cross_review') or {}).get('status')=='passed' else 0,
            'formal_release_entries':len(batch['entries']) if batch['release_eligible'] else 0,
            'note':'Structural checks only; no automatic semantic approval.'}

def validate_evidence(catalog, batches, sources, evidence):
    """Check field-review bookkeeping, not the truth of the source or its images."""
    assert evidence['schema_version'] == 1
    assert evidence['record_kind'] == 'field_review_checkpoint'
    assert evidence['release_eligible'] is False, 'A field checkpoint is not a release'
    assert evidence['status'] == 'stroke_order_original_pages_cross_checked'
    assert evidence['review_method'] == 'original_page_render_then_paired_row_second_pass'
    assert evidence['reviewer'] and evidence['review_date']
    assert evidence['independent_reviewers'] is False, 'This record describes same-agent rechecking'
    assert evidence['source_relationship'], 'Disclose source inheritance'
    assert set(evidence['supported_fields']) == {'stroke_count','stroke_order','source_glyph_relations'}
    assert {'fine_stroke_names','pronunciation','vector_matching','layout','target_edition_identity','variants'} <= set(evidence['pending_fields'])
    declared = next(b for b in batches['frozen_batches'] if b['id'] == evidence['batch_id'])
    entries = evidence['entries']
    assert ''.join(e['character'] for e in entries) == declared['main_glyphs'], 'Evidence must match frozen teaching order'
    assert len(entries) == evidence['total_entries']
    assert sum(e['strokes'] for e in entries) == evidence['total_strokes']
    ids = {r['glyph']:r for r in expand(catalog)}
    publications = {s['id']:s for s in sources['sources']}
    assert set(evidence['source_files']) == {'S02','S04'}, 'Use the two reviewed publications, not two mirrors'
    for sid, file in evidence['source_files'].items():
        source = publications[sid]
        assert file['publication_id'] == source['publication_id']
        assert file['sha256'] == source['sha256'], 'Source file hash drift'
        assert len(file['sha256']) == 64 and set(file['sha256']) <= set('0123456789abcdef')
        assert file['pages'] == source.get('pdf_page_count', source.get('pdf_pages'))
        assert file['bytes'] > 0
        assert file['recovery_repository'] == 'netplus/zitie'
    assert publications['S02']['publication_id'] != publications['S04']['publication_id']
    checkpoint = catalog['field_review_checkpoints'][evidence['batch_id']]
    assert checkpoint['main_ids'] == [e['main_id'] for e in entries]
    assert checkpoint['stroke_order_evidence'] == declared['stroke_order_evidence']
    assert checkpoint['generated_main_count'] == 0 and checkpoint['release_eligible'] is False
    for e in entries:
        assert ids[e['character']]['main_id'] == e['main_id']
        assert ids[e['character']]['strokes'] == e['strokes'] == len(e['order_code'])
        assert set(e['order_code']) <= set('12345')
        assert e['ucs'] == format(ord(e['character']), '05X')
        assert len(e['table_no']) == 4 and e['table_no'].isdigit()
        assert e['first_pass'] == 'original_page_viewed' and e['second_pass'] == 'paired_rows_viewed'
        assert e['result'] == 'count_order_match' and e['observation']
        for sid, offset, max_rows in [('S02',6,13), ('S04',5,10)]:
            loc = e[sid]
            source = publications[sid]
            reviewed = source.get('pdf_pages_reviewed', source.get('reviewed_pdf_pages', []))
            assert loc['pdf_page'] in reviewed, 'Page is not recorded as actually viewed'
            assert loc['pdf_page'] - loc['printed_page'] == offset
            assert 1 <= loc['pdf_page'] <= evidence['source_files'][sid]['pages']
            assert loc['column'] in ('L','R') and 1 <= loc['row'] <= max_rows
            box = loc['clip_pdf_points']
            assert len(box) == 4 and 0 <= box[0] < box[2] and 0 <= box[1] < box[3]
    return {'batch_id':evidence['batch_id'], 'source_cross_checked_entries':len(entries),
            'source_cross_checked_strokes':evidence['total_strokes'], 'generated_entries':0,
            'formal_release_entries':0, 'note':'Field evidence consistency only; not semantic approval.'}


def validate_metadata_evidence(catalog, batches, sources, evidence):
    """Check B03 fine-stroke-name and pronunciation review bookkeeping only."""
    assert evidence['schema_version'] == 1
    assert evidence['record_kind'] == 'metadata_field_review_checkpoint'
    assert evidence['release_eligible'] is False, 'Metadata review is not a release'
    assert evidence['status'] == 'fine_stroke_names_and_pronunciation_reviewed'
    assert evidence['review_method'] == 'original_scan_page_render_visual_review'
    assert evidence['reviewer'] and evidence['review_date']
    assert evidence['independent_reviewers'] is False
    assert set(evidence['supported_fields']) == {'fine_stroke_names','pronunciation'}
    assert {'component_names','teaching_text','vector_matching','layout','target_edition_identity','variants'} <= set(evidence['pending_fields'])
    declared = next(b for b in batches['frozen_batches'] if b['id'] == evidence['batch_id'])
    assert declared['metadata_evidence'] == 'data/evidence/B03-metadata.json'
    assert declared['metadata_review_record'] == evidence['review_record']
    assert 'metadata_checked' in declared['status']
    entries = evidence['entries']
    assert ''.join(e['character'] for e in entries) == declared['main_glyphs']
    assert len(entries) == evidence['total_entries'] == 10
    ids = {r['glyph']:r for r in expand(catalog)}
    publications = {s['id']:s for s in sources['sources']}
    assert set(evidence['source_files']) == {'S04','S05','S06'}
    for sid, file in evidence['source_files'].items():
        source = publications[sid]
        assert file['publication_id'] == source['publication_id']
        assert file['sha256'] == source['sha256'], 'Metadata source hash drift'
        assert file['pages'] == source.get('pdf_page_count', source.get('pdf_pages'))
    checkpoint = catalog['field_review_checkpoints'][evidence['batch_id']]
    assert checkpoint['metadata_evidence'] == declared['metadata_evidence']
    assert {'fine_stroke_names','pronunciation'} <= set(checkpoint['reviewed_fields'])
    assert checkpoint['generated_main_count'] == 0 and checkpoint['release_eligible'] is False
    for e in entries:
        assert ids[e['character']]['main_id'] == e['main_id']
        assert len(e['stroke_names']) == ids[e['character']]['strokes']
        assert e['adopted_pinyin']
        assert e['stroke_name_evidence'], e['character'] + ': missing fine-stroke evidence'
        for item in e['stroke_name_evidence']:
            sid = item['source_id']
            assert sid in ('S04','S05')
            source = publications[sid]
            reviewed = source.get('pdf_pages_reviewed', source.get('reviewed_pdf_pages', []))
            assert item['pdf_page'] in reviewed
            if sid == 'S05':
                assert item['pdf_page'] in (8,9)
                assert item['printed_page'] == item['pdf_page'] - 2
                assert item['table_row'] in {'5.1','5.2','5.8','5.9','5.15'}
                assert item['adopted_name']
            else:
                assert item['pdf_page'] == 5 and item['printed_page_label'] == '说明第2页'
                assert item['supports']
        pron = e['pronunciation_evidence']
        assert pron['source_id'] == 'S06' and pron['result'] == 'matched'
        assert pron['pdf_page'] in {31,34,42,44,47,51,53,73,83,92}
        assert pron['pdf_page'] - pron['printed_page'] == 6
        assert pron['adopted_pinyin'] == e['adopted_pinyin']
        assert pron['application'] in ('direct','morpheme_first')
        if pron['application'] == 'morpheme_first':
            assert '不冒充独立' in pron['usage']
        else:
            assert '独立词条' in pron['usage']
    return {'batch_id':evidence['batch_id'], 'metadata_reviewed_entries':len(entries),
            'fine_stroke_name_entries':len(entries), 'pronunciation_entries':len(entries),
            'generated_entries':0, 'formal_release_entries':0,
            'note':'Metadata evidence consistency only; source reading remains separately recorded.'}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--release', action='store_true')
    p.add_argument('--batch', default='B01')
    args = p.parse_args()
    c,b,v = (load(n) for n in ['data/coverage.json','data/batches.json','data/variants.json'])
    valid_batches = {item['id'] for item in b['frozen_batches']}
    if args.batch not in valid_batches:
        raise SystemExit('Unknown frozen batch: '+args.batch)
    x = load(f'data/{args.batch}.json')
    result = validate(c,b,v,x)
    sources = load("sources/catalog.json")
    result["field_checkpoints"] = [validate_evidence(c,b,sources,load(item["stroke_order_evidence"]))
                                   for item in b["frozen_batches"] if item.get("stroke_order_evidence")]
    result["metadata_checkpoints"] = [validate_metadata_evidence(c,b,sources,load(item["metadata_evidence"]))
                                      for item in b["frozen_batches"] if item.get("metadata_evidence")]
    if args.release and not x['release_eligible']:
        raise SystemExit('Release blocked: authoritative cross-review and/or other gates remain pending.')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
