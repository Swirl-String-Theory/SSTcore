# Ideal-knot index (`ideal.txt`)

Overzicht van knoop- en link-IDs in Brian Gilbert's *Database of Ideal Knots 3–10 crossings*
(`ideal.txt`). Mapping `N:1:k` → Rolfsen `N_k` volgt `KNOTPLOT_SCAN_REPORT.md`.

**ID-schema:** `C:R:V` = crossings : index : variant. Conway-notatie en ideale lengte `L`
staan op elke `<AB>`-regel. Attribuut `n="k"` = multi-component **link**.

---

## 0–2 crossings (links & referentie)

| Id | Rolfsen / naam | Conway | L | comp. | Opmerking |
|----|----------------|--------|---|-------|-----------|
| `0:1:1` | 0₁ unknot | `0` | 6.283 | 1 | BEM-referentie |
| `0:1:2` | 0₂ (2× unknot) | `0` | 12.0 | 2 | split link |
| `2:2:1` | L₂a₁ Hopf link | `2` | 12.0 | 2 | Lk = −1 (gevalideerd) |

---

## 3 crossings (1 prime knot)

| Id | Rolfsen | Conway | L | SST | Type |
|----|---------|--------|---|-----|------|
| `3:1:1` | **3₁** | `3` | 16.372 | e⁻ | torus T(2,3) **en** twist(1) |

Regel: 25

---

## 4 crossings (1 prime knot)

| Id | Rolfsen | Conway | L | SST | Type |
|----|---------|--------|---|-----|------|
| `4:1:1` | **4₁** | `2 2` | 21.043 | dark | amphichiral twist(2), \|Wr\|=0 |

Regel: 210

---

## 5 crossings (2 prime knots)

| Id | Rolfsen | Conway | L | SST | Type |
|----|---------|--------|---|-----|------|
| `5:1:1` | **5₁** | `5` | 23.599 | μ | torus T(2,5) |
| `5:1:2` | **5₂** | `3 2` | 24.734 | u | twist(3) |

Regels: 432, 667

---

## 6 crossings (3 prime knots + 1 link)

| Id | Rolfsen | Conway | L | SST | Type |
|----|---------|--------|---|-----|------|
| `6:1:1` | **6₁** | `4 2` | 28.355 | d | twist(4), stevedore |
| `6:1:2` | **6₂** | `3 1 2` | 28.509 | — | twist |
| `6:1:3` | **6₃** | `2 1 1 2` | 28.915 | — | twist |
| `6:2:3` | L₆a₄ | `6` | 18.0 | triple-gear | **3 comp.**, Borromean-klasse |

Regels: 910, 1152, 1403, 1652

> **Let op:** Borromean / triple-gear = `6:2:3` (3 componenten), **niet** `6:1:3`.

---

## 7 crossings (7 prime knots — compleet)

| Id | Rolfsen | Conway | L | SST | Type |
|----|---------|--------|---|-----|------|
| `7:1:1` | **7₁** | `7` | 30.700 | τ | torus T(2,7) |
| `7:1:2` | **7₂** | `5 2` | 31.931 | s | twist(5) |
| `7:1:3` | **7₃** | `4 3` | 31.964 | — | |
| `7:1:4` | **7₄** | `3 1 3` | 32.130 | — | |
| `7:1:5` | **7₅** | `3 2 2` | 32.628 | — | |
| `7:1:6` | **7₆** | `2 2 1 2` | 32.821 | — | |
| `7:1:7` | **7₇** | `2 1 1 1 2` | 32.800 | — | |

Regels: 1666–3101

---

## 8 crossings (21 entries: 18 prime + 3 satellieten — compleet)

| Id | Rolfsen | Conway | L | SST | Type |
|----|---------|--------|---|-----|------|
| `8:1:1` | **8₁** | `6 2` | 35.491 | c | twist(6) |
| `8:1:2` | **8₂** | `5 1 2` | 35.694 | — | |
| `8:1:3` | **8₃** | `4 4` | 35.578 | — | |
| `8:1:4` | **8₄** | `4 1 3` | 35.732 | — | |
| `8:1:5` | **8₅** | `3,3,2` | 36.064 | — | |
| `8:1:6` | **8₆** | `3 3 2` | 36.238 | — | |
| `8:1:7` | **8₇** | `4 1 1 2` | 36.103 | — | |
| `8:1:8` | **8₈** | `2 3 1 2` | 36.363 | — | |
| `8:1:9` | **8₉** | `3 1 1 3` | 36.217 | — | |
| `8:1:10` | **8₁₀** | `3,2 1,2` | 36.467 | — | |
| `8:1:11` | **8₁₁** | `3 2 1 2` | 36.446 | — | |
| `8:1:12` | **8₁₂** | `2 2 2 2` | 36.917 | — | |
| `8:1:13` | **8₁₃** | `3 1 1 1 2` | 36.398 | — | |
| `8:1:14` | **8₁₄** | `2 2 1 1 2` | 36.882 | — | |
| `8:1:15` | **8₁₅** | `2 1,2 1,2` | 36.826 | — | |
| `8:1:16` | **8₁₆** | `.2.2 0` | 36.750 | — | |
| `8:1:17` | **8₁₇** | `.2.2` | 37.241 | — | |
| `8:1:18` | **8₁₈** | `8*` | 37.453 | — | |
| `8:1:19` | 8₅ satelliet | `3,3,2-` | 30.494 | — | variant |
| `8:1:20` | 8₁₀ satelliet | `3,2 1,2-` | 31.546 | — | variant |
| `8:1:21` | 8₁₅ satelliet | `2 1,2 1,2-` | 32.766 | — | variant |

Regels: 3352–8204

---

## SST-kernknoopen 9 / 10 / 11

Alleen de fysiek/SST-relevante entries; de volledige 9- en 10-crossings-tabellen
(49 resp. 166 entries) staan in `ideal.txt` maar zijn hier niet opgenomen.

| Id | Rolfsen | Conway | L | SST | Type | Regel |
|----|---------|--------|---|-----|------|-------|
| `9:1:1` | **9₁** | `9` | 37.744 | lepton | torus T(2,9) | 8458 |
| `9:1:2` | **9₂** | `7 2` | 39.016 | b | twist(7) | 8692 |
| `10:1:1` | **10₁** | `8 2` | 42.581 | t | twist(8) | 20353 |
| `K11a367` | **11₁** | `11` | 44.805 | lepton | torus T(2,11) | 60248 |
| `K11a247` | **11₂** | `9 2` | 46.146 | quark | twist(9) | 60481 |

11-crossing knopen gebruiken KnotPlot-IDs (`K11a…`) i.p.v. `11:1:k`.

---

## Telling (≤8 crossings)

| Crossings | Prime knots | Links | Totaal in `ideal.txt` |
|-----------|-------------|-------|------------------------|
| 0–2 | 1 (unknot) | 2 | 3 |
| 3 | 1 | 0 | 1 |
| 4 | 1 | 0 | 1 |
| 5 | 2 | 0 | 2 |
| 6 | 3 | 1 | 4 |
| 7 | 7 | 0 | 7 |
| 8 | 18 + 3 sat. | 0 | 21 |
| **≤8 totaal** | **33 prime** | **3 links** | **39 entries** |

Volledige 9-crossings-serie: `9:1:1` … `9:1:49` (49 entries, regels 8458–20107).
Volledige 10-crossings-serie: `10:1:1` … `10:1:166` (166 entries, regels 20353–60008).

---

## SST-families

```
Leptons  = torus T(2,oneven):  3_1, 5_1, 7_1, 9_1, 11_1
           → Id: 3:1:1, 5:1:1, 7:1:1, 9:1:1, K11a367

Quarks   = twist (niet-torus): 5_2, 6_1, 7_2, 8_1, 9_2, 10_1, 11_2
           → Id: 5:1:2, 6:1:1, 7:1:2, 8:1:1, 9:1:2, 10:1:1, K11a247

Dark     = amphichiral:         4_1  →  4:1:1

Links    = Borromean/triple-gear: 6:2:3  (3 comp., niet in BEM single-knot runs)
```

---

## Snelle referentie (scripts / BEM)

```text
Referentie:     0:1:1
Hopf:           2:2:1
e⁻ / torus:     3:1:1, 5:1:1, 7:1:1, 9:1:1, K11a367
Quark / twist:  5:1:2, 6:1:1, 7:1:2, 8:1:1, 9:1:2, 10:1:1, K11a247
Dark:           4:1:1
Triple-gear:    6:2:3
```

Bron: `ideal.txt` (Brian Gilbert, 2016). SST-toewijzingen: `SST_emergent_SR_foundational_audit.md`.
