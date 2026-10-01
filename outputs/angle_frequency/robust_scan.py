import numpy as np
from stereo_model import JointEstimator,GRID,templates

class RobustScanEstimator(JointEstimator):
    def __init__(self,receivers=2):
        super().__init__(receivers)
        self.receivers=receivers
        self.previous=[]

    def _fit_weighted(self,y,weights):
        a=self.a*np.sqrt(weights)[:,None]
        z=y*np.sqrt(weights)
        gram=a.conj().T@a; norm=np.real(np.diag(gram)); b=a.conj().T@z
        i,j=self.i,self.j; cross=gram[i,j]
        determinant=norm[i]*norm[j]-abs(cross)**2
        score1=abs(b)**2/norm; one=int(np.argmax(score1))
        score2=(norm[j]*abs(b[i])**2+norm[i]*abs(b[j])**2-2*np.real(np.conj(b[i])*cross*b[j]))/determinant
        best=int(np.argmax(score2)); pair=[int(i[best]),int(j[best])]
        energy=float(np.vdot(z,z).real); n=2*len(z)
        rss1=max(energy-float(score1[one]),np.finfo(float).tiny)
        rss2=max(energy-float(score2[best]),np.finfo(float).tiny)
        gain=n*np.log(rss1/rss2)-3*np.log(n)
        selected=pair if gain>6 else [one]
        def solution(indices):
            aa=a[:,indices]
            coefficients=np.linalg.lstsq(aa,z,rcond=None)[0]
            rss=float(np.sum(abs(z-aa@coefficients)**2))
            variance=rss/max(1,2*len(z)-2*len(indices))
            sd=np.sqrt(2*variance*np.real(np.diag(np.linalg.inv(aa.conj().T@aa))))
            return coefficients,abs(coefficients)/np.maximum(sd,1e-15)
        coeff,snr=solution(selected)
        if len(selected)==2 and np.any(snr<4):
            selected=[one]; coeff,snr=solution(selected)
        if np.any(snr<4):
            selected=[]; coeff=np.array([],complex)
        prediction=self.a[:,selected]@coeff if selected else np.zeros_like(y)
        return selected,prediction,float(gain)

    def fit_current(self,signal):
        y=np.asarray(signal,complex)
        if y.shape!=(self.a.shape[0],) or not np.isfinite(y).all():
            raise ValueError('Finite scan with expected receiver count required')
        weights=np.ones(len(y))
        for _ in range(3):
            indices,prediction,gain=self._fit_weighted(y,weights)
            residual=(y-prediction).reshape(-1,self.receivers)
            norms=np.sqrt(np.mean(abs(residual)**2,axis=1))
            threshold=max(4*float(np.median(norms))/np.sqrt(np.log(2)),1e-12)
            group_weights=np.minimum(1.,threshold/np.maximum(norms,1e-12))
            weights=np.repeat(group_weights,self.receivers)
        indices,prediction,gain=self._fit_weighted(y,weights)
        return dict(count=len(indices),angles=GRID[indices].tolist(),bic_gain=gain,
                    downweighted_positions=int(np.sum(weights.reshape(-1,self.receivers)[:,0]<.999))),weights

    def observe(self,signal):
        current,weights=self.fit_current(signal)
        angles=np.array(current['angles']); smoothed=False
        if len(angles)>0 and len(angles)==len(self.previous) and np.max(abs(angles-self.previous))<=np.deg2rad(.15):
            proposal=.75*angles+.25*np.array(self.previous)
            y=np.asarray(signal)*np.sqrt(weights)
            def loss(theta):
                a=templates(theta,self.receivers)*np.sqrt(weights)[:,None]
                return float(np.sum(abs(y-a@np.linalg.lstsq(a,y,rcond=None)[0])**2))
            if loss(proposal)<=1.05*loss(angles):
                angles=proposal; smoothed=True
        self.previous=angles.tolist()
        return {**current,'angles':self.previous.copy(),'memory_used':smoothed}
