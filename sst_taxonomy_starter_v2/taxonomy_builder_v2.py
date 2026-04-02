
from __future__ import annotations
import argparse, csv, io, json, re, zipfile
from pathlib import Path

CORE_IDS = [
    "1_1","3_1","4_1","5_1","5_2","6_1","7_1","7_2","8_1","9_1","9_2","10_1","11_1","11_2",
    "Hopf","Solomon","Borromean","triple_gear_realization"
]

IDENTITY_FIELDS = [
    "id","standard_name","components","is_prime","object_class","geometry_class",
    "crossing_number","braid_index","genus","determinant","signature","arf",
    "chirality_label","reversible","amphichiral","amphichiral_type","symmetry_group",
    "pd_code","dt_code","source","notes"
]
EMBED_FIELDS = [
    "embedding_id","id","variant","source_file","representation","ideal_or_relaxed","sample_count",
    "curve_length","bbox_xmin","bbox_xmax","bbox_ymin","bbox_ymax","bbox_zmin","bbox_zmax",
    "normalization","fourier_block_count","provenance","notes"
]
COMP_FIELDS = [
    "id","vol_hyperbolic","vol_ref","hvol_norm","method","backend","tolerance","status","provenance","notes"
]
FIELD_FIELDS = [
    "embedding_id","id","grid_size","spacing","interior","polyline_samples","Hc","Hm","a_mu",
    "descriptor_backend","status","provenance","notes"
]
VALID_FIELDS = [
    "run_id","id","backend","N_geom","N_int","A_K","A_ratio_1_over_4pi","a_nc_over_rc","a_star_over_rc",
    "contact_model","fit_window","lambda_K","root_choice","jump","postcheck_status","continuation_status",
    "source_script","notes"
]

def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})

def read_csv_from_zip(zf: zipfile.ZipFile, name: str) -> list[dict]:
    data = zf.read(name).decode("utf-8", errors="ignore")
    return list(csv.DictReader(io.StringIO(data)))

def read_json_from_zip(zf: zipfile.ZipFile, name: str):
    return json.loads(zf.read(name).decode("utf-8", errors="ignore"))

def norm_id(raw: str) -> str:
    raw = (raw or "").strip()
    raw = raw.replace("knot.", "").replace(".fseries", "")
    raw = raw.replace("knot_", "").replace("_sst", "")
    raw = raw.replace("L2a1", "Hopf").replace("L4a1", "Solomon").replace("L6a4", "Borromean")
    raw = raw.replace("11.1","11_1").replace("11.2","11_2")
    return raw

def split_variant(kid: str) -> tuple[str, str | None]:
    m = re.match(r"^(\d+_\d+)([a-z])$", kid)
    if m:
        return m.group(1), m.group(2)
    return kid, None

def seeded_identity_row(kid: str) -> dict:
    row = {
        "id": kid,
        "standard_name": kid,
        "components": 1,
        "is_prime": True,
        "object_class": "knot",
        "geometry_class": "unknown",
        "crossing_number": None,
        "braid_index": None,
        "genus": None,
        "determinant": None,
        "signature": None,
        "arf": None,
        "chirality_label": "unknown",
        "reversible": None,
        "amphichiral": None,
        "amphichiral_type": "unknown",
        "symmetry_group": None,
        "pd_code": None,
        "dt_code": None,
        "source": "seeded_starter_v2",
        "notes": None,
    }
    if kid == "1_1":
        row["geometry_class"] = "unknot"
    elif kid in {"3_1","5_1","7_1"}:
        row["geometry_class"] = "torus"
    elif kid in {"4_1","5_2","6_1","7_2","8_1","9_1","9_2","10_1","11_1","11_2"}:
        row["geometry_class"] = "hyperbolic_or_unknown"
    elif kid in {"Hopf","Solomon","Borromean"}:
        row["components"] = 2 if kid in {"Hopf","Solomon"} else 3
        row["object_class"] = "link"
        row["is_prime"] = None
        row["geometry_class"] = "link"
    elif kid == "triple_gear_realization":
        row["components"] = 3
        row["object_class"] = "mechanical_realization"
        row["is_prime"] = None
        row["geometry_class"] = "linked_mechanical_hopf_type"
        row["notes"] = "Mechanical realization; not a standard knot-table object."
    if re.match(r"^\d+_\d+$", kid):
        row["crossing_number"] = int(kid.split("_")[0])
    return row

def seed_identity() -> list[dict]:
    return [seeded_identity_row(k) for k in CORE_IDS]

def extract_embeddings(resources_zip: Path | None, dashboard_zip: Path | None) -> list[dict]:
    seen = set()
    rows = []
    def add_row(src_zip: Path, internal_name: str):
        base_name = Path(internal_name).name
        if not base_name.endswith(".fseries"):
            return
        kid_raw = norm_id(base_name).replace("knot.", "").replace(".fseries", "")
        base_id, variant = split_variant(kid_raw)
        emb_id = f"{base_id}::{base_name}"
        if emb_id in seen:
            return
        seen.add(emb_id)
        rows.append({
            "embedding_id": emb_id,
            "id": base_id,
            "variant": variant or "base",
            "source_file": internal_name,
            "representation": "fseries",
            "ideal_or_relaxed": "resource_embedding",
            "sample_count": None,
            "curve_length": None,
            "bbox_xmin": None, "bbox_xmax": None,
            "bbox_ymin": None, "bbox_ymax": None,
            "bbox_zmin": None, "bbox_zmax": None,
            "normalization": None,
            "fourier_block_count": None,
            "provenance": src_zip.name,
            "notes": None,
        })
    for zpath in [resources_zip, dashboard_zip]:
        if not zpath:
            continue
        with zipfile.ZipFile(zpath) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".fseries"):
                    add_row(zpath, name)
    return sorted(rows, key=lambda r: (r["id"], r["embedding_id"]))

def extract_field_descriptors(dashboard_zip: Path | None) -> list[dict]:
    if not dashboard_zip:
        return []
    rows = []
    with zipfile.ZipFile(dashboard_zip) as zf:
        target = "SST_Dashboard/exports/SST_helicity_by_base.csv"
        if target not in zf.namelist():
            return []
        for r in read_csv_from_zip(zf, target):
            kid = norm_id(r.get("base",""))
            rows.append({
                "embedding_id": f"{kid}::aggregate_base",
                "id": kid,
                "grid_size": None,
                "spacing": None,
                "interior": None,
                "polyline_samples": None,
                "Hc": None,
                "Hm": None,
                "a_mu": r.get("mean"),
                "descriptor_backend": "helicity_csv_aggregate",
                "status": "aggregated_from_export",
                "provenance": target,
                "notes": f"std={r.get('std')}; count={r.get('count')}; is_amphi={r.get('is_amphi')}; flag={r.get('flag')}",
            })
    return rows

def extract_complement_geometry(dashboard_zip: Path | None, resources_zip: Path | None) -> list[dict]:
    rows_by_id = {}
    candidates = []
    if dashboard_zip:
        candidates.append((dashboard_zip, "SST_Dashboard/exports/fseries_batch_results.csv"))
    if resources_zip:
        candidates.append((resources_zip, "resources/fseries_batch_results.csv"))
        candidates.append((resources_zip, "resources/Knots_FourierSeries/fseries_batch_results.csv"))
    for zpath, internal in candidates:
        with zipfile.ZipFile(zpath) as zf:
            if internal not in zf.namelist():
                continue
            for r in read_csv_from_zip(zf, internal):
                kid = norm_id(r.get("knot_id", "") or r.get("file", ""))
                base_id, _ = split_variant(kid)
                hv = r.get("hyperbolic_volume_meta") or r.get("Hvortex_Vol(Vol/Vol(4_1))")
                if not hv:
                    continue
                rec = rows_by_id.get(base_id, {
                    "id": base_id,
                    "vol_hyperbolic": None,
                    "vol_ref": None,
                    "hvol_norm": None,
                    "method": "export_lookup",
                    "backend": "csv_export",
                    "tolerance": None,
                    "status": "unknown",
                    "provenance": internal,
                    "notes": None,
                })
                try:
                    val = float(hv)
                    if rec["hvol_norm"] is None:
                        rec["hvol_norm"] = val
                        rec["status"] = "partial_from_export"
                except Exception:
                    pass
                rows_by_id[base_id] = rec
    for kid in ["1_1","3_1","5_1","7_1","Hopf","Solomon"]:
        rows_by_id.setdefault(kid, {
            "id": kid,
            "vol_hyperbolic": 0.0 if kid in {"1_1","3_1","5_1","7_1"} else None,
            "vol_ref": None,
            "hvol_norm": None,
            "method": "seeded",
            "backend": "starter_v2",
            "tolerance": None,
            "status": "seeded_nonhyperbolic" if kid in {"1_1","3_1","5_1","7_1"} else "seeded_link_unknown",
            "provenance": "starter_seed",
            "notes": None,
        })
    return sorted(rows_by_id.values(), key=lambda r: r["id"])

def clean_float(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None

def clean_int(v):
    f = clean_float(v)
    if f is None:
        return None
    try:
        return int(round(f))
    except Exception:
        return None

def choose_id_from_row(row):
    keys = ["knot_id", "base_id", "base", "knot", "id"]
    for k in keys:
        if k in row and str(row[k]).strip():
            kid = norm_id(str(row[k]))
            base_id, _ = split_variant(kid)
            return base_id
    return None

def parse_validation_csv_rows(rows, source_name):
    out = []
    # normalize keys
    for r in rows:
        low = {str(k).strip().lower(): v for k, v in r.items()}
        kid = choose_id_from_row(low) or "3_1"
        run_id = source_name
        backend = low.get("backend")
        n_geom = clean_int(low.get("n_geom") or low.get("ngeom"))
        n_int = clean_int(low.get("n_int") or low.get("nint"))
        A_K = clean_float(low.get("a_k") or low.get("ak"))
        A_ratio = clean_float(low.get("a_ratio_1_over_4pi") or low.get("a_ratio") or low.get("ak_over_1_over_4pi"))
        a_nc = clean_float(low.get("a_nc_over_rc") or low.get("anc_over_rc") or low.get("a0_over_rc"))
        a_star = clean_float(low.get("a_star_over_rc") or low.get("astar_over_rc") or low.get("xstar"))
        contact_model = low.get("contact_model")
        fit_window = low.get("fit_window") or low.get("plateau")
        lambda_K = clean_float(low.get("lambda_k") or low.get("lambda"))
        root_choice = low.get("root_choice")
        jump = clean_float(low.get("jump"))
        postcheck_status = low.get("postcheck_status")
        continuation_status = low.get("continuation_status")
        if not any(v is not None and v != "" for v in [n_geom, n_int, A_K, A_ratio, a_nc, a_star, lambda_K, fit_window]):
            continue
        out.append({
            "run_id": run_id,
            "id": kid,
            "backend": backend,
            "N_geom": n_geom,
            "N_int": n_int,
            "A_K": A_K,
            "A_ratio_1_over_4pi": A_ratio,
            "a_nc_over_rc": a_nc,
            "a_star_over_rc": a_star,
            "contact_model": contact_model,
            "fit_window": fit_window,
            "lambda_K": lambda_K,
            "root_choice": root_choice,
            "jump": jump,
            "postcheck_status": postcheck_status,
            "continuation_status": continuation_status,
            "source_script": source_name,
            "notes": None,
        })
    return out

def extract_validation(dashboard_zip: Path | None) -> list[dict]:
    if not dashboard_zip:
        return []
    rows = []
    patterns = [
        re.compile(r"trefoil_closure/exports/.*/robustness_summary.*\.csv$", re.I),
        re.compile(r"trefoil_closure/exports/.*/final_best_estimate.*\.csv$", re.I),
        re.compile(r"trefoil_closure/exports/.*/shiftfree_postcheck.*\.csv$", re.I),
    ]
    with zipfile.ZipFile(dashboard_zip) as zf:
        names = zf.namelist()
        for name in names:
            if any(p.search(name) for p in patterns):
                try:
                    csv_rows = read_csv_from_zip(zf, name)
                    rows.extend(parse_validation_csv_rows(csv_rows, name))
                except Exception:
                    pass
        # supplement run metadata notes
        run_meta = {}
        for name in names:
            if re.search(r"trefoil_closure/exports/.*/run_metadata.*\.json$", name, re.I):
                try:
                    run_meta[name] = read_json_from_zip(zf, name)
                except Exception:
                    pass

    # attach run metadata hints where folder prefix matches
    for r in rows:
        for meta_name, meta in run_meta.items():
            folder = meta_name.rsplit("/", 1)[0]
            if r["run_id"].startswith(folder):
                bits = []
                if isinstance(meta, dict):
                    for k in ["backend", "contact_model", "plateau", "preferred_plateau", "label", "mode"]:
                        if k in meta and meta[k] is not None:
                            bits.append(f"{k}={meta[k]}")
                if bits:
                    r["notes"] = (r["notes"] + "; " if r["notes"] else "") + "; ".join(bits)
                if not r["backend"] and isinstance(meta, dict) and meta.get("backend"):
                    r["backend"] = meta["backend"]
                if not r["contact_model"] and isinstance(meta, dict) and meta.get("contact_model"):
                    r["contact_model"] = meta["contact_model"]

    # de-duplicate
    seen = set()
    dedup = []
    for r in rows:
        key = (r["run_id"], r["id"], r["N_geom"], r["N_int"], r["lambda_K"], r["A_K"], r["a_star_over_rc"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)
    return dedup

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resources", type=Path, default=None)
    ap.add_argument("--dashboard", type=Path, default=None)
    ap.add_argument("--sstcore", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    identity_rows = seed_identity()
    embed_rows = extract_embeddings(args.resources, args.dashboard)
    field_rows = extract_field_descriptors(args.dashboard)
    comp_rows = extract_complement_geometry(args.dashboard, args.resources)
    val_rows = extract_validation(args.dashboard)

    write_csv(out / "taxonomy_identity.csv", identity_rows, IDENTITY_FIELDS)
    write_csv(out / "taxonomy_embeddings.csv", embed_rows, EMBED_FIELDS)
    write_csv(out / "taxonomy_complement_geometry.csv", comp_rows, COMP_FIELDS)
    write_csv(out / "taxonomy_field_descriptors.csv", field_rows, FIELD_FIELDS)
    write_csv(out / "taxonomy_validation.csv", val_rows, VALID_FIELDS)

    summary = {
        "identity_rows": len(identity_rows),
        "embedding_rows": len(embed_rows),
        "complement_rows": len(comp_rows),
        "field_rows": len(field_rows),
        "validation_rows": len(val_rows),
        "inputs": {
            "resources": str(args.resources) if args.resources else None,
            "dashboard": str(args.dashboard) if args.dashboard else None,
            "sstcore": str(args.sstcore) if args.sstcore else None,
        }
    }
    (out / "build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
