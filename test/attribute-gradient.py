import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# ─── theme ────────────────────────────────────────────────────────────────────
sns.set_theme(style='whitegrid', font_scale=1.05)
plt.rcParams.update({
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'axes.edgecolor':   '#cccccc', 'axes.linewidth': 1.0,
    'grid.color':       '#e8e8e8', 'grid.linewidth': 0.8,
    'font.family':      'DejaVu Sans',
    'axes.spines.top':  False,    'axes.spines.right': False,
})
C_GRAD = '#2563EB'   # blue  - gradient
C_ATTR = '#DC2626'   # red   - LRP attribution
C_ARC  = '#D97706'   # amber - arc rule
C_TRUE = '#16A34A'   # green - ground truth


# ══════════════════════════════════════════════════════════════════════════════
# DATA ZONE  ─  change only here.  Everything downstream adapts automatically.
# ─────────────────────────────────────────────────────────────────────────────
#   target_fn(X)  →  maps ANY (n,2) array to (n,1) targets.
#                    Used by BOTH make_data() (training) AND true_grid() (viz).
#   DATA_LABEL    →  shown in all titles / axes.
#   DOMAIN        →  input range [lo, hi] for x0 and x1.
# ══════════════════════════════════════════════════════════════════════════════
DATA_LABEL = "0.4*x0 + 0.6*x1^2"
DOMAIN     = (0, 1.0)

def target_fn(X):
    """Ground truth: X is (n,2), returns (n,1).  Edit freely."""

    half_n = X.shape[0] // 2
    # Keeping the 2D shape (32, 1) during the math
    y_upper = - 0.4 * X[:half_n, 0:1]**2 + 0.6 * X[:half_n, 1:2]**2  # Cubic half
    y_lower = 0.4 * X[half_n:, 0:1] + 0.6 * X[half_n:, 1:2]        # Linear half

    # Concatenate along axis 0 to get a (64, 1) matrix
    y = np.concatenate([y_upper, y_lower], axis=0)

    return y

def make_data(n=500, seed=0):
    """Training set — calls target_fn, so it always matches the visualization."""
    np.random.seed(seed)
    lo, hi = DOMAIN
    X = np.random.rand(n, 2) * (hi - lo) + lo
    return X, target_fn(X)

def true_grid(n=64):
    """Dense evaluation grid — calls target_fn, always identical to make_data."""
    lo, hi = DOMAIN
    g  = np.linspace(lo, hi, n)
    G0, G1 = np.meshgrid(g, g)
    Xg = np.column_stack([G0.ravel(), G1.ravel()])
    Z  = target_fn(Xg).reshape(n, n)
    return G0, G1, Z
# ══════════════════════════════════════════════════════════════════════════════


# ─── model ────────────────────────────────────────────────────────────────────
def he_init(fan_in, fan_out):
    return np.random.randn(fan_in, fan_out) * np.sqrt(2.0 / fan_in)

def xavier_init(fan_in, fan_out):
    lim = np.sqrt(6.0 / (fan_in + fan_out))
    return np.random.uniform(-lim, lim, (fan_in, fan_out))

def relu(x):   return np.maximum(0, x)
def relu_d(x): return (x > 0).astype(float)

W1 = b1 = W2 = b2 = W3 = b3 = None

def reset_weights(seed=42):
    global W1, b1, W2, b2, W3, b3
    np.random.seed(seed)
    W1 = he_init(2, 3);     b1 = np.zeros((1, 3))
    W2 = xavier_init(3, 3); b2 = np.zeros((1, 3))
    W3 = xavier_init(3, 2); b3 = np.zeros((1, 2))

def forward(X):
    z1 = X@W1+b1;  a1 = relu(z1)
    z2 = a1@W2+b2; a2 = z2        # L3 linear
    z3 = a2@W3+b3
    return z3, dict(X=X, z1=z1, a1=a1, a2=a2, out=z3)

def mse_loss(p, t): return np.mean((p - t)**2)


# ─── backprop A: gradient descent ─────────────────────────────────────────────
def bp_grad(cache, target, lr, bs):
    global W1, b1, W2, b2, W3, b3
    X, z1, a1, a2, out = cache['X'], cache['z1'], cache['a1'], cache['a2'], cache['out']
    d   = 2*(out - target)/bs
    dW3 = a2.T@d;    db3 = d.sum(0, keepdims=True);   da2 = d@W3.T
    dW2 = a1.T@da2;  db2 = da2.sum(0, keepdims=True);  da1 = da2@W2.T
    dz1 = da1 * relu_d(z1)
    dW1 = X.T@dz1;   db1 = dz1.sum(0, keepdims=True)
    W3 -= lr*dW3; b3 -= lr*db3
    W2 -= lr*dW2; b2 -= lr*db2
    W1 -= lr*dW1; b1 -= lr*db1


# ─── backprop B: LRP-style attribution ────────────────────────────────────────
def bp_attr(cache, target, lr, bs):
    global W1, b1, W2, b2, W3, b3
    X, z1, a1, a2, out = cache['X'], cache['z1'], cache['a1'], cache['a2'], cache['out']
    eps   = 1e-8
    error = out - target
    def attr_back(act, W, err):
        c = np.abs(act[:, :, None]) * np.abs(W[None, :, :])
        return (err[:, None, :] * c / (c.sum(1, keepdims=True) + eps)).sum(2)
    e2  = attr_back(a2, W3, error)
    dW3 = a2.T@error/bs; db3 = error.mean(0, keepdims=True)
    e1  = attr_back(a1, W2, e2)
    dW2 = a1.T@e2/bs;    db2 = e2.mean(0, keepdims=True)
    eg  = e1 * relu_d(z1)
    dW1 = X.T@eg/bs;     db1 = eg.mean(0, keepdims=True)
    W3 -= lr*dW3; b3 -= lr*db3
    W2 -= lr*dW2; b2 -= lr*db2
    W1 -= lr*dW1; b1 -= lr*db1


# ─── backprop C: arc attribution rule (the chip's own learning rule) ──────────
# Per wire:  contribution = |a_in * w|
# Momentum:  EMA  —  m = alpha*m + (1-alpha)*|a*w|
# Feedback:  ONE global sign from output-0 error only  (brainstem.py)
# Delta:     pulse * momentum * sign(a*w) * feedback   (scap.py)
# Online:    one sample at a time
ALPHA_ARC   = 0.75
W_RAIL_ARC  = 3.0
M_FLOOR_ARC = 1e-3
M_CEIL_ARC  = 50.0
arc_M = {}

def _fsign(x):
    return np.where(x >= 0.0, 1.0, -1.0)   # 0 -> +1  (chip convention)

def reset_arc():
    global arc_M
    arc_M = {k: np.ones_like(v)
             for k, v in zip(['W1','b1','W2','b2','W3','b3'],
                             [W1, b1, W2, b2, W3, b3])}

def _arc_step(x1, t1, lr):
    global W1, b1, W2, b2, W3, b3, arc_M
    z1  = x1@W1+b1; a1 = relu(z1)
    a2  = a1@W2+b2
    out = a2@W3+b3
    c = {
        'W1': np.abs(x1[0, :, None]*W1), 'b1': np.abs(b1),
        'W2': np.abs(a1[0, :, None]*W2), 'b2': np.abs(b2),
        'W3': np.abs(a2[0, :, None]*W3), 'b3': np.abs(b3),
    }
    a = ALPHA_ARC
    for k in arc_M:
        arc_M[k] = np.clip(a*arc_M[k] + (1-a)*c[k], M_FLOOR_ARC, M_CEIL_ARC)
    err_s    = float(t1[0, 0] - out[0, 0])
    feedback = 1.0 if err_s >= 0.0 else -1.0
    pulse    = lr * abs(err_s)
    W1 += pulse * arc_M['W1'] * _fsign(x1[0, :, None]*W1) * feedback
    b1 += pulse * arc_M['b1'] * _fsign(b1)                 * feedback
    W2 += pulse * arc_M['W2'] * _fsign(a1[0, :, None]*W2) * feedback
    b2 += pulse * arc_M['b2'] * _fsign(b2)                 * feedback
    W3 += pulse * arc_M['W3'] * _fsign(a2[0, :, None]*W3) * feedback
    b3 += pulse * arc_M['b3'] * _fsign(b3)                 * feedback
    for arr in (W1, b1, W2, b2, W3, b3):
        np.clip(arr, -W_RAIL_ARC, W_RAIL_ARC, out=arr)

def bp_arc(cache, target, lr, bs):
    X = cache['X']
    for i in range(len(X)):
        _arc_step(X[i:i+1], target[i:i+1], lr)


# ─── weight helpers ───────────────────────────────────────────────────────────
def get_weights():
    return {k: v.copy() for k, v in
            zip(['W1','b1','W2','b2','W3','b3'], [W1,b1,W2,b2,W3,b3])}

def _restore_weights(w):
    global W1, b1, W2, b2, W3, b3
    W1[:]=w['W1']; b1[:]=w['b1']
    W2[:]=w['W2']; b2[:]=w['b2']
    W3[:]=w['W3']; b3[:]=w['b3']

def predict_grid(w, n=64):
    """Output-0 on a dense grid — domain follows DOMAIN so it matches true_grid."""
    _restore_weights(w)
    lo, hi = DOMAIN
    g  = np.linspace(lo, hi, n)
    G0, G1 = np.meshgrid(g, g)
    preds, _ = forward(np.column_stack([G0.ravel(), G1.ravel()]))
    return G0, G1, preds[:, 0].reshape(n, n)


# ─── training loop ─────────────────────────────────────────────────────────────
def train(method='grad', epochs=600, batch_size=32, lr=0.05, seed=42):
    reset_weights(seed)
    if method == 'arc':
        reset_arc()
    X, y = make_data()
    bp   = {'grad': bp_grad, 'attr': bp_attr, 'arc': bp_arc}[method]
    hist = []
    for _ in range(epochs):
        idx = np.random.permutation(len(X))
        ep_loss, nb = 0.0, 0
        for s in range(0, len(X), batch_size):
            bi = idx[s:s+batch_size]
            Xb, yb = X[bi], y[bi]
            pred, cache = forward(Xb)
            ep_loss += mse_loss(pred, yb)
            bp(cache, yb, lr, len(Xb))
            nb += 1
        hist.append(ep_loss / nb)
    pred_all, _ = forward(X)
    return hist, X, y, pred_all


# ─── run ──────────────────────────────────────────────────────────────────────
print("Training GRADIENT...")
loss_g,   X, y, pred_g   = train('grad')
weights_g   = get_weights()
print(f"  MSE={loss_g[-1]:.6f}")

print("Training LRP ATTRIBUTION...")
loss_a,   X, y, pred_a   = train('attr')
weights_a   = get_weights()
print(f"  MSE={loss_a[-1]:.6f}")

print("Training ARC RULE...")
loss_arc, X, y, pred_arc = train('arc')
weights_arc = get_weights()
print(f"  MSE={loss_arc[-1]:.6f}")


# ─── precompute all surfaces ───────────────────────────────────────────────────
G0, G1, Z_true = true_grid()          # ground truth — from target_fn
_,  _,  Z_g    = predict_grid(weights_g)
_,  _,  Z_a    = predict_grid(weights_a)
_,  _,  Z_arc  = predict_grid(weights_arc)


# ─── auto color scale from ground truth range ─────────────────────────────────
_zlo  = float(Z_true.min())
_zhi  = float(Z_true.max())
_span = _zhi - _zlo

# diverging colormap if data has both meaningful negative and positive values
_mixed = (_zlo < -0.05 * _span - 0.02) and (_zhi > 0.05 * _span + 0.02)
if _mixed:
    HM_CMAP  = 'RdYlBu_r'
    _bound   = max(abs(_zlo), abs(_zhi))
    HM_VMIN, HM_VMAX = -_bound, _bound
    HM_CLINE = '#333333'
else:
    HM_CMAP  = 'plasma'
    HM_VMIN, HM_VMAX = _zlo, _zhi
    HM_CLINE = 'white'

HM_LEVELS  = np.linspace(HM_VMIN, HM_VMAX, 9)
_z_margin  = 0.12 * _span if _span > 0 else 0.1


# ─── plot helpers ─────────────────────────────────────────────────────────────
def plot_heatmap(ax, Z, title, border_color='#888888'):
    """2D heatmap + iso-value contours. Grid (G0,G1) and scale are globals."""
    ax.pcolormesh(G0, G1, Z, cmap=HM_CMAP,
                  vmin=HM_VMIN, vmax=HM_VMAX, shading='auto')
    cs = ax.contour(G0, G1, Z, levels=HM_LEVELS,
                    colors=HM_CLINE, linewidths=0.9, alpha=0.75)
    ax.clabel(cs, inline=True, fontsize=7, fmt='%.2f', colors=HM_CLINE)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=5)
    ax.set_xlabel('x0', fontsize=9)
    ax.set_ylabel('x1', fontsize=9)
    ax.set_aspect('equal')
    ax.tick_params(labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(2.2)

def plot_3d(ax, X, y_true, y_pred, c_pred, label, mse_val):
    """3D scatter (true + predicted) with wireframe from true_grid."""
    # wireframe — subsampled from the same true_grid that drives the heatmap
    step = max(1, G0.shape[0] // 16)
    ax.plot_wireframe(
        G0[::step, ::step], G1[::step, ::step], Z_true[::step, ::step],
        color=C_TRUE, alpha=0.25, linewidth=0.7, label='True surface'
    )
    # scatter: true values colored by z (same cmap), predictions in method color
    idx = np.argsort(y_true)
    ax.scatter(X[idx, 0], X[idx, 1], y_true[idx],
               c=y_true[idx], cmap=HM_CMAP, vmin=HM_VMIN, vmax=HM_VMAX,
               s=10, alpha=0.4, edgecolors='none', depthshade=True, label='true')
    ax.scatter(X[idx, 0], X[idx, 1], y_pred[idx],
               color=c_pred, s=15, alpha=0.55,
               edgecolors='none', depthshade=True, label='pred')
    # z-axis from ground truth range + margin
    ax.set_zlim(_zlo - _z_margin, _zhi + _z_margin)
    # styling
    ax.set_facecolor('white')
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.set_facecolor('#f5f5f5'); pane.set_edgecolor('#dddddd')
    ax.tick_params(labelsize=8, colors='#444444', pad=1)
    ax.set_xlabel('x0', fontsize=9, labelpad=6)
    ax.set_ylabel('x1', fontsize=9, labelpad=6)
    ax.set_zlabel('y',  fontsize=9, labelpad=4)
    ax.set_title(f'{label}\nMSE = {mse_val:.5f}',
                 fontsize=10, fontweight='bold', pad=8, color='#1a1a1a')
    ax.legend(fontsize=7, loc='upper left', framealpha=0.6, markerscale=1.2)
    ax.view_init(elev=22, azim=220)


# ─── figure  (3 rows x 4 cols) ────────────────────────────────────────────────
# row 0 : loss curve       [spans all 4 cols]
# row 1 : heatmaps         [GT | Gradient | LRP | Arc]
# row 2 : 3D surface plots [blank | Gradient | LRP | Arc]
fig = plt.figure(figsize=(24, 20), facecolor='white')
fig.suptitle(
    f'Gradient  vs  LRP Attribution  vs  Arc Rule  |  y = {DATA_LABEL}',
    fontsize=13, fontweight='bold', color='#1a1a1a', y=0.995
)
gs = gridspec.GridSpec(
    3, 4, figure=fig,
    height_ratios=[0.8, 1.6, 1.5],
    hspace=0.50, wspace=0.30,
    left=0.05, right=0.96, top=0.95, bottom=0.04
)

# row 0 ── loss ───────────────────────────────────────────────────────────────
ax_loss = fig.add_subplot(gs[0, :])
ep_r = range(len(loss_g))
ax_loss.plot(ep_r, loss_g,   color=C_GRAD, lw=2.2,
             label=f'Gradient        (final {loss_g[-1]:.5f})')
ax_loss.plot(ep_r, loss_a,   color=C_ATTR, lw=2.2, ls='--',
             label=f'LRP Attribution (final {loss_a[-1]:.5f})')
ax_loss.plot(ep_r, loss_arc, color=C_ARC,  lw=2.2, ls=':',
             label=f'Arc Rule        (final {loss_arc[-1]:.5f})')
ax_loss.set_xlabel('Epoch', fontsize=11)
ax_loss.set_ylabel('MSE', fontsize=11)
ax_loss.set_title('MSE Loss vs Epoch', fontsize=12, fontweight='bold', pad=8)
ax_loss.legend(fontsize=10, framealpha=0.7)

# row 1 ── heatmaps ───────────────────────────────────────────────────────────
ax_ht = [fig.add_subplot(gs[1, i]) for i in range(4)]
plot_heatmap(ax_ht[0], Z_true, f'Ground Truth\n{DATA_LABEL}',            C_TRUE)
plot_heatmap(ax_ht[1], Z_g,    f'Gradient\nMSE={loss_g[-1]:.5f}',       C_GRAD)
plot_heatmap(ax_ht[2], Z_a,    f'LRP Attribution\nMSE={loss_a[-1]:.5f}', C_ATTR)
plot_heatmap(ax_ht[3], Z_arc,  f'Arc Rule\nMSE={loss_arc[-1]:.5f}',      C_ARC)

sm = plt.cm.ScalarMappable(cmap=HM_CMAP,
                            norm=plt.Normalize(vmin=HM_VMIN, vmax=HM_VMAX))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax_ht, orientation='vertical',
                    fraction=0.015, pad=0.02)
cbar.set_label('y', fontsize=9)
cbar.ax.tick_params(labelsize=8)

# row 2 ── 3D plots ───────────────────────────────────────────────────────────
mse_g   = float(np.mean((pred_g[:,0]   - y[:,0])**2))
mse_a   = float(np.mean((pred_a[:,0]   - y[:,0])**2))
mse_arc = float(np.mean((pred_arc[:,0] - y[:,0])**2))

ax3d = [fig.add_subplot(gs[2, i+1], projection='3d') for i in range(3)]
# gs[2,0] intentionally blank

plot_3d(ax3d[0], X, y[:,0], pred_g[:,0],   C_GRAD, 'Gradient Descent', mse_g)
plot_3d(ax3d[1], X, y[:,0], pred_a[:,0],   C_ATTR, 'LRP Attribution',  mse_a)
plot_3d(ax3d[2], X, y[:,0], pred_arc[:,0], C_ARC,  'Arc Rule',         mse_arc)

plt.savefig('nn_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
print("Saved: nn_comparison.png")
