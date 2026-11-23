"""Offline tests for source matching. No HTTP calls."""
import unittest
from reconcile_sources import norm, similarity, score, reconcile

class SourceReconciliationTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(norm("The  Secret: of LIGHT!"),"the secret of light")
    def test_similarity(self):
        self.assertEqual(similarity("The Secret of Light","The Secret of Light"),1)
    def test_exact_candidate(self):
        ref={"id":"T","title":"The Secret of Light","author":"Walter Russell","year":"1947","url":"https://example.org","verification":"bibliographic-search"}
        candidate={"title":"The Secret of Light","author":"Walter Russell","year":"1947"}
        self.assertEqual(score(ref,candidate)["score"],1)
    def test_offline_never_promotes(self):
        refs=[{"id":"T","title":"Test","author":"A","year":"2000","url":"https://example.org","verification":"bibliographic-search"}]
        result=reconcile(refs,online=False)
        self.assertEqual(result[0]["decision"],"not_queried_offline")
        self.assertEqual(result[0]["candidates"],[])
if __name__=="__main__": unittest.main()
