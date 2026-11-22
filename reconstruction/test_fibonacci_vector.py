import sys,tempfile,unittest,math
from pathlib import Path
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fibonacci_vector import fib,PHI,B,golden_point,generate,PRESETS

class FibonacciTests(unittest.TestCase):
    def test_fibonacci_sequence(self):
        self.assertEqual([fib(i) for i in range(13)],[0,1,1,2,3,5,8,13,21,34,55,89,144])
    def test_negative_rejected(self):
        with self.assertRaises(ValueError):fib(-1)
    def test_ratio(self):
        self.assertAlmostEqual(fib(24)/fib(23),PHI,places=8)
    def test_quarter_turn(self):
        x,y=golden_point(0);u,v=golden_point(math.pi/2)
        self.assertAlmostEqual(math.hypot(u,v)/math.hypot(x,y),PHI,places=12)
    def test_generate(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(generate(d),4)
            for name in PRESETS:
                root=ET.parse(Path(d)/(name+".svg")).getroot()
                self.assertTrue(root.tag.endswith("svg"))
                self.assertGreater(len(list(root)),3)
if __name__=="__main__":unittest.main()
