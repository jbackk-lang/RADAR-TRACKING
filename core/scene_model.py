"""Two-detection scene model with real repository TIMDR operator."""
import numpy as np
from .timdr_change import timdr_change

def recognize_scene(positions,doppler,times,use_timdr=False):
    p=np.array(positions,float,copy=True);v=np.array(doppler,float,copy=True);t=np.asarray(times,float)
    if p.ndim!=3 or p.shape[1:]!=(2,2) or v.shape!=p.shape[:2] or t.ndim!=1 or len(t)!=len(p) or len(t)<3:
        raise ValueError('Two 2D detections per frame with times and Doppler required')
    if not np.isfinite(p).all() or not np.isfinite(v).all() or not np.isfinite(t).all() or np.any(np.diff(t)<=0):raise ValueError('Finite inputs and increasing times required')
    decisions=[];calls=0
    for i in range(1,len(t)):
        prediction=p[i-1].copy();scores=[]
        if i>=2:
            velocity=(p[i-1]-p[i-2])/(t[i-1]-t[i-2])
            for j in range(2):
                if use_timdr:
                    history=[dict(x=float(p[k,j,0]),y=float(p[k,j,1]),t=float(t[k])) for k in range(max(0,i-6),i)]
                    score=timdr_change(history);calls+=1
                else:score=dict(T=0.,D=0.,R=0.,TIMDR=0.)
                scores.append(score)
                damping=max(.2,1-score['TIMDR']) if use_timdr else 1.
                prediction[j]+=velocity[j]*(t[i]-t[i-1])*damping
        swapped=np.sum((p[i,::-1]-prediction)**2)<np.sum((p[i]-prediction)**2)
        if swapped:p[i]=p[i,::-1];v[i]=v[i,::-1]
        decisions.append(dict(frame=i,swapped=bool(swapped),scores=scores))
    ranges=np.linalg.norm(p,axis=2)
    slopes=np.array([np.polyfit(t,ranges[:,j],1)[0] for j in range(2)])
    mismatch=float(np.max(abs(slopes-v.mean(axis=0))))
    separation=np.linalg.norm(p[:,1]-p[:,0],axis=1);spread=float(np.std(separation))
    if mismatch>.6:label='inconsistent_echo';count=None
    elif spread>.35:label='separate_motion';count=2
    else:label='coherent_group_unresolved';count=None
    return dict(label=label,count=count,observed_extent_m=float(np.median(separation)),timdr_calls=calls,association=decisions)
