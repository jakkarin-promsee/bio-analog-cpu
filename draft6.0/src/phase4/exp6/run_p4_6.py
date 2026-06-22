"""
Experiment P4.6 — noise robustness (A7): the substrate axis. The whole project is an ANALOG chip — weights are
charge on capacitors (Scaps), read/written with noise. Forward-only/local learning is repeatedly reported MORE
hardware-noise-robust than backprop (Distance-Forward; the analog-IMC corpus). So this is where OURS is *expected
to win* a static axis, and it directly tests the substrate thesis.

Method: train each racer CLEAN, then inject multiplicative Gaussian WEIGHT noise (W -> W*(1 + sigma*N(0,1)) — the
analog Scap programming/read-noise model) at eval, sweep sigma, measure the degradation curve. (Activation/PVT
realism is the deferred fuller layer — rule #7; weight noise IS the Scap story and is the cheap, decisive probe.)
Task: the canonical flat make_gauss (dim 40, 4-class, overlap 0.7). Racers: OURS / tuned BP / Mono. Metric: accuracy
vs sigma + RETENTION acc(sigma)/acc(0) (the robustness read). 5 seeds, 5 noise draws/cell.

CHECKPOINTED per seed. Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_6.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase3"))          # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p4lib import make_gauss, MonoForward, fit_readout, n_w            # noqa: E402
from p3lib import SCFFContrastOLU                                      # noqa: E402
from models_extra import MLP, match_width                             # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
SIGMAS = [0.0, 0.05, 0.1, 0.2, 0.4]                                   # multiplicative weight-noise std
DIM, NCLASS, NCLUST, OVERLAP = 40, 4, 16, 0.7
NTR, NTE = 4000, 1500
L, WD, WIN = 4, 64, 2
REPS = 5                                                              # noise draws averaged per (sigma)
OUT = os.path.join(_HERE, "figs_p4_6")


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
                r = json.loads(line); done[r["seed"]] = r
    return done


def _mul(Ws, sigma, rng):
    return [W * (1.0 + sigma * rng.standard_normal(W.shape)) for W in Ws]


def noisy_ours(m, ro, Xte, Yte, sigma, rng):
    W0 = [W.copy() for W in m.W]; r0 = [W.copy() for W in ro.W]; accs = []
    for _ in range(REPS):
        m.W = _mul(W0, sigma, rng); ro.W = _mul(r0, sigma, rng)
        F = np.concatenate(m.infer(Xte), 1)
        accs.append(float((ro.predict(F) == Yte).mean()))
    m.W = W0; ro.W = r0
    return float(np.mean(accs))


def noisy_mlp(m, Xte, Yte, sigma, rng):
    W0 = [W.copy() for W in m.W]; accs = []
    for _ in range(REPS):
        m.W = _mul(W0, sigma, rng); accs.append(float(m.accuracy(Xte, Yte)))
    m.W = W0
    return float(np.mean(accs))


def noisy_mono(m, Xte, Yte, sigma, rng):
    W0 = [W.copy() for W in m.W]; M0 = [M.copy() for M in m.M]; accs = []
    for _ in range(REPS):
        m.W = _mul(W0, sigma, rng); m.M = _mul(M0, sigma, rng)
        accs.append(float((m.predict(Xte) == Yte).mean()))
    m.W = W0; m.M = M0
    return float(np.mean(accs))


def train_bp_model(Xtr, Ytr, Xte, Yte, dims, seed):
    best = None
    for lr in (3e-3, 1e-3, 3e-4):
        for wd in (0.0, 1e-3):
            m = MLP(dims, seed, lr=lr, l2=wd); rng = np.random.default_rng(seed)
            for _ in range(60):
                idx = rng.permutation(len(Xtr))
                for s in range(0, len(Xtr), 32):
                    m.train_step(Xtr[idx[s:s + 32]], Ytr[idx[s:s + 32]])
            te = m.accuracy(Xte, Yte)
            if best is None or te > best[1]:
                best = (m, te)
    return best[0]


def run_cell(seed):
    rng = np.random.default_rng(seed)
    Xtr, Ytr, _ = make_gauss(NTR, rng, dim=DIM, n_class=NCLASS, n_clusters=NCLUST, overlap=OVERLAP)
    Xte, Yte, _ = make_gauss(NTE, np.random.default_rng(seed + 7), dim=DIM, n_class=NCLASS,
                             n_clusters=NCLUST, overlap=OVERLAP)
    total = n_w([DIM] + [WD] * L) + n_w([L * WD, 32, NCLASS]); bw, _ = match_width(total, DIM, NCLASS, L)
    dims = [DIM] + [bw] * L + [NCLASS]
    # OURS
    m = SCFFContrastOLU([DIM] + [WD] * L, seed=seed, window=WIN, mask_ratio=0.5, temp=0.5)
    r = np.random.default_rng(seed)
    for _ in range(25):
        idx = r.permutation(len(Xtr))
        for s in range(0, len(Xtr), 32):
            xb = Xtr[idx[s:s + 32]]
            if len(xb) >= 4:
                m.train_step(xb, r)
    ro = fit_readout(np.concatenate(m.infer(Xtr), 1), Ytr, NCLASS, seed)
    bp = train_bp_model(Xtr, Ytr, Xte, Yte, dims, seed)
    mo = MonoForward(dims, NCLASS, seed=seed); rr = np.random.default_rng(seed)
    for _ in range(40):
        idx = rr.permutation(len(Xtr))
        for s in range(0, len(Xtr), 32):
            mo.train_step(Xtr[idx[s:s + 32]], Ytr[idx[s:s + 32]])
    nrng = np.random.default_rng(seed + 555)
    ours = [noisy_ours(m, ro, Xte, Yte, sg, nrng) for sg in SIGMAS]
    bpn = [noisy_mlp(bp, Xte, Yte, sg, nrng) for sg in SIGMAS]
    mon = [noisy_mono(mo, Xte, Yte, sg, nrng) for sg in SIGMAS]
    return dict(seed=seed, ours=ours, bp=bpn, mono=mon)


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.6 weight-noise robustness | sigmas={SIGMAS} | seeds={seeds} | {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for s in seeds:
        if s in done:
            continue
        r = run_cell(s); done[s] = r
        fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        print(f"  seed {s}: OURS {r['ours'][0]:.3f}->{r['ours'][-1]:.3f}  BP {r['bp'][0]:.3f}->{r['bp'][-1]:.3f}  "
              f"Mono {r['mono'][0]:.3f}->{r['mono'][-1]:.3f}  (sigma 0->{SIGMAS[-1]})", flush=True)
    fck.close()

    rows = list(done.values())
    def stack(k): return np.array([r[k] for r in rows])                # [n_seed, n_sigma]
    ours, bp, mono = stack("ours"), stack("bp"), stack("mono")
    mo_, mb, mm = np.median(ours, 0), np.median(bp, 0), np.median(mono, 0)
    ret = lambda M: np.median(M / M[:, :1], 0)                         # retention acc(sigma)/acc(0), median over seeds
    print(f"\n--- P4.6 median over seeds, n={len(seeds)} ---")
    print(f"{'sigma':>6} {'OURS':>6} {'BP':>6} {'Mono':>6} | {'OURSret':>7} {'BPret':>7} {'Monoret':>7}")
    ro_, rb, rm = ret(ours), ret(bp), ret(mono)
    for i, sg in enumerate(SIGMAS):
        print(f"{sg:6.2f} {mo_[i]:6.3f} {mb[i]:6.3f} {mm[i]:6.3f} | {ro_[i]:7.3f} {rb[i]:7.3f} {rm[i]:7.3f}")
    print(f"\n  retention @sigma={SIGMAS[-1]}: OURS {ro_[-1]:.3f}  BP {rb[-1]:.3f}  Mono {rm[-1]:.3f} "
          f"(higher = more noise-robust)", flush=True)

    np.savez(os.path.join(OUT, "arrays.npz"), sigmas=np.array(SIGMAS),
             ours=mo_, bp=mb, mono=mm, ours_ret=ro_, bp_ret=rb, mono_ret=rm,
             ours_all=ours, bp_all=bp, mono_all=mono, seeds=np.array(seeds))
    json.dump({"experiment": "p4_6", "git_commit": _git(), "seeds": list(seeds), "sigmas": SIGMAS,
               "noise": "multiplicative weight", "reps": REPS, "task": "make_gauss flat 4-class",
               "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_6 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
