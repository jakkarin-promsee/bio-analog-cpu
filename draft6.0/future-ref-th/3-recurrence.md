# 3 — วงลูป / "คิดวนหลายรอบจนกว่าจะนิ่ง"

> คำถามของคุณ: *"ต้องเป็น LSTM เต็มตัวไหม? recurrent แค่ไหน?"* คำตอบที่ผมเถียงไว้: **ไม่ใช่ LSTM เป็นแกน** สมอง (และตัวอย่างรถสีส้มของคุณ) รันวงลูป *หลายรอบบนอินพุตเดียว* จนกว่ามันจะหยุดเปลี่ยน — นั่นคือการคำนวณแบบ **fixed-point / equilibrium** ซึ่ง **ฮาร์ดแวร์แอนะล็อกทำให้ฟรี** และเป็นสิ่งที่ทั้ง LSTM (ก้าวเดียวต่ออินพุต) และ transformer (ไม่มี recurrence ในแนวลึก) ต่างพลาดไป เก็บ *gate* สไตล์ LSTM ไว้สำหรับความจำข้ามเวลา; แต่อย่าทำให้มันเป็นตัวคิด

---

## Deep Equilibrium Models (DEQ) — แก้หา fixed point โดยตรง

*Bai, Kolter & Koltun, 2019, NeurIPS ([arXiv 1909.01377](https://arxiv.org/abs/1909.01377)).*

### ปัญหาที่มันแก้

ลองนึกภาพ: คุณซ้อน transformer block 100 ชั้นเพื่อให้ deep มากขึ้น ถ้าดูอย่างดี hidden state ของ layer 90, 95, 99 ก็แทบเหมือนกันแล้ว มันเหมือนกำลัง "วนลูปซ้ำๆ จนกว่าจะนิ่ง" แต่เราทิ้ง 99 ชุดของ intermediate activations ไว้ใน memory เพื่อ backprop Bai และทีมถามว่า: "ถ้าเราแก้หา fixed point โดยตรงแทนล่ะ?"

### กลไกจริงๆ

**Weight tying**: แทนที่จะมี layer 1, layer 2, layer 3 ที่แตกต่างกัน DEQ ใช้ **block เดียวกัน f(z; θ)** ซ้ำๆ คล้ายกับ RNN แต่แทนที่จะทำ T steps ที่กำหนดไว้ล่วงหน้า มัน:

**ขั้นที่ 1 — Forward (inference)**: หา z* ที่ satisfy:
```
z* = f(z*, x; θ)
```
โดยใช้ root-finding algorithm (Broyden's method หรือ Anderson acceleration) — นี่คือการแก้สมการ implicit ไม่ใช่การซ้อนชั้น Broyden เหมือน Newton's method แต่ไม่ต้องคำนวณ Jacobian เต็ม: ใช้ rank-1 update จาก iterations ก่อนหน้า ใช้ computational effort น้อยกว่า "unroll 100 steps" มาก

**ขั้นที่ 2 — Backward (training)**: ถ้าใช้ backprop ธรรมดา ต้องเก็บ computation graph ของการ iterate ทั้งหมด → หน่วยความจำ O(T) ซึ่ง T อาจเป็น 50-100 DEQ ใช้ **implicit differentiation**:

จากสมการ z* = f(z*, x; θ):
```
dz*/dθ = -(∂f/∂z*|_{z*} - I)^{-1} (∂f/∂θ|_{z*})
```
ซึ่งหมายความว่าต้องแก้ระบบ linear หนึ่งครั้งที่ z* แทนที่จะ backprop ผ่านทุก iteration และ **หน่วยความจำ O(1)** ไม่ว่าจะ "ลึก" แค่ไหน

### ผลที่น่าตื่นเต้น

บน language modeling: DEQ ที่ระบุ depth เทียบเท่า infinite layer ทำได้ดีพอๆ กับ Transformer 12 layers ด้วย parameter น้อยกว่าเพราะ weight tied

Memory: DEQ ใช้ RAM น้อยกว่า deep network 6-8x เพราะไม่เก็บ intermediate activations ระหว่างหลายๆ ชั้น

AlphaFold 2 ใช้ DEQ-like ideas ใน evoformer — block เดียวที่ iterate จนโครงสร้างโปรตีน converge มันเป็นตัวอย่างที่ทรงพลังที่สุดของ "วงลูปจนนิ่ง = เข้าใจแล้ว" ในวงการ ML

### สำหรับเรา

นี่คือ **mathematical license** สำหรับวิธีที่ substrate แอนะล็อกทำงาน:

**วงจรแอนะล็อกหา fixed point ด้วยการคลายตัวลงไปหามันทางกายภาพ** — RC circuit ทุกตัว capacitor ทุกอัน ธรรมชาติมันคือการ settle ไปยัง equilibrium DEQ บอกว่านี่คือ "การคำนวณ" ที่ถูกต้องและ expressiveness เทียบเท่า deep network ไม่ใช่ shortcut

ความแตกต่างสำคัญ: DEQ ต้องการ root-finder algorithm ที่รัน iterations หลายรอบ ซึ่งใน software แปลว่า "เร็ว แต่ไม่ฟรี" แต่บน **analog substrate มัน "ฟรี"** จริงๆ — วงจรแค่ settle ไปเองตาม physics โดยไม่มี clock cycle ที่ต้องซื้อ

ดังนั้น: ไม่ต้องออกแบบ "กี่ layer" ของ prefrontal loop ในเฟส 2 แค่ออกแบบ **หนึ่ง block ที่ดี** แล้วปล่อยให้ settle เองตามธรรมชาติ depth คือจำนวน settling time ไม่ใช่จำนวน module ที่ซ้อน

---

## Equilibrium Propagation (EqProp) — และการ settle นั้น *ยังให้* gradient ด้วย

*Scellier & Bengio, 2017 ([Frontiers in Computational Neuroscience](https://www.frontiersin.org/articles/10.3389/fncom.2017.00024/full)).*

### ปัญหาที่มันแก้

DEQ บอกว่า "การ settle = การคำนวณ" แต่ยังไม่ตอบ: *"แล้วเรียนรู้ยังไง?"* ถ้า backprop ผ่าน settling (DEQ แก้ด้วย implicit differentiation) มันยังต้องการ global information ไหลผ่านทุก weight พร้อมกัน — ซึ่งบน biological / analog substrate เป็นไปไม่ได้ EqProp ตอบว่า: **เรียนรู้ได้จาก local information จากการ settle สองครั้ง**

### กลไกจริงๆ

EqProp ทำงานกับ **energy-based network** — ตาข่ายที่มีฟังก์ชัน energy F(s, x, y; θ) โดย s คือ hidden state, x คือ input, y คือ output เป้าหมาย

**Phase 1 — Free phase**: clamp แค่ input x ปล่อยให้ s settle จนพบ:
```
s* = argmin_s F(s, x; θ)
```
นี่คือ "การคิด" ปกติ — หา equilibrium ของ state ที่ minimize energy กับ input ที่กำหนด

**Phase 2 — Nudge phase**: clamp ทั้ง input x **และ** output y (nudge เล็กน้อยด้วยแรงขนาด β ดึงไปยัง target) ปล่อยให้ settle อีกครั้ง:
```
s**(β) = argmin_s [F(s, x; θ) + β/2 ||y_output - y_target||²]
```

**Weight update**: ผลต่างของ energy gradient ระหว่างสอง equilibrium:
```
Δθ ∝ (1/β) [∂F/∂θ|_{s**} - ∂F/∂θ|_{s*}]
```

ในลิมิต β→0: นี่พิสูจน์ได้ว่าเท่ากับ **gradient ของ loss ตาม θ อย่างแม่นยำ** และที่สำคัญ: ∂F/∂θ ที่แต่ละ synapse คือ **local function** (เช่น s_i × s_j สำหรับ synapse (i,j)) ดังนั้น weight update คือ Hebbian-like ทั้งหมด: **ความแตกต่างของ correlation ระหว่างสอง equilibrium** — ไม่มี global backprop

### ผลที่น่าตื่นเต้น

EqProp สามารถเรียนรู้ MNIST, CIFAR ได้โดย **ไม่ใช้ backpropagation เลย** — มีแค่สองรอบ settle และ Hebbian subtraction local ผลลัพธ์ยังห่างจาก backprop บ้าง (4-5% gap) แต่มันพิสูจน์ concept ว่า local learning ผ่าน contrastive Hebbian ทำงานได้จริง

งานสายนี้ยังเชื่อมกับ **Boltzmann machine** (Hinton): free energy ของ EqProp เทียบเท่า RBM energy และ contrastive phase เป็นกลไกเดียวกับ contrastive divergence

### สำหรับเรา

EqProp คือ **ตัวเก็งอันดับต้นๆ สำหรับ "gradient บน analog circuit แบบ local"** และมันต่อกับ DEQ ได้พอดิบพอดี:

**การ settle เดียวกันที่ทำการคิดให้คุณ → ยังผลิต gradient signal ได้ด้วย** แบบ local ไม่ต้องมี backward pass

ใน hardware: Phase 1 = วงจร settle ตามธรรมชาติ, Phase 2 = เพิ่ม feedback เล็กน้อยจาก "target" (อาจมาจาก hippocampus replay หรือ GD block ใน draft 6.0), Weight update = local Hebbian subtraction บนแต่ละ Scap

ข้อต้องระวัง: EqProp ต้องการ **symmetric connections** (W_ij = W_ji) ซึ่งต้องการ matching capacitor อย่างละเอียด บน analog ที่มี mismatch อาจเป็นปัญหา และ feedback ที่สมมาตรต้องออกแบบพิเศษ มันเป็นต้นทุนที่ต้องวัดในการทดลองก่อน ว่า symmetric constraint tight แค่ไหนถึงจะเรียนได้

---

## Predictive Coding — การอนุมานแบบวนซ้ำในฐานะค่าตั้งต้นของสมอง

*Rao & Ballard, 1999; ในฐานะตัวประมาณ backprop: Whittington & Bogacz, 2017.*

### ปัญหาที่มันแก้

ในปี 1999 Rao และ Ballard เห็นข้อมูลประสาทวิทยาที่แปลก: neurons ใน visual cortex ที่ "respond to edges" นั้นจริงๆ response มันซับซ้อนกว่า — มันดูเหมือน subtract prediction ออกก่อน แล้ว response ต่อ "สิ่งที่ไม่ได้คาด" ถ้าสมองทำนายสิ่งที่จะเห็นล่วงหน้าแล้วส่ง error ขึ้นมา ทำไมมันถึงทำอย่างนั้น?

### กลไกจริงๆ

Predictive coding เป็น **ลำดับชั้นของ generator และ error detector** แทรกสลับกัน:

สำหรับ network ที่มี L ชั้น ที่ชั้น l:
- **Representation node** r_l: เก็บ belief เกี่ยวกับโลกที่ระดับ abstraction l
- **Prediction node**: คำนวณ prediction ลงไปยังชั้นล่าง: μ_{l-1} = g(r_l) (top-down prediction)
- **Error node** e_{l-1}: คำนวณ prediction error: e_{l-1} = r_{l-1} - μ_{l-1}

การ update (inference) ทำแบบ **gradient descent บนผลรวมของ prediction errors ทุกชั้น**:
```
dr_l/dt = -∂F/∂r_l = e_l - ∂μ_l/∂r_l · e_{l-1}
```

ซึ่งแปลว่า: r_l update ตาม error จากชั้นบน (e_l) ลบกับ ∂μ/∂r ครั้ง error ที่ส่งลงมา (e_{l-1}) — **local ทั้งหมด** ไม่มีการส่งสัญญาณ global

การ **settle** จนกว่า error ทุกชั้นจะน้อยมาก = "เข้าใจ stimulus แล้ว" = free energy ต่ำแล้ว จากนั้น:
- Weight update (learning): Δθ_l ∝ e_{l-1} · r_l^T (Hebbian กับ error signal)

Whittington & Bogacz 2017 พิสูจน์ว่า: ในลิมิตที่ precision เท่ากันทุกชั้น weight update ของ predictive coding **ประมาณ backprop ได้แม่น**

### ผลที่น่าตื่นเต้น

งาน simulation: predictive coding สามารถเรียนรู้ MNIST, CIFAR ได้โดยไม่ใช้ backprop explicit ด้วยความแม่นคล้ายกัน งานสาย bio-plausible learning ที่ดีที่สุดในปัจจุบัน

งานกับ visual cortex: predictive coding จำลอง response ของ neurons ใน V1, V2, IT ได้ตรงกับข้อมูล fMRI — neurons ที่ level สูงทำนายลงมา neurons ที่ level ต่ำ response ต่อ error ที่เหลือ

### สำหรับเรา

Predictive coding คือ **สะพานสำคัญ** ระหว่างสองไอเดีย:

1. "Settle ลงสู่ equilibrium = ทำความเข้าใจ" (DEQ)
2. "ความรู้สึกถูกต้อง = prediction error ต่ำ" (File 4)

บน SCFF stack ปัจจุบัน residual connection ที่คุณมีอยู่แล้วคือ prediction error path — เลเยอร์บนทำนายว่า activation ของเลเยอร์ล่างควรเป็นอะไร แล้วส่ง residual (ที่เหลือหลังหัก prediction) ขึ้นไป ซึ่งหมายความว่า **SCFF stack ที่มี skip connections อยู่แล้วเป็น predictive coding network ครึ่งหนึ่ง** โดยไม่รู้ตัว

สิ่งที่เฟส 2 จะเพิ่มคือ **top-down prediction path**: prefrontal ส่ง prediction ลงมายัง SCFF ทำให้ SCFF บวกทั้ง bottom-up input และ top-down prior — นี่คือ **bidirectional hierarchy** ที่ draft-5 เคยพลาดไป

---

## Adaptive Computation Time & PonderNet — *เรียนรู้* ว่าจะหยุดเมื่อไหร่

*ACT: Graves, 2016 ([arXiv 1603.08983](https://arxiv.org/abs/1603.08983)); PonderNet: Banino, Balaguer & Blundell, 2021 ([arXiv 2107.05407](https://arxiv.org/abs/2107.05407)).*

### ปัญหาที่มันแก้

ถ้า network วนลูปจนนิ่ง (DEQ) คำถามที่ตามมาทันทีคือ: **"หยุดเมื่อไหร่?"** ถ้ากำหนด T steps ตายตัว — บางงานง่ายที่ใช้แค่ 3 steps จะต้องรอ 10 steps โดยเปล่าประโยชน์ บางงานยากที่ต้องการ 20 steps จะถูก cut ที่ 10 ACT เสนอว่าให้ **network เรียนรู้เองว่าจะหยุดเมื่อไหร่** ต่อแต่ละ input

### กลไกจริงๆ

**ACT (Graves 2016)**:

ที่แต่ละ step n network ผลิต:
- hidden state h_n = f(h_{n-1}, input)
- **halting probability** p_n = sigmoid(W·h_n + b) ∈ (0,1)

Cumulative probability: R_n = Σ_{t=1}^{n} p_t เมื่อ R_N ≥ 1 → หยุดที่ step N

Output เป็น weighted average: ŷ = Σ_{n=1}^{N} h_n · λ_n โดย λ_n คือ น้ำหนักที่ normalize ตาม p_n

Regularization: เพิ่ม ponder cost ∝ N (บทลงโทษเวลาที่ใช้) เพื่อไม่ให้ network คิดนานโดยไม่จำเป็น

**PonderNet (Banino et al. 2021)**:

ปัญหาของ ACT: การ average output ทำให้ gradient ไหลไม่ดีเสมอ PonderNet เปลี่ยนวิธีมอง: ที่แต่ละ step n network ผลิต **(y_n, h_n, λ_n)** โดย:
- y_n = output ที่ step n
- λ_n = prob ว่าจะหยุดที่ step n นี้ (ไม่ใช่ cumulative)
- n_halt ~ Categorical(λ₁, λ₂, ...) — random variable ว่าจะหยุดที่ step ไหน

Loss มีสองส่วน:
```
L = E_{n~p(halt)}[L_task(y_n)] + β · D_KL(p(halt) || Geometric(λ_prior))
```

ส่วนแรก: loss ของ output ที่ step ที่หยุด (random, averaged over distribution)
ส่วนที่สอง: KL ระหว่าง halt distribution กับ geometric prior (ต้องการหยุดเร็วๆ ถ้าทำได้)

ผลคือ network **เรียนรู้ว่า step ไหนที่ "พอแล้ว"** สำหรับ input นั้นๆ โดย gradient flow ชัดเจน

### ผลที่น่าตื่นเต้น

ACT บน Universal Transformer: input ที่ง่ายใช้ 2-3 steps, input ที่ยากใช้ 6-10 steps — สอดคล้องกับสัญชาตญาณ

PonderNet บน **parity task** (นับว่า 1 มีจำนวนคี่หรือคู่ใน sequence ยาว): ยิ่ง sequence ยาว ยิ่งใช้ steps มาก — เกิด complexity-sensitive computation โดยอัตโนมัติ

PonderNet บน **shortest path**: รันมากขึ้นสำหรับ graph ที่ซับซ้อนกว่า generalize ได้ดีกว่า fixed-depth network

### สำหรับเรา

นี่คือ **กลไก "หยุดเมื่อความรู้สึกจุดติด" ที่ทำให้เรียนรู้ได้** และที่เจ๋งสุดคือ:

**Halt probability = ความรู้สึกว่าถูกที่ข้ามเกณฑ์** — วงลูป settle จนนิ่ง (DEQ) แต่มี halting head ขนาดเล็กที่อ่าน current state แล้วบอกว่า "พอแล้ว" เมื่อ λ_n สูงพอ ซึ่งในแอนะล็อก halting head อาจเป็นวงจรที่วัด **rate of change ของ state** — ถ้า |dz/dt| < threshold → นิ่งแล้ว → หยุด ไม่ต้องมี learned classifier เลยด้วยซ้ำ

**Adaptive computation time = ประสิทธิภาพพลังงาน**: input ง่าย settle เร็ว ใช้พลังงานน้อย input ยากใช้เวลานานขึ้น ซึ่งสำหรับ always-on chip หมายถึง dynamic power proportional to difficulty — biological efficiency จริงๆ

---

## Universal Transformer — recurrence ในแนวลึก พร้อมการหยุด

*Dehghani, Gouws, Vinyals, Uszkoreit & Kaiser, 2018 ([arXiv 1807.03819](https://arxiv.org/abs/1807.03819)).*

### ปัญหาที่มันแก้

Standard Transformer: แต่ละ layer มี weight ต่างกัน ซ้อน L layers แต่ไม่มีการ iterate ซ้ำบน input เดิม ไม่ใช่ recurrent ในแนวลึก LSTM: recurrent แต่ทำก้าวเดียวต่อ input token ไม่มี attention เป็น core Universal Transformer รวมทั้งสอง: **recurrence + attention**

### กลไกจริงๆ

Universal Transformer เอา Transformer block เดียวมาทำซ้ำ T รอบ (weight tied):

```
h^{t+1} = Transformer_Block(h^t, x; θ_shared)
```

แต่ละรอบ block เดิมรับ current state h^t, original input x และอัปเดต state พร้อม ACT สำหรับแต่ละ token (token ที่หยุดแล้วไม่ถูก update)

ผลคือเป็น **ทัวริงสมบูรณ์** (Turing-complete) ในทางทฤษฎี เพราะ recurrence + adaptive halting = สามารถจำลอง Turing machine ได้ ต่างจาก standard Transformer ที่มี fixed depth จึงมี fixed computation budget

### ผลที่น่าตื่นเต้น

บน **algorithmic tasks** (copy, reverse, sort) Universal Transformer ดีกว่า standard Transformer ชัดเจน เพราะ standard Transformer ต้องซ้อน L layers ที่ต่างกัน แต่ Universal Transformer ใช้ block เดียวซ้ำ → เรียนรู้ "algorithm" ไม่ใช่ "depth-specific pattern"

บน **language understanding**: ดีพอๆ กัน แต่ parameter น้อยกว่า (weight shared)

### สำหรับเรา

Universal Transformer เป็น **ตัวอย่างที่สะอาดที่สุดของ "block เดียว วนซ้ำ"** และมันเหมาะกับ substrate:

**Shared-weight block + analog settling = Universal Transformer** บนชิปที่มี weight ใน Scap: แทนที่จะออกแบบ "N layer ที่ต่างกัน" ออกแบบ "block ดีที่สุดหนึ่งอัน" แล้ว:
- Digital mode: clock มันหลาย T rounds
- Analog mode: ปล่อย settle ทางกายภาพ

ทั้งสองได้ผลเดียวกันทาง math แต่ analog ทำได้ "ฟรี" โดยไม่ต้องจ่าย clock cycle

สำหรับเฟส 2: prefrontal loop ไม่ใช่ "layer ซ้อนหลายชั้น" แต่เป็น "block เดียวที่ query hippocampus วนซ้ำจนนิ่ง" นี่คือ implementation ที่เรียบง่ายที่สุดของ recurrent thought

---

## LSTM / GRU — เก็บ gate ไว้ ไม่ใช่เก็บบัลลังก์

*Hochreiter & Schmidhuber, 1997; GRU: Cho et al., 2014.*

### ปัญหาที่มันแก้

RNN ธรรมดาในปี 1990s มีปัญหา vanishing gradient — signal จากก้าว time step ห่างๆ หายไปก่อนที่จะเดินทางกลับมา Hochreiter พบว่าสาเหตุคือ gradient ถูก scale ด้วย W ซ้ำๆ ถ้า eigenvalue < 1 มันยุบ ถ้า > 1 มันระเบิด LSTM แก้ด้วยการ **ทำเส้นทาง identity** (constant error carousel)

### กลไกจริงๆ

LSTM มี **cell state c_t** ที่ไหลผ่านเวลาโดยถูกแตะแค่ผ่าน **elementwise operations** (ไม่ผ่าน matrix multiply):

```
c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t
```

โดย:
- **f_t (forget gate)** = σ(W_f · [h_{t-1}, x_t]) ∈ (0,1) — "จำได้ fraction เท่าไหร่จากก้าวที่แล้ว"
- **i_t (input gate)** = σ(W_i · [h_{t-1}, x_t]) ∈ (0,1) — "รับ input ใหม่เท่าไหร่"
- **g_t (candidate)** = tanh(W_g · [h_{t-1}, x_t]) ∈ (-1,1) — "input ใหม่คืออะไร"
- **o_t (output gate)** = σ(W_o · [h_{t-1}, x_t]) ∈ (0,1) — "อ่าน cell state ออกเท่าไหร่"
- **h_t** = o_t ⊙ tanh(c_t) — hidden state ที่ส่งออก

c_t ไหล "ตรงๆ" ข้ามเวลา gradient จึงไหลกลับได้โดยไม่ vanish GRU ลด gate เหลือสองตัว (reset, update) แทน แต่ idea เดิม

### ผลที่น่าตื่นเต้น

LSTM พิสูจน์ตัวเองในงาน sequence-to-sequence แทบทุกประเภทตลอดทศวรรษ 2000-2015: machine translation, speech recognition, music generation, protein sequence analysis ก่อนที่ Transformer จะเข้ามาแทน มันทำงานได้เพราะ gate ช่วยให้เรียนว่า "จำอะไร ลืมอะไร" ได้อย่างยืดหยุ่น

### สำหรับเรา

สัญชาตญาณคุณถูก: **ลด LSTM จากแกนมาเป็นองค์ประกอบ**

สิ่งที่ LSTM ดีที่สุดคือ **gate — วาล์วที่เรียนรู้ได้สำหรับความจำข้ามเวลา** ซึ่งยังต้องการอยู่ใน:
- เก็บ context ข้ามหลาย query (ตอนที่กำลัง "คิด" ต้องจำว่ากำลังทำอะไร)
- เรียนว่าเมื่อไหร่ควร reset state (จบงานหนึ่งเริ่มงานใหม่)
- ควบคุม flow ของ information ใน hippocampus LUT (PBWM ที่ถูกลง)

แต่ **"การคิด" ไม่ใช่ LSTM** — ไม่ใช่ "ก้าวเดียวต่อ input" แต่เป็น "วนลูปบน input เดียวจนนิ่ง" LSTM คือ *projection* ของสมอง recurrent ลงบนก้าวเดียว เฟส 2 ต้องการ settling เต็มๆ (DEQ) ไม่ใช่ gate ธรรมดา

ในเชิง implementation บน substrate: gate ของ LSTM คือ **transmission gate analog** ที่ถูกมาก (transistor เดียว controlled โดย voltage) ส่วนการ settle คือ **RC network ที่ drain ไปยัง equilibrium** ทั้งสองอยู่ใน toolbox อยู่แล้ว แค่ต้องออกแบบให้ถูกที่

---

## รูปร่างของคำตอบ (ไฟล์นี้)

recurrence สำหรับเรา **ไม่ใช่ "ใช้ LSTM"** แต่คือ:

- **วนลูปจนกว่าจะ settle ลงสู่ fixed point (DEQ)** — substrate แอนะล็อกทำมันเป็นการคลายตัวทางกายภาพแบบฟรี
- **การ settle นั้นยัง produce gradient signal ได้แบบ local (EqProp, predictive coding)** — สองรอบ settle + Hebbian subtraction = learning ที่ไม่ต้อง backprop global
- **Bidirectional: top-down prediction + bottom-up error (predictive coding)** — เชื่อม "การคิด" กับ "ความรู้สึก" ผ่าน error minimization
- **จำนวนรอบเป็น adaptive ที่เรียนรู้ได้ (ACT/PonderNet)** — หยุดเมื่อความรู้สึกบอกว่าพอ
- **Block เดียว weight-tied วนซ้ำ (Universal Transformer)** — ง่ายกว่าหลาย layer สำหรับ substrate
- **Gate ของ LSTM** เก็บไว้เฉพาะสำหรับ memory-across-time — ไม่ใช่เป็นแกนของการคิด

วงลูปชั้นในคือ physics ของ analog; วงลูปชั้นนอกคือ gate + halt logic ที่เรียนรู้ได้ ทั้งสองอยู่ใน substrate ที่มีอยู่แล้ว แค่ต้องเดินสายให้ถูก
