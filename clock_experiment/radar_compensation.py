"""Known-instrument calibration for a simplified coherent pulsed radar."""
import numpy as np
C=299792458.

def estimate(iq,fs,prf,carrier,bearing,trigger_offset_s=0.,bearing_bias=0.,instrument_phase=None):
    z=np.asarray(iq,complex)
    if z.ndim!=2 or min(z.shape)<2 or not np.isfinite(z).all(): raise ValueError('Finite pulses x samples required')
    if min(fs,prf,carrier)<=0 or not np.isfinite([fs,prf,carrier,bearing,trigger_offset_s,bearing_bias]).all():
        raise ValueError('Invalid acquisition parameters')
    if instrument_phase is not None:
        phi=np.asarray(instrument_phase,float)
        if phi.shape!=(len(z),) or not np.isfinite(phi).all(): raise ValueError('Phase shape mismatch')
        z=z*np.exp(-1j*phi[:,None])
    energy=np.mean(abs(z)**2,axis=0)
    if not np.any(energy>0): raise ValueError('No received signal')
    k=int(np.argmax(energy))
    cross=np.sum(z[1:,k]*np.conj(z[:-1,k]))
    if abs(cross)==0: raise ValueError('No coherent phase information')
    velocity=C/carrier*prf*np.angle(cross)/(4*np.pi)
    theta=(bearing-bearing_bias+np.pi)%(2*np.pi)-np.pi
    return {'range_m':float(C*(k/fs-trigger_offset_s)/2), 'bearing_rad':float(theta),
            'radial_velocity_m_s':float(velocity),'range_bin':k,
            'unambiguous_speed_m_s':float(C/carrier*prf/4)}

def simulate(seed,range_m=1200.,speed=0.,bearing=.1,trigger_samples=3,bearing_bias=.025,instrument_speed=.7,noise=.15):
    fs=20e6; prf=8000.; carrier=77e9; wavelength=C/carrier
    pulse_time=np.arange(64)/prf; sample=np.arange(2048)
    centre=2*range_m/C*fs+trigger_samples
    envelope=np.exp(-.5*((sample-centre)/1.5)**2)
    instrument_phase=4*np.pi*instrument_speed*pulse_time/wavelength
    phase=4*np.pi*speed*pulse_time/wavelength+instrument_phase
    rng=np.random.default_rng(seed)
    iq=np.exp(1j*phase[:,None])*envelope[None,:]+noise*(rng.normal(size=(64,2048))+1j*rng.normal(size=(64,2048)))
    return iq,{'fs':fs,'prf':prf,'carrier':carrier,'bearing':bearing+bearing_bias}, {
        'trigger_offset_s':trigger_samples/fs,'bearing_bias':bearing_bias,'instrument_phase':instrument_phase}
