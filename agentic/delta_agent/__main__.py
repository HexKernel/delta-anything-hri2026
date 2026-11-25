import argparse
from .core import MockDelta, Dispatcher
from .agent import Agent, LocalChatModel

def main():
    p=argparse.ArgumentParser(description='Simulation-only Delta agent CLI; typed transcripts.')
    p.add_argument('--model',required=True,help='Installed local tool-capable model name')
    p.add_argument('--endpoint',default='http://127.0.0.1:11434/v1/chat/completions')
    args=p.parse_args(); mock=MockDelta(); agent=Agent(LocalChatModel(args.model,args.endpoint),Dispatcher(mock))
    print('SIMULATION ONLY. /enable arms mock, /stop disarms, /quit exits.')
    try:
        while True:
            line=input('You: ').strip()
            if line=='/quit': break
            if line=='/enable': mock.enable_local(); print('Mock enabled.'); continue
            if line=='/stop': print(agent.stop_local()); continue
            print('Agent:',agent.turn(line))
    except (EOFError,KeyboardInterrupt): pass
    finally: agent.stop_local()

if __name__=='__main__': main()
