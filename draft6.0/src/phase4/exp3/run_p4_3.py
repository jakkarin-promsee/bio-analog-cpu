"""
Experiment P4.3 — width x depth (A4): the Scap-budget Pareto. At a FIXED total weight budget (the substrate's real
constraint — Scaps are finite), how should you spend it: wide-shallow or narrow-deep? And does the answer differ by
TASK REGIME? This ties P4.2 (depth pays on a headroom task) to Phase-1/2 (wide-shallow wins on a flat task).

Design: TWO sweeps.
  (1) ISO-BUDGET shape sweep (mode "iso"): fix total weights B (= the canonical L4/W64 cell). For each depth L in
      [2,3,4,6,8,10,12] pick the OURS bulk width that hits B (so every shape spends ~the same Scaps), and match the
      BP ceiling to OURS's actual total at that shape. Walk wide-shallow (L2) -> narrow-deep (L12). Racers: OURS vs
      tuned BP (Mono dropped) + the OLD energy-Sh2 wall cell.
  (2) FIXED-WIDTH control (mode "fixw"): hold width = CTRL_W (generous, =64) and sweep depth L in [4,6,8,10,12] —
      OURS vs OLD only. ONE thing changed (depth), so it SEPARATES depth-decay from the iso-budget width-shrink
      confound (iso makes deeper = narrower; here width is constant). If OURS still droops at W64 -> decay; if it
      holds -> the iso drop was width/capacity. The decisive test of the L8+ headroom dip.
Two regimes both sweeps:
  flat     = make_gauss (overlap 0.7, Bayes ~0.108) — no depth headroom (Phase-1/2 regime)
  headroom = make_tierb (the P4.2 headroom config)  — depth pays (P4.2 regime)
Headline: accuracy vs depth per regime + the cost Pareto + the wall (per-layer probe) + the fixed-width control.

CHECKPOINTED per (mode, regime, L, seed). Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_3.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))          # p2lib (make_tierb)
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p4lib import make_gauss, race_ours, race_energy, race_bp, n_w     # noqa: E402
from p2lib import make_tierb                                           # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
DEPTHS = [2, 3, 4, 6, 8, 10, 12]                                       # wide-shallow -> narrow-deep (iso-budget)
CTRL_W = 64                                                            # fixed-width control: hold width, vary depth
CTRL_DEPTHS = [4, 6, 8, 10, 12]                                        # (decay vs width: one thing changed = depth)
REGIMES = ["flat", "headroom"]
DIM, NCLASS = 40, 4
NTR, NTE = 4000, 1500
READOUT_LAST_N = 1                                                     # the readout reads the LAST layer only =
# the realistic position a single GD head sits (top of the bulk). All-tap would let the readout BYPASS decayed
# deep layers via the early ones -> it masks the energy depth-wall (the whole point of this rung). Other Phase-4
# rungs keep all-tap (race_ours's default); only A4 measures at the readout position.
B = n_w([DIM] + [64] * 4) + n_w([4 * 64, 32, NCLASS])                  # iso-budget = the canonical L4/W64 cell
OUT = os.path.join(_HERE, "figs_p4_3")


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
                r = json.loads(line); done[(r.get("mode", "iso"), r["regime"], r["L"], r["seed"])] = r
    return done


def ours_width_for_budget(B, D, L, C):
    """Pick the OURS bulk width so bulk([D]+[W]*L) + all-tap readout([L*W,32,C]) ~= B (iso total weights)."""
    best = None
    for W in range(8, 320):
        tot = n_w([D] + [W] * L) + n_w([L * W, 32, C])
        if best is None or abs(tot - B) < abs(best[1] - B):
            best = (W, tot)
    return best


def make_regime(regime, n, seed):
    if regime == "flat":
        X, Y, _ = make_gauss(n, np.random.default_rng(seed), dim=DIM, n_class=NCLASS, n_clusters=16, overlap=0.7)
        return X, Y
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=0.6,
                      label="random", n_class=NCLASS)


def run_cell(regime, L, seed):
    Xtr, Ytr = make_regime(regime, NTR, seed + 1)
    Xte, Yte = make_regime(regime, NTE, seed + 2)
    W, ours_total = ours_width_for_budget(B, DIM, L, NCLASS)
    o = race_ours(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=W, w=2, seed=seed,
                  readout_last_n=READOUT_LAST_N, probe=True)
    e = race_energy(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=W, seed=seed,             # the OLD energy-Σh² wall cell
                    goodness="squared", norm="lengthnorm", readout_last_n=READOUT_LAST_N, probe=True)
    b = race_bp(Xtr, Ytr, Xte, Yte, NCLASS, total=ours_total, in_dim=DIM, depths=(L,), seed=seed)
    return dict(mode="iso", regime=regime, L=L, width=int(W), ours_total=int(ours_total), seed=seed,
                ours_te=o["acc_te"], ours_tr=o["acc_tr"], ours_bwd=o["bwd"], ours_probe=o["probe"],
                energy_te=e["acc_te"], energy_tr=e["acc_tr"], energy_bwd=e["bwd"], energy_probe=e["probe"],
                bp_te=b["acc_te"], bp_tr=b["acc_tr"], bp_bwd=b["bwd"], bp_width=b["width"],
                gap=float(b["acc_te"] - o["acc_te"]))


def run_ctrl_cell(regime, L, seed):
    """Fixed-width (CTRL_W) depth point — OURS vs OLD only. Width is CONSTANT across depth, so any droop is
    depth-decay, not the iso-budget width-shrink. No BP (the question is forward-only decay-vs-width)."""
    Xtr, Ytr = make_regime(regime, NTR, seed + 1)
    Xte, Yte = make_regime(regime, NTE, seed + 2)
    o = race_ours(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=CTRL_W, w=2, seed=seed,
                  readout_last_n=READOUT_LAST_N, probe=True)
    e = race_energy(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=CTRL_W, seed=seed,
                    goodness="squared", norm="lengthnorm", readout_last_n=READOUT_LAST_N, probe=True)
    return dict(mode="fixw", regime=regime, L=L, width=CTRL_W, seed=seed,
                ours_te=o["acc_te"], ours_probe=o["probe"],
                energy_te=e["acc_te"], energy_probe=e["probe"])


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    depths = DEPTHS[:2] if "--quick" in sys.argv else DEPTHS
    ctrl_depths = CTRL_DEPTHS[:2] if "--quick" in sys.argv else CTRL_DEPTHS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.3 width x depth (iso-budget B={B}) | depths={depths} | ctrl W{CTRL_W} L{ctrl_depths} | "
          f"regimes={REGIMES} | seeds={seeds} | {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for regime in REGIMES:                                              # (1) iso-budget sweep
        for L in depths:
            for s in seeds:
                if ("iso", regime, L, s) in done:
                    continue
                r = run_cell(regime, L, s); done[("iso", regime, L, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                print(f"  iso  {regime:8s} L{L} W{r['width']:>3} seed {s}: OURS {r['ours_te']:.3f}  "
                      f"OLD {r['energy_te']:.3f}  BP {r['bp_te']:.3f}  gap {r['gap']:+.3f}  "
                      f"(tot~{r['ours_total']/1000:.0f}k)", flush=True)
    for regime in REGIMES:                                             # (2) fixed-width control (decay vs width)
        for L in ctrl_depths:
            for s in seeds:
                if ("fixw", regime, L, s) in done:
                    continue
                r = run_ctrl_cell(regime, L, s); done[("fixw", regime, L, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                print(f"  fixw {regime:8s} L{L} W{CTRL_W} seed {s}: OURS {r['ours_te']:.3f}  "
                      f"OLD {r['energy_te']:.3f}", flush=True)
    fck.close()

    rows = list(done.values())
    iso_rows = [r for r in rows if r.get("mode", "iso") == "iso"]
    ctrl_rows = [r for r in rows if r.get("mode") == "fixw"]
    agg = {}; deep_L = max(depths)
    print(f"\n--- P4.3 ISO median over seeds, n={len(seeds)} | OLD = energy-Sh2 wall cell | pL = last-layer probe ---")
    for regime in REGIMES:
        print(f"[{regime}]  {'L':>2} {'W':>4} {'OURS':>6} {'OLD':>6} {'BP':>6} {'gap':>7} "
              f"{'OURSbwd':>8} {'OLDbwd':>8} {'BPbwd':>8} {'OURSpL':>7} {'OLDpL':>7}")
        a = []
        for L in depths:
            rs = [r for r in iso_rows if r["regime"] == regime and r["L"] == L]
            if not rs:
                continue
            def md(k): return float(np.median([r[k] for r in rs]))
            a.append(dict(L=L, width=rs[0]["width"], ours=md("ours_te"), energy=md("energy_te"), bp=md("bp_te"),
                          gap=md("gap"), ours_bwd=md("ours_bwd"), energy_bwd=md("energy_bwd"), bp_bwd=md("bp_bwd"),
                          ours_probe_last=float(np.median([r["ours_probe"][-1] for r in rs])),
                          energy_probe_last=float(np.median([r["energy_probe"][-1] for r in rs]))))
            x = a[-1]
            print(f"        {L:>2} {x['width']:>4} {x['ours']:6.3f} {x['energy']:6.3f} {x['bp']:6.3f} "
                  f"{x['gap']:+7.3f} {x['ours_bwd']/1000:7.0f}k {x['energy_bwd']/1000:7.0f}k "
                  f"{x['bp_bwd']/1000:7.0f}k {x['ours_probe_last']:7.3f} {x['energy_probe_last']:7.3f}")
        agg[regime] = a
        best_ours = max(a, key=lambda z: z["ours"]); best_bp = max(a, key=lambda z: z["bp"])
        print(f"   -> OURS best shape L{best_ours['L']}/W{best_ours['width']} ({best_ours['ours']:.3f}); "
              f"BP best L{best_bp['L']}/W{best_bp['width']} ({best_bp['bp']:.3f})", flush=True)

    # iso deepest-shape per-layer probe profile (within-stack decay at that shape's width), median over seeds
    profile = {}
    for rg in REGIMES:
        rs = [r for r in iso_rows if r["regime"] == rg and r["L"] == deep_L]
        if rs:
            profile[f"{rg}_ours_profile"] = np.median(np.array([r["ours_probe"] for r in rs]), axis=0)
            profile[f"{rg}_energy_profile"] = np.median(np.array([r["energy_probe"] for r in rs]), axis=0)

    # fixed-width control: last-layer acc vs depth at CONSTANT width (decay-vs-width disambiguator)
    ctrl_agg = {}; ctrl_deep_L = max(ctrl_depths); ctrl_profile = {}
    print(f"\n--- P4.3 FIXED-WIDTH control (W{CTRL_W}), n={len(seeds)} | width CONSTANT -> droop = decay not width ---")
    for regime in REGIMES:
        print(f"[{regime}]  {'L':>2} {'OURS':>6} {'OLD':>6} {'OURSpL':>7} {'OLDpL':>7}")
        ca = []
        for L in ctrl_depths:
            rs = [r for r in ctrl_rows if r["regime"] == regime and r["L"] == L]
            if not rs:
                continue
            ca.append(dict(L=L, ours=float(np.median([r["ours_te"] for r in rs])),
                           energy=float(np.median([r["energy_te"] for r in rs])),
                           ours_probe_last=float(np.median([r["ours_probe"][-1] for r in rs])),
                           energy_probe_last=float(np.median([r["energy_probe"][-1] for r in rs]))))
            x = ca[-1]
            print(f"        {L:>2} {x['ours']:6.3f} {x['energy']:6.3f} {x['ours_probe_last']:7.3f} "
                  f"{x['energy_probe_last']:7.3f}")
        ctrl_agg[regime] = ca
        rs = [r for r in ctrl_rows if r["regime"] == regime and r["L"] == ctrl_deep_L]
        if rs:
            ctrl_profile[f"ctrl_{regime}_ours_profile"] = np.median(np.array([r["ours_probe"] for r in rs]), axis=0)
            ctrl_profile[f"ctrl_{regime}_energy_profile"] = np.median(np.array([r["energy_probe"] for r in rs]), axis=0)

    iso_save = {f"{rg}_{k}": np.array([z[k] for z in agg[rg]])
                for rg in REGIMES for k in ("ours", "energy", "bp", "gap", "ours_bwd", "energy_bwd", "bp_bwd",
                                            "ours_probe_last", "energy_probe_last")}
    ctrl_save = {f"ctrl_{rg}_{k}": np.array([z[k] for z in ctrl_agg[rg]])
                 for rg in REGIMES for k in ("ours", "energy", "ours_probe_last", "energy_probe_last")}
    np.savez(os.path.join(OUT, "arrays.npz"),
             depths=np.array(depths), widths=np.array([z["width"] for z in agg[REGIMES[0]]]),
             ctrl_depths=np.array(ctrl_depths), ctrl_w=CTRL_W, ctrl_deep_L=ctrl_deep_L,
             **iso_save, **ctrl_save, **profile, **ctrl_profile,
             deep_L=deep_L, B=B, seeds=np.array(seeds))
    json.dump({"experiment": "p4_3", "git_commit": _git(), "seeds": list(seeds), "depths": depths,
               "ctrl_width": CTRL_W, "ctrl_depths": ctrl_depths, "regimes": REGIMES, "budget_weights": int(B),
               "dim": DIM, "n_class": NCLASS, "readout_last_n": READOUT_LAST_N,
               "racers": ["ours", "energy(old, Sh2)", "bp"], "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_3 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
