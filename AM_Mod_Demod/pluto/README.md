# Pluto AM Experiment — Build, Settings, Analysis, and Audio Preparation

This is the English reference for the current `am_tx_pluto.grc` and `am_rx_pluto.grc` flowgraphs, version 2. We use two Windows 11 Pro laptops, each connected to one ADALM-PLUTO.

**Current radio settings: 2.4 MS/s and LO = 2.450 GHz.** Earlier tone examples used different settings. Use the values in this document together with the current flowgraphs.

The aim is to understand what we built, why we chose each setting, how the signal changes through the blocks, and how to check the result. A saved setting is not a hardware measurement. A clean-looking waveform alone does not prove that it came from our transmitter.

## 1. Files and equipment

| Item | Purpose |
|---|---|
| `am_tx_pluto.grc` | Open on Laptop 1 to build and run the AM transmitter. |
| `am_rx_pluto.grc` | Open on Laptop 2 to build and run the AM receiver. |
| `am_tx_pluto_v2.py` | Python generated from the transmitter flowgraph. |
| `am_rx_pluto_v2.py` | Python generated from the receiver flowgraph. |
| `AM_reference.png` | Calculated reference for modulation depth and envelope detection; not a Pluto measurement. |
| `README.md` | This reference. |

Open the `.grc` files in GNU Radio Companion. Save and run them there. Running an old `.py` file does not include later changes to its `.grc` file.

The supplied AM flowgraphs generate and recover a sinusoidal message. The audio section describes the next experiments; it does not claim that an audio transmitter and receiver are already included or tested.

### The physical signal journey

1. Laptop 1 calculates numerical samples of an AM signal in GNU Radio.
2. Its USB connection carries I/Q samples and configuration commands to Pluto 1.
3. Pluto 1 converts the samples into a radio-frequency electrical signal. The TX antenna radiates it.
4. The RX antenna on Pluto 2 receives that signal together with noise and other signals.
5. Pluto 2 selects a band around its tuning frequency and converts the received signal into I/Q samples.
6. USB carries those samples to Laptop 2. GNU Radio selects the AM channel and recovers the message.

GNU Radio blocks are software operations. The lines between them carry streams of samples. USB connects each laptop to its own Pluto; the antennas provide the wireless link between the two Plutos.

## 2. Terms used in this experiment

| Term | Meaning and example |
|---|---|
| Message | The information we want to send. Initially, it is a 1000 Hz cosine wave. Later, it can be speech. |
| Message frequency | The frequency of our test message: 1000 Hz, or one cycle every 1 ms. |
| Baseband | A digital representation around zero frequency, before conversion to RF or after conversion from RF. Pluto performs the RF frequency conversion; the computer does not directly sample a 2.45 GHz oscillation at 2.4 MS/s. |
| I/Q | Two numbers per complex sample: I is the real part and Q is the imaginary part. Together they describe amplitude and phase, including positive and negative frequency offsets around the LO. |
| LO Frequency | Local oscillator frequency: the radio tuning center. Our saved value is 2450000000 Hz. |
| carrier_offset | Position of our carrier within the digital baseband: +200000 Hz. |
| RF carrier | Actual transmitted carrier frequency: LO + carrier_offset = 2450200000 Hz, or 2450.2 MHz. |
| Sample Rate | Number of samples per second. At Pluto, we use 2400000 complex samples/second. This is different from message frequency, RF carrier frequency, or a digital bit rate. |
| Bandwidth | Width of a frequency range occupied or passed. Ideal conventional AM with a 1 kHz sinusoidal message has sidebands at carrier ±1 kHz, spanning 2 kHz. |
| Gain | Receiver amplification. More gain can increase both signal and noise levels and can cause overload. We start with Manual RX gain = 30 dB. |
| Attenuation | Transmitter reduction. Increasing TX attenuation from 40 to 45 dB makes transmission weaker. The setting is not an output-power measurement in dBm. |
| FFT | A calculation that displays frequency components instead of amplitude versus time. |
| DC | A constant component, corresponding to zero frequency. The detected AM envelope contains an expected DC level. A spike at zero in the raw receiver spectrum can instead be a radio artifact. |

### Three different frequencies: do not confuse them

| Quantity | Current value | Where it is set |
|---|---|---|
| Message frequency | 1000 Hz | `message_freq`, used by the message Signal Source. |
| Digital carrier offset | 200000 Hz | `carrier_offset`, used by the complex carrier Signal Source. |
| Radio tuning center | 2450000000 Hz | `lo_freq`, used by both Pluto blocks. |
| Actual RF carrier | 2450200000 Hz | Result of LO + carrier_offset. |
| Radio sample rate | 2400000 S/s | `samp_rate`, used by the radio and relevant DSP blocks. |

## 3. How we designed the AM transmitter

We started with the required signal equation, then assigned each mathematical operation to a GNU Radio block.

```text
m(t) = Am cos(2*pi*fm*t)
E(t) = Ac [1 + ka*m(t)]
mu = ka*Am
sBB(t) = E(t) exp(j*2*pi*carrier_offset*t)
```

- `m(t)` is the original message.
- `Am` is its peak amplitude, set by `msg_amp`.
- `Ac` is the carrier scale, set by `carrier_amp`.
- `ka` controls how strongly the message changes the carrier amplitude.
- `mu` is the modulation index, also called modulation depth.
- `E(t)` is the signed envelope factor.
- `sBB(t)` is the complex signal sent to Pluto.

Here, `Am = 1`, so `mu = ka` numerically. This equality is specific to our selected message amplitude.

When `E(t)` is nonnegative, its value equals the ideal signal magnitude. During overmodulation, it becomes negative for part of a cycle. The receiver's magnitude detector produces `abs(E(t))`, which folds negative parts upward and distorts the recovered message.

### Main transmitter variables

| Variable | Initial value | Why we chose it |
|---|---|---|
| `samp_rate` | `2400000` | Common radio rate, with integer reductions to 48000 and 12000 in the receiver. |
| `lo_freq` | `2450000000` | Current saved tuning center; use a laboratory-permitted frequency with suitable antennas. |
| `carrier_offset` | `200000` | Separates the wanted carrier from the zero-frequency/DC region. |
| `msg_amp` | `1.0` | Normalizes the test message and makes mu equal to ka numerically. |
| `carrier_amp` | `0.35` | Leaves digital amplitude headroom when ka changes. This is not RF power in dBm. |
| `ka` | `0.5` | Starts at 50% modulation, suitable for envelope detection. |
| `message_freq` | `1000` | Gives an easily checked 1 ms period. |
| `tx_atten` | `40` | Initial attenuation for an antenna experiment. It does not make a direct TX-to-RX cable safe. |
| `pluto_uri` | `''` | Automatic discovery when exactly one Pluto is attached to the laptop. |
| `channel_rate` | `samp_rate // 50` | 48000 S/s in the transmitter's spectrum display branch only. |

The transmitter controls allow ka from 0 to 1.4, message frequency from 200 to 3000 Hz, and TX attenuation from 10 to 70 dB. Do not sweep transmitter power without checking the received level.

### Build the transmitter step by step

All blocks in the main transmitter path operate at 2400000 S/s. Use Vector Length = 1 where applicable.

| Block | Input/output types | Settings and connection | Output at the initial settings |
|---|---|---|---|
| Signal Source: message | No input; Float output | Output Type = Float; Sample Rate = samp_rate; Waveform = Cosine; Frequency = message_freq; Amplitude = msg_amp; Offset = 0; Initial Phase = 0. | cos(2*pi*1000*t), ranging from -1 to +1. |
| Multiply Const | Float to Float | Constant = ka; connect the message output to its input. | 0.5*cos(2*pi*1000*t), ranging from -0.5 to +0.5. |
| Add Const | Float to Float | Constant = 1.0; connect after Multiply Const. | 1 + 0.5*cos(2*pi*1000*t), ranging from 0.5 to 1.5. |
| Multiply Const | Float to Float | Constant = carrier_amp; connect after Add Const. | E(t) = 0.35 + 0.175*cos(2*pi*1000*t), ranging from 0.175 to 0.525. |
| Float To Complex | Float inputs to Complex output | Connect E(t) to the real input. Leave the optional imaginary input unconnected, giving zero. | E(t) + j*0. |
| Signal Source: carrier | No input; Complex output | Output Type = Complex; Sample Rate = samp_rate; Waveform = Cosine; Frequency = carrier_offset; Amplitude = 1; Offset = 0; Initial Phase = 0. | Complex oscillator at +200 kHz: its real part is cosine and imaginary part is sine. |
| Multiply | Two Complex inputs to one Complex output | Number of Inputs = 2; connect Float To Complex to one input and the carrier Signal Source to the other. | Conventional AM centered at +200 kHz in baseband. |
| PlutoSDR Sink | Complex float32 input | Connect the Multiply output to in; use the radio settings below. | Streams samples to the transmitting Pluto. |

**Why add 1?** It creates the carrier component of conventional AM. Multiplying the message by the carrier without this constant produces double-sideband suppressed-carrier modulation, DSB-SC. Our simple envelope detector would not recover the original signed message correctly from that signal.

**Why no Throttle?** Pluto paces the radio flowgraph. A Throttle is not needed in this hardware path.

### PlutoSDR Sink settings

| Setting | Value |
|---|---|
| Input Type | Complex float32 |
| IIO context URI | `pluto_uri` |
| LO Frequency | `int(lo_freq)` |
| Sample Rate | `int(samp_rate)` |
| Buffer size | `32768` |
| Cyclic | `False` |
| Attenuation TX1 (dB) | `tx_atten` |
| Packet Length Tag | Empty |
| Filter Configuration | `Auto` |
| RF Bandwidth (Hz) | `2000000` |

The buffer contains about 13.65 ms of samples at 2.4 MS/s. This is not a measurement of total end-to-end latency.

### Transmitter display branches

The display branches help us inspect the signal without replacing its path to Pluto.

| Branch | Purpose and settings |
|---|---|
| Message output to QT GUI Time Sink | Original message; Float; Sample Rate = samp_rate; Number of Points = 7200, giving 3 ms. |
| Carrier to Complex to Real to QT GUI Time Sink | Shows the real carrier; 96 points at 2.4 MS/s give 40 us, or about 8 cycles of a 200 kHz carrier. |
| AM output to Complex to Real to QT GUI Time Sink | Shows the real AM waveform over 3 ms. |
| E(t) and E(t) multiplied by -1 to the other inputs of that Time Sink | Draws the signed upper and lower boundaries. During overmodulation these lines cross. |
| AM output to Frequency Xlating FIR Filter to QT GUI Frequency Sink | Selects the channel and reduces the display branch to 48 kS/s. This does not change the rate sent to Pluto. |

The transmitter display filter uses Decimation = 50, Center Frequency = carrier_offset, and the taps below. Its frequency display has Center Frequency = carrier_offset and Bandwidth = channel_rate. This relabels the selected spectrum around its original +200 kHz position; it does not shift the samples back up.

```python
firdes.low_pass(1.0, samp_rate, 15000, 5000, window.WIN_HAMMING)
```

### Transmitter tabs

| Tab | What to inspect |
|---|---|
| `1 AM + envelope` | Real AM waveform and its signed envelope boundaries over 3 ms. |
| `2 Message + carrier` | Original message and a separate close-up of the carrier. |
| `3 TX spectrum` | Carrier near +200 kHz, with sidebands near +199 and +201 kHz when fm = 1 kHz. |

A 200 kHz carrier is 200 times faster than a 1 kHz message. Its oscillations therefore look dense on the 3 ms AM plot. Use the carrier close-up to inspect individual cycles.

## 4. Modulation depth: under, 100%, and over

| ka, with Am = 1 | Condition | Signed envelope range | Expected ideal envelope-detection result |
|---|---|---|---|
| 0.5 | 50% modulation | 0.175 to 0.525 | Message recovered without folding distortion. |
| 1.0 | 100% modulation | 0 to 0.700 | Envelope just touches zero; ideal limiting case. |
| 1.3 | 130% overmodulation | -0.105 to 0.805 | Negative parts fold upward during magnitude detection; recovered message is distorted. |

At ka = 1.4, the maximum numerical magnitude is 0.35*(1+1.4) = 0.84. This leaves digital headroom below 1, but does not guarantee that the RF path or receiver will avoid overload.

Overmodulation and clipping have different causes. Overmodulation occurs when the signed AM envelope crosses zero. Clipping occurs when a stage reaches an amplitude limit. Clipping can happen even at ka = 0.5 if the received level or gain is too high.

For ideal linear sinusoidal AM, each sideband has amplitude mu/2 relative to the carrier:

```text
Sideband level relative to carrier = 20*log10(mu/2) dBc
For mu = 0.5: approximately -12.04 dBc per sideband.
```

An ideal linear transmitter still produces a carrier and two sidebands when mu exceeds 1. Additional harmonics after envelope detection can result from the magnitude operation folding the envelope; they do not automatically imply additional transmitted RF sidebands. Hardware nonlinearity or clipping can create additional RF components.

For a clear, non-overmodulated envelope, modulation depth can be estimated using:

```text
mu = (Emax - Emin) / (Emax + Emin)
```

Reduce the influence of noise before applying this expression. Do not use it to estimate overmodulation from an already folded envelope or from the recovered message after DC removal.

Use fm = 1000 Hz when comparing ka = 0.5, 1.0, and 1.3. At higher message frequencies, the receiver's 4 kHz message filter can remove distortion harmonics and make the waveform look cleaner than the unfiltered result.

## 5. Build and understand the receiver

### Receiver variables and PlutoSDR Source settings

| Setting or variable | Initial value |
|---|---|
| `samp_rate` | `2400000` |
| `lo_freq` | `2450000000`, matching TX |
| `pluto_uri` | `''` for automatic discovery |
| `channel_rate` | `samp_rate // 50` = 48000 |
| `message_rate` | `channel_rate // 4` = 12000 |
| `rx_gain` | 30 dB; control range 0 to 60 dB |
| `carrier_position` | 200000 Hz; control range 100000 to 300000 Hz, step 500 Hz |
| PlutoSDR Source Output Type | Complex float32 |
| IIO context URI | `pluto_uri` |
| LO Frequency | `int(lo_freq)` |
| Sample Rate | `int(samp_rate)` |
| Buffer size | `32768` |
| Quadrature Correction | True |
| RF DC Correction | True |
| BB DC Correction | True |
| Gain Mode (RX1) | Manual |
| Manual Gain (RX1)(dB) | `rx_gain` |
| Filter Configuration | Auto |
| RF Bandwidth (Hz) | `2000000`, as saved in the block |
| Packet Length Tag | Empty |

Choose Manual from the block's GUI option. The current generated Python explicitly sets `set_gain_mode(0, 'manual')`. The earlier incorrectly saved enum values could fall back to another mode; the current version corrects that problem.

The current generated PlutoSDR Source Python does not contain a separate `set_bandwidth` call, despite the RF Bandwidth field in the flowgraph. Therefore, 2 MHz is documented as a configured field, not a measured analog filter bandwidth. The digital channel-selection filter below is explicitly defined.

### Main receiver path and connections

| Block | Input/output types | Settings | Purpose |
|---|---|---|---|
| PlutoSDR Source | No stream input; Complex output | Radio settings above; output at 2.4 MS/s. | Receives I/Q containing the wanted signal, noise, and other signals in the captured band. |
| Frequency Xlating FIR Filter | Complex to Complex, real taps | Decimation = 50; Center Frequency = carrier_position; Sample Rate = samp_rate; taps below. Connect Source output to its input. | Moves the selected carrier toward zero, filters the channel, and reduces the rate to 48 kS/s. |
| Complex to Mag | Complex to Float | Vector Length = 1; connect after channel filter. | Calculates sqrt(I*I + Q*Q) to detect the envelope magnitude. Rate remains 48 kS/s. |
| DC Blocker | Float to Float | Length = 512; Long Form = True; connect after Complex to Mag. | Removes the carrier's constant envelope level; introduces delay and a settling transient. Rate remains 48 kS/s. |
| Low Pass Filter | Float to Float | Gain = 1; Sample Rate = channel_rate; Cutoff Freq = 4000; Transition Width = 1000; Decimation = 4; Window = Hamming. Connect after DC Blocker. | Keeps the message band, reduces higher-frequency noise, and outputs 12 kS/s. |

Channel filter taps:

```python
firdes.low_pass(1.0, samp_rate, 15000, 5000, window.WIN_HAMMING)
```

### Why this order works

For a sufficiently clean, correctly selected channel, the received signal approximately has this form:

```text
r(t) = H * E(t) * exp(j*(2*pi*frequency_error*t + phase)) + noise
```

`H` represents the radio path's scale and phase. Magnitude detection removes carrier rotation. With a nonnegative E(t), the result is approximately a scaled envelope. DC removal then removes the constant part, leaving a scaled message. The low-pass filter reduces noise outside the message band.

The devices do not need identical carrier phases for this envelope detector. A residual frequency offset is acceptable while the carrier and both sidebands remain inside the selected channel. This offset does not directly become an equal shift in the recovered message frequency. Sampling-clock differences can still cause small timing and frequency errors.

Filtering cannot remove all noise: noise inside the wanted signal's own frequency range remains.

### Sample-rate changes

| Position | Rate | Calculation |
|---|---|---|
| Pluto output and channel-filter input | 2400000 S/s | samp_rate |
| Channel-filter output | 48000 S/s | 2400000 / 50 |
| Complex to Mag output | 48000 S/s | No rate change. |
| DC Blocker output | 48000 S/s | No rate change. |
| Message-filter output | 12000 S/s | 48000 / 4 |

Decimation means keeping fewer samples after suitable filtering. The channel filter transitions from its 15 kHz cutoff toward rejection around 20 kHz, below the new 24 kHz Nyquist frequency. The message filter transitions from 4 to about 5 kHz, below the final 6 kHz Nyquist frequency.

A display's Sample Rate, or its frequency sink Bandwidth setting, must match the actual rate at that display's input. Changing only the displayed rate changes the axis interpretation; it does not resample the data.

### Receiver display connections

| Signal branch | Display and important settings |
|---|---|
| PlutoSDR Source output | Wide QT GUI Frequency Sink; Complex; Bandwidth = samp_rate; Center Frequency = 0; FFT Size = 32768. |
| Channel-filter output | Channel QT GUI Frequency Sink; Complex; Bandwidth = channel_rate; Center Frequency = 0; FFT Size = 8192. |
| Complex to Mag output | Envelope QT GUI Time Sink; Float; Sample Rate = channel_rate; Number of Points = 480, giving 10 ms; Autoscale enabled. |
| Message-filter output | Recovered QT GUI Time Sink; Float; Sample Rate = message_rate; Number of Points = 120, giving 10 ms; Autoscale enabled; automatic positive-going trigger at zero. |
| Message-filter output | Recovered QT GUI Frequency Sink; Float; Bandwidth = message_rate; Center Frequency = 0; FFT Size = 4096; positive-frequency display. |

### Receiver tabs

| Tab | What to inspect |
|---|---|
| `1 Recovered message` | Left: message over 10 ms. Right: message spectrum from zero to approximately 6 kHz. |
| `2 AM channel + envelope` | Left: selected carrier and sidebands. Right: detected envelope including DC. |
| `3 Find carrier` | Wide spectrum before digital channel selection; frequency is an offset from the receiver LO. |

## 6. Connect the equipment and identify each Pluto

1. Connect Pluto 1 to Laptop 1 and Pluto 2 to Laptop 2 through their data-capable USB connections.
2. Attach suitable antennas to TX on Pluto 1 and RX on Pluto 2. Start about one meter apart, with similar antenna orientation.
3. Use a frequency approved for your laboratory experiment and suitable for the antennas. The saved 2.450 GHz tuning value is not confirmation of permission to transmit there.
4. Close other running SDR experiments so that only one application uses each Pluto.
5. With one Pluto on each laptop, first try `pluto_uri = ''` for automatic discovery.
6. If discovery fails, open radioconda Prompt from the Windows Start menu. Type this command inside the prompt:

```bat
iio_info -s
```

“radioconda Prompt” is an application name, not a command to type into Command Prompt.

If the output lists a context such as `[usb:1.9.5]`, enter this in the Value field of the Variable named pluto_uri:

```python
'usb:1.9.5'
```

Keep IIO context URI inside the Pluto block set to `pluto_uri`. The quotes are required in the Variable because its value is a Python string expression. Use the actual URI reported on that laptop; USB addresses may change after reconnection.

On Windows, `Unable to create Local IIO context : Function not implemented (40)` does not by itself indicate USB failure when the Pluto is listed under Available contexts. `No IIO context found` means that discovery did not find the device and needs investigation.

### Receiver protection with RF cables

This experiment starts with antennas. Do not connect TX directly to RX using only an RF cable. A cabled test requires external RF attenuation selected from the maximum possible transmitter output, receiver input limit, cable loss, and a suitable margin. The attenuators must support the frequency and power involved. Software TX attenuation alone is not sufficient protection for a direct connection. Check the device limits and your laboratory's setup before building a cabled path.

## 7. Run the AM experiment

1. On Laptop 2, open `am_rx_pluto.grc`, save, and click Run or press F6. Maximize its plots. Noise before TX starts is expected.
2. On Laptop 1, open `am_tx_pluto.grc`. Start with ka = 0.5, Message frequency = 1000 Hz, and TX attenuation = 40 dB. Save and run.
3. Allow about two seconds for filter transients and spectrum averaging to settle.
4. In the receiver's first tab, look for a periodic waveform and a component near 1 kHz.
5. If missing, open `3 Find carrier`. Look for a new component near +200 kHz that follows transmitter operation. A zero-frequency spike alone is not evidence of the link.
6. If the actual carrier peak is near +207 kHz, set Carrier position to 207000. The slider selects a filter center; its number is not an automatic carrier measurement.
7. If the signal is weak, check antennas, USB, matching LO values, and the selected channel first. For the antenna experiment, a single change from TX attenuation = 40 to 35 dB can be compared if needed, while monitoring overload. Change one setting at a time.

Do not change Sample Rate to solve a weak signal. That setting also affects filters and display rates.

## 8. Read the plots correctly

### Time-domain axes

- Horizontal axis: time, automatically displayed in seconds, milliseconds, or microseconds.
- Vertical axis: numerical amplitude, usually labeled a.u. These values are not calibrated volts.
- Display duration = Number of Points / Sample Rate.

Examples:

```text
120 points / 12000 samples/s = 0.010 s = 10 ms
7200 points / 2400000 samples/s = 0.003 s = 3 ms
```

A 1 kHz message should show about ten cycles in 10 ms. A 2 kHz message should show about twenty. At the recovered rate, there are 12 samples per 1 kHz cycle and 6 per 2 kHz cycle. Straight lines between a small number of samples can look angular without indicating RF clipping.

### Frequency-domain axes

| Display | What zero means | Expected result for a 1 kHz message |
|---|---|---|
| Find carrier | Receiver LO frequency. | Carrier near +200 kHz, with a possible device frequency offset. |
| Selected AM channel | Digitally selected channel center. | Carrier near zero, sidebands about 1 kHz below and above it. |
| Recovered message spectrum | DC in the recovered real message. | Wanted peak near +1 kHz in the positive-frequency view. |

The saved RF carrier is at 2450.200 MHz. Its ideal RF sidebands for fm = 1 kHz are at 2450.199 and 2450.201 MHz. Before channel translation, the corresponding digital offsets are 199, 200, and 201 kHz.

FFT bin spacing is Sample Rate / FFT Size:

| Spectrum | Calculation | Approximate bin spacing |
|---|---|---|
| Wide receiver | 2400000 / 32768 | 73.24 Hz |
| Selected AM channel | 48000 / 8192 | 5.86 Hz |
| Recovered message | 12000 / 4096 | 2.93 Hz |

Bin spacing is not a guarantee of measurement accuracy or the ability to separate nearby signals. Window shape, noise, averaging, frequency drift, and the signal's position between bins affect the result.

The vertical spectrum scale is relative dB, not calibrated dBm. A peak's height above an FFT noise floor is not automatically the total channel SNR.

### Distinguish the wanted signal, noise, and DC

The receiver measures continuously, including before the transmitter starts. Noise, other transmitters, and internal artifacts can already be present. Our transmission adds to that received mixture.

A wanted signal should follow a deliberate transmitter change. Check TX on/off and a message change from 1000 to 2000 Hz. Do not identify it only because a peak looks tall. A DC spike tends to stay at the receiver's zero-frequency position rather than following the intended offset carrier.

### Compare original and recovered messages

Compare these properties separately:

1. Frequency: check the period and the spectral peak.
2. Shape: compare smooth sinusoidal behavior or the expected distortion.
3. Amplitude: account for path loss and gain; normalize before comparing shape quantitatively.
4. Delay: align recordings before comparing individual samples.

Radio propagation, filters, buffers, and independent device clocks can change amplitude, phase, and timing. The recovered amplitude does not need to equal the original value of 1.

### Why the waveform may move

- Horizontal movement can come from trigger behavior, where each plot window begins, or sampling-clock differences.
- Apparent vertical changes may come from Autoscale. Read the axis numbers before deciding that the physical amplitude changed.
- Real amplitude changes can come from antenna movement, people, reflections, or noise.
- Clipping usually produces repeated flattened peaks at an amplitude limit; inspect the level and spectrum as well.
- Autoscale can magnify noise after TX stops. A moving trace after TX stops does not prove that the message is still being received.

## 9. What we observed, and what still needs confirmation

The latest shared screenshots show approximately ten recovered cycles across 10 ms:

```text
T approximately equals 10 ms / 10 = 1 ms
f approximately equals 1 / 0.001 = 1000 Hz
```

The waveform looks close to sinusoidal and centered near zero. Its amplitude is roughly +/-0.0008 to +/-0.0009 in those screenshots. The fuller screenshot shows a spectral component near 1 kHz. The later cropped screenshot does not show the entire spectrum.

These are approximate observations from screenshots, not averaged measurements or amplitude calibration. They are consistent with recovery of the intended 1 kHz message. Controlled transmitter changes are still needed to confirm the source.

| Check | Expected outcome | Documented status |
|---|---|---|
| Both devices detected by iio_info | Each laptop lists its connected Pluto. | Reported earlier, with different device serial numbers. Recheck after connection problems. |
| fm = 1000, ka = 0.5 | About ten cycles in 10 ms and a peak near 1 kHz. | Screenshots approximately match. |
| Change only TX message frequency to 2000 | About twenty cycles in 10 ms and a peak near 2 kHz. | Not yet documented. |
| Stop TX while RX continues | Coherent component at the message frequency falls toward the background. | Not yet documented. |
| Return to fm = 1000, then set ka = 0 | Carrier remains but the intended message component disappears toward the background. | Record your result. |
| Test ka = 0.5, 1.0, and 1.3 at fm = 1000 | Positive envelope, envelope touching zero, then folded-envelope distortion. | Hardware comparison not yet documented. |
| Audio transmission and playback | Recognizable received audio following the source. | Not yet confirmed. |

After the frequency-change test, return to 1000 Hz before testing modulation depth. Save a screenshot of the message, channel spectrum, and envelope for each depth.

## 10. Relative power and calibration

A useful digital relative-power measure is the average of `I*I + Q*Q` after complex channel selection, before envelope detection and DC removal. Keep RX gain, filter bandwidth, scaling, and the measurement procedure fixed.

```text
Relative power difference in dB = 10*log10(P2/P1)
```

Before reporting absolute RF power in dBm, calibrate against a known RF source. Account for cable and attenuator losses, frequency, receiver gain, sample scaling, and filters. Verify that the receiver remains linear and does not clip. An uncalibrated FFT display alone does not provide this calibration.

## 11. Troubleshoot one cause at a time

| Symptom | Next check |
|---|---|
| iio_info is not recognized | Open the installed radioconda Prompt. Confirm that libiio tools are available in that environment. |
| No IIO context found | Check the data USB cable, direct USB port, device connection, and competing programs; scan again on that laptop. |
| A previously saved USB URI stops working | Run iio_info -s again and update pluto_uri, or try automatic discovery with one device attached. |
| Radio is busy | Stop other flowgraphs or programs using that Pluto. |
| Frequency assertion such as frequency >= 70000000 and <= 6000000000 | Check lo_freq in Hz. A value such as 2.45 or 1000 is not the intended LO. Message frequency belongs in the message source. The assertion range is not permission to use every frequency in that range. |
| No message | Check TX running, antenna ports, matching LO values, and Find carrier before changing power. |
| Carrier outside the channel filter | Measure its position in the wide spectrum and adjust Carrier position. |
| Distortion at ka = 0.5 | Inspect level, gain, possible overload, interference, and channel selection. Request the envelope and spectrum, not only the time trace. |
| Small numerical amplitude but a clear message component | Check the message-change test. Small numbers are not calibrated volts and do not alone mean failure. |
| Flat tops or rising unwanted harmonics | Investigate clipping. Reduce RX gain or increase TX attenuation one step, then compare. Do not deliberately force overload. |
| Distortion appears mainly when ka exceeds 1 | Check overmodulation and envelope folding; reduce ka to 0.5 for comparison. |
| Waveform looks vertically unstable | Check Autoscale axis changes, then investigate actual gain or channel variation. |
| USB errors or interrupted reception | Send the exact error. Check the cable, direct USB port, and computer load. Do not assume UHD-specific error letters apply to Pluto. |
| Red block or flowgraph generation failure | Send the exact error and GNU Radio version. The flowgraphs were checked against GNU Radio 3.10.12.0 definitions. |
| A new setting has no effect | Confirm which .grc and generated .py are running. Stop the old process, save the intended graph, and rerun. |

Keep a small log: what you changed, its old and new values, what happened, and the relevant screenshot or error. Avoid changing frequency, gain, and sample rate together.

## 12. Move to audio, one experiment at a time

Audio contains many frequencies that change over time. We will retain the AM principle and replace the sinusoidal message with appropriately filtered and scaled audio.

### Experiment A: local speaker test — perform this first

**Purpose:** verify that GNU Radio can play sound through the receiving laptop before introducing the wireless path.

**Expected result:** a quiet, steady 1 kHz beep.

1. Stop the AM experiment.
2. Create a new flowgraph on the receiving laptop and save it as `audio_test.grc`.
3. Set the existing Variable block to ID = samp_rate and Value = 48000.
4. Add Signal Source and Audio Sink with the following settings.

| Block | Setting | Value |
|---|---|---|
| Signal Source | Output Type | Float |
| Signal Source | Sample Rate | samp_rate |
| Signal Source | Waveform | Cosine |
| Signal Source | Frequency | 1000 |
| Signal Source | Amplitude | 0.05 |
| Signal Source | Offset | 0 |
| Audio Sink | Sample Rate | 48000 |
| Audio Sink | Device Name | Leave empty to use the default device. |
| Audio Sink | OK to Block | Yes |

5. Connect the Signal Source Float output directly to the Audio Sink input.
6. Do not add Throttle; Audio Sink paces this local experiment.
7. Set Windows volume to about 10%, run for a few seconds, then stop.

This experiment uses only the laptop. Pluto is not involved. If it fails, record the exact error and check the Windows output device before modifying the radio flowgraphs.

**One modification after success:** change Frequency from 1000 to 500 while keeping Sample Rate = 48000. The pitch should become lower.

**Check your understanding:** Which value controls pitch? Which value describes samples per second? Why did we keep both connected blocks at the same sample rate?

Answers: Frequency controls pitch; Sample Rate describes sample count per second; Audio Sink must interpret the incoming samples at the rate at which they represent the sound.

### Experiment B: play a WAV file locally

After the beep works, use a short WAV file as a repeatable message. First check the file's sample rate and channel count. A stereo file has two channels; our initial AM message will be mono. Do not assume that renaming an MP3 file to .wav converts its format.

The goal is to hear the source clearly on the laptop before transmitting it. Exact file-source settings and any conversion will depend on the chosen file.

### Experiment C: transmit the audio through AM

The planned audio path uses a 48 kS/s mono message, limited to approximately the receiver's 4 kHz message band. Convert it to 2.4 MS/s by interpolation by 50 before using it in the high-rate AM path.

Scale the message so that `1 + ka*m(t)` stays nonnegative during the first clear-audio experiment. Replacing a unit-amplitude sine with arbitrary audio does not automatically preserve the same modulation depth. Check the actual peaks after filtering and rate conversion.

Keep the receiver's channel selection, envelope detection, DC removal, and message filter conceptually the same.

### Experiment D: play the recovered audio

The current receiver output is 12 kS/s. Do not feed it directly to an Audio Sink set to 48 kS/s.

The planned additional blocks are:

- Rational Resampler, Float to Float, Interpolation = 4 and Decimation = 1, to convert 12 kS/s to 48 kS/s.
- Multiply Const, Float to Float, with a modest playback gain selected from the observed amplitude.
- Audio Sink with Sample Rate = 48000.

Increasing playback gain makes both the recovered signal and noise louder. It does not improve the radio signal-to-noise ratio.

### Experiment E: microphone input later

After a repeatable WAV-file link works, use Audio Source for microphone input. Check Windows microphone permissions, the selected device, sample rate, and amplitude.

Continuous audio also involves independent audio-device and radio clocks. Long-running playback may need buffering or clock-rate handling if interruptions occur. A successful sine-wave link does not prove uninterrupted live audio.

Do not change Pluto's sample rate to 48000 simply because the audio uses 48000. Use explicit sample-rate conversion and keep all dependent filters and displays consistent.

## 13. What was checked during preparation

These checks refer to the earlier preparation of the supplied v2 flowgraphs, not to a new physical RF test during this English translation:

- GNU Radio 3.10.12.0 GRC source was used to validate block definitions, connections, sample types, and expressions, and to generate the supplied Python files.
- Generation used import substitutes for unavailable radio and Qt libraries. This checked the GRC generation path; it did not execute the actual GNU Radio DSP, GUI, or Pluto hardware.
- Generated Python syntax was checked. The receiver explicitly uses manual gain and Auto filter configuration.
- Slider callbacks were exercised with substitute blocks to check that ka, message frequency, TX attenuation, RX gain, and carrier position reach the intended setters.
- An independent numerical simulation covered mu = 0.5, 1.0, and 1.3, carrier offsets of approximately +/-7 kHz, and an added-noise case. It recovered the 1 kHz component and showed the expected envelope-detection distortion during overmodulation.
- Actual RF transmission, Qt operation, analog bandwidth, absolute power, and audio continuity were not tested in the preparation environment. Your hardware screenshots and controlled experiments provide the evidence for your devices.

The current version also uses automatic device discovery by default, correct enum storage, separate message/carrier views, and a lower-rate selected-channel spectrum. The old short raw I/Q view was removed from the main interface because it did not show a full 1 kHz message cycle. The generated Python class names end in _v2 to help distinguish them from earlier versions.

## 14. Short review questions

1. Is 2.45 GHz the message frequency? No. It is the tuning center. Our message is 1 kHz and our RF carrier is 2.4502 GHz with the current values.
2. Why do we receive a trace before TX runs? The receiver captures noise, environmental signals, and internal artifacts continuously.
3. Does more RX gain always help? No. It can cause overload and cannot remove noise already mixed with the signal.
4. Why remove DC after Complex to Mag? To remove the constant carrier envelope level and leave the changing message around zero.
5. Must TX and RX always use equal sample rates? Not in general. Their frequency coverage and processing must be compatible, and each internal path must handle rates correctly. We chose equal radio rates to simplify this example.
6. Why can we not report dBm directly from the spectrum? The display has not been calibrated for absolute RF power.
7. Why is a 1 kHz recovered waveform not sufficient proof? An unintended signal or artifact can also be periodic. Controlled TX changes establish the relationship.

This foundation supports later channel detection, I/Q recording, and relative received-power analysis for the robot-tracking project. First become comfortable selecting the intended signal, verifying its source, and measuring it consistently before adding localization, EKF, or AoA.

## 15. Official references

- [GNU Radio v3.10.12.0 source](https://github.com/gnuradio/gnuradio/tree/v3.10.12.0)
- [PlutoSDR Source](https://wiki.gnuradio.org/index.php/PlutoSDR_Source)
- [PlutoSDR Sink](https://wiki.gnuradio.org/index.php/PlutoSDR_Sink)
- [QT GUI Time Sink](https://wiki.gnuradio.org/index.php/QT_GUI_Time_Sink)
- [QT GUI Frequency Sink](https://wiki.gnuradio.org/index.php/QT_GUI_Frequency_Sink)
- [Frequency Xlating FIR Filter](https://wiki.gnuradio.org/index.php/Frequency_Xlating_FIR_Filter)
- [Complex to Mag](https://wiki.gnuradio.org/index.php/Complex_to_Mag)
- [DC Blocker](https://wiki.gnuradio.org/index.php/DC_Blocker)
- [Audio Sink](https://wiki.gnuradio.org/index.php/Audio_Sink)
