"""NumPy-only low-rank flux reconstruction at arbitrary target points."""
import numpy as np

class FieldEstimator:
    def __init__(self,path):
        d=np.load(path)
        for name in ['sx','mu_x','mu_y','G','C','var','basis','mean_psi','spline']:
            setattr(self,name,d[name])
        self.lam=float(d['lam']);self.ip0=float(d['ip0'])
        self.grid=np.concatenate([self.mean_psi[None],self.basis.reshape(-1,65,65)])
        self.full_W=np.linalg.solve(self.G+np.diag(self.var+self.lam),self.C)
        self.reset()
    def reset(self):
        self.keep=None;self.W=None
    def prepare(self,obs):
        if self.keep is None:
            keep=np.ones(512,bool);keep[:500]=obs[:500]!=0
            self.keep=np.flatnonzero(keep)
            self.W=self.full_W if keep.all() else np.linalg.solve(self.G[np.ix_(keep,keep)]+np.diag(self.var[keep]+self.lam),self.C[keep])
            W=self.W
            self.raw_W=(W/self.sx[self.keep,None]).astype(np.float32)
            self.bias=(self.mu_y-(self.mu_x[self.keep]/self.sx[self.keep])@W).astype(np.float32)
    def predict(self,obs):
        self.prepare(obs)
        x=np.asarray(obs[self.keep],dtype=np.float32)
        return (x@self.raw_W)*(self.ip0/max(float(obs[512]),1e4))+self.bias
    def bilinear(self,pts):
        q=(np.asarray(pts)-[.1,-2.2])/[1.9/64,4.4/64]
        ix=np.floor(q).astype(int);ix=np.clip(ix,0,63);w=q-ix
        a,b=ix.T;u,v=w.T;g=self.grid
        return ((1-u)*(1-v))[:,None]*g[:,a,b].T+(u*(1-v))[:,None]*g[:,a+1,b].T+((1-u)*v)[:,None]*g[:,a,b+1].T+(u*v)[:,None]*g[:,a+1,b+1].T
    @staticmethod
    def weights(t,h,order):
        if order==0:return np.stack([(1-t)**3,3*t**3-6*t*t+4,-3*t**3+3*t*t+3*t+1,t**3],1)/6
        if order==1:return np.stack([-.5*(1-t)**2,1.5*t*t-2*t,-1.5*t*t+t+.5,.5*t*t],1)/h
        return np.stack([1-t,3*t-2,-3*t+1,t],1)/(h*h)
    def cubic(self,pts,dr=0,dz=0):
        h=np.array([1.9/64,4.4/64]);q=(np.asarray(pts)-[.1,-2.2])/h
        ix=np.floor(q).astype(int);ix=np.clip(ix,2,61);t=q-ix
        ir=ix[:,0,None]+np.arange(-1,3);iz=ix[:,1,None]+np.arange(-1,3)
        c=self.spline[:,ir[:,:,None],iz[:,None,:]]
        return np.einsum('ni,nj,knij->nk',self.weights(t[:,0],h[0],dr),self.weights(t[:,1],h[1],dz),c,optimize=False)
    def cache(self,pts,xp):
        # Fields at 32 target boundary points, then a quadratic expansion at
        # both requested X-points and an axis guess. All geometry is observed.
        theta=np.arctan2(pts[:,1],pts[:,0]-.95)
        self.cos=np.cos(theta); self.sin=np.sin(theta)
        center=np.array([[.95,float(np.median(pts[:,1]))]])
        critical=np.vstack([xp,center])
        values=[self.bilinear(pts),self.cubic(pts,1,0),self.cubic(pts,0,1)]
        crit=[self.cubic(critical,dr,dz) for dr,dz in [(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)]]
        return np.vstack(values+[np.stack(crit,1).reshape(18,-1)]).astype(np.float32)
    def measurements(self,obs,cache,rt,theta,xt):
        f=self.predict(obs)
        h=np.empty(len(f),dtype=np.float32); h[0]=1.;h[1:]=f[:-1]
        v=cache@h
        stationary=[]; y=np.empty(37)
        for i,q in enumerate(v[96:].reshape(3,6).tolist()):
            value,gr,gz,hrr,hrz,hzz=q
            det=hrr*hzz-hrz*hrz
            if abs(det)<1e-10:det=-1e-10 if det<0 else 1e-10
            dr=max(-.15,min(.15,(hzz*gr-hrz*gz)/det))
            dz=max(-.15,min(.15,(hrr*gz-hrz*gr)/det))
            stationary.append(value-.5*(dr*gr+dz*gz))
            if i<2:
                y[32+2*i]=xt[2*i]-dr; y[33+2*i]=xt[2*i+1]-dz
        axis=stationary[2]
        boundary=max(stationary[:2]) if axis>(stationary[0]+stationary[1])*.5 else min(stationary[:2])
        target_phi=.995*boundary+.005*axis
        radial=v[32:64]*self.cos+v[64:96]*self.sin
        denom=np.where(radial<0,-np.maximum(np.abs(radial),.02),np.maximum(np.abs(radial),.02))
        y[:32]=rt-(v[:32]-target_phi)/denom
        y[36]=f[-1]
        return y
