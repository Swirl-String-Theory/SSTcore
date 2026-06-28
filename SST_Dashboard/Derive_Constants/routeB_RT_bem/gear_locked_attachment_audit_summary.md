# Gear-Locked Attachment Lemma audit summary

## Purpose

This audit treats the 3D print as a mechanical analogue of a closed framed SST tube with gear-locked phases. It tests whether the assembly admits one collective phase and whether a central helix/axle phase can represent a global attachment holonomy.

```text
[SUPPORTING MECHANICAL MODEL] not a proof of physical SST dynamics.
The core question is whether local ring/core rotations are globally locked to a central phase.
```

## Mesh inventory

| label | vertices | faces | watertight | body_count | extents | volume |
|---|---|---|---|---|---|---|
| gear | 127857 | 255714 | YES | 3 | 69.912 x 74.119 x 45.402 | 47171.8959873 |
| axle | 82291 | 164582 | YES | 1 | 13.239 x 13.239 x 300.667 | 16694.6295636 |

## Gear components

| id | center | volume | normal | angle_to_axle_deg |
|---|---|---|---|---|
| 1 | (-4.896,-8.561,0.054) | 15723.9653537 | (0.578,-0.339,0.742) | 42.0878707541 |
| 2 | (9.862,0.040,0.054) | 15723.9653204 | (0.004,0.670,0.742) | 42.0809141423 |
| 3 | (-4.966,8.521,0.054) | 15723.9653132 | (-0.583,-0.331,0.742) | 42.1177386371 |

## Component center distances

| i | j | distance | dx | dy | dz |
|---|---|---|---|---|---|
| 1 | 2 | 17.0818396291 | 14.758380688 | 8.60113042471 | 4.82613256719e-08 |
| 1 | 3 | 17.0818396614 | -0.0696070850355 | 17.0816978393 | 3.98917285524e-08 |
| 2 | 3 | 17.0818396278 | -14.827987773 | 8.48056741459 | -8.36959711953e-09 |

## Phase-lock scenarios

Sign mode: `all`; helix ratio `m=1.0`; chi target `1`.

Status counts: `{'FULLY_LOCKED_ATTACHMENT_ANALOG': 4, 'FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION': 4}`

| scenario | s12 | s13 | s23 | cycle | nullity | psi/theta1 | n_core | exact | status |
|---|---|---|---|---|---|---|---|---|---|
| S01_s12+1_s13+1_s23+1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | YES | FULLY_LOCKED_ATTACHMENT_ANALOG |
| S02_s12+1_s13+1_s23-1 | 1 | 1 | -1 | -1 | 0 |  | -1 | NO | FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION |
| S03_s12+1_s13-1_s23+1 | 1 | -1 | 1 | -1 | 0 |  | -1 | NO | FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION |
| S04_s12+1_s13-1_s23-1 | 1 | -1 | -1 | 1 | 1 | 1 | 1 | YES | FULLY_LOCKED_ATTACHMENT_ANALOG |
| S05_s12-1_s13+1_s23+1 | -1 | 1 | 1 | -1 | 0 |  | -1 | NO | FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION |
| S06_s12-1_s13+1_s23-1 | -1 | 1 | -1 | 1 | 1 | 1 | 1 | YES | FULLY_LOCKED_ATTACHMENT_ANALOG |
| S07_s12-1_s13-1_s23+1 | -1 | -1 | 1 | 1 | 1 | 1 | 1 | YES | FULLY_LOCKED_ATTACHMENT_ANALOG |
| S08_s12-1_s13-1_s23-1 | -1 | -1 | -1 | -1 | 0 |  | -1 | NO | FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION |

## Interpretation

```text

FULLY_LOCKED_ATTACHMENT_ANALOG:
  The gear sign graph is unfrustrated, the helix/axle is locked to one collective phase, and the helix holonomy matches chi.

FULLY_LOCKED_BUT_HELIX_RATIO_NOT_CHI:
  A collective mode exists, but the chosen helix gear ratio does not produce exact chi.

FRUSTRATED_OR_OVERCONSTRAINED_NO_COLLECTIVE_ROTATION:
  The sign constraints eliminate nonzero collective rotation; a simple all-external triangular gear graph has this problem.

UNDERLOCKED_MULTIPLE_PHASE_MODES:
  More than one phase remains, so the assembly is not globally attached.

```

## Canon status

```text

[KEEP / SUPPORTING MODEL]
  At least one lock scenario supports a single collective phase with exact chi holonomy.

[NOT A PROOF]
  The script is a mechanical analogy/audit. It does not prove the physical SST Attachment Lemma.

[NEXT MODULES]
  Reuse the bookkeeping for Hopf, Solomon, Borromean, TL3.3 Gear and twist-knot framed-tube controls.

```
