"""Optional independent numerical references; no GNU Radio/radio access.

Run: python reference_models.py
Requires NumPy, SciPy and Matplotlib. Every figure is labeled simulation.
The Hamming low-pass design follows the published v3.10.12 firdes formula;
it is a numerical reimplementation, not execution of GNU Radio's C++ kernels.
"""
from pathlib import Path
import json
import numpy as np
from scipy.signal import lfilter, freqz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def hamming_lowpass(fs, cutoff, transition):
    count = int(53 * fs / (22 * transition))
    if count % 2 == 0:
        count += 1
    n = np.arange(count) - (count-1)/2
    taps = (2*cutoff/fs) * np.sinc(2*cutoff/fs*n) * np.hamming(count)
    return taps / taps.sum()


def save(ix, fig):
    folder = next(ROOT.glob(f'Example_{ix:02d}_*')) / 'results'
    folder.mkdir(exist_ok=True)
    fig.savefig(folder/'reference_simulation.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def main():
    plt.rcParams.update({'font.size': 11, 'axes.spines.top':False, 'axes.spines.right':False})
    checks = {}
    # Controlled complex tone; graph axes are normalized digital quantities.
    fs=2400000; n=np.arange(48000); z=.2*np.exp(2j*np.pi*100000*n/fs)
    checks['complex_tone_mean_square_0_04'] = bool(np.isclose(np.mean(abs(z)**2),.04))
    fig,ax=plt.subplots(2,1,figsize=(9,6.5),layout='constrained')
    fig.suptitle('Example 3 | Ideal numerical reference, not received hardware data',weight='bold')
    sel=np.arange(96); ax[0].plot(sel/fs*1e6,z.real[:96],label='I',color='#c13e38');ax[0].plot(sel/fs*1e6,z.imag[:96],label='Q',color='#2268a2')
    ax[0].set(xlabel='Time (microseconds)',ylabel='Digital amplitude',title='Complex tone: I cosine and Q sine',ylim=(-.25,.25));ax[0].legend(ncol=2)
    f=np.fft.fftshift(np.fft.fftfreq(len(z),1/fs));a=abs(np.fft.fftshift(np.fft.fft(z)))/len(z)
    ax[1].plot(f/1000,a,color='#2268a2');ax[1].set(xlabel='Baseband frequency (kHz)',ylabel='DFT magnitude / N',xlim=(-200,200),title='One component at +100 kHz')
    for axis in ax:axis.grid(alpha=.2)
    save(3,fig)

    # Visual AM: red waveform and one blue positive envelope, matching GRC.
    fs=192000; n=np.arange(38400); t=n/fs; ac=.5; mu=.5; fm=500; fc=10000
    env=ac*(1+mu*np.cos(2*np.pi*fm*t));am=env*np.cos(2*np.pi*fc*t)
    checks['am_envelope_min_max']=bool(np.isclose(env.min(),.25) and np.isclose(env.max(),.75))
    fft=abs(np.fft.fft(am))/len(am)
    c=fft[int(fc*len(am)/fs)]; sb=fft[int((fc+fm)*len(am)/fs)]
    checks['am_sideband_to_carrier_amplitude_0_25']=bool(np.isclose(sb/c,.25,atol=1e-10))
    fig,ax=plt.subplots(2,1,figsize=(10,7),layout='constrained')
    fig.suptitle('Example 4A | AM numerical reference simulation',fontsize=17,weight='bold')
    count=768;ax[0].plot(t[:count]*1000,am[:count],color='#d34038',lw=1.1,label='AM waveform')
    ax[0].plot(t[:count]*1000,env[:count],color='#1468aa',lw=2,label='Positive envelope')
    ax[0].set(xlabel='Time (ms)',ylabel='Digital amplitude',title='10 kHz carrier | 500 Hz message | modulation index 0.5',xlim=(0,4),ylim=(-.85,.85));ax[0].legend(ncol=2,loc='upper center',bbox_to_anchor=(0.5,-0.20),frameon=False)
    freqs=np.fft.fftfreq(len(am),1/fs);mask=(freqs>8800)&(freqs<11200)
    ax[1].plot(freqs[mask],fft[mask],color='#1468aa',lw=1.2)
    for hz,label in [(9500,'Lower sideband'),(10000,'Carrier'),(10500,'Upper sideband')]:
        value=fft[int(hz*len(am)/fs)];ax[1].annotate(label,xy=(hz,value),xytext=(hz,value+.025),ha='center',fontsize=10)
    ax[1].set(xlabel='Frequency (Hz) - positive-frequency group enlarged',ylabel='Two-sided DFT magnitude / N',xlim=(8800,11200),ylim=(0,.30),title='Sidebands are 500 Hz either side of the carrier')
    for axis in ax:axis.grid(alpha=.2)
    save(4,fig)

    # Independently verify selection, decimation and ideal magnitude recovery.
    fs=2400000;n=np.arange(480000);t=n/fs
    signal=.1*.25*(1+.5*np.cos(2*np.pi*1000*t))*np.exp(2j*np.pi*100250*t+0.7j)
    taps=hamming_lowpass(fs,5000,3000)
    selected=lfilter(taps,[1.],signal*np.exp(-2j*np.pi*100000*t))[::50]
    recovered=abs(selected[1024:]);recovered-=recovered.mean()
    f=np.fft.rfftfreq(len(recovered),1/48000);mag=abs(np.fft.rfft(recovered*np.hanning(len(recovered))))
    peak=float(f[np.argmax(mag)])
    checks['am_ideal_recovery_1khz_after_decimation']=bool(abs(peak-1000)<=48000/len(recovered))

    # Audio reference: only message waveform, no fabricated recovered recording.
    fs=48000;n=np.arange(480);t=n/fs;message=.8*np.sin(2*np.pi*1000*t)
    fig,ax=plt.subplots(figsize=(9,3.4),layout='constrained')
    fig.suptitle('Example 5 | Known 1 kHz audio section - numerical reference',weight='bold')
    ax.plot(t*1000,message,color='#1468aa');ax.set(xlabel='Time (ms)',ylabel='Message amplitude',ylim=(-1,1),xlim=(0,10));ax.grid(alpha=.2);save(5,fig)
    checks['audio_rate_ratio_50']=bool(2400000/48000==50)
    checks['audio_envelope_headroom']=bool(np.isclose(.25*(1-.5*.8),.15) and np.isclose(.25*(1+.5*.8),.35))

    fs=48000;taps=hamming_lowpass(fs,3000,2000)
    freqs=np.linspace(0,20000,4001);_,h=freqz(taps,worN=freqs,fs=fs)
    _,test_h=freqz(taps,worN=[1000,10000],fs=fs)
    desired_db=float(20*np.log10(abs(test_h[0])));unwanted_db=float(20*np.log10(abs(test_h[1])))
    checks['filter_preserves_1khz_within_0_2db']=bool(abs(desired_db)<.2)
    checks['filter_rejects_10khz_over_40db']=bool(unwanted_db < -40)
    n=np.arange(fs*2);z=.2*np.exp(2j*np.pi*1000*n/fs)+.2*np.exp(2j*np.pi*10000*n/fs)
    y=lfilter(taps,[1.],z)[fs:];x=z[fs:]
    f=np.fft.fftshift(np.fft.fftfreq(fs,1/fs))
    bx=20*np.log10(np.maximum(abs(np.fft.fftshift(np.fft.fft(x)))/fs,1e-12))
    by=20*np.log10(np.maximum(abs(np.fft.fftshift(np.fft.fft(y)))/fs,1e-12))
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    fig.suptitle('Example 6 | Independent FIR simulation - equal axes',weight='bold')
    ax.plot(f,bx,label='Before',color='#d34038');ax.plot(f,by,label='After',color='#1468aa',alpha=.9)
    ax.set(xlabel='Baseband frequency (Hz)',ylabel='DFT amplitude (dB re 1)',xlim=(-2000,14000),ylim=(-110,0));ax.legend(ncol=2);ax.grid(alpha=.2);save(6,fig)
    ratio=10*np.log10(.01/.04);checks['half_amplitude_minus_6_0206db']=bool(np.isclose(ratio,-6.020599913279624))
    out=ROOT/'validation';out.mkdir(exist_ok=True)
    report=dict(evidence='Independent NumPy/SciPy simulation; no GNU Radio DSP or hardware execution',checks=checks,all_checks_passed=all(checks.values()),filter_6a=dict(tap_count=len(taps),desired_1khz_gain_db=desired_db,unwanted_10khz_gain_db=unwanted_db),ideal_am_recovery_peak_hz=peak)
    (out/'numerical_model_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    if not all(checks.values()):raise AssertionError(report)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
