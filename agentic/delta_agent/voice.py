"""Optional push-to-talk style WAV transcription; no automatic actuation."""
from pathlib import Path
import subprocess
import tempfile
import wave

class WhisperSTT:
    def __init__(self,model='base'):
        import whisper
        self.model=whisper.load_model(model)
    def transcribe(self,path):
        with wave.open(str(path),'rb') as f:
            if f.getnframes()/f.getframerate()>30: raise ValueError('audio exceeds 30 seconds')
        return self.model.transcribe(str(path),fp16=False)['text'].strip()

def record_wav(seconds=5, rate=16000):
    if not 0<seconds<=30: raise ValueError('invalid recording duration')
    import sounddevice as sd
    data=sd.rec(int(seconds*rate),samplerate=rate,channels=1,dtype='int16'); sd.wait()
    with tempfile.NamedTemporaryFile(suffix='.wav',delete=False) as f: path=Path(f.name)
    try:
        with wave.open(str(path),'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(data.tobytes())
        return path
    except Exception:
        path.unlink(missing_ok=True); raise

def speak(text):
    subprocess.run(['espeak','--stdin'],input=text,text=True,check=True,timeout=30)
