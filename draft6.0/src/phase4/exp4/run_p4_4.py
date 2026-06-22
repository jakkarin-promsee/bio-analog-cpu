"""
Experiment P4.4 — class count (A5) + real-data anchors. Does the cheap brain hold as the label space grows? And
does the synthetic story survive REAL flat input?

Synthetic sweep: FIXED cluster geometry (40 clusters, dim 40, overlap 0.6) — only the label granularity changes
(each cluster -> random class in {0..C-1}), C in [2,4,10,20]. Same input distribution, finer labels -> a clean
"class count" dial. Exact Bayes per cell (chance = 1/C scales, capture normalizes it out).

Real anchors (confirmatory, overlaid at their class count): digits (64-D, 10-class) full-rigor; CIFAR-flat (3072-D,
10-class) lighter (3 seeds, lighter BP grid — it's a confirmatory point, not the swept axis, and 218k-weight nets at
3072-D are expensive). Racers: OURS / tuned BP / Mono-Forward.

CHECKPOINTED per (kind, key, seed). Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_4.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase3", "exp0"))  # run_p3_0 (CIFAR loader)
from p4lib import make_gauss, bayes_error, race_ours, race_bp, race_mono, n_w   # noqa: E402
from models_extra import match_width                                   # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
NCLASSES = [2, 4, 10, 20]
NCLUST, DIM, OVERLAP = 40, 40, 0.6                                     # fixed geometry; only labels change
NTR, NTE = 4000, 1500
L, WD, WIN = 4, 64, 2
OUT = os.path.join(_HERE, "figs_p4_4")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                r = json.loads(line); done[(r["kind"], r["key"], r["seed"])] = r
    return done


def _budget_and_dims(D, C):
    total = n_w([D] + [WD] * L) + n_w([L * WD, 32, C])
    bw, _ = match_width(total, D, C, L)
    return total, [D] + [bw] * L + [C]


def run_synth(C, seed):
    rng = np.random.default_rng(seed)
    Xtr, Ytr, params = make_gauss(NTR, rng, dim=DIM, n_class=C, n_clusters=NCLUST, overlap=OVERLAP)
    Xte, Yte, _ = make_gauss(NTE, np.random.default_rng(seed + 7), dim=DIM, n_class=C,
                             n_clusters=NCLUST, overlap=OVERLAP)
    bayes = bayes_error(params, np.random.default_rng(seed + 99), n=20000)
    total, mono_dims = _budget_and_dims(DIM, C)
    o = race_ours(Xtr, Ytr, Xte, Yte, C, L=L, Wd=WD, w=WIN, seed=seed)
    b = race_bp(Xtr, Ytr, Xte, Yte, C, total=total, in_dim=DIM, seed=seed)
    mo = race_mono(Xtr, Ytr, Xte, Yte, C, dims=mono_dims, seed=seed)
    return dict(kind="synth", key=C, seed=seed, n_class=C, bayes=bayes, chance=1.0 / C,
                ours_te=o["acc_te"], ours_tr=o["acc_tr"], ours_bwd=o["bwd"],
                bp_te=b["acc_te"], bp_tr=b["acc_tr"], bp_bwd=b["bwd"],
                mono_te=mo["acc_te"], mono_tr=mo["acc_tr"], mono_bwd=mo["bwd"],
                gap=float(b["acc_te"] - o["acc_te"]),
                capture=float((o["acc_te"] - 1.0 / C) / max(1e-6, (1 - bayes) - 1.0 / C)))


def _load_real(dataset, seed):
    if dataset == "digits":
        from sklearn.datasets import load_digits
        d = load_digits(); X = d.data / 16.0; Y = d.target
        rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
        ntr = 1250; tr, te = idx[:ntr], idx[ntr:]
        return X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te], 10
    from run_p3_0 import load_cifar_local
    X, Y = load_cifar_local(); rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:4000], idx[4000:5500]
    return X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te], 10


def run_real(dataset, seed):
    Xtr, Ytr, Xte, Yte, C = _load_real(dataset, seed)
    D = Xtr.shape[1]; total, mono_dims = _budget_and_dims(D, C)
    o = race_ours(Xtr, Ytr, Xte, Yte, C, L=L, Wd=WD, w=WIN, seed=seed)
    if dataset == "cifar":                                            # lighter BP (confirmatory point, 3072-D is dear)
        b = race_bp(Xtr, Ytr, Xte, Yte, C, total=total, in_dim=D, depths=(2, 4),
                    lrs=(1e-2, 1e-3, 3e-4), wds=(0.0, 1e-3), ep=40, seed=seed)
    else:
        b = race_bp(Xtr, Ytr, Xte, Yte, C, total=total, in_dim=D, seed=seed)
    mo = race_mono(Xtr, Ytr, Xte, Yte, C, dims=mono_dims, seed=seed)
    return dict(kind="real", key=dataset, seed=seed, n_class=C, dim=D, bayes=-1.0, chance=1.0 / C,
                ours_te=o["acc_te"], ours_tr=o["acc_tr"], ours_bwd=o["bwd"],
                bp_te=b["acc_te"], bp_tr=b["acc_tr"], bp_bwd=b["bwd"],
                mono_te=mo["acc_te"], mono_tr=mo["acc_tr"], mono_bwd=mo["bwd"],
                gap=float(b["acc_te"] - o["acc_te"]), capture=-1.0)


def main():
    quick = "--quick" in sys.argv
    classes = NCLASSES[:2] if quick else NCLASSES
    seeds = SEEDS[:2] if quick else SEEDS
    # digits = primary real anchor (cheap, clean, 10-class, full rigor); CIFAR-flat = single-seed sanity point
    # only (3072-D OURS is minutes-slow, AND CIFAR-flat is already the fully-characterized "wall" from Phase 2/3).
    real_jobs = [("digits", seeds)] if quick else [("digits", SEEDS), ("cifar", SEEDS[:1])]
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.4 class-count + real anchors | C={classes} | seeds={seeds} | reals={[r[0] for r in real_jobs]} "
          f"| {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for C in classes:
        for s in seeds:
            if ("synth", C, s) in done:
                continue
            r = run_synth(C, s); done[("synth", C, s)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  synth C{C:>2} seed {s}: bayes {r['bayes']:.3f} chance {r['chance']:.3f} | "
                  f"OURS {r['ours_te']:.3f} BP {r['bp_te']:.3f} Mono {r['mono_te']:.3f} | gap {r['gap']:+.3f} "
                  f"cap {r['capture']:.2f}", flush=True)
    for dataset, dseeds in real_jobs:
        for s in dseeds:
            if ("real", dataset, s) in done:
                continue
            r = run_real(dataset, s); done[("real", dataset, s)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  real {dataset:>6} seed {s}: OURS {r['ours_te']:.3f} BP {r['bp_te']:.3f} "
                  f"Mono {r['mono_te']:.3f} | gap {r['gap']:+.3f}", flush=True)
    fck.close()

    rows = list(done.values())
    print(f"\n--- P4.4 synth median over seeds ---")
    print(f"{'C':>3} {'bayes':>6} {'chance':>6} {'OURS':>6} {'BP':>6} {'Mono':>6} {'gap':>7} {'cap':>6}")
    agg = []
    for C in classes:
        rs = [r for r in rows if r["kind"] == "synth" and r["key"] == C]
        if not rs:
            continue
        def md(k): return float(np.median([r[k] for r in rs]))
        agg.append(dict(n_class=C, bayes=md("bayes"), chance=1.0 / C, ours=md("ours_te"), bp=md("bp_te"),
                        mono=md("mono_te"), ours_tr=md("ours_tr"), bp_tr=md("bp_tr"), mono_tr=md("mono_tr"),
                        gap=md("gap"), capture=md("capture"), ours_bwd=rs[0]["ours_bwd"], bp_bwd=rs[0]["bp_bwd"]))
        a = agg[-1]
        print(f"{C:>3} {a['bayes']:6.3f} {a['chance']:6.3f} {a['ours']:6.3f} {a['bp']:6.3f} {a['mono']:6.3f} "
              f"{a['gap']:+7.3f} {a['capture']:6.2f}")
    reals = {}
    for dataset in set(r["key"] for r in rows if r["kind"] == "real"):
        rs = [r for r in rows if r["kind"] == "real" and r["key"] == dataset]
        def md(k): return float(np.median([r[k] for r in rs]))
        reals[dataset] = dict(n_class=rs[0]["n_class"], ours=md("ours_te"), bp=md("bp_te"), mono=md("mono_te"),
                              gap=md("gap"))
        print(f"  REAL {dataset}: OURS {reals[dataset]['ours']:.3f} BP {reals[dataset]['bp']:.3f} "
              f"Mono {reals[dataset]['mono']:.3f} gap {reals[dataset]['gap']:+.3f}")

    np.savez(os.path.join(OUT, "arrays.npz"),
             n_class=np.array([a["n_class"] for a in agg]),
             **{k: np.array([a[k] for a in agg]) for k in ("bayes", "chance", "ours", "bp", "mono",
                                                           "ours_tr", "bp_tr", "mono_tr", "gap", "capture",
                                                           "ours_bwd", "bp_bwd")},
             real_names=np.array(list(reals.keys())),
             real_nclass=np.array([reals[d]["n_class"] for d in reals]),
             real_ours=np.array([reals[d]["ours"] for d in reals]),
             real_bp=np.array([reals[d]["bp"] for d in reals]),
             real_mono=np.array([reals[d]["mono"] for d in reals]),
             real_gap=np.array([reals[d]["gap"] for d in reals]), seeds=np.array(seeds))
    json.dump({"experiment": "p4_4", "git_commit": _git(), "classes": classes, "n_clusters": NCLUST,
               "dim": DIM, "overlap": OVERLAP, "reals": list(reals.keys()), "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)}, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_4 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
