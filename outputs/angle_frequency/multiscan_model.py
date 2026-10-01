import numpy as np
from stereo_model import JointEstimator,GRID

class MultiScanEstimator(JointEstimator):
    def propose(self,scans):
        y=np.asarray(scans,complex)
        if y.ndim!=2 or y.shape[1]!=self.a.shape[0] or len(y)<2 or not np.isfinite(y).all():
            raise ValueError('At least two finite scans required')
        b=self.a.conj().T@y.T
        score1=np.sum(abs(b)**2,axis=1)/self.norm
        one=int(np.argmax(score1))
        i,j=self.i,self.j
        cross=self.gram[i,j,None]
        determinant=self.norm[i]*self.norm[j]-abs(self.gram[i,j])**2
        score2=np.sum(self.norm[j,None]*abs(b[i])**2+self.norm[i,None]*abs(b[j])**2-
                      2*np.real(np.conj(b[i])*cross*b[j]),axis=1)/determinant
        best=int(np.argmax(score2)); pair=[int(i[best]),int(j[best])]
        n=2*y.size; energy=float(np.sum(abs(y)**2)); s=len(y)
        rss1=max(energy-float(score1[one]),np.finfo(float).tiny)
        rss2=max(energy-float(score2[best]),np.finfo(float).tiny)
        bic1=n*np.log(rss1/n)+(1+2*s)*np.log(n)
        bic2=n*np.log(rss2/n)+(2+4*s)*np.log(n)
        return dict(indices=pair if bic2<bic1 else [one],one_index=one,
                    bic_one=float(bic1),bic_two=float(bic2),training_scans=s)

    def confirm(self,proposal,scan):
        y=np.asarray(scan,complex)
        if y.shape!=(self.a.shape[0],) or not np.isfinite(y).all():
            raise ValueError('Finite confirmation scan required')
        indices=proposal['indices']
        def rss(selected):
            a=self.a[:,selected]
            return float(np.sum(abs(y-a@np.linalg.lstsq(a,y,rcond=None)[0])**2))
        residual=rss(indices); n=2*len(y)
        energy=float(np.sum(abs(y)**2))
        ratio=residual/max(energy,np.finfo(float).tiny)
        confirmed=ratio<=.5
        gain=None
        if len(indices)==2:
            single_res=min(rss([i]) for i in set(indices+[proposal['one_index']]))
            bic1=n*np.log(max(single_res,np.finfo(float).tiny)/n)+2*np.log(n)
            bic2=n*np.log(max(residual,np.finfo(float).tiny)/n)+4*np.log(n)
            gain=float(bic1-bic2)
            confirmed=confirmed and gain>0
        return dict(state='confirmed' if confirmed else 'uncertain',count=len(indices) if confirmed else 0,
                    angles=GRID[indices].tolist() if confirmed else [],proposed_angles=GRID[indices].tolist(),
                    residual_energy_ratio=ratio,confirmation_bic_gain=gain)
