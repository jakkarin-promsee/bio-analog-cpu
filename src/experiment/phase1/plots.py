"""Phase 1 shared plots — the 'see with eyes' deliverables. Headless (Agg backend).

surface_heatmaps : the two output channels over the 2-D input grid (rung-0a prior).
target_vs_fit    : target vs best-fit surface side by side (rung-0b reachability).
make_gallery     : write a gallery.md in a figure folder embedding every PNG (scroll one file).
"""

import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402


def surface_heatmaps(Z0, Z1, xs, ys, title, path):
    """Both output channels as heatmaps over the 2-D input grid; saved to `path`."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, Z, name in zip(axes, (Z0, Z1), ("out[0]", "out[1]")):
        im = ax.imshow(Z, origin="lower", aspect="auto",
                       extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="viridis")
        ax.set_title(f"{title} · {name}")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def target_vs_fit(name, T, P, xs, ys, path, resid=None):
    """2x2, all in the target's REAL output units:
      top    : target heatmap | best-fit heatmap (the top-down map)
      bottom : target 3-D surface | best-fit 3-D surface (the REAL shape).
    The 3-D row is the honest shape — a plane is a flat plane, a paraboloid a bowl, xor a step-checkerboard;
    compare left vs right to read the fit. (1-D collapses like sort/1:1 distort shape, so they're out.)
    `resid` is the normalized residual (shown in the title)."""
    X1, X2 = np.meshgrid(xs, ys)
    vmin = float(min(T.min(), P.min()))
    vmax = float(max(T.max(), P.max()))
    fig = plt.figure(figsize=(12, 9))

    # top row: heatmaps (top-down map)
    for i, (Z, lab) in enumerate([(T, "target"), (P, "best-fit (real ALU)")]):
        ax = fig.add_subplot(2, 2, i + 1)
        im = ax.imshow(Z, origin="lower", aspect="auto", vmin=vmin, vmax=vmax,
                       extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="viridis")
        ax.set_title(f"{name} · {lab}")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # bottom row: 3-D surfaces (the real shape), shared z-scale + view angle
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


def trend_plot(x, series, xlabel, ylabel, title, path, xticklabels=None):
    """Line plot of one or more series vs x (e.g., residual or a metric vs the weight ceiling).
    `series` = {label: y-values}; `xticklabels` relabels the x ticks (e.g. the W_max values)."""
    fig, ax = plt.subplots(figsize=(7, 5))
    for label, y in series.items():
        ax.plot(x, y, marker="o", label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if xticklabels is not None:
        ax.set_xticks(x)
        ax.set_xticklabels(xticklabels)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def ceiling_grid(surfaces, sublabels, xs, ys, title, path):
    """One Ganglion under a tightening cap. `surfaces` = out0 arrays (one per W_max). Top row = RAW on a
    shared color scale (see the amplitude crush); bottom row = each normalized (see whether the SHAPE
    survives). `sublabels` = per-column captions (e.g. clipped/29 + range width)."""
    n = len(surfaces)
    fig, axes = plt.subplots(2, n, figsize=(3.3 * n, 6.6))
    vmin = float(min(s.min() for s in surfaces))
    vmax = float(max(s.max() for s in surfaces))
    ext = [xs[0], xs[-1], ys[0], ys[-1]]
    im = None
    for j, (S, lab) in enumerate(zip(surfaces, sublabels)):
        ax = axes[0, j]
        im = ax.imshow(S, origin="lower", extent=ext, vmin=vmin, vmax=vmax, cmap="viridis", aspect="auto")
        ax.set_title(lab, fontsize=8)
        ax.set_xticks([]); ax.set_yticks([])
        if j == 0:
            ax.set_ylabel("raw — shared scale\n(amplitude)")
        sn = (S - S.mean()) / (S.std() or 1.0)
        ax2 = axes[1, j]
        ax2.imshow(sn, origin="lower", extent=ext, cmap="viridis", aspect="auto")
        ax2.set_xticks([]); ax2.set_yticks([])
        if j == 0:
            ax2.set_ylabel("normalized\n(shape)")
    fig.colorbar(im, ax=list(axes[0, :]), fraction=0.015, pad=0.01)
    fig.suptitle(title, y=0.99)
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
