#!/usr/bin/env python3
import copy
import unittest
from validate_project import load, validate

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

if __name__ == '__main__': unittest.main()
