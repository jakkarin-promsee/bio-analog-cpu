"""
Exp 2a — the SCFF:GD ratio (the split point). THE direct test of Exp 1's depth-degradation
finding: since SCFF features degrade with depth, how much of the block should be cheap SCFF
before precision suffers? Slide the split 0% SCFF (= pure GD) -> ... -> 100% SCFF.

Block at split k (of L=4 layers): first k layers SCFF-trained (local, unsupervised, frozen);
the GD back = the remaining (L-k) layers + readout, trained by backprop, reading the
concat of ALL SCFF layers 1..k (all-layer tap, per Exp 1's fix).
  k=0  -> pure GD (the ceiling)        k=L -> Exp-1 block (max SCFF)

F9 trade curve: held-out accuracy AND backward cost vs SCFF fraction. Reuses exp0/exp1.
Run:  python run_exp2a.py digits   |   python run_exp2a.py mnist
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))
sys.path.insert(0, os.path.join(_HERE, "..", "exp1"))
from scff_gate import SCFF, THETA, LR_SCFF, GOODNESS_MODE              # noqa: E402
from models_extra import MLP                                          # noqa: E402
from run_exp1 import load_data, bwd_flops, _git_hash                  # noqa: E402

BATCH, L, PROBE_C = 32, 4, 1.0
CFG = {"digits": dict(H=64, scff_ep=40, sup_ep=60, n_train=600, n_test=600,
                      seeds=[42, 137, 271, 314, 1729]),
       "mnist":  dict(H=128, scff_ep=25, sup_ep=40, n_train=3000, n_test=3000,
                      seeds=[42, 137, 271])}   # 3 seeds for the trade-curve shape (cost)
C_BLOCK, C_GD = "#117a78", "#e08214"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": False, "savefig.facecolor": "white"})


def run_split(name, k, seed):
    c = CFG[name]; H = c["H"]
    Xtr, Ytr, Xte, Yte, C = load_data(name, c["n_train"], c["n_test"], seed)
    D = Xtr.shape[1]
    # SCFF front (k local layers), two-phase: pretrain unsupervised, freeze
    if k > 0:
        sc = SCFF([D] + [H] * k, THETA, LR_SCFF, seed, objective="two_sided",
                  goodness_mode=GOODNESS_MODE)
        rng = np.random.default_rng(seed)
        for _ in range(c["scff_ep"]):
            idx = rng.permutation(len(Xtr))
            for s in range(0, len(Xtr), BATCH):
                sc.train_step(Xtr[idx[s:s + BATCH]], rng)
        feat = lambda X: np.concatenate(sc.infer(X), axis=1)     # all-layer tap (1..k)
        scff_local = sum(4 * dims[0] * dims[1] for dims in
                         [([D, H][i:i + 2] if i == 0 else [H, H]) for i in range(k)])
        scff_local = 4 * D * H + 4 * H * H * (k - 1)
    else:
        feat = lambda X: X; scff_local = 0
    Ftr, Fte = feat(Xtr), feat(Xte)
    # GD back: (L-k) hidden layers width H + a 32 penult + C, trained by backprop
    gd_dims = [Ftr.shape[1]] + [H] * (L - k) + [32, C]
    gd = MLP(gd_dims, seed, lr=1.5e-3)
    rng = np.random.default_rng(seed + 5)
    for _ in range(c["sup_ep"]):
        idx = rng.permutation(len(Ftr))
        for s in range(0, len(Ftr), BATCH):
            gd.train_step(Ftr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    held = gd.accuracy(Fte, Yte); gap = gd.accuracy(Ftr, Ytr) - held
    return dict(held=float(held), gap=float(gap),
                gd_bwd=bwd_flops(gd_dims), scff_local=int(scff_local),
                weights=gd.n_weights() + (sum(w.size + b.size for w, b in zip(sc.W, sc.b)) if k > 0 else 0))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "digits"
    seeds = CFG[name]["seeds"]; t0 = time.time()
    KS = list(range(0, L + 1))                       # 0..4 SCFF layers
    R = {k: [run_split(name, k, s) for s in seeds] for k in KS}
    print(f"\n=== Exp 2a [{name}] SCFF:GD ratio, median n={len(seeds)} ===")
    print(f"  {'SCFF layers':>11} {'frac':>5} {'held-out':>18} {'gap':>7} {'GD-bwd FLOPs':>13} {'weights':>8}")
    for k in KS:
        held = np.array([r["held"] for r in R[k]]); gap = np.median([r["gap"] for r in R[k]])
        bwd = R[k][0]["gd_bwd"]; wts = R[k][0]["weights"]
        print(f"  {k:>11} {k/L:>5.2f} {np.median(held):>8.3f} [{np.percentile(held,25):.3f},"
              f"{np.percentile(held,75):.3f}] {gap:>+7.3f} {bwd:>13,} {wts:>8,}")

    OUT = os.path.join(_HERE, f"figs_exp2a_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {"ks": np.array(KS), "seeds": np.array(seeds)}
    for k in KS:
        saved[f"held_{k}"] = np.array([r["held"] for r in R[k]])
        saved[f"gap_{k}"] = np.array([r["gap"] for r in R[k]])
    saved["gd_bwd"] = np.array([R[k][0]["gd_bwd"] for k in KS])
    saved["scff_local"] = np.array([R[k][0]["scff_local"] for k in KS])
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)
    json.dump({"experiment": f"exp2a-{name}", "git_commit": _git_hash(), "L": L,
               "seeds": seeds, "config": CFG[name], "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    _fig(saved, name, OUT)
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}")


def _fig(A, name, OUT):
    ks = A["ks"]; frac = ks / L
    held = np.array([A[f"held_{k}"] for k in ks])             # [k, seed]
    m, lo, hi = np.median(held, 1), np.percentile(held, 25, 1), np.percentile(held, 75, 1)
    bwd = A["gd_bwd"].astype(float)
    fig, ax1 = plt.subplots(figsize=(6.8, 4.4))
    ax1.plot(frac, m, color=C_BLOCK, marker="o", label="held-out acc")
    ax1.fill_between(frac, lo, hi, color=C_BLOCK, alpha=0.2)
    ax1.axhline(m[0], color=C_GD, ls="--", lw=1.2, label="pure-GD ceiling (0% SCFF)")
    ax1.set_xlabel("SCFF fraction (k / L)"); ax1.set_ylabel("held-out accuracy", color=C_BLOCK)
    ax2 = ax1.twinx()
    ax2.plot(frac, bwd / bwd[0], color="#888", marker="s", ls=":", label="GD backward cost (rel)")
    ax2.set_ylabel("GD backward cost / pure-GD", color="#888")
    ax1.set_title(f"F9 {name}: SCFF:GD trade — accuracy vs cheap-SCFF fraction (n={held.shape[1]})")
    h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc="lower left")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F9_trade.png")); plt.close(fig)


if __name__ == "__main__":
    main()
