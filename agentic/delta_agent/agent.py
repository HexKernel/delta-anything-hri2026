"""Task-level agent loop and local OpenAI-compatible chat transport."""
import json
import urllib.request
from typing import Protocol
from .core import TOOLS, Dispatcher

SYSTEM=('You are a simulated wearable haptic guidance assistant. Interpret only user-requested guidance. '
        'Ask for clarification if direction or frame is ambiguous; default ordinary left/right/up/down '
        'to user frame. Do not invent target IDs or tracking observations. '
        'Only invoke motion tools for explicit user requests. Never claim that the user or hardware moved. '
        'All requests are simulated. Respect tool failures and report actual results. Do not request raw motor commands. '
        'If a request is unsupported, explain the limitation. Do not restart after cancellation.')

class ChatModel(Protocol):
    def complete(self, messages, tools) -> dict: ...

class LocalChatModel:
    """For a user-operated local server supporting OpenAI-style tool calls."""
    def __init__(self, model, endpoint='http://127.0.0.1:11434/v1/chat/completions', timeout=30):
        self.model=model; self.endpoint=endpoint; self.timeout=timeout
    def complete(self, messages, tools):
        payload=json.dumps({'model':self.model,'messages':messages,'tools':tools,'stream':False}).encode()
        req=urllib.request.Request(self.endpoint,data=payload,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=self.timeout) as response:
            return json.load(response)['choices'][0]['message']

class Agent:
    def __init__(self, model: ChatModel, dispatcher: Dispatcher, max_rounds=4):
        self.model=model; self.dispatcher=dispatcher; self.max_rounds=max_rounds
        self.messages=[{'role':'system','content':SYSTEM}]
    def stop_local(self):
        result=self.dispatcher.invoke('stop_guidance',{})
        self.messages=[{'role':'system','content':SYSTEM}]
        return result
    def turn(self, transcript):
        if not isinstance(transcript,str) or not transcript.strip(): return 'Please provide a command.'
        if transcript.strip().lower().rstrip('.!') in {'stop','stop guiding me','cancel','emergency stop'}:
            self.stop_local(); return 'Simulation stopped and disarmed.'
        self.messages.append({'role':'user','content':transcript})
        motion_requested=False
        try:
            for _ in range(self.max_rounds):
                msg=self.model.complete(self.messages,TOOLS)
                calls=msg.get('tool_calls') or []
                self.messages.append({'role':'assistant','content':msg.get('content') or '',**({'tool_calls':calls} if calls else {})})
                if not calls: return msg.get('content') or 'No response.'
                for call in calls:
                    f=call['function']; name=f['name']
                    try: args=json.loads(f['arguments']) if isinstance(f['arguments'],str) else f['arguments']
                    except (ValueError,TypeError): args=None
                    if name in {'guide_direction','guide_to_target'} and motion_requested:
                        result={'ok':False,'reason':'one_motion_request_per_turn'}
                    else:
                        if name in {'guide_direction','guide_to_target','stop_guidance'}: motion_requested=True
                        result=self.dispatcher.invoke(name,args)
                    self.messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(result)})
            self.stop_local(); return 'Tool-round limit reached. Simulation stopped and disarmed.'
        except Exception:
            self.stop_local(); return 'Agent or tool failure. Simulation stopped and disarmed.'
