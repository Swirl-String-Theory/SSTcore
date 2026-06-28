import numpy as np
import os
import re
from scipy.interpolate import splprep, splev


def parse_knot_name(input_file: str):
    """
    Examples:
        knot_3.1.txt -> ("knot_3.1", "3:1:1", "3_1")
        knot_4.1.txt -> ("knot_4.1", "4:1:1", "4_1")
    """
    base = os.path.basename(input_file)
    stem, _ = os.path.splitext(base)

    m = re.fullmatch(r"knot_(\d+)\.(\d+)", stem)
    if m:
        crossings = int(m.group(1))
        index = int(m.group(2))
        knot_id = f"{crossings}:{index}:1"
        label = f"{crossings}_{index}"
        return stem, knot_id, label

    return stem, stem, stem.replace(".", "_")


def compute_original_polygon_length(coords):
    coords = np.asarray(coords, dtype=float)
    if np.allclose(coords[0], coords[-1]):
        closed = coords
    else:
        closed = np.vstack((coords, coords[0]))
    diffs = np.diff(closed, axis=0)
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def compute_fseries_from_coords(coords, num_harmonics=100, num_points=4000):
    """
    Convert closed 3D polygonal coordinates into Fourier coefficients
    using periodic spline resampling and arc-length quadrature.

    Returns:
        coeffs: list of tuples (ax, bx, ay, by, az, bz), j=1..num_harmonics
        L_tot: total resampled curve length
        coords_eq_centered: resampled centered coordinates
        ds: arc-length weights
        theta: angle grid
        original_point_count: number of distinct input points used
        original_closure_gap: ||r0-rN|| before endpoint cleanup
    """
    coords = np.asarray(coords, dtype=float)

    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError(f"Expected Nx3 coordinates, got shape {coords.shape}")

    original_closure_gap = float(np.linalg.norm(coords[0] - coords[-1]))

    # Remove duplicated endpoint if already closed
    if np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]

    original_point_count = len(coords)

    if original_point_count < 4:
        raise ValueError("Need at least 4 distinct points")

    # Closed polygon for chord-length parameterization
    closed_coords = np.vstack((coords, coords[0]))
    diffs = np.diff(closed_coords, axis=0)
    chord_lengths = np.linalg.norm(diffs, axis=1)

    if not np.any(chord_lengths > 0):
        raise ValueError("Degenerate coordinate set")

    # Parameter u in [0,1)
    u = np.concatenate(([0.0], np.cumsum(chord_lengths[:-1])))
    if u[-1] <= 0:
        raise ValueError("Degenerate parameterization")
    u /= u[-1]

    # Periodic spline fit and uniform resampling
    tck, _ = splprep(
        [coords[:, 0], coords[:, 1], coords[:, 2]],
        u=u,
        s=0.0,
        per=True,
    )
    u_uniform = np.linspace(0.0, 1.0, num_points, endpoint=False)
    x_eq, y_eq, z_eq = splev(u_uniform, tck)
    coords_eq = np.column_stack((x_eq, y_eq, z_eq))

    # Arc-length weights on resampled closed curve
    diffs_eq = np.diff(np.vstack((coords_eq, coords_eq[0])), axis=0)
    ds = np.linalg.norm(diffs_eq, axis=1)
    L_tot = float(np.sum(ds))

    if L_tot <= 0:
        raise ValueError("Resampled curve has zero total length")

    # Angle variable theta = 2*pi*s/L
    s = np.concatenate(([0.0], np.cumsum(ds[:-1])))
    theta = 2.0 * np.pi * s / L_tot

    # Arc-length-weighted centering
    center = np.average(coords_eq, axis=0, weights=ds)
    coords_eq_centered = coords_eq - center

    coeffs = []
    for j in range(1, num_harmonics + 1):
        cos_j = np.cos(j * theta)
        sin_j = np.sin(j * theta)

        ax = (2.0 / L_tot) * np.sum(coords_eq_centered[:, 0] * cos_j * ds)
        bx = (2.0 / L_tot) * np.sum(coords_eq_centered[:, 0] * sin_j * ds)

        ay = (2.0 / L_tot) * np.sum(coords_eq_centered[:, 1] * cos_j * ds)
        by = (2.0 / L_tot) * np.sum(coords_eq_centered[:, 1] * sin_j * ds)

        az = (2.0 / L_tot) * np.sum(coords_eq_centered[:, 2] * cos_j * ds)
        bz = (2.0 / L_tot) * np.sum(coords_eq_centered[:, 2] * sin_j * ds)

        coeffs.append((ax, bx, ay, by, az, bz))

    return (
        coeffs,
        L_tot,
        coords_eq_centered,
        ds,
        theta,
        original_point_count,
        original_closure_gap,
    )


def reconstruct_from_fseries(coeffs, theta):
    """
    Reconstruct centered coordinates from Fourier coefficients on the theta grid.
    """
    theta = np.asarray(theta, dtype=float)
    recon = np.zeros((len(theta), 3), dtype=float)

    for j, (ax, bx, ay, by, az, bz) in enumerate(coeffs, start=1):
        cos_j = np.cos(j * theta)
        sin_j = np.sin(j * theta)

        recon[:, 0] += ax * cos_j + bx * sin_j
        recon[:, 1] += ay * cos_j + by * sin_j
        recon[:, 2] += az * cos_j + bz * sin_j

    return recon


def compute_reconstruction_metrics(coords_eq_centered, coords_recon):
    """
    Compare reconstructed curve to the centered resampled target curve.
    """
    delta = coords_eq_centered - coords_recon
    err = np.linalg.norm(delta, axis=1)

    rms_error = float(np.sqrt(np.mean(err**2)))
    max_error = float(np.max(err))
    mean_error = float(np.mean(err))

    rms_radius = float(np.sqrt(np.mean(np.sum(coords_eq_centered**2, axis=1))))
    max_radius = float(np.max(np.linalg.norm(coords_eq_centered, axis=1)))

    bbox_min = np.min(coords_eq_centered, axis=0)
    bbox_max = np.max(coords_eq_centered, axis=0)
    bbox_diag = float(np.linalg.norm(bbox_max - bbox_min))

    rel_rms_vs_rms_radius = rms_error / rms_radius if rms_radius > 0 else np.nan
    rel_rms_vs_bbox_diag = rms_error / bbox_diag if bbox_diag > 0 else np.nan
    rel_max_vs_bbox_diag = max_error / bbox_diag if bbox_diag > 0 else np.nan

    return {
        "rms_error": rms_error,
        "mean_error": mean_error,
        "max_error": max_error,
        "rms_radius": rms_radius,
        "max_radius": max_radius,
        "bbox_diag": bbox_diag,
        "rel_rms_vs_rms_radius": rel_rms_vs_rms_radius,
        "rel_rms_vs_bbox_diag": rel_rms_vs_bbox_diag,
        "rel_max_vs_bbox_diag": rel_max_vs_bbox_diag,
    }


def write_fseries(output_file, input_file, coeffs, L_tot):
    """
    Write plain 6-column .fseries file:
        ax bx ay by az bz
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"% Source {os.path.basename(input_file)}\n")
        f.write("% Fourier coefficients from periodic spline + arc-length quadrature\n")
        f.write(f"% L = {L_tot:.12f}\n")
        f.write("% columns: ax bx ay by az bz\n")
        f.write("% x(theta)=sum_j[ax_j cos(j theta)+bx_j sin(j theta)], etc.\n")
        for row in coeffs:
            f.write(" ".join(f"{v: .9f}" for v in row) + "\n")


def write_ideal_like_txt(output_file, input_file, knot_id, coeffs, L_tot):
    """
    Write single-entry ideal_short.txt-like XML-ish file:
        <DATA ...>
          <AB Id="3:1:1" ...>
            <Coeff I="1" A="ax, ay, az" B="bx, by, bz" />
            ...
          </AB>
        </DATA>
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('<DATA Title="Generated from KnotPlot coordinates" ')
        f.write('Author="conversion script" ')
        f.write('Date="generated locally">\n')

        f.write(f'  <AB Id="{knot_id}" Conway="" L="{L_tot:.12f}" D="1.000000">\n')
        for j, (ax, bx, ay, by, az, bz) in enumerate(coeffs, start=1):
            f.write(
                f'    <Coeff I="{j:3d}" '
                f'A="{ax: .9f},{ay: .9f},{az: .9f}" '
                f'B="{bx: .9f},{by: .9f},{bz: .9f}" />\n'
            )
        f.write("  </AB>\n")
        f.write("</DATA>\n")


def write_report(
        output_file,
        input_file,
        knot_id,
        num_harmonics,
        num_points,
        original_point_count,
        original_polygon_length,
        original_closure_gap,
        L_tot,
        metrics,
):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"source_file: {os.path.basename(input_file)}\n")
        f.write(f"knot_id: {knot_id}\n")
        f.write(f"num_harmonics: {num_harmonics}\n")
        f.write(f"num_resample_points: {num_points}\n")
        f.write(f"original_point_count: {original_point_count}\n")
        f.write(f"original_polygon_length: {original_polygon_length:.12f}\n")
        f.write(f"resampled_spline_length: {L_tot:.12f}\n")
        f.write(f"original_closure_gap: {original_closure_gap:.12e}\n")
        f.write("\n")
        f.write("# reconstruction error against centered resampled spline\n")
        f.write(f"rms_error: {metrics['rms_error']:.12e}\n")
        f.write(f"mean_error: {metrics['mean_error']:.12e}\n")
        f.write(f"max_error: {metrics['max_error']:.12e}\n")
        f.write("\n")
        f.write("# geometric scales\n")
        f.write(f"rms_radius: {metrics['rms_radius']:.12e}\n")
        f.write(f"max_radius: {metrics['max_radius']:.12e}\n")
        f.write(f"bbox_diag: {metrics['bbox_diag']:.12e}\n")
        f.write("\n")
        f.write("# relative errors\n")
        f.write(f"rel_rms_vs_rms_radius: {metrics['rel_rms_vs_rms_radius']:.12e}\n")
        f.write(f"rel_rms_vs_bbox_diag: {metrics['rel_rms_vs_bbox_diag']:.12e}\n")
        f.write(f"rel_max_vs_bbox_diag: {metrics['rel_max_vs_bbox_diag']:.12e}\n")

        rel = metrics["rel_rms_vs_bbox_diag"]
        f.write("\n")
        f.write("# quick assessment\n")
        if np.isfinite(rel):
            if rel < 1e-4:
                f.write("assessment: excellent\n")
            elif rel < 1e-3:
                f.write("assessment: very_good\n")
            elif rel < 1e-2:
                f.write("assessment: usable_check_needed\n")
            else:
                f.write("assessment: increase_harmonics_or_resampling\n")
        else:
            f.write("assessment: undefined_scale\n")


def convert_knot_txt_file(
        input_file,
        export_root="export",
        num_harmonics=100,
        num_points=4000,
):
    coords = np.loadtxt(input_file)
    stem, knot_id, label = parse_knot_name(input_file)

    original_polygon_length = compute_original_polygon_length(coords)

    (
        coeffs,
        L_tot,
        coords_eq_centered,
        ds,
        theta,
        original_point_count,
        original_closure_gap,
    ) = compute_fseries_from_coords(
        coords,
        num_harmonics=num_harmonics,
        num_points=num_points,
    )

    coords_recon = reconstruct_from_fseries(coeffs, theta)
    metrics = compute_reconstruction_metrics(coords_eq_centered, coords_recon)

    knot_export_dir = os.path.join(export_root, stem)
    os.makedirs(knot_export_dir, exist_ok=True)

    fseries_file = os.path.join(knot_export_dir, f"{stem}.fseries")
    ideal_file = os.path.join(knot_export_dir, f"{stem}_ideal.txt")
    report_file = os.path.join(knot_export_dir, f"{stem}_report.txt")

    write_fseries(fseries_file, input_file, coeffs, L_tot)
    write_ideal_like_txt(ideal_file, input_file, knot_id, coeffs, L_tot)
    write_report(
        report_file,
        input_file,
        knot_id,
        num_harmonics,
        num_points,
        original_point_count,
        original_polygon_length,
        original_closure_gap,
        L_tot,
        metrics,
    )

    print(f"Generated: {fseries_file}")
    print(f"Generated: {ideal_file}")
    print(f"Generated: {report_file}")


def batch_convert_current_directory(
        export_root="export",
        num_harmonics=100,
        num_points=4000,
):
    """
    Convert raw coordinate files under export/<stem>/<stem>.txt (one per knot folder).
    """
    if not os.path.isdir(export_root):
        return
    for name in sorted(os.listdir(export_root)):
        if not name.startswith("knot_"):
            continue
        knot_dir = os.path.join(export_root, name)
        if not os.path.isdir(knot_dir):
            continue
        target = os.path.join(knot_dir, f"{name}.txt")
        if not os.path.isfile(target):
            continue
        try:
            convert_knot_txt_file(
                target,
                export_root=export_root,
                num_harmonics=num_harmonics,
                num_points=num_points,
            )
        except Exception as e:
            print(f"Failed on {target}: {e}")


if __name__ == "__main__":
    batch_convert_current_directory(
        export_root="export",
        num_harmonics=100,
        num_points=4000,
    )