# Reproducing the finite-core trefoil / spherical-cell closure calculation

This folder contains a minimal reproducibility script:

```text
reproduce_alpha_cell_closure.py
```

The script evaluates a Fourier ideal-trefoil centerline, performs a Biot–Savart cutoff-energy scan, extracts the logarithmic coefficient \(A_K\), evaluates the no-contact core-radius closure

\[
\frac{a_{\rm nc}}{r_c}=\sqrt{4\pi A_K},
\]

and then computes the spherical-cell closure estimate

\[
\alpha_{\rm cell}
=
\frac{2}{
\mathcal E_0
\left[
1-
\dfrac{\pi}{4\mathcal E_0^2}
\left(
1+\dfrac{3}{4\mathcal L_K}
+\dfrac{1}{16\mathcal L_K^2}
\right)
\right]
}.
\]

The code is intended to reproduce the numerical coefficient extraction and tables in the manuscript/supplement. It does not replace the analytic assumptions stated in the appendices.

---

## 1. Requirements

Python 3.10 or newer is recommended.

Install the required packages:

```bash
python -m pip install numpy pandas matplotlib
```
 
No compiled C++ extension, GPU backend, Torch, or SST-specific package is required.

---

## 2. Downloading `ideal.txt`

The ideal-knot Fourier coefficient database can be downloaded from the Knot Atlas:

```text
https://katlas.org/images/d/d2/Ideal.txt.gz
```

### Linux / macOS / WSL

```bash
curl -L -o Ideal.txt.gz https://katlas.org/images/d/d2/Ideal.txt.gz
gunzip -k Ideal.txt.gz
mv Ideal.txt ideal.txt
```

### Windows PowerShell

```powershell
Invoke-WebRequest -Uri "https://katlas.org/images/d/d2/Ideal.txt.gz" -OutFile "Ideal.txt.gz"
```

Then decompress it with 7-Zip, WinRAR, or another gzip-capable archive utility, and rename the extracted file to:

```text
ideal.txt
```

Place `ideal.txt` in the same directory as:

```text
reproduce_alpha_cell_closure.py
```

The script can run without `ideal.txt`, but then it uses the embedded 30-mode fallback trefoil. For manuscript-grade reproduction, use the downloaded `ideal.txt`.

---

## 3. Basic run

With the embedded fallback coefficients:

```bash
python reproduce_alpha_cell_closure.py
```

With the Knot Atlas `ideal.txt` database:

```bash
python reproduce_alpha_cell_closure.py --ideal-txt ideal.txt --knot-id 3:1:1
```

For a somewhat stronger numerical run:

```bash
python reproduce_alpha_cell_closure.py --ideal-txt ideal.txt --knot-id 3:1:1 --n-geom 4000 --n-int 4000 --a-count 24
```

For a heavier run:

```bash
python reproduce_alpha_cell_closure.py --ideal-txt ideal.txt --knot-id 3:1:1 --n-geom 8000 --n-int 8000 --a-count 24 --block 512
```

The Biot–Savart scan is \(O(N^2)\), so the heavier run can take noticeably longer.

---

## 4. Output files

By default, the script writes results to:

```text
outputs_alpha_cell/
```

Expected files:

```text
geometry_summary.csv
bs_scan.csv
local_A_curve.csv
fit_summary.csv
closure_summary.csv
alpha_cell_summary.csv
local_A_curve.png
local_A_curve.pdf
```

The most important files are:

```text
closure_summary.csv
alpha_cell_summary.csv
```

`closure_summary.csv` contains the extracted \(A_K\) and the no-contact closure ratio:

\[
a_{\rm nc}/r_c=\sqrt{4\pi A_K}.
\]

`alpha_cell_summary.csv` contains the spherical-cell correction factor \(\Xi_{\rm sph}\), the effective aspect ratio \(\mathcal E_{\rm eff}\), and the predicted \(\alpha_{\rm cell}\).

---

## 5. Key quantities

The script reports:

```text
A_K_used
A_required_1_over_4pi
A_ratio_to_required
a_nc_over_r_core
Xi_sph
E_eff
alpha_cell
alpha_cell_inverse
relative_error_vs_CODATA_2022
v_core_pred_m_per_s
```

The robust theoretical target for the trefoil Biot–Savart coefficient is:

\[
A_K \to \frac{1}{4\pi}.
\]

When this holds,

\[
a_{\rm nc}/r_c \to 1.
\]

The spherical pressure-cell factor is evaluated as

\[
\Xi_{\rm sph}
=
1+\frac{3}{4\mathcal L_K}
+\frac{1}{16\mathcal L_K^2},
\]

where \(\mathcal L_K=L_K/D\) is the ideal-trefoil ropelength.

---

## 6. Optional finite-resolution variant

By default, the fine-structure estimate uses the theorem-limit core factor:

\[
\pi^2 A_K \to \frac{\pi}{4}.
\]

This avoids using noisy finite-resolution deviations in \(A_K\) as if they were physical.

To force the finite-resolution value \(\pi^2 A_K\) into the alpha-cell estimate, run:

```bash
python reproduce_alpha_cell_closure.py --ideal-txt ideal.txt --knot-id 3:1:1 --use-A-for-alpha
```

This option is diagnostic only. The manuscript formula should use the theorem-limit \(\pi/4\), unless a separate convergence study justifies using finite-resolution \(A_K\).

---

## 7. Reproducibility notes

Recommended manuscript/supplement wording:

> The supplied Python script reproduces the Biot–Savart coefficient extraction and the numerical evaluation of the spherical-cell closure formula. The code is not used as evidence for the analytic assumptions; those assumptions are stated separately in the appendices.

Recommended citation for the ideal-knot data source:

> Knot Atlas ideal knot data, `Ideal.txt.gz`, available from `https://katlas.org/images/d/d2/Ideal.txt.gz`.

For a journal submission, archive the exact version of `ideal.txt`, this script, and the generated CSV outputs together, preferably in a DOI-backed repository such as Zenodo or OSF.

---

## 8. Quick sanity check

A successful run should produce values qualitatively close to:

\[
A_K \approx \frac{1}{4\pi},
\qquad
a_{\rm nc}/r_c \approx 1,
\]

and

\[
\alpha_{\rm cell}^{-1}
\approx
137.0359992
\]

when the theorem-limit \(\pi/4\) and ideal-trefoil ropelength are used.

Small deviations in the extracted finite-resolution \(A_K\) are expected; they depend on Fourier truncation, integration resolution, cutoff range, and plateau selection.