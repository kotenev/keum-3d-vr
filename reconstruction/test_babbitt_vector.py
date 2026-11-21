import sys, tempfile, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from babbitt_vector import PRESETS,generate
class BabbittVectorTests(unittest.TestCase):
    def test_all_presets_xml(self):
        self.assertEqual(len(PRESETS),4)
        for name,fn in PRESETS.items():
            with self.subTest(name=name):
                root=fn()
                self.assertEqual(root.tag,"svg")
                self.assertGreater(len(list(root.iter())),15)
                ET.fromstring(ET.tostring(root))
    def test_write(self):
        with tempfile.TemporaryDirectory() as p:
            self.assertEqual(generate(p),4)
            for name in PRESETS:
                ET.parse(Path(p)/(name+".svg"))
if __name__=="__main__":unittest.main()
