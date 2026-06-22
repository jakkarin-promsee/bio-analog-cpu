"""
Experiment P3.3 — the continual veto (the adoption-deciding question for the objective reframe).

The non-negotiable test: does the NEW objective (`contrast + cross-layer coordination`, the P3.0–P3.2 winner)
RE-EARN the Phase-1 continual win? The Phase-1 win rested on ENERGY-SCFF being forgetting-robust (clusters
unsupervised -> new classes ADD clusters, don't overwrite). The contrastive objective discriminates samples with
in-batch negatives -> it MIGHT bias to the current task and forget. So we veto-test it directly, against the
energy baseline, on the exp4/P2.6 class-incremental digits stream.

Conditions (one variable = the SCFF objective; sleep on/off isolates readout consolidation):
  gd                 — plain MLP online through the stream (catastrophic-forgetting baseline)
  energy_sleep       — energy-SCFF (P2.1 healthy cell, L=4) + sleep readout re-fit (the Phase-1/2 baseline)
  contrast_sleep     — contrast+coordination (SCFFContrastOLU L=4, w=2) + sleep (THE new recipe)
  contrast_nosleep   — contrast+coordination, no sleep (the rot control)

Pass gate: BWT(contrast_sleep) >= BWT(energy_sleep) - 0.02 (the continual win preserved) AND the contrast
all-class SCFF probe stays flat (doesn't forget). 3 seeds. Single-threaded (phantom guard).
Run:  OMP_NUM_THREADS=1 python -u run_p3_3.py   (add --quick for 1 seed)
"""
from __future__ import annotations
import json, os, subprocess, sys, time, warnings
import numpy as np
from sklearn.linear_model import LogisticRegression
warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                                              # plot
sys.path.insert(0, os.path.join(_HERE, ".."))                         # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))                 # run_p3_0 (unused but harmless)
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))         # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2", "exp6"))  # the P2.6 continual harness
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p2lib import SCFF2, EPS                                          # noqa: E402
from p3lib import SCFFContrastOLU                                     # noqa: E402
from models_extra import MLP                                         # noqa: E402
from run_exp6 import (load_digits_split, fit_readout, acc_matrix_metrics, per_task_acc,   # noqa: E402
                      TASKS, WIDTH, BATCH, C, SCFF_EP, SLEEP_EP, CELL)

SEEDS = [42, 137, 271]
L = 4


class Stack:
    """A single deep SCFF-family bulk (energy OR contrast+coordination) + a readout, sleep-consolidated.
    The P3.2 winner is a single deep contrast+coordination stack (not the P2.6 boosted blocks)."""
    def __init__(self, D, seed, kind):
        if kind == "energy":
            self.m = SCFF2([D] + [WIDTH] * L, seed=seed, **CELL)
        else:                                                          # contrast + coordination (w=2)
            self.m = SCFFContrastOLU([D] + [WIDTH] * L, seed=seed, window=2, mask_ratio=0.5, temp=0.5)
        self.kind = kind; self.readout = None

    def _tap(self, X):
        return np.concatenate(self.m.infer(X), 1)                     # all-layer tap

    def train_scff(self, Xb, rng):
        if self.kind != "energy" and len(Xb) < 4:                     # InfoNCE needs in-batch negatives
            return
        self.m.train_step(Xb, rng)

    def train_readout_online(self, Xb, Yb):
        t = self._tap(Xb)
        if self.readout is None:
            self.readout = MLP([t.shape[1], 32, C], 0, lr=2e-3)
        self.readout.train_step(t, Yb)

    def sleep(self, BX, BY, seed):
        self.readout = fit_readout(self._tap(BX), BY, seed, SLEEP_EP)

    def predict(self, X):
        return self.readout.forward(self._tap(X)).argmax(1)


def run_condition(kind, Xtr, Ytr, Xte, Yte, seed):
    rng = np.random.default_rng(seed)
    pr = rng.permutation(len(Xtr))[:800]; Xpr, Ypr = Xtr[pr], Ytr[pr]
    a = [[0.0] * len(TASKS) for _ in range(len(TASKS))]
    traj, scff_probe, drift = [], [], []
    prev_rep = None; bufX, bufY = [], []

    if kind == "gd":
        gd = MLP([Xtr.shape[1], 96, 96, 96, C], seed, lr=1e-3); predict = gd.predict
    else:
        stk = Stack(Xtr.shape[1], seed, "energy" if kind.startswith("energy") else "contrast")
        predict = stk.predict

    for t, cls in enumerate(TASKS):
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(SCFF_EP):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), BATCH):
                b = idx[s:s + BATCH]
                if kind == "gd":
                    gd.train_step(Xt[b], Yt[b])
                else:
                    stk.train_scff(Xt[b], rng); stk.train_readout_online(Xt[b], Yt[b])
        bufX.append(Xt); bufY.append(Yt)
        if kind.endswith("_sleep"):
            stk.sleep(np.concatenate(bufX), np.concatenate(bufY), seed)
        for kk in range(t + 1):
            a[t][kk] = per_task_acc(predict, Xte, Yte)[kk]
        traj.append(float((predict(Xte) == Yte).mean()))
        if kind != "gd":
            P = np.concatenate(stk.m.infer(Xpr), 1); Pte = np.concatenate(stk.m.infer(Xte), 1)
            clf = LogisticRegression(C=1.0, max_iter=2000).fit(P, Ypr)
            scff_probe.append(float(clf.score(Pte, Yte)))
            rep = P / (np.linalg.norm(P, axis=1, keepdims=True) + EPS)
            drift.append(0.0 if prev_rep is None else float(np.linalg.norm(rep - prev_rep, axis=1).mean()))
            prev_rep = rep
    final, bwt, forget = acc_matrix_metrics(a)
    return dict(traj=traj, final=final, bwt=bwt, forget=forget,
                scff_probe=scff_probe or [0.0] * len(TASKS), drift=drift or [0.0] * len(TASKS))


CONDS = ["gd", "energy_sleep", "contrast_sleep", "contrast_nosleep"]
LAB = {"gd": "GD-online (forget)", "energy_sleep": "energy-SCFF + sleep (P1/P2 base)",
       "contrast_sleep": "contrast+coord + sleep (NEW recipe)", "contrast_nosleep": "contrast+coord no-sleep (rot)"}


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def main():
    seeds = SEEDS[:1] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P3.3 [digits] continual veto on contrast+coord | conds={CONDS} | seeds={seeds} ===", flush=True)
    runs = {c: [] for c in CONDS}
    for s in seeds:
        Xtr, Ytr, Xte, Yte = load_digits_split(s)
        for c in CONDS:
            r = run_condition(c, Xtr, Ytr, Xte, Yte, s); runs[c].append(r)
            print(f"  seed {s} {c:20s} final {r['final']:.3f}  BWT {r['bwt']:+.3f}  forget {r['forget']:.3f}",
                  flush=True)

    def med(c, k): return float(np.median([r[k] for r in runs[c]]))
    def iqr(c, k):
        v = [r[k] for r in runs[c]]; return float(np.percentile(v, 25)), float(np.percentile(v, 75))

    print(f"\n--- P3.3 [digits] median, n={len(seeds)} ---")
    for c in CONDS:
        lo, hi = iqr(c, "bwt")
        print(f"  {LAB[c]:36s} final {med(c,'final'):.3f}  BWT {med(c,'bwt'):+.3f}[{lo:+.3f},{hi:+.3f}]  "
              f"forget {med(c,'forget'):.3f}")
    base_bwt, rec_bwt = med("energy_sleep", "bwt"), med("contrast_sleep", "bwt")
    base_fin, rec_fin = med("energy_sleep", "final"), med("contrast_sleep", "final")
    sp = np.median([r["scff_probe"] for r in runs["contrast_sleep"]], 0)
    sp_flat = (sp[-1] - sp[0]) > -0.05
    veto = ("PASS - contrast+coord RE-EARNS the continual win" if (rec_bwt >= base_bwt - 0.02 and sp_flat)
            else "FAIL - contrast+coord worsens BWT / forgets (the objective reframe costs the continual win)")
    print(f"\n  VETO: contrast+coord BWT {rec_bwt:+.3f} vs energy {base_bwt:+.3f} "
          f"(final {rec_fin:.3f} vs {base_fin:.3f}); contrast SCFF-probe {np.round(sp,3)} "
          f"({'flat' if sp_flat else 'DROPS'}) -> {veto}", flush=True)

    OUT = os.path.join(_HERE, "figs_p3_3_digits"); os.makedirs(OUT, exist_ok=True)
    saved = {}
    for c in CONDS:
        for k in ["traj", "final", "bwt", "forget", "scff_probe", "drift"]:
            saved[f"{c}__{k}"] = np.array([r[k] for r in runs[c]])
    saved["seeds"] = np.array(seeds)
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)
    manifest = {"experiment": "p3_3-digits", "git_commit": _git(), "seeds": list(seeds), "tasks": TASKS,
                "L": L, "window": 2, "conds": CONDS,
                "results_median": {c: {"final": med(c, "final"), "bwt": med(c, "bwt"),
                                       "forget": med(c, "forget")} for c in CONDS},
                "veto": veto, "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p3_3 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
