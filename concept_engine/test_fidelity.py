import unittest
from fidelity import rmse,chamfer,topology,compare

class FidelityTests(unittest.TestCase):
    def test_identical(self):
        a=[[0.,0.],[1.,0.],[0.,1.]]
        self.assertEqual(rmse(a,a),0)
        self.assertEqual(chamfer(a,a),0)

    def test_known_error(self):
        self.assertAlmostEqual(rmse([[0,0]],[[3,4]]),5)

    def test_triangle_cycle(self):
        result=topology(["a","b","c"],[["a","b"],["b","c"],["c","a"]])
        self.assertEqual(result["cycle_rank"],1)
        self.assertEqual(result["components"],1)

    def test_no_reference_not_verified(self):
        self.assertEqual(compare({"id":21})["status"],"unverified")

    def test_reject_mismatched(self):
        with self.assertRaises(ValueError):rmse([[0,0]],[[1,1],[2,2]])

if __name__=="__main__":unittest.main()
