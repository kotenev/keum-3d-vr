import unittest
import json
from pathlib import Path
from ontology import compile_ontology

class OntologyTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((Path(__file__).resolve().parents[1]/"data/catalog.json").read_text(encoding="utf-8"))

    def test_all_412(self):
        result=compile_ontology(self.data)
        self.assertEqual(result["concept_count"],412)
        self.assertEqual(len(result["category_counts"]),14)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            compile_ontology(self.data[:-1]+[self.data[0]])

    def test_every_concept_has_family(self):
        result=compile_ontology(self.data)
        self.assertTrue(all(x["formal_family"] for x in result["concepts"]))

if __name__=="__main__":unittest.main()
