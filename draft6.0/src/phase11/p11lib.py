"""
p11lib — the Phase-11 apparatus: the LIMIT MAP. Take the FROZEN P9 two-brain object to real data + scale, honestly.
A CHIP NETLIST, not normal Python: every reuse is a *tested* p10lib primitive carried unchanged (which re-exports
p9/p8/p7/p6/p5/p4); every genuinely-new organ ships with a guard. Phase 11 MEASURES the frozen recipe (Arm A,
porthole D=40) and BUILDS pre-registered scaled instances (Arm B, recipe rule) — it tunes NOTHING in either arm;
ER-strong is re-tuned per arena on the disjoint seed-7 stream (the asymmetry runs against the home team).

The traps this file was built to NOT re-discover (design §8):
  * `cl_metrics` (p10lib), NOT `gauntlet_metrics` (never existed).                                  (F1)
  * committed config = `P10.COMMITTED_LOOP` + override cadence_every 8->4 + `P10.HEAD` ("slda").      (F2)
  * noise-σ by P10 noise-to-signal EQUIVALENCE  σ_rung = (0.6/RMS_P10-digits)·RMS_rung, computed
    once at bench, frozen — NOT the "0.6×RMS" shorthand.                                              (F3)
  * NEVER `p8cfg.SEEDS9` (contains seed 7 = the ER tuning seed). P11 9-seed = SEEDS+[1009,2027,9091,8191]. (F4)
  * real streams: the accuracy channel is PREQUENTIAL (balanced) accuracy, every learner incl. no-change;
    80/20 within-block splits feed retention/BWT only; blocks with eval-n<100 excluded from worst-point. (R2/R8)
  * two ER points on real streams (byte-matched + bigbuf); verdicts vs the STRONGER. + sgd-linear +
    first-block-frozen + no-change in every real-stream roster.                                       (R3/R5/R11)

numpy only. CPU float64. OMP_NUM_THREADS=1 by the run layer. Loaders may touch the local data cache / a cached
fetch_openml at BENCH ONLY — never inside a live cell. GD reads taps, never writes SCFF (the P2.5 envelope).
"""
from __future__ import annotations
import os
import sys
import types
import json

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase10"))
sys.path.insert(0, os.path.join(_HERE, "..", "phase9"))
sys.path.insert(0, os.path.join(_HERE, "..", "phase5"))
import p10lib as P10                                                    # noqa: E402  (re-exports the whole stack)
import p10cfg as CFG0                                                   # noqa: E402  (the pinned base config)

# the frozen loop + head (F2) — the ONLY committed-config source
COMMITTED_LOOP = dict(P10.COMMITTED_LOOP)                               # gate=ddm,trigger=error_ema,sleep=grid,cbrs,lam1
COMMITTED_LOOP_G4 = {**COMMITTED_LOOP, "cadence_every": 4}              # the grid-4 headline (8->4 override, Trap-1)
HEAD = P10.HEAD                                                         # "slda"
SEEDS = list(CFG0.SEEDS)                                                # [42,137,271,314,1729]
SEEDS9 = SEEDS + [1009, 2027, 9091, 8191]                              # F4: 9-seed set WITHOUT seed 7
DATA = os.path.join(_HERE, "data")

# frequently-used carries (import, don't retype)
make_committed_cell = P10.make_committed_cell
make_stream_head = P10.make_stream_head
readout_feats = P10.readout_feats
all_tap_feats = P10.all_tap_feats
class_balanced_reservoir = P10.class_balanced_reservoir
build_cache_p9 = P10.build_cache_p9
run_economy_p9 = P10.run_economy_p9
meter_from_trace = P10.meter_from_trace
hardware_cost_meter = P10.hardware_cost_meter
bp_replay_energy = P10.bp_replay_energy
ContinualBP = P10.ContinualBP
run_bp_stream = P10.run_bp_stream
cl_metrics = P10.cl_metrics
acc_matrix_metrics = P10.acc_matrix_metrics
NoiseModel = P10.NoiseModel
class_axis = P10.class_axis
EPS = P10.EPS


# ============================================================ config cloning (Arm A / Arm B; the recipe-guard axis)
def clone_cfg(base=CFG0, **over):
    """A namespace copy of the pinned config with ONLY the whitelisted overrides. Library functions read cfg.ATTR,
    so a SimpleNamespace with every base constant + {DIM,WIDTH,DEPTH,NCLASS,CBRS_CAP} overridden behaves bit-for-bit
    like the module for the un-overridden knobs (the recipe-freeze made mechanical)."""
    c = types.SimpleNamespace()
    for k in dir(base):
        if not k.startswith("_"):
            setattr(c, k, getattr(base, k))
    for k, v in over.items():
        setattr(c, k, v)
    return c


def _cbrs_cap(C):
    """The committed P9.3 rule: the LUT cap grows with #classes (800 @ C=10 => 80/class). Stretches lawfully."""
    return int(80 * C)


def arm_a_cfg(C):
    """Arm A — the FROZEN recipe through the porthole: D=40, W=64, L=12 bit-equal committed; only NCLASS + the
    class-count-scaled LUT cap (the committed rule, not a knob) move per arena. C=10 => the committed cfg exactly."""
    return clone_cfg(DIM=40, WIDTH=64, DEPTH=12, NCLASS=C, CBRS_CAP=_cbrs_cap(C))


def recipe_instance(D, C):
    """Arm B — the pre-registered scaling recipe: D quantized by the caller, W=ceil(1.6*D) (the committed 64/40
    ratio, held), L=12 fixed, LUT cap by the P9.3 rule; EVERY other knob bit-equal committed (recipe_guard enforces
    the whitelist)."""
    W = int(np.ceil(1.6 * D))
    return clone_cfg(DIM=int(D), WIDTH=W, DEPTH=12, NCLASS=C, CBRS_CAP=_cbrs_cap(C))


def recipe_guard(cfg, *, arm, C, verbose=True):
    """The recipe-freeze: diff a built instance against the committed config; whitelist ONLY {DIM,WIDTH,DEPTH(=12),
    NCLASS,CBRS_CAP}. ANY other knob that differs from CFG0 -> STOP (a silent tuning leak)."""
    whitelist = {"DIM", "WIDTH", "DEPTH", "NCLASS", "CBRS_CAP"}
    leaks = []
    for k in dir(CFG0):
        if k.startswith("_") or k in whitelist:
            continue
        v0 = getattr(CFG0, k)
        if callable(v0) or isinstance(v0, types.ModuleType):
            continue
        vc = getattr(cfg, k, None)
        try:
            same = bool(np.all(v0 == vc))
        except Exception:
            same = (v0 == vc)
        if not same:
            leaks.append(k)
    if arm == "A":
        ok = (cfg.DIM == 40 and cfg.WIDTH == 64 and cfg.DEPTH == 12 and not leaks)
    else:
        ok = (cfg.WIDTH == int(np.ceil(1.6 * cfg.DIM)) and cfg.DEPTH == 12 and not leaks)
    if verbose:
        print(f"  [recipe_guard arm-{arm}] D={cfg.DIM} W={cfg.WIDTH} L={cfg.DEPTH} C={cfg.NCLASS} "
              f"cap={cfg.CBRS_CAP} leaks={leaks or 'none'}  {'OK' if ok else '!! RECIPE LEAK'}", flush=True)
    return bool(ok), dict(leaks=leaks, D=cfg.DIM, W=cfg.WIDTH)


# ============================================================ arena loaders (house signature; bench-only network)
def _from_npz(name):
    d = np.load(os.path.join(DATA, name + ".npz"))
    return {k: d[k] for k in d.files}


def _digits_raw():
    from sklearn.datasets import load_digits
    d = load_digits()
    return (d.data / 16.0).astype(np.float64), d.target.astype(np.int64), 8


def _mnist_raw():
    """MNIST 784 from the local openml cache (id 554; cached on this box — offline)."""
    from sklearn.datasets import fetch_openml
    d = fetch_openml(data_id=554, as_frame=False, parser="liac-arff")
    X = np.asarray(d.data, np.float64) / 255.0
    y = np.asarray(d.target).astype(np.int64)
    return X, y, 28


def _fashion_raw():
    d = _from_npz("fashion")
    X = np.vstack([d["Xtr"], d["Xte"]]).astype(np.float64) / 255.0
    y = np.concatenate([d["ytr"], d["yte"]]).astype(np.int64)
    return X, y, 28


def _cifar10gray_raw():
    """CIFAR-10 -> grayscale -> center-crop 32->28 = 784 (shares MNIST/Fashion native space, §8 R7)."""
    from p5lib import load_cifar_flat
    Xtr, Ytr, Xte, Yte = load_cifar_flat(0, n_train=20000, n_test=6000)
    X = np.vstack([Xtr, Xte]); y = np.concatenate([Ytr, Yte]).astype(np.int64)
    # openml CIFAR_10 stores 3072 = R(1024)G(1024)B(1024) row-major -> (N,3,32,32); gray, center-crop 32->28 = 784
    img = X.reshape(-1, 3, 32, 32)
    gray = img.mean(1)[:, 2:30, 2:30].reshape(-1, 784)
    gray = (gray - gray.min()) / (np.ptp(gray) + EPS)
    return gray.astype(np.float64), y, 28


IMAGE_ARENAS = {"digits": _digits_raw, "mnist": _mnist_raw, "fashion": _fashion_raw, "cifar10gray": _cifar10gray_raw}


def load_image_split(arena, seed, n_train, n_test):
    """The house signature for the image arenas: a seeded train/test split in native flat space (values ~[0,1])."""
    Xraw, yraw, side = IMAGE_ARENAS[arena]()
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(Xraw))
    tr, te = idx[:n_train], idx[n_train:n_train + n_test]
    return Xraw[tr], yraw[tr], Xraw[te], yraw[te], side


def load_real(arena):
    """The real-world streaming arenas: raw native (X,y) + the DECLARED stream-order key + C. No split — a stream
    has one natural order (design §1). y is remapped to 0..C-1; the order key defines the natural blocks."""
    if arena == "gas":
        d = _from_npz("gas")
        y = d["y"] - 1                                                  # 1..6 -> 0..5
        return dict(X=d["X"].astype(np.float64), y=y.astype(np.int64), order=d["batch"].astype(np.int64),
                    C=6, order_name="batch(1..10, sensor-drift time)", block_key="batch")
    if arena == "har":
        d = _from_npz("har")
        return dict(X=d["X"].astype(np.float64), y=(d["y"] - 1).astype(np.int64),
                    order=d["subject"].astype(np.int64), C=6, order_name="subject blocks", block_key="subject")
    if arena == "electric":
        d = _from_npz("electric")
        return dict(X=d["X"].astype(np.float64), y=d["y"].astype(np.int64),
                    order=np.arange(len(d["y"])), C=2, order_name="chronological (date+period)", block_key="chrono")
    if arena == "covtype":
        d = _from_npz("covtype")
        return dict(X=d["X"].astype(np.float64), y=(d["y"] - 1).astype(np.int64),
                    order=np.arange(len(d["y"])), C=7, order_name="file order", block_key="fileorder")
    raise ValueError(arena)


def composition_table(y, order, blocks):
    """The per-block class-composition table (a bench artifact; the STREAM composition strip + the imbalance test).
    `blocks` = the ordered list of block ids. Returns [n_blocks, C] counts + the per-block n."""
    C = int(y.max()) + 1
    comp = np.zeros((len(blocks), C), int)
    for bi, b in enumerate(blocks):
        m = (order == b)
        for c in range(C):
            comp[bi, c] = int(((y == c) & m).sum())
    return comp


def imbalance_ratio(comp):
    tot = comp.sum(0).astype(float)
    tot = tot[tot > 0]
    return float(tot.max() / (tot.min() + EPS))


# ============================================================ the porthole projection (K5 — one per source)
def porthole(native_dim, D, *, pseed=12345):
    """ONE seed-frozen Gaussian projection native_dim->D (the P10.3 discipline). Applied identically to every learner
    -> a bit-identical projected stream. One projection per (native_dim, D)."""
    return np.random.default_rng(pseed).standard_normal((native_dim, D)) / np.sqrt(native_dim)


def unit_rms_scaler(Xfit):
    """Fit a single scalar so the fitted block has unit RMS (the frozen scaler; fit on the FIRST natural block only)."""
    rms = float(np.sqrt(np.mean(Xfit ** 2)) + EPS)
    return rms


# ============================================================ the noise-to-signal equivalence (F3 — the direction killer)
def p10_digits_rms(seed=42):
    """RMS of the P10 gauntlet's digit inputs (8x8 /16). σ_noise=0.6 is ABSOLUTE on THIS RMS -> σ/RMS ratio frozen."""
    X, _, _ = _digits_raw()
    return float(np.sqrt(np.mean(X ** 2)))


def equiv_noise_sigma(rms_arena, *, rms_p10=None):
    """σ_rung = (0.6 / RMS_P10-digits) · RMS_rung  (§8 F3). Preserves P10's noise-to-signal ratio on the noised
    gauntlet domain so the ladder is not confounded by a milder/harsher noise at a different input scale."""
    rms_p10 = p10_digits_rms() if rms_p10 is None else rms_p10
    return float((CFG0.GAUNTLET_NOISE_RMS / rms_p10) * rms_arena)


# ============================================================ the generalized domain-IL gauntlet (P11.2/P11.5)
def _domain_transform_img(Ximg, domain, side, *, perm, noise_rms, rng):
    """A domain's INPUT transform in native flat image space (before the ->D projection). Same classes (domain-IL,
    shared head): identity / permuted-pixels / rotated-90 / layernorm-invariant covariate / noised (σ by equivalence)."""
    if domain == "identity":
        return Ximg
    if domain == "permuted":
        return Ximg[:, perm]
    if domain == "rotated":
        img = Ximg.reshape(-1, side, side)
        return np.rot90(img, k=1, axes=(1, 2)).reshape(-1, side * side)
    if domain == "covariate":
        return CFG0.GAUNTLET_COV_GAIN * Ximg + CFG0.GAUNTLET_COV_OFFSET
    if domain == "noised":
        return Ximg + noise_rms * rng.standard_normal(Ximg.shape)
    raise ValueError(domain)


def make_arena_gauntlet_stream(arena, cfg, seed, *, ntr=1200, nte=2000, block=24, order=None,
                               regime="rapid", noise_rms=None, domains=None):
    """The 5-domain domain-IL gauntlet on ANY image arena (generalizes p10lib.make_gauntlet_stream). Native-space
    transforms -> ONE frozen porthole native_dim->cfg.DIM (K5). Two switch regimes:
      regime='rapid'  : every domain `block` steps (default 24 — the P10.3 continuity control).
      regime='long'   : long-randomized non-multiple blocks [50..70] (the E8 convention — PRIMARY from here, since
                        P10 showed rapid-switch flatters OURS).
    `order='reversed'` reverses the domain sequence. Emits the exact fields build_cache_p9 / run_economy_p9 consume.
    Every learner replays this SAME projected stream (bit-identical)."""
    domains = list(domains or CFG0.GAUNTLET_DOMAINS)
    if order == "reversed":
        domains = domains[::-1]
    Xtr_img, Ytr, Xte_img, Yte, side = load_image_split(arena, seed, ntr, nte)
    native = Xtr_img.shape[1]
    Pj = porthole(native, cfg.DIM)
    perm = np.random.default_rng(9999).permutation(native)
    if noise_rms is None:
        noise_rms = equiv_noise_sigma(float(np.sqrt(np.mean(Xtr_img ** 2))))
    C = cfg.NCLASS; B = cfg.BATCH
    rng = np.random.default_rng(seed + 606)
    # per-domain projected (train,test)
    data = {}
    for dm in domains:
        Xtr_t = _domain_transform_img(Xtr_img, dm, side, perm=perm, noise_rms=noise_rms, rng=rng)
        Xte_t = _domain_transform_img(Xte_img, dm, side, perm=perm, noise_rms=noise_rms, rng=rng)
        data[dm] = (Xtr_t @ Pj, Ytr.copy(), Xte_t @ Pj, Yte.copy())
    if regime == "long":
        rb = np.random.default_rng(seed + 4242)
        blocks = [int(rb.integers(50, 71)) for _ in domains]           # non-multiples of the grid-4 period
    else:
        blocks = [int(block)] * len(domains)
    return _assemble_gauntlet(data, domains, blocks, cfg, seed, Pj)


def _assemble_gauntlet(data, domains, blocks, cfg, seed, Pj):
    """Shared assembly for a domain-IL stream (mirrors p10lib.make_gauntlet_stream's field contract)."""
    C = cfg.NCLASS; B = cfg.BATCH
    Xtr_all, Ytr_all, dom_slices, off = [], [], {}, 0
    for dm in domains:
        Xtr_d, Ytr_d, _, _ = data[dm]
        Xtr_all.append(Xtr_d); Ytr_all.append(Ytr_d)
        dom_slices[dm] = np.arange(off, off + len(Xtr_d)); off += len(Xtr_d)
    Xtr_all = np.vstack(Xtr_all); Ytr_all = np.concatenate(Ytr_all)
    rng = np.random.default_rng(seed + 707)

    def draw(dm, n):
        pool = dom_slices[dm]
        return rng.choice(pool, n, replace=len(pool) < n)

    steps, checkpoints, real_onsets, monitor = [], [], [], []
    D = len(domains)
    for di, dm in enumerate(domains):
        real_onsets.append(len(steps))
        for r in range(blocks[di]):
            seg = f"onset{di}" if r < 4 else f"plateau{di}"
            steps.append(dict(idx=draw(dm, B), seg=seg, nuis=None, seen=di))
        checkpoints.append((len(steps) - 1, di))
    n_steps = len(steps)
    per = max(C, cfg.PROBE_N // len(domains))
    Xs, Ys = [], []
    for dm in domains:
        Xd, Yd = data[dm][0], data[dm][1]
        sel = rng.choice(len(Xd), min(per, len(Xd)), replace=False)
        Xs.append(Xd[sel]); Ys.append(Yd[sel])
    Xpr, Ypr = np.vstack(Xs), np.concatenate(Ys)
    eval_by_task = {di: (data[dm][2], data[dm][3]) for di, dm in enumerate(domains)}
    warmup_idx = draw(domains[0], max(6, cfg.WARMUP_STEPS) * B)
    probe_grid = sorted(set(range(cfg.LIFE_PROBE_EVERY - 1, n_steps, cfg.LIFE_PROBE_EVERY))
                        | set(s for s, _ in checkpoints) | set(monitor))
    return dict(steps=steps, n_steps=n_steps, Xtr=Xtr_all, Ytr=Ytr_all, Xpr=Xpr, Ypr=Ypr,
                eval_by_task=eval_by_task, checkpoints=checkpoints, warmup_idx=warmup_idx,
                tasks=[list(range(C))] * D, C=C, real_onsets=real_onsets, nuis_onset=n_steps,
                nuisance_steps=[], stationary_steps=list(range(max(0, n_steps - 8), n_steps)),
                calib_steps=list(range(max(1, cfg.WIN_W - 1), n_steps)),
                monitor_steps=sorted(monitor), probe_grid=probe_grid,
                Xearly=data[domains[0]][2], Yearly=data[domains[0]][3], early_task=0, domains=domains, proj=Pj)


# ============================================================ class-IL streams (Split-MNIST / cross-dataset; P11.2/4)
def make_ci_stream(sources, cfg, seed, *, ntr=1200, nte=2000, order=None, task_size=2, shared_porthole=True):
    """A class-INCREMENTAL stream. `sources` is a list of (arena, class_list, label_offset) blocks presented ONCE
    contiguously, iid within block, no revisits (§8 R1). Split-MNIST = one arena, 5 tasks of 2; cross-dataset =
    [mnist,fashion,cifar10gray] each a contiguous 10-class block, offsets 0/10/20 (30-way, §8 R7). The porthole is
    ONE shared native->D projection + a scaler fit on SOURCE-1's train only (frozen); future sources arrive
    uncalibrated (the honest gain-shock read). Emits the build_cache_p9 / run_economy_p9 field contract."""
    if order == "reversed":
        sources = sources[::-1]
    C = cfg.NCLASS; B = cfg.BATCH
    rng = np.random.default_rng(seed + 707)
    # load each source's split, restricted to its class_list, remapped to offset labels
    proj = None; scaler = None
    task_specs = []                                                    # (Xtr_D, Ytr, Xte_D, Yte) per task
    tasks = []                                                         # class id lists per task (for the acc matrix rows)
    for si, (arena, class_list, offset) in enumerate(sources):
        Xtr, Ytr, Xte, Yte, side = load_image_split(arena, seed + si, ntr * 3, nte * 2)
        native = Xtr.shape[1]
        if proj is None or not shared_porthole:
            proj = porthole(native, cfg.DIM)
        # subset+remap to this source's class list
        def sub(X, Y):
            keep = np.isin(Y, class_list)
            Xk, Yk = X[keep], Y[keep]
            remap = {c: i + offset for i, c in enumerate(class_list)}
            Yr = np.array([remap[int(v)] for v in Yk], np.int64)
            return Xk, Yr
        Xtr, Ytr = sub(Xtr, Ytr); Xte, Yte = sub(Xte, Yte)
        if scaler is None or not shared_porthole:
            scaler = unit_rms_scaler(Xtr)                              # fit on source-1 train only (frozen)
        Xtr = (Xtr / scaler) @ proj; Xte = (Xte / scaler) @ proj
        # break the source's classes into task_size chunks
        cl = sorted(set((Ytr).tolist()))
        for ti in range(0, len(cl), task_size):
            chunk = cl[ti:ti + task_size]
            mtr = np.isin(Ytr, chunk); mte = np.isin(Yte, chunk)
            task_specs.append((Xtr[mtr][:ntr], Ytr[mtr][:ntr], Xte[mte][:nte], Yte[mte][:nte]))
            tasks.append(chunk)
    return _assemble_ci(task_specs, tasks, cfg, seed, proj)


def _assemble_ci(task_specs, tasks, cfg, seed, proj, *, steps_per_task=24):
    """Assemble a class-IL stream: each task a contiguous block; the acc matrix is task x task (retention). The sleep
    probe is a cross-task balanced sample (domain-IL-fair, exactly the p10lib gauntlet convention)."""
    C = cfg.NCLASS; B = cfg.BATCH
    Xtr_all, Ytr_all, task_slices, off = [], [], {}, 0
    for ti, (Xtr, Ytr, _, _) in enumerate(task_specs):
        Xtr_all.append(Xtr); Ytr_all.append(Ytr)
        task_slices[ti] = np.arange(off, off + len(Xtr)); off += len(Xtr)
    Xtr_all = np.vstack(Xtr_all); Ytr_all = np.concatenate(Ytr_all)
    rng = np.random.default_rng(seed + 707)

    def draw(ti, n):
        pool = task_slices[ti]
        return rng.choice(pool, n, replace=len(pool) < n)

    steps, checkpoints, real_onsets = [], [], []
    T = len(task_specs)
    for ti in range(T):
        real_onsets.append(len(steps))
        # arrival = this task's classes only (true class-IL onset)
        cur = np.where(np.isin(Ytr_all, tasks[ti]))[0]
        loc = {c: task_slices[ti] for c in tasks[ti]}
        for r in range(steps_per_task):
            seg = f"onset{ti}" if r < 4 else f"plateau{ti}"
            steps.append(dict(idx=draw(ti, B), seg=seg, nuis=None, seen=ti))
        checkpoints.append((len(steps) - 1, ti))
    n_steps = len(steps)
    # cross-task balanced probe
    per = max(C, cfg.PROBE_N // T)
    Xs, Ys = [], []
    for ti, (Xtr, Ytr, _, _) in enumerate(task_specs):
        sel = rng.choice(len(Xtr), min(per, len(Xtr)), replace=False)
        Xs.append(Xtr[sel]); Ys.append(Ytr[sel])
    Xpr, Ypr = np.vstack(Xs), np.concatenate(Ys)
    eval_by_task = {ti: (task_specs[ti][2], task_specs[ti][3]) for ti in range(T)}
    warmup_idx = draw(0, max(6, cfg.WARMUP_STEPS) * B)
    probe_grid = sorted(set(range(cfg.LIFE_PROBE_EVERY - 1, n_steps, cfg.LIFE_PROBE_EVERY))
                        | set(s for s, _ in checkpoints))
    return dict(steps=steps, n_steps=n_steps, Xtr=Xtr_all, Ytr=Ytr_all, Xpr=Xpr, Ypr=Ypr,
                eval_by_task=eval_by_task, checkpoints=checkpoints, warmup_idx=warmup_idx,
                tasks=tasks, C=C, real_onsets=real_onsets, nuis_onset=n_steps,
                nuisance_steps=[], stationary_steps=list(range(max(0, n_steps - 8), n_steps)),
                calib_steps=list(range(max(1, cfg.WIN_W - 1), n_steps)),
                monitor_steps=[], probe_grid=probe_grid,
                Xearly=task_specs[0][2], Yearly=task_specs[0][3], early_task=0, tasknames=tasks, proj=proj)


# ============================================================ real-world natural-block streams (P11.3)
def make_real_stream(arena, cfg, seed, *, arm="A", order=None, max_n=None, scaler_block=None):
    """A natural-block stream over a real-world arena (gas batches / HAR subjects / electric+covtype slices). The
    scaler is fit on the FIRST natural block only (frozen); every learner sees the SAME projected stream. Blocks are
    the acc-matrix rows (retention across blocks). Prequential accuracy is read pre-update in the run loop.
    Returns (stream, meta) — meta carries the block ids, per-block n, composition, order_name."""
    R = load_real(arena)
    X, y, order_key, C = R["X"], R["y"], R["order"], R["C"]
    cfg.NCLASS = C
    if arena in ("electric", "covtype") and max_n:
        X, y, order_key = X[:max_n], y[:max_n], order_key[:max_n]
    # natural blocks
    if arena == "gas":
        blocks = list(range(1, 11))
    elif arena == "har":
        blocks = sorted(set(order_key.tolist()))
        rb = np.random.default_rng(seed + 11)                          # subject order arbitrary -> seed-shuffled (declared)
        blocks = list(rb.permutation(blocks))
    else:                                                             # electric / covtype: contiguous slices
        n_blocks = 10
        edges = np.linspace(0, len(X), n_blocks + 1).astype(int)
        block_of = np.zeros(len(X), int)
        for bi in range(n_blocks):
            block_of[edges[bi]:edges[bi + 1]] = bi
        order_key = block_of; blocks = list(range(n_blocks))
    if order == "reversed":
        blocks = blocks[::-1]
    # scaler on the first natural block only (frozen)
    first_mask = (order_key == blocks[0])
    scaler = unit_rms_scaler(X[first_mask])
    native = X.shape[1]
    Pj = porthole(native, cfg.DIM)
    Xp = (X / scaler) @ Pj
    # 80/20 within-block split for retention/BWT (eval never trained on); prequential uses the full arriving batch
    rng = np.random.default_rng(seed + 999)
    is_eval = np.zeros(len(X), bool)
    for b in blocks:
        idx = np.where(order_key == b)[0]
        ne = max(1, int(0.2 * len(idx)))
        is_eval[rng.choice(idx, ne, replace=False)] = True
    B = cfg.BATCH
    steps, checkpoints, real_onsets, block_n_eval = [], [], [], {}
    Xtr_all = Xp; Ytr_all = y
    for bi, b in enumerate(blocks):
        tr_idx = np.where((order_key == b) & (~is_eval))[0]
        real_onsets.append(len(steps))
        # stream the block's TRAIN samples in arrival order, batched
        for s0 in range(0, len(tr_idx), B):
            sub = tr_idx[s0:s0 + B]
            if len(sub) >= 2:
                steps.append(dict(idx=sub, seg=(f"onset{bi}" if s0 == 0 else f"plateau{bi}"), nuis=None, seen=bi))
        checkpoints.append((len(steps) - 1, bi))
        block_n_eval[bi] = int((is_eval & (order_key == b)).sum())
    n_steps = len(steps)
    eval_by_task = {}
    for bi, b in enumerate(blocks):
        ev = np.where(is_eval & (order_key == b))[0]
        eval_by_task[bi] = (Xp[ev], y[ev])
    # sleep probe = cross-block balanced sample from TRAIN
    per = max(C, cfg.PROBE_N // len(blocks))
    Xs, Ys = [], []
    for b in blocks:
        idx = np.where((order_key == b) & (~is_eval))[0]
        sel = rng.choice(idx, min(per, len(idx)), replace=False) if len(idx) else idx
        Xs.append(Xp[sel]); Ys.append(y[sel])
    Xpr, Ypr = np.vstack(Xs), np.concatenate(Ys)
    warmup_idx = np.where((order_key == blocks[0]) & (~is_eval))[0][:max(6, cfg.WARMUP_STEPS) * B]
    probe_grid = sorted(set(range(cfg.LIFE_PROBE_EVERY - 1, n_steps, cfg.LIFE_PROBE_EVERY))
                        | set(s for s, _ in checkpoints))
    stream = dict(steps=steps, n_steps=n_steps, Xtr=Xtr_all, Ytr=Ytr_all, Xpr=Xpr, Ypr=Ypr,
                  eval_by_task=eval_by_task, checkpoints=checkpoints, warmup_idx=warmup_idx,
                  tasks=[sorted(set(y.tolist()))] * len(blocks), C=C, real_onsets=real_onsets, nuis_onset=n_steps,
                  nuisance_steps=[], stationary_steps=list(range(max(0, n_steps - 8), n_steps)),
                  calib_steps=list(range(max(1, cfg.WIN_W - 1), n_steps)),
                  monitor_steps=[], probe_grid=probe_grid,
                  Xearly=eval_by_task[0][0], Yearly=eval_by_task[0][1], early_task=0, proj=Pj,
                  order_key=order_key, is_eval=is_eval, Xnative=X)
    comp = composition_table(y, order_key, blocks)
    meta = dict(blocks=[int(b) for b in blocks], block_n_eval=block_n_eval, C=C, order_name=R["order_name"],
                composition=comp, imbalance=imbalance_ratio(comp), native_dim=native, scaler=scaler)
    return stream, meta


# ============================================================ stream controls (R2/R5/R11)
def nochange_baseline(stream):
    """The no-change (persistence) baseline: predict the previous sample's label. Prequential balanced accuracy over
    the stream in arrival order (mandatory on every real-world stream — the ELEC2 autocorrelation trap, D2)."""
    y_order = []
    for st in stream["steps"]:
        y_order.append(stream["Ytr"][st["idx"]])
    y = np.concatenate(y_order)
    pred = np.empty_like(y); pred[0] = y[0]; pred[1:] = y[:-1]
    return balanced_acc(y, pred)


def sgd_linear(stream, C, in_dim, *, lr=0.1, seed=0, prequential=True):
    """Online logistic SGD on the projected features (the streaming community's default opponent, §8 R11). Trained on
    the arriving batch each step; prequential (pre-update) balanced accuracy. lr tuned on the seed-7 stream by the
    caller. Ten lines of numpy — no sklearn/River in a live cell."""
    W = np.zeros((in_dim, C)); b = np.zeros(C)
    ys, ps = [], []
    for st in stream["steps"]:
        xb = stream["Xtr"][st["idx"]]; yb = stream["Ytr"][st["idx"]]
        logit = xb @ W + b
        if prequential:
            ps.append(logit.argmax(1)); ys.append(yb)
        p = _softmax(logit); oh = np.zeros_like(p); oh[np.arange(len(yb)), yb] = 1.0
        g = xb.T @ (p - oh) / len(yb)
        W -= lr * g; b -= lr * (p - oh).mean(0)
    return balanced_acc(np.concatenate(ys), np.concatenate(ps))


def _softmax(z):
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / (e.sum(1, keepdims=True) + EPS)


def balanced_acc(y, pred):
    """Mean per-class recall (balanced accuracy). Absent classes dropped from the mean (§8 R8)."""
    y = np.asarray(y); pred = np.asarray(pred); recs = []
    for c in np.unique(y):
        m = (y == c)
        if m.any():
            recs.append(float((pred[m] == c).mean()))
    return float(np.mean(recs)) if recs else 0.0


# ============================================================ decomposition cells (P11.1; "is it just SLDA?")
class _IdentityCell:
    """proj->namer: the strike cell. NO SCFF bulk — the namer reads the frozen ->D porthole input DIRECTLY. infer
    returns [X] so readout_feats gives X (DIM-D). train_step is a no-op (there is no bulk to learn)."""

    def __init__(self, dims, seed):
        self.dims = dims

    def infer(self, X):
        return [np.asarray(X, dtype=np.float64)]

    def train_step(self, *a, **k):
        return None


def identity_cell(dims, seed):
    return _IdentityCell(dims, seed)


def random_frozen_cell(dims, seed):
    """random-frozen-bulk: the reservoir control — the committed cell's 12 nonlinear layers at RANDOM init, NEVER
    trained (train_step no-op). Separates '12 nonlinear layers exist' (reservoir) from 'SCFF learned structure'."""
    cell = make_committed_cell(dims, seed)
    cell.train_step = lambda *a, **k: None
    return cell


def decomp_cells():
    """The P11.1 roster (each a cell_factory for build_cache_p9): the committed bulk, the strike (no bulk), and the
    dim-matched reservoir control. no-sleep is a LOOP variant (cadence off), handled in the run script."""
    return dict(bulk=make_committed_cell, proj=identity_cell, reservoir=random_frozen_cell)


# ============================================================ the meter-derived GD-share shape (C3; P11.0 pre-derivation)
def meter_share_derivation(W_list, *, D=80, L=12, C=10, n_steps=430, fire_frac=0.02, sleep_frac=0.06,
                           probe_n=600, batch=32):
    """Walk the meter's OWN per-op counts vs W (NOT from memory): the SLDA namer reads all-tap Fdim = L·W, so its
    inference ~O(F)=O(LW) per sample and its fire/sleep SOLVE ~O(F^3)=O((LW)^3) — the term that can make GD-share
    RISE with W. Returns the predicted GD-share-vs-W curve straight from hardware_cost_meter (the P11.6 pinned shape).
    n_fire/n_sleep held at committed-run fractions so ONLY W moves (one variable)."""
    n_fire = max(1, int(fire_frac * n_steps)); n_sleep = max(1, int(sleep_frac * n_steps))
    shares = []
    for W in W_list:
        scff_dims = [D] + [int(W)] * L
        m = hardware_cost_meter(CFG0, head_name="slda", Fdim=L * int(W), C=C, n_fire=n_fire, n_sleep=n_sleep,
                                n_steps=n_steps, batch=batch, probe_n=probe_n, scff_dims=scff_dims, substrate="analog")
        shares.append(m["gdshare"])
    return np.array(W_list, float), np.array(shares, float)


# ============================================================ ER-strong per arena (grid pinned; disjoint seed 7)
def tune_er_arena(stream_fn, cfg, in_dim, C, *, tune_seed=7, buffer_cap=None,
                  lrs=(0.3, 0.1, 0.03, 0.01), replays=(1, 2, 4), hidden_mults=(1, 2, 4), base_hidden=64):
    """ER-strong config selection on the DISJOINT seed-7 stream (grid pinned in design §3-P11.0: lr × replay-ratio ×
    hidden with a capacity axis). Selection = final AA on the seed-7 stream. Returns the chosen config. The dominance
    guard (>= naive-BP, >= ER-budget) is checked by the caller."""
    stream = stream_fn(tune_seed)
    buffer_cap = buffer_cap or cfg.PROBE_N
    best = None
    for hm in hidden_mults:
        h = base_hidden * hm
        bp_dims = [in_dim, h, h, C]
        for lr in lrs:
            for r in replays:
                m = run_bp_stream(stream, "er", bp_dims, cfg, tune_seed, lr=lr, replay=r * 32, buffer_cap=buffer_cap)
                if best is None or m["aa"] > best["aa"]:
                    best = dict(aa=m["aa"], bp_dims=bp_dims, lr=lr, replay=r * 32, hidden=h, buffer_cap=buffer_cap)
    return best


# ============================================================ prequential accuracy (R2 — the real-stream channel)
def ours_prequential(cache, res, cfg, seed):
    """OURS's prequential (pre-update) balanced accuracy over the stream — a GUARDED faithful replay: it re-applies
    the head's committed update sequence using the RECORDED fire/sleep masks from `res` (not a re-decided gate), so
    the head trajectory is identical to the frozen run; the per-step pre-update prediction IS the prequential read.
    Asserts plain-acc == 1 - err_trace (faithfulness to the frozen loop) — a rebuild, never a re-run (§8 F7)."""
    steps = cache["steps"]; C = cache["stream"]["C"]
    head = make_stream_head(HEAD, C, seed=seed, **cfg.SLDA_KNOB)
    fires = np.asarray(res["fires"], bool); sleeps = np.asarray(res["sleeps"], bool)
    err_ref = np.asarray(res["err_trace"], float)
    lam = COMMITTED_LOOP["lam_ema"]
    ys, preds, plain = [], [], []
    fitted = False
    for si, rec in enumerate(steps):
        phi_b = rec["phi_b"]; y_b = rec["y_b"]
        if head.W is not None:
            pred = head.predict(phi_b)
            plain.append(1.0 - float((pred == y_b).mean()))
        else:
            pred = np.full(len(y_b), -1); plain.append(np.nan)
        ys.append(y_b); preds.append(pred)
        if fires[si]:
            head.partial_fit(phi_b, y_b, lam_ema=lam); fitted = True
        if ("eval" in rec) and not fitted:
            head.partial_fit(phi_b, y_b, lam_ema=lam); fitted = True
        if sleeps[si] and "phi_probe" in rec:
            Fp, Yp = rec["phi_probe"], rec["y_probe"]
            if COMMITTED_LOOP["cbrs"]:
                Fp, Yp = class_balanced_reservoir(Fp, Yp, C, cfg.CBRS_CAP, np.random.default_rng(2000 + si))
            if len(Fp) >= C:
                head.sleep_fit(Fp, Yp); fitted = True
    plain = np.array(plain, float)
    mism = np.nanmax(np.abs(plain - err_ref)) if np.isfinite(plain).any() else 0.0
    if mism > 1e-9:
        raise AssertionError(f"ours_prequential unfaithful: max|plain-err_trace|={mism:.2e}")
    y = np.concatenate(ys); p = np.concatenate(preds); ok = p >= 0
    return dict(bal=balanced_acc(y[ok], p[ok]), plain=float((p[ok] == y[ok]).mean()),
                y=y, pred=p, live=1.0 - plain)


def bp_prequential(stream, policy, bp_dims, cfg, seed, *, lr=3e-3, replay=0, buffer_cap=0):
    """A BP+replay learner's prequential balanced accuracy — ContinualBP (the tested racer) with the pre-update
    prediction recorded each step. Same arrival order every learner sees."""
    C = stream["C"]
    learner = ContinualBP(policy, bp_dims, C, seed, lr=lr, replay=replay, buffer_cap=buffer_cap)
    rng = np.random.default_rng(seed + 4242)
    ys, preds = [], []
    for st in stream["steps"]:
        xb = stream["Xtr"][st["idx"]]; yb = stream["Ytr"][st["idx"]]
        if policy != "gdumb" and learner.net.W is not None:
            ys.append(yb); preds.append(learner.net.predict(xb))
        if len(xb) >= 2:
            learner.step(xb, yb, rng)
    if not ys:
        return dict(bal=0.0, plain=0.0)
    y = np.concatenate(ys); p = np.concatenate(preds)
    return dict(bal=balanced_acc(y, p), plain=float((p == y).mean()), learner=learner)


# ============================================================ uniform noise-retention (fair Δbulk noise channel)
def _adc_quant(X, bits):
    """Uniform mid-rise ADC quantization to `bits` over the batch's dynamic range (the sub-3-bit read stress)."""
    lo, hi = X.min(), X.max()
    levels = max(2, 2 ** int(bits))
    q = np.round((X - lo) / (hi - lo + EPS) * (levels - 1))
    return lo + q / (levels - 1) * (hi - lo)


def cell_noise_retention(cell, Xpr, Ypr, Xte, Yte, cfg, C, seed, channels=("iid", "directional", "adc3b")):
    """The fair Δbulk NOISE channel: fit the SLDA namer on CLEAN features of `cell`, evaluate under a coherent input
    shift (the P6/P10 read — the directional enemy is a COHERENT TRANSLATION along the class axis, a DIRECTION not a
    magnitude), retention = noisy_acc / clean_acc. Applied identically to bulk / proj / reservoir cells (same read,
    same rms) so the Δbulk on this channel is a controlled one-variable comparison. Undefended (no proto-reanchor) so
    it isolates the BULK's contribution, not the sleep defence."""
    namer = make_stream_head(HEAD, C, seed=seed, **cfg.SLDA_KNOB)
    namer.sleep_fit(readout_feats(cell.infer(Xpr), None), Ypr)
    clean = float((namer.predict(readout_feats(cell.infer(Xte), None)) == Yte).mean())
    ax = class_axis(Xpr, Ypr)                                           # input-space class axis (coherent shift dir)
    rng = np.random.default_rng(seed + 321)
    out = {"clean": clean}
    for ch in channels:
        if ch == "iid":
            Xn = Xte + cfg.NOISE_IID_RMS * rng.standard_normal(Xte.shape)
        elif ch == "directional":
            Xn = Xte + cfg.NOISE_HOLDOUT_INPUT_RMS * ax[None, :]
        elif ch == "adc3b":
            Xn = _adc_quant(Xte + cfg.NOISE_HOLDOUT_INPUT_RMS * ax[None, :], cfg.NOISE_HOLDOUT_ADC_BITS)
        else:
            raise ValueError(ch)
        acc = float((namer.predict(readout_feats(cell.infer(Xn), None)) == Yte).mean())
        out[ch] = acc / (clean + EPS)
    return out


def allprev_retention(matrix):
    """From a task/domain × task/domain acc-matrix: retention on ALREADY-SEEN tasks (k<t). mean + worst-point."""
    vals = [matrix[t][k] for t in range(len(matrix)) for k in range(t) if matrix[t][k] > 0]
    return dict(mean=float(np.mean(vals)) if vals else 0.0, worst=float(np.min(vals)) if vals else 0.0)


# ============================================================ the FLOOR criterion (C1; two-sided R6)
def floor_state(ours, best_field, *, ceiling, chance, delta=0.02, nochange=None, all_raced=None):
    """Apply the §2.4 FLOOR criterion to one map cell. FLOOR iff (a) ceiling < chance+5δ, or (b) every raced learner
    < chance+2δ, or (c) real stream: no raced learner beats no-change+δ. Two-sided: a FLOOR cell still annotates the
    paired OURS-vs-field delta. Else win/tie/loss by the real-difference bar on (ours - best_field)."""
    is_floor = False; reason = ""
    if ceiling is not None and ceiling < chance + 5 * delta:
        is_floor, reason = True, "ceiling<chance+5delta"
    elif all_raced is not None and all(a < chance + 2 * delta for a in all_raced):
        is_floor, reason = True, "all-raced<chance+2delta"
    elif nochange is not None and all_raced is not None and not any(a > nochange + delta for a in all_raced):
        is_floor, reason = True, "none-beat-nochange"
    d = float(ours - best_field)
    if is_floor:
        tag = f"FLOOR ({'field leads +%.3f' % (-d) if d < -delta else ('OURS leads +%.3f' % d if d > delta else 'tie')})"
        return dict(state="FLOOR", reason=reason, delta=d, label=tag)
    if d > delta:
        return dict(state="win", delta=d, label=f"win +{d:.3f}")
    if d < -delta:
        return dict(state="loss", delta=d, label=f"loss {d:.3f}")
    return dict(state="tie", delta=d, label=f"tie ({d:+.3f})")


# ============================================================ stats (carried from p9run) + IO
med = P10.__dict__.get("med")
try:
    import p9run as _R9
    med = _R9.med; iqr = _R9.iqr; fmt = _R9.fmt; real_diff = _R9.real_diff; paired_sign_neg = _R9.paired_sign_neg
except Exception:
    def med(x): return float(np.median(np.atleast_1d(np.asarray(x, float))))
    def iqr(x):
        x = np.atleast_1d(np.asarray(x, float)); return float(np.percentile(x, 25)), float(np.percentile(x, 75))
    def fmt(x):
        q1, q3 = iqr(x); return f"{med(x):.3f} [{q1:.3f}-{q3:.3f}]"


def jsonsafe(o):
    return P10.jsonsafe(o)


def git_hash():
    import subprocess
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def save_run(outdir, arrays, manifest):
    os.makedirs(outdir, exist_ok=True)
    np.savez(os.path.join(outdir, "arrays.npz"), **{k: np.asarray(v) for k, v in arrays.items()})
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(jsonsafe(manifest), f, indent=2)
