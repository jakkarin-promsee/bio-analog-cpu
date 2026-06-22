"""
Experiment P3.1 — cross-layer coordination (the user's Direction 1 / OLU) on the CONTRASTIVE objective.

P3.0 settled the objective: contrast (InfoNCE/CLAPP) preserves CLASS info (selectivity +0.060, above random) but
still DECLINES with depth (slope -0.016) -- each layer discriminates myopically (no cross-layer signal). P3.1
adds a COORDINATION WINDOW: layers trained in joint groups of `window` (gradient shared across the window, then
detached). window=1 == P3.0 contrast (per-layer, the baseline); window=2,4 = increasing coordination. THE
question: does coordination take the slope from -0.016 toward >= 0 while keeping selectivity > 0?

Cells: contrast window in {1,2,4} + energy-wall reference + GD-hidden ceiling + untrained random floor.
5 seeds, median+IQR. Reuses the P3.0 bench (run_p3_0 loaders/scorecard/GD-ceiling) + p3lib.SCFFContrastOLU.

Run (single-threaded -- OpenMP phantom guard):
  OMP_NUM_THREADS=1 python -u run_p3_1.py synth        (code sanity; window=1 must reproduce P3.0 contrast)
  OMP_NUM_THREADS=1 python -u run_p3_1.py cifar         (the headline)
  add --quick for 2 seeds.
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                                              # plot_p3_1
sys.path.insert(0, os.path.join(_HERE, ".."))                         # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))                 # run_p3_0 (the bench)
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))         # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p2lib import probe_per_layer, effective_rank                     # noqa: E402
from p3lib import SCFFContrastOLU                                      # noqa: E402
from run_p3_0 import (load_task, CFG, SEEDS, L, WIDTH, BATCH, n_w, train_energy,    # noqa: E402
                      train_mlp, gd_hidden_probe, scorecard)
from models_extra import match_width                                  # noqa: E402

WINDOWS = [1, 2, 4]


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def train_olu(dims, Xtr, seed, epochs, window):
    m = SCFFContrastOLU(dims, seed=seed, window=window, mask_ratio=0.5, temp=0.5)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def run_seed(name, seed):
    c = CFG[name]
    Xtr, Ytr, Xte, Yte, C, D = load_task(name, seed)
    dims = [D] + [WIDTH] * L
    out = {"C": C, "D": D, "chance": 1.0 / C}

    en = train_energy(dims, Xtr, seed, c["ep"])
    out["energy_probe"] = probe_per_layer(en, Xtr, Ytr, Xte, Yte)

    rand = SCFFContrastOLU(dims, seed=seed, window=1)                  # untrained -> selectivity floor
    out["rand_probe"] = probe_per_layer(rand, Xtr, Ytr, Xte, Yte)

    for win in WINDOWS:
        m = train_olu(dims, Xtr, seed, c["ep"], win)
        p = probe_per_layer(m, Xtr, Ytr, Xte, Yte)
        out[f"ct_w{win}"] = p
        out[f"sel_w{win}"] = (np.array(p) - np.array(out["rand_probe"])).tolist()
        out[f"dead_w{win}"] = m.dead_fraction(Xte).tolist()
        out[f"erank_w{win}"] = [effective_rank(a) for a in m.infer(Xte)]

    scff_budget = n_w(dims) + (L * WIDTH * C + C)
    w, _ = match_width(scff_budget, D, C, L)
    gd, out["gd_held"] = train_mlp([D] + [w] * L + [C], Xtr, Ytr, Xte, Yte, seed, c["gd_ep"])
    out["gd_perlayer"] = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "synth"
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P3.1 [{name}] coordination window on contrast | windows={WINDOWS} | seeds={seeds} ===", flush=True)
    runs = []
    for s in seeds:
        r = run_seed(name, s)
        msg = " | ".join(f"w{win} {r[f'ct_w{win}'][0]:.3f}->{r[f'ct_w{win}'][-1]:.3f}"
                         f"(sel {np.mean(r[f'sel_w{win}']):+.3f})" for win in WINDOWS)
        print(f"  seed {s}: {msg} | GD {r['gd_held']:.3f}", flush=True)
        runs.append(r)

    def st(k): return np.array([r[k] for r in runs])
    chance = float(np.median(st("chance")))
    print(f"\n--- P3.1 [{name}] median, n={len(seeds)} ---")
    base = scorecard(np.median(st("ct_w1"), 0), chance)
    print(f"  contrast w1 (=P3.0 baseline): slope {base['slope']:+.4f}  sel {np.median(st('sel_w1'),0).mean():+.3f}")
    best = None
    for win in WINDOWS:
        p = np.median(st(f"ct_w{win}"), 0); sc = scorecard(p, chance); sel = np.median(st(f"sel_w{win}"), 0)
        print(f"  contrast w{win}: {np.round(p,3)}  slope {sc['slope']:+.4f}  decl {sc['decline']:.3f} "
              f"tail {sc['tail_ret']:.2f}  sel(mean) {sel.mean():+.3f}")
        if (best is None or sc["slope"] > best[1]) and sel.mean() > 0.01:
            best = (win, sc["slope"], float(sel.mean()))
    en_p = np.median(st("energy_probe"), 0); gd_p = np.median(st("gd_perlayer"), 0)
    print(f"  energy-wall ref: slope {scorecard(en_p,chance)['slope']:+.4f} | GD ceiling ~{np.median(gd_p):.3f}")
    if best is not None and best[1] >= -0.005:
        verdict = (f"PASS - coordination w={best[0]} flattens the slope to {best[1]:+.4f} (sel {best[2]:+.3f}) "
                   f"-> unsupervised forward-only depth EARNED -> route P3.3 (continual veto)")
    elif best is not None and best[1] > base["slope"] + 0.004:
        verdict = (f"PARTIAL - coordination w={best[0]} improves slope {base['slope']:+.4f}->{best[1]:+.4f} "
                   f"(sel +) but not yet flat -> try direct-feedback / bigger window, else Mono-Forward (P3.2)")
    else:
        verdict = ("FAIL - coordination window doesn't bend the slope up -> direct-feedback next, "
                   "else Mono-Forward fallback (P3.2)")
    print(f"  GATE: {verdict}", flush=True)

    OUT = os.path.join(_HERE, f"figs_p3_1_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {k: st(k) for k in runs[0].keys()}
    saved.update(seeds=np.array(seeds), L=L, width=WIDTH, chance=chance, windows=np.array(WINDOWS))
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in saved.items()})
    manifest = {"experiment": f"p3_1-{name}", "git_commit": _git(), "seeds": list(seeds), "task": name,
                "windows": WINDOWS, "L": L, "width": WIDTH, "batch": BATCH, "verdict": verdict,
                "baseline_w1_slope": base["slope"], "numpy": np.__version__,
                "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p3_1 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), name, OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
