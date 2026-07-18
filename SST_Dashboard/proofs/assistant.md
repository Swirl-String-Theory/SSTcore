# Role

You are an IntelliJ code agent working on a LaTeX repo for Swirl String Theory (SST). Your job is to **carry over** specific sections from `Swirl-String-Theory-Canon/SST_CANON-0.4.4.tex` into `Swirl-String-Theory-Canon/CANON-0.5.8.tex` **one by one**, replacing TODO placeholders and inserting status tags and cross-refs. Preserve LaTeX structure, numbering, and labels.

# Inputs & Paths

-   Source: `Swirl-String-Theory-Canon/SST_CANON-0.4.4.tex` (v0.4.4)

-   Destination: `Swirl-String-Theory-Canon/CANON-0.5.8.tex` (v0.5.8)

-   Both are UTF-8 LaTeX files in the project root (adjust paths if different).


# Global Editing Rules

-   **Never** overwrite existing v0.5.8 content unrelated to the checklist.

-   For each inserted block, add a line-comment tag:  
    `% [STATUS: <Canonical|Empirical|Research>]  [SOURCE: v0.4.4 §<sec-id>]`

-   Do **not** import v0.4.4 page headers/footers, table of contents, or duplicate preamble macros if already defined.

-   Keep math as-is; convert any inline Unicode (e.g., θ, Φ) to LaTeX commands if needed.

-   Respect destination labels; when adding labels, use a namespaced pattern to avoid collisions: `\label{canon58:<slug>}`.

-   Maintain existing `\ref{}`/`\eqref{}` in v0.5.8; when you bring in material that had labels in v0.4.4, either (a) translate them to new `canon58:` labels and update local refs within the pasted block, or (b) comment out the old label and add a new one next to it.

-   Where a section exists in 0.5.8 but has a `% TODO:` block, **replace only the TODO region** between its comment sentinels (see below).

-   Add a **one-liner “Dimensional & Recovery Check”** at the tail of each imported theorem/equation: `% Check: [units ok; limit → <Newtonian|Coulomb|Bohr>]`.


# TODO Region Sentinels (Destination)

Consider any block starting after a banner like:

```shell
%========================================================================================
% <TITLE> (<Status>)
%========================================================================================
% <TODO lines…>
```

Replace only the TODO lines, keeping the banner and section header. If no section header exists, insert a proper `\section{...}` as instructed below.

# Order of Operations (carry-over sequence)

Follow this exact order; **commit after each step** with the given message template.

1.  **Canon Governance & Status Taxonomy**


-   Find in v0.5.8: section banner “CANON GOVERNANCE & STATUS TAXONOMY”.

-   From v0.4.4: copy the formal taxonomy (definitions of Canonical/Empirical/Research; promotion/demotion rules for Axiom/Definition/Theorem/Corollary; canonicality tests checklist).

-   Insert as prose with a short `description` or `itemize` environment for classes + a compact checklist environment for “Canonicality Tests”.

-   Add tag: `% [STATUS: Canonical] [SOURCE: v0.4.4 §3]`.

-   **Commit**: `feat(canon58): port Governance & Status Taxonomy from v0.4.4 §3; replace TODO`


2.  **Calibrations & Protocols (Empirical Anchors)**


-   In v0.5.8: section “CALIBRATIONS & PROTOCOLS (Empirical)”.

-   From v0.4.4: bring the boxed empirical anchors: `m_W`, `m_Z`, `\sin^2\theta_W`, `v_\Phi≈246 GeV`, and the constants set `{\vswirl, r_c, \rho_f, \rho_m, FmaxEM, FmaxG}` with a brief note on **how they’re fixed**. Format as a LaTeX `\begin{tcolorbox}` (or `\begin{mdframed}`) if available; else `\paragraph{Empirical Anchors.}` + `aligned`.

-   Add tag: `% [STATUS: Empirical] [SOURCE: v0.4.4 §6.1 & constants table]`.

-   **Commit**: `feat(canon58): add Empirical Anchors box and calibration notes; cross-refs set`


3.  **Classical Invariants: Chronos–Kelvin + Clock–Radius Transport**


-   Destination: section banner exists; replace TODO.

-   Source: v0.4.4 Axiom (CK) and transport corollary with equations for `D/Dt(R^2\omega)=0` and `dS_t/dt = ...`.

-   Include the pseudo-metric remark as a boxed “Remark (Pseudo-metric)”.

-   Tag canonical and add labels `\label{canon58:CK}` and `\label{canon58:clock-transport}`.

-   **Commit**: `feat(canon58): import Chronos–Kelvin invariant + transport law with pseudo-metric remark`


4.  **Effective Medium: Coarse-Graining Derivation of \\rho\_f**


-   Destination: “EFFECTIVE MEDIUM…” section.

-   Source: v0.4.4 derivation with `\mu_*=\rho_m \pi r_c^2`, `\Gamma_*=2\pi r_c \vswirl`, `\nu`, elimination to `\rho_f(\rho_m, r_c, \vswirl, \langle\omega\rangle)`.

-   Present the final relation in a `\begin{boxedminipage}` or `\begin{tcolorbox}` as “Boxed Result”.

-   **Commit**: `feat(canon58): add coarse-graining derivation of rho_f with boxed result`


5.  **Swirl–EM Emergence (Full Derivation)**


-   Destination: “SWIRL–EM EMERGENCE”.

-   Source: v0.4.4 derivation from divergence-free `\mathbf a` to Maxwell wave equation, gauge condition, energy densities; include the photon as (pulsed) unknot and lossless radiation criteria.

-   Put main derivation in text; add `\appendix` pointer for extended math if needed.

-   Status tags: `% [STATUS: Canonical (derivation); Research notes where assumptions remain]`.

-   **Commit**: `feat(canon58): port Swirl–EM derivation incl. photon-as-unknot; add appendix hook`


6.  **Unified SST Lagrangian (Hydro + YM + Matter + Constraints)**


-   Create/locate section “UNIFIED SST LAGRANGIAN”.

-   Insert compact `\mathcal{L}_{\rm SST+Gauge+Matter}` block with incompressibility multiplier, optional helicity, YM terms, scalar/Higgs-like sector, minimal couplings; then provide bullet list of Euler–Lagrange recoveries.

-   Status: Canonical (form). Mark any coupling specifics Empirical/Research.

-   **Commit**: `feat(canon58): introduce unified SST+Gauge+Matter Lagrangian with EL recoveries`


7.  **Master Equations: Hydrogen Soft-Core + Bohr Recovery**


-   Destination: “MASTER EQUATIONS: HYDROGEN SOFT-CORE…”.

-   Source: potential `V(r) = -\Lambda/\sqrt{r^2+r_c^2}`, Coulomb limit, recover `a_0, E_1` for `r\gg r_c`. Add a mini numeric cross-check lines as comments or a small table.

-   **Commit**: `feat(canon58): add hydrogen soft-core potential and Bohr recovery + numeric cross-check`


8.  **Swirl Pressure Law (Euler Corollary) — Full Derivation**


-   Destination: “SWIRL PRESSURE LAW…”.

-   Source: derive `\frac{dp}{dr}=\rho_f \frac{v_\theta^2}{r}` and integrate to `p(r)=p_0+\rho_f v_0^2 \ln(r/r_0)`; note scope/limits.

-   Put full working to Appendix F (or create if not present) and keep main text concise.

-   **Commit**: `feat(canon58): derive swirl pressure law with integrated form and scope`


9.  **Gauge/EWSB Sector: Empirical-First Box + Theory**


-   Start section with the Empirical Anchors box (refer back to step 2 via `\ref{}`).

-   Then add director-elasticity derivation of `\theta_W` and the EWSB scale; include explicit cross-check vs data.

-   Tag mixed status; add `\label{canon58:gauge-openers}`.

-   **Commit**: `feat(canon58): gauge/EWSB opener with empirical-first anchors and derivations`


10.  **Quantum Measurement: Kernel Law + Near-Field Corollary + Bounds**


-   Insert kernel law `\Gamma_{R\to T}=\int \chi u\,\mathcal F`, demote geometry-invariant `P/A_{\rm eff}` to near-field corollary, include `\chi_{\rm eff}^{\max}` bounds and an “experimental status” note.

-   Tag: Canonical (kernel), Empirical (bounds), Research (universal resonance, if present).

-   **Commit**: `feat(canon58): add measurement kernel, near-field corollary, and bounds`


11.  **Hydrogen–Gravity Construction (if included)**


-   Short section. Include chiral-axis circulation and pressure deficit `\Delta p=-\tfrac12 \rho_f v^2`. Clearly split canonical vs long-range claims with inline status tags.

-   **Commit**: `feat(canon58): add hydrogen–gravity construction with explicit mixed-status labels`


12.  **Systematic Dimensional & Recovery Checks**


-   After each major theorem/equation above, add a one-liner comment:  
    `% Check: [units ok; limit → Newtonian/Coulomb/Bohr]`.

-   In Appendices, create a small table of these checks and link from sections.

-   **Commit**: `chore(canon58): inject systematic unit/limit checks and appendix table`


13.  **Appendices (A–I)**


-   Create/ensure appendices exist and are cross-referenced:

    -   A) Swirl Hamiltonian Density (include `r_c^2\|\omega\|^2`, `r_c^4\|\nabla\omega\|^2`, Kelvin-compatibility proof)

    -   B) Dimensional Analyses & Recovery Limits (tables)

    -   C) Derivation of `\rho_f` (full coarse-graining)

    -   D) Hydrogen Soft-Core Numerics (`a_0, E_1` with uncertainty propagation)

    -   E) Photon/Unknot Sector (lossless conditions; pulsed construction)

    -   F) Swirl Pressure Law — galaxy-scale integrals

    -   G) Calibration Protocol Notes (how `{\vswirl,r_c,\rho_f,\rho_m,FmaxEM,FmaxG}` are fixed)

    -   H) Experimental Status & Bounds (`\chi_{\rm eff}^{\max}` extraction; bounds table)

    -   I) Notation, Ontology, Glossary (symbol tables + taxonomy)

-   **Commit**: `feat(canon58): scaffold appendices A–I and wire cross-references`


# Matching & Extraction Heuristics

When the exact section titles differ between versions, use these regexes on `SST_CANON-0.4.4.tex`:

-   Governance/Status: `^(\\section|\\subsection)\\*?\\s*\\{.*(Governance|Status|Taxonomy).*\\}`

-   Calibrations & Protocols: `\\b(m_W|m_Z|\\sin\\^?2\\s*\\theta_W|v_\\Phi|v_{\\\\Phi})\\b` near a constants table/box.

-   CK invariant: `D\\s*/\\s*Dt\\s*\\(\\s*R\\^?2\\s*\\omega\\s*\\)` or `\\bChronos[-–]Kelvin\\b`

-   Coarse-graining `\\rho_f`: `\\mu_\\*\\s*=|\\Gamma_\\*\\s*=|\\rho_f\\s*\\(`

-   Swirl–EM: `\\nabla\\s*\\times\\s*E\\s*=\\s*-\\s*\\partial_t B|\\mathbf a|\\text\\{Maxwell\\}`

-   Unified Lagrangian: `\\mathcal L_{\\s*SST\\+Gauge\\+Matter\\s*}`

-   Hydrogen soft-core: `V\\(r\\)\\s*=\\s*-\\s*\\\\Lambda/\\sqrt\\{r\\^2\\+r_c\\^2\\}`

-   Pressure law: `\\b\\frac\\{dp\\}\\{dr\\}\\s*=\\s*\\rho_f\\s*\\frac\\{v_\\theta\\^2\\}\\{r\\}`

-   Gauge/EWSB: `\\theta_W|v_\\Phi|m_W|m_Z`

-   Measurement kernel: `\\Gamma_{R\\to T}\\s*=\\s*\\int\\s*\\chi\\s*u\\s*,\\s*\\mathcal F`

-   Hydrogen–Gravity: `\\Delta p\\s*=\\s*-\\s*\\tfrac\\{1\\}\\{2\\}\\s*\\rho_f\\s*v\\^2`


# Section Placement Map (Destination)

Map each carried item to these anchors in `CANON-0.5.8.tex`:

-   Governance → **Sec. 1 (front-matter or early “Formal Structure”)**

-   Calibrations → **Early “Calibrations & Protocols”**

-   CK & Transport → **Classical Invariants** (immediately after CK axiom)

-   Coarse-graining `\rho_f` → **Constants & Densities** (with boxed result)

-   Swirl–EM → **Swirl–EM** (main text; detailed math → Appendix E)

-   Unified Lagrangian → **End of core theory** or a dedicated main section before gauge details

-   Hydrogen soft-core → **Master Equations**

-   Pressure Law → **Master Equations** (+ full derivation → Appendix F)

-   Gauge/EWSB → **Gauge section opening**

-   Measurement → **Measurement section**

-   Hydrogen–Gravity → **Short dedicated section** (optional)

-   Dimensional checks → **Inline one-liners** + **Appendix B tables**

-   Appendices A–I → **End matter** (ensure `\appendix` structure)


# Cross-References & Labels

-   When inserting boxed equations, add `\label{canon58:box-<slug>}` right after `\begin{equation}` or the box start.

-   For each imported theorem/axiom, add `\label{canon58:thm-<slug>}` and use `\ref{}` where referenced in v0.5.8.


# Verification Checklist (per step)

-    Replaced only the `% TODO:` lines inside the targeted section banner.

-    Inserted status tag and source pointer.

-    Added (or updated) labels and local `\ref{}`s.

-    Added the one-liner **Dimensional & Recovery Check** comment.

-    Built LaTeX locally (if available) to confirm no missing refs/labels.

-    Committed with the exact commit message template above.


# Finalization

After completing all steps:

-   Run a full project build.

-   Generate a list of unresolved references or duplicate labels; resolve by namespacing with `canon58:`.

-   Output a brief summary diff of sections modified.


---