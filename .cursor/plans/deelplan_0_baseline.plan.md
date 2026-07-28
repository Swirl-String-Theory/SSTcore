---
name: Deelplan 0 Baseline
overview: "Baseline CI groen + Optie-A versiesync (beide 0.8.19). Geen fysica-API’s. Voorwaarde voor alle latere deelplannen."
todos:
  - id: d0-ci-baseline
    content: "Draai python -m pytest tests/ -q + npm test + npm run test:parity; failures eerst fixen"
    status: pending
  - id: d0-version-sync
    content: "SSTCORE_CANON_VERSION = 0.8.19 (gelijk package); pins test_basic.js / smoke"
    status: pending
  - id: d0-docs
    content: "VERSION_MANAGEMENT.md Optie-A sync-regel documenteren"
    status: pending
  - id: d0-ci-final
    content: "CI-poort stap 3–5: regressie 100% (geen nieuwe fysica-tests nodig)"
    status: pending
  - id: d0-git-commit
    content: "CI stap 6: git commit — SSTcore v0.8.19: sync package and canon version"
    status: pending
isProject: false
---

# Deelplan 0 — Baseline + versiesync

**Hoofdplan:** [sstcore_full_canon_upgrade_41269b2e.plan.md](sstcore_full_canon_upgrade_41269b2e.plan.md)  
**Depends on:** niets  
**Next:** [deelplan_0_8_20_geometry_contact.plan.md](deelplan_0_8_20_geometry_contact.plan.md)  
**Target versions:** `SSTCORE_VERSION == SSTCORE_CANON_VERSION == "0.8.19"`  
**Conventies:** [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md)

## Must-ship

```text
include/sstcore_version.h          # beide macros "0.8.19"
setup.py / package.json / src/SSTcore/__init__.py
tests/test_basic.js                # canonVersion == packageVersion
tests/test_version_consistency.py  # mismatch guard (stap 4)
docs/VERSION_MANAGEMENT.md
validation/baseline_inventory.json # lokaal artifact; niet committen tenzij gevraagd
```

Python: `CANON_VERSION` alleen als **alias** van `__version__` (zelfde string).

## CI-poort


1. **Baseline registreren**
   - `python -m pytest tests/ -q`
   - `npm test`
   - `npm run test:parity`
   - Leg Python-, Node-, CMake-, compiler-, platform- en `SST_NUMERIC_PROFILE`-informatie vast.
   - Bewaar stdout, stderr en exitcodes onder `validation/baseline/`.

2. **Code zonder nieuwe feature-tests**
   - Synchroniseer uitsluitend versievelden, smoke-pins en documentatie.
   - Voeg in deze stap nog geen nieuwe wetenschappelijke API of testmodule toe.

3. **Regressie**
   - Draai exact dezelfde drie commando’s opnieuw.
   - Elke nieuwe failure blokkeert de rest van het deelplan.

4. **Guard-tests**
   - Alleen versieconsistentie- en smoke-guards toevoegen.
   - Geen nieuwe fysica-tests.

5. **Final**
   - Python, Node en parity 100% groen.
   - Baseline-evidence en versie-inventaris aanwezig.

## Scope


- Herstel mismatch: [include/sstcore_version.h](../../include/sstcore_version.h) heeft nu package `0.8.19` / canon `0.8.20` → beide **0.8.19**.
- Update [tests/test_basic.js](../../tests/test_basic.js) (`canonVersion` pin).
- Update alle smoke/scripts die `0.8.20` verwachten.
- Docs: [docs/VERSION_MANAGEMENT.md](../../docs/VERSION_MANAGEMENT.md) — altijd gelijk houden.

**Repository-inventaris**

Leg vóór iedere wijziging vast:

- branch en commit;
- gewijzigde/ongetrackte bestanden;
- alle locaties waarin `0.8.x` voorkomt;
- actieve Python- en Node-native modules;
- bestaande platformskips;
- numeriek profiel en compilerflags.

Output: `validation/baseline_inventory.json`.

**Centrale versievelden**

Exposeer en test minimaal:

```cpp
SSTCORE_VERSION
SSTCORE_CANON_VERSION
```

```python
SSTcore.__version__
SSTcore.CANON_VERSION
```

Node moet dezelfde twee waarden rapporteren. Alle velden moeten exact `"0.8.19"` zijn.

**Automatische mismatch-guard**

Voeg een test toe die:

- alle versievelden vergelijkt;
- Python ↔ native vergelijkt;
- Node ↔ native vergelijkt;
- faalt wanneer één verborgen pin op `0.8.20` blijft staan.

**Versiebeheer-documentatie**

`VERSION_MANAGEMENT.md` beschrijft:

- Optie A: package- en canonversie zijn altijd gelijk;
- alle verplichte bumpplaatsen;
- verbod op gedeeltelijke bumps;
- hotfixbeleid;
- buildmetadata zoals commit en numeric profile zonder tweede canonversie.

## Out of scope


- Nieuwe modules of wetenschappelijke API’s.
- Formulewijzigingen of herkalibratie van canonieke constanten.
- Version bump naar `0.8.20+`.
- Refactors die output, performanceprofiel of resource-layout wijzigen.

## Exit


- `version == canonVersion == "0.8.19"` in C++, Python, Node, package metadata en tests.
- Alle bestaande tests groen of als expliciete, reproduceerbare platformskip vastgelegd.
- Een opzettelijk gewijzigde versiepin laat de guard aantoonbaar falen.
- Geen wetenschappelijke uitvoer verandert.
- `validation/baseline_inventory.json` en testlogs zijn aanwezig en reproduceerbaar vanaf een schone checkout.

## Git (stap 6)

Na Exit (CI 100%): **aparte commit** — `SSTcore v0.8.19: sync package and canon version`. Zie [SHARED_CONVENTIONS.md](SHARED_CONVENTIONS.md). Geen bundeling met andere deelplannen.
