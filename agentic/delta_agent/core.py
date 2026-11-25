"""Simulation-only task-level guidance contract. Never connects to actuators."""
from enum import Enum
from threading import RLock
from typing import Protocol
import time

class Direction(str, Enum):
    LEFT='left'; RIGHT='right'; UP='up'; DOWN='down'
    UP_LEFT='up_left'; UP_RIGHT='up_right'; DOWN_LEFT='down_left'; DOWN_RIGHT='down_right'

class Frame(str, Enum):
    USER='user'; SKIN='skin'

class GuidanceBackend(Protocol):
    def guide_direction(self, direction: Direction, frame: Frame) -> dict: ...
    def guide_to_target(self, target_id: str) -> dict: ...
    def get_guidance_status(self) -> dict: ...
    def stop_guidance(self) -> dict: ...

class MockDelta:
    """Records semantic requests only. Does not simulate skin mechanics or tracking."""
    def __init__(self):
        self._lock=RLock(); self._enabled=False; self._active=None; self.events=[]
    def enable_local(self):
        with self._lock: self._enabled=True
    def _event(self, action, **kwargs):
        event={'action':action, 'time_monotonic':time.monotonic(), **kwargs}
        self.events.append(event)
        return event.copy()
    def guide_direction(self, direction, frame):
        if not isinstance(direction, Direction) or not isinstance(frame, Frame):
            return {'ok':False,'reason':'invalid_direction_or_frame','simulated':True}
        with self._lock:
            if not self._enabled:
                return {'ok':False,'reason':'local_enable_required','simulated':True}
            if self._active is not None:
                return {'ok':False,'reason':'active_session_stop_first','simulated':True}
            self._active={'direction':direction.value,'frame':frame.value}
            self._event('direction_requested', **self._active)
            return {'ok':True,'state':'simulated_request_active',**self._active,'simulated':True}
    def guide_to_target(self, target_id):
        return {'ok':False,'reason':'target_tracking_not_implemented','simulated':True}
    def get_guidance_status(self):
        with self._lock:
            return {'ok':True,'enabled':self._enabled,'state':'simulated_request_active' if self._active else 'idle','request':self._active.copy() if self._active else None,'simulated':True}
    def stop_guidance(self):
        with self._lock:
            self._active=None; self._enabled=False
            self._event('stopped_and_disarmed')
            return {'ok':True,'state':'idle','enabled':False,'simulated':True}

DIRECTIONS=[d.value for d in Direction]
FRAMES=[f.value for f in Frame]

def schema(name, description, properties):
    return {'type':'function','function':{'name':name,'description':description,'parameters':{'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}}}

TOOLS=[
    schema('guide_direction','Request a supported planar tactile direction. Does not move the user.',{'direction':{'type':'string','enum':DIRECTIONS},'frame':{'type':'string','enum':FRAMES}}),
    schema('guide_to_target','Request guidance to an already resolved target ID.',{'target_id':{'type':'string'}}),
    schema('get_guidance_status','Inspect current simulated guidance session.',{}),
    schema('stop_guidance','Cancel guidance and disarm the mock.',{}),
]

class Dispatcher:
    def __init__(self, backend: GuidanceBackend): self.backend=backend
    def invoke(self, name, args):
        if not isinstance(args, dict): return {'ok':False,'reason':'invalid_arguments'}
        try:
            if name=='guide_direction' and set(args)=={'direction','frame'}:
                return self.backend.guide_direction(Direction(args['direction']), Frame(args['frame']))
            if name=='guide_to_target' and set(args)=={'target_id'} and isinstance(args['target_id'],str) and 0<len(args['target_id'].strip())<=128:
                return self.backend.guide_to_target(args['target_id'])
            if name=='get_guidance_status' and not args: return self.backend.get_guidance_status()
            if name=='stop_guidance' and not args: return self.backend.stop_guidance()
        except (ValueError, TypeError): pass
        return {'ok':False,'reason':'unsupported_tool_or_arguments'}
