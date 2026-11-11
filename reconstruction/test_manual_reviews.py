import copy
import json
import unittest
from pathlib import Path
from validate_reviews import verify, MANIFEST, LINKS

class ManualReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.links=json.loads(LINKS.read_text(encoding="utf-8"))

    def review(self):
        size=self.manifest["records"][0]["original_size"]
        return {"schema":"keum.manual-review.v1","image_id":1,"concept_id":21,
                "image_size":size,"status":"draft","reviewer":"","notes":"",
                "points":{"reference":[],"model":[]},"shapes":[]}

    def test_draft_unverified(self):
        result=verify(self.review(),self.manifest,self.links)
        self.assertFalse(result["geometry_verified"])
        self.assertIsNone(result["rmse_px"])

    def test_verified_requires_matched_points(self):
        x=self.review();x["status"]="verified";x["reviewer"]="expert";x["notes"]="inspected"
        with self.assertRaises(ValueError):verify(x,self.manifest,self.links)

    def test_verified_metrics(self):
        x=self.review();x["status"]="verified";x["reviewer"]="expert";x["notes"]="control points manually checked"
        x["points"]={"reference":[[0,0],[10,0],[0,10]],"model":[[0,0],[10,0],[0,10]]}
        result=verify(x,self.manifest,self.links)
        self.assertTrue(result["geometry_verified"])
        self.assertFalse(result["scientific_claim_verified"])
        self.assertEqual(result["rmse_px"],0)

    def test_out_of_bounds(self):
        x=self.review();x["points"]["reference"]=[[1e6,1e6]]
        with self.assertRaises(ValueError):verify(x,self.manifest,self.links)

    def test_image_dimensions(self):
        x=self.review();x["image_size"]=[100,100]
        with self.assertRaises(ValueError):verify(x,self.manifest,self.links)

if __name__=="__main__":unittest.main()
