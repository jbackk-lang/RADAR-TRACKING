import numpy as np
from angle_model import C

OMEGA=2*np.pi
BEAMWIDTH=np.deg2rad(1.5)
METHODS=('nominal_time_peak','encoder_peak','encoder_centroid')

def pointing(t,variation=0.,phase=0.):
    return OMEGA*t+OMEGA*variation/(4*np.pi)*(np.cos(phase)-np.cos(4*np.pi*t+phase))

def simulate(seed,theta,variation=0.,clock_offset=0.,noise=.1,encoder_noise=np.deg2rad(.02)):
    rng=np.random.default_rng(seed)
    t=np.arange(0,.5001,.0002)
    phase=float(rng.uniform(-np.pi,np.pi))
    angles=pointing(t,variation,phase)
    power=np.exp(-4*np.log(2)*((angles-theta)/BEAMWIDTH)**2)
    iq=np.sqrt(power).astype(complex)
    iq+=noise*(rng.normal(size=len(t))+1j*rng.normal(size=len(t)))
    encoder=angles+encoder_noise*rng.normal(size=len(t))
    return dict(echo_time=t+2*1500/C+clock_offset,iq=iq,encoder_time=t,encoder_angle=encoder,measured_range_m=1500.)

def estimate(data):
    echo_time=np.asarray(data['echo_time'],float)
    iq=np.asarray(data['iq'],complex)
    et=np.asarray(data['encoder_time'],float)
    ea=np.asarray(data['encoder_angle'],float)
    distance=data['measured_range_m']
    if (echo_time.ndim!=1 or iq.shape!=echo_time.shape or len(echo_time)<3 or
        et.ndim!=1 or ea.shape!=et.shape or len(et)<2 or np.any(np.diff(et)<=0) or
        np.any(np.diff(echo_time)<=0) or not np.isfinite(distance) or distance<=0 or
        not all(np.isfinite(v).all() for v in (echo_time,iq,et,ea))):
        raise ValueError('Finite echoes, ordered encoder samples and positive measured range required')
    transmit_time=echo_time-2*distance/C
    power=abs(iq)**2
    peak=int(np.argmax(power))
    mask=abs(transmit_time-transmit_time[peak])<=3*BEAMWIDTH/OMEGA
    if transmit_time[mask].min()<et[0] or transmit_time[mask].max()>et[-1]:
        raise ValueError('Encoder does not cover echo window')
    angle=np.interp(transmit_time[mask],et,np.unwrap(ea))
    weights=np.maximum(0.,power[mask]-np.median(power)/np.log(2))
    if weights.sum()<=0:
        raise ValueError('No beam passage detected')
    return dict(nominal_time_peak=float(OMEGA*transmit_time[peak]),
                encoder_peak=float(np.interp(transmit_time[peak],et,np.unwrap(ea))),
                encoder_centroid=float(np.dot(angle,weights)/weights.sum()))
