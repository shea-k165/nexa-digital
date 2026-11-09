import csv
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from digital import generate, save

class DigitalTests(unittest.TestCase):
    def test_content(self):
        slug, files=generate('Focus', 'Beginners', 7)
        self.assertEqual(slug, 'focus')
        self.assertEqual(len(list(csv.reader(io.StringIO(files['tracker.csv'])))),8)
        self.assertIn('Day 7',files['workbook.md'])
        self.assertIsNone(json.loads(files['listing-draft.json'])['price'])
    def test_bad_input(self):
        for topic, audience, days in [('', 'x', 7), ('x','',7), ('x','y',0), ('x','y',91), ('x\ny','z',7)]:
            with self.assertRaises(ValueError): generate(topic,audience,days)
    def test_safe_slug(self):
        slug,_=generate('../../Hello', 'People')
        self.assertEqual(slug,'hello')
    def test_package_and_hashes(self):
        with tempfile.TemporaryDirectory() as t:
            p=save('Focus','People',7,t)
            with zipfile.ZipFile(p/'customer-product.zip') as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(set(z.namelist()),{'workbook.md','tracker.csv','buyer-readme.txt'})
            for name, digest in json.loads((p/'manifest.json').read_text()).items():
                self.assertEqual(hashlib.sha256((p/name).read_bytes()).hexdigest(),digest)
            with self.assertRaises(FileExistsError): save('Focus','People',7,t)
    def test_deterministic(self):
        self.assertEqual(generate('Focus','People'),generate('Focus','People'))

if __name__ == '__main__': unittest.main()
