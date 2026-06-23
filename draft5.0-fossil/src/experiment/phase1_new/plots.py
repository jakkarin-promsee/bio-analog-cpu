"""Phase 1 (new) shared plots — the 'see it with your eyes' deliverables. Headless (Agg backend).

The rung-0 story is told by three pictures, top to bottom:
  surface_heatmaps : the raw output surface (both channels) over the input square.
  region_map       : the SAME surface cut into its linear regions, with the creases drawn on top
                     -> "each colored tile is one plane y = ax + b".
  slices           : a few horizontal cuts -> each is a piecewise-LINE: straight segments (y=ax+b)
                     joined at kinks (the creases). The most literal view of the relation.
target_vs_fit is the reachability picture (step-2): target vs best-fit, heatmap + real 3-D shape.
"""

import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402


def surface_heatmaps(Z0, Z1, xs, ys, title, path, creases=None):
    """Both output channels as heatmaps over the 2-D input grid; saved to `path`. If `creases` is
    given, the same lines are drawn on BOTH panels — the point being that out[0] and out[1] are read
    off the very same L2 cuts (one segmentation, two voices)."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, Z, name in zip(axes, (Z0, Z1), ("out[0]", "out[1]")):
        im = ax.imshow(Z, origin="lower", aspect="auto",
                       extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="viridis")
        if creases:
            _draw_creases(ax, creases, xs, ys)
        ax.set_title(f"{title} · {name}")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def lines_on_surfaces(name, T, P, lines, xs, ys, path, resid=None):
    """STRESS TEST: where did the best-fit put its three L2 lines? target+lines | best-fit+lines.
    `lines` = list of (a, b, c) pulled from the fitted L2 weights. Reveals the *mechanism* behind a
    fit — why xor can't be carved by one line-set, and the gaussian's concurrent 3-lines -> wedges."""
    vmin = float(min(T.min(), P.min()))
    vmax = float(max(T.max(), P.max()))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, Z, lab in zip(axes, (T, P), ("target", "best-fit (real ALU)")):
        im = ax.imshow(Z, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                       vmin=vmin, vmax=vmax, cmap="viridis", aspect="auto")
        _draw_creases(ax, lines, xs, ys)
        ax.set_title(f"{name} · {lab}  + its 3 L2 lines")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    if resid is not None:
        fig.suptitle(f"{name}: the three lines under stress  (norm-residual {resid:.3f})", y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def _draw_creases(ax, creases, xs, ys):
    """Draw each line a*x1 + b*x2 + c = 0 across the domain (dashed white). A near-zero (a, b) means
    a dead neuron with no line in-plane — skip it."""
    x0, x1 = xs[0], xs[-1]
    y0, y1 = ys[0], ys[-1]
    for (a, b, c) in creases:
        if (a * a + b * b) ** 0.5 < 1e-9:       # dead neuron: no line
            continue
        if abs(b) < 1e-12:                      # vertical line  x1 = -c/a
            xv = -c / a
            ax.plot([xv, xv], [y0, y1], "w--", lw=1.5, alpha=0.9)
        else:                                   # x2 = -(a*x1 + c) / b
            xx = np.array([x0, x1])
            yy = -(a * xx + c) / b
            ax.plot(xx, yy, "w--", lw=1.5, alpha=0.9)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)


def _line_label(a, b, c):
    """Human-readable 'a·x1 + b·x2 + c' with zero terms dropped."""
    parts = []
    if a:
        parts.append(f"{a:g}·x1")
    if b:
        parts.append(f"{b:g}·x2")
    body = " + ".join(parts) if parts else "0"
    return f"{body} {c:+g}"


def relu_neurons(creases, xs, ys, title, path):
    """One panel per L2 neuron: the line it draws + the ramp it makes (0 = silent side, bright =
    active side). `creases` = list of (a, b, c); neuron output = ReLU(a·x1 + b·x2 + c). This is L2's
    whole job — *region segmentation* — made literal: three activation units = three lines."""
    X1, X2 = np.meshgrid(xs, ys)
    n = len(creases)
    fig, axes = plt.subplots(1, n, figsize=(4.3 * n, 4.2))
    if n == 1:
        axes = [axes]
    for j, (ax, (a, b, c)) in enumerate(zip(axes, creases)):
        ramp = np.maximum(a * X1 + b * X2 + c, 0.0)
        im = ax.imshow(ramp, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                       cmap="magma", aspect="auto")
        _draw_creases(ax, [(a, b, c)], xs, ys)
        ax.set_title(f"neuron {j}:  ReLU({_line_label(a, b, c)})", fontsize=9)
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def activation_zones(creases, xs, ys, title, path):
    """The three lines overlaid, with the plane colored by HOW MANY of the L2 ReLUs are ON (0..3).
    Replaces the hard-to-read N-color region soup with a meaningful few-level map: the 3 lines are
    the stars, and the shading shows the segmentation 'depth' they build up."""
    X1, X2 = np.meshgrid(xs, ys)
    n = len(creases)
    depth = np.zeros_like(X1)
    for (a, b, c) in creases:
        depth += (a * X1 + b * X2 + c > 0).astype(float)
    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = plt.get_cmap("YlGnBu", n + 1)
    im = ax.imshow(depth, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                   cmap=cmap, vmin=-0.5, vmax=n + 0.5, aspect="auto", interpolation="nearest")
    _draw_creases(ax, creases, xs, ys)
    ax.set_title(title)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    cbar = fig.colorbar(im, ax=ax, ticks=range(n + 1), fraction=0.046, pad=0.04)
    cbar.set_label("# of the 3 L2 ReLUs active here")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def region_map(labels, n_regions, xs, ys, title, path, creases=None):
    """The carve: each linear region a flat color, creases drawn on top. `labels` from
    metrics.region_labels (NaN = boundary, rendered blank)."""
    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = plt.get_cmap("tab10", max(n_regions, 1)).copy()
    cmap.set_bad("white")
    im = ax.imshow(labels, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                   cmap=cmap, vmin=-0.5, vmax=n_regions - 0.5, aspect="auto",
                   interpolation="nearest")
    if creases:
        _draw_creases(ax, creases, xs, ys)
    ax.set_title(title)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    cbar = fig.colorbar(im, ax=ax, ticks=range(n_regions), fraction=0.046, pad=0.04)
    cbar.set_label("region  (each tile = one plane y = a·x1 + b·x2 + c)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def region_map_row(panels, xs, ys, title, path):
    """A row of region maps for comparison. `panels` = list of (labels, n_regions, sublabel).
    Each panel is colored by its OWN region count (counts differ across draws — that's the point)."""
    n = len(panels)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.4))
    if n == 1:
        axes = [axes]
    for ax, (labels, k, sub) in zip(axes, panels):
        cmap = plt.get_cmap("tab10", max(k, 1)).copy()
        cmap.set_bad("white")
        ax.imshow(labels, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                  cmap=cmap, vmin=-0.5, vmax=max(k, 1) - 0.5, aspect="auto", interpolation="nearest")
        ax.set_title(sub, fontsize=10)
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def slices(Z, xs, ys, at_rows, title, path, ylabel="out[0]"):
    """A few horizontal cuts y(x1) at fixed x2 -> each a piecewise-LINE (the y=ax+b segments)."""
    fig, ax = plt.subplots(figsize=(7, 5))
    for c in at_rows:
        j = int(np.argmin(np.abs(np.asarray(ys) - c)))
        ax.plot(xs, Z[j, :], marker="", lw=2, label=f"x2 = {ys[j]:+.2f}")
    ax.set_xlabel("x1")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def target_vs_fit(name, T, P, xs, ys, path, resid=None):
    """2x2 in the target's REAL units: top = target | best-fit heatmaps; bottom = target | best-fit
    3-D surfaces (the honest shape). Compare left vs right to read how well the atom fits."""
    X1, X2 = np.meshgrid(xs, ys)
    vmin = float(min(T.min(), P.min()))
    vmax = float(max(T.max(), P.max()))
    fig = plt.figure(figsize=(12, 9))
    for i, (Z, lab) in enumerate([(T, "target"), (P, "best-fit (real ALU)")]):
        ax = fig.add_subplot(2, 2, i + 1)
        im = ax.imshow(Z, origin="lower", aspect="auto", vmin=vmin, vmax=vmax,
                       extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="viridis")
        ax.set_title(f"{name} · {lab}")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    for i, (Z, lab) in enumerate([(T, "target"), (P, "best-fit (real ALU)")]):
        ax = fig.add_subplot(2, 2, i + 3, projection="3d")
        ax.plot_surface(X1, X2, Z, cmap="viridis", vmin=vmin, vmax=vmax,
                        rstride=3, cstride=3, linewidth=0, antialiased=True)
        ax.set_zlim(vmin, vmax)
        ax.set_title(f"{name} · {lab} (3-D)")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        ax.view_init(elev=28, azim=-58)
    if resid is not None:
        fig.suptitle(f"{name}:  norm-residual = {resid:.3f}", y=0.99, fontsize=12)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def trend(x, series, xlabel, ylabel, title, path, logx=False, logy=False, bands=None, vlines=None):
    """Line plot of one or more series vs x. `series` = {label: y-values}. Optional log axes, shaded
    horizontal `bands` = list of (lo, hi, color, label) (e.g. the healthy gain band), and `vlines` =
    list of (x, label) (e.g. the measured knee)."""
    fig, ax = plt.subplots(figsize=(7.5, 5))
    if bands:
        for lo, hi, color, lab in bands:
            ax.axhspan(lo, hi, color=color, alpha=0.15, label=lab)
    for label, y in series.items():
        ax.plot(x, y, marker="o", lw=2, label=label)
    if vlines:
        for xv, lab in vlines:
            ax.axvline(xv, ls=":", color="k", alpha=0.7)
            ax.text(xv, ax.get_ylim()[1], f" {lab}", va="top", fontsize=8)
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def cap_panels(surfaces, lines_list, sublabels, xs, ys, title, path):
    """One Ganglion under a tightening cap, left (loose) to right (tight). `surfaces` = out0 arrays on
    a SHARED color scale (so the amplitude crush is visible), each with its (capped) 3 lines drawn —
    so you watch the lines slide AND the surface go flat at the same time."""
    n = len(surfaces)
    fig, axes = plt.subplots(1, n, figsize=(4.0 * n, 4.2))
    if n == 1:
        axes = [axes]
    vmin = float(min(s.min() for s in surfaces))
    vmax = float(max(s.max() for s in surfaces))
    im = None
    for ax, S, lines, lab in zip(axes, surfaces, lines_list, sublabels):
        im = ax.imshow(S, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                       vmin=vmin, vmax=vmax, cmap="viridis", aspect="auto")
        _draw_creases(ax, lines, xs, ys)
        ax.set_title(lab, fontsize=9)
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
    fig.colorbar(im, ax=list(axes), fraction=0.02, pad=0.01, label="out0 (shared scale)")
    fig.suptitle(title, y=1.02)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def gain_zone_map(W_maxes, ks, gain, xs_label, title, path, healthy=(0.5, 3.0)):
    """Heatmap of cascade gain (output peak-to-peak) over the (W_max, k) grid, log-colored, with the
    healthy band drawn as contours. On log-log axes the iso-gain contours are straight diagonals
    (k·W_max = const) — the cascade law, seen directly. Marks the vanish / healthy / saturate zones."""
    G = np.asarray(gain)
    Wm, Km = np.meshgrid(W_maxes, ks)
    lo, hi = healthy
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    pcm = ax.pcolormesh(Wm, Km, np.log10(G + 1e-9), cmap="magma", shading="gouraud")
    cs = ax.contour(Wm, Km, G, levels=[lo, hi], colors="cyan", linewidths=1.8)
    ax.clabel(cs, fmt={lo: f"gain {lo:g}", hi: f"gain {hi:g}"}, fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(xs_label)
    ax.set_ylabel("MUL scale  k")
    ax.set_title(title)
    fig.colorbar(pcm, ax=ax, label="log10(output peak-to-peak)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def grouped_bars(groups, bar_labels, annotations, ylabel, title, path):
    """Grouped bar chart. `groups` = {item: [value per bar]}; `bar_labels` names the bars;
    `annotations` = {item: text} drawn above each group (e.g. the resulting gain)."""
    items = list(groups.keys())
    n_bars = len(bar_labels)
    x = np.arange(len(items))
    w = 0.8 / n_bars
    fig, ax = plt.subplots(figsize=(8, 5))
    for b in range(n_bars):
        ax.bar(x + (b - (n_bars - 1) / 2) * w, [groups[i][b] for i in items], w, label=bar_labels[b])
    ymax = max(max(v) for v in groups.values())
    for i, item in enumerate(items):
        if annotations.get(item):
            ax.text(i, ymax * 1.03, annotations[item], ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(items)
    ax.set_ylim(0, ymax * 1.18)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def shape_under_caps(name, raw_row, norm_row, col_labels, xs, ys, path):
    """Two rows of heatmaps for one target across tightening caps. TOP = real units on a SHARED color
    scale (watch the amplitude collapse -> the gain dies). BOTTOM = each self-normalized (watch the
    SHAPE survive). The concrete version of 'gain limit, not shape limit'."""
    n = len(col_labels)
    fig, axes = plt.subplots(2, n, figsize=(3.2 * n, 6.3))
    ext = [xs[0], xs[-1], ys[0], ys[-1]]
    vmin = float(min(s.min() for s in raw_row))
    vmax = float(max(s.max() for s in raw_row))
    im = None
    for j in range(n):
        im = axes[0, j].imshow(raw_row[j], origin="lower", extent=ext, vmin=vmin, vmax=vmax,
                               cmap="viridis", aspect="auto")
        axes[0, j].set_title(col_labels[j], fontsize=9)
        axes[0, j].set_xticks([]); axes[0, j].set_yticks([])
        S = norm_row[j]
        sn = (S - S.mean()) / (S.std() or 1.0)
        axes[1, j].imshow(sn, origin="lower", extent=ext, cmap="viridis", aspect="auto")
        axes[1, j].set_xticks([]); axes[1, j].set_yticks([])
    axes[0, 0].set_ylabel("raw — shared scale\n(amplitude / gain)")
    axes[1, 0].set_ylabel("normalized\n(shape)")
    fig.colorbar(im, ax=list(axes[0, :]), fraction=0.015, pad=0.01)
    fig.suptitle(f"{name}: tightening the cap kills amplitude (top) but keeps shape (bottom)", y=0.99)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def film_strip(name, panels_top, panels_bottom, col_labels, row_labels, xs, ys, path, suptitle=None):
    """Rung-1 'film': two rows of heatmaps on a SHARED color scale, watching a surface form over epochs.
    `panels_top`/`panels_bottom` = lists of 2-D arrays (same length as `col_labels`); `row_labels` =
    (top, bottom). Panels should be display-normalized (trainers.display_norm) so SHAPE is comparable
    and a flat/asleep frame reads uniform."""
    ncol = len(col_labels)
    allp = list(panels_top) + list(panels_bottom)
    vmin = min(float(p.min()) for p in allp)
    vmax = max(float(p.max()) for p in allp)
    ext = [xs[0], xs[-1], ys[0], ys[-1]]
    fig, axes = plt.subplots(2, ncol, figsize=(2.5 * ncol, 5.4))
    axes = np.atleast_2d(axes)
    im = None
    for r, (row_label, panels) in enumerate(zip(row_labels, (panels_top, panels_bottom))):
        for c in range(ncol):
            ax = axes[r, c]
            im = ax.imshow(panels[c], origin="lower", extent=ext, vmin=vmin, vmax=vmax,
                           cmap="viridis", aspect="auto")
            if r == 0:
                ax.set_title(col_labels[c], fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])
        axes[r, 0].set_ylabel(row_label, fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=list(axes.ravel()), fraction=0.012, pad=0.01, label="shape (display-normalized)")
    fig.suptitle(suptitle or f"{name}: watching the surface form (shape, shared scale)", y=1.0)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def film_strip_hd(name, panels_top, panels_bottom, col_labels, row_labels, xs, ys, path, suptitle=None):
    """Film with BOTH views — per learner a heatmap row AND a 3-D surface row (4 rows total:
    top-heat, top-3D, bottom-heat, bottom-3D). Panels are display-normalized (shape, shared scale), so
    the heatmap shows *where* the creases are and the 3-D shows the *shape* the model actually makes —
    together they show all of what happened to the model across epochs."""
    X1, X2 = np.meshgrid(xs, ys)
    ncol = len(col_labels)
    allp = list(panels_top) + list(panels_bottom)
    vmin = min(float(p.min()) for p in allp)
    vmax = max(float(p.max()) for p in allp)
    ext = [xs[0], xs[-1], ys[0], ys[-1]]
    rows = [(row_labels[0], panels_top, "heat"), (row_labels[0], panels_top, "3d"),
            (row_labels[1], panels_bottom, "heat"), (row_labels[1], panels_bottom, "3d")]
    fig = plt.figure(figsize=(2.5 * ncol, 10.0))
    im = None
    for r, (rlab, panels, kind) in enumerate(rows):
        for c in range(ncol):
            idx = r * ncol + c + 1
            if kind == "heat":
                ax = fig.add_subplot(4, ncol, idx)
                im = ax.imshow(panels[c], origin="lower", extent=ext, vmin=vmin, vmax=vmax,
                               cmap="viridis", aspect="auto")
                if r == 0:
                    ax.set_title(col_labels[c], fontsize=9)
                ax.set_xticks([]); ax.set_yticks([])
            else:
                ax = fig.add_subplot(4, ncol, idx, projection="3d")
                ax.plot_surface(X1, X2, panels[c], cmap="viridis", vmin=vmin, vmax=vmax,
                                rstride=4, cstride=4, linewidth=0, antialiased=True)
                ax.set_zlim(vmin, vmax)
                ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
                ax.view_init(elev=30, azim=-60)
    for yc, lab in zip((0.88, 0.66, 0.42, 0.20),
                       (f"{row_labels[0]} · heatmap", f"{row_labels[0]} · 3-D",
                        f"{row_labels[1]} · heatmap", f"{row_labels[1]} · 3-D")):
        fig.text(0.015, yc, lab, rotation=90, va="center", ha="center", fontsize=9, fontweight="bold")
    fig.suptitle(suptitle or f"{name}: forming the surface (heatmap + 3-D, shape)", y=1.0)
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def panels_with_bands(data, panel_order, xlabel, ylabel, title, path, ncol=3,
                      ylim=None, hlines=None):
    """A grid of line-plots (one panel per item in `panel_order`). `data[item]` = list of
    (label, x, med, lo, hi); each draws a median line + IQR band. `hlines[item]` = (label, y) draws a
    dashed reference (e.g. the rung-0 oracle floor). Shared structure for the curves / momentum / noise
    steps."""
    n = len(panel_order)
    nrow = (n + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.6 * ncol, 3.8 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for ax, item in zip(axes, panel_order):
        for (label, x, med, lo, hi) in data[item]:
            line, = ax.plot(x, med, lw=2, label=label, marker="", zorder=3)
            if lo is not None:
                ax.fill_between(x, lo, hi, alpha=0.16, color=line.get_color(), zorder=1)
        if hlines and item in hlines:
            hlab, hy = hlines[item]
            ax.axhline(hy, ls="--", color="0.35", lw=1.3, label=hlab, zorder=2)
        ax.set_title(item)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(*ylim)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7.5)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle(title, y=1.005, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def make_gallery(figdir, title=None):
    """Write gallery.md in figdir embedding every PNG (relative links), so you scroll one file."""
    pngs = sorted(f for f in os.listdir(figdir) if f.lower().endswith(".png"))
    lines = [f"# {title or os.path.basename(figdir)}", ""]
    for name in pngs:
        lines += [f"### {name}", "", f"![{name}]({name})", ""]
    with open(os.path.join(figdir, "gallery.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
