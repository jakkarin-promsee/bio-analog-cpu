## สรุปทุกอย่างที่คุยกันทั้งหมด

---

### Hebbian Variants ที่เจอ

**1. Hebbian ดิบ**

```
ΔW = η × a_i × a_j
```

ไม่มี constraint → diverge ทุกครั้ง ไม่มี direction

**2. Oja's Rule**

```
ΔW = η × a_j × (a_i - a_j × W_ij)
```

converge → principal component ของ data (PCA)

**3. BCM Rule**

```
ΔW = η × a_i × a_j × (a_j - θ)
θ = sliding threshold
```

converge → selective feature detector เหมือน visual cortex

**4. Competitive Hebbian**

```
winner = argmax(W · x)
ΔW_winner = η × (x - W_winner)
```

converge → cluster centroids (SOM)

**5. Supervised Hebbian / Delta Rule**

```
ΔW = η × x × y_true
```

กลายเป็น Perceptron rule แล้ว ไม่ใช่ Hebbian จริงๆ

**6. Neuromodulated Hebbian**

```
ΔW = η × a_i × a_j × r
r = reward / dopamine signal
```

ใช้ใน RL + Hebbian

---

### Forward-Only Methods ที่เจอ

**1. Hinton FF (2022)**

```
goodness = Σ a²
loss = log(1 + e^(-goodness_pos)) + log(1 + e^(goodness_neg))
```

ต้องการ positive + negative data

**2. Self-Contrastive FF**

```
x_neg = x - α × ∂goodness/∂x
```

สร้าง negative เอง ไม่ต้องหาจากภายนอก

**3. Collaborative FF**

```
goodness_collab = Σ_l w_l × goodness_l
```

layers share goodness ข้าม layer

**4. Mono-Forward**

```
forward รอบเดียว ไม่ต้อง negative pass
```

เร็วสุดในกลุ่ม FF

---

### Credit Assignment Methods ที่เจอ

**1. Attribution-Based (LRP)**

```
e_i = Σ_j [ e_j × (|a_i·W_ij| / Σ_i|a_i·W_ij|) ]
```

ใช้ใน explainability ไม่ใช่ training

**2. Target Propagation**

```
target_{l-1} = a_{l-1} - α × δ_{l-1}
```

ส่ง target แทน gradient

**3. Prospective Configuration**

```
infer target pattern ก่อน → update weight ทีหลัง
```

เหมือนสมองจริงๆ

**4. Stochastic Variational Propagation**

```
optimize local ELBO แต่ละ layer แยกกัน
```

treat activation เป็น latent variable

---

### สิ่งที่คุณประยุกต์ใช้จริงใน Architecture

**ผสม 4 อย่างเข้าด้วยกัน:**

```
1. Hebbian (type A broadcast):
   ΔW = η_h × a_{l-1}^T · a_l
   → เรียน co-activation ตอนไม่มี backward

2. Attribution-based local update (type B broadcast):
   ΔW = η_b × error^T · (C / Σ C)
   C = |a| ⊗ |W|
   → กระจาย credit ตาม contribution

3. W_eff approximation (δ chain):
   W_eff = a_out^T · pinv(a_in^T)
   δ_{l-1} = δ_l · W_eff
   → approximate backward โดยไม่ต้อง W^T จริงๆ

4. Hippocampal Replay (consolidation):
   replay (a_in, a_out, loss) ตอน "นอน"
   full backward ครบทุก layer
   → แก้ vanishing จาก random layer selection
```
