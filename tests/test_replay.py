"""Simple regression tests; all tests run without network or GPU."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from gpv_replay.core import external,check_relations,aggregate,stage_accounting,development_metrics

class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.q,cls.r=external()
    def test_seven_complete_policies(self):self.assertEqual(check_relations(self.q,self.r)['timing_observations'],17493)
    def test_reference_aggregates(self):
        group,cohorts,pool=aggregate(self.r)
        self.assertEqual(len(group),21)
        self.assertAlmostEqual(float(pool.iloc[0].saving_depth_pct),-30.461337104314918,places=7)
        self.assertAlmostEqual(float(pool.iloc[0].saving_runtime_pct),-27.004341269756896,places=7)
    def test_block_accounting(self):
        stage=stage_accounting(self.q)
        self.assertEqual(len(stage),9)
        expected={
          'Freiburg_Across_Seasons':([.285,.760,10.200],[.400,-.100,.200]),
          'Daejeon520':([1.543,1.182,5.411],[-.200,-.200,-.401]),
          'Alderley_Day_Night':([-.490,-3.460,-8.520],[.200,-.100,0.0])}
        for ds,(depth,recall) in expected.items():
            vals=stage[stage.dataset==ds].set_index('stage').loc[['5_to_10','10_to_20','20_to_50']]
            for observed,target in zip(vals.extra_candidates_GPV_minus_PI,depth):
                self.assertAlmostEqual(observed,target,delta=.0015)
            for observed,target in zip(vals.delta_recall_pp,recall):
                self.assertAlmostEqual(observed,target,delta=.0015)
    def test_full_precision_development(self):
        values,counts=development_metrics()
        self.assertEqual(sum(counts.values()),5400)
        self.assertAlmostEqual(values.loc[values.method=='GPV','mean_depth'].iloc[0],14.957407407407407,places=9)

if __name__=='__main__':unittest.main()
