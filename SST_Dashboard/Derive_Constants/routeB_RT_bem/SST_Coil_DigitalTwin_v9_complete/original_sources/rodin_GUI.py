import numpy as np
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

MU0_4PI = 1e-7  # μ0/(4π)


# ----------------------------
# Physics: Biot–Savart on grid
# ----------------------------
def biot_savart_wire_grid(X, Y, Z, polyline, current, r_softening=1e-6):
    Bx = np.zeros_like(X, dtype=np.float64)
    By = np.zeros_like(Y, dtype=np.float64)
    Bz = np.zeros_like(Z, dtype=np.float64)

    p0 = polyline[:-1]
    p1 = polyline[1:]
    dl = p1 - p0
    mid = 0.5 * (p0 + p1)

    target = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)

    for i in range(len(dl)):
        dL = dl[i]
        r_vec = target - mid[i]
        r_sq = np.sum(r_vec * r_vec, axis=1) + (r_softening ** 2)
        r_cubed = r_sq * np.sqrt(r_sq)

        cross = np.cross(np.broadcast_to(dL, r_vec.shape), r_vec)
        factor = (MU0_4PI * current) / r_cubed
        Bseg = cross * factor[:, None]

        Bx += Bseg[:, 0].reshape(X.shape)
        By += Bseg[:, 1].reshape(Y.shape)
        Bz += Bseg[:, 2].reshape(Z.shape)

    return Bx, By, Bz


# ---------------------------------------------
# Geometry: torus-knot with per-cell phase shift
# ---------------------------------------------
def torus_knot_cellphase_polyline(
        R_major, r_minor, p, q,
        n_points=1200,
        turns=1,
        cell_phase_frac=0.0,   # 0, 1/phases, 2/phases ...
        mirror=False,          # CCW partner: phi -> -phi
        z_offset=0.0,
        theta_offset=0.0,      # rigid toroidal rotation for node shifts (radians)
):
    p = int(max(1, p))
    q = int(max(1, q))
    turns = int(max(1, turns))

    t = np.linspace(0.0, 2.0 * np.pi * turns, int(max(120, n_points)))

    dt_cell = float(cell_phase_frac) * (2.0 * np.pi / q)  # per-cell sector
    tp = t + dt_cell

    theta = p * tp + float(theta_offset)
    phi_t = q * tp
    if mirror:
        phi_t = -phi_t

    x = (R_major + r_minor * np.cos(phi_t)) * np.cos(theta)
    y = (R_major + r_minor * np.cos(phi_t)) * np.sin(theta)
    z = r_minor * np.sin(phi_t) + z_offset

    return np.stack([x, y, z], axis=1)


def build_coils(
        R_major, r_minor, p, q,
        phases=3,
        turns=1,
        points=1200,
        separate_families=True,
        gap=0.05,
        ccw_start_mode="Same",  # "Same" or "Opposite (1->19)"
):
    phases = int(max(1, phases))
    q = int(max(1, q))

    cell_fracs = np.arange(phases, dtype=float) / phases

    z_cw = -gap / 2.0 if separate_families else 0.0
    z_ccw = +gap / 2.0 if separate_families else 0.0

    theta_offset_ccw = np.pi if ccw_start_mode.startswith("Opposite") else 0.0

    colors_cw = ["crimson", "darkorange", "gold", "tomato", "sienna", "khaki"]
    colors_ccw = ["royalblue", "navy", "teal", "deepskyblue", "slateblue", "cyan"]

    coils = []

    for i, cf in enumerate(cell_fracs):
        pts = torus_knot_cellphase_polyline(
            R_major, r_minor, p, q,
            n_points=points, turns=turns,
            cell_phase_frac=cf,
            mirror=False,
            z_offset=z_cw,
            theta_offset=0.0
        )
        coils.append((pts, colors_cw[i % len(colors_cw)], "-"))

    for i, cf in enumerate(cell_fracs):
        pts = torus_knot_cellphase_polyline(
            R_major, r_minor, p, q,
            n_points=points, turns=turns,
            cell_phase_frac=cf,
            mirror=True,
            z_offset=z_ccw,
            theta_offset=theta_offset_ccw
        )
        coils.append((pts, colors_ccw[i % len(colors_ccw)], "--"))

    return coils


# ----------------------------
# Scrollable sidebar frame
# ----------------------------
class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, width=430):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=width)
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.inner = ttk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.inner_id, width=e.width))

        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.inner)

    def _bind_mousewheel(self, widget):
        widget.bind("<Enter>", lambda e: self._activate_mousewheel())
        widget.bind("<Leave>", lambda e: self._deactivate_mousewheel())

    def _activate_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _deactivate_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")

    def _on_mousewheel_linux(self, event):
        self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")


# ----------------------------
# Collapsible section widget
# ----------------------------
class CollapsibleSection(ttk.Frame):
    def __init__(self, parent, title, initially_open=True):
        super().__init__(parent)
        self._open = tk.BooleanVar(value=initially_open)

        header = ttk.Frame(self)
        header.pack(fill=tk.X)
        self.btn = ttk.Button(header, width=2, command=self.toggle)
        self.btn.pack(side=tk.LEFT)
        ttk.Label(header, text=title, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(6, 0))

        self.body = ttk.Frame(self)
        self.body.pack(fill=tk.X, pady=(4, 8))
        self._refresh()

    def toggle(self):
        self._open.set(not self._open.get())
        self._refresh()

    def _refresh(self):
        if self._open.get():
            self.btn.configure(text="▼")
            self.body.pack(fill=tk.X, pady=(4, 8))
        else:
            self.btn.configure(text="►")
            self.body.forget()


# ----------------------------
# GUI Application
# ----------------------------
class SSTCoilGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SST Torus-Knot Coil GUI — fixes p,q commit + CCW node 1→19")
        self.geometry("1380x800")

        self._after_id = None
        self._layout_heatmap = None
        self._cbar = None

        # Vars
        self.var_quality = tk.StringVar(value="Normal")

        self.var_major_d_cm = tk.DoubleVar(value=9.8)
        self.var_minor_r_mm = tk.DoubleVar(value=12.0)

        self.var_p = tk.IntVar(value=5)
        self.var_q = tk.IntVar(value=12)
        self.var_turns = tk.IntVar(value=1)
        self.var_phases = tk.IntVar(value=3)
        self.var_points = tk.IntVar(value=450)

        self.var_separate = tk.BooleanVar(value=True)
        self.var_gap_cm = tk.DoubleVar(value=5.0)
        self.var_ccw_start = tk.StringVar(value="Same")

        self.var_current = tk.DoubleVar(value=2000.0)
        self.var_bounds_cm = tk.DoubleVar(value=30.0)
        self.var_grid_res = tk.IntVar(value=26)
        self.var_soft_um = tk.DoubleVar(value=10.0)

        self.var_arrow_scale = tk.DoubleVar(value=0.05)
        self.var_quiver_step = tk.IntVar(value=2)
        self.var_null_threshold = tk.DoubleVar(value=0.60)
        self.var_b_floor = tk.DoubleVar(value=1e-9)

        self.var_show_quiver = tk.BooleanVar(value=True)
        self.var_show_null = tk.BooleanVar(value=True)
        self.var_show_heatmap = tk.BooleanVar(value=True)

        self.var_autoupdate = tk.BooleanVar(value=False)

        # widget refs for commit (critical!)
        self._spin_refs = {}
        self._entry_refs = {}

        self._build_controls()
        self._build_plot()
        self._apply_quality_preset(initial=True)
        self.update_plot()

    # ----------------------------
    # helpers
    # ----------------------------
    def _add_labeled_entry(self, parent, label, var, key=None):
        block = ttk.Frame(parent); block.pack(fill=tk.X, pady=3)
        ttk.Label(block, text=label).pack(anchor="w")
        e = ttk.Entry(block, textvariable=var)
        e.pack(fill=tk.X)
        if key is not None:
            self._entry_refs[key] = e
        return e

    def _add_labeled_spin(self, parent, label, var, from_, to_, increment=1, key=None):
        block = ttk.Frame(parent); block.pack(fill=tk.X, pady=3)
        ttk.Label(block, text=label).pack(anchor="w")
        sp = ttk.Spinbox(block, from_=from_, to=to_, increment=increment, textvariable=var)
        sp.pack(fill=tk.X)
        if key is not None:
            self._spin_refs[key] = sp
        return sp

    def _add_slider(self, parent, label, var, from_, to_, fmt_func):
        block = ttk.Frame(parent); block.pack(fill=tk.X, pady=6)
        top = ttk.Frame(block); top.pack(fill=tk.X)
        ttk.Label(top, text=label).pack(side=tk.LEFT)
        val_lbl = ttk.Label(top, text=""); val_lbl.pack(side=tk.RIGHT)

        def _update(*_):
            try: v = float(var.get())
            except Exception: v = 0.0
            val_lbl.configure(text=fmt_func(v))

        s = ttk.Scale(block, from_=from_, to=to_, orient="horizontal", variable=var)
        s.pack(fill=tk.X)
        var.trace_add("write", lambda *_: _update())
        _update()
        return s

    def _quality_map(self):
        return {
            "Low":    {"grid_res": 18, "points": 220, "phases": 1, "quiver_step": 3},
            "Normal": {"grid_res": 26, "points": 450, "phases": 3, "quiver_step": 2},
            "High":   {"grid_res": 38, "points": 900, "phases": 3, "quiver_step": 2},
        }

    def _apply_quality_preset(self, initial=False):
        preset = self._quality_map().get(self.var_quality.get(), self._quality_map()["Normal"])
        self.var_grid_res.set(preset["grid_res"])
        self.var_points.set(preset["points"])
        self.var_phases.set(preset["phases"])
        self.var_quiver_step.set(preset["quiver_step"])
        if not initial:
            self.lbl_status.config(text=f"Applied quality: {self.var_quality.get()}")

    def _on_quality_change(self, *_):
        self._apply_quality_preset()
        if self.var_autoupdate.get():
            self._schedule_update()

    # CRITICAL: commit typed spinbox/entry text into variables BEFORE computing
    def _commit_inputs(self):
        def _safe_int(widget, fallback):
            try:
                return int(float(widget.get()))
            except Exception:
                return fallback

        def _safe_float(widget, fallback):
            try:
                return float(widget.get())
            except Exception:
                return fallback

        # Spinboxes
        if "p" in self._spin_refs:
            self.var_p.set(max(1, _safe_int(self._spin_refs["p"], int(self.var_p.get()))))
        if "q" in self._spin_refs:
            self.var_q.set(max(1, _safe_int(self._spin_refs["q"], int(self.var_q.get()))))
        if "turns" in self._spin_refs:
            self.var_turns.set(max(1, _safe_int(self._spin_refs["turns"], int(self.var_turns.get()))))
        if "phases" in self._spin_refs:
            self.var_phases.set(max(1, _safe_int(self._spin_refs["phases"], int(self.var_phases.get()))))
        if "points" in self._spin_refs:
            self.var_points.set(max(120, _safe_int(self._spin_refs["points"], int(self.var_points.get()))))
        if "grid_res" in self._spin_refs:
            self.var_grid_res.set(max(10, _safe_int(self._spin_refs["grid_res"], int(self.var_grid_res.get()))))
        if "quiver_step" in self._spin_refs:
            self.var_quiver_step.set(max(1, _safe_int(self._spin_refs["quiver_step"], int(self.var_quiver_step.get()))))

        # Entries
        if "major_d" in self._entry_refs:
            self.var_major_d_cm.set(max(0.1, _safe_float(self._entry_refs["major_d"], float(self.var_major_d_cm.get()))))
        if "minor_r" in self._entry_refs:
            self.var_minor_r_mm.set(max(0.1, _safe_float(self._entry_refs["minor_r"], float(self.var_minor_r_mm.get()))))
        if "soft_um" in self._entry_refs:
            self.var_soft_um.set(max(0.0, _safe_float(self._entry_refs["soft_um"], float(self.var_soft_um.get()))))
        if "arrow_scale" in self._entry_refs:
            self.var_arrow_scale.set(max(0.001, _safe_float(self._entry_refs["arrow_scale"], float(self.var_arrow_scale.get()))))

    # ----------------------------
    # plot area
    # ----------------------------
    def _build_plot(self):
        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.fig = plt.Figure(figsize=(9.6, 6.9), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._ensure_axes(self.var_show_heatmap.get())

    def _ensure_axes(self, show_heatmap: bool):
        show_heatmap = bool(show_heatmap)
        if self._layout_heatmap == show_heatmap:
            return

        if self._cbar is not None:
            try: self._cbar.remove()
            except Exception: pass
            self._cbar = None

        self.fig.clf()
        if show_heatmap:
            self.ax3d = self.fig.add_subplot(1, 2, 1, projection="3d")
            self.ax2d = self.fig.add_subplot(1, 2, 2)
        else:
            self.ax3d = self.fig.add_subplot(1, 1, 1, projection="3d")
            self.ax2d = None

        self._layout_heatmap = show_heatmap

    # ----------------------------
    # sidebar
    # ----------------------------
    def _build_controls(self):
        sidebar = ttk.Frame(self)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        scroll = ScrollableFrame(sidebar, width=440)
        scroll.pack(fill=tk.BOTH, expand=True)
        frm = scroll.inner

        # quality
        qb = ttk.Frame(frm); qb.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(qb, text="Quality preset", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        qrow = ttk.Frame(qb); qrow.pack(fill=tk.X, pady=3)
        ttk.Combobox(qrow, textvariable=self.var_quality, values=["Low", "Normal", "High"], state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(qrow, text="Apply", command=self._apply_quality_preset).pack(side=tk.RIGHT, padx=(6, 0))
        self.var_quality.trace_add("write", self._on_quality_change)

        sec_geom = CollapsibleSection(frm, "Geometry", True); sec_geom.pack(fill=tk.X)
        sec_trap = CollapsibleSection(frm, "Trap / CW–CCW Relation", True); sec_trap.pack(fill=tk.X)
        sec_compute = CollapsibleSection(frm, "Compute", True); sec_compute.pack(fill=tk.X)
        sec_viz = CollapsibleSection(frm, "Viz", True); sec_viz.pack(fill=tk.X)

        g = sec_geom.body
        self._add_labeled_entry(g, "Major diameter [cm] (default 9.8)", self.var_major_d_cm, key="major_d")
        self._add_labeled_entry(g, "Minor radius [mm]", self.var_minor_r_mm, key="minor_r")
        self._add_labeled_spin(g, "p", self.var_p, 1, 200, key="p")
        self._add_labeled_spin(g, "q", self.var_q, 1, 200, key="q")
        self._add_labeled_spin(g, "Turns", self.var_turns, 1, 50, key="turns")
        self._add_labeled_spin(g, "Phases per cell (0,1/N,..)", self.var_phases, 1, 12, key="phases")
        self._add_labeled_spin(g, "Polyline points per phase", self.var_points, 150, 6000, increment=50, key="points")

        t = sec_trap.body
        ttk.Checkbutton(t, variable=self.var_separate, text="Separate CW and CCW families along z (gap)").pack(anchor="w", pady=(0, 6))
        self._add_slider(t, "Gap [cm] (hot)", self.var_gap_cm, 0.0, 25.0, lambda v: f"{v:.2f} cm")
        block = ttk.Frame(t); block.pack(fill=tk.X, pady=3)
        ttk.Label(block, text="CCW start relative to CW").pack(anchor="w")
        ttk.Combobox(block, textvariable=self.var_ccw_start, values=["Same", "Opposite (1->19)"], state="readonly").pack(fill=tk.X)

        c = sec_compute.body
        self._add_slider(c, "Current [A] (hot)", self.var_current, 0.0, 5000.0, lambda v: f"{v:.0f} A")
        self._add_slider(c, "Bounds [cm] (hot)", self.var_bounds_cm, 5.0, 80.0, lambda v: f"{v:.1f} cm")
        self._add_labeled_spin(c, "Grid res (quality controls this)", self.var_grid_res, 10, 72, key="grid_res")
        self._add_labeled_entry(c, "Softening [µm]", self.var_soft_um, key="soft_um")

        v = sec_viz.body
        self._add_labeled_entry(v, "Arrow scale", self.var_arrow_scale, key="arrow_scale")
        self._add_labeled_spin(v, "Quiver step (quality controls this)", self.var_quiver_step, 1, 10, key="quiver_step")
        self._add_slider(v, "Null threshold (hot)", self.var_null_threshold, 0.0, 0.95, lambda x: f"{x:.2f}")
        ttk.Checkbutton(v, variable=self.var_show_quiver, text="Show quiver").pack(anchor="w", pady=2)
        ttk.Checkbutton(v, variable=self.var_show_null, text="Show null proxy scatter (1/|B|)").pack(anchor="w", pady=2)
        ttk.Checkbutton(v, variable=self.var_show_heatmap, text="Show mid-plane heatmap").pack(anchor="w", pady=2)

        bottom = ttk.Frame(frm); bottom.pack(fill=tk.X, pady=(10, 8))
        ttk.Button(bottom, text="Update", command=self.update_plot).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Checkbutton(bottom, variable=self.var_autoupdate, text="Auto").pack(side=tk.RIGHT)

        self.lbl_status = ttk.Label(frm, text="Ready.")
        self.lbl_status.pack(anchor="w", pady=(0, 8))

        self._bind_autoupdate()

    def _bind_autoupdate(self):
        watch = [
            self.var_quality,
            self.var_major_d_cm, self.var_minor_r_mm,
            self.var_p, self.var_q, self.var_turns, self.var_phases, self.var_points,
            self.var_separate, self.var_gap_cm, self.var_ccw_start,
            self.var_current, self.var_bounds_cm, self.var_grid_res, self.var_soft_um,
            self.var_arrow_scale, self.var_quiver_step, self.var_null_threshold,
            self.var_show_quiver, self.var_show_null, self.var_show_heatmap,
        ]
        for v in watch:
            v.trace_add("write", lambda *_: self._schedule_update())

    def _schedule_update(self):
        if not self.var_autoupdate.get():
            return
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(250, self.update_plot)

    # ----------------------------
    # compute + render
    # ----------------------------
    def update_plot(self):
        self.lbl_status.config(text="Computing…")
        self.update_idletasks()

        # commit typed inputs (THIS fixes your p,q issue)
        self._commit_inputs()

        # read vars
        major_d = float(self.var_major_d_cm.get()) * 1e-2
        R_major = 0.5 * major_d
        r_minor = float(self.var_minor_r_mm.get()) * 1e-3

        p = int(self.var_p.get())
        q = int(self.var_q.get())
        turns = int(self.var_turns.get())
        phases = int(self.var_phases.get())
        points = int(self.var_points.get())

        separate = bool(self.var_separate.get())
        gap = float(self.var_gap_cm.get()) * 1e-2
        ccw_start = str(self.var_ccw_start.get())

        I = float(self.var_current.get())
        bounds = float(self.var_bounds_cm.get()) * 1e-2
        res = int(self.var_grid_res.get())
        r_soft = float(self.var_soft_um.get()) * 1e-6

        arrow_scale = float(self.var_arrow_scale.get())
        quiver_step = int(self.var_quiver_step.get())
        null_thr = float(self.var_null_threshold.get())
        b_floor = float(self.var_b_floor.get())

        show_quiver = bool(self.var_show_quiver.get())
        show_null = bool(self.var_show_null.get())
        show_heatmap = bool(self.var_show_heatmap.get())

        self._ensure_axes(show_heatmap)

        # basic clamps
        r_minor = max(1e-6, min(r_minor, 0.95 * max(1e-9, R_major)))
        bounds = max(0.02, bounds)
        res = max(10, min(res, 72))
        points = int(max(120, min(points, 6000)))
        phases = int(max(1, min(phases, 12)))

        coils = build_coils(
            R_major, r_minor, p, q,
            phases=phases, turns=turns, points=points,
            separate_families=separate, gap=gap,
            ccw_start_mode=ccw_start
        )

        x = np.linspace(-bounds, bounds, res)
        y = np.linspace(-bounds, bounds, res)
        z = np.linspace(-bounds, bounds, res)
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

        Bx_tot = np.zeros_like(X); By_tot = np.zeros_like(Y); Bz_tot = np.zeros_like(Z)
        for pts, _, _ in coils:
            bx, by, bz = biot_savart_wire_grid(X, Y, Z, pts, I, r_softening=max(1e-12, r_soft))
            Bx_tot += bx; By_tot += by; Bz_tot += bz

        B_mag = np.linalg.norm(np.stack([Bx_tot, By_tot, Bz_tot], axis=-1), axis=-1)
        null_map = 1.0 / (B_mag + b_floor)
        null_map /= np.max(null_map)

        # clear axes + colorbar
        self.ax3d.cla()
        if self.ax2d is not None:
            self.ax2d.cla()
        if self._cbar is not None:
            try: self._cbar.remove()
            except Exception: pass
            self._cbar = None

        # 3D
        self.ax3d.set_xlabel("X [m]")
        self.ax3d.set_ylabel("Y [m]")
        self.ax3d.set_zlabel("Z [m]")
        self.ax3d.set_xlim(-bounds, bounds)
        self.ax3d.set_ylim(-bounds, bounds)
        self.ax3d.set_zlim(-bounds, bounds)

        for pts, col, ls in coils:
            self.ax3d.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=col, linestyle=ls, lw=1.35, alpha=0.9)

        if show_null:
            mask = null_map > null_thr
            if np.any(mask):
                self.ax3d.scatter(X[mask], Y[mask], Z[mask], c=null_map[mask], cmap="inferno", s=10, alpha=0.22)

        if show_quiver:
            step = max(1, quiver_step)
            xs = X[::step, ::step, ::step]
            ys = Y[::step, ::step, ::step]
            zs = Z[::step, ::step, ::step]
            bxs = Bx_tot[::step, ::step, ::step]
            bys = By_tot[::step, ::step, ::step]
            bzs = Bz_tot[::step, ::step, ::step]
            self.ax3d.quiver(xs, ys, zs, bxs, bys, bzs, length=arrow_scale, normalize=True, alpha=0.32, color="gray")

        self.ax3d.view_init(elev=20, azim=40)

        # heatmap
        if self.ax2d is not None:
            k0 = int(np.argmin(np.abs(z - 0.0)))
            Nmid = null_map[:, :, k0]
            im = self.ax2d.imshow(
                Nmid.T, origin="lower",
                extent=[-bounds, bounds, -bounds, bounds],
                aspect="equal"
            )
            self.ax2d.set_title("Mid-plane z≈0: 1/|B| (proxy)")
            self.ax2d.set_xlabel("X [m]")
            self.ax2d.set_ylabel("Y [m]")
            self._cbar = self.fig.colorbar(im, ax=self.ax2d, fraction=0.046, pad=0.04)

        n_nodes = phases * q
        self.fig.suptitle(
            f"Quality={self.var_quality.get()} | T({p},{q}) | Ø={major_d*100:.2f} cm | phases={phases} (nodes={n_nodes}) | CCW={ccw_start}",
            fontsize=10
        )
        self.fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.95])
        self.canvas.draw()

        self.lbl_status.config(text=f"Done. Used p={p}, q={q}, turns={turns} (nodes={n_nodes}).")


if __name__ == "__main__":
    app = SSTCoilGUI()
    app.mainloop()