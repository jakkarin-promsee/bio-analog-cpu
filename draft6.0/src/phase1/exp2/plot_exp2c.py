"""Exp 2c figures from saved arrays.  python plot_exp2c.py <run-dir> <dataset>"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": False, "savefig.facecolor": "white"})
C = "#117a78"


def draw_all(A, name, out):
    rhos = A["rhos"]; n = len(A["seeds"])
    held = np.array([A[f"held_{r}"] for r in rhos])           # [rho, seed]
    drift = np.array([A[f"drift_{r}"][:, -1] for r in rhos])  # end-drift [rho, seed]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    hm, hl, hh = np.median(held, 1), np.percentile(held, 25, 1), np.percentile(held, 75, 1)
    ax[0].plot(rhos, hm, color=C, marker="o", label="held-out")
    ax[0].fill_between(rhos, hl, hh, color=C, alpha=0.2)
    ax2 = ax[0].twinx()
    ax2.plot(rhos, np.median(drift, 1), color="#c1272d", marker="s", ls=":", label="end-drift")
    ax[0].set_xlabel("read-layer SCFF rate ρ  (0=frozen … 1=fast)")
    ax[0].set_ylabel("held-out accuracy", color=C); ax2.set_ylabel("tap drift", color="#c1272d")
    ax[0].set_title(f"2c {name}: plasticity — accuracy ~flat, drift ↑ with ρ (n={n})")
    # per-layer separability for each rho (degradation persists)
    for r in rhos:
        pl = np.median(A[f"perlayer_{r}"], 0)
        ax[1].plot(range(1, len(pl) + 1), pl, marker="o", label=f"ρ={r}")
    ax[1].set_xlabel("SCFF layer"); ax[1].set_ylabel("linear-probe acc")
    ax[1].set_title("2c: depth-degradation persists at every ρ\n(plasticity ≠ degradation fix)")
    ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out, "exp2c_plasticity.png")); plt.close(fig)
    print(f"[plot_exp2c] {name} -> {out}")


if __name__ == "__main__":
    run_dir = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else "dataset"
    draw_all(np.load(os.path.join(run_dir, "arrays.npz"), allow_pickle=True), name, run_dir)
