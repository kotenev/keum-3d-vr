import unittest,math,tempfile,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"concept_engine"))
from runtime import catalog,instance,validate,svg,scene
from export_all import as_graph,export

class UniversalRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=catalog()

    def test_412_unique(self):
        self.assertEqual(len(self.items),412)
        self.assertEqual(len(set(x["id"] for x in self.items)),412)

    def test_all_14_families_have_instances(self):
        self.assertEqual(len(set(x["category"] for x in self.items)),14)
        for item in self.items:
            model=instance(item,1.25)
            self.assertTrue(validate(model))
            self.assertEqual(model["id"],item["id"])
            self.assertGreater(len(model["nodes"]),1)
            self.assertGreater(len(model["edges"]),0)

    def test_determinism(self):
        for item in self.items:
            self.assertEqual(instance(item,5.5),instance(item,5.5))

    def test_time_evolution(self):
        for item in self.items:
            a=instance(item,0)["nodes"]
            b=instance(item,1)["nodes"]
            self.assertNotEqual(a,b)

    def test_svg_well_formed(self):
        import xml.etree.ElementTree as ET
        for item in self.items:
            ET.fromstring(svg(instance(item)))

    def test_gltf_bridge(self):
        from graph_engine import gltf
        for item in self.items:
            g=as_graph(instance(item))
            output=gltf(g)
            self.assertEqual(output["asset"]["version"],"2.0")

    def test_export_one(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(export(d,selected=self.items[0]["id"]),1)
            self.assertEqual(len(list(Path(d).glob("*.gltf"))),1)
            self.assertEqual(len(json.loads((Path(d)/"manifest.json").read_text())),1)

    def test_reject_nan(self):
        with self.assertRaises(ValueError):
            instance(self.items[0],math.nan)

if __name__=="__main__":unittest.main()
