import numpy as np
from angle_model import C

def simulate(seed,theta,turns,delay,zero,variable=False):
    rng=np.random.default_rng(seed)
    omega=2*np.pi*turns
    t=np.arange(0,max(.5,2.4/omega+.05),.0002)
    phase=float(rng.uniform(-np.pi,np.pi))
    amplitude=.05 if variable else 0.
    angle=omega*t+omega*amplitude/(4*np.pi)*(np.cos(phase)-np.cos(4*np.pi*t+phase))
    power=np.exp(-4*np.log(2)*((angle-theta)/np.deg2rad(1.5))**2)
    iq=np.sqrt(power)+.1*(rng.normal(size=len(t))+1j*rng.normal(size=len(t)))
    return dict(echo_time=t+2*1500/C+delay,iq=iq,encoder_time=t,
                encoder_angle=angle+zero+np.deg2rad(.02)*rng.normal(size=len(t)),
                measured_range_m=float(1500+rng.normal(0,2)),nominal_omega=omega)

def window(data):
    et=np.asarray(data['encoder_time'],float); ea=np.asarray(data['encoder_angle'],float)
    echo=np.asarray(data['echo_time'],float); iq=np.asarray(data['iq'],complex)
    distance=data['measured_range_m']; omega=data['nominal_omega']
    if (et.ndim!=1 or ea.shape!=et.shape or echo.shape!=iq.shape or echo.ndim!=1 or
        len(et)<3 or np.any(np.diff(et)<=0) or np.any(np.diff(echo)<=0) or
        not all(np.isfinite(v).all() for v in (et,ea,echo,iq)) or
        not np.isfinite([distance,omega]).all() or min(distance,omega)<=0):
        raise ValueError('Finite ordered scan and encoder data required')
    time=echo-2*distance/C
    power=abs(iq)**2; peak=int(np.argmax(power))
    mask=abs(time-time[peak])<=3*np.deg2rad(1.5)/omega
    w=np.maximum(power[mask]-np.median(power)/np.log(2),0.)
    if w.sum()<=0:
        raise ValueError('No reference beam passage')
    return time[mask],w/w.sum(),et,np.unwrap(ea)

def read_angle(data,delay=0.,zero=0.):
    time,w,et,ea=window(data)
    shifted=time-delay
    if shifted.min()<et[0] or shifted.max()>et[-1]:
        raise ValueError('Encoder does not cover shifted echo window')
    return float(np.dot(w,np.interp(shifted,et,ea))-zero)

def calibrate(references,known_angles):
    if len(references)<3 or len(references)!=len(known_angles) or not np.isfinite(known_angles).all():
        raise ValueError('At least three known reference angles required')
    windows=[window(data) for data in references]
    speeds=[]
    for time,w,et,ea in windows:
        center=float(np.dot(w,time))
        mask=abs(et-center)<.012
        speeds.append(float(np.polyfit(et[mask]-center,ea[mask],1)[0]))
    if np.std(speeds)<.5:
        raise ValueError('Time offset and encoder zero are not identifiable at these rotation speeds')
    grid=np.linspace(-.004,.004,801)
    residuals=[]
    for time,w,et,ea in windows:
        if (time-grid.max()).min()<et[0] or (time-grid.min()).max()>et[-1]:
            raise ValueError('Encoder does not cover calibration delay range')
        residuals.append([float(np.dot(w,np.interp(time-delay,et,ea))) for delay in grid])
    residuals=np.array(residuals)-np.array(known_angles)[:,None]
    losses=np.var(residuals,axis=0); best=int(np.argmin(losses))
    rmse=float(np.sqrt(losses[best]))
    if best in (0,len(grid)-1) or rmse>np.deg2rad(.15):
        raise ValueError('Reference fit rejected: boundary or inconsistent reference')
    return dict(delay_s=float(grid[best]),zero_rad=float(residuals[:,best].mean()),
                reference_rmse_rad=rmse,angle_only_rad=float(residuals[:,400].mean()),
                measured_speed_std=float(np.std(speeds)))
