"""Two-receiver frequency-resolved far-field phase experiment."""
import numpy as np

C = 299792458.
F0 = 77e9
D = C/(2*79e9)
METHODS = ('phase_center','phase_all','slope_two','slope_all')

def simulate(seed,theta,bandwidth=4e9,phase_offset=0.,channel_delay=0.,noise=.15):
    f = np.linspace(F0-bandwidth/2,F0+bandwidth/2,17)
    rng = np.random.default_rng(seed)
    common = rng.uniform(-np.pi,np.pi,size=(len(f),64))
    phi = 2*np.pi*f*(D*np.sin(theta)/C+channel_delay)+phase_offset
    iq = np.stack((np.exp(1j*common),np.exp(1j*(common+phi[:,None]))),axis=1)
    iq += noise*(rng.normal(size=iq.shape)+1j*rng.normal(size=iq.shape))
    return f,iq

def estimate(f,iq,d=D):
    f = np.asarray(f,dtype=float)
    iq = np.asarray(iq,dtype=complex)
    if (f.ndim!=1 or len(f)<2 or not np.isfinite(f).all() or
        np.any(f<=0) or np.any(np.diff(f)<=0) or not np.isfinite(d) or d<=0):
        raise ValueError('Increasing finite positive frequencies and spacing required')
    if iq.ndim!=3 or iq.shape[:2]!=(len(f),2) or iq.shape[2]<1 or not np.isfinite(iq).all():
        raise ValueError('Finite frequency x 2 receivers x snapshots required')
    cross = np.mean(iq[:,1,:]*np.conj(iq[:,0,:]),axis=1)
    if np.any(abs(cross)==0):
        raise ValueError('No interreceiver phase information')
    phase = np.unwrap(np.angle(cross))
    center = len(f)//2
    # Center phase is anchored to the principal branch, fixing the shared 2*pi ambiguity.
    phase -= 2*np.pi*np.round((phase[center]-np.angle(cross[center]))/(2*np.pi))
    phase_delay = float(np.dot(f/F0,phase)/np.dot(f/F0,f/F0)/(2*np.pi*F0))
    x = (f-f.mean())/np.ptp(f)
    slope_delay = float(np.dot(x,phase)/np.dot(x,x)/(2*np.pi*np.ptp(f)))
    delays = dict(phase_center=float(phase[center]/(2*np.pi*f[center])),phase_all=phase_delay,
                  slope_two=float((phase[-1]-phase[0])/(2*np.pi*(f[-1]-f[0]))),slope_all=slope_delay)
    out = {}
    for method,delay in delays.items():
        sine = C*delay/d
        out[method] = dict(sine=sine,angle_rad=float(np.arcsin(sine)) if abs(sine)<=1 else None)
    return out
