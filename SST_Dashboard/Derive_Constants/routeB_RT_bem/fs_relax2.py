import numpy as np
def deriv(f,i,dx): return (np.roll(f,-1,i)-np.roll(f,1,i))/(2*dx)
def adj(g,i,dx):   return (np.roll(g,1,i)-np.roll(g,-1,i))/(2*dx)

def components_eg(n, dx):
    """Return E2,g2 (sigma) and E4,g4 (Faddeev) separately. Raw grads (pre-sphere-projection)."""
    D=[np.array([deriv(n[a],i,dx) for a in range(3)]) for i in range(3)]
    cross=[[np.cross(D[i],D[j],axis=0) for j in range(3)] for i in range(3)]
    F=[[np.sum(n*cross[i][j],axis=0) for j in range(3)] for i in range(3)]
    E2=sum(np.sum(D[i]*D[i]) for i in range(3))
    E4=sum(np.sum(F[i][j]**2) for i in range(3) for j in range(3))
    g2=np.zeros_like(n); g4=np.zeros_like(n); gD=[np.zeros_like(n) for _ in range(3)]
    for i in range(3):                                  # E2 grad via adjoint of -2∇²
        for a in range(3): g2[a]+=adj(2*D[i][a],i,dx)
    gD4=[np.zeros_like(n) for _ in range(3)]
    for i in range(3):
        for j in range(3):
            dF=2*F[i][j]
            g4 += dF*cross[i][j]
            gD4[i]+= dF*np.cross(D[j],n,axis=0); gD4[j]+= dF*np.cross(n,D[i],axis=0)
    for i in range(3):
        for a in range(3): g4[a]+=adj(gD4[i][a],i,dx)
    return E2,g2,E4,g4

def proj_sphere(g,n): return g-np.sum(g*n,axis=0)*n

def relax_fixedE2(n,dx,steps,delta=0.02,E2_target=None,feedback=0.3,report=40,charge_fn=None):
    """Minimise E4 (shape) while pinning E2 (scale) -> prevents lattice collapse, conserves Q_H."""
    E2,_,_,_=components_eg(n,dx)
    if E2_target is None: E2_target=E2
    for s in range(steps+1):
        E2,g2,E4,g4=components_eg(n,dx)
        g2p=proj_sphere(g2,n); g4p=proj_sphere(g4,n)
        # project E4-gradient tangent to the E2=const surface
        denom=np.sum(g2p*g2p)+1e-12
        gc=g4p-(np.sum(g4p*g2p)/denom)*g2p
        # gentle feedback to hold E2 at target (correct discretisation drift)
        gc=gc+feedback*((E2-E2_target)/E2_target)*g2p
        gmax=np.max(np.sqrt(np.sum(gc**2,axis=0)))+1e-12
        if s%report==0:
            q=charge_fn(n,dx) if charge_fn else float('nan')
            print(f"   step {s:4d}  E2={E2*dx**3:8.2f} (tgt {E2_target*dx**3:7.2f})  E4={E4*dx**3:8.2f}  Q_H={q:+.3f}")
        n=n-(delta/gmax)*gc; n=n/np.linalg.norm(n,axis=0)
    return n
