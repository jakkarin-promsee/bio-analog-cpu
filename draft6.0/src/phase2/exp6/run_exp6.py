"""
Experiment P2.6 — the continual veto (closes Phase 2).

The non-negotiable test: does the surviving depth recipe — boosted-`read` multi-block (P2.5) — PRESERVE the
Phase-1 continual win? Re-run the class-incremental stream (exp4 setup, digits) with the depth recipe vs the
single-block baseline, both sleep-consolidated, and report the per-task accuracy matrix -> final ACC + BWT +
forgetting. A recipe that lifts static depth but worsens BWT is rejected. Per-block SCFF = the P2.1 healthy cell
(layer-norm + linear + contrast) — which also re-tests whether THIS cell keeps the win (exp4 used length+squared).

Conditions (one variable = block count; sleep on/off isolates readout consolidation):
  GD-online            — plain MLP online through the stream (catastrophic-forgetting baseline)
  single-block + sleep — 1 SCFF block (k=4) + readout; sleep = full-buffer readout re-fit (Phase-1 baseline)
  boosted-read + sleep — [SCFF×1 -> readout]×4 (equal total SCFF depth 4), ensemble; sleep re-fit (THE recipe)
  boosted-read no-sleep — the rot control

Also: SCFF all-class probe stability (does SCFF forget?), feature drift per task (the Phase-3 gate hand-off),
and the SUBSTRATE table (in the card). 3 seeds [42,137,271], median + IQR. Single-threaded (phantom guard).
Run:  OMP_NUM_THREADS=1 python -u run_exp6.py   (add --quick for 1 seed)
"""
from __future__ import annotations
import json, os, subprocess, sys, time, warnings
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p2lib import SCFF2, EPS                                            # noqa: E402
from models_extra import MLP                                           # noqa: E402

SEEDS = [42, 137, 271]
TASKS = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
WIDTH, BATCH, C = 64, 32, 10
CELL = dict(norm="layernorm", goodness="linear", objective="contrast")   # the P2.1 healthy cell
SCFF_EP, SLEEP_EP = 8, 60


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def load_digits_split(seed, n_train=1200, n_test=600):
    d = load_digits(); X = (d.data / 16.0).astype(np.float64); Y = d.target.astype(np.int64)
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:n_train], idx[n_train:n_train + n_test]
    return X[tr], Y[tr], X[te], Y[te]


def fit_readout(F, Y, seed, epochs):
    ro = MLP([F.shape[1], 32, C], seed, lr=2e-3); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(F))
        for s in range(0, len(F), BATCH):
            ro.train_step(F[idx[s:s + BATCH]], Y[idx[s:s + BATCH]])
    return ro


class BlockStack:
    """N boosted blocks; each = a k-layer SCFF (P2.1 healthy cell) + a readout. read mode: stream = the
    block's last SCFF layer; final prediction = ensemble (sum) of block-readout logits."""
    def __init__(self, D, N, k, seed):
        self.N, self.k = N, k
        d = D; self.blocks = []
        for b in range(N):
            self.blocks.append(SCFF2([d] + [WIDTH] * k, seed=seed + b, **CELL)); d = WIDTH
        self.readouts = [None] * N

    def _taps(self, X):
        """Per-block all-tap (for readouts) + the propagated stream. Forward-only."""
        stream = X; taps = []
        for b in range(self.N):
            reps = self.blocks[b].infer(stream)
            taps.append(np.concatenate(reps, 1)); stream = reps[-1]
        return taps

    def train_scff(self, Xb, rng):
        stream = Xb
        for b in range(self.N):
            self.blocks[b].train_step(stream, rng)
            stream = self.blocks[b].infer(stream)[-1]

    def train_readouts_online(self, Xb, Yb):
        for b, t in enumerate(self._taps(Xb)):
            if self.readouts[b] is None:
                self.readouts[b] = MLP([t.shape[1], 32, C], b, lr=2e-3)
            self.readouts[b].train_step(t, Yb)

    def sleep(self, bufX, bufY, seed):
        taps = self._taps(bufX)
        self.readouts = [fit_readout(taps[b], bufY, seed + b, SLEEP_EP) for b in range(self.N)]

    def predict(self, X):
        taps = self._taps(X)
        return np.sum([self.readouts[b].forward(taps[b]) for b in range(self.N)], 0).argmax(1)

    def probe_concat(self, X):
        return np.concatenate(self._taps(X), 1)


def acc_matrix_metrics(a):
    """a[i,k] = acc on task k after task i (lower-tri). Returns final-all ACC proxy, BWT, forgetting."""
    T = len(a)
    final = float(np.mean([a[T - 1][k] for k in range(T)]))
    bwt = float(np.mean([a[T - 1][k] - a[k][k] for k in range(T - 1)]))
    forget = float(np.mean([max(a[i][k] for i in range(k, T)) - a[T - 1][k] for k in range(T - 1)]))
    return final, bwt, forget


def per_task_acc(predict, Xte, Yte):
    return [float((predict(Xte[np.isin(Yte, cls)]) == Yte[np.isin(Yte, cls)]).mean()) for cls in TASKS]


def run_condition(kind, Xtr, Ytr, Xte, Yte, seed):
    rng = np.random.default_rng(seed)
    pr = rng.permutation(len(Xtr))[:800]; Xpr, Ypr = Xtr[pr], Ytr[pr]   # fixed all-class probe set
    a = [[0.0] * len(TASKS) for _ in range(len(TASKS))]
    traj, scff_probe, drift = [], [], []
    prev_rep = None
    bufX, bufY = [], []

    if kind == "gd":
        gd = MLP([Xtr.shape[1], 96, 96, 96, C], seed, lr=1e-3)
        predict = gd.predict
    else:
        N, k = (1, 4) if kind.startswith("single") else (4, 1)
        stack = BlockStack(Xtr.shape[1], N, k, seed)
        predict = stack.predict

    for t, cls in enumerate(TASKS):
        m = np.isin(Ytr, cls); Xt, Yt = Xtr[m], Ytr[m]
        for _ in range(SCFF_EP):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), BATCH):
                b = idx[s:s + BATCH]
                if kind == "gd":
                    gd.train_step(Xt[b], Yt[b])
                else:
                    stack.train_scff(Xt[b], rng)
                    stack.train_readouts_online(Xt[b], Yt[b])
        bufX.append(Xt); bufY.append(Yt)
        if kind in ("single_sleep", "boosted_sleep"):   # explicit: "nosleep" also ends with "sleep"
            BX, BY = np.concatenate(bufX), np.concatenate(bufY)
            stack.sleep(BX, BY, seed)
        for kk in range(t + 1):
            a[t][kk] = per_task_acc(predict, Xte, Yte)[kk]
        traj.append(float((predict(Xte) == Yte).mean()))
        if kind != "gd":
            clf = LogisticRegression(C=1.0, max_iter=2000).fit(stack.probe_concat(Xpr), Ypr)
            scff_probe.append(float(clf.score(stack.probe_concat(Xte), Yte)))
            rep = stack.probe_concat(Xpr)
            rep = rep / (np.linalg.norm(rep, axis=1, keepdims=True) + EPS)
            drift.append(0.0 if prev_rep is None else float(np.linalg.norm(rep - prev_rep, axis=1).mean()))
            prev_rep = rep
    final, bwt, forget = acc_matrix_metrics(a)
    return dict(traj=traj, final=final, bwt=bwt, forget=forget,
                scff_probe=scff_probe or [0.0] * len(TASKS), drift=drift or [0.0] * len(TASKS))


CONDS = ["gd", "single_sleep", "boosted_sleep", "boosted_nosleep"]
LAB = {"gd": "GD-online (forget)", "single_sleep": "single-block + sleep (P1 base)",
       "boosted_sleep": "boosted-read + sleep (RECIPE)", "boosted_nosleep": "boosted-read no-sleep (rot)"}


def main():
    seeds = SEEDS[:1] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P2.6 [digits] continual veto | conds={CONDS} | seeds={seeds} ===", flush=True)
    runs = {c: [] for c in CONDS}
    for s in seeds:
        Xtr, Ytr, Xte, Yte = load_digits_split(s)
        for c in CONDS:
            r = run_condition(c, Xtr, Ytr, Xte, Yte, s); runs[c].append(r)
            print(f"  seed {s} {c:18s} final {r['final']:.3f}  BWT {r['bwt']:+.3f}  "
                  f"forget {r['forget']:.3f}", flush=True)

    def med(c, k): return float(np.median([r[k] for r in runs[c]]))
    def iqr(c, k):
        v = [r[k] for r in runs[c]]; return float(np.percentile(v, 25)), float(np.percentile(v, 75))

    print(f"\n--- P2.6 [digits] median, n={len(seeds)} ---")
    for c in CONDS:
        lo, hi = iqr(c, "bwt")
        print(f"  {LAB[c]:34s} final {med(c,'final'):.3f}  BWT {med(c,'bwt'):+.3f}[{lo:+.3f},{hi:+.3f}]  "
              f"forget {med(c,'forget'):.3f}")
    base_bwt = med("single_sleep", "bwt"); rec_bwt = med("boosted_sleep", "bwt")
    base_fin = med("single_sleep", "final"); rec_fin = med("boosted_sleep", "final")
    verdict = ("PASS — boosted-read PRESERVES the continual win" if rec_bwt >= base_bwt - 0.02
               else "FAIL — boosted-read worsens BWT vs single-block (depth costs continual stability)")
    print(f"\n  VETO: boosted-read BWT {rec_bwt:+.3f} vs single-block {base_bwt:+.3f} "
          f"(final {rec_fin:.3f} vs {base_fin:.3f}) -> {verdict}")
    print(f"  SCFF probe (recipe, all-class) {np.round(np.median([r['scff_probe'] for r in runs['boosted_sleep']],0),3)} "
          f"(flat = SCFF doesn't forget)")

    OUT = os.path.join(_HERE, "figs_exp6_digits"); os.makedirs(OUT, exist_ok=True)
    saved = {}
    for c in CONDS:
        for k in ["traj", "final", "bwt", "forget", "scff_probe", "drift"]:
            saved[f"{c}__{k}"] = np.array([r[k] for r in runs[c]])
    saved["seeds"] = np.array(seeds); saved["tasks"] = np.array(["+%d,%d" % (a, b) for a, b in TASKS])
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v, dtype=object) if k == "tasks"
                                                 else np.array(v) for k, v in saved.items()})
    manifest = {"experiment": "exp6-digits", "git_commit": _git(), "seeds": list(seeds), "tasks": TASKS,
                "cell": CELL, "conds": CONDS,
                "results_median": {c: {"final": med(c, "final"), "bwt": med(c, "bwt"),
                                       "forget": med(c, "forget")} for c in CONDS},
                "veto": verdict, "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_exp6
        plot_exp6.draw_all(np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True), OUT)
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
