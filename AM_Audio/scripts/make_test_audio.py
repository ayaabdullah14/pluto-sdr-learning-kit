"""Creates assets/test_audio_48k.wav: mono, 48000 S/s, 16-bit, 10 s, peak 0.9.
Content: 2 x melody (440, 554.4, 659.3, 880 Hz, 0.5 s each) + sweep 300->3500 Hz (3 s) + chord 500+1500 Hz (1.5 s) + 10 ms burst marker.
Everything is below 4 kHz so it fits the 4 kHz AM audio band."""
import numpy as np, wave
fs=48000
def tone(f,d,a=1.0):
    t=np.arange(int(d*fs))/fs; x=a*np.sin(2*np.pi*f*t); r=min(int(0.02*fs),len(x)//4); w=np.ones_like(x); w[:r]=np.linspace(0,1,r); w[-r:]=np.linspace(1,0,r); return x*w
mel=np.concatenate([tone(f,0.5) for f in (440,554.4,659.3,880)])
t=np.arange(int(3*fs))/fs; sweep=np.sin(2*np.pi*(300*t+0.5*(3500-300)/3*t**2)); r=int(0.05*fs); sweep[:r]*=np.linspace(0,1,r); sweep[-r:]*=np.linspace(1,0,r)
chord=0.5*(tone(500,1.5)+tone(1500,1.5))
burst=tone(2000,0.01); gap=np.zeros(int(0.3*fs))
x=np.concatenate([gap,burst,gap,mel,mel,sweep,chord,gap]); x=np.pad(x,(0,fs*10-len(x))) if len(x)<fs*10 else x[:fs*10]
x=0.9*x/np.abs(x).max()
with wave.open('assets/test_audio_48k.wav','wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs); w.writeframes((x*32767).astype(np.int16).tobytes())
print("written", len(x)/fs, "s, peak", np.abs(x).max(), " mean square <x^2> =", round(np.mean(x**2),4))
