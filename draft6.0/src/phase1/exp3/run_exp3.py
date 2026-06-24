"""
Exp 3 — residual-boosting block chain vs the monolithic deep SCFF stack (and pure GD).

The Exp-2 pivot to test: depth must come from STACKING shallow GD-corrected blocks on a
RESIDUAL stream, not from a deep SCFF stack (which degrades). The residual skip
  g_k = norm(g_{k-1} + relu(W_k g_{k-1}))
preserves the good early features while adding depth. Boosting (N3/BoostResNet): a per-block
readout fits the running residual; training error should fall ~exp(-1/2 T gamma^2) with depth.

Tests:
  (A) PIVOT — per-block linear-probe acc, residual skip ON (chain) vs OFF (plain stack).
      ON should hold/rise with depth where OFF degrades (the Exp-1/2 finding).
  (B) BOOSTING — gradient-boost a linear weak learner on the residual stream g_1..g_N;
      train/held error vs #blocks (F8) + per-block weak-edge gamma (dead-block watch).
  vs the pure-GD ceiling at matched weights.

Reuses exp0/exp1. numpy only.  Run:  python run_exp3.py digits | mnist
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
from scipy.special import expit, softmax
from sklearn.linear_model import LogisticRegression
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "exp0"))
sys.path.insert(0, os.path.join(_HERE, "..", "exp1"))
from scff_gate import relu, EPS, THETA, LR_SCFF                       # noqa: E402
from models_extra import MLP, match_width                            # noqa: E402
from run_exp1 import load_data, _git_hash                            # noqa: E402

BATCH, PROBE_C = 32, 1.0
N_BLOCKS = 6
CFG = {"digits": dict(H=64, scff_ep=40, n_train=600, n_test=600, seeds=[42, 137, 271, 314, 1729]),
       "mnist":  dict(H=128, scff_ep=20, n_train=3000, n_test=3000, seeds=[42, 137, 271])}
C_CHAIN, C_PLAIN, C_GD = "#117a78", "#c1272d", "#e08214"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
                     "savefig.transparent": False, "savefig.facecolor": "white"})


def _norm(a):
    return a / (np.linalg.norm(a, axis=1, keepdims=True) + EPS)


class Chain:
    """SCFF stem + N shallow blocks. residual=True -> residual stream (chain); False -> plain stack."""
    def __init__(self, D, H, N, seed, residual=True, theta=THETA, lr=LR_SCFF, res_scale=1.0):
        rng = np.random.default_rng(seed)
        dims = [D] + [H] * N
        self.W = [rng.normal(0, np.sqrt(2.0 / dims[i]), (dims[i + 1], dims[i])) for i in range(N)]
        self.b = [np.zeros(dims[i + 1]) for i in range(N)]
        self.N, self.residual, self.theta, self.lr = N, residual, theta, lr
        self.res_scale = res_scale          # epsilon: g_k = norm(g_{k-1} + eps*h_k)

    def _upd(self, W, b, hp, hn, ip, inn):
        Gp, Gn = (hp ** 2).sum(1), (hn ** 2).sum(1)            # sum goodness
        cpos = (expit(Gp - self.theta) - 1.0) * 2.0
        cneg = (expit(Gn - self.theta)) * 2.0
        B = len(hp)
        W -= self.lr * ((cpos[:, None] * hp).T @ ip + (cneg[:, None] * hn).T @ inn) / B
        b -= self.lr * ((cpos[:, None] * hp).sum(0) + (cneg[:, None] * hn).sum(0)) / B

    def train_step(self, Xb, rng):
        perm = rng.permutation(len(Xb))
        gp, gn = _norm(2.0 * Xb), _norm(Xb + Xb[perm])
        for k in range(self.N):
            hp, hn = relu(gp @ self.W[k].T + self.b[k]), relu(gn @ self.W[k].T + self.b[k])
            self._upd(self.W[k], self.b[k], hp, hn, gp, gn)
            if self.residual and k > 0:                        # stem (k=0) has no skip
                gp, gn = _norm(gp + self.res_scale * hp), _norm(gn + self.res_scale * hn)
            else:
                gp, gn = _norm(hp), _norm(hn)

    def stream(self, X):
        g = _norm(X); out = []
        for k in range(self.N):
            h = relu(g @ self.W[k].T + self.b[k])
            g = _norm(g + self.res_scale * h) if (self.residual and k > 0) else _norm(h)
            out.append(g)
        return out                                             # [g_0 ... g_{N-1}]


def perlayer_probe(ch, Xtr, Ytr, Xte, Yte):
    return [float(LogisticRegression(C=PROBE_C, max_iter=3000).fit(rtr, Ytr).score(rte, Yte))
            for rtr, rte in zip(ch.stream(Xtr), ch.stream(Xte))]


def gradient_boost(streams_tr, Ytr, streams_te, Yte, C, alpha=0.6):
    """Linear weak learner per block fits the running residual (gradient boosting on logits)."""
    n, m = len(Ytr), len(Yte)
    r_tr, r_te = np.zeros((n, C)), np.zeros((m, C))
    Yoh = np.eye(C)[Ytr]
    tr_err, te_err, gamma = [], [], []
    for Gk, Gke in zip(streams_tr, streams_te):
        A = np.hstack([Gk, np.ones((n, 1))]); Ae = np.hstack([Gke, np.ones((m, 1))])
        resid = Yoh - softmax(r_tr, axis=1)
        Bmat = np.linalg.lstsq(A, resid, rcond=None)[0]
        o_tr, o_te = A @ Bmat, Ae @ Bmat
        # weak edge: fraction of residual variance this block explains
        gamma.append(float(np.clip((o_tr * resid).sum() / ((resid ** 2).sum() + EPS), 0, 1)))
        r_tr += alpha * o_tr; r_te += alpha * o_te
        tr_err.append(float((r_tr.argmax(1) != Ytr).mean()))
        te_err.append(float((r_te.argmax(1) != Yte).mean()))
    return np.array(tr_err), np.array(te_err), np.array(gamma)


def run_seed2(name, seed):
    c = CFG[name]; H = c["H"]
    Xtr, Ytr, Xte, Yte, C = load_data(name, c["n_train"], c["n_test"], seed)
    D = Xtr.shape[1]

    def fit(residual):
        ch = Chain(D, H, N_BLOCKS, seed, residual=residual)
        rng = np.random.default_rng(seed)
        for _ in range(c["scff_ep"]):
            idx = rng.permutation(len(Xtr))
            for s in range(0, len(Xtr), BATCH):
                ch.train_step(Xtr[idx[s:s + BATCH]], rng)
        return ch

    chain, plain = fit(True), fit(False)
    out = {}
    out["probe_chain"] = perlayer_probe(chain, Xtr, Ytr, Xte, Yte)
    out["probe_plain"] = perlayer_probe(plain, Xtr, Ytr, Xte, Yte)
    tr, te, gam = gradient_boost(chain.stream(Xtr), Ytr, chain.stream(Xte), Yte, C)
    out["boost_tr_err"], out["boost_te_err"], out["gamma"] = tr, te, gam
    # inter-block drift: how much the stream moves block-to-block (chain)
    S = chain.stream(Xte)
    out["drift"] = [float(np.linalg.norm(S[k] - S[k - 1], axis=1).mean()) for k in range(1, len(S))]
    # pure-GD ceiling at weights ~ matched to the chain
    chain_w = sum(W.size + b.size for W, b in zip(chain.W, chain.b)) + (H * C + C)
    w, _ = match_width(chain_w, D, C, 4)
    gd = MLP([D, w, w, w, w, C], seed, lr=1e-3)
    rng = np.random.default_rng(seed + 9)
    for _ in range(50):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            gd.train_step(Xtr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    out["gd_held"] = float(gd.accuracy(Xte, Yte))
    out["gd_gap"] = float(gd.accuracy(Xtr, Ytr) - gd.accuracy(Xte, Yte))
    out["chain_held"] = float(1 - te[-1]); out["chain_gap"] = float((1 - tr[-1]) - (1 - te[-1]))
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "digits"
    seeds = CFG[name]["seeds"]; t0 = time.time()
    runs = [run_seed2(name, s) for s in seeds]
    st = lambda k: np.array([r[k] for r in runs])
    pc = np.median(st("probe_chain"), 0); pp = np.median(st("probe_plain"), 0)
    print(f"\n=== Exp 3 [{name}] residual chain, median n={len(seeds)} ===")
    print(f"  per-block probe  chain(skip ON) {np.round(pc,3)}")
    print(f"  per-block probe  plain(skip OFF){np.round(pp,3)}   <- Exp-2 degradation baseline")
    print(f"  boosting train-err vs #blocks {np.round(np.median(st('boost_tr_err'),0),3)}")
    print(f"  boosting held-err  vs #blocks {np.round(np.median(st('boost_te_err'),0),3)}")
    print(f"  per-block weak-edge gamma     {np.round(np.median(st('gamma'),0),3)}")
    print(f"  chain final held {np.median(st('chain_held')):.3f} (gap {np.median(st('chain_gap')):+.3f})  "
          f"| pure-GD {np.median(st('gd_held')):.3f} (gap {np.median(st('gd_gap')):+.3f})")

    OUT = os.path.join(_HERE, f"figs_exp3_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {k: st(k) for k in runs[0].keys()}; saved["seeds"] = np.array(seeds)
    np.savez(os.path.join(OUT, "arrays.npz"), **saved)
    json.dump({"experiment": f"exp3-{name}", "git_commit": _git_hash(), "n_blocks": N_BLOCKS,
               "seeds": seeds, "config": CFG[name], "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    _fig(saved, name, OUT)
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}")


def _fig(A, name, OUT):
    blocks = np.arange(1, N_BLOCKS + 1)
    pc, pp = np.median(A["probe_chain"], 0), np.median(A["probe_plain"], 0)
    pcl, pch = np.percentile(A["probe_chain"], 25, 0), np.percentile(A["probe_chain"], 75, 0)
    # PIVOT figure: residual skip ON vs OFF
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(blocks, pc, color=C_CHAIN, marker="o", label="residual chain (skip ON)")
    ax.fill_between(blocks, pcl, pch, color=C_CHAIN, alpha=0.2)
    ax.plot(blocks, pp, color=C_PLAIN, marker="s", ls="--", label="plain stack (skip OFF)")
    ax.set_xlabel("block / layer (depth)"); ax.set_ylabel("linear-probe acc")
    ax.set_title(f"Exp3 {name}: residual skip + mandatory-norm DILUTES early features\n"
                 f"(per-block stream degrades; boosting ENSEMBLE is what helps) — n={A['probe_chain'].shape[0]}")
    ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(OUT, "pivot_skip.png")); plt.close(fig)
    # F8 boosting shape + gamma bars + theory bound
    tr = np.median(A["boost_tr_err"], 0); te = np.median(A["boost_te_err"], 0)
    gam = np.median(A["gamma"], 0); g = float(np.median(gam[gam > 0])) if (gam > 0).any() else 0.05
    bound = np.exp(-0.5 * blocks * g ** 2)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(blocks, tr, color=C_CHAIN, marker="o", label="chain train error")
    ax[0].plot(blocks, te, color=C_CHAIN, marker="o", ls="--", alpha=0.6, label="chain held error")
    ax[0].plot(blocks, bound * tr[0] / bound[0], color="grey", ls=":", label=f"~exp(-½Tγ²), γ={g:.2f}")
    ax[0].set_xlabel("# blocks"); ax[0].set_ylabel("error"); ax[0].set_yscale("log")
    ax[0].set_title("F8 boosting: error falls with depth"); ax[0].legend(fontsize=8)
    ax[1].bar(blocks, gam, color=C_CHAIN); ax[1].axhline(0.02, color=C_PLAIN, ls=":", label="dead-block")
    ax[1].set_xlabel("block"); ax[1].set_ylabel("weak-edge γ (residual var explained)")
    ax[1].set_title("F8: per-block edge (dead-block watch)"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "F8_boosting.png")); plt.close(fig)


if __name__ == "__main__":
    main()
