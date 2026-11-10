import unittest,json,tempfile,subprocess,sys
from pathlib import Path
from xml.etree import ElementTree as ET
from graph_engine import CATEGORIES,graph,validate,svg,gltf
class TestGraphEngine(unittest.TestCase):
 def test_all(self):
  for preset in CATEGORIES:
   g=graph(preset);self.assertTrue(validate(g));self.assertGreater(len(g['nodes']),0);self.assertGreater(len(g['edges']),0)
   self.assertEqual(g,graph(preset));ET.fromstring(svg(g));o=gltf(g);self.assertEqual(o['asset']['version'],'2.0');self.assertEqual(o['meshes'][0]['primitives'][0]['mode'],1)
 def test_kathara(self):self.assertEqual(len(graph('kathara')['nodes']),12)
 def test_lotus(self):self.assertEqual(len(graph('lotus')['nodes']),25)
 def test_validation(self):
  g=graph();g['edges'].append({'source':'missing','target':'K1'});
  with self.assertRaises(AssertionError):validate(g)
if __name__=='__main__':unittest.main()