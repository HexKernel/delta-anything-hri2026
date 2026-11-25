"""Synthetic tracking and guidance. Coordinates are meters; never drives hardware."""
from dataclasses import dataclass
from math import cos, sin, hypot, isfinite
from .core import MockDelta, Dispatcher, TOOLS, schema

@dataclass(frozen=True)
class Observation:
    position: tuple
    stamp: float
    def valid(self, now, max_age):
        return (len(self.position) == 3 and all(isfinite(v) for v in self.position)
                and isfinite(self.stamp) and 0 <= now-self.stamp <= max_age)

def skin_vector(vector, yaw):
    """World-to-skin inverse yaw rotation; synthetic calibration only."""
    x,y,z = vector
    return (cos(yaw)*x+sin(yaw)*y, -sin(yaw)*x+cos(yaw)*y, z)

class SimDelta(MockDelta):
    def __init__(self, tolerance=.015, max_age=.25, max_duration=20.):
        super().__init__()
        if not all(isfinite(x) and x>0 for x in (tolerance,max_age,max_duration)):
            raise ValueError('positive finite simulation parameters required')
        self.now=0.; self.yaw=0.; self.hand=Observation((0.,0.,0.),0.)
        self.targets={'cup':Observation((.20,.12,.05),0.),'phone':Observation((-.15,.10,0.),0.)}
        self.tolerance=tolerance; self.max_age=max_age; self.max_duration=max_duration
        self.started=0.; self.cue=None; self.outcome='idle'; self.trace=[]
    def observe(self, dt=.05, hand=None, refresh=True):
        if not isfinite(dt) or dt<=0: raise ValueError('invalid time step')
        with self._lock:
            self.now+=dt
            if refresh:
                self.hand=Observation(tuple(hand) if hand is not None else self.hand.position,self.now)
                self.targets={k:Observation(v.position,self.now) for k,v in self.targets.items()}
            return self.tick()
    def list_targets(self):
        with self._lock:
            return {'ok':True,'simulated':True,'target_ids':[k for k,v in self.targets.items() if v.valid(self.now,self.max_age)]}
    def guide_to_target(self,target_id):
        with self._lock:
            if not self._enabled or self._active is not None:
                return {'ok':False,'reason':'enable_and_idle_required','simulated':True}
            if target_id not in self.targets or not self.targets[target_id].valid(self.now,self.max_age) or not self.hand.valid(self.now,self.max_age):
                return {'ok':False,'reason':'unknown_or_stale_target','simulated':True}
            self._active={'target_id':target_id}; self.started=self.now; self.outcome='active'
            self._event('target_requested',target_id=target_id)
            return {'ok':True,'state':'accepted','target_id':target_id,'simulated':True}
    def _finish(self,reason):
        self._active=None; self._enabled=False; self.cue=None; self.outcome=reason
        return self.get_guidance_status()
    def stop_guidance(self):
        with self._lock:
            super().stop_guidance(); return self._finish('stopped')
    def get_guidance_status(self):
        with self._lock:
            return {**super().get_guidance_status(),'outcome':self.outcome,'cue':self.cue,'simulation_time':self.now}
    def tick(self):
        with self._lock:
            if not self._active or 'target_id' not in self._active: return self.get_guidance_status()
            target=self.targets.get(self._active['target_id'])
            if self.now-self.started>=self.max_duration: return self._finish('timeout')
            if target is None or not target.valid(self.now,self.max_age) or not self.hand.valid(self.now,self.max_age) or not isfinite(self.yaw):
                return self._finish('tracking_fault')
            error=tuple(t-h for t,h in zip(target.position,self.hand.position)); distance=hypot(*error)
            if distance<=self.tolerance: return self._finish('target_region_reached')
            direction=tuple(e/distance for e in error)
            self.cue={'skin_vector':skin_vector(direction,self.yaw),'world_vector':direction,'distance_m':distance,'depth_channel':'abstract_unvalidated'}
            self.trace.append({'time':self.now,'hand':self.hand.position,'distance_m':distance})
            return self.get_guidance_status()

class SimDispatcher(Dispatcher):
    tools=TOOLS+[schema('list_targets','List available synthetic tracked target IDs.',{})]
    def invoke(self,name,args):
        if name=='list_targets' and args=={}: return self.backend.list_targets()
        return super().invoke(name,args)

def run_reach(target='cup', step=.01, max_steps=100):
    """Ideal synthetic participant follows world cue. No human performance claim."""
    if not isfinite(step) or step<=0: raise ValueError('invalid step')
    sim=SimDelta(); sim.enable_local(); accepted=sim.guide_to_target(target)
    if not accepted['ok']: return {'outcome':'rejected','simulated':True,'steps':0}
    path=0.; steps=0; status=sim.tick()
    while status['outcome']=='active' and steps<max_steps:
        cue=status['cue']; amount=min(step,cue['distance_m'])
        hand=tuple(h+amount*d for h,d in zip(sim.hand.position,cue['world_vector']))
        path+=amount; steps+=1; status=sim.observe(hand=hand)
    if status['outcome']=='active': sim.stop_guidance(); status=sim.get_guidance_status()
    distance=hypot(*(t-h for t,h in zip(sim.targets[target].position,sim.hand.position)))
    return {'outcome':status['outcome'],'simulated':True,'steps':steps,'path_m':path,'final_error_m':distance,'time_s':sim.now}
