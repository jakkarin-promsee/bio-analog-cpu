# 21 — มุมมองพลังงาน: หลักการเดียวที่อยู่ใต้ครึ่งหนึ่งของแฟ้มนี้

> นี่คือ **บทสรุปยอดเขา (capstone)** ไม่ใช่กลไกใหม่ แต่เป็นไอเดียเดียวที่ *รวม* ไฟล์จำนวนน่าตกใจที่คุณอ่านไปแล้วเข้าด้วยกัน และมัดมันเข้ากับฟิสิกส์ของชิปคุณ หลักการ: **นิยาม "พลังงาน" แบบ scalar ที่ต่ำสำหรับ configuration ที่ดีและสูงสำหรับที่แย่ แล้วการอนุมานคือการกลิ้งลงเขา และการเรียนรู้คือการปั้นเนินใหม่** พอคุณเห็นมัน SCFF, Hopfield, equilibrium propagation, predictive coding, ความรู้สึกว่าถูก, attractor dynamics, และเสถียรภาพแอนะล็อก ล้วน *เป็นสิ่งเดียวกันที่ใส่เสื้อผ้าต่างกัน* และที่ก้นบึ้งคือหลักการ Landauer — พื้นเชิงอุณหพลศาสตร์ที่บอกว่า substrate แบบ settle-ไม่-ลบ ของคุณ เป็นเส้นทางที่ถูกที่สุดในเชิงกายภาพ

---

## กรอบคิด: Energy-Based Learning — กลไกที่แท้จริง

*Energy-Based Learning: LeCun, Chopra, Hadsell, Ranzato & Huang, 2006 ([tutorial](http://yann.lecun.com/exdb/publis/pdf/lecun-06.pdf)).*

### แนวคิดหลัก

**ฟังก์ชันพลังงาน** E(x, y) คือ scalar function ที่วัด *ความไม่เข้ากัน (incompatibility)* ระหว่าง input x และ label/output y:
- E ต่ำ → x กับ y "เข้ากัน" ดี (configuration ที่ถูกต้อง)
- E สูง → x กับ y "ขัดกัน" (configuration ที่ผิด)

มีสองปฏิบัติการบน E นี้:

**การอนุมาน (Inference):** เมื่อให้ input x หา y\* ที่ minimize E:
$$y^* = \arg\min_y E(x, y)$$
นั่นคือหา "output ที่เข้ากันที่สุดกับ input นี้" โดยการกลิ้งลงเขา

**การเรียนรู้ (Learning):** ปรับ parameters ของ E (weights) ให้:
- คู่ (x, y_correct) นั่งอยู่ใน **หุบเขาพลังงานต่ำ**
- คู่ (x, y_wrong) นั่งอยู่บน **เนินพลังงานสูง**

### วิธีเทรน EBM จริงๆ: ปัญหาและทางออก

นี่คือส่วนที่คนมักข้ามไป EBM ฟังดูง่าย แต่มีปัญหาพื้นฐาน:

เพื่อจะ "ดัน E(x, y_correct) ลง" คุณต้องรู้ว่า E(x, y_wrong) อยู่ที่ไหน และต้อง "ดันมันขึ้น" ด้วย ปัญหาคือ: **จะหา y_wrong ได้อย่างไร?**

ถ้า y คือ discrete label (เช่น class 0–9) ก็ง่าย — y_wrong คือ class อื่นๆ แต่ถ้า y คือ high-dimensional continuous (เช่น image, text, representation vector) y_wrong อยู่ทุกที่ในพื้นที่ continuous — ไม่สามารถ enumerate ได้

**วิธีดั้งเดิม: MCMC sampling**

ใช้ Markov Chain Monte Carlo (MCMC) sample จาก distribution ∝ exp(-E(x, y)) จนได้ "y ที่น่าจะเป็น" แบบ wrong ปัญหา: MCMC ช้ามาก ต้อง run หลายพัน steps ก่อน sample ดีออกมา ทำให้ EBM เทรนได้ช้ามาก

**Contrastive Divergence (Hinton 2002): ไม่ต้อง run MCMC จนจบ**

แทนที่จะรอ MCMC converge แค่รัน **K steps** (K = 1 ก็พอ) จาก data point แล้วใช้ endpoint เป็น "negative sample" approximate learning rule:

$$\Delta W \propto \mathbb{E}_{data}[\nabla_W E] - \mathbb{E}_{K-step}[\nabla_W E]$$

ใช้ได้ในทางปฏิบัติแต่ยัง approximate และ slow

**SCFF: ทางออกที่ elegant ที่สุด**

SCFF (Self-Contrastive Forward-Forward) แก้ปัญหา negative sample ด้วยวิธีที่ฉลาดมาก: **สร้าง y_wrong ด้วย data augmentation แทน MCMC**

สำหรับ pair (positive: augmented_view_1, negative: augmented_view_2 ที่ต่างกันมาก หรือ corrupted/shuffled):
- Positive: E(x, good_aug) ต่ำ
- Negative: E(x, bad_aug) สูง

เพราะ negative sample มาจาก augmentation ที่ domain-specific ไม่ต้อง sample จาก prior ที่กว้าง ไม่ต้อง MCMC เลย เทรน EBM ได้เร็ว stable และ local ในเวลาเดียวกัน

นั่นคือสาเหตุที่ SCFF ทำงานได้บน analog chip ที่ไม่มี backprop: EBM framework ต้องการแค่ forward pass เพื่อ compare E ไม่ต้อง backward pass ข้ามทั้ง network

### ข้อได้เปรียบเชิงลึก: ไม่ต้อง Normalize

โมเดลเชิงความน่าจะเป็น (เช่น softmax classifier) ต้องคำนวณ **partition function** Z = Σ_y exp(-E(x,y)) เพื่อ normalize ให้เป็น probability ปัญหาคือ Z ต้อง sum เหนือ **ทุก y ที่เป็นไปได้** ซึ่งไม่ scalable สำหรับ y ที่ continuous หรือ high-dimensional

EBM ไม่ต้อง normalize คุณต้องการแค่ **E(x, y_correct) < E(x, y_wrong)** ไม่ต้องรู้ตัวเลขสัมบูรณ์ แค่รู้ relative ก็พอ

สำหรับชิปแอนะล็อกนี้สำคัญมาก: ชิปไม่ได้คำนวณ probability มัน **กลิ้งลงเขา** ไม่จำเป็นต้อง normalize อะไรทั้งนั้น

**สำหรับเรา:** SCFF ของเราคือ EBM ที่ปลอด normalization และปลอด MCMC เทรนได้ local ด้วย forward pass เท่านั้น และ inference คือ "กลิ้งลงเขาสู่ low-energy configuration" ซึ่ง analog physics ทำให้ฟรี เพียงแค่ออกแบบ E landscape ให้ถูกต้อง (ซึ่งคือ role ของ weight training)

---

## การรวมความคิด: ทุกอย่างที่คุณอ่านมาคือการไหลลงตามพลังงาน

ตอนนี้ดูว่ากี่ไฟล์ที่ยุบรวมเข้าสู่หลักการเดียวนี้ นี่ไม่ใช่ metaphor ที่หยาบ — แต่ละอันมี E function ที่ชัดเจน และ dynamics ที่ minimize มัน:

---

### 1. SCFF goodness (`../../papers/phase1-2/scff.md`)

**E function:** E(x) = -||h(x)||²_F = ลบ norm ยกกำลังสอง ของ activation

**Training:** ดัน E ลง (goodness สูง) บน positive samples, ดัน E ขึ้น (goodness ต่ำ) บน negative samples = สร้าง landscape ที่ "good data" อยู่ที่ก้นหุบเขา

**Inference:** forward pass → ผ่านทุกชั้น → เลือก class ที่มี E ต่ำที่สุด = กลิ้งลงเขา implicit

---

### 2. Hopfield Associative Memory (`1-memory.md`)

**E function ที่ชัดเจน:**
$$E = -\frac{1}{2} \sum_{ij} W_{ij} x_i x_j + \sum_i \theta_i x_i$$

**Training:** เซ็ต W ด้วย Hebbian rule ให้ stored patterns เป็น local minima ของ E (modern Hopfield: softmax attention = differentiable retrieval)

**Inference (recall):** ให้ noisy input → update neurons ตาม rule ที่ลด E เสมอ → settle ที่ local minimum ที่ใกล้ที่สุด = pattern ที่ clean ที่สุดที่ใกล้ input

**ความจำคือ landscape ของ E** ไม่ใช่ lookup table ธรรมดา

---

### 3. Equilibrium Propagation (`3-recurrence.md`)

**E function:** total energy ของ network ทั้งหมด รวม bias และ input coupling:
$$F(s, \theta, x, y) = \frac{1}{2}\sum_i s_i^2 - \sum_{ij} W_{ij} \rho(s_i)\rho(s_j) - \sum_i b_i \rho(s_i) - \lambda C(s, y)$$

**Training:** phase หนึ่ง = settle โดย free (ไม่ clamp y) → ได้ s_free; phase สอง = settle โดย clamp y ไว้ → ได้ s_clamped กฎการเรียนรู้คือผลต่าง:
$$\Delta W \propto \frac{1}{\beta}\left[\rho(s_i^{\text{clamped}})\rho(s_j^{\text{clamped}}) - \rho(s_i^{\text{free}})\rho(s_j^{\text{free}})\right]$$

**เรียนรู้จาก local comparison ของสองสถานะ** ไม่ต้อง backprop ทั้ง network นัยยะสำคัญ: กฎ local นี้ประมาณ gradient ของ loss ได้ถ้า β เล็ก

---

### 4. Predictive Coding & Free Energy (`3-recurrence.md`, `4-signal.md`)

**E function:** total prediction error ทุกชั้น:
$$F = \sum_l \frac{1}{2}||\epsilon_l||^2 = \sum_l \frac{1}{2}||x_l - \hat{x}_l(x_{l+1})||^2$$

เมื่อ ε_l = prediction error ที่ชั้น l (ความต่างระหว่าง representation จริงกับที่ชั้นบนทำนายลงมา)

**Inference:** ทั้ง top-down predictions และ bottom-up representations ปรับตัวพร้อมกันเพื่อ minimize F total → "เห็นภาพ" คือ "เข้าใจ" คือ "prediction error = 0" คือ "F แตะก้น"

**ความรู้สึก "เข้าใจแล้ว" = พลังงาน F ถึงจุดต่ำสุด** นี่เป็น formal grounding ของ "correctness เป็น feeling" ของโปรเจกต์

---

### 5. Attractor Dynamics & Stability (`17-durability.md`, `20-dynamics.md`)

**E function:** ฟังก์ชัน Lyapunov V(x) ซึ่งสำหรับวงจรแอนะล็อกคือ total charge energy:
$$V = \sum_i \frac{1}{2}C_i V_i^2$$

**Dynamics:** dV/dt < 0 เสมอ (dissipation ทางกายภาพ) → กลิ้งลงเขาเสมอ → settle ที่ minimum

**Basin of attraction = error correction region:** ถ้า input อยู่ใน basin ของ attractor ที่ถูก ก็จะ recall ถูก แม้ถูก corrupt

**เสถียรภาพ = การไหลลงตามพลังงาน** และ training ออกแบบให้ basin อยู่ที่ถูกต้อง

---

### 6. Diffusion Models (กรณีพิเศษ: กลิ้งลงเขาถอยหลัง)

**E function:** score function s(x) = ∇_x log p(x) บอกทิศที่ไปยัง high-density region

**Generation:** เริ่มจาก noise สูง → follow score (ทิศที่ E ลด = ทิศที่ความน่าจะเป็นสูง) → ถึง clean data

**กลิ้งลงเขา *จากทิศตรงข้าม***: ไม่ใช่จาก data สู่ representation แต่จาก noise สู่ data สร้างด้วยการ minimize E

---

### สรุป: หกสิ่งคือไอเดียเดียว

| สิ่ง | E function | Training | Inference |
|------|-----------|---------|---------|
| SCFF | -goodness = -\|\|h\|\|² | ดัน E ลง/ขึ้น ด้วย augmentation | เลือก class ที่ E ต่ำสุด |
| Hopfield | -½ xᵀWx | Hebbian: patterns เป็น minima | Settle ลงสู่ minimum ที่ใกล้ |
| EqProp | Total network energy | Two-phase local comparison | Settle at free minimum |
| Predictive coding | Total prediction error | Minimize error top-down & bottom-up | Settle ที่ error = 0 |
| Lyapunov/Attractor | Charge energy / Lyapunov V | Training shapes basin locations | Fall into correct basin |
| Diffusion | -log p(x) = score | Learn score function | Walk down score landscape |

**ดังนั้น:** ชิปคุณคือ **เครื่องปั้นพลังงาน (energy-shaping machine)** Training = แกะสลัก landscape ให้ของดีอยู่ต่ำ Inference = ปล่อยฟิสิกส์กลิ้งลงเขา

ประโยคเดียวนี้คือจิตวิญญาณของสถาปัตยกรรมทั้งหมด

**สำหรับเรา:** นัยยะออกแบบที่ concrete:
- ออกแบบ E landscape โดย SCFF training ก่อน (หุบเขาหลัก)
- เสริมด้วย GD readout เพื่อ fine-tune boundary ระหว่าง basin
- Sleep consolidation (`main.ideas.v1.md`) = global reshape ของ landscape ให้ consistent ทุกครั้ง
- Hippocampus LUT = set ของ attractor ที่ explicit เก็บไว้ ไม่ต้องรวมไว้ใน weight

---

## พื้นเชิงอุณหพลศาสตร์: Landauer และทำไมแบบสมองถึงเป็นเส้นทางที่ถูก

*Landauer, 1961 ([Landauer's principle](https://en.wikipedia.org/wiki/Landauer%27s_principle)); reversible computing: Bennett, 1973; ทบทวนยุคใหม่: [Plenio & Vitelli, 2001](https://arxiv.org/abs/quant-ph/0103108).*

### ที่มา: Maxwell's Demon และ Szilard's Engine

ปี 1867 Maxwell ตั้ง thought experiment: ถ้ามี demon ตัวเล็กๆ คอยเปิดปิดประตูกั้นระหว่างสองห้อง โดย demon รู้ว่า molecule แต่ละตัวเร็วหรือช้า มันสามารถ **แยก molecule เร็วไปห้องหนึ่ง ช้าไปอีกห้อง** โดยไม่ทำงาน — ทำให้ห้องหนึ่งร้อน อีกห้องเย็น โดยไม่ใช้พลังงาน ฝ่าฝืน second law ของ thermodynamics?

ปี 1929 Szilard แก้ปริศนาบางส่วน: demon ต้อง **วัดและจดจำ** ว่า molecule แต่ละตัวเป็นอย่างไร การวัดนั้นมีต้นทุน

ปี 1961 Landauer แก้ปริศนาสมบูรณ์: ต้นทุนไม่ได้อยู่ที่การวัด มันอยู่ที่ **การลบความจำของ demon** เมื่อ demon reset memory เพื่อ measure รอบต่อไป นั่นคือที่ที่พลังงานถูกจ่าย

### Landauer's Principle: กลไกที่แท้จริง

**หลักการ Landauer:** การลบข้อมูล 1 bit อย่าง irreversible ต้องสลายความร้อนอย่างน้อย:

$$Q \geq k_B T \ln 2$$

ที่ T = อุณหภูมิ (Kelvin), k_B = Boltzmann constant = 1.38 × 10⁻²³ J/K

ที่ room temperature (300 K):

$$Q_{\min} = 1.38 \times 10^{-23} \times 300 \times \ln 2 \approx 2.87 \times 10^{-21} \text{ J} = 2.87 \text{ zJ}$$

**ทำไมถึงต้องเสียพลังงานตอนลบ?** เพราะ second law ของ thermodynamics: entropy ของ universe ต้องไม่ลด การลบ bit (จาก uncertain → certain 0) ลด entropy ของ memory 1 บิต = k_B ln2 entropy นั้นต้อง "ไปอยู่ที่ไหนสักที่" → กลายเป็น heat ที่ปล่อยออกไปสู่ environment

การ **measure** (ไม่ลบ) สามารถทำได้ฟรีในเชิงอุณหพลศาสตร์ แค่การ **erase** เท่านั้นที่มีต้นทุน

### ตัวเลขที่น่าตกใจ: ห่างจาก Landauer limit แค่ไหน?

| ระบบ | Energy ต่อ operation | เท่ากับ Landauer limit กี่เท่า |
|------|--------------------|-----------------------------|
| **Landauer limit (300K)** | 2.87 zJ (= 2.87 × 10⁻²¹ J) | 1× (ขีดจำกัด) |
| **Synapse ของสมอง** | ~1 fJ (= 10⁻¹⁵ J) | ~350,000× |
| **CPU Intel i9 (2024)** | ~1 pJ (= 10⁻¹² J) | ~350,000,000× |
| **GPU A100** | ~10 pJ | ~3,500,000,000× |
| **Analog neuromorphic (เป้าหมาย)** | ~1–10 fJ | ~350,000–3,500,000× |

สมองห่างจาก Landauer limit ประมาณ 350,000× ซึ่งดูมาก แต่ CPU ห่างกว่าถึง **1,000 เท่า** ของสมอง ดังนั้นสมองประหยัดกว่า CPU 1,000× ในสิ่งที่เทียบกันได้

### Bennett's Reversible Computing: ทำได้ฟรีถ้าไม่ลบ

ปี 1973 Bennett แสดงว่า **computing ไม่ต้องใช้พลังงานในเชิงหลักการ** ถ้าทำ reversibly — เก็บ intermediate results ทั้งหมดไว้ ไม่ลบ แล้ว "un-compute" (compute ย้อนกลับ) หลังจากได้ผลลัพธ์ ดังนั้น logical reversibility ⟺ thermodynamic reversibility ⟺ zero energy cost

แต่ในทางปฏิบัติ reversible computing ต้อง **เก็บ state ทุกขั้นตอน** ซึ่งต้องการหน่วยความจำที่เติบโต linear ตาม computation depth ไม่ scalable จึงไม่ได้ใช้กันจริงๆ

### ทำไมแบบสมองถึงเข้าใกล้ Landauer limit กว่า

นี่คือการเชื่อมกับ substrate ของเราโดยตรง ดูว่าคอมพิวเตอร์ดิจิทัลผลาญพลังงานตรงไหน:

**สาเหตุที่ 1: Digital ลบตลอดเวลา**

ทุก clock cycle ทุก register ที่ถูกเขียนทับคือการ "ลบ" ค่าเก่า ทุก cache write คือการลบ line เก่า ทุก ALU operation สร้าง output ใหม่และลบ state กลาง CPU ทั่วไป **erase หลายพัน bits ต่อ clock cycle** แม้จะทำงานง่ายๆ ทุก erase = Landauer cost

**Scap ของเราไม่เคยถูกลบหรือเขียนทับในระหว่าง inference** weight คงอยู่เป็นประจุ เปลี่ยนแค่ตอน learning update และแม้แต่ learning update ก็เป็นการ drift ค่า analog ไม่ใช่ discrete erase-and-rewrite

**สาเหตุที่ 2: Von Neumann bottleneck — เคลื่อน bits ก็เสีย Landauer**

CPU แยก memory และ computation: data ต้องเดินทางจาก RAM → Cache → Register → ALU → กลับ ทุกขั้นตอนคือ read จาก one location และ write to another ซึ่งทำลาย (erase) ค่าในที่หนึ่งและสร้างในอีกที่ การเคลื่อน bit หนึ่ง = logical erasure อย่างน้อยหนึ่งครั้ง

**Compute-in-memory ของเรา (crossbar + Scap):** ทำการคูณที่ที่ weight อยู่ ไม่มีการ "เคลื่อนย้าย weight" จาก memory ไป ALU ไม่มี von Neumann bottleneck ไม่มี erasure ที่ไม่จำเป็น

**สาเหตุที่ 3: Discrete bit-flip vs. Continuous settling**

CPU ทำงานบน discrete bits ทุก state transition คือ bit-flip จาก 0 → 1 หรือ 1 → 0 ซึ่งเป็น logically irreversible (0 อาจมาจาก 0 หรือ 1 ก็ได้) → จ่าย Landauer ทุกครั้ง

ตาข่ายแอนะล็อกที่ settle ลงสู่ equilibrium: สถานะเปลี่ยนแบบ **continuous ผ่าน gradient-like path** ไม่ใช่ discrete bit-flip จึงไม่มีการ "erasure" ของ bit ที่ชัดเจน การสูญสลาย Lyapunov energy เกิดจาก dissipation ทางกายภาพ (heat จาก resistance) ซึ่งหลีกเลี่ยงไม่ได้แต่น้อยกว่า digital erasure มาก

### ความหมายสองอย่างของ "พลังงาน" มาบรรจบกัน

ณ จุดนี้มีสองนิยามของ "พลังงาน" ในไฟล์นี้:

1. **Energy landscape สำหรับ learning/inference:** E(x, y) ที่ training แกะสลักและ inference กลิ้งลง
2. **Thermodynamic energy ที่ chip ใช้จริง:** Joules ที่ต้องจ่ายตามหลัก Landauer

สิ่งที่น่าทึ่งคือ **ทั้งสองลดพร้อมกันใน substrate ของเรา:**

- Inference ที่ **กลิ้งลงตาม E landscape** ทำโดย **settling แบบ continuous** (ไม่ใช่ discrete erasure) ดังนั้น Landauer cost ต่ำ
- Weight ที่ **คงอยู่เป็นประจุ** (resident weight) ไม่ถูก erase ระหว่าง operation → ไม่จ่าย Landauer ซ้ำๆ
- Learning ที่ **local** (SCFF) อัพเดต weight ที่ใช้แค่ local information → erasure น้อยมากต่อ update

**สำหรับเรา:** คำกล่าวอ้าง "การคำนวณแบบสมองคือเส้นทางที่ถูกในซิลิคอน" มีฐานทางฟิสิกส์จริงๆ ไม่ใช่แค่ slogan:
- ไม่ erase weights ระหว่าง inference → หลบต้นทุน Landauer หลัก
- Compute-in-memory → ไม่เคลื่อน data → ไม่มี erasure จาก von Neumann bottleneck
- Continuous settling → ไม่มี discrete bit-flip → Landauer ต่ำต่อ operation

ตัวเลข: ถ้าเป้าหมายของ chip คือ 1–10 fJ/operation เทียบกับ CPU ที่ ~1 pJ/operation = ประหยัดได้ 100–1000× นั่นคือ **order of magnitude ที่เปลี่ยน application ได้** (edge AI ที่ทำงานบน coin-cell battery แทนที่จะต้องต่อไฟ)

---

## รูปร่างของคำตอบ (ไฟล์นี้)

**หลักการเดียวรวมแฟ้มทั้งหมด: พลังงาน**

นิยาม scalar E(x, y) ที่ต่ำสำหรับ configuration ดีและสูงสำหรับที่แย่ การอนุมาน = กลิ้งลงเขา การเรียนรู้ = แกะสลักหุบเขา

**EBM ของ LeCun** ให้กรอบแม่บท: ไม่ต้อง normalize (ใช้แค่ relative E) ทำให้ chip ที่ไม่คำนวณ probability ใช้ได้ SCFF แก้ปัญหา negative sampling ด้วย augmentation ไม่ต้อง MCMC

**ผ่านเลนส์นั้น:** goodness ของ SCFF (-||h||²), Hopfield energy (-½ xᵀWx), EqProp energy, prediction error ของ predictive coding, Lyapunov function ของ analog circuit, และ score function ของ diffusion — **ล้วนเป็นสิ่งเดียวกัน** inference = ปล่อยให้ physics กลิ้งลงเขา learning = ปั้นเขาให้ถูกที่

**ใต้พลังงาน learning คือพลังงาน thermodynamic:** Landauer บอกว่าต้นทุนจริงของการคำนวณคือ **การลบและเคลื่อนบิต** ซึ่ง digital ทำตลอดเวลาในทุก clock cycle CPU ห่างจาก Landauer limit ถึง 350,000,000× สมองห่างแค่ 350,000× substrate ของเรา (resident-weight, compute-in-memory, continuous settling) เข้าใกล้ limit กว่า digital ด้วยกลไกเดียวกับสมอง

เก็บประโยคเดียวจากทั้ง 21 ไฟล์:

> **ชิปคุณคือเครื่องปั้นพลังงานที่คำนวณด้วยการไหลลงตามภูมิทัศน์ที่มันไม่เคยต้องลบ**
