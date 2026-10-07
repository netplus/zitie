#!/usr/bin/env python3
import copy
import unittest
from validate_project import load, validate, validate_evidence, validate_metadata_evidence

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = [load(n) for n in ['data/coverage.json','data/batches.json','data/variants.json','data/B01.json']]
    def reject(self, change):
        data = copy.deepcopy(self.data)
        change(data)
        with self.assertRaises(AssertionError): validate(*data)
    def test_valid_research_state(self):
        self.assertEqual(validate(*self.data)['main_index_count'],201)
    def test_no_false_release(self):
        self.assertEqual(validate(*self.data)['formal_release_entries'],0)
    def test_count(self):
        self.reject(lambda d:d[0]['groups'][0].update(glyphs='一丨丿丶'))
    def test_duplicate_main(self):
        self.reject(lambda d:d[0]['groups'][0].update(glyphs='一一丿丶乛'))
    def test_edition_relabel(self):
        self.reject(lambda d:d[0].update(baseline_publication='GF0011—2022'))
    def test_wrong_main_order(self):
        self.reject(lambda d:d[0]['groups'][0].update(glyphs='丨一丿丶乛'))
    def test_wrong_batch_size(self):
        self.reject(lambda d:d[1]['frozen_batches'][0].update(main_glyphs='一十'))
    def test_non_main(self):
        self.reject(lambda d:d[1]['frozen_batches'][0].update(main_glyphs='二十人八大工土口山巾'))
    def test_duplicate_batch(self):
        self.reject(lambda d:d[1]['frozen_batches'][1].update(main_glyphs=d[1]['frozen_batches'][0]['main_glyphs']))
    def test_parent(self):
        self.reject(lambda d:d[2]['items'][0].update(parent='二'))
    def test_stroke_mismatch(self):
        self.reject(lambda d:d[3]['entries'][0].update(order_code='11'))
    def test_false_approval(self):
        self.reject(lambda d:d[3].update(release_eligible=True))

    def test_all_frozen_batches_structural(self):
        catalog,batches,variants = [load(n) for n in ['data/coverage.json','data/batches.json','data/variants.json']]
        for item in batches['frozen_batches']:
            batch=load(f"data/{item['id']}.json")
            result=validate(catalog,batches,variants,batch)
            self.assertEqual(result['main_index_count'],201)
            self.assertEqual(result['formal_release_entries'],0)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = [load(n) for n in ['data/coverage.json','data/batches.json','sources/catalog.json','data/evidence/B03-stroke-order.json']]
    def reject(self, change):
        data = copy.deepcopy(self.data)
        change(data)
        with self.assertRaises(AssertionError): validate_evidence(*data)
    def test_source_checkpoint_only(self):
        result = validate_evidence(*self.data)
        self.assertEqual((result['source_cross_checked_entries'],result['source_cross_checked_strokes']), (10,34))
        self.assertEqual((result['generated_entries'],result['formal_release_entries']), (0,0))
    def test_reviewed_sequence_fixture(self):
        actual = {e['character']:e['order_code'] for e in self.data[3]['entries']}
        self.assertEqual(actual,dict(zip('刀力又子女小王石白立',['53','53','54','521','531','234','1121','13251','32511','41431'])))
    def test_actual_page_fixture(self):
        actual = [(e['S02']['pdf_page'],e['S04']['pdf_page']) for e in self.data[3]['entries']]
        self.assertEqual(actual,[(9,6),(9,7),(9,7),(11,9),(11,9),(10,8),(12,10),(19,18),(21,22),(23,23)])
    def test_cannot_promote_field_review(self):
        self.reject(lambda d:d[3].update(release_eligible=True))
    def test_no_inferred_visual_check(self):
        self.reject(lambda d:d[3]['entries'][3].update(first_pass='pagination_inferred'))
    def test_wrong_source_hash(self):
        self.reject(lambda d:d[3]['source_files']['S04'].update(sha256='0'*64))
    def test_main_identity_drift(self):
        self.reject(lambda d:d[3]['entries'][0].update(main_id=23))
    def test_unviewed_page(self):
        self.reject(lambda d:d[3]['entries'][0]['S04'].update(pdf_page=100,printed_page=95))
    def test_stroke_total_drift(self):
        self.reject(lambda d:d[3].update(total_strokes=36))
    def test_cannot_count_as_generated(self):
        self.reject(lambda d:d[0]['field_review_checkpoints']['B03'].update(generated_main_count=10))


class MetadataEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = [load(n) for n in ['data/coverage.json','data/batches.json','sources/catalog.json','data/evidence/B03-metadata.json']]
    def reject(self, change):
        data = copy.deepcopy(self.data)
        change(data)
        with self.assertRaises(AssertionError): validate_metadata_evidence(*data)
    def test_metadata_checkpoint_only(self):
        result = validate_metadata_evidence(*self.data)
        self.assertEqual((result['fine_stroke_name_entries'],result['pronunciation_entries']), (10,10))
        self.assertEqual((result['generated_entries'],result['formal_release_entries']), (0,0))
    def test_fine_names_fixture(self):
        actual = {e['character']:e['stroke_names'] for e in self.data[3]['entries']}
        self.assertEqual(actual['刀'], ['横折钩','撇'])
        self.assertEqual(actual['又'], ['横撇','捺'])
        self.assertEqual(actual['子'], ['横撇','弯钩','横'])
        self.assertEqual(actual['女'], ['撇点','撇','横'])
        self.assertEqual(actual['小'], ['竖钩','撇','点'])
    def test_pronunciation_fixture(self):
        actual = {e['character']:e['adopted_pinyin'] for e in self.data[3]['entries']}
        self.assertEqual(actual, dict(zip('刀力又子女小王石白立',['dāo','lì','yòu','zǐ','nǚ','xiǎo','wáng','shí','bái','lì'])))
    def test_compound_scope_retained(self):
        by = {e['character']:e['pronunciation_evidence'] for e in self.data[3]['entries']}
        self.assertEqual(by['子']['application'],'morpheme_first')
        self.assertEqual(by['石']['application'],'morpheme_first')
        self.assertIn('不冒充独立',by['子']['usage'])
        self.assertIn('不冒充独立',by['石']['usage'])
    def test_unviewed_pronunciation_page_rejected(self):
        self.reject(lambda d:d[3]['entries'][0]['pronunciation_evidence'].update(pdf_page=100,printed_page=94))
    def test_unknown_fold_row_rejected(self):
        self.reject(lambda d:d[3]['entries'][0]['stroke_name_evidence'][0].update(table_row='5.99'))
    def test_false_metadata_release_rejected(self):
        self.reject(lambda d:d[3].update(release_eligible=True))
    def test_generated_count_still_zero(self):
        self.reject(lambda d:d[0]['field_review_checkpoints']['B03'].update(generated_main_count=10))

if __name__ == '__main__': unittest.main()
