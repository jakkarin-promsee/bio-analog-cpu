# 10 — forward + เรียนรู้แบบเร็วและ realtime (online, สตรีม, latency ต่ำ)

> คำพูดของคุณ: *"forward และการเรียนรู้ที่เร็วและ realtime ได้"* นี่คือข้อกำหนดเชิงระบบที่ยากที่สุดในทั้งโปรเจกต์ เพราะ deep learning มาตรฐานคือ *ตรงข้าม* กับ realtime: มันเรียนจาก **ทั้ง batch** ด้วย **backward pass เหนือประวัติที่เก็บไว้** ชิปที่เรียนรู้ *ขณะรัน ทีละตัวอย่าง เดี๋ยวนี้* ต้องใช้วิธีคนละตระกูล ข่าวดี: ตระกูลนั้นมีอยู่จริง มีแรงบันดาลใจจากชีววิทยา และ substrate ของคุณสร้างมาเพื่อมัน

---

## ปัญหา: ทำไมการเทรนปกติถึงไม่ realtime

Backpropagation-Through-Time (BPTT) คือวิธีที่ RNN/Transformer เรียนซีเควนซ์ มีสามจุดตายสำหรับ realtime:

**จุดตาย 1 — ต้องการอนาคต:** gradient ไหลย้อนหลังผ่าน timesteps ทั้งหมดในซีเควนซ์ นั่นหมายถึง gradient ที่ timestep t ขึ้นกับ loss ที่ timestep T (สุดท้าย) คุณต้องรอให้ sequence จบก่อนถึงจะเรียนรู้ได้ — ไม่ causal

**จุดตาย 2 — ต้องการความจำทั้งประวัติ:** BPTT store activations ทุก timestep เพื่อ compute gradient — memory O(T×n) ที่ T = sequence length และ n = hidden size sequence ยาว = memory หมด

**จุดตาย 3 — offline เท่านั้น:** เรียนรู้เป็น batch แบบ offline ต้องมี dataset สมบูรณ์ก่อน ไม่ใช่การเรียนรู้จาก stream ที่กำลังเกิดขึ้น

ทุกวิธีข้างล่างทิ้งข้อกำหนด backward-เหนือ-ประวัติทิ้งไปคนละวิธี

---

## Real-Time Recurrent Learning (RTRL) — gradient online ที่เป๊ะ ไปข้างหน้าอย่างเดียว

*Williams & Zipser, 1989; มุมมองสมัยใหม่: Zucchet & Orvieto, 2023 ([arXiv 2305.19044](https://arxiv.org/abs/2305.19044)).*

### ปัญหา: มี exact gradient โดยไม่เก็บประวัติได้มั้ย?

RTRL เป็นคำตอบที่ "ถูกต้องสมบูรณ์" สำหรับคำถามนี้ และพร้อมกันก็แสดงว่าทำไมมันถึงยาก

### กลไก: พก influence matrix ไปข้างหน้าตลอดเวลา

ใน RNN state `h_t = f(h_{t-1}, x_t, W)` RTRL คำนวณ **influence matrix** `P_t` ที่บอกว่า: "h_t แต่ละมิติขึ้นกับ W แต่ละ weight อย่างไร?"

```
P_t = ∂h_t/∂W
```

Update rule:
```
P_t = (∂h_t/∂h_{t-1}) · P_{t-1} + (∂h_t/∂W)|_{direct}
```
Jacobian `∂h_t/∂h_{t-1}` คำนวณได้ ณ timestep t (forward เท่านั้น) ไม่ต้องรู้อนาคต

Weight update ณ timestep t:
```
ΔW_t = −η · (∂L_t/∂h_t) · P_t
```
`∂L_t/∂h_t` คือ error signal สำหรับ step นี้ ⊗ กับ influence matrix = gradient ที่ exact

**ไม่ต้องเก็บประวัติเลย** เพราะ P_t summarize ทุกอย่างที่ผ่านมา

### ทำไมถึงไม่ใช้กันทั่วไป

ขนาดของ P_t = (n hidden) × (n hidden × n hidden) = O(n³) ต่อ timestep update P_t ต้องคำนวณ Jacobian × P_{t-1} = O(n⁴) ต่อ step สำหรับ n=1000 นั่นคือ 10^12 operations ต่อ timestep ใน practice — แก้ไม่ไหว ยกเว้นตาข่ายจิ๋ว ๆ (n<100)

**สำหรับตาข่าย sparse/local:** ถ้า Jacobian sparse (นิวรอน i ขึ้นกับนิวรอนใกล้ ๆ เท่านั้น) P_t ก็ sparse ตาม และ computation ลดลงตาม connectivity — substrate ของคุณที่ sparse = RTRL แก้ไหวมากกว่า dense network อย่างชัดเจน

### สำหรับเรา

RTRL คือ *อุดมคติ* ที่ชิปคุณอยากได้ (เรียนเดี๋ยวนี้ ไปข้างหน้าอย่างเดียว ไม่มีประวัติ) รายการถัดไป (e-prop, local learning) คือตัวประมาณ RTRL ที่แก้ไหวและเป็นชีววิทยา

ข้อคิดสำคัญ: RTRL exact แต่แก้ไม่ไหว e-prop approximate แต่ O(n) และ on-chip ตัวประมาณนั้น **คุ้มค่ามาก** เพราะ approximate RTRL ยังดีกว่า BPTT สำหรับ realtime อย่างชัดเจน

---

## e-prop — กฎการเรียนรู้ realtime สำหรับตาข่าย spiking/recurrent

*Bellec, Scherr, Subramoney, Hajek, Salaj, Legenstein & Maass, Nature Communications 2020 ([paper](https://www.nature.com/articles/s41467-020-17236-y)).*

### นี่คือเปเปอร์ที่เกี่ยวข้องที่สุดอันเดียวในไฟล์นี้ อ่านละเอียด

### ปัญหา: ทำ RTRL แบบแก้ไหวและ on-chip ได้มั้ย?

Bellec et al. ถาม: ถ้า RTRL exact แต่แก้ไม่ไหว มีการประมาณที่ยังดีพอ ยังเป็น local, ยังเป็น forward-only และ implement ใน hardware ได้มั้ย?

### กลไก: แยก gradient เป็น trace × signal

RTRL gradient = `(∂L/∂h_t) · P_t` e-prop แยกสองส่วนนี้ออก:

**ส่วน 1 — Eligibility Trace `e_t` (forward, local, per-synapse):**
```
e_t^{ij} = pre_j(t) × post_i_deriv(t) + decay × e_{t-1}^{ij}
```
โดย:
- `pre_j(t)` = activity ของ pre-synaptic neuron j ณ เวลา t
- `post_i_deriv(t)` = derivative ของ activation function ของ post-synaptic neuron i
- `decay` = leakage term (คาปาซิเตอร์รั่ว!)

**Eligibility trace คือ "ความทรงจำ" per-synapse ว่า synapse นี้ทำอะไรไปในช่วงเวลาที่ผ่านมา** มันบอกว่า "pair pre-post นี้ co-active ในช่วง t-recent มากแค่ไหน?" — Hebbian trace แต่มีมิติเวลา

**ส่วน 2 — Learning Signal `L_t` (global, delayed):**
```
L_t = ∂loss/∂output_t
```
error signal จาก output — อาจมาจาก GD head, reward signal, หรือ teacher

**Weight update:**
```
ΔW_ij ∝ L_t × e_t^{ij}
```
เป็น **product สองส่วน** ที่ทั้งคู่หาได้ online:
- Trace `e_t` หาได้แบบ local และ forward — ไม่ต้องรู้อนาคต
- Learning signal `L_t` อาจ delayed (รอ output) หรือ broadcast ก็ได้ — ไม่ต้องเดินทางย้อนกลับผ่านทุก layer

### ทำไม e-prop ถึงเป็น approximate RTRL?

e-prop ตัดทิ้ง "long-range" influence ใน P_t — รักษาเฉพาะ "ผลทันทีและผลผ่าน recent history" ซึ่ง eligibility trace capture ได้ ในทางปฏิบัติสำหรับงาน biological timescale (perception, motor control) ส่วนที่ตัดไปไม่สำคัญ

### ผลที่ได้

ทดสอบบน tasks ที่ต้องการ temporal memory:
- **Evidence accumulation:** agent รับ visual input แบบ sequential ต้องจำ evidence ทั้งหมดก่อนตัดสินใจ e-prop ทำได้ใกล้ BPTT มาก แม้ว่า trace decay เร็ว
- **Pattern recognition บน speech (TIMIT):** LIF spiking network + e-prop ได้ **3.9% phone error rate** เทียบ backprop 3.7% — ต่างกันน้อยมาก แต่ e-prop เรียนรู้ online โดยไม่มี backward pass
- **Working memory tasks (NeuroGym):** เทียบเท่า BPTT บน match-to-sample, delayed comparison
- งาน motor control: เรียนรู้ได้เร็วกว่า BPTT เมื่อ environment เปลี่ยนระหว่าง task

### สำหรับเรา

**นี่คือ template ของการเรียนรู้ realtime บน substrate ของคุณ**

**Eligibility trace = capacitor รั่วต่อ synapse:**
```
e_t ≈ pre_activity × post_deriv + decay × e_{t-1}
```
คือ RC circuit ที่ charge จาก `pre × post` และ leak ผ่าน decay term ซึ่งคุณมี "momentum/eligibility register" ใน Scap อยู่แล้ว — นั่นคือ hardware trace ที่รอการตีความอยู่

**Learning signal = broadcast ของคุณ:**
ใน SCFF + GD: GD head สร้าง `∂loss/∂output` และ broadcast ไปยัง SCFF layers ข้างล่าง นั่นคือ learning signal ใน e-prop ตรง ๆ ไม่ต้อง backprop ผ่านทุกชั้น แค่ broadcast signal และให้แต่ละ synapse คูณกับ trace ของตัวเอง

**e-prop บอกว่า:** *"ร่องรอย forward แบบโลคอล × สัญญาณสอนแบบ global = การเรียนรู้ online ที่สู้ backprop ได้"* — ซึ่งแทบจะเป็น "local SCFF + การแก้ GD แบบ broadcast" ของ draft-6.0 คุณเป๊ะ มีฐานทางทฤษฎีฝั่ง realtime/temporal มาหนุนหลังแล้ว

**Timescale coupling:** e-prop มี trace decay ที่ set ว่า "จำ ​recent past นานแค่ไหน" — นั่นคือ τ ของ eligible trace ตั้งได้โดย leak resistance ของ Scap ใน analog circuit คุณสมบัตินี้ tie กับ liquid neuron ใน `8-atom.md` — ถ้า τ ของ trace = τ ของ neuron, learning และ dynamics ทำงานบน timescale เดียวกัน

ถ้าเฟส 2 ต้องเรียนบน temporal stream: **e-prop คือกฎนั้น** implement ด้วย leaky trace capacitor + global broadcast — ทั้งคู่เป็น native กับ substrate

---

## Reservoir Computing — เรียนรู้เร็วจนเป็นแค่ regression

*Echo State Networks / Liquid State Machines (ดู `8-atom.md` ด้วย).*

### ทางออกที่เรียนเร็วที่สุด: ไม่เรียนตาข่ายส่วนใหญ่เลย

ครอบคลุมในฐานะ *อะตอม* ใน `8-atom.md` แต่ประเด็นที่แตกต่างสำหรับ **realtime** คือ:

**Inference realtime:** reservoir วิวัฒน์ตาม input ทันที — ไม่มี forward pass ที่ต้องคำนวณ discrete layers คุณแค่ "ปล่อยให้วงจรรัน" และอ่าน output ณ ขณะนั้น latency = RC settling time ≈ nanoseconds ใน analog

**Learning realtime:** เทรนแค่ linear readout — ทำได้ด้วย **Recursive Least Squares (RLS)** ที่ update weight ทุก timestep:
```
ΔW_out = P_t · r_t · e_t^T
P_t = P_{t-1} − (P_{t-1} · r_t · r_t^T · P_{t-1}) / (1 + r_t^T · P_{t-1} · r_t)
```
P_t คือ estimated covariance inverse — RLS เป็น optimal online linear estimator compute ต่อ step = O(k²) ที่ k = readout size (ไม่ใช่ reservoir size)

**เหมาะมากสำหรับ substrate:** reservoir เป็น analog circuit สุ่มตายตัว (ไม่ต้อง precision) readout เป็น digital weights เล็ก ๆ ที่ update ด้วย RLS — hybrid ที่ถูกมาก

**ข้อจำกัด:** reservoir สุ่มตายตัวมี ceiling ที่แน่นอน ถ้า task ต้องการ representation ที่ specific มากกว่าที่ random dynamics ให้ได้ต้องย้ายไป trained network

---

## Liquid Networks — การอนุมาน realtime ในเวลาต่อเนื่อง

*Liquid Time-Constant Nets / CfC: Hasani, Lechner, Rus (ดู `8-atom.md` ด้วย).*

### อะตอม + realtime = คู่ที่ใช้งานได้จริง

ครอบคลุมใน `8-atom.md` แล้ว แต่ประเด็นสำหรับ realtime ที่ต้องเพิ่ม:

**Inference realtime:** liquid neuron เป็น ODE ต่อเนื่อง ดังนั้น inference *เป็น realtime โดยธรรมชาติ* — ไม่มีแนวคิด "timestep" ระบบ integrate สัญญาณขณะที่มันมาถึง ปรับ τ ตาม input dynamics อัตโนมัติ

**Closed-form Continuous-time (CfC):** แทน ODE solver ที่ต้องวนลูป CfC ให้รูปแบบปิด:
```
x(t) = σ(−f(x_0, I, θ))·x_0 + (1−σ(−f))·g(x_0, I, θ)
```
= interpolation ระหว่างสองสถานะด้วย learned sigmoidal gate รัน single forward pass ไม่ต้อง integrate ซ้ำ ๆ latency คงที่

**ทำไม CfC ถึง realtime ดีกว่า LSTM:**
- LSTM: update state ทุก discrete timestep ต้องรู้ว่า "ก้าว" คืออะไร
- CfC: integrate ข้าม interval time ใด ๆ ได้ ไม่ว่า Δt จะเท่าไหร่ — เหมาะกับ event-driven computation ที่ input มาไม่สม่ำเสมอ

**Integration กับ e-prop:** liquid atom + e-prop learning = ชิปที่รับรู้และเรียนรู้จากสตรีมสดพร้อมกัน ทั้งคู่เป็นธรรมชาติของแอนะล็อก นี่คือ full realtime stack: อะตอมที่เวลาต่อเนื่อง + กฎเรียนรู้ที่ online forward-only

---

## Spiking Neural Networks & Hardware Neuromorphic — realtime แบบขับด้วยเหตุการณ์

*ภาพรวม SNN; Intel Loihi, SpiNNaker, IBM TrueNorth.*

### ขนบฮาร์ดแวร์ที่สร้างมา *เพื่อ* realtime

SNN (Spiking Neural Networks) ไม่ใช้ floating-point activations — ใช้ **spikes** แบบ binary: neuron ยิงหรือไม่ยิง ณ เวลาที่ต่อเนื่อง

**Event-driven computation:** neuron ทำงาน **เฉพาะตอนมันยิง** ในเวลาอื่นไม่มีอะไรเกิดขึ้น ถ้าสัญญาณ sparse (สมองจริง: 1-2% spike rate) ส่วนใหญ่ของเวลา chip ไม่ทำงานเลย — กินไฟต่ำมาก

**ความแตกต่างจากดิจิทัล:** ไม่มี global clock ที่ tick ทุก cycle neuron ทำงานแบบ asynchronous ตามเหตุการณ์ที่เข้ามา latency = เวลาที่ spike ผ่านจากสัญญาณ → output ไม่ใช่ clock cycles

### Architecture ของ Loihi 2

Intel Loihi 2 (2021): neuromorphic chip ที่ state-of-the-art:
- **128 "neurocore":** แต่ละ core simulate neurons สูงสุด 256 ตัวด้วย programmable dynamics
- **On-chip learning:** รองรับ STDP (Spike-Timing Dependent Plasticity) และ variant ของ e-prop
- **Mesh interconnect:** spikes route ผ่าน 2D mesh — spike จาก core A ถึง core B ใน O(hop distance) time
- **Power:** 1-10 mW ต่อ core สำหรับ SNN ที่ทำงาน real-world tasks

**ผลที่ได้บน Loihi:**
- SLAM (robot localization): power 100× น้อยกว่า GPU equivalent
- Speech detection: 99% accuracy ที่ 140 μW — GPU equivalent ต้องการ 10 mW+
- Keyword spotting: latency < 1ms (event-driven)

SpiNNaker: architecture ที่ต่างออกไป เน้น simulate biological neuron จำนวนมาก (10^9 neurons) ใช้ ARM cores จำนวนมาก

### สำหรับเรา

นี่คือ **เพื่อนบ้านที่ใกล้ที่สุดในเจตนา** — chips เหล่านี้มีเป้าหมายเหมือนกับคุณ (analog/sparse/online/low-power) และเป็นคู่แข่งที่ต้องวางตำแหน่งเทียบ

**บทเรียนที่ต้องขโมย:**

**1. Event-driven = คำนวณเฉพาะตอนมีการเปลี่ยนแปลง:** นี่คือหลักการ realtime ที่ลึกที่สุด และมันคือคุณสมบัติ **sparse** ของ substrate คุณดันไปถึงขีดสุด ถ้า unit active แค่ 2% ของเวลา และคุณ compute แค่ตอนที่มัน active — effective compute ลดลง 50× โดยอัตโนมัติ

**2. Asynchronous timing:** ไม่มี global clock = ไม่มี synchronization overhead = latency natural จาก physics ไม่ใช่จาก clock cycle คาปาซิเตอร์ที่ settle แบบ event-driven คือ SNN ในรูปแบบ analog

**3. On-chip learning = e-prop:** ไม่ใช่เรื่องบังเอิญที่ e-prop เป็น learning rule ที่ neuromorphic hardware เลือกใช้ — มันเป็น family เดียวกับ STDP (pre-before-post = strengthen, post-before-pre = weaken) ซึ่งเป็น e-prop ที่ใช้ spike timing แทน continuous trace

**4. Positioning vs. Loihi/SpiNNaker:** substrate ของคุณใช้ capacitor weights (continuous analog) ขณะที่ neuromorphic hardware ใช้ memristor หรือ SRAM weights SNN จัดการ temporal dynamics ด้วย spike timing; คุณจัดการด้วย RC settling time นี่คือ trade-off ที่ควร articulate ในงานเขียนเฟส 1

คุณไม่จำเป็นต้องรับ spike model มาใช้ แต่ **"หน่วยไม่กินอะไรเลยจนกว่ามันจะ active"** คือหลักการ realtime/พลังงานที่ควรขโมยมาใช้

---

## State-Space Models / Mamba — การประมวลผลซีเควนซ์ที่มีประสิทธิภาพยุคใหม่

*S4: Gu et al., ICLR 2022; Mamba: Gu & Dao, 2023 ([arXiv 2312.00752](https://arxiv.org/abs/2312.00752)).*

### ปัญหา: Transformer แพงมากสำหรับซีเควนซ์ยาว

Transformer มี attention ที่ scale O(T²) ใน T = sequence length ซีเควนซ์ยาว 1000 tokens ก็แพงแล้ว 100,000 tokens แทบเป็นไปไม่ได้ ยิ่งกว่านั้น inference ต้องการ KV cache ที่ใหญ่ตาม context window

Mamba มาจากสาย State-Space Models ที่ solve ปัญหานี้

### กลไก S4 → Mamba

**S4 (Structured State Space Sequence):**

นิยาม dynamics เป็น ODE ต่อเนื่อง:
```
dx/dt = Ax + Bu(t)
y(t) = Cx + Du(t)
```
A, B, C, D เป็น matrices ที่เรียนรู้ได้ x คือ hidden state u คือ input y คือ output

Discretize ด้วยวิธี Zero-Order Hold ที่ step Δ:
```
x_k = Ā·x_{k-1} + B̄·u_k
y_k = C·x_k
```
โดย `Ā = exp(AΔ)`, `B̄ = (A)^{-1}(Ā−I)B`

ผลสำคัญ: สมการ discrete recurrence นี้มีรูปแบบ **linear recurrence** ดังนั้น:
- **Inference mode:** รัน recurrence O(1) ต่อ token — มี KV cache ขนาดคงที่ = state x เท่านั้น
- **Training mode:** unfold เป็น convolution ที่ parallelize ได้ O(T log T) — เร็วกว่า O(T²) attention มาก

**Mamba (S6):** เพิ่ม selectivity ที่ขาดไปใน S4 — ปัญหาของ S4 คือ A, B, C เป็น constant ไม่ขึ้นกับ input ทำให้ไม่สามารถ "focus" บน token ที่สำคัญได้

Mamba ทำ B, C ขึ้นกับ input:
```
B_k = Linear(u_k)    (input-dependent selection)
C_k = Linear(u_k)
```
นั่นทำให้ model เลือกได้ว่าจะ "ใส่" input ไหนเข้า state และ "อ่าน" อะไรออกจาก state — คล้าย attention แต่ recurrent ไม่ใช่ quadratic

**Hardware implementation:** Mamba ใช้ scan operation ที่ GPU efficient และเลือก state size เล็ก (16) เพื่อ fit ใน SRAM — inference ต้องการ memory O(1) ต่อ layer ไม่ว่า sequence จะยาวแค่ไหน

### ผลที่ได้

- Mamba เอาชนะ Transformer บน language modeling ที่ sequence length 1M tokens ด้วย compute และ memory น้อยกว่ามาก
- State size 16 เพียงพอสำหรับงาน language หลาย ๆ อย่าง — แสดงว่า compressed state เป็น sufficient representation
- Mamba-2 (2024): เชื่อม SSM กับ attention ผ่าน algebraic structure เหมือนกัน — ทำให้ hybrid model ง่ายขึ้น
- Bio applications: Mamba บน DNA sequences เอาชนะ transformer เพราะ sequences ยาวมาก

### สำหรับเรา

**สองเหตุผลที่ควรรู้:**

**1. แกนกลาง `dx/dt = Ax + Bu` คือวงจรแอนะล็อกเชิงเส้น:**
นั่นคือ differential equation ของ RC network ที่มี input current วงการ ML กำลัง "ค้นพบใหม่" ว่าพลวัตเชิงเส้นเวลาต่อเนื่องนั้นถูกและทรงพลัง — เป็น bet เดียวกับ substrate ของคุณ

ถ้าคุณดูงาน SSM ในภาษาของ analog circuit: S4/Mamba คือ **trainable analog filter bank** ที่ทั้งวงการ NLP กำลัง converge มาหา เพราะมันเป็น efficient ที่สุดสำหรับซีเควนซ์

**2. Inference แบบ recurrent คือ streaming ที่ native:**
Mamba inference mode: `x_k = Ā·x_{k-1} + B̄·u_k` — update state ทุก token ด้วย O(1) operations นั่นคือ **streaming processing** ที่ true realtime ไม่มี attention overhead ไม่มี KV cache ที่ grow ได้แค่ state vector คงที่

ถ้าคุณอยากได้ sequence processor ยุคใหม่ที่มีคน support ดีเพื่อ benchmark กับ analog loop ของคุณ — Mamba คือตัวนั้น เพราะมันเป็น mathematical twin ของ analog dynamics ในรูป digital

**Mamba selectivity = liquid neuron adaptive τ:** B, C ที่ขึ้นกับ input ใน Mamba ≈ τ ที่ขึ้นกับ input ใน liquid neuron (ดู `8-atom.md`) — ทั้งคู่คือ "ปรับ timescale ตาม content" แต่ Mamba ทำ digital, liquid neuron ทำ analog

---

## รูปร่างของคำตอบ (ไฟล์นี้)

realtime สำหรับเรา: **ทิ้ง BPTT ไปให้หมด** (มันต้องการอนาคตและทั้งประวัติ)

ตระกูลการเรียนรู้ realtime คือ **ร่องรอย forward แบบโลคอล × สัญญาณสอน**:
- **RTRL** = อุดมคติที่เป๊ะแต่แพง — O(n⁴) แต่ sparse/local network แก้ไหวมากกว่า
- **e-prop** = รูปแบบ on-chip ที่แก้ไหว — eligibility trace (leaky capacitor ที่คุณมีอยู่แล้ว) × learning signal (broadcast จาก GD head) = gradient online ที่ชนะ BPTT บน many tasks

อะตอม realtime: **liquid neuron** (`8-atom.md`) สำหรับ *inference* — ODE ต่อเนื่อง native กับ RC physics **CfC** สำหรับ single forward pass ไม่ต้อง integration loop

ถูกที่สุด: **reservoir** — เทรนแค่ readout ด้วย RLS online, reservoir เป็น analog spaghetti ตายตัว mismatch คือ feature

หลักการ deep จาก neuromorphic: **event-driven = หน่วยไม่กินอะไรจนกว่าจะ active** — คุณสมบัติ sparse ดันไปสุดขีด ไม่ต้องรับ spike model แค่รับหลักการ

SSM/Mamba คือข้อพิสูจน์ยุคใหม่ว่า **พลวัตเชิงเส้นต่อเนื่อง** = substrate ของคุณตรง ๆ — คือวิธีทำซีเควนซ์ที่มีประสิทธิภาพที่สุด ทั้ง ML world กำลัง converge มาหา biology

**ประโยคเดียวของทั้งไฟล์:** ชิปแอนะล็อกของคุณเป็นเครื่อง realtime อยู่แล้ว ชิ้นที่ขาดคือ *กฎการเรียนรู้* แบบ realtime และกฎนั้นคือ **e-prop** (leaky trace × broadcast signal) ซึ่งทั้งสองชิ้นมีอยู่ใน substrate ของคุณแล้ว รอแค่ตีความ
