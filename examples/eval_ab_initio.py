import time
import sys
import math
import pandas as pd
# Tabel uit de afbeelding (Standard Model overzicht)
particles = [
    # Quarks (generaties I, II, III)
    {"category": "quark", "generation": "I",   "symbol": "u",   "name": "up",              "mass": "2.4 MeV/c^2",    "charge":  2/3, "spin": 0.5},
    {"category": "quark", "generation": "II",  "symbol": "c",   "name": "charm",           "mass": "1.27 GeV/c^2",   "charge":  2/3, "spin": 0.5},
    {"category": "quark", "generation": "III", "symbol": "t",   "name": "top",             "mass": "171.2 GeV/c^2",  "charge":  2/3, "spin": 0.5},

    {"category": "quark", "generation": "I",   "symbol": "d",   "name": "down",            "mass": "4.8 MeV/c^2",    "charge": -1/3, "spin": 0.5},
    {"category": "quark", "generation": "II",  "symbol": "s",   "name": "strange",         "mass": "104 MeV/c^2",    "charge": -1/3, "spin": 0.5},
    {"category": "quark", "generation": "III", "symbol": "b",   "name": "bottom",          "mass": "4.2 GeV/c^2",    "charge": -1/3, "spin": 0.5},

    # Leptons (generaties I, II, III)
    {"category": "lepton", "generation": "I",   "symbol": "νe",  "name": "electron neutrino", "mass": "<2.2 eV/c^2",   "charge":  0, "spin": 0.5},
    {"category": "lepton", "generation": "II",  "symbol": "νμ",  "name": "muon neutrino",     "mass": "<0.17 MeV/c^2", "charge":  0, "spin": 0.5},
    {"category": "lepton", "generation": "III", "symbol": "ντ",  "name": "tau neutrino",      "mass": "<15.5 MeV/c^2", "charge":  0, "spin": 0.5},

    {"category": "lepton", "generation": "I",   "symbol": "e",   "name": "electron",        "mass": "0.511 MeV/c^2",  "charge": -1, "spin": 0.5},
    {"category": "lepton", "generation": "II",  "symbol": "μ",   "name": "muon",            "mass": "105.7 MeV/c^2",  "charge": -1, "spin": 0.5},
    {"category": "lepton", "generation": "III", "symbol": "τ",   "name": "tau",             "mass": "1.777 GeV/c^2",  "charge": -1, "spin": 0.5},

    # Gauge bosons
    {"category": "gauge boson", "generation": "-", "symbol": "γ",   "name": "photon",   "mass": "0",             "charge": 0,  "spin": 1},
    {"category": "gauge boson", "generation": "-", "symbol": "g",   "name": "gluon",    "mass": "0",             "charge": 0,  "spin": 1},
    {"category": "gauge boson", "generation": "-", "symbol": "Z^0", "name": "Z boson",  "mass": "91.2 GeV/c^2",  "charge": 0,  "spin": 1},
    {"category": "gauge boson", "generation": "-", "symbol": "W±",  "name": "W boson",  "mass": "80.4 GeV/c^2",  "charge": "±1","spin": 1},
]



try:
    import swirl_string_core as sstcore
except ImportError:
    import sstbindings as sstcore

# Formules voor Alexander Root
phi0 = (1 + math.sqrt(5)) / 2
def twist_t_plus(n: int) -> float:
    return ((2.0 * n + 1.0) + math.sqrt(4.0 * n + 1.0)) / (2.0 * n)

def k_from_twist_alexander(n: int, phi_val: float = phi0) -> float:
    t_plus = twist_t_plus(n)
    return (2.0 * math.log(phi_val)) / math.log(t_plus)

# De Volledige Catalogus met Theorema Parameters
KNOT_INVARIANTS = {
    "3:1:1":  {"name": "Electron",      "k": 3.0,                       "g": 1, "G": 0},
    "5:1:1":  {"name": "Muon",          "k": 5.0,                       "g": 2, "G": 1},
    "7:1:1":  {"name": "Tau",           "k": 7.0,                       "g": 3, "G": 2},
    "4:1:1":  {"name": "Dark Matter",   "k": k_from_twist_alexander(1), "g": 1, "G": 1},
    "5:1:2":  {"name": "Up Quark",      "k": k_from_twist_alexander(2), "g": 1, "G": 1},
    "6:1:1":  {"name": "Down Quark",    "k": k_from_twist_alexander(3), "g": 1, "G": 1},
    "7:1:2":  {"name": "Strange Quark", "k": k_from_twist_alexander(4), "g": 1, "G": 1},
    "8:1:1":  {"name": "Charm Quark",   "k": k_from_twist_alexander(5), "g": 1, "G": 2},
    "9:1:2":  {"name": "Bottom Quark",  "k": k_from_twist_alexander(6), "g": 1, "G": 2},
    "10:1:1": {"name": "Top Quark",     "k": k_from_twist_alexander(7), "g": 1, "G": 2}
}

# Constanten voor de Master Equation
alpha_fs = 0.0072973525693  # 1 / 137.036
ELECTRON_MASS_MEV = 0.51099895

# PDG referentiemassa's (MeV) voor vergelijking met SST voorspellingen
KNOT_TO_PDG_MEV = {
    "3:1:1":  0.51099895,    # electron
    "5:1:1":  105.6583745,   # muon
    "7:1:1":  1776.86,       # tau
    "5:1:2":  2.4,           # up quark
    "6:1:1":  4.8,           # down quark
    "7:1:2":  104.0,         # strange quark
    "8:1:1":  1270.0,        # charm quark
    "9:1:2":  4180.0,        # bottom quark
    "10:1:1": 171200.0,      # top quark
}

def evaluate_particle(knot_id, M0_calibration, collect=False):
    props = KNOT_INVARIANTS.get(knot_id)
    if not props: return None

    print(f"\n┌──────────────────────────────────────────────────────────────────")
    print(f"│ 🔬 DEELTJE: {props['name']}  |  Topologie ID: {knot_id}")
    print(f"├──────────────────────────────────────────────────────────────────")

    # 1. AB INITIO C++ FYSICA: Laat de vloeistof de fysieke L_tot bepalen
    particle = sstcore.ParticleEvaluator(knot_id, resolution=2000)
    particle.relax(iterations=1500, timestep=0.005)
    L_tot = particle.get_dimless_ropelength()

    # 2. SST-59 THEOREMA: Pas de analytische theorie toe op de fysieke meetwaarde
    amplification = (4.0 / alpha_fs) ** props['G']
    braid_suppression = props['k'] ** -1.5
    genus_suppression = phi0 ** -props['g']

    # De Master Mass Equation
    mass_mev = M0_calibration * amplification * braid_suppression * genus_suppression * L_tot

    print(f"│ 📏 Ab Initio L_tot : {L_tot:.3f} (Fysiek samengeperst volume)")
    print(f"│ 🧮 Theorema Factors: k^-1.5 = {braid_suppression:.4f} | phi^-g = {genus_suppression:.4f}")
    print(f"│ 🛡️ Shielding (G)   : {props['G']} (Amplificatie = {amplification:.1e}x)")
    print(f"├──────────────────────────────────────────────────────────────────")
    pdg_mev = KNOT_TO_PDG_MEV.get(knot_id)
    if pdg_mev is not None:
        ratio = mass_mev / pdg_mev
        print(f"│ 🎯 SST Voorspelling: {mass_mev:.3f} MeV/c^2  |  PDG: {pdg_mev:.2f} MeV  |  Ratio: {ratio:.3f}")
    else:
        print(f"│ 🎯 SST Voorspelling: {mass_mev:.3f} MeV/c^2")
    print(f"└──────────────────────────────────────────────────────────────────")

    if collect:
        return {
            "knot_id": knot_id,
            "name": props["name"],
            "L_tot": L_tot,
            "mass_sst_mev": mass_mev,
            "mass_pdg_mev": KNOT_TO_PDG_MEV.get(knot_id),
        }
    return mass_mev

if __name__ == "__main__":
    print("\n=== SST Invariant Master Mass (Volledig Afgewerkt Model) ===")

    # STAP A: IJking van het Vacuum (M0) op het Elektron
    print("\n[*] Initialisatie: IJking van de Ether-dichtheid via het Elektron (3_1)...")
    electron_props = KNOT_INVARIANTS["3:1:1"]
    e_particle = sstcore.ParticleEvaluator("3:1:1", resolution=2000)
    e_particle.relax(iterations=1500, timestep=0.005)
    L_tot_electron = e_particle.get_dimless_ropelength()

    # Bereken M0 zodat het elektron EXACT 0.51099895 MeV weegt
    b_supp = electron_props['k'] ** -1.5
    g_supp = phi0 ** -electron_props['g']
    M0 = ELECTRON_MASS_MEV / (b_supp * g_supp * L_tot_electron)

    print(f"[+] Kalibratie voltooid. Globale M0 = {M0:.6f} MeV per L_tot")

    # STAP B: Voorspel de rest van het Standaardmodel en vergelijk met PDG
    targets = [
        "3:1:1", "5:1:1", "7:1:1",           # Leptonen
        "5:1:2", "6:1:1",                    # Quarks (Generatie 1)
        "7:1:2", "8:1:1",                    # Quarks (Generatie 2)
        "9:1:2", "10:1:1"                    # Quarks (Generatie 3)
    ]
    sst_results = []
    for knot in targets:
        row = evaluate_particle(knot, M0, collect=True)
        if row:
            sst_results.append(row)

    # Vergelijk SST voorspellingen met PDG in een DataFrame
    df_sst = pd.DataFrame(sst_results)
    if not df_sst.empty:
        df_sst["ratio_sst_pdg"] = df_sst.apply(
            lambda r: r["mass_sst_mev"] / r["mass_pdg_mev"] if r["mass_pdg_mev"] else float("nan"),
            axis=1
        )
        df_sst = df_sst[["knot_id", "name", "L_tot", "mass_sst_mev", "mass_pdg_mev", "ratio_sst_pdg"]]
        print("\n" + "=" * 80)
        print("SST Voorspelling vs PDG (Standaardmodel)")
        print("=" * 80)
        print(df_sst.to_string(index=False))

    # Originele particles-tabel (alleen voor referentie)
    print("\n" + "=" * 80)
    print("PDG Particle Overview (reference)")
    print("=" * 80)
    df_pdg = pd.DataFrame(particles)
    print(df_pdg.to_string(index=False))