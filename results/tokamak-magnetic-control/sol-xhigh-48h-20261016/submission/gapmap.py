"""One affine map from boundary descriptors to fixed machine gap resources."""
import numpy as np
class GapMap:
 def __init__(self,path):
  d=np.load(path);self.points=d['points'];self.gaps=d['gap_points'];self.J=d['J_gap'];self.inverse=np.linalg.pinv((self.points[1:]-self.points[0]).reshape(-1,64).T);self.key=None
 def at(self,points):
  if self.key is None or not np.array_equal(points,self.key):
   w=self.inverse@(points-self.points[0]).ravel()
   self.result=(self.gaps[0]+np.einsum('i,ijk->jk',w,self.gaps[1:]-self.gaps[0]),self.J[0]+np.einsum('i,ijk->jk',w,self.J[1:]-self.J[0]))
   self.key=points.copy()
  return self.result
