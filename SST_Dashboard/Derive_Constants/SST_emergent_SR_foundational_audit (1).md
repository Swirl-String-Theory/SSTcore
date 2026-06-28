# SST Foundational-Layer Audit: Does the Substrate Yield Emergent Special Relativity?

**Scope.** Consolidates the reasoning chain on whether SST's substrate dynamics produce
emergent special relativity (a single universal `c`, exact `γ` for the swirl clock) and
whether the photon and matter sectors can be made consistent with Lorentz-invariance (LV)
bounds. This is the layer *logically prior* to Papers I–IV (α, mass, EM): if it fails,
calling `α_cell` "the fine-structure constant" loses the Minkowski/lightcone structure it
presupposes.

**Date:** 2026-06-23  **Status:** working audit, not a canon patch.

**Label legend.**
`[ORTHODOX]` established physics/math · `[DERIVED]` follows from stated SST assumptions ·
`[DERIVED NEGATIVE]` a route is *closed* by explicit argument · `[OPEN]` not yet settled ·
`[RETRACTED]` a claim I previously made and now withdraw · `[DECISION]` an ontological
choice with a price, not a calculation · `[UNBUILT]` requires constructing new structure
the corpus has not specified.

---

## 0. Dependency spine

```
v_↺ tangential (not causal)            [DERIVED, prior turns]
        │
§1  Boost algebra: Galilei vs Poincaré  ── İnönü–Wigner axis
        │   (three branches; Tak II = branch 2 chosen)        [DECISION]
        │
§2  Tak II ⇒ c_s = c ⇒ ξ = ℏ/(m_eff c) ⇒ E_LV = m_eff c²
        │   n=2 dispersion bound ⇒ ξ ≠ r_c forced            [DERIVED]
        │
§3  Photon as protected transverse mode
        │   σ-decoupling [DERIVED] · F□F survives [OPEN]
        │   birefringence self-undermining claim             [RETRACTED]
        │
§4  Volovik route: photon = emergent U(1) at nodal points
        │   M_* decouples from r_c                             [DERIVED — the real win]
        │
§5  Gate A (leading isotropy) before Gate C (a_γ)
        │   cube = 2-design ✔ dim-4 · dim-6 survives          [DERIVED]
        │   matter isotropy = the binding gate                [DERIVED]
        │
§6  Electron = trefoil knot-soliton
        │   static trefoil anisotropic [DERIVED NEGATIVE]
        │   O-orientational delocalization isotropizes        [DERIVED, conditional]
        │   L_K orientation-invariant ⇒ α-program survives    [RETRACTED prior claim]
        │
§7  Foundational target space                                 [OPEN / UNBUILT]
            + metric locking c_e = c_γ                        [OPEN, load-bearing]
```

---

## 1. Boost algebra — the Galilei/Poincaré diagnostic

The structure constants of `[K_i,K_j]` and `[K_i,P_j]` decide everything; they are read off
without assuming `γ`.

- **Candidate A — incompressible Euler / non-relativistic GP.** Boost generator
  `K_i^G = m∫x_i|ψ|² − tP_i`; `[K_i^G,K_j^G]=0`, `[K_i^G,P_j]=iℏMδ_ij`. **Galilei (Bargmann)**,
  mass as central charge. A moving vortex is a *different* solution, not a `1/γ`-contracted
  rest state → no `γ`. `[DERIVED]`
- **Candidate B — relativistic GP (□ in the action).** `[K_i^L,K_j^L]=−(i/c²)ε_ijk J_k`,
  `[K_i^L,P_j]=(i/c²)δ_ij H`. **Poincaré**; Nielsen–Olesen strings contract by `γ`. `[DERIVED]`
- **İnönü–Wigner.** Galilei is the `c→∞` contraction of Poincaré. Strict incompressibility
  *is* `c_s→∞` in the pressure sector, so incompressibility forces the Galilei contraction.
  `[ORTHODOX]`

**Three-branch verdict** `[DERIVED]`:
1. Strict incompressible → pure Galilei, no SR for anything → falsified as a theory of
   relativistic matter.
2. Non-relativistic GP (finite `c_s`, Schrödinger time-derivative) → fundamental substrate is
   Galilei; only the linearized phonon sector carries *approximate* Poincaré(`c_s`) at low `k`
   via the acoustic metric. Vortices stay Galilean; phonons are approximately Lorentz. This is
   the Volovik situation; SST-23 dual-vacuum is its phenomenology.
3. Relativistic GP → exact Poincaré, but "incompressible fluid" is gone.

No fourth option: İnönü–Wigner forbids a Galilean fluid substrate *and* exact-Lorentz matter
simultaneously. You cannot have both (a) absolute Euclidean 3D+t and (b) exact emergent SR for
matter. **Tak II = branch 2 chosen.** `[DECISION]`

*Numerically verified:* explicit generators and commutators for both algebras.

---

## 2. LV dispersion scale and the healing length

- Tak II requires the emergent signal speed = light speed, `c_s = c`. With
  `ξ = ℏ/(m_eff c_s)`, this gives `E_LV = ℏc/ξ = m_eff c²`: **the LV scale is the rest energy
  of the condensate quantum.** `[DERIVED]`
- Bogoliubov dispersion `ω² = c²k²(1+(kξ/2)²)` is **quadratic (n=2)**. The binding constraint
  is the n=2 photon time-of-flight bound, `E_LV ≳ 10¹⁰–10¹¹ GeV`, *not* the linear (n=1) bound.
  `[DERIVED]`
- `ξ = r_c` → `E_LV = 140 MeV` → excluded by ~11 orders (a 10 GeV photon sits ~70× above the
  scale). `ξ = 10⁻³ r_c` (140 GeV) still excluded by ~8 orders. **Safety requires
  `ξ ≲ 10⁻¹¹ r_c`, i.e. `m_eff ≳ 10¹⁰ GeV`** (full safety ~`m_Planck`). `[DERIVED / FALSIFIED for ξ=r_c]`
- **Ontology consequence:** the swirl/Compton/`r_c` sector is IR-emergent ~11–20 orders below
  the medium scale (analog-gravity-like). The medium is *not* the fm-scale object the papers
  describe; `r_c` is a defect scale, not the substrate scale. `[DERIVED]`

**Self-corrections (turn 14):**
- The Bogoliubov sign is **superluminal** (`v_g = c(1+(3/8)(kξ)²)`): high-energy photons arrive
  *early*. Definite sign ⇒ falsifiable. `[DERIVED]`
- My earlier worry of a naive `(v_lab/c)² ~ 10⁻⁶` frame anisotropy was **overstated**: the
  leading acoustic metric is exactly Lorentzian (uniform flow is Painlevé–Gullstrand, removable),
  so anisotropy lives only in the dispersive `(kξ)²` sector. The GRB dispersion bound binds, not
  the optical resonator bound. `[RETRACTED overstatement]`

*Numerically verified:* `E_LV`, `m_eff`, and dispersion at 10 GeV across the `ξ` cases.

---

## 3. Photon as a protected transverse mode (the ξ~r_c escape attempt)

- **σ-sector decoupling.** A strictly transverse mode (`k·A_T = 0`) in an isotropic,
  parity-even condensate does **not** inherit the longitudinal `(kξ)²` healing term; the
  quadratic propagator is block-diagonal. `[DERIVED, under isotropy + no density mixing]`
- **But F□F is not thereby forbidden.** The parity-even operator `F_{μν}□F^{μν}` is allowed by
  every symmetry except exact LI. Bianchi `dF=0` is *kinematic* and does not constrain the
  dynamical action. At `ξ~r_c` it needs `a_γ ≲ 10⁻²⁴` (a symmetry zero). Forbidding it = exact
  LI = Tak III. `[DERIVED NEGATIVE for Bianchi/Kelvin-closure as the protection]`
- **Birefringence sub-thread.** `h = v·ω` is a pseudoscalar; `⟨h⟩≠0 ⟺ θE·B birefringence`.
  I claimed "torsion ⇒ `⟨h⟩≠0` ⇒ self-undermining."
  **`[RETRACTED]`** — a mode *carrying* helicity is not a vacuum *carrying* helicity. A
  parity-even vacuum (`⟨h⟩=0`) supports degenerate helicity eigenmodes; the Maxwell photon is
  the existence proof (individual photons are helical, the vacuum is not optically active).
  Torsion is therefore **not** automatically birefringent.

**Net:** `ξ~r_c` survives only if `a_γ = 0` by emergent-LI / fixed-point protection; the
parity-even dispersion operator, not birefringence, is the live obstruction. `[OPEN]`

*Numerically verified:* parity-even (`a_γ`) vs parity-odd (`b_γ`) coefficient suppression at
`ξ=r_c`, and the parity assignment `v` (polar), `ω` (axial), `h` (pseudoscalar).

---

## 4. Volovik route — the genuine win

- Photon = emergent `U(1)` gauge mode near nodal/Fermi points, **not** the raw `l̂`-Goldstone
  (which would be a material wave with multi-speed dispersion). `[DECISION, correct]`
- The photon's UV cutoff becomes `M_*` (the nodal linearity scale), **decoupled from `r_c`**.
  This escapes the 140 MeV death: the dispersion gate becomes `M_*c²/√a_γ ≳ 10¹⁰–10¹¹ GeV`,
  not `ℏc/r_c ≳ …`. `[DERIVED — this is why the route lives]`
- `a_γ` is no longer a free EFT coefficient but a *calculable* deviation from Fermi-point
  linearity. `[REFRAME]`

---

## 5. Gate A (leading isotropy) precedes Gate C (a_γ)

- **³He-A is rejected as a final vacuum.** Two Weyl nodes on one `l̂`-axis give leading
  (dim-4) anisotropy `c_∥/c_⊥ ~ 10³`. `[DERIVED NEGATIVE for two-node uniaxial]`
- **Spherical 2-design condition.** Isotropic leading photon metric ⟺
  `Σ_a w_a n_a^i n_a^j = (W/3)δ^{ij}`. The 8-node cube satisfies it (`Σ = (8/3)δ`). `[DERIVED]`
- **Cube is a 3-design, not a 4-design.** dim-6 (`k⁴`) cubic anisotropy survives
  (cubic-anisotropy `= −0.222`). Killing it needs the **icosahedron** (5-design,
  cubic-anisotropy `= 0`). `[DERIVED]`
- **Gate ordering corrected:** Gate A (isotropy) before Gate C (`a_γ`). `a_γ` is not the first
  gate. `[DERIVED]`
- **Hidden condition:** a *single democratic* `U(1)` coupling equally to all nodes (else
  multiple emergent gauge fields, not one photon). `[OPEN]`
- **The binding gate is matter isotropy, not `a_γ`.** The photon averages over nodes (vacuum
  polarization sum); a single-node Weyl *fermion* lives at one node and sees that node's
  anisotropic cone. Matter-sector rotation/LV is bounded ~`10⁻²⁹–10⁻³³` — tighter than the
  photon. Node-locking to isotropize fermions → Nielsen–Ninomiya gaps them; RG-isotropization
  is non-generic and fails in ³He-A. `[DERIVED — matter isotropy binds]`

*Numerically verified:* 2nd- and 4th-moment tensors for tetra/octa/cube/icosa node sets.

---

## 6. Electron = trefoil knot-soliton

- **Escape:** the electron is a knot-soliton sampling the node set, not a single-node Weyl
  fermion. Preserves the corpus identity (matter = knot). `[DECISION, SST-consistent]`

**Self-corrections (turn 18) — both withdrawals of my own prior overclaims:**
- **`L_K` is orientation-invariant.** Ropelength is a property of the knot *type*, not its
  spatial orientation. Orientational delocalization does **not** blur `L_K`, so the α-program
  (`α⁻¹ ≈ (8π/3)·L_K`) survives delocalization. `[RETRACTED: "delocalization kills sharp L_K"]`
- Consequently the "**irreconcilable fork** between isotropy and the chiral-knot taxonomy" was
  too strong. They reconcile. `[RETRACTED]`

**Mechanism correction (against the "3D sampling" intuition):**
- The *static* trefoil is **anisotropic**: gyration tensor eigenvalues `0.28 / 1.36 / 1.36`,
  anisotropy ratio ~4.9. A wiggly 3D curve is not isotropic; it has a C₃ axis. Symmetry of the
  effective metric = symmetry of the configuration = C₃/D₃ → uniaxial. Only O/I/SO(3) force
  rank-2 isotropy. `[DERIVED NEGATIVE for static-trefoil isotropy]`
- **Working mechanism:** quantum orientational delocalization over the chiral cubic group `O`.
  The `O`-average of the uniaxial tensor is exactly isotropic (eigenvalues → `1,1,1`).
  Averaging over proper rotations preserves chirality (`e⁻` stays `e⁻`) and `L_K`. `[DERIVED, conditional]`
- If the node-lattice `O` symmetry is **exact**, the electron ground state (symmetric
  orientational superposition) is exactly `O`-invariant → **exactly** isotropic at rank-2, no
  tuning. The binding question reduces to: *is the node point-group symmetry exact?* `[DERIVED]`

*Numerically verified:* trefoil gyration tensor; `O`-orientation-average → isotropic.

---

## 7. Foundational target space + metric locking

- **The target space must carry four structures at once** `[OPEN / UNBUILT]`:
  (i) a *fermionic* paired vacuum (Weyl nodes need a Bloch/Dirac Hamiltonian);
  (ii) 12 chirality-balanced Weyl nodes in icosahedral arrangement (photon dim-6 isotropy +
  Nielsen–Ninomiya `Σχ_a=0`);
  (iii) `π_3 ≠ 0` supporting trefoil solitons (the electron);
  (iv) a single emergent `U(1)`.
  A single `l̂` (³He-A) gives 2 nodes, not 12. No known order parameter satisfies all four; it
  must be constructed.
- **Crystallographic obstruction** `[DERIVED NEGATIVE for icosahedral crystal]`: the icosahedron
  (needed for dim-6 isotropy) requires 5-fold axes, forbidden in any periodic lattice
  (rotation trace `1+φ` is irrational; only 1,2,3,4,6-fold are lattice-compatible). So
  icosahedral isotropy needs a continuous / quasicrystalline medium, where the Weyl-node /
  Bloch machinery that produced the nodes is not well-defined. A cubic crystal is allowed but
  retains dim-6 anisotropy.
- **Metric locking `c_e = c_γ`** `[OPEN, load-bearing]`: point-group symmetry forces each
  stiffness isotropic but does *not* relate their magnitudes. `c_γ` ~ Weyl-cone velocity,
  `c_e` ~ soliton order-parameter stiffness — distinct sectors, unequal in ³He-A. Equality
  needs an emergent-Lorentz RG fixed point (strong coupling), which ³He-A does not have.
  **Irony:** if the fixed point is assumed, it isotropizes everything anyway, making the node
  engineering partly redundant; if not assumed, metric locking fails. The real heavy lifting is
  the unproven RG assumption — i.e. "assume the IR flows to exact Lorentz invariance."
- **Predictivity** `[OPEN]`: the stacked structure (fermionic vacuum + icosahedral nodes +
  `π_3` solitons + single `U(1)` + RG fixed point) risks unfalsifiability. The distinctive
  predictions left are generic emergent-LV signatures (dim-6 anisotropy if cubic, `M_*`
  dispersion, CMB preferred frame). A *uniquely* SST prediction beyond emergent SM/GR is not
  yet identified.

*Numerically verified:* crystallographic restriction (lattice-compatible rotation orders);
lowest cubic/icosahedral harmonics (l=4, l=6).

---

## 8. CP¹/Hopfion resolution of the target-space gate (bosonic redirect)

The §5–§7 difficulties are artifacts of the **fermionic** (momentum-space nodal) realization.
A **bosonic** target space dissolves them. Primary candidate:

```
M_SST = S² ≃ CP¹       [PRIMARY CANON TARGET]
```

the order parameter is a unit director field `n(x,t) ∈ S²` (a superfluid-liquid-crystal:
flows, plus an internal "compass needle" per point).

**Electron = trefoil Hopfion.** Classified by `π₃(S²) = ℤ` (the Hopf charge `Q_H`). The closed
swirl-string is the **preimage loop** `n⁻¹(p) ⊂ ℝ³`; that it is a 1D curve is dimension counting
`3 − 2 = 1`, **not** `π₂`. (`π₂(S²)=ℤ` is the monopole/point-defect charge — the flux of the
emergent gauge field — not the knot.) `[CORRECTION of turns 21/23: π₃ not π₂]`

- The trefoil is **not** a minimal Hopfion: `Q_H = 1,2` are unknots; the trefoil is the
  minimal-energy configuration near `Q_H ≈ 7` (Hietarinta–Salo, Battye–Sutcliffe). So `e⁻` is a
  `Q_H ≈ 7` knot — a specific structural claim that fits a knot-taxonomy (successive particles =
  minimal knots at successive Hopf charges). The bound `E ≳ Q_H^{3/4}` keeps it stable against
  fission. `[RESEARCH-TRACK]`
- **Stability is not free:** Derrick's theorem kills solitons in the pure 2-derivative S² model;
  the **Faddeev–Skyrme quartic term** `(∂n × ∂n)²` is mandatory. The medium is a
  Faddeev–Skyrme medium, not a generic superfluid. `[ORTHODOX constraint]`

**What this buys (the genuine win):** continuous `SO(3)` of the S² model forces rank-2 isotropy
**automatically** — no node lattice, no spherical designs, no Nielsen–Ninomiya, no cube-vs-
icosahedron, no trefoil-vs-node competition. **§5–§7 move to research-track.** `[DERIVED]`

**R2 (emergent photon) — downgraded:** the CP¹ connection `a_μ = −i z†∂_μ z` is a *composite*
field. A free, gapless, spin-1 Maxwell photon requires a **deconfined U(1)/Coulomb phase**
(quantum spin ice; Hermele–Fisher–Balents). `[CONDITIONAL, not SATISFIED — correction]`

**The binding gate — phase coexistence, and it leans negative.** In CP¹:
```
n ordered (Hopfion needs ordered background)  ⟺  z condensed  ⟺  a_μ HIGGSED  ⟹  no gapless photon
gapless Coulomb photon                        ⟺  z uncondensed (n disordered) ⟹  no stable Hopfion
```
The Hopfion and the deconfined photon sit in **mutually exclusive phases** of the same field.
This is not a neutral "open" — it is a near **no-go in the minimal single-field CP¹**. Escape
requires a *multi-field* construction (one field orders for the knots, another stays deconfined
for the photon), which is unbuilt and forfeits the simplicity that motivated CP¹.
`[OPEN, leaning NEGATIVE in minimal CP¹]`

**Unchanged by the redirect:** Tak II / approximate emergent SR (§1); the LV gate
`M_* ≳ 10¹⁰–10¹¹ GeV` (§2); metric locking `c_e = c_γ` `[OPEN, HARD, target-independent]` —
the Hopfion speed (n-sector stiffness) and photon speed (emergent-U(1) sector) are not forced
equal by any symmetry.

**Status block (§8):**
- `M_SST = S² ≃ CP¹` — `[PRIMARY CANON TARGET]`
- trefoil-Hopfion electron, `π₃(S²)=ℤ`, `Q_H≈7` — `[SATISFIED at topology level]`
- swirl-string = Hopfion preimage loop — `[CANON REINTERPRETATION]`
- automatic rank-2 isotropy from continuous SO(3) — `[SATISFIED if continuum SO(3) exact]`
- Faddeev–Skyrme term mandatory (Derrick) — `[ORTHODOX constraint]`
- emergent photon — `[CONDITIONAL: deconfined Coulomb phase]`
- **phase coexistence (photon ↔ Hopfion)** — `[OPEN, CENTRAL, leaning NEGATIVE]`
- metric locking `c_e = c_γ` — `[OPEN, HARD]`
- fermionic Volovik node-stack (§5–§7) — `[DEMOTED to research-track]`

### 8.1 Two-sector refinement (the Higgsing obstruction)

Minimal one-field CP¹ is insufficient: if the same charged spinor `z` both orders the Hopfion
background and carries `U(1)_γ` charge, then `⟨z⟩≠0` **Higgses the photon** (Anderson–Higgs /
Meissner). So the visible photon cannot be coupled by naïve minimal coupling to the condensing
Hopfion field. Surviving structure:

```
neutral Faddeev–Skyrme/CP¹ Hopfion matter sector
   +  separate deconfined U(1)_γ photon sector
   +  topological electric-charge assignment (NOT a charged condensate)
```

The electron's electric charge must therefore come from **topology**, not from a charged
condensate. New gate:

**Topological Charge Coupling Gate.** Construct a conserved, gauge-invariant, quantized current
`J^μ_topo` for the Hopfion such that `S_int = q ∫ A_μ J^μ_topo` gives charge `−e` while leaving
`U(1)_γ` deconfined and massless. The electric index is *not* assumed to be `Q_H`:
`Q_elec = q · I_charge`, where `I_charge` may be Hopf charge, linking, writhe/twist, or another
index — the mapping `Q_H≈7 ↦ −1` must be derived, not posited.

Refined status:
- Hopfion stability (Faddeev–Skyrme term) — `[SATISFIED]`
- deconfined `U(1)_γ` in 3+1D (monopoles gapped) — `[SATISFIED]`
- no photon Higgsing — `[CONDITIONAL on neutral condensate]`
- electric charge from topology — `[OPEN — next gate]`
- cosmological birefringence from matter asymmetry — `[SPECULATIVE — only if charge tracks a parity index]`
- metric locking `c_e = c_γ` — `[OPEN, HARD]`

### 8.2 Topological charge result and the spinon redefinition

**Charge-from-Hopf fails.** The Hopf invariant is a Chern–Simons-type global quantity; its
local density `K^μ ~ ε^{μνρσ}a_ν f_ρσ` shifts by a total derivative under `a→a+∂χ`, so the
*integral* `Q_H` is invariant but the *density* is gauge-variant — `A_μ K^μ` is not a legal
gauge-invariant Maxwell source. `[DERIVED NEGATIVE]`
The only local gauge-invariant topological current of `S²/CP¹` is the flux 2-form (the `π₂`
monopole charge); a Hopfion has **zero net monopole charge**. `[DERIVED NEGATIVE for Hopfion]`
Deep reason: `S²` gives knots but a non-local (CS) charge; `S³` gives a local gauge-invariant
charge (Skyrme baryon current) but lumps, not knots. **Knot and local-topological-charge are
mutually exclusive for the simple targets.** `[DERIVED]`

**Surviving electron picture (no longer a pure charged Hopfion):**
```
e⁻ = H⁰_{3₁}  ⊗  s⁻
     neutral trefoil-Hopfion (knot identity, mass, chirality, L_K)
     ⊗ charged spinon of the deconfined U(1)_γ sector (carries −e)
```

**Gates added (this refinement):**
- charge from topology (`A_μ K^μ_Hopf`, `A_μ J^μ_{π₂}`) — `[DERIVED NEGATIVE]`
- `e⁻ = H⁰_{3₁} ⊗ s⁻` — `[OPEN, surviving route]`
- one spinon per Hopfion — `[OPEN, NEXT GATE; tension: index ∝ Q_H≈7 ⇒ −7e]`
- spin/statistics (`J=½`, Fermi) — `[OPEN, LOAD-BEARING; spinon-carries vs knot-carries fork]`
- compositeness (pointlike ≲10⁻¹⁹ m; spinon not free at low E) — `[OPEN, LOAD-BEARING; tension with r_c~fm]`
- charge vs α-program: charge wants `Q_H=1` (unknot); α wants trefoil (`Q_H≈7`) — `[OPEN, cross-corpus tension]`
- cosmological birefringence — `[downgraded; vanishes in the spinon route]`
- `c_e = c_γ` — `[OPEN, HARD]`

### 8.3 Reinterpretation of r_c: circulation radius, not tube radius

`r_c = ‖v_↺‖/ω_C` rearranges to `‖v_↺‖ = ω_C r_c`: **r_c is a circulation radius** — the radius at
which the tangential swirl speed equals `‖v_↺‖` at the Compton angular frequency. Read it as a
horn-torus / return-flow radius, **not** the physical tube radius or the EM charge radius.
Notation (make explicit in canon): with the *reduced* Compton wavelength `λ̄_C = ℏ/(m_e c)`,
`r_c = (α/2) λ̄_C`; with the *ordinary* `λ_C = h/(m_e c)`, `r_c = (α/4π) λ_C`. `[WELL-FOUNDED]`

- α-program is **decoupled**: it uses the dimensionless ideal ropelength `L_{3₁}`, not the
  physical `r_c`. Do **not** set `a_rope = r_c` (that would change the tightness condition and
  break `L_{3₁}=16.37`). The reinterpretation neither saves nor damages α. `[α UNAFFECTED]`

**Magnetic moment (corrects the prior turn's overclaim).** Three forms must be separated:
- literal VAM current loop `μ = e‖v_↺‖r_c/2 = (α²/4)μ_B ≈ 10⁻⁵ μ_B` — **wrong magnitude** *and*
  EM-active at fm (excluded by g-2). `[DERIVED NEGATIVE]`
- the visible moment is Compton-scale Dirac/Zitterbewegung: `e·c·λ̄_C/2 = μ_B` exactly (charge at
  the Compton radius at speed c), i.e. the pointlike charged-sector g=2 moment. `[ORTHODOX]`
- **SST-51 and SST-86 survive** the reinterpretation: SST-51 is a *selection principle* (the
  moment is variationally selected, not a literal fm current loop); SST-86 derives the
  hydrodynamic spin `ℏ_SST = ρ_core r_c³ Γ_SST` (EM-neutral angular momentum) and feeds it into
  the *standard* `μ_B = eℏ/2m_e` (Dirac). The EM-active part is the Dirac formula, not the fm
  flow. So the swirl supplies the **spin/mass geometry**; the **charged spinon** supplies the
  Dirac moment. `[CONSISTENT under reinterpretation]`

The surviving requirement (the real open gate): the composite `H⁰_{3₁} ⊗ s⁻` (spin/ℏ from the
flow, charge `e` on the pointlike spinon) must reproduce **g = 2 to ~10⁻¹²** — i.e. behave as a
pointlike Dirac fermion. SST-51 *asserts* this via dynamical selection rather than deriving it;
proving the composite g-factor is `2 + O(α/2π)` without fm-scale form-factor deviations is the
open task. `[OPEN, LOAD-BEARING]`

Status (§8.3):
- `r_c = R_horn/flow` (not tube/charge radius) — `[REINTERPRETATION, WELL-FOUNDED]`
- `r_c ≠ R_charge` — `[REQUIRED]`; charge compositeness — `[SOLVED if spinon-localized]`
- literal fm current-loop moment — `[DERIVED NEGATIVE]`; Dirac moment on spinon — `[REQUIRED]`
- SST-51 / SST-86 (spin from flow + Dirac μ_B) — `[SURVIVE; reinterpret, do not discard]`
- composite g = 2 to 10⁻¹² — `[OPEN, LOAD-BEARING]`
- `ρ_core, Γ₀, R_∞, ℏ_SST = ρ_core r_c³ Γ` under r_c-as-flow — `[REQUIRES corpus-wide r_c pass]`

---

## Bottom line

**Dead as a fundamental ontology** (three independent axes): the fm-scale classical
incompressible scalar fluid cannot be the substrate for the relativistic/photon sector —
killed by (1) the Galilei boost algebra (§1), (2) the `F□F` dispersion = Tak III (§3), and
(3) the foundational over-constraint (§7). It survives only as an **IR-effective** description.

**Two survivors (updated by §8):**
1. **CP¹ / Hopfion bosonic route** `[PRIMARY]` — `M_SST = S² ≃ CP¹`; electron = trefoil Hopfion
   (`π₃=ℤ`, `Q_H≈7`); automatic rank-2 isotropy from continuous SO(3). Binding gate: **phase
   coexistence** of a deconfined photon and ordered Hopfions (leans negative in the minimal
   model). Plus the target-independent metric-locking gate.
2. **Trans-Planckian scalar medium** `[ALTERNATIVE]` — `ξ ≲ 10⁻¹¹ r_c`, `m_eff ~ m_Planck`; the
   fluid is purely IR-effective; the whole swirl/`r_c` sector is emergent ~20 orders below.
3. **Fermionic Volovik node vacuum** `[DEMOTED to research-track]` — exact O nodes are crystal-
   only (dim-6 survives), exact I unreachable (§7, §8); superseded by the bosonic route.

**The two gates that now bear the weight (both target-independent of the topology win):**
- **phase coexistence** — can one phase host a gapless emergent U(1) photon *and* stable trefoil
  Hopfions? (Minimal CP¹ says no; a multi-field construction is unbuilt.)
- **metric locking** `c_e = c_γ` — needs an emergent-Lorentz RG fixed point; not delivered by any
  point or continuous symmetry alone.

**What survives intact from the corpus:** `v_↺` as internal/tangential (rest mass, not a second
lightcone); `L_K` and the α-relation (orientation-invariant; survives the Hopfion reinterpretation
since `L_K` is the preimage-loop ropelength); chirality as the matter/antimatter label
(now = sign of the Hopf charge `Q_H`); the Compton anchor. None were damaged by this audit.
