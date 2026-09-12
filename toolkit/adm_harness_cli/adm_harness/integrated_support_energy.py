"""Dense support energy obtained from its counted local work history."""
import numpy as np
from numpy.polynomial import Polynomial
from numpy.polynomial.legendre import leggauss


class IntegratedEnergy:
    """Integrate a prescribed M_t with polynomial dense output inside each panel.

    Panels include every material and source interpolation knot. Four Gauss
    samples define a cubic derivative and its quartic energy primitive. The
    returned derivative is the derivative of that primitive, so an independent
    power audit can measure the remaining quadrature error directly.
    """
    def __init__(self,edges,initial,rhs,*,order=4):
        self.edges=np.asarray(edges)
        if np.any(np.diff(self.edges)<=0):raise ValueError('ordered integration panels required')
        z,w=leggauss(order);self.theta=(z+1)/2
        times=(self.edges[:-1,None]+np.diff(self.edges)[:,None]*self.theta).ravel()
        values=np.asarray(rhs(times))
        self.stages=values.reshape(len(self.edges)-1,order,*values.shape[1:])
        increments=np.einsum('ig...,g,i->i...',self.stages,w/2,np.diff(self.edges))
        self.values=np.asarray(initial)[None,...]+np.concatenate(
            [np.zeros_like(np.asarray(initial))[None,...],np.cumsum(increments,axis=0)],axis=0)
        self.polynomials=[];self.primitives=[]
        for i,node in enumerate(self.theta):
            others=np.delete(self.theta,i)
            polynomial=Polynomial.fromroots(others)/np.prod(node-others)
            primitive=polynomial.integ()
            self.polynomials.append(polynomial)
            self.primitives.append(primitive-primitive(0.))

    def evaluate(self,times):
        t=np.asarray(times);i=np.clip(np.searchsorted(self.edges,t,side='right')-1,0,len(self.edges)-2)
        dt=np.diff(self.edges)[i];theta=(t-self.edges[i])/dt
        primitives=np.array([p(theta) for p in self.primitives]).T
        basis=np.array([p(theta) for p in self.polynomials]).T
        extra=np.einsum('ig,ig...->i...',primitives,self.stages[i])
        energy=self.values[i]+extra*dt.reshape((-1,)+(1,)*(extra.ndim-1))
        derivative=np.einsum('ig,ig...->i...',basis,self.stages[i])
        return energy,derivative
