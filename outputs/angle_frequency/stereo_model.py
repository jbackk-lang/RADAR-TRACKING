import numpy as np

C=299792458.
F=77e9
SPACING=C/(2*F)
CENTER=1.2
WIDTH=np.deg2rad(1.5)
SCAN=CENTER+np.deg2rad(np.linspace(-6,6,121))
GRID=CENTER+np.deg2rad(np.linspace(-5,5,101))

def templates(angles,receivers=2):
    angles=np.asarray(angles,float)
    beam=np.exp(-2*np.log(2)*((SCAN[:,None]-angles[None,:])/WIDTH)**2)
    spatial=np.exp(1j*2*np.pi*F*SPACING/C*np.arange(receivers)[:,None]*np.sin(angles)[None,:])
    return (beam[:,None,:]*spatial[None,:,:]/np.sqrt(receivers)).reshape(-1,len(angles))

def simulate(seed,angles,amplitudes,receivers=2,noise=.05):
    rng=np.random.default_rng(seed)
    signal=templates(angles,receivers)@np.asarray(amplitudes,complex)
    signal+=noise*(rng.normal(size=signal.shape)+1j*rng.normal(size=signal.shape))
    return signal

class JointEstimator:
    def __init__(self,receivers=2):
        if receivers not in (1,2):
            raise ValueError('One or two receivers required')
        self.a=templates(GRID,receivers)
        self.gram=self.a.conj().T@self.a
        self.norm=np.real(np.diag(self.gram))
        i,j=np.triu_indices(len(GRID),k=1)
        mask=(GRID[j]-GRID[i]>=np.deg2rad(.3)-1e-12)
        self.i,self.j=i[mask],j[mask]

    def fit(self,signal):
        y=np.asarray(signal,complex)
        if y.shape!=(self.a.shape[0],) or not np.isfinite(y).all():
            raise ValueError('Finite scan samples with expected receiver count required')
        b=self.a.conj().T@y
        energy=float(np.vdot(y,y).real)
        score1=abs(b)**2/self.norm
        one=int(np.argmax(score1))
        i,j=self.i,self.j
        cross=self.gram[i,j]
        determinant=self.norm[i]*self.norm[j]-abs(cross)**2
        score2=(self.norm[j]*abs(b[i])**2+self.norm[i]*abs(b[j])**2-2*np.real(np.conj(b[i])*cross*b[j]))/determinant
        best=int(np.argmax(score2))
        pair=[int(i[best]),int(j[best])]
        n=2*len(y)
        rss1=max(energy-float(score1[one]),np.finfo(float).tiny)
        rss2=max(energy-float(score2[best]),np.finfo(float).tiny)
        bic1=n*np.log(rss1/n)+3*np.log(n)
        bic2=n*np.log(rss2/n)+6*np.log(n)
        selected=pair if bic2<bic1 else [one]
        coefficients=np.linalg.lstsq(self.a[:,selected],y,rcond=None)[0]
        return dict(count=len(selected),angles=GRID[selected].tolist(),bic_one=float(bic1),bic_two=float(bic2),
                    amplitudes=[[float(v.real),float(v.imag)] for v in coefficients])
