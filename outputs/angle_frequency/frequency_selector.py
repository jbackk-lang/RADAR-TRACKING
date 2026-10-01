import numpy as np

C=299792458.; F0=77e9; CENTER=1.2
FREQUENCIES=np.linspace(75e9,79e9,9)
SCAN=CENTER+np.deg2rad(np.linspace(-4,4,41))
ANGLES=CENTER+np.deg2rad(np.linspace(-2,2,41))
RANGES=np.linspace(-.06,.06,13)
THETA,DR=np.meshgrid(ANGLES,RANGES,indexing='ij')
THETA=THETA.ravel(); DR=DR.ravel()

def template(theta,dr):
    theta=np.atleast_1d(theta); dr=np.atleast_1d(dr)
    beam=np.exp(-2*np.log(2)*((SCAN[:,None]-theta)/np.deg2rad(1.5))**2)
    spatial=2*np.pi*FREQUENCIES[:,None,None]*(C/(2*F0))/C*np.arange(2)[None,:,None]*np.sin(theta)[None,None,:]
    delay=-4*np.pi*(FREQUENCIES-F0)[:,None,None]*dr[None,None,:]/C
    return (np.exp(1j*(spatial+delay))[:,:,None,:]*beam[None,None,:,:]/np.sqrt(18)).reshape(-1,len(theta))

def generate(seed,weak=False,separation=.75,dr=0.,empty=False,impulsive=False):
    rng=np.random.default_rng(seed)
    strong_angle=CENTER+np.deg2rad(rng.uniform(-.08,.08))
    y=np.zeros(9*2*41,complex)
    if not empty:
        y+=template(strong_angle,0.)[:,0]*np.exp(1j*rng.uniform(-np.pi,np.pi))
    weak_angle=strong_angle+np.deg2rad(separation)
    if weak:
        y+=.15*template(weak_angle,dr)[:,0]*np.exp(1j*rng.uniform(-np.pi,np.pi))
    y+=.04*(rng.normal(size=len(y))+1j*rng.normal(size=len(y)))
    if impulsive:
        cube=y.reshape(9,2,41)
        positions=rng.choice(41,4,replace=False)
        cube[:,:,positions]+=.5*(rng.normal(size=(9,2,4))+1j*rng.normal(size=(9,2,4)))
    return y,dict(weak_angle=weak_angle,dr=dr,strong_angle=strong_angle)

class FrequencySelector:
    def __init__(self):
        self.a=template(THETA,DR)
        self.norm=np.sum(abs(self.a)**2,axis=0)

    def scores(self,y):
        y=np.asarray(y,complex)
        if y.shape!=(738,) or not np.isfinite(y).all():
            raise ValueError('Finite 9 frequencies x 2 receivers x 41 scan positions required')
        weights=np.ones(41)
        for _ in range(2):
            w=np.tile(weights,18)
            norms=np.sum(abs(self.a)**2*w[:,None],axis=0)
            b=self.a.conj().T@(w*y)
            strong=int(np.argmax(abs(b)**2/norms))
            residual=y-self.a[:,strong]*(b[strong]/norms[strong])
            magnitude=np.sqrt(np.mean(abs(residual.reshape(9,2,41))**2,axis=(0,1)))
            cutoff=max(4*float(np.median(magnitude)),1e-12)
            weights=np.minimum(1.,cutoff/np.maximum(magnitude,1e-12))
        w=np.tile(weights,18)
        a=self.a*np.sqrt(w)[:,None]; z=y*np.sqrt(w)
        norms=np.sum(abs(a)**2,axis=0); b=a.conj().T@z
        strong=int(np.argmax(abs(b)**2/norms))
        s=a[:,strong]; cross=a.conj().T@s
        retained=norms-abs(cross)**2/norms[strong]
        numerator=b-cross*b[strong]/norms[strong]
        valid=retained>.05*norms
        coherent=np.where(valid,abs(numerator)**2/np.maximum(retained,1e-15),-np.inf)
        cube=a.reshape(9,82,-1); zcube=z.reshape(9,82)
        incoherent=np.zeros(len(THETA)); band_valid=np.ones(len(THETA),bool)
        for band in range(9):
            aa=cube[band]; zz=zcube[band]; ss=aa[:,strong]
            norm=np.sum(abs(aa)**2,axis=0); ns=float(np.vdot(ss,ss).real)
            bb=aa.conj().T@zz; cc=aa.conj().T@ss
            rr=norm-abs(cc)**2/ns
            num=bb-cc*(np.vdot(ss,zz)/ns)
            band_valid&=rr>.05*norm
            incoherent+=abs(num)**2/np.maximum(rr,1e-15)
        incoherent=np.where(band_valid,incoherent,-np.inf)
        out={}
        for name,values in (('coherent',coherent),('band_power',incoherent)):
            index=int(np.argmax(values))
            out[name]=dict(score=float(values[index]),angle=float(THETA[index]),dr=float(DR[index]))
        return out
