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

### 8.4 Route B: spin-charge-separated electron with topological spin-½ (canon candidate)

The two-sector electron `e⁻ = H⁰_{3₁} ⊗ (charged scalar)` is made concrete and the g=2 gate is
**resolved up to one pinned axiom**. This is the first net-positive result of the foundational
audit; it strengthens "matter = knot" rather than weakening it.

**(a) Orbital μ_B from quantized circulation [DERIVED GIVEN one-quantum Compton circulation].** Give the neutral
Hopfion flow one circulation quantum `κ = h/m_e`. Then `v(R) = ℏ/(m_e R)`, so `R·v = ℏ/m_e` on
*every* streamline. A charge advected by the flow has `L = ℏ` and `μ = e v R/2 = μ_B` at any
radius — **no fine-tuning of the streamline** (verified numerically). The Compton radius `λ̄_C`
is the `v=c` inner edge (Zitterbewegung); the neutral core `r_c = (α/2)λ̄_C = λ̄_C/274` sits well
inside, EM-inert. This converts SST-86's open "select the streamline" gate into "select one
quantum (n=1)."

**(b) Spin-½ is topological [DERIVED, conditional on θ=π and odd Q_H].** In 3+1D the S² sigma
model admits a ℤ₂ θ-term because `π₄(S²) = ℤ₂` (the 3+1D analogue of Wilczek–Zee). At `θ=π` a
2π rotation of a Hopfion gives a phase `(−1)^{Q_H}`: **odd Q_H → fermion (spin-½), even Q_H →
boson**. The trefoil at `Q_H ≈ 7` (odd) is a fermion. Spin AND exchange statistics come from the
same ℤ₂ invariant, so they are automatically consistent — **no appeal to emergent Lorentz / the
spin-statistics theorem is needed**; the spin-½ is topological, not dynamical.

**(c) Spin-charge separation — CORRECTS the SST-51/86 patch.** For `fermion ⊗ X = fermion`, since
the Hopfion is now a fermion, the charged object must be a **boson**:
```
H⁰_{3₁} = spinon   : spin-½, neutral, carries spin + statistics + knot identity   [the knot carries spin]
chargon  : spin-0 boson, charge −e, gapped (uncondensed → photon stays massless)
e⁻ = spinon ⊗ chargon  : spin-½, charge −e
```
The patch assigned spin+charge to the "spinon"; the correct (standard spin-charge-separation)
assignment is the reverse — the neutral knot is the spinon, the charged scalar is the chargon.
This **strengthens "matter = knot carries spin/identity"** and avoids Route A (vestigial knot).

**(d) g=2 reinterpreted [DERIVED, conditional].** Visible moment `μ = μ_B` is the chargon's
orbital (`L=ℏ`); spin `S = ℏ/2` is the Hopfion's. `g = μ/(μ_B·S/ℏ) = μ_B/(μ_B/2) = 2`. The
"anomalous" doubling is the ratio of a full orbital quantum to a half spin quantum. Penning-trap
precession is reproduced.

**(e) θ=π is pinned, not derived [POSITED, falsifiable].** `θ` is a free ℤ₂ choice at the IR
level; `θ=π` is the unique value giving fermionic odd-Q_H matter, so it is **pinned by observed
fermion statistics** (as `N_c` odd is pinned by baryon statistics in QCD). Not derived from the
sigma model; needs an axiom or a UV (parton) completion.

**Canonical prediction (falsifiable, corpus-wide):**
```
Q_H odd  ⇔ fermion ;  Q_H even ⇔ boson   (for ALL particles)
```
photon (unknot, Q_H=0, even) = boson ✓ ; electron (trefoil, Q_H≈7, odd) = fermion ✓.
**Required check:** the entire lepton/quark knot sequence T(p,2) must have odd Q_H, and all gauge/
scalar bosons even Q_H. Any violation falsifies θ=π and breaks the knot taxonomy.

**Status (§8.4):**
- orbital μ_B from `κ = h/m_e` circulation quantum — `[DERIVED GIVEN one-quantum circulation; selection of Γ_C=h/m_e is the open binding gate]`
- spin-½ from `π₄(S²)=ℤ₂` θ-term at θ=π, odd Q_H — `[DERIVED, conditional on θ=π & odd Q_H]`
- spin-charge separation (knot = spinon, charge = bosonic chargon) — `[CANON CANDIDATE; corrects patch]`
- g=2 (orbital-ℏ / spin-½) — `[DERIVED, conditional]`
- θ=π — `[POSITED, pinned by fermion statistics; not derived]`
- `Q_H parity ⇔ statistics` for all particles — `[FALSIFIABLE PREDICTION; check T(p,2) Hopf charges]`
- one-quantum (n=1) selection; chargon–Hopfion binding; EM-inertness < δa_H; metric locking
  `c_e=c_γ` — `[OPEN]`

### 8.5 Knot → particle taxonomy (torus = lepton, twist = quark, amphichiral = dark)

Proposed assignment, with knot-theory family and geometry computed from the ideal
(tight) knots in `ideal.txt` (writhe = Gauss self-linking integral, validated:
trefoil |Wr|=3.419, amphichiral 4_1 |Wr|=0.000).

| knot | part. | family | L_rope | \|writhe\| |
|------|-------|--------|-------:|-------:|
| 3_1 | e⁻ | torus T(2,3) **&** twist(1) | 16.372 | 3.419 |
| 4_1 | dark | **amphichiral** twist(2) | 21.043 | **0.000** |
| 5_1 | μ | torus T(2,5) | 23.599 | 6.295 |
| 5_2 | u | twist(3) | 24.734 | 4.539 |
| 6_1 | d | twist(4) | 28.355 | 1.107 |
| 7_1 | τ | torus T(2,7) | 30.700 | 9.181 |
| 7_2 | s | twist(5) | 31.931 | 5.672 |
| 8_1 | c | twist(6) | 35.491 | 2.216 |
| 9_1 | (lep) | torus T(2,9) | 37.744 | 12.067 |
| 9_2 | b | twist(7) | 39.016 | 6.769 |
| 10_1 | t | twist(8) | 42.581 | 3.324 |
| 11_1 | (lep) | torus T(2,11) | 44.805 | 14.937 |
| 11_2 | (q) | twist(9) | 46.146 | 7.874 |

**Structural results (knot theory, solid):**
- **Leptons = torus T(2,odd)** {3_1,5_1,7_1,9_1,11_1}; **quarks = twist (non-torus)**
  {5_2,6_1,7_2,8_1,9_2,10_1,11_2}; **3_1 = unique knot that is BOTH** → electron
  (lightest, the overlap). All chiral except 4_1. `[STRUCTURALLY SOUND]`
- **4_1 = unique amphichiral knot → writhe = 0 exactly → self-mirror → self-conjugate**
  (own antiparticle) → natural Majorana/dark candidate. `[DERIVED — geometric confirmation]`
- Torus-lepton writhe grows linearly: 3.42, 6.30, 9.18, 12.07, 14.94 (Δ≈2.88/step). `[OBSERVED]`
- Twist-quark writhe splits into two interleaved linear series by half-twist parity
  (odd n: 4.54,5.67,6.77,7.87; even n: 1.11,2.22,3.32; Δ≈1.11). `[OBSERVED]`

**Critical caveats:**
- `[CRITICAL NOTE]` **writhe ≠ Q_H.** Writhe is real-valued/geometric; the θ=π test
  (§8.4) needs the **integer Hopf charge** of the minimal-energy Hopfion, which is
  framing-dependent and needs Faddeev–Skyrme (§8.6). Writhe gives the chirality/
  self-conjugacy structure (decisive for 4_1=dark) but NOT the fermion/boson parity.
- `[CRITICAL NOTE]` the twist writhe sub-series (odd/even half-twist) does **not** map
  onto quark electric charge (+2/3 vs −1/3) in the current assignment — up/charm/top and
  down/strange/bottom each straddle both sub-series. Twist-index → fractional charge
  remains `[SPECULATIVE]` and in tension with charge-on-chargon (§8.4).
- Q_H(T(2,q)) = pq+1 hypothesis (→ 7,11,15,19,23, all odd → leptons fermionic). Even
  `Q_H(3_1)=7` is `[EXPECTED FROM LITERATURE — Hietarinta–Salo; NOT YET VERIFIED IN SST PIPELINE]`;
  the whole taxonomy is `[EXECUTABLE, NOT YET EXECUTED]`.

### 8.6 Faddeev–Skyrme tooling and the executable status of the θ=π test

Built and validated the full pipeline to read off Q_H of relaxed knotted Hopfions
(`hopfion_tools.py`, `fs_hopfion_pipeline.py`, C++ kernel in `sstcore_ext/`).

- **Hopf-charge meter** Q_H=(1/16π²)∫A·B — converges to integer with resolution
  (0.88→0.95 for N=48→128, Q=1), topologically conserved under smooth deformation
  (<0.1%), returns Q_H=mn for axial (m,n) ansätze, charges 1–6. `[VERIFIED]`
- **Faddeev–Skyrme energy + analytic gradient** (manual reverse-mode) — gradient-checked
  vs finite differences to **1.3×10⁻⁸** (machine precision). `[VERIFIED]`
- **C++ writhe kernel** (pybind11, SSTcore-ready) — identical to numpy, 18–48× faster. `[VERIFIED]`
- **Relaxer** — lowers the discrete energy monotonically. `[WORKS]`
- **Lattice collapse / unwinding** — two failure modes diagnosed: (i) scale collapse
  (soliton shrinks below grid) and (ii) sub-grid charge unwinding. The **fixed-E₂
  constraint** (minimise E₄ at pinned E₂) kills (i): scale held to +0.2%. Mode (ii) is
  resolution-bound — Q_H retention over 100 steps rises 59%→71%→**98%** at N=40→56→**72**.
  `[fixed-E₂ constraint VERIFIED; N≥128 expected clean — Battye–Sutcliffe '98 / Hietarinta–Salo '00]`
- **Knotted seed** from `ideal.txt` Fourier curve + parallel-transport frame — builds
  knots, Q_H measurable. `[WORKS]` Note: Q_H=7 is an **emergent minimiser property**,
  not a seed input. `[NOTE]`

**Status of the θ=π / odd-Q_H taxonomy test:** moved from `[UNTESTABLE — no Q_H tool]`
to **`[EXECUTABLE, COMPUTE-BOUND]`**. Every component is validated incl. the fixed-E₂
relaxer (`fs_relax2.py`, holds Q_H to 98% at N=72). Handoff: port the relaxer to GPU,
N≥128, seed Q=7 (trefoil) and Q=11 (5_1), read off Q_H → decides pq+1 (is the muon knot
odd-Q_H → fermion?). Trefoil Q_H=7: `[EXPECTED FROM LITERATURE/PROGRAM; NOT YET VERIFIED IN SST PIPELINE]` — needs the run
above before `3_1 → Q_H=7` may be asserted. N≥128 charge conservation:
`[EXPECTED FROM 59→71→98% trend; NOT YET VERIFIED]`.

Link/boson sector: `sstcore_link` gives writhe + pairwise linking
(Hopf link Lk=−1 ✓, Borromean 6:2:3 all-zero matrix ✓); collective Borromean linking
needs the Milnor μ₁₂₃ kernel (next).

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
