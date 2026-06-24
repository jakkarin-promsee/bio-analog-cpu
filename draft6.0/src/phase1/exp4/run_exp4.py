"""
Exp 4 — maintenance: does the continual stream ROT (the shift/forget problem), and does
SLEEP recover it? Class-incremental stream (classes arrive in waves). The shift is real:
SCFF keeps adapting to new classes, so its features move and the readout goes stale.

Conditions (all-class held-out after each task):
  GD-online      — plain MLP trained online through the stream (the catastrophic-forgetting baseline)
  block no-sleep — SCFF online + readout online (3.0): watch it rot
  block sleep-full (3.1) — at each task end, re-fit the readout on the FULL buffer vs CURRENT SCFF taps
  block sleep-LUT  (3.2) — re-fit on a prototype LUT (winner-take-all, vigilance) — the real hippocampus

Also: does SCFF ITSELF forget? (all-class linear probe of SCFF taps over the stream.) The thesis hope is
SCFF (unsupervised) stays stable and only the small readout needs sleep.

Reuses exp0/exp1. numpy only.  Run:  python run_exp4.py digits | mnist
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
from sklearn.linear_model import LogisticRegression

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))
sys.path.insert(0, os.path.join(_HERE, "..", "exp1"))
from scff_gate import SCFF, EPS, THETA, LR_SCFF, GOODNESS_MODE         # noqa: E402
from models_extra import MLP                                          # noqa: E402
from run_exp1 import load_data, _git_hash                            # noqa: E402

BATCH, PROBE_C = 32, 1.0
CFG = {"digits": dict(H=64, scff_ep=8, sleep_ep=60, n_train=1200, n_test=600,
                      vig=0.93, seeds=[42, 137, 271]),
       "mnist":  dict(H=128, scff_ep=4, sleep_ep=30, n_train=5000, n_test=2000,
                      vig=0.90, seeds=[42, 137])}
TASKS = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]


class LUT:
    """Prototype store: winner-take-all novelty allocation (cosine vigilance). The hippocampus."""
    def __init__(self, vig):
        self.P, self.Y, self.vig = [], [], vig

    def add(self, X, Y):
        for x, y in zip(X, Y):
            if not self.P:
                self.P.append(x); self.Y.append(y); continue
            P = np.asarray(self.P)
            sims = (P @ x) / (np.linalg.norm(P, axis=1) * (np.linalg.norm(x) + EPS) + EPS)
            if sims.max() < self.vig:
                self.P.append(x); self.Y.append(y)

    def replay(self):
        return np.asarray(self.P), np.asarray(self.Y)


def taps(sc, X):
    return np.concatenate(sc.infer(X), axis=1)


def fit_readout(F, Y, C, seed, epochs):
    ro = MLP([F.shape[1], 32, C], seed, lr=2e-3); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            ro.train_step(F[idx[s:s + BATCH]], Y[idx[s:s + BATCH]])
    return ro


def run_seed(name, seed):
    c = CFG[name]; H = c["H"]
    Xtr, Ytr, Xte, Yte, C = load_data(name, c["n_train"], c["n_test"], seed)
    D = Xtr.shape[1]
    sc = SCFF([D, H, H, H, H], THETA, LR_SCFF, seed, objective="two_sided", goodness_mode=GOODNESS_MODE)
    online_ro = MLP([taps(sc, Xtr[:1]).shape[1], 32, C], seed, lr=2e-3)
    gd = MLP([D, 96, 96, 96, C], seed, lr=1e-3)             # pure-GD online baseline
    lut = LUT(c["vig"]); bufX, bufY = [], []
    rng = np.random.default_rng(seed)
    # a small fixed all-class probe set (to ask: does SCFF forget?)
    pr = rng.permutation(len(Xtr))[:1000]; Xpr, Ypr = Xtr[pr], Ytr[pr]

    rec = {k: [] for k in ["online", "gd", "sleep_full", "sleep_lut", "scff_probe", "lut_size"]}
    for cls in TASKS:
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(c["scff_ep"]):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), BATCH):
                b = idx[s:s + BATCH]
                sc.train_step(Xt[b], rng)                  # SCFF online
                online_ro.train_step(taps(sc, Xt[b]), Yt[b])   # readout online (will forget)
                gd.train_step(Xt[b], Yt[b])                # pure GD online
        bufX.append(Xt); bufY.append(Yt); lut.add(Xt, Yt)
        BX, BY = np.concatenate(bufX), np.concatenate(bufY)
        # sleep: re-fit readout vs CURRENT SCFF taps (body frozen during sleep)
        ro_full = fit_readout(taps(sc, BX), BY, C, seed, c["sleep_ep"])
        pX, pY = lut.replay(); ro_lut = fit_readout(taps(sc, pX), pY, C, seed, c["sleep_ep"])
        Fte = taps(sc, Xte)
        rec["online"].append(online_ro.accuracy(Fte, Yte))
        rec["gd"].append(gd.accuracy(Xte, Yte))
        rec["sleep_full"].append(ro_full.accuracy(Fte, Yte))
        rec["sleep_lut"].append(ro_lut.accuracy(Fte, Yte))
        # does SCFF itself retain all classes? all-class linear probe of current taps
        clf = LogisticRegression(C=PROBE_C, max_iter=2000).fit(taps(sc, Xpr), Ypr)
        rec["scff_probe"].append(clf.score(Fte, Yte))
        rec["lut_size"].append(len(lut.P))
    rec["buf_size"] = len(BY)
    return rec


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "digits"
    seeds = CFG[name]["seeds"]; t0 = time.time()
    runs = [run_seed(name, s) for s in seeds]
    st = lambda k: np.array([r[k] for r in runs])
    tasks_seen = [f"+{c[0]},{c[1]}" for c in TASKS]
    print(f"\n=== Exp 4 [{name}] continual class-incremental, median n={len(seeds)} ===")
    print(f"  tasks:           {tasks_seen}")
    for k, lab in [("gd", "GD-online      "), ("online", "block no-sleep "),
                   ("sleep_full", "block sleep-FULL"), ("sleep_lut", "block sleep-LUT "),
                   ("scff_probe", "SCFF probe(all)")]:
        print(f"  {lab} {np.round(np.median(st(k), 0), 3)}")
    print(f"  LUT size {np.median(st('lut_size'),0).astype(int)} vs full buffer {int(np.median([r['buf_size'] for r in runs]))}")
    print(f"  FINAL all-class held-out: GD {np.median(st('gd')[:,-1]):.3f}  no-sleep {np.median(st('online')[:,-1]):.3f}  "
          f"sleep-full {np.median(st('sleep_full')[:,-1]):.3f}  sleep-LUT {np.median(st('sleep_lut')[:,-1]):.3f}")

    OUT = os.path.join(_HERE, f"figs_exp4_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {k: st(k) for k in ["online", "gd", "sleep_full", "sleep_lut", "scff_probe", "lut_size"]}
    saved["buf_size"] = np.array([r["buf_size"] for r in runs]); saved["seeds"] = np.array(seeds)
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)
    json.dump({"experiment": f"exp4-{name}", "git_commit": _git_hash(), "tasks": TASKS,
               "seeds": seeds, "config": CFG[name], "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    _fig(saved, name, OUT)
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}")


def _fig(A, name, OUT):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10, "savefig.transparent": False, "savefig.facecolor": "white"})
    x = np.arange(1, len(TASKS) + 1)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    style = [("gd", "#e08214", "GD-online"), ("online", "#c1272d", "block no-sleep (3.0)"),
             ("sleep_full", "#117a78", "block sleep-full (3.1)"), ("sleep_lut", "#1f5fbf", "block sleep-LUT (3.2)")]
    for k, col, lab in style:
        m = np.median(A[k], 0); lo, hi = np.percentile(A[k], 25, 0), np.percentile(A[k], 75, 0)
        ax[0].plot(x, m, color=col, marker="o", label=lab); ax[0].fill_between(x, lo, hi, color=col, alpha=0.15)
    ax[0].set_xlabel("tasks seen (class-incremental)"); ax[0].set_ylabel("ALL-class held-out acc")
    ax[0].set_xticks(x); ax[0].set_xticklabels([f"+{c[0]},{c[1]}" for c in TASKS])
    ax[0].set_title(f"Exp4 {name}: rot vs sleep recovery (n={A['gd'].shape[0]})"); ax[0].legend(fontsize=8)
    # SCFF probe stability + LUT size
    m = np.median(A["scff_probe"], 0); lo, hi = np.percentile(A["scff_probe"], 25, 0), np.percentile(A["scff_probe"], 75, 0)
    ax[1].plot(x, m, color="#117a78", marker="o", label="SCFF all-class probe")
    ax[1].fill_between(x, lo, hi, color="#117a78", alpha=0.2)
    ax[1].set_xlabel("tasks seen"); ax[1].set_ylabel("SCFF linear-probe acc (all classes)")
    ax[1].set_xticks(x); ax[1].set_xticklabels([f"+{c[0]},{c[1]}" for c in TASKS])
    ax[1].set_title("Does SCFF itself forget? (taps probe)"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "exp4_rot_sleep.png")); plt.close(fig)


if __name__ == "__main__":
    main()
