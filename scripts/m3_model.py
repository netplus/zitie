#!/usr/bin/env python3
"""Read-only M3 presentation adapter with positive evidence and field gates."""
import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from build_batch import reviewed_stroke_names
from build_book_matter import stroke_count
from verify_m2_closeout import load, require, safe_file, teaching_restrictions, verify as verify_policy

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'data/m3_book.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class M3Edition:
    version: str = '0.5.0'
    mode: str = 'candidate'  # Compatibility with the legacy page renderer only.

    def __post_init__(self):
        require(self.version == '0.5.0' and self.mode == 'candidate', 'M3 renderer only supports its engineering edition')

    @property
    def identifier(self):
        return self.version + '-dev1'

    @property
    def label(self):
        return '工程预览 v' + self.identifier

    @property
    def practice_label(self):
        return self.label + '｜先看示范，再独立写；证据说明见卷末。'


def validate_config(config):
    require(config['schema_version'] == 1 and config['version'] == '0.5.0', 'Unknown M3 edition')
    require(config['status'] == 'engineering_preview' and config['candidate_frozen'] is False,
            'This builder cannot freeze a release candidate')
    require(config['release_eligible'] is False and config['Q1_completed'] is False,
            'This builder cannot grant publication or Q1')
    require(config['batches'] == [f'B{i:02}' for i in range(1, 22)], 'Expected B01-B21')
    require(config['layout'] == {'paper': 'A4', 'orientation': 'portrait', 'rows': 4,
                                'columns': 8, 'max_steps_per_page': 6}, 'Practice geometry changed')
    require(config['modules'] == ['guidance', 'contents', 'practice', 'comparison_recall', 'appendix'],
            'Unknown or incomplete module declaration')
    require(config['missing_modules'] == ['whole_character_migration'], 'Declare unfinished migration module')
    return config


def evidence_file(root, review):
    require(isinstance(review, dict) and review.get('evidence'), 'Missing evidence record')
    return str(safe_file(root, review['evidence']).relative_to(root))


def positive_evidence(root, batch, entry, field):
    """Absence of a restriction is never sufficient positive evidence."""
    early = batch['batch_id'] in ('B01', 'B02', 'B03')
    status = entry.get('field_status', {}).get(field, '')
    if field == 'stroke_order':
        if early:
            require(entry['primary_pdf_page'] in batch['primary_review']['pdf_pages']
                    and batch['primary_source'] == 'S02', 'Early primary page not reviewed')
            require(entry['cross_evidence']['result'] == 'matched'
                    and 'stroke_order' in entry['cross_evidence']['fields'], 'Missing early cross evidence')
            return str(safe_file(root, batch['metadata_review_record']).relative_to(root))
        require(status.startswith('reviewed'), 'Stroke order not reviewed')
        review = entry['stroke_order_review']
        require(review['result'].startswith('reviewed') and review.get('pdf_page'), 'No positive stroke review')
        return evidence_file(root, review)
    if field == 'fine_stroke_names':
        if early:
            require(batch['metadata_review'] == 'passed' and entry.get('stroke_names'), 'Missing early names')
            return str(safe_file(root, batch['metadata_review_record']).relative_to(root))
        require(status.startswith('reviewed'), 'Fine names not reviewed')
        return evidence_file(root, entry['fine_stroke_names_review'])
    if field == 'pronunciation':
        if early:
            review = entry['pronunciation_evidence']
            require(review['result'] == 'matched' and review['adopted_pinyin'] == entry['pinyin'],
                    'Early adopted pronunciation mismatch')
            return str(safe_file(root, batch['metadata_review_record']).relative_to(root))
        require(status.startswith('reviewed'), 'Pronunciation not reviewed')
        review = entry['pronunciation_review']
        adopted = review.get('adopted_pronunciation', review.get('adopted_reading'))
        require(adopted == entry['pinyin'] and adopted, 'Adopted pronunciation mismatch')
        return evidence_file(root, review)
    if field == 'position_migration':
        review = entry['position_migration_review']
        require(review['result'].startswith('reviewed') and review['visual_review'] is True,
                'No positive migration review')
        return evidence_file(root, review)
    raise ValueError('No positive-evidence adapter for requested field: ' + field)


def authorize(root, policy, batch, entry, fields):
    restrictions = teaching_restrictions(policy, entry['main_id'], fields)
    require(not restrictions, 'Blocked teaching dependency: ' + ','.join(restrictions))
    return {field: positive_evidence(root, batch, entry, field) for field in fields}


def display_entry(root, policy, batch, entry):
    """Return a copy; blocked values cannot leak through stale pinyin/name data."""
    e = copy.deepcopy(entry)
    evidence = authorize(root, policy, batch, e, ['stroke_order'])
    restrictions = teaching_restrictions(policy, e['main_id'], ['fine_stroke_names', 'pronunciation'])
    decisions = {'main_id': e['main_id'], 'character': e['character'], 'evidence': evidence}
    if 'fine_stroke_names' in restrictions:
        e['stroke_names'] = None
        e['fine_stroke_names_review'] = {}
        decisions['fine_names'] = 'ordinal_only'
        e['tips'] = ['看清这一步新出现的红色笔画，再接着写。',
                     '先按序号练习，不把待核实的笔画名称当作答案。']
        e['check'] = '按顺序检查有没有漏写、拆笔或提前书写。'
    else:
        evidence.update(authorize(root, policy, batch, e, ['fine_stroke_names']))
        require(reviewed_stroke_names(e, stroke_count(entry)), 'Missing adopted fine names')
        decisions['fine_names'] = 'reviewed_names'
    status = e.get('field_status', {}).get('pronunciation', '')
    if 'pronunciation' in restrictions or status.startswith('not_applicable'):
        e['pinyin'] = None
        e['reading_note'] = ('读音待核：本页不标注' if 'pronunciation' in restrictions
                             else '本页不单列读音，先练笔顺')
        decisions['pronunciation'] = 'blocked' if 'pronunciation' in restrictions else 'not_applicable'
    else:
        evidence.update(authorize(root, policy, batch, e, ['pronunciation']))
        decisions['pronunciation'] = 'adopted'
    # Editorial simplification only; full original statements remain canonical
    # and the corresponding limitations are printed in the new audit appendix.
    if e['character'] in '阜食高黄鹿鼎黑黍龠':
        e['tips'][1] = '这一页先练完整范字；换到别的字里，要重新看整字示范。'
        if e['character'] in '高黄鹿鼎黑黍龠':
            e['check'] = f'共{stroke_count(entry)}画；对照累计示范，检查先后和有没有漏写。'
        decisions['technical_note_moved_to_appendix'] = True
    return e, decisions


def read_model(root=ROOT):
    root = Path(root)
    verify_policy(root)
    config = validate_config(load(root, CONFIG))
    scope = load(root, 'data/m3_scope.json')
    policy = load(root, scope['normative_policy'])
    batches, by_id = [], {}
    for bid in config['batches']:
        batch = load(root, f'data/{bid}.json')
        batches.append(batch)
        for entry in batch['entries']:
            require(entry['main_id'] not in by_id, 'Duplicate main ID')
            by_id[entry['main_id']] = (batch, entry)
    require(sorted(by_id) == list(range(1, 202)), 'Missing canonical main ID')
    for pair in scope['comparison_pairs']:
        for target in pair['targets']:
            batch, entry = by_id[target['main_id']]
            require(target['character'] == entry['character'], 'Pair identity mismatch')
            authorize(root, policy, batch, entry, pair['required_fields'])
    return config, scope, policy, batches, by_id
