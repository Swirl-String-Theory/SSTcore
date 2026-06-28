import math
L = 16.371637
aobs = 137.0359992          # alpha^-1 observed
A = (8*math.pi/3)*L         # leading
print(f"A = (8pi/3)L                = {A:.7f}")
print(f"leading gap                 = {A-aobs:+.7f}")
print(f"leading gap [ppm]           = {(A-aobs)/aobs*1e6:.2f}  (doc: 866.24)")
# required c2 for EXACT closure
c2_req = L*L*(1 - aobs/A)
print(f"c2_req                      = {c2_req:.10f}  (doc: 0.2319781083)")
print(f"c2(11/48)                   = {11/48:.10f}")
print(f"Delta c2                    = {c2_req-11/48:.10f}  (doc: 0.0028114416)")
print(f"Delta c2 / (11/48) [%]      = {(c2_req-11/48)/(11/48)*100:.3f}  (doc: 1.23%)")
# alpha from 11/48
a_1148 = A*(1-(11/48)/L**2)
print(f"alpha^-1 at 11/48           = {a_1148:.7f}  (doc: 137.0374378)")
print(f"  residual [ppm]            = {(a_1148-aobs)/aobs*1e6:.2f}  (doc: 10.50)")
# required sigma, w_perp (chi_R=2 fixed)
sig_req = 16*c2_req
w_req = 1.5*(sig_req-3)
print(f"sigma_req                   = {sig_req:.9f}  (doc: 3.711649733)")
print(f"w_perp_req (NOT 1!)         = {w_req:.7f}  (doc: 1.0674746)")
# proxy
wp=2.075916167; sigp=3+(2/3)*wp; c2p=sigp/16; ap=A*(1-c2p/L**2)
print(f"proxy w_perp=2.0759 -> a^-1 = {ap:.7f}  -> [ppm]={(ap-aobs)/aobs*1e6:.1f}  (doc: -156.9, wrong side)")
# Route B chi_R
chiB=math.sqrt((11/3)/(4*c2_req)); print(f"Route B chi_R               = {chiB:.7f}  ({(chiB-2)/2*100:.4f}%)")
# Route C V_sector  (A = (1/2) N_p V_sector L ; N_p=4 -> A=2 V L ; V=A/(2L))
# exact: need A_eff=2 a c... actually V_req from matching residual:
V_now=4*math.pi/3
# A scales linearly with V_sector (since 16pi/3 = N_p*4pi/3, A=(8pi/3)L=(1/2)*4*Vnow*L/... ) check:
# A = (8pi/3)L and 8pi/3 = 2*(4pi/3) -> A = 2*V_now*L? 2*4.18879*16.3716=137.15 yes
V_req = aobs/( (1-(c2_req)/L**2) * 2*L )  # keep shell at c2_req? -> instead: residual route at fixed 11/48
# simpler: V_req so that A_eff*(1-11/48/L^2)=aobs ; A_eff=2 V_req L
Aeff_req = aobs/(1-(11/48)/L**2)
V_req = Aeff_req/(2*L)
print(f"Route C V_sector_req        = {V_req:.10f}  vs 4pi/3={V_now:.10f}  [ppm]={(V_req-V_now)/V_now*1e6:.3f}")
# Route D ropelength
# need A_eff*(1-11/48/Lr^2)=aobs with A_eff=(8pi/3)Lr  -> solve numerically
from scipy.optimize import brentq
f=lambda Lr:(8*math.pi/3)*Lr*(1-(11/48)/Lr**2)-aobs
Lr=brentq(f,16.0,16.7)
print(f"Route D ropelength_req      = {Lr:.10f}  vs {L}  [ppm]={(Lr-L)/L*1e6:.2f}")
# sensitivities
dadc2=-A/L**2
print(f"d(a^-1)/d c2                = {dadc2:.6f}  (doc: -0.511713)")
print(f"|Dc2| for 1ppm              < {1.37036e-4/abs(dadc2):.3e}  (doc 2.68e-4)")
print(f"|DL| for 1ppm               < {1.37036e-4/(8*math.pi/3):.3e}  (doc 1.63e-5)")
