import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime import catalog,instance,validate
from specializations import OVERRIDES

class SourceAwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items={x["id"]:x for x in catalog()}

    def test_all_specializations(self):
        for cid in OVERRIDES:
            with self.subTest(cid=cid):
                model=instance(self.items[cid],3.14)
                self.assertTrue(validate(model))
                self.assertEqual(model["geometry_status"],"interpretive-specific-construction")
                self.assertEqual(model["construction"],OVERRIDES[cid][0])
                self.assertGreater(len(model["nodes"]),0)

    def test_kathara(self):
        model=instance(self.items[21])
        self.assertEqual(len(model["nodes"]),12)
        self.assertEqual(len(model["edges"]),23)

    def test_density_labels(self):
        model=instance(self.items[3])
        self.assertEqual(sum(x["role"]=="dimension-label" for x in model["nodes"]),15)

    def test_hova_five_levels(self):
        models=[instance(self.items[i]) for i in range(123,128)]
        self.assertEqual(len(set(m["construction"] for m in models)),1)
        self.assertEqual(len(set(round(m["nodes"][0]["position"][2],2) for m in models)),5)

    def test_fire_letters(self):
        model=instance(self.items[321])
        self.assertEqual(len(model["nodes"]),144)
        self.assertEqual(len(model["edges"]),264)

    def test_merkaba(self):
        model=instance(self.items[41])
        self.assertEqual(len(model["nodes"]),8)
        self.assertEqual(len(model["edges"]),12)
        self.assertNotEqual(instance(self.items[41],0)["nodes"],
                            instance(self.items[41],1)["nodes"])

    def test_lotus(self):
        model=instance(self.items[279])
        self.assertEqual(len(model["nodes"]),2+24*9)
        self.assertGreater(len(model["edges"]),0)

    def test_other_models_remain_available(self):
        for item in self.items.values():
            self.assertTrue(validate(instance(item,2.5)))

if __name__=="__main__":unittest.main()
