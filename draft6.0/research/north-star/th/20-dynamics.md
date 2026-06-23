# 20 — พลวัตและเสถียรภาพ: ระบบแอนะล็อกของคุณจะ *settle* ไหม?

> ชิปคุณไม่ได้ "ประมวลผลเลเยอร์" — มันคือ **ระบบพลวัตทางกายภาพ (physical dynamical system) ที่วิวัฒน์ประจุไปตามเวลาแล้ว settle** นั่นเปลี่ยนคำถามรากฐานจาก "คณิตศาสตร์ถูกไหม?" เป็น **"พลวัตจะลู่เข้า หรือแกว่ง หรือระเบิด?"** ไฟล์นี้เดินผ่านเครื่องมือแต่ละชิ้น: Lyapunov (จะพิสูจน์การ settle อย่างไร), contraction (เงื่อนไขที่ออกแบบได้), edge of chaos (จะ tune ยังไง), และ attractors (ทำไม settling *คือ* การคำนวณ) ทั้งหมดกระจัดกระจายอยู่ใน `3`/`8`/`17`; ไฟล์นี้คือกระดูกสันหลัง

---

## การตีกรอบใหม่: ตาข่ายดิจิทัลคือฟังก์ชัน ตาข่ายแอนะล็อกคือระบบพลวัต

ก่อนจะไปถึงทฤษฎี ต้องเปลี่ยนกรอบความคิดก่อน เพราะมันเป็นหัวใจของทุกอย่างในไฟล์นี้

**ตาข่ายดิจิทัล feed-forward:** คือ *ฟังก์ชัน* อินพุตเข้า → ฟังก์ชัน → เอาต์พุต ทันที เสร็จในก้าวเดียว ไม่มีเวลา ไม่มีการเปลี่ยนแปลงระหว่างทาง

**ตาข่ายแอนะล็อกของเรา:** คือ **ระบบพลวัต** สถานะ x (ประจุบนคาปาซิเตอร์ทุกตัว ศักย์ไฟฟ้าทุกจุด) วิวัฒน์ด้วยกฎ:

$$\frac{dx}{dt} = f(x, \text{input}, \text{weights})$$

และ "คำตอบ" ไม่ใช่ผลทันที — มันคือ **จุดที่ระบบ settle** — equilibrium หรือ fixed point ที่ dx/dt ≈ 0

นี่คือมุมมองเบื้องหลัง Neural ODEs (`8`), Deep Equilibrium Models (`3`), Hopfield memory (`1`), และระบบของเราเอง

### สามโชคชะตาที่เป็นไปได้

เมื่อพลวัตรัน สามอย่างเกิดขึ้นได้:

1. **ลู่เข้า (converge / settle):** สถานะวิ่งไปยัง fixed point เดียวกันทุกครั้ง ไม่ว่าจะเริ่มจากไหน — นี่คือสิ่งที่ต้องการ output ที่มีความหมาย
2. **แกว่ง (oscillate / limit cycle):** สถานะวนซ้ำ ไม่ไป settle ที่ไหน — บางทีมีประโยชน์ (ถ้าเราต้องการ rhythmic output) แต่ส่วนมากไม่ดี
3. **ลู่ออก (diverge / explode):** สถานะระเบิดออกไปชนขอบ (voltage rail, saturation) — chip ตาย

อันไหนเกิดขึ้นถูกตัดสินโดยคณิตศาสตร์ด้านล่าง และคุณ *ออกแบบ* ให้ลู่เข้าได้ นั่นคือสาระของไฟล์นี้

---

## เสถียรภาพ Lyapunov — "ถ้าพลังงานลดเสมอ ระบบต้องลู่เข้า"

*Lyapunov, 1892; แพร่หลายในทฤษฎีการควบคุม (control theory).*

### Intuition ก่อน

ลองนึกภาพลูกบอลในชาม ถ้าชามมีด้านต่ำสุดหนึ่งจุด (bowl-shaped) และลูกบอลมีแรงเสียดทาน (energy dissipation) แล้วไม่ว่าจะปล่อยลูกบอลจากที่ไหนในชาม มันก็จะกลิ้งลงมา settle ที่ก้นชาม เสมอ ความสูง h(x) ของลูกบอล ≥ 0 และลดลงเรื่อยๆ จนถึงศูนย์ที่ก้นชาม

Lyapunov formalize intuition นี้ให้เป็น theorem ที่ใช้กับระบบทั่วไปได้

### กลไกที่แท้จริง: Lyapunov function

**Lyapunov function** V(x) คือ scalar function ที่ต้องมีคุณสมบัติ:
1. **V(x) ≥ 0** สำหรับทุก x (bounded below, ไม่ติดลบ)
2. **V(x\*) = 0** ที่ equilibrium x\* ที่ต้องการ (ศูนย์ที่ก้น)
3. **dV/dt = ∇V · f(x) < 0** ตลอดการวิวัฒน์ (ลดลงเสมอ เหมือนลูกบอลกลิ้งลง)

ถ้าหา V(x) ที่มีคุณสมบัติครบได้ ระบบ **ต้องลู่เข้าหา x\*** — proof by energy drainage คุณไม่ต้อง simulate แม้แต่ครั้งเดียว V "drains away" ไปเรื่อยๆ จนถึงศูนย์

### วงจรแอนะล็อกมี Lyapunov function ในตัวทุกตัว

นี่คือข่าวดีที่สุดสำหรับ hardware: **วงจรแอนะล็อกที่ dissipative (มี resistors, lossy elements, current sink) มีฟังก์ชัน Lyapunov ในตัว** — นั่นคือ **พลังงานไฟฟ้ารวม** ของระบบ

$$V = \sum_i \frac{1}{2} C_i V_i^2 \quad \text{(total stored charge energy)}$$

ทุกครั้งที่ระบบวิวัฒน์ พลังงานไฟฟ้านี้ **ถูกสูญสลายออกไปทาง resistance** (กลายเป็น heat) ดังนั้น dV/dt < 0 โดยกฎฟิสิกส์ ระบบแอนะล็อกที่มี dissipation ใดๆ จึง **settle เสมอ** จาก physics โดยตรง ไม่ต้องพิสูจน์เพิ่ม

### Hopfield สร้างสิ่งนี้อย่างไร

Hopfield (1982) เข้าใจ intuition นี้ และ **ออกแบบ energy function ของตาข่ายให้ชัดเจน**:

$$E = -\frac{1}{2} \sum_{ij} W_{ij} x_i x_j + \sum_i \theta_i x_i$$

เขาพิสูจน์ว่าถ้า update rule ของ neuron แต่ละตัวคือ "บวกหรือลบแบบ threshold" แล้ว E ลดลงทุก update หรือคงที่ — ไม่มีทางเพิ่มขึ้น ดังนั้น network **ต้อง settle** ที่ local minimum ของ E

การ recall ความจำ = เริ่มจาก noisy pattern → กลิ้งลงเขาตาม E → ถึง minimum ที่เป็น clean stored memory ที่ใกล้ที่สุด นั่นคือ associative memory จาก Lyapunov dynamics ล้วนๆ

**สำหรับเรา:** นี่คือวิธี *รับรอง (certify)* ว่าบล็อกแอนะล็อกจะลู่เข้า แทนที่จะสั่น (ring) ถ้า Scap circuit มี dissipation path (ซึ่งมีแน่ จาก leakage และ op-amp output resistance) ก็มี natural Lyapunov function = total charge energy ที่ลดลงเสมอ

ขั้นต่อไปคือออกแบบให้ minimum ของ E อยู่ที่ "คำตอบที่ถูกต้อง" ไม่ใช่แค่ปล่อยให้ settle ที่ไหนก็ได้ นั่นคือ role ของ weight training — SCFF/GD training = "แกะสลัก E landscape ให้ correct answers อยู่ที่ก้นหุบเขา" (`21`)

---

## ทฤษฎี Contraction — เงื่อนไขที่แข็งแกร่งและออกแบบได้

*Lohmiller & Slotine, 1998; contraction สำหรับ RNNs/Neural-ODEs: [รีวิว](https://arxiv.org/abs/2110.00207).*

### ทำไม Contraction ดีกว่าแค่ Lyapunov

Lyapunov บอกว่า "ถ้าหา V ได้ ระบบ settle" แต่การหา V ไม่ง่าย และมักต้องทำ case by case

**Contraction theory** เปลี่ยนคำถามเล็กน้อย แทนที่จะถามว่า "trajectory ไปหา x\* ไหม?" ถามว่า **"trajectory สองเส้นใดๆ ลู่เข้าหากันไหม?"**

ถ้า *ทุก* คู่ trajectory ลู่เข้าหากันแบบ exponential (ระยะห่างระหว่างสองเส้นลดลงแบบ e^{-αt}) แล้วมีผลที่ตามมาทันที:
- Equilibrium **มีเอกลักษณ์** (ไม่มีทางมี two different fixed points ถ้าทุก trajectory ลู่เข้าหากัน)
- Convergence เป็น **global exponential** (จากทุก initial condition)
- **Noise ถูกลืม** อย่างรวดเร็ว (perturbation ใดๆ จะ decay ตาม e^{-αt})
- **ไม่มี chaos** (เส้นทางที่ใกล้กันอยู่ใกล้กันตลอด ไม่แยกออก)

### เงื่อนไขที่เช็คได้และออกแบบได้

ระบบ dx/dt = f(x) หดเข้า (contracting) ถ้า **symmetric part ของ Jacobian** F_s = (J + J^T)/2 มี eigenvalues **ลบทั้งหมด** (negative definite) ทุกที่ใน state space:

$$\lambda_{\max}\left(\frac{J + J^T}{2}\right) \leq -\alpha < 0$$

สำหรับ linear system dx/dt = Ax คือแค่ A + A^T ต้อง negative definite

**ทำไมถึงออกแบบได้?** เพราะเงื่อนไขนี้เกี่ยวกับ **Jacobian ของ dynamics** ซึ่งถูก shape โดย weight matrix และ gain ของ nonlinearity สำหรับ leaky integrator ทั่วไป: dx/dt = -x/τ + Wx ระบบหดเข้าถ้า:

$$\|W\|_2 < \frac{1}{\tau}$$

(spectral norm ของ W ต้องน้อยกว่าอัตราการรั่ว) นั่นคือเงื่อนไขที่ concrete ที่ออกแบบได้โดยตรง

### เส้นด้ายเดียวที่รัดสามสิ่ง

เงื่อนไข contraction เชื่อมสิ่งที่มีอยู่แล้วในโปรเจกต์นี้เข้าด้วยกัน:

**เชื่อม spectral norm จาก `17`:** เงื่อนไข ||W||₂ < 1/τ คือ *เงื่อนไขเดียวกัน* กับ Lipschitz bound ที่จำกัดการขยาย noise ดังนั้น **constraint เดียว — spectral norm bounded — ให้สามอย่างพร้อมกัน**: เสถียรภาพ (settle) + ความทนทาน (noise ไม่ระเบิด) + generalization (flat minimum)

**เชื่อม echo state property จาก `8`/`10`:** "echo state property" ของ reservoir computing ซึ่งบอกว่า reservoir ที่ดีต้องมี "fading memory" (อินพุตเก่าถูกลืมแบบ exponential) คือ **เงื่อนไข contraction เป๊ะๆ** reservoir ที่ spectral radius < 1 หดเข้า ดังนั้น fading memory ไม่ใช่ property โดยบังเอิญ มันคือ **definition ของ contraction** ในรูปแบบ reservoir

**เชื่อม leakage ของ Scap:** Scap คาปาซิเตอร์รั่ว (leakage current) คือ dissipation term -x/τ ที่ดัน dynamics ให้หดเข้า การรั่วไม่ใช่แค่ "loss ที่ยอมรับได้" มัน **เป็น contraction mechanism** ที่การันตีว่าระบบ settle แทนที่จะแกว่งตลอดกาล

**สำหรับเรา:** ออกแบบ:
1. **เพดาน spectral norm ต่อ crossbar** (ไม่ให้ gain เกิน 1/τ_leak) → contraction รับประกัน
2. **Leakage ที่เหมาะสม** (τ ไม่เล็กเกินจนข้อมูลหายเร็วเกิน ไม่ใหญ่เกินจนรักษา noise นาน)
3. **Saturation ที่ op-amp** (nonlinearity แบบ bounded) → ป้องกัน eigenvalue ใหญ่เกินเมื่อ amplitude ใหญ่

ถ้าทำได้สามข้อนี้ contraction รับประกันได้ ไม่ต้อง simulate ทุก corner case

---

## Edge of Chaos — จุดหวานระหว่างระเบียบกับความโกลาหล

*(จาก Deep Information Propagation ของ `17`; ที่นี่คือ interpretation เชิงพลวัต)*

### Lyapunov Exponents: วัดว่าระบบหดหรือขยาย

เพื่อ "วัด" ว่าพลวัตของระบบ contracting แค่ไหน เราใช้ **Lyapunov exponents (λ)** ซึ่งคือ **อัตราการเติบโต/ลดของ perturbation เล็กๆ**:

ถ้าเริ่ม trajectory สองเส้นห่างกันนิดเดียว δ₀ หลังจากเวลา t ระยะห่างจะเป็น:

$$\delta(t) \approx \delta_0 \cdot e^{\lambda t}$$

- **λ < 0:** perturbation **หด** → ระบบลืม noise → stable, contracting
- **λ > 0:** perturbation **ขยาย** → chaos → เส้นทางที่ใกล้กันแยกออกแบบ exponential → ระบบ **ระเบิด**
- **λ = 0:** perturbation **คงที่** → อยู่บนขอบ เสถียรภาพพอดี → **edge of chaos**

### การคำนวณ Lyapunov Exponent สำหรับตาข่าย (Mean-Field Theory)

สำหรับตาข่าย feed-forward ที่มี tanh activation และ weights ที่สุ่มมาจาก Gaussian(0, σ²_w) mean-field theory ให้ recursion สำหรับ variance ของ activation ต่อชั้น:

$$q^{l+1} = \sigma_w^2 \int \left(\tanh\left(\sqrt{q^l} \cdot z\right)\right)^2 \mathcal{D}z$$

โดย Dz คือ Gaussian measure (integration เหนือ Gaussian noise) และจาก recursion นี้มี **ฟิกซ์พอยต์ q\*** ที่ variance ของ activation ไม่เปลี่ยนชั้นต่อชั้น

เสถียรภาพของฟิกซ์พอยต์นั้นบอก phase:
- ถ้า q\* **stable** (perturbation กลับมา) → **ordered phase**, λ < 0
- ถ้า q\* **unstable** (perturbation หนี) → **chaotic phase**, λ > 0
- บน **critical line** (boundary) → λ = 0 → edge of chaos

**ตัวเลข concrete:** สำหรับ tanh network edge of chaos อยู่ที่ σ²_w ≈ 1 (weight variance ≈ 1 ต่อ fan-in ประมาณ) ถ้า σ²_w > 1 → chaos; ถ้า < 1 → ordered

### ทำไม "ขอบ" คือจุดที่ดีที่สุด

ที่ edge of chaos ระบบ **expressive ที่สุดแต่ยังเสถียร**:

- **Ordered phase (λ < 0 มากๆ):** สัญญาณ "ตาย" ตามความลึก — gradient จางหาย (vanishing gradient) เรียนรู้ได้แค่ชั้นบนสุด ตาข่าย "ไม่รู้สึก" ชั้นล่าง
- **Chaotic phase (λ > 0):** สัญญาณ "ระเบิด" ตามความลึก — gradient ระเบิด ข้อมูลสองอินพุตที่ต่างกันนิดเดียวให้ผลต่างกันมาก ไม่ใช่ basis สำหรับ stable computation
- **Edge (λ = 0):** perturbation "propagate ไปตลอด" โดยไม่ fade และไม่ระเบิด → gradient signal เดินทางได้ถึงชั้นล่างสุด → เรียนรู้ได้ทุกชั้น → expressive ที่สุด

นี่คือเหตุผล deep learning work: residual connections ดัน network ไปอยู่ใกล้ edge of chaos ทำให้เทรนได้

### วิธี Tune ชิปแอนะล็อกให้อยู่ที่ขอบ

สำหรับชิปแอนะล็อก "ลูกบิด" ที่ควบคุม Lyapunov exponent คือ:

| พารามิเตอร์ | ผลกระทบ | Tune ยังไง |
|------------|---------|-----------|
| **เกนของ crossbar (||W||₂)** | สูง → chaos; ต่ำ → ordered | Spectral normalization ระหว่างเทรน |
| **อัตราการรั่วของ Scap (1/τ)** | สูง → ordered; ต่ำ → chaos | เลือกขนาด C และ leakage path |
| **เพดาน op-amp (saturation)** | ลด effective gain → push toward ordered | ออกแบบ operating point |
| **Residual skip connection** | ยก λ ขึ้นจาก ordered → ดัน toward edge | เพิ่มหรือลด skip weight |

**สำหรับเรา:** นี่คือ "physical knobs" ที่ชัดเจน ออกแบบ:
- Gain ต่อ crossbar ≈ 0.8–1.2 (อยู่ใกล้ขอบ ไม่ห่างมาก)
- Leakage rate ≈ 1/(4–8 time steps) (ลืมเร็วพอที่จะ settle แต่ไม่เร็วเกินจนสูญเสียข้อมูล)
- Skip connections เป็น structural requirement ไม่ใช่ optional (ให้อยู่ที่ขอบได้โดยไม่ต้องปรับ gain สูงเกิน)

simulation ใน draft 6.0 ควรวัด effective Lyapunov exponent ตาม depth สำหรับ architecture แต่ละแบบ เพื่อ verify ว่าอยู่ใกล้ขอบจริงๆ

---

## Attractors *คือ* การคำนวณ

*Hopfield, 1982 (`1-memory.md`); attractor dynamics.*

### Attractor และ Basin of Attraction

ในระบบพลวัตที่เสถียร **attractor** คือ set A ที่ trajectory ลู่เข้าหา และ **basin of attraction** คือ set ของ initial conditions ทั้งหมดที่ลู่เข้าหา A นั้น

ภาพง่ายๆ: landscape ของหุบเขา แต่ละหุบเขาคือ attractor basin ของ basin คือ watershed — ถ้าเริ่มในแอ่งนี้ ก็จะไหลลงสู่ก้นแอ่งนี้เสมอ

สำหรับ Hopfield network ที่เก็บ M patterns: แต่ละ pattern คือ attractor (local minimum ของ E) basin ของแต่ละ pattern คือ "บริเวณ" ที่ถ้า input อยู่ใน basin นั้น จะ recall pattern นั้น

**ขนาด basin = ความทนทานต่อ noise:** ถ้า basin กว้าง input ที่ถูก corrupt มากก็ยัง recall ได้ ถ้า basin แคบ แค่ noise นิดเดียวก็หลุด basin ไปสู่ pattern ผิด

### Hopfield Capacity: เก็บได้กี่ Pattern?

Hopfield's original (1982) ด้วย Hebbian rule: เก็บได้ประมาณ **0.14N patterns** (N คือจำนวน neurons) เกินนี้ patterns ชนกัน เกิด spurious memory (false attractors)

Modern Hopfield Networks (Ramsauer et al., 2020): ขยาย capacity เป็น **exponential ใน embedding dimension** โดยใช้ softmax-based update rule นั่นคือ attention ที่เราใช้ใน transformers — ดังนั้น **modern Hopfield = attention = dense retrieval** เป็น connection ที่ตรงมาก

**สำหรับเรา:** LUT ของ hippocampus เรา (`1`) ก็คือ Hopfield network รูปแบบหนึ่ง ขนาด capacity ของมันขึ้นกับ implementation: Hebbian → จำกัดที่ 0.14N; modern Hopfield (softmax) → exponential แต่ต้อง query ทั้งหมด (ไม่ local) ขนาด L (size ของ hippocampus LUT) จึงเป็น tradeoff ระหว่าง memory capacity กับ silicon area

### Attractor *คือ* Computation

นี่คือ insight เดิมที่ดูธรรมดาแต่ profound มาก:

**Classification:** "input อันนี้คลาสไหน?" = "input นี้ fall ใน basin ของ attractor ไหน?" ตอบโดยการ settle

**Memory recall:** "pattern นี้คืออะไร?" = "attractor ที่ใกล้ที่สุดของ input นี้คืออะไร?" ตอบโดยการ settle

**Decision making:** "ควรทำ action ไหน?" = "attractor ที่ win-take-all คืออะไร?" ตอบโดยการ settle

และเพราะการ settle คือ **การลงเขาสู่ attractor** มันจึง **ทำความสะอาด noise ฟรี** สถานะที่ถูก corrupt กลิ้งกลับลงสู่ attractor ที่สะอาดโดยอัตโนมัติ ทุก settling คือ "restoring organ" (`17` von Neumann) ในตัว

**สำหรับเรา:** นี่คือเหตุผลที่ชิปแอนะล็อกที่ settle ได้ **ไม่ใช่แค่ "ทำงานได้ทั้งที่มี noise"** มัน active ทำความสะอาด noise ทุกครั้งที่ settle landscape ที่ออกแบบดี = deep basin = ดูด noise เข้า = output ที่สะอาด

สิ่งที่ต้องออกแบบ:
1. **Basin กว้างพอ** (รองรับ noise ระดับที่คาดไว้)
2. **แต่ละ basin แยกกันชัดพอ** (ไม่มี crosstalk ระหว่าง classes)
3. **ไม่มี spurious attractors** ที่ไม่มีความหมาย (limit capacity ด้วย weight structure ที่ออกแบบ)

ข้อ 3 เป็นเหตุผลที่ SCFF training สำคัญ — training shapes landscape ให้มี attractor อยู่ที่ "ที่ถูก" ไม่ใช่ปล่อยให้ physics สร้าง attractor สุ่ม

---

## รูปร่างของคำตอบ (ไฟล์นี้)

ชิปแอนะล็อกคำนวณด้วยการ settle ดังนั้น "มันถูกไหม?" กลายเป็น **"มัน settle ไหม และ settle ที่ถูกไหม?"** — คำถามเสถียรภาพที่มีคำตอบ *ออกแบบได้*:

**Lyapunov:** ถ้าวงจร dissipative มีอยู่ (มีแน่ จาก leakage) total charge energy เป็น Lyapunov function ที่ลดเสมอ → settling **พิสูจน์ได้จาก physics** ไม่ต้อง simulate เทียบ: Hopfield สร้าง memory ด้วยการออกแบบ energy function ให้ patterns เป็น minimum

**Contraction:** spectral norm bounded + leakage → dynamics หดเข้า → equilibrium **เอกลักษณ์**, convergence **global exponential**, noise **ถูกลืม**, ไม่มี chaos Constraint spectral norm ยังให้ความทนทาน (`17`) และ generalization (`19`) — **constraint เดียว สามผลตอบแทน**

**Edge of chaos:** Lyapunov exponent ≈ 0 คือจุดหวาน — expressive ที่สุด (signal propagate ทั้ง network) แต่ยัง stable (ไม่ระเบิด) Tune ผ่าน gain ต่อ crossbar, leakage rate, และ residual skip weight ควร verify ด้วย simulation ว่า effective λ อยู่ใกล้ 0 ตาม depth

**Attractors:** basins คือ computation — classification/recall/decision ทั้งหมดคือ "settle สู่ attractor ไหน?" และทุก settling คือ noise cleaning ฟรี ขนาด basin = noise budget ที่ design ได้ จาก landscape ที่ training shapes

เส้นเชื่อมทั้งหมด: **ออกแบบพลวัตแอนะล็อกให้ contracting ใกล้ edge of chaos แล้ว settling, เสถียรภาพ, ความทนทาน, และ noise cleaning มาด้วยกันทั้งหมด** — ซึ่งคือภาพ energy-landscape ตรงตัวของ `21-energy.md`
