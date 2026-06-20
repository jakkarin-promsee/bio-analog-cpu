"""
Exp 2c — the plasticity gradient: frozen / slow / fast read-layers in ONLINE co-training.

The committed N2 drift fix (ideas1 Ch6, LLRD-mirror): the late SCFF layers GD reads learn
SLOW; the front stays fast. Tested in the regime it's *for* — SCFF still learning while the
GD readout reads it (co-training), so the taps drift. Sweep the read-layer SCFF rate rho.

We ALSO measure per-layer separability under each rho, to check whether plasticity touches
the Exp-1 depth-DEGRADATION finding (hypothesis: it fixes drift, not degradation).

read-layers = deep half (L3,L4); front = L1,L2. Reuses exp0/exp1. numpy only.
Run:  python run_exp2c.py digits     |     python run_exp2c.py mnist
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))
sys.path.insert(0, os.path.join(_HERE, "..", "exp1"))
from scff_gate import SCFF, relu, EPS, THETA, LR_SCFF, GOODNESS_MODE   # noqa: E402
from models_extra import MLP                                          # noqa: E402
from run_exp1 import load_data, _git_hash                            # noqa: E402

BATCH, PROBE_C = 32, 1.0
RHOS = [0.0, 0.1, 0.3, 1.0]          # read-layer SCFF rate: frozen / slow / mid / fast
CFG = {"digits": dict(H=64, warm=20, co=40, n_train=600, n_test=600, seeds=[42, 137, 271]),
       "mnist":  dict(H=128, warm=12, co=20, n_train=3000, n_test=3000, seeds=[42, 137, 271])}
CO_CKPTS = [1, 2, 4, 8, 16, 30, 40]


class ScffPlastic(SCFF):
    """SCFF with a per-layer learning-rate scale (the plasticity gradient)."""
    def set_plasticity(self, lr_scale):
        self.lr_scale = np.asarray(lr_scale, float)

    def train_step(self, Xb, rng):
        if not hasattr(self, "lr_scale"):
            self.lr_scale = np.ones(self.L)
        B = len(Xb); perm = rng.permutation(B)
        a_pos, a_neg = self._in(2.0 * Xb), self._in(Xb + Xb[perm])
        for l in range(self.L):
            W, b = self.W[l], self.b[l]
            hp, hn = relu(a_pos @ W.T + b), relu(a_neg @ W.T + b)
            M = hp.shape[1]; gs = self._gscale(M)
            Gp, Gn = (hp ** 2).sum(1) * gs, (hn ** 2).sum(1) * gs
            cpos = (expit(Gp - self.theta) - 1.0) * (2.0 * gs)
            cneg = (expit(Gn - self.theta)) * (2.0 * gs)
            gW = ((cpos[:, None] * hp).T @ a_pos + (cneg[:, None] * hn).T @ a_neg) / B
            gb = ((cpos[:, None] * hp).sum(0) + (cneg[:, None] * hn).sum(0)) / B
            lr = self.lr * self.lr_scale[l]
            self.W[l] -= lr * gW; self.b[l] -= lr * gb
            a_pos, a_neg = self._norm(hp), self._norm(hn)


def taps(sc, X):
    return np.concatenate(sc.infer(X), axis=1)          # all layers


def perlayer(sc, Xtr, Ytr, Xte, Yte):
    return [float(LogisticRegression(C=PROBE_C, max_iter=3000).fit(rtr, Ytr).score(rte, Yte))
            for rtr, rte in zip(sc.infer(Xtr), sc.infer(Xte))]


def run_one(name, rho, seed):
    c = CFG[name]; H = c["H"]
    Xtr, Ytr, Xte, Yte, C = load_data(name, c["n_train"], c["n_test"], seed)
    D = Xtr.shape[1]
    sc = ScffPlastic([D, H, H, H, H], THETA, LR_SCFF, seed,
                     objective="two_sided", goodness_mode=GOODNESS_MODE)
    rng = np.random.default_rng(seed)
    # warmup: all layers full rate
    sc.set_plasticity([1, 1, 1, 1])
    for _ in range(c["warm"]):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            sc.train_step(Xtr[idx[s:s + BATCH]], rng)
    # co-train: front fast, read-layers (L3,L4) at rho; GD readout reads all-layer taps
    sc.set_plasticity([1, 1, rho, rho])
    ro = MLP([taps(sc, Xtr[:1]).shape[1], 32, C], seed, lr=2e-3)
    roR = np.random.default_rng(seed + 7)
    curve, drift, prev = [], [], None
    Xd = Xte[:400]
    co_ck = [e for e in CO_CKPTS if e <= c["co"]]
    for ep in range(1, c["co"] + 1):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            b = idx[s:s + BATCH]
            sc.train_step(Xtr[b], rng)                  # SCFF keeps learning (front + rho*read)
            F = taps(sc, Xtr[b]); ro.train_step(F, Ytr[b])   # GD readout tracks
        if ep in co_ck:
            cur = taps(sc, Xd)
            d = 0.0 if prev is None else float(np.linalg.norm(cur - prev, axis=1).mean())
            drift.append(d); prev = cur
            curve.append((ro.accuracy(taps(sc, Xtr), Ytr), ro.accuracy(taps(sc, Xte), Yte)))
    return dict(curve=np.array(curve), drift=np.array(drift),
                perlayer=perlayer(sc, Xtr, Ytr, Xte, Yte),
                held=float(ro.accuracy(taps(sc, Xte), Yte)),
                gap=float(ro.accuracy(taps(sc, Xtr), Ytr) - ro.accuracy(taps(sc, Xte), Yte)),
                co_ck=co_ck)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "digits"
    seeds = CFG[name]["seeds"]; t0 = time.time()
    R = {rho: [run_one(name, rho, s) for s in seeds] for rho in RHOS}
    print(f"\n=== Exp 2c [{name}] read-layer plasticity, median n={len(seeds)} ===")
    for rho in RHOS:
        held = np.median([r["held"] for r in R[rho]]); gap = np.median([r["gap"] for r in R[rho]])
        drift = np.median([r["drift"][-1] for r in R[rho]])
        pl = np.median([r["perlayer"] for r in R[rho]], 0)
        tag = {0.0: "frozen", 1.0: "fast"}.get(rho, "slow")
        print(f"  rho={rho:<4} ({tag:6s}) held {held:.3f}  gap {gap:+.3f}  end-drift {drift:.3f}  "
              f"per-layer {np.round(pl, 3)}")

    OUT = os.path.join(_HERE, f"figs_exp2c_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {f"held_{rho}": np.array([r["held"] for r in R[rho]]) for rho in RHOS}
    for rho in RHOS:
        saved[f"perlayer_{rho}"] = np.array([r["perlayer"] for r in R[rho]])
        saved[f"drift_{rho}"] = np.array([r["drift"] for r in R[rho]])
        saved[f"curve_{rho}"] = np.array([r["curve"] for r in R[rho]])
    saved["rhos"] = np.array(RHOS); saved["seeds"] = np.array(seeds)
    saved["co_ck"] = np.array(R[RHOS[0]][0]["co_ck"])
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)
    json.dump({"experiment": f"exp2c-{name}", "git_commit": _git_hash(), "rhos": RHOS,
               "seeds": seeds, "config": CFG[name], "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    print(f"  ({time.time()-t0:.0f}s) arrays+manifest -> {OUT}")


if __name__ == "__main__":
    main()
