import tempfile,unittest,json,sys
from pathlib import Path
import cv2,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pipeline import detect,candidate_svg,mask_metrics,process,run
from xml.etree import ElementTree as ET
class PipelineTests(unittest.TestCase):
 def test_synthetic(self):
  im=np.zeros((360,360,3),np.uint8);cv2.circle(im,(180,180),95,(255,255,255),3);cv2.line(im,(40,40),(320,40),(255,255,255),3)
  geometry,edges=detect(im);self.assertTrue(geometry['lines'] or geometry['circles']);ET.fromstring(candidate_svg(geometry,360,360))
 def test_mask(self):
  a=np.zeros((40,40),np.uint8);a[10,10]=255
  m=mask_metrics(a,a);self.assertEqual(m['f1'],1.)
 def test_end_to_end(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'sources').mkdir();im=np.zeros((300,300,3),np.uint8);cv2.circle(im,(150,150),75,(255,255,255),3);cv2.imwrite(str(p/'sources'/'0001.jpg'),im)
   result=run(p/'sources',p/'out',400);self.assertEqual(result['count'],1);self.assertEqual(result['verified_count'],0)
   record=json.loads((p/'out'/'image_01'/'candidates.json').read_text());self.assertEqual(record['status'],'unverified-candidates')
if __name__=='__main__':unittest.main()