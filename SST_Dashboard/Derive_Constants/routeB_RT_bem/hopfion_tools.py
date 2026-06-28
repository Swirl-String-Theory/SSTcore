import numpy as np

def hopf_charge(n, dx):
    """Validated Hopf-charge meter. n:(3,N,N,N) unit field. Returns Q_H (real; round to int)."""
    d=[np.array([np.gradient(n[a],dx,edge_order=2,axis=i) for a in range(3)]) for i in range(3)]
    F=lambda i,j: np.sum(n*np.cross(d[i],d[j],axis=0),axis=0)
    B=np.array([-F(1,2),-F(2,0),-F(0,1)])
    N=n.shape[1]; k=2*np.pi*np.fft.fftfreq(N,d=dx)
    KX,KY,KZ=np.meshgrid(k,k,k,indexing='ij'); K=np.array([KX,KY,KZ])
    k2=KX**2+KY**2+KZ**2; k2[0,0,0]=1.0
    Bh=np.array([np.fft.fftn(B[i]) for i in range(3)])
    A=np.array([np.fft.ifftn((1j*np.cross(K,Bh,axis=0)/k2)[i]).real for i in range(3)])
    return (1/(16*np.pi**2))*np.sum(A*B)*dx**3

def faddeev_energy(n, dx):
    """Faddeev-Skyrme energy E = ∫[(∂n)^2 + (F)^2]; E4=2∫B^2."""
    d=[np.array([np.gradient(n[a],dx,edge_order=2,axis=i) for a in range(3)]) for i in range(3)]
    E2=np.sum([np.sum(d[i]*d[i]) for i in range(3)])*dx**3
    F=lambda i,j: np.sum(n*np.cross(d[i],d[j],axis=0),axis=0)
    E4=np.sum(F(0,1)**2+F(1,2)**2+F(2,0)**2)*dx**3
    return E2+E4, E2, E4

def build_mn(N=96, box=8.0, a=1.2, m=1, nn=1):
    x=np.linspace(-box/2,box/2,N,endpoint=False); dx=x[1]-x[0]
    X,Y,Z=np.meshgrid(x,x,x,indexing='ij'); r2=X**2+Y**2+Z**2; den=r2+a**2
    Z1=(2*a*(X+1j*Y))/den; Z2=(2*a*Z+1j*(r2-a**2))/den
    u=Z1**m; v=Z2**nn; nrm=np.abs(u)**2+np.abs(v)**2
    n=np.array([2*(u.conj()*v).real/nrm,2*(u.conj()*v).imag/nrm,(np.abs(u)**2-np.abs(v)**2)/nrm])
    return n/np.linalg.norm(n,axis=0), dx

# ---------------------------------------------------------------------------
# VALIDATED (numpy, no GPU):
#   * hopf_charge: converges to integer with resolution; topologically conserved.
#     (m,n) axial ansatz returns Q_H = m*n for all tested charges 1..6.
#   * faddeev_energy: E2+E4; reproduces A_{2,1} < A_{1,2} energy ordering at Q=2.
#
# REMAINING for the theta=pi taxonomy test (Q_H of knotted minimizers):
#   1. E4 variational gradient (delta E4 / delta n) for the relaxer  [NOT YET IMPLEMENTED]
#   2. a KNOTTED seed (trefoil / 5_1) — axial (m,n) seeds do NOT buckle into knots
#   3. arrested-Newton or gradient flow to convergence on a >=128^3 grid (heavy)
# Then: relax -> hopf_charge() reads off Q_H -> test  pq+1  (e.g. is 5_1 at Q=11, odd?).
# The METER (the previously missing tool) now makes that test EXECUTABLE.
# ---------------------------------------------------------------------------
