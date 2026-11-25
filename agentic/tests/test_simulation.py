import unittest
from math import pi
from delta_agent.simulation import SimDelta, SimDispatcher, skin_vector, run_reach

class SimulationTests(unittest.TestCase):
    def test_rotation(self):
        x,y,z=skin_vector((1,0,2),pi/2); self.assertAlmostEqual(x,0); self.assertAlmostEqual(y,-1); self.assertEqual(z,2)
    def test_reach(self):
        result=run_reach(); self.assertEqual(result['outcome'],'target_region_reached'); self.assertLessEqual(result['final_error_m'],.015)
    def test_unknown(self): self.assertEqual(run_reach('unknown')['outcome'],'rejected')
    def test_disarmed(self): self.assertFalse(SimDelta().guide_to_target('cup')['ok'])
    def test_stale(self):
        sim=SimDelta(); sim.enable_local(); sim.guide_to_target('cup'); self.assertEqual(sim.observe(.3,refresh=False)['outcome'],'tracking_fault'); self.assertIsNone(sim.cue)
    def test_timeout(self):
        sim=SimDelta(max_duration=.1); sim.enable_local(); sim.guide_to_target('cup'); self.assertEqual(sim.observe(.2)['outcome'],'timeout')
    def test_cancel(self):
        sim=SimDelta(); sim.enable_local(); sim.guide_to_target('cup'); sim.tick(); self.assertEqual(sim.stop_guidance()['outcome'],'stopped'); self.assertIsNone(sim.cue); self.assertFalse(sim.guide_to_target('cup')['ok'])
    def test_targets(self): self.assertIn('cup',SimDispatcher(SimDelta()).invoke('list_targets',{})['target_ids'])
    def test_nonfinite(self):
        sim=SimDelta(); sim.enable_local(); sim.guide_to_target('cup'); self.assertEqual(sim.observe(hand=(float('nan'),0,0))['outcome'],'tracking_fault')
