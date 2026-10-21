"""NumPy controller with an auditable bundled C99 arithmetic kernel."""
import ctypes
import json
from pathlib import Path
import sys
import numpy as np
import core
HERE=Path(__file__).resolve().parent
F=ctypes.POINTER(ctypes.c_float);D=ctypes.POINTER(ctypes.c_double)

class Controller(core.Controller):
    def __init__(self):
        super().__init__()
        if len(self.est.mu_y)!=33:raise ValueError('kernel requires the checkpoint\'s 32 flux modes')
        self.obsbuf=np.zeros(585,np.float32);self.wbuf=np.zeros((33,512),np.float32);self.biasbuf=np.zeros(33,np.float32);self.cachebuf=np.zeros((86,33),np.float32)
        self.kbuf=np.zeros((4,11,38),np.float64);self.geombuf=np.zeros(2,np.float64);self.statebuf=np.zeros(16,np.float64);self.outbuf=np.zeros(12,np.float64)
        p=self.p
        pars=np.array([.0005,max(1,p['ramp']),p['k_shape'],p['k_zt'],p['k_ip'],p['ki_ip'],p['tau_c'],p['dmax'],p['e_clip'],p['x_gate'],p['kz_p'],p['kz_d'],p['kz_i'],self.est.ip0,p.get('ramp_ip',1)])
        self.machinebuf=np.r_[self.Rc,self.Lc.ravel(),self.lo,self.hi,-self.vmax,self.vmax,pars].astype(np.float64)
        self.library=ctypes.CDLL(str(HERE/'control_kernel.so'));self.kernel=self.library.control_step
        self.kernel.argtypes=[F,F,F,F,D,D,D,D,D];self.kernel.restype=None
        self.geometry_kernel=self.library.geometry_cache
        self.geometry_kernel.argtypes=[ctypes.c_int,D,D,D,D,F];self.geometry_kernel.restype=None
        self.geometry_grid=np.ascontiguousarray(self.est.grid,dtype=np.float64)
        self.geometry_spline=np.ascontiguousarray(self.est.spline,dtype=np.float64)
        self.geometry_out=np.empty((118,len(self.geometry_grid)),np.float32)
        self.gap_kernel=self.library.gap_cache
        self.gap_kernel.argtypes=[ctypes.c_int,D,D,F];self.gap_kernel.restype=None
        self.est.cache=self._native_cache
        arrays=[self.obsbuf,self.wbuf,self.biasbuf,self.cachebuf,self.kbuf,self.geombuf,self.machinebuf,self.statebuf,self.outbuf]
        self.args=tuple(arr.ctypes.data_as(F if i<4 else D) for i,arr in enumerate(arrays))
    def _native_cache(self,points,xpoints):
        pts=np.ascontiguousarray(points,dtype=np.float64)
        critical=np.ascontiguousarray(np.vstack([xpoints,[[.95,float(np.median(points[:,1]))]]]),dtype=np.float64)
        theta=np.arctan2(points[:,1],points[:,0]-.95)
        self.est.cos=np.cos(theta);self.est.sin=np.sin(theta)
        self.geometry_kernel(len(self.geometry_grid),self.geometry_grid.ctypes.data_as(D),self.geometry_spline.ctypes.data_as(D),pts.ctypes.data_as(D),critical.ctypes.data_as(D),self.geometry_out.ctypes.data_as(F))
        gaps=np.ascontiguousarray(self.gap_points,dtype=np.float64)
        self.gap_kernel(len(self.geometry_grid),self.geometry_spline.ctypes.data_as(D),gaps.ctypes.data_as(D),self.geometry_out[114:].ctypes.data_as(F))
        return self.geometry_out
    def reset(self,low,high):
        super().reset(low,high);self.statebuf.fill(0);self.initialized=False
        self.machinebuf[154:166]=low;self.machinebuf[166:178]=high
    def act(self,observation):
        obs=self.obsbuf;obs[:]=observation;t=obs[513:584]
        if self.tkey is None or not np.array_equal(t[:71],self.tkey):
            self._targets(obs,t);self.tkey=t[:71].copy();f=self.field_cache
            self.cachebuf[:]=np.vstack([f[:32],f[32:64]*self.est.cos[:,None]+f[64:96]*self.est.sin[:,None],f[96:]])
            self.kbuf[:]=np.stack([self._operator(bool(i&1),bool(i&2)) for i in range(4)])
            self.geombuf[:]=[self.dz_dI6,self.nx]
            if not self.initialized:
                self.wbuf.fill(0);self.wbuf[:,self.est.keep]=self.est.raw_W.T;self.biasbuf[:]=self.est.bias
                self.statebuf[:11]=obs[500:511];self.statebuf[12]=self.z_t;self.initialized=True
        self.kernel(*self.args)
        return self.outbuf.copy()

def main():
    c=Controller()
    for line in sys.stdin:
        req=json.loads(line);reply={'request_id':req['request_id']}
        if req.get('protocol')!='tokamak-policy/v1':raise SystemExit('unsupported protocol')
        if req['op']=='reset':c.reset(req['action_low'],req['action_high']);reply['ready']=True
        elif req['op']=='act':reply['action']=c.act(req['observation']).tolist()
        elif req['op']=='close':reply['closed']=True;print(json.dumps(reply),flush=True);return
        print(json.dumps(reply),flush=True)
if __name__=='__main__':main()
