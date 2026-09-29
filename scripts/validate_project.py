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
        assert len(e['stroke_names']) == len(e['order_code']), e['character'] + ': stroke count mismatch'
        assert set(e['order_code']) <= set('12345'), 'Invalid stroke category code'
        assert e['primary_pdf_page'] - e['primary_printed_page'] == 6
    if batch['release_eligible']:
        assert catalog['target_edition_status'] == 'fulltext_verified'
        assert batch['cross_review']['status'] == 'passed' and batch['cross_review']['source_id']
        assert batch['metadata_review'] == 'passed'
        assert batch['artwork_review']['status'] == 'passed' and batch['artwork_review']['reviewer']
        assert batch['layout_review']['status'] == 'passed' and batch['layout_review']['reviewer']
    return {'main_index_count':len(rows), 'frozen_batch_count':len(batches['frozen_batches']),
            'variant_candidates':len(vs), batch['batch_id']+'_primary_checked':len(batch['entries']),
            batch['batch_id']+'_cross_checked':len(batch['entries']) if batch['cross_review']['status']=='passed' else 0,
            'formal_release_entries':10 if batch['release_eligible'] else 0,
            'note':'Structural checks only; no automatic semantic approval.'}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--release', action='store_true')
    p.add_argument('--batch', choices=['B01','B02'], default='B01')
    args = p.parse_args()
    c,b,v,x = (load(n) for n in ['data/coverage.json','data/batches.json','data/variants.json',f'data/{args.batch}.json'])
    result = validate(c,b,v,x)
    if args.release and not x['release_eligible']:
        raise SystemExit('Release blocked: authoritative cross-review and/or other gates remain pending.')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
