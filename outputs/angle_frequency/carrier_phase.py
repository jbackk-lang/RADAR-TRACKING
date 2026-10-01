import numpy as np

C=299792458.; CARRIER=77e9; WAVELENGTH=C/CARRIER; FS=20e6; PRF=8000.
TIMES=np.arange(64)/PRF
CASES={'single_slow':(1.,.04,False,0.),'single_fast':(1.,1.,False,0.),
       'weak_isolated':(.2,.04,False,0.),'weak_overlap':(.2,.04,True,0.),
       'weak_overlap_separated_doppler':(.2,1.,True,0.),'instrument_drift':(1.,.04,False,.02)}

def simulate(seed,case):
    amplitude,velocity,overlap,drift=CASES[case]
    rng=np.random.default_rng(seed); sample=np.arange(512)
    distance=1200+velocity*TIMES
    center=2*distance/C*FS
    envelope=np.exp(-.5*((sample[None,:]-center[:,None])/1.5)**2)
    phi=rng.uniform(-np.pi,np.pi)+4*np.pi*distance/WAVELENGTH+4*np.pi*drift*TIMES/WAVELENGTH
    iq=amplitude*envelope*np.exp(1j*phi[:,None])
    if overlap:
        strong=np.exp(-.5*((sample-2*1201/C*FS)/1.5)**2)
        iq+=strong[None,:]*np.exp(1j*(rng.uniform(-np.pi,np.pi)+4*np.pi*1201/WAVELENGTH))
    iq+=.15*(rng.normal(size=iq.shape)+1j*rng.normal(size=iq.shape))
    return iq,velocity

def estimate(iq):
    iq=np.asarray(iq,complex)
    if iq.shape!=(64,512) or not np.isfinite(iq).all():
        raise ValueError('Finite 64 x 512 I/Q required')
    k=int(np.argmax(np.mean(abs(iq)**2,axis=0)))
    cross=np.sum(iq[1:,k]*np.conj(iq[:-1,k]))
    baseline=float(WAVELENGTH*PRF*np.angle(cross)/(4*np.pi))
    indices=np.arange(max(0,k-3),min(512,k+4))
    weights=np.exp(-.5*((indices-k)/1.5)**2)
    phasor=iq[:,indices]@weights/weights.sum()
    spectrum=abs(np.fft.fft(phasor,4096))**2
    peak=int(np.argmax(spectrum)); left=spectrum[(peak-1)%4096]; mid=spectrum[peak]; right=spectrum[(peak+1)%4096]
    denominator=left-2*mid+right
    offset=float(.5*(left-right)/denominator) if denominator!=0 else 0.
    offset=float(np.clip(offset,-.5,.5))
    index=(peak+offset+2048)%4096-2048
    velocity=float(WAVELENGTH/2*index*PRF/4096)
    return dict(range_m=float(C*k/(2*FS)),baseline_v=baseline,carrier_v=velocity,
                baseline_delta_m=baseline*TIMES[-1],carrier_delta_m=velocity*TIMES[-1]),phasor
