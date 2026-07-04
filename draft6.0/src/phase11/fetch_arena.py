"""P11.0 bench — the ONE deliberate network session (isolated per-arena downloads).

Run ONE arena per process so a hang on one never blocks another; each call writes
data/<arena>.npz (or logs a clean FAIL). Live cells NEVER call this — they load the
local cache. Reliable routes chosen to dodge the dead api.openml.org:
  fashion  -> Zalando github idx.gz          (bypasses openml)
  covtype  -> sklearn.fetch_covtype (figshare)
  gas      -> UCI static/public/224 zip
  har      -> UCI static/public/240 zip (double-nested)
  electric -> openml 151 (best-effort; may time out)
Usage:  python -u fetch_arena.py <fashion|covtype|gas|har|electric>
"""
import sys, os, io, gzip, zipfile, urllib.request, ssl, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RAW  = os.path.join(DATA, "raw")
os.makedirs(RAW, exist_ok=True)
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE          # this box has a documented cert block


def _get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
        return r.read()


def _save(name, **arrays):
    path = os.path.join(DATA, name + ".npz")
    np.savez_compressed(path, **arrays)
    shapes = {k: v.shape for k, v in arrays.items()}
    print(f"[OK] {name} -> {path}  {shapes}", flush=True)


def _idx_images(buf):
    b = gzip.decompress(buf)
    n = int.from_bytes(b[4:8], "big"); r = int.from_bytes(b[8:12], "big"); c = int.from_bytes(b[12:16], "big")
    return np.frombuffer(b[16:], np.uint8).reshape(n, r * c).astype(np.float32)


def _idx_labels(buf):
    b = gzip.decompress(buf)
    return np.frombuffer(b[8:], np.uint8).astype(np.int64)


def fetch_fashion():
    base = "https://github.com/zalandoresearch/fashion-mnist/raw/master/data/fashion/"
    Xtr = _idx_images(_get(base + "train-images-idx3-ubyte.gz"))
    ytr = _idx_labels(_get(base + "train-labels-idx1-ubyte.gz"))
    Xte = _idx_images(_get(base + "t10k-images-idx3-ubyte.gz"))
    yte = _idx_labels(_get(base + "t10k-labels-idx1-ubyte.gz"))
    _save("fashion", Xtr=Xtr, ytr=ytr, Xte=Xte, yte=yte)


def fetch_covtype():
    from sklearn.datasets import fetch_covtype
    d = fetch_covtype()                     # figshare mirror; file order preserved
    _save("covtype", X=d.data.astype(np.float32), y=d.target.astype(np.int64))


def fetch_gas():
    url = "https://archive.ics.uci.edu/static/public/224/gas+sensor+array+drift+dataset.zip"
    raw = _get(url, timeout=120)
    open(os.path.join(RAW, "gas.zip"), "wb").write(raw)
    z = zipfile.ZipFile(io.BytesIO(raw))
    # find batch1.dat..batch10.dat anywhere in the (possibly nested) archive
    names = [n for n in z.namelist() if n.lower().endswith(".dat") and "batch" in n.lower()]
    def keyf(n):
        base = os.path.basename(n).lower().replace("batch", "").replace(".dat", "")
        return int("".join(ch for ch in base if ch.isdigit()) or 0)
    names = sorted(names, key=keyf)
    Xs, ys, bs = [], [], []
    for n in names:
        bidx = keyf(n)
        for line in z.read(n).decode("utf-8", "ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            head, *feats = line.split()
            cls = int(head.split(";")[0])
            vec = np.zeros(128, np.float32)
            for f in feats:
                if ":" in f:
                    i, v = f.split(":")
                    j = int(i) - 1
                    if 0 <= j < 128:
                        vec[j] = float(v)
            Xs.append(vec); ys.append(cls); bs.append(bidx)
    _save("gas", X=np.array(Xs, np.float32), y=np.array(ys, np.int64), batch=np.array(bs, np.int64))


def fetch_har():
    url = "https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip"
    raw = _get(url, timeout=120)
    open(os.path.join(RAW, "har.zip"), "wb").write(raw)
    z = zipfile.ZipFile(io.BytesIO(raw))
    inner = [n for n in z.namelist() if n.lower().endswith(".zip")]
    zz = zipfile.ZipFile(io.BytesIO(z.read(inner[0]))) if inner else z
    def load(split):
        def rd(p):
            # exact-basename match: 'y_train.txt' must NOT hit 'body_acc_y_train.txt' (the inertial-signals trap)
            cand = [n for n in zz.namelist() if os.path.basename(n) == p and "Inertial" not in n]
            return zz.read(cand[0]).decode("utf-8", "ignore")
        X = np.array([[float(v) for v in ln.split()] for ln in rd(f"X_{split}.txt").splitlines() if ln.strip()], np.float32)
        y = np.array([int(v) for v in rd(f"y_{split}.txt").split()], np.int64)
        s = np.array([int(v) for v in rd(f"subject_{split}.txt").split()], np.int64)
        return X, y, s
    Xtr, ytr, str_ = load("train"); Xte, yte, ste = load("test")
    X = np.vstack([Xtr, Xte]); y = np.concatenate([ytr, yte]); subj = np.concatenate([str_, ste])
    _save("har", X=X, y=y, subject=subj)


def fetch_electric():
    from sklearn.datasets import fetch_openml
    d = fetch_openml(data_id=151, as_frame=False, parser="liac-arff")   # ELEC2, chronological v1
    X = np.asarray(d.data, np.float32)
    yr = np.asarray(d.target)
    classes = sorted(set(yr.tolist()))
    y = np.array([classes.index(v) for v in yr], np.int64)
    _save("electric", X=X, y=y)


FETCH = {"fashion": fetch_fashion, "covtype": fetch_covtype, "gas": fetch_gas,
         "har": fetch_har, "electric": fetch_electric}

if __name__ == "__main__":
    name = sys.argv[1]
    t = time.time()
    try:
        FETCH[name]()
        print(f"[DONE] {name} in {time.time()-t:.1f}s", flush=True)
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {str(e)[:200]}", flush=True)
        sys.exit(1)
