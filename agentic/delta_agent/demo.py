"""Interactive agent demonstration. No physical hardware access."""
import argparse
import json
from .agent import Agent, LocalChatModel
from .simulation import SimDelta, SimDispatcher, run_reach
from .voice import WhisperSTT, record_wav, speak

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--model',help='Local tool-capable model')
    p.add_argument('--endpoint',default='http://127.0.0.1:11434/v1/chat/completions')
    p.add_argument('--voice',action='store_true',help='Enable explicit /record command')
    p.add_argument('--tts',action='store_true')
    p.add_argument('--benchmark',action='store_true')
    args=p.parse_args()
    if args.benchmark:
        print(json.dumps([run_reach(t) for t in ('cup','phone','unknown')],indent=2)); return
    if not args.model: p.error('--model is required for interactive operation')
    sim=SimDelta(); agent=Agent(LocalChatModel(args.model,args.endpoint),SimDispatcher(sim))
    stt=WhisperSTT() if args.voice else None
    print('SIMULATION ONLY. /enable, /record, /step, /status, /stop, /quit. /step advances ideal synthetic hand.')
    try:
        while True:
            line=input('You: ').strip()
            if line=='/quit': break
            if line=='/enable': sim.enable_local(); continue
            if line=='/stop': print(agent.stop_local()); continue
            if line=='/status': print(sim.get_guidance_status()); continue
            if line=='/step':
                status=sim.tick(); cue=status['cue']
                if cue:
                    amount=min(.01,cue['distance_m'])
                    hand=tuple(h+amount*d for h,d in zip(sim.hand.position,cue['world_vector']))
                    print(sim.observe(hand=hand))
                else: print(status)
                continue
            if line=='/record':
                if stt is None: print('Voice disabled. Start with --voice.'); continue
                path=record_wav()
                try: line=stt.transcribe(path)
                finally: path.unlink(missing_ok=True)
                print('Transcript:',line)
                if input('Submit transcript? [y/N] ').strip().lower()!='y': continue
            response=agent.turn(line); print('Agent:',response)
            if args.tts: speak(response)
    except (EOFError,KeyboardInterrupt): pass
    finally: agent.stop_local()

if __name__=='__main__': main()
