import unittest
from delta_agent.core import MockDelta, Dispatcher
from delta_agent.agent import Agent

class FakeModel:
    def __init__(self,*messages): self.messages=iter(messages); self.calls=0
    def complete(self,messages,tools): self.calls+=1; return next(self.messages)

def call(name,args,id='call1'):
    return {'id':id,'type':'function','function':{'name':name,'arguments':args}}

class Tests(unittest.TestCase):
    def setUp(self): self.mock=MockDelta(); self.d=Dispatcher(self.mock)
    def test_disarmed(self): self.assertFalse(self.d.invoke('guide_direction',{'direction':'left','frame':'user'})['ok'])
    def test_direction(self):
        self.mock.enable_local()
        self.assertTrue(self.d.invoke('guide_direction',{'direction':'left','frame':'user'})['ok'])
    def test_invalid(self):
        self.mock.enable_local()
        self.assertFalse(self.d.invoke('guide_direction',{'direction':'invalid','frame':'user'})['ok'])
        self.assertFalse(self.d.invoke('guide_direction',{'direction':'left','frame':'user','force':100})['ok'])
    def test_target_unavailable(self):
        self.assertFalse(self.d.invoke('guide_to_target',{'target_id':'cup'})['ok'])
    def test_stop_disarms(self):
        self.mock.enable_local(); self.d.invoke('guide_direction',{'direction':'left','frame':'user'}); self.d.invoke('stop_guidance',{})
        self.assertFalse(self.mock.get_guidance_status()['enabled']); self.assertIsNone(self.mock.get_guidance_status()['request'])
    def test_no_overwrite(self):
        self.mock.enable_local(); self.d.invoke('guide_direction',{'direction':'left','frame':'user'}); self.assertFalse(self.d.invoke('guide_direction',{'direction':'right','frame':'user'})['ok'])
    def test_agent_tool_loop(self):
        self.mock.enable_local(); model=FakeModel({'tool_calls':[call('guide_direction','{"direction":"left","frame":"user"}')]},{'content':'Simulated left request.'}); a=Agent(model,self.d)
        self.assertEqual(a.turn('Guide left'),'Simulated left request.'); self.assertEqual(self.mock.events[0]['direction'],'left'); self.assertEqual(model.calls,2)
    def test_clarify(self):
        model=FakeModel({'content':'Which direction?'}); a=Agent(model,self.d); self.assertEqual(a.turn('Guide me'),'Which direction?'); self.assertEqual(self.mock.events,[])
    def test_stop_bypasses_model(self):
        self.mock.enable_local(); model=FakeModel(); a=Agent(model,self.d); a.turn('stop guiding me'); self.assertEqual(model.calls,0); self.assertFalse(self.mock.get_guidance_status()['enabled'])
    def test_failure_disarms(self):
        self.mock.enable_local(); a=Agent(FakeModel(),self.d); self.assertIn('failure',a.turn('left')); self.assertFalse(self.mock.get_guidance_status()['enabled'])
    def test_round_limit(self):
        self.mock.enable_local(); a=Agent(FakeModel({'tool_calls':[call('get_guidance_status','{}')]}),self.d,max_rounds=1); self.assertIn('limit',a.turn('status')); self.assertFalse(self.mock.get_guidance_status()['enabled'])
    def test_stop_then_motion_in_same_turn(self):
        self.mock.enable_local(); a=Agent(FakeModel({'tool_calls':[call('stop_guidance','{}'),call('guide_direction','{"direction":"left","frame":"user"}','call2')]},{'content':'Stopped.'}),self.d); a.turn('stop and move'); self.assertFalse(self.mock.get_guidance_status()['enabled']); self.assertEqual(len(self.mock.events),1)

if __name__=='__main__': unittest.main()
