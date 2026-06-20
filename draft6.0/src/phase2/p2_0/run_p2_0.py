"""
Experiment P2.0 — re-establish the wall + the decisive test (lost vs entangled).

Per seed, per task:
  (1) WALL      — deep SCFF (lengthnorm + squared goodness, L=8, w=64): per-layer linear probe (F3+ the wall),
                  dead-unit fraction, effective rank (the deactivation/collapse cause, DeeperForward).
  (2) CEILING   — pure-GD MLP (6 hidden, matched weight budget): held-out (the ceiling) + per-layer hidden
                  probe (the GD-hidden envelope, flat-high reference).
  (3) DECIDE    — max-power readout (deep MLP, to convergence) on FROZEN deep-SCFF all-layer features vs the
                  pure-GD held-out:  < GD - 0.05 => LOST ; ~= GD => ENTANGLED.  (routes the phase)
  (4) WIDTHxDEPTH (F6+) — narrow-deep (64x6) vs wide-shallow (~Wx2) SCFF at EQUAL weight budget, tapped
                  readout held-out: the substrate-collision gap = one number to close.

5 seeds [42,137,271,314,1729], median + IQR. Reuses p2lib (pluggable SCFF) + phase1 models_extra (MLP,
match_width). Saves arrays.npz + manifest.json; plot_p2_0.py regenerates every figure.

Run:  python run_p2_0.py synth        (default; fast, no network)
      python run_p2_0.py cifar        (CIFAR-10 flat-MLP, the documented wall; fetch via openml ~170MB)
      add --quick for 2 seeds.
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                       # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p2lib import SCFF2, probe_per_layer, probe_one, effective_rank, make_tierb  # noqa: E402
from models_extra import MLP, match_width, RandomProjStack                       # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
L, WIDTH, BATCH = 8, 64, 32

CFG = {
    "synth": dict(n_train=6000, n_test=2000, scff_ep=30, gd_ep=60, decide_ep=80,
                  task=dict(dim=20, grid=4, n_active=2, overlap=0.30, label="random", n_class=2)),
    "cifar": dict(n_train=5000, n_test=2000, scff_ep=20, gd_ep=40, decide_ep=60, task=None),
}


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ----------------------------------------------------------------------------- data
_CIFAR_CACHE = None
_CIFAR_GZ = os.path.expanduser(
    "~/scikit_learn_data/openml/openml.org/data/v1/download/16797613/CIFAR_10.arff.gz")


def load_cifar_local(path=_CIFAR_GZ):
    """CIFAR-10 parsed DIRECTLY from the locally-cached OpenML ARFF.gz, bypassing sklearn's md5
    check. Why: fetch_openml is broken on this machine — the download truncates (~26k of 60k rows)
    so the md5 never matches and it errors. The cached gz decompresses cleanly and its ~25.7k rows
    are class-balanced over all 10 classes (verified ~2.5k each) — ample for a 5k/2k flat-MLP depth
    PROBE (CIFAR here is a probe, NOT a benchmark claim; README §2). Returns X in [0,1] float32
    [N,3072], Y int64 [N]; parsed once, module-cached."""
    global _CIFAR_CACHE
    if _CIFAR_CACHE is not None:
        return _CIFAR_CACHE
    import gzip
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"CIFAR cache missing at {path}. OpenML fetch is broken here (md5 mismatch / truncated "
            f"download); point load_cifar_local at a local CIFAR_10.arff.gz copy.")
    X = np.empty((30000, 3072), dtype=np.float32); Y = np.empty(30000, dtype=np.int64); i = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        indata = False
        for line in f:
            if not indata:
                if line.strip().lower() == "@data":
                    indata = True
                continue
            vals = line.rstrip("\n").split(",")
            if len(vals) != 3073:                 # skip header noise + the 1 truncated tail row
                continue
            X[i] = np.array(vals[:3072], dtype=np.float32); Y[i] = int(vals[3072]); i += 1
    X = X[:i]; Y = Y[:i]; X /= 255.0
    _CIFAR_CACHE = (X, Y)
    return _CIFAR_CACHE


def load_task(name, seed):
    c = CFG[name]
    if name == "synth":
        t = c["task"]
        Xtr, Ytr = make_tierb(c["n_train"], np.random.default_rng(seed + 1), **t)
        Xte, Yte = make_tierb(c["n_test"], np.random.default_rng(seed + 2), **t)
        return Xtr, Ytr, Xte, Yte, int(t["n_class"]), Xtr.shape[1]
    if name == "cifar":
        X, Y = load_cifar_local()
        rng = np.random.default_rng(seed)
        idx = rng.permutation(len(X))
        tr, te = idx[:c["n_train"]], idx[c["n_train"]:c["n_train"] + c["n_test"]]
        return (X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te],
                int(Y.max() + 1), X.shape[1])
    raise ValueError(name)


def n_w(dims):
    return sum((dims[i] + 1) * dims[i + 1] for i in range(len(dims) - 1))


def train_scff(dims, kw, Xtr, seed, epochs):
    m = SCFF2(dims, seed=seed, **kw)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], rng)
    return m


def train_mlp(dims, Xtr, Ytr, Xte, Yte, seed, epochs, lr=1e-3):
    m = MLP(dims, seed, lr=lr)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    return m, float(m.accuracy(Xte, Yte))


def gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte):
    gd.forward(Xtr); htr = [a.copy() for a in gd.cache[1:]]
    gd.forward(Xte); hte = [a.copy() for a in gd.cache[1:]]
    return [probe_one(a, Ytr, b, Yte) for a, b in zip(htr, hte)]


# ----------------------------------------------------------------------------- one seed
WALL = dict(norm="lengthnorm", goodness="squared")   # the Phase-1 wall config, two-sided theta=2.0
# (The DeeperForward candidate — layernorm + linear + contrast — is a P2.1 lever, NOT P2.0. P2.0 is the
#  wall ALONE: one SCFF config, so the degradation curve every later lever must bend up exists cleanly.
#  Note from the synth preview: layernorm+linear scored ~= the wall here because synth has no depth-wall
#  to bend; that pre-result is logged for P2.1, where the full goodness x norm grid runs on CIFAR-flat.)


def run_seed(name, seed):
    c = CFG[name]
    Xtr, Ytr, Xte, Yte, C, D = load_task(name, seed)
    out = {"C": C, "D": D}

    # (1) WALL — deep SCFF, per-layer probe + dead + erank
    scff = train_scff([D] + [WIDTH] * L, WALL, Xtr, seed, c["scff_ep"])
    out["wall_probe"] = probe_per_layer(scff, Xtr, Ytr, Xte, Yte)
    out["wall_dead"] = scff.dead_fraction(Xte).tolist()
    out["wall_erank"] = [effective_rank(a) for a in scff.infer(Xte)]
    out["wall_gap"] = scff.goodness_gap(Xte).tolist()

    # (2) CEILING — pure-GD at MATCHED DEPTH (L hidden) + matched weight budget, so its per-layer
    #     hidden probe spans the SAME 1..L axis as the SCFF stacks (the exp-1 F3 format: aligned x).
    scff_budget = n_w([D] + [WIDTH] * L) + (L * WIDTH * C + C)   # stack + an all-tap linear head
    w, _ = match_width(scff_budget, D, C, L)
    gd_dims = [D] + [w] * L + [C]
    gd, out["gd_held"] = train_mlp(gd_dims, Xtr, Ytr, Xte, Yte, seed, c["gd_ep"])
    out["gd_perlayer"] = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)
    out["gd_width"] = w

    # (3) DECIDE — max-power readout on frozen deep-SCFF, WITH selectivity controls.
    #   A powerful nonlinear probe has LOW selectivity (Hewitt & Liang 2019): high acc on frozen
    #   features can mean the PROBE solved the task, not that SCFF *encoded* it. So run the SAME
    #   max-power MLP on three feature sets and compare to the pure-GD ceiling:
    #     SCFF : frozen deep-SCFF all-tap     (the representation under test)
    #     RAND : frozen random-proj all-tap   (same arch/dims, UNTRAINED) -> the selectivity floor
    #     RAW  : raw input                     (can the probe solve it alone? -> is DECIDE informative?)
    #   selectivity = SCFF - RAND = what SCFF *training* added that the probe can read. A small
    #   selectivity means an "entangled" verdict is probe-driven, not a property of SCFF.
    def decide_mlp(Ft, Fe):
        return train_mlp([Ft.shape[1], 256, 128, C], Ft, Ytr, Fe, Yte, seed, c["decide_ep"])[1]
    Ftr = np.concatenate(scff.infer(Xtr), axis=1)
    Fte = np.concatenate(scff.infer(Xte), axis=1)
    rp = RandomProjStack([D] + [WIDTH] * L, seed)                     # matched arch, no learning
    Rtr = np.concatenate(rp.infer(Xtr), axis=1)
    Rte = np.concatenate(rp.infer(Xte), axis=1)
    out["decide_scff"] = decide_mlp(Ftr, Fte)
    out["decide_rand"] = decide_mlp(Rtr, Rte)
    out["decide_raw"] = decide_mlp(Xtr, Xte)
    out["decide_gap"] = float(out["gd_held"] - out["decide_scff"])           # vs ceiling: >0.05 => LOST
    out["decide_selectivity"] = float(out["decide_scff"] - out["decide_rand"])  # validity check
    out["decide_verdict"] = "lost" if out["decide_gap"] > 0.05 else "entangled"

    # (4) WIDTH x DEPTH (F6+) — narrow-deep vs wide-shallow at equal SCFF weight budget
    nd_dims = [D] + [WIDTH] * 6
    target = n_w(nd_dims)
    W2 = max(int(c["n_test"]), 8)  # placeholder; pick W2 so a 2-layer stack ~= target
    best, bw = None, None
    for cand in range(WIDTH, 4000, 8):
        nw = n_w([D, cand, cand])
        if best is None or abs(nw - target) < abs(best - target):
            best, bw = nw, cand
    ws_dims = [D, bw, bw]
    nd = train_scff(nd_dims, WALL, Xtr, seed, c["scff_ep"])
    ws = train_scff(ws_dims, WALL, Xtr, seed, c["scff_ep"])
    nd_acc = probe_one(np.concatenate(nd.infer(Xtr), 1), Ytr, np.concatenate(nd.infer(Xte), 1), Yte)
    ws_acc = probe_one(np.concatenate(ws.infer(Xtr), 1), Ytr, np.concatenate(ws.infer(Xte), 1), Yte)
    out["nd_acc"], out["ws_acc"] = nd_acc, ws_acc
    out["wd_gap"] = float(ws_acc - nd_acc)                            # +ve => wide-shallow wins (the gap)
    out["nd_w"], out["ws_w"], out["ws_width"] = target, best, bw
    return out


# ----------------------------------------------------------------------------- aggregate
def main():
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "synth"
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P2.0 [{name}] wall + DECIDE + widthxdepth | seeds={seeds} ===", flush=True)
    runs = []
    for s in seeds:
        r = run_seed(name, s)
        runs.append(r)
        print(f"  seed {s}: wall L1->L{L} {r['wall_probe'][0]:.3f}->{r['wall_probe'][-1]:.3f} "
              f"(dead {r['wall_dead'][-1]:.2f}) | GD {r['gd_held']:.3f} | "
              f"DECIDE scff {r['decide_scff']:.3f} rand {r['decide_rand']:.3f} raw {r['decide_raw']:.3f} "
              f"= {r['decide_verdict']} (gap {r['decide_gap']:+.3f}, select {r['decide_selectivity']:+.3f})"
              f" | wd_gap {r['wd_gap']:+.3f}", flush=True)

    def st(k): return np.array([r[k] for r in runs])
    def med(k): return np.median(st(k), 0)
    def iqr(k):
        a = st(k); return np.percentile(a, 25, 0), np.percentile(a, 75, 0)

    wall = med("wall_probe"); gdpl = med("gd_perlayer")
    slope = float(np.polyfit(np.arange(1, L + 1), wall, 1)[0])
    env_gap = float(np.median(gdpl) - np.median(wall))
    dg = st("decide_gap")
    verdict = "LOST" if np.median(dg) > 0.05 else "ENTANGLED"
    print(f"\n--- P2.0 [{name}] median, n={len(seeds)} ---")
    print(f"  WALL probe/layer : {np.round(wall, 3)}  slope {slope:+.4f}/layer "
          f"({'DECLINES' if slope < 0 else 'RISES/FLAT'})  [lengthnorm+squared]")
    print(f"  GD-hidden envel. : {np.round(gdpl, 3)}  (envelope gap vs wall ~ {env_gap:+.3f})")
    print(f"  dead/layer       : {np.round(med('wall_dead'), 2)}")
    print(f"  erank/layer      : {np.round(med('wall_erank'), 1)}")
    sel = st("decide_selectivity")
    print(f"  DECIDE           : SCFF {np.median(st('decide_scff')):.3f}  rand "
          f"{np.median(st('decide_rand')):.3f}  raw {np.median(st('decide_raw')):.3f}  vs GD "
          f"{np.median(st('gd_held')):.3f}")
    print(f"    gap-vs-ceiling : {np.median(dg):+.3f} [{np.percentile(dg,25):+.3f},"
          f"{np.percentile(dg,75):+.3f}] -> {verdict}")
    print(f"    selectivity    : {np.median(sel):+.3f} [{np.percentile(sel,25):+.3f},"
          f"{np.percentile(sel,75):+.3f}]  "
          f"({'OK: SCFF adds readable info' if np.median(sel) > 0.03 else 'LOW: probe may be doing the work'})")
    print(f"  WIDTHxDEPTH      : wide-shallow {np.median(st('ws_acc')):.3f} (w={runs[0]['ws_width']}) vs "
          f"narrow-deep {np.median(st('nd_acc')):.3f}  gap {np.median(st('wd_gap')):+.3f}")

    OUT = os.path.join(_HERE, f"figs_p2_0_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {k: st(k) for k in runs[0].keys() if k != "decide_verdict"}
    saved["seeds"] = np.array(seeds); saved["L"] = L; saved["width"] = WIDTH
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in saved.items()})
    manifest = {"experiment": f"p2_0-{name}", "git_commit": _git(), "seeds": list(seeds),
                "task": name, "config": {k: v for k, v in CFG[name].items()},
                "wall_config": WALL, "L": L, "width": WIDTH, "batch": BATCH,
                "results_median": {"wall_slope": slope, "envelope_gap": env_gap,
                                   "decide_scff": float(np.median(st("decide_scff"))),
                                   "decide_rand": float(np.median(st("decide_rand"))),
                                   "decide_raw": float(np.median(st("decide_raw"))),
                                   "decide_gap": float(np.median(dg)),
                                   "decide_selectivity": float(np.median(sel)),
                                   "decide_verdict": verdict,
                                   "wd_gap": float(np.median(st("wd_gap")))},
                "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    try:
        import plot_p2_0
        plot_p2_0.draw_all(np.load(os.path.join(OUT, "arrays.npz")), name, OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
