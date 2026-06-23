# 12 — กำแพง ALU: ทำไมการเคลื่อนข้อมูลถึงแพงกว่าการคำนวณ

> ไฟล์นี้ตอบคำถามที่ draft-5 ตั้งไว้เรื่อง "กำแพง ALU" — ชื่อจริงคือ memory wall, กลไกเบื้องหลัง, ทำไม analog crossbar ถึงเป็นคำตอบที่ถูกต้อง, และ systolic array (TPU) คือ middle ground ที่ digital ใช้แก้ปัญหาเดียวกัน

---

## บทนำ: คำถามที่ต้องถามให้ถูก

คำถามที่ draft-5 ถาม: "ฉันจะ time-multiplex ALU ตัวเดียวข้าม 29 weights ได้ไหม เหมือน CPU ทำ?"
คำตอบ: "ได้ แต่นั่นคือทางที่แพงที่สุด"

คำถามที่ถูกกว่า: "ทำไมการเคลื่อนข้อมูลถึงแพงกว่าการคำนวณ และ substrate ของฉันหลีกเลี่ยงมันได้อย่างไร?"

ไฟล์นี้ตอบตั้งแต่ต้นเหตุ (memory wall) → วิธีแก้ทางทฤษฎี (spatial vs temporal) → วิธีที่ hardware แต่ละชนิดแก้ (crossbar, systolic, CIM) → ความหมายกับ architecture ของคุณ

---

## บทที่ 1: Memory Wall — เมื่อ CPU เร็วขึ้น แต่ RAM ไม่ตาม

### เรื่องราว

ปี 1994: Wulf & McKee ตีพิมพ์ "Hitting the Memory Wall" ใน ACM SIGARCH Computer Architecture News ชื่อกลายเป็นศัพท์ที่วงการใช้มาถึงวันนี้

ปัญหาที่พวกเขาพบ:

CPU speed เพิ่มตาม Moore's Law ≈ **60% ต่อปี**
DRAM bandwidth เพิ่ม ≈ **10% ต่อปี**

ตัวเลขที่ตาม:
```
ปี 1980: CPU multiply ≈ 10 ns.    DRAM access ≈ 100 ns  → ต่าง 10×
ปี 1990: CPU multiply ≈ 1 ns.     DRAM access ≈ 70 ns   → ต่าง 70×
ปี 2000: CPU multiply ≈ 0.5 ns.   DRAM access ≈ 60 ns   → ต่าง 120×
ปี 2010: CPU multiply ≈ 0.3 ns.   DRAM access ≈ 50 ns   → ต่าง 167×
ปี 2020: CPU multiply ≈ 0.1 ns.   DRAM access ≈ 100 ns  → ต่าง 1000×
```

Gap แย่ลงทุกปี CPU เร็วขึ้นเรื่อยๆ แต่ DRAM "วิ่งตามไม่ทัน" จากต่าง 10× กลายเป็น 1000× ในสี่สิบปี

**พลังงานที่แย่กว่า latency:**
```
1 multiply-accumulate (32-bit) ≈ 0.075 pJ  (in ALU registers)
1 L1 cache access (32KB, on-die): ≈ 1 pJ
1 L2 cache access (256KB, on-die): ≈ 5 pJ
1 L3 cache access (8MB, on-die): ≈ 20 pJ
1 DRAM access (off-chip): ≈ 200 pJ

DRAM:MAC ratio = 200/0.075 = 2,667×  —  เคลื่อนข้อมูลแพงกว่าคำนวณ 2,667 เท่า
```

(ตัวเลขจาก Horowitz 2014, "Computing's Energy Problem", ISSCC)

### ทำไม Neural Network ถึงโดนหนักที่สุด

Neural network inference = multiply-accumulate กับ weight matrix ทุก layer สำหรับ model ขนาดกลาง:

```
ResNet-50: 25M parameters × 4 bytes (FP32) = 100 MB weights
ถ้า weights ไม่ fit ใน cache → ต้อง fetch จาก DRAM ทุก inference

Energy estimate (batch=1):
  Computation: 4G MACs × 0.075 pJ = 0.3 J
  Weight loading: 100 MB × 200 pJ/byte = 20 J
  
  Weight loading > computation 67 เท่า
```

ที่ batch=1 (real-time inference) cache ช่วยได้น้อย เพราะ model ใหญ่กว่า L3 cache เกือบทุกตัว weights ต้องมาจาก DRAM

**GPT-2 (1.5B params) — ตัวอย่างที่น่ากลัว:**
```
Parameters: 1.5B × 2 bytes (FP16) = 3 GB
DRAM energy ต่อ inference: 3G bytes × 200 pJ = 600 J   !!!
Computation energy: 3B MACs × 0.075 pJ = 0.225 J

DRAM/Compute ratio = 2,667:1
```

พลังงาน 99.96% ไปกับการ fetch weights จาก DRAM ไม่ใช่ไปกับการ compute จริงๆ

### สำหรับเรา

นี่คือ **เหตุผลทั้งหมดของโปรเจกต์คุณ** พูดด้วยถ้อยคำของวงการเอง:

**Compute-in-memory** คือคำตอบตามตำรา: ถ้า weight ไม่เคยออกจากชิป คุณไม่เคยจ่าย DRAM energy เลย

คาปาซิเตอร์ของคุณ (Scap) **เป็น** weight — ไม่ใช่ "เก็บ weight" แต่ **คือ** weight ตัวมันเอง เวลา forward pass ไม่มีการ load weight จากที่ไหน ไม่มี DRAM access ไม่มี cache miss ฟิสิกส์ทำการคูณโดยตรง ณ ที่ที่ weight อยู่

Energy budget ที่เปลี่ยนไป:
```
Digital CIM: ยัง access SRAM (เล็กกว่า DRAM แต่ยังต้อง move)
Analog crossbar: ไม่มี move เลย — voltage เข้า, current ออก, ทุก weight active ตลอด
Energy: O(n+m) สำหรับ activate inputs และ read outputs ไม่ใช่ O(n×m) ของ DRAM fetches
```

---

## บทที่ 2: Roofline Model — แผนที่ของ hardware performance

### เรื่องราว

Williams, Waterman, Patterson (UC Berkeley, 2009) สร้าง "Roofline model" ซึ่งกลายเป็น standard tool สำหรับ understand และ analyze hardware performance

แนวคิด: ทุก computation บน hardware ถูก bound โดยหนึ่งในสอง หรือทั้งสอง:
1. **Compute-bound**: มี arithmetic เยอะกว่า bandwidth ที่จะ feed ให้มัน (เหมือนช่างฝีมือรอวัตถุดิบ)
2. **Memory-bound**: ต้องรอ data จาก memory มากกว่าที่ compute units จะ process ได้ (เหมือนโรงงานมี machine เยอะแต่วัตถุดิบมาช้า)

**Arithmetic Intensity (AI) = FLOPs ÷ Bytes transferred**

วัดว่า computation "หนักแค่ไหน" เทียบกับ data ที่ต้องเคลื่อน:
- AI ต่ำ = ทำ arithmetic น้อย ต่อ byte ที่ load → memory-bound
- AI สูง = ทำ arithmetic เยอะ ต่อ byte ที่ load → compute-bound

```
Performance (GFLOPS)
         ↑
         |       ████ Compute ceiling (เส้นแบน)
         |   ████
         | ██          ← Memory bandwidth slope: AI × BW
         |█
         +------------------------→ Arithmetic Intensity (FLOP/byte)
         0   low       high
```

**ตัวอย่าง Arithmetic Intensity:**

Matrix-Matrix multiply (M×K) × (K×N):
```
FLOPs = 2×M×K×N
Bytes loaded = (M×K + K×N) × element_size
AI = 2×M×K×N / [(M×K + K×N) × 4]
   ≈ N/2  สำหรับ M=K=N (ใหญ่ขึ้น → memory reuse ดีขึ้น)
```
ที่ N=1024: AI ≈ 512 → compute-bound บน hardware ส่วนใหญ่

Element-wise operation (เช่น activation function):
```
FLOPs = M×N (1 op ต่อ element)
Bytes = M×N × 4
AI = 1/4 = 0.25 → memory-bound เสมอ
```

Neural network layer (batch=1, inference):
```
Linear layer: M=1 (batch), K=1024 (input), N=1024 (output)
FLOPs = 2 × 1 × 1024 × 1024 = 2M
Bytes = (1×1024 + 1024×1024 + 1×1024) × 4 ≈ 4 MB  (dominated by weight matrix)
AI = 2M / 4M = 0.5 → memory-bound อย่างรุนแรง
```

งาน ML inference ส่วนใหญ่อยู่ฝั่งซ้าย (memory-bound) โดยเฉพาะที่ batch=1

### สำหรับเรา

Analog crossbar อยู่ฝั่งขวา (compute-ceiling) เพราะ:
- Data "arrives" เป็น voltage บน row lines → O(n) energy เพื่อ charge
- Computation เกิด "ในทันที" ผ่าน Ohm's law (current = V×G) → 0 compute energy เพิ่มเติม
- Settle time เป็น function ของ RC time constant ไม่ใช่ของจำนวน operations

AI ของ crossbar = ∞ ในแง่ arithmetic เพราะ "arithmetic" ไม่ใช่ digital gate switching แต่คือฟิสิกส์ที่เกิดอยู่แล้ว คุณสร้าง hardware ที่ทำ dense matrix operation แต่จ่ายแค่ O(n+m) ในการ activate

---

## บทที่ 3: Spatial vs Temporal Dataflow — แผนที่ของการตัดสินใจออกแบบ

### กรอบคิด: trade-off พื้นฐาน

ทุก accelerator ตอบคำถามเดียวกัน: "จะทำ MAC operation กี่ตัวพร้อมกัน?"

**Temporal extreme: ALU เดียว ทำทีละ 1 MAC**
```
Hardware: 1 multiplier + 1 adder
Latency: N MACs × 1 cycle ต่อ MAC = N cycles
Area: ถูกมาก (2 units)
นี่คือ CPU
```

**Spatial extreme: 1 MAC unit ต่อ weight ทุกตัว ทำพร้อมกันหมด**
```
Hardware: N multipliers ขนานกัน
Latency: 1 cycle (parallel execution)
Area: แพงมาก (N units)
นี่คือ analog crossbar ของคุณ (ถ้า "unit" = passive device)
```

**Middle grounds:**
- Processor array (P units): N/P cycles
- Systolic array: จัดให้ data flow ผ่านอย่าง efficient (TPU)
- Blocked spatial: tile matrix ให้พอ fit ใน hardware แล้ว process ทีละ tile

### ทำไม Analog เหมาะกับ Spatial Extreme

ใน **digital**: 1 multiplier (32-bit FP) ≈ 1000-3000 transistors ขึ้นกับ design
สำหรับ N=1000 weights: ต้องการ 1,000,000-3,000,000 transistors แค่สำหรับ compute

ใน **analog**: "multiplier" คือ conductance device (resistor, capacitor, memristor) = 1 passive component
สำหรับ N=1000 weights: ต้องการ 1,000 passive components

**Area efficiency ของ passive devices ดีกว่า active circuits ~1000-10000× บน same process node**

ดังนั้น spatial extreme ที่ไม่ practical บน digital (area ใหญ่เกินไป) กลาย practical บน analog — คุณ afford ได้ที่จะมี 1 "multiplier" ต่อ weight ทุกตัว เพราะ "multiplier" ถูกมาก

**Trade-off ที่เหลือ:**
- Spatial: Area proportional to weight count, settle time = RC constant (ดี)
- Temporal: Area ถูก แต่ latency = N × settle time (แย่)

สำหรับ analog substrate ที่ settle time ≈ RC ≈ ns-µs ขึ้นกับ design: ต้องการ 1000 settle cycles = 1000 µs = 1 ms — ช้าเกินไปสำหรับ real-time use ดังนั้น spatial (1 settle time ต่อ layer) คือ path ที่ถูกต้องอย่างชัดเจน

### สี่โซนของ Design Space

```
                Spatial ← → Temporal
    ─────────────────────────────────────────
Dense  |  Analog crossbar     CPU (ALU 1 unit)
       |  (ของคุณ)            (general purpose)
       |
Block  |  Systolic array      Tiled matmul
Local  |  (TPU)               (GPU streaming)
       |
Sparse |  MoE crossbar        Sparse CPU
       |  (Ganglion routing)  (branch prediction)
    ─────────────────────────────────────────
```

คุณอยู่ที่ spatial-dense (full unrolling) ซึ่งดีที่สุดสำหรับ analog แต่ต้องคุม crossbar size ด้วย block-local grouping (ไฟล์ 11) เพื่อให้ area manageable

---

## บทที่ 4: Analog Crossbar MVM — ฟิสิกส์ที่ทำ Matrix-Vector Multiply ใน 1 ก้าว

### เรื่องราว

Crossbar computing สำหรับ neural networks ถูก propose อย่างจริงจังหลัง memristor ถูก fabricate ได้จริงโดย HP Labs (2008) แม้ว่าแนวคิดพื้นฐาน (analog MVM ผ่าน resistive network) มีมาตั้งแต่ยุค 1960s แต่การ apply กับ ML กลายเป็นงานใหญ่ช่วงปี 2015-ปัจจุบัน

papers สำคัญ:
- Prezioso et al. (2015) "Training and operation of an integrated neuromorphic network" — Nature, memristor crossbar ตัวแรกที่ train network ได้
- Shafiee et al. (2016) "ISAAC: A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars" — ISCA, proof of concept สำหรับ CNN
- Liu et al. (2020) "RRAM-based analog compute-in-memory" — สำรวจ non-idealities จริงๆ

### กลไกที่แท้จริง — ฟิสิกส์ทีละขั้ว

**Setup:**
จัด weights เป็น conductances บนกริด N rows × M columns แต่ละ cell (i,j) มี conductance G_ij ซึ่ง represent weight W_ij (positive หรือ negative ขึ้นกับ encoding)

**Inference (1 forward pass):**

ขั้นที่ 1: ใส่ input voltages:
```
V_i = x_i    สำหรับ row i = 0..N-1
(ทุก row ได้ voltage พร้อมกัน ขนาน)
```

ขั้นที่ 2: Ohm's Law ทำงานทุก cell พร้อมกัน:
```
I_ij = V_i × G_ij = x_i × W_ij     (current ที่ cell i,j)
```
นี่คือ multiplication — เกิดตามธรรมชาติ ฟรีทาง computation

ขั้นที่ 3: Kirchhoff's Current Law รวม column:
```
I_j = Σᵢ I_ij = Σᵢ (x_i × W_ij)     (current รวมที่ column j)
```
นี่คือ accumulation (summation) — เกิดตามธรรมชาติจาก KCL ไม่ต้องมี adder

ขั้นที่ 4: Read output:
```
y_j ∝ I_j = Σᵢ x_i × W_ij     (dot product ของ x กับ column j ของ W)
```

**ผลลัพธ์: Matrix-Vector Multiply y = Wx ทั้งหมด เกิดใน 1 settle time**

### ตัวอย่างรูปธรรม — 3×3 crossbar

```
W = [W₀₀ W₀₁ W₀₂]   G matrix ที่ correspond:
    [W₁₀ W₁₁ W₁₂]   G_ij = |W_ij| (magnitude เก็บเป็น conductance)
    [W₂₀ W₂₁ W₂₂]   sign เก็บแยก (SRAM bit per cell)

Input x = [2, 1, 3]  → V = [2V, 1V, 3V] บน rows 0, 1, 2

Column 0:
  I₀₀ = 2 × G₀₀ = 2 × W₀₀
  I₁₀ = 1 × G₁₀ = 1 × W₁₀
  I₂₀ = 3 × G₂₀ = 3 × W₂₀
  I_col0 = I₀₀ + I₁₀ + I₂₀ = 2W₀₀ + W₁₀ + 3W₂₀ = (Wx)₀  ✓

Column 1 และ 2: คำนวณพร้อมกันในทำนองเดียวกัน

ทั้ง MVM เกิดใน ~1 settle time (≈ RC time constant of the crossbar)
```

### Signed Weights — วิธีจัดการ

Conductance ≥ 0 เสมอ (physical constraint) แต่ weights มีได้ทั้ง + และ -

**วิธี 1: Differential pair** (วิธีที่ clean ที่สุด, draft-5 §15 ของคุณ):
```
แต่ละ weight W_ij ถูก implement ด้วย 2 conductances:
  G⁺_ij = max(W_ij, 0)   (positive part)
  G⁻_ij = max(-W_ij, 0)  (negative part)

Column j มี 2 output currents:
  I⁺_j = Σᵢ xᵢ × G⁺_ij   (positive contribution)
  I⁻_j = Σᵢ xᵢ × G⁻_ij   (negative contribution)

Output: y_j = I⁺_j - I⁻_j   (ทำด้วย op-amp subtractor)
```

ต้นทุน: crossbar ใหญ่ขึ้น 2× (M columns กลายเป็น 2M) แต่ sign ถูก handle อย่างถูกต้อง

**วิธี 2: Sign bit ใน SRAM + magnitude ใน conductance:**
```
SRAM bit: sign(W_ij) = {0, 1}
Conductance: G_ij = |W_ij|

ตอน read: ใช้ SRAM bit เพื่อตัดสินว่าจะ add หรือ subtract current ที่ column
```
ต้นทุน: digital logic เพิ่มที่ output แต่ crossbar ขนาดเท่าเดิม

### Non-Idealities ที่ต้องรู้

**IR Drop (Voltage drop on wires):**
```
สาย (wire) บน crossbar มี resistance R_wire ≠ 0
Voltage ที่ cell (i,j) ≠ V_i ที่ input
Error = V_i - (actual voltage at cell) = I × R_wire

ยิ่ง crossbar ใหญ่ ยิ่งมี R_wire รวมมาก ยิ่ง error มาก
Rule of thumb: crossbar size ≤ 128×128 สำหรับ IR drop acceptable
(ขึ้นกับ process และ target precision)
```

**Device Variation (σ_G/G):**
```
conductance เป้าหมาย: G_target = W_ij
conductance จริง: G_actual = G_target × (1 + ε)  โดย ε ~ N(0, σ²)

σ สำหรับ RRAM: ~5-20%
σ สำหรับ PCM: ~10-30%
σ สำหรับ Flash: ~1-5%
σ สำหรับ capacitor (ของคุณ): ขึ้นกับ process, typically ~1-5%
```

**Sneak Paths (passive crossbar เท่านั้น):**
```
ใน passive crossbar: current อาจไหลผ่าน path ที่ไม่ต้องการ
เช่น: current ใน row 0 อาจไหล → cell(0,1) → row 1 → cell(1,1) แทนที่จะลงตรง

วิธีแก้: ใส่ selector device (transistor, diode) ต่อ series กับแต่ละ cell
  → Active crossbar: 1T1R (1 transistor + 1 resistor) ต่อ cell
  → ขจัด sneak paths แต่ area ใหญ่ขึ้น
```

**Limited Bit Precision:**
```
Analog compute inherently noisy → precision จำกัด
RRAM ทั่วไป: 4-6 bits effective precision
Flash in-memory: 4-8 bits
Capacitor (yours): ขึ้นกับ charge retention และ sense amp resolution

วิธีแก้:
  1. Bit-slicing: represent weight เป็น k-bit chunks, compute แยก, ผสมด้วย digital shift-add
  2. Noise-aware training: train model ให้ robust ต่อ quantization noise
  3. Larger caps: เพิ่ม C ลด kT/C noise แต่ area ใหญ่ขึ้น
```

### สำหรับเรา

Ganglion ของคุณ = crossbar tile หนึ่ง:
- Scap cell = conductance G_ij ใน crossbar
- Input voltage = charge level บน input lines
- Settle time = RC time constant ของ crossbar circuit
- Output current = settled charge บน output column capacitors

Key design decisions ที่ crossbar physics บอก:

1. **Crossbar ต่อ Ganglion ต้องเล็ก** — IR drop และ device variation สำคัญขึ้นตาม size² จัดการ crossbar ≤ 64×64 หรือ 128×128 ต่อ tile ก่อนแล้วค่อย tile หลาย Ganglion

2. **Train with noise ตั้งแต่ต้น** — device variation ≈ noise injection ซึ่งเท่ากับ regularization ฟรี (ดู 18-analog-noise.md)

3. **Sign handling ต้องตัดสินใจก่อน** — differential pair (2× area) vs SRAM sign bit (2× logic) ทั้งคู่ work แต่ commit ก่อนออกแบบ crossbar

---

## บทที่ 5: Systolic Array — Digital Middle Ground ที่พิสูจน์แล้ว

### เรื่องราว

Kung & Leiserson (1978, MIT) propose "systolic arrays" ใน ACM Computing Surveys บทความที่ influential มาก ชื่อ "systolic" มาจาก systole (หัวใจสูบ) เพราะ data "ถูกสูบ" ผ่าน array เป็นจังหวะ เหมือน pipeline

แนวคิดหลัก: แทนที่จะมีหน่วยคำนวณตัวเดียวที่ต้อง fetch/store ทุก operand จาก central memory ให้มีกริดของ processing elements (PE) ที่ data **ไหลผ่าน** แต่ละ PE ทำ MAC หนึ่งครั้งแล้ว **pass result ไปเพื่อนบ้าน** ข้อมูลเดียวกันผ่านหลาย PE ทำให้ reuse สูง

Google เอาแนวคิดนี้มาสร้าง **TPU v1** (2017) ซึ่งเป็น production chip ตัวแรกที่ใช้ systolic array สำหรับ deep learning

### กลไกที่แท้จริง — TPU Systolic Array

**TPU v1 architecture:**
- Systolic array: **256 × 256** PE = 65,536 processing elements
- แต่ละ PE: multiply-accumulate unit (8-bit integer)
- Weight memory: **28 MB on-chip SRAM** ("Weight FIFO") ป้อน weights เข้า array
- Unified buffer: **24 MB** เก็บ activations ระหว่าง layers

**Weight-Stationary Dataflow** (dataflow ที่ TPU v1 ใช้):

Weights ถูก pre-loaded เข้า PE แต่ละตัวและ **ไม่เคลื่อน** ตลอด computation ของ matrix multiply นั้น

Input activations ถูก "pump" เข้า array จากทางซ้าย ไหลไปทางขวาทีละ cycle:

```
เวลา t=0:
  [a₀] → [PE₀₀] [PE₀₁] [PE₀₂] ...
           ↓       ↓       ↓
          [PE₁₀] [PE₁₁] [PE₁₂]
           ↓       ↓       ↓
          [PE₂₀] [PE₂₁] [PE₂₂]

เวลา t=1:
  [a₁] → [PE₀₀]   [a₀] → [PE₀₁]   ...
          ↓                ↓
         [PE₁₀]           [PE₁₁]

เวลา t=2:
  [a₂] → [PE₀₀]   [a₁] → [PE₀₁]   [a₀] → [PE₀₂]  ...
```

แต่ละ PE ทำ: `partial_sum += input × weight` แล้วส่ง partial_sum ลงด้านล่าง และ input ไปทางขวา

หลัง N+M-1 cycles: partial sums ออกจากด้านล่าง ครบทุก row ของ output matrix

**ตัวอย่างเล็กๆ: 3×3 multiply 3×1:**

```
W = [[W₀₀, W₀₁, W₀₂],
     [W₁₀, W₁₁, W₁₂],
     [W₂₀, W₂₁, W₂₂]]

x = [x₀, x₁, x₂]

ต้องการ: y = W × x

t=0: x₀ เข้า row 0   y₀ += W₀₀×x₀
t=1: x₁ เข้า row 0   y₀ += W₀₁×x₁,  y₁ += W₁₀×x₀
t=2: x₂ เข้า row 0   y₀ += W₀₂×x₂,  y₁ += W₁₁×x₁,  y₂ += W₂₀×x₀
t=3:                                   y₁ += W₁₂×x₂,  y₂ += W₂₁×x₁
t=4:                                                    y₂ += W₂₂×x₂

ผล: y = [y₀, y₁, y₂] = W×x  ✓ ใน 5 cycles (แทน 9×1 = 9 ถ้าทำทีละ MAC)
```

สำหรับ 256×256 array: throughput ≈ 256² × 2 = 131,072 MACs ต่อ cycle

**ตัวเลขจริงของ TPU v1 (2017):**
```
Peak throughput: 92 TOPS (tera-operations/sec)
Power: 40 W
Efficiency: 2.3 TOPS/W

เทียบกับ K80 GPU (2014):
  Peak: 8.7 TFLOPS
  Power: 300 W
  Efficiency: 0.029 TFLOPS/W

TPU/GPU efficiency ratio: 2.3/0.029 = 79× ดีกว่า
```

(แต่ TPU ทำ INT8 ไม่ใช่ FP32 ต้องระวังเปรียบเทียบ)

### ความแตกต่างกับ Crossbar ของคุณ

| Aspect | TPU Systolic | Analog Crossbar |
|---|---|---|
| Compute unit | Digital 8-bit MAC | Passive device (R/C) |
| Weight storage | SRAM ใน PE (แยกจาก compute) | Capacitor = compute unit ตัวเอง |
| Data movement | Inputs flow through array | All inputs applied simultaneously |
| Parallelism | 256×256 simultaneous MACs | N×M simultaneous MACs (per crossbar) |
| Latency | 256+N cycles | 1 settle time |
| Precision | INT8 (exact) | Analog (~4-8 bits effective) |
| Update (learning) | Reload weight SRAM | Charge/discharge Scap |

Key insight: TPU **moves activations** ผ่าน stationary weights (data ไหล, weights นิ่ง) ส่วน crossbar ของคุณ **ทุก activation applied พร้อมกัน** ไม่มีการ pipeline การ parallelize ของ crossbar จึง more extreme กว่า TPU: 1 settle time vs N+M-1 cycles

อย่างไรก็ตาม TPU ขยาย (tile) ได้ง่ายกว่าเพราะ digital: แค่ increase clock หรือ tile หลาย arrays ส่วน analog crossbar มี limit ที่ IR drop และ sneak paths

### Tiling สำหรับ Crossbar ใหญ่

ถ้าต้องการ matrix 1024×1024 แต่ crossbar ใหญ่สุดที่ build ได้คือ 128×128:

**Block tiling:**
```
แบ่ง W (1024×1024) เป็น 64 blocks ขนาด 128×128
Output y_j = Σ_blocks W_block × x_partial

จัดการ:
  1. Stream x in 8 chunks (128 elements ต่อ chunk)
  2. แต่ละ chunk ผ่าน 8 crossbar tiles ใน row
  3. Sum partial results → y

Latency: 8 × 1 settle = 8 settle times (vs 1 สำหรับ full crossbar)
Area: 64 × (128×128) = 1024×1024 cells (เหมือนกัน แต่ fabricable)
```

นี่คือ systolic-style สำหรับ analog: stream activations ผ่าน crossbar tiles เล็กๆ ซึ่งเข้ากันกับ Ganglion block architecture ของคุณตามธรรมชาติ — **แต่ละ Ganglion tile ทำส่วนของตัวเอง แล้วรวม**

---

## บทที่ 6: Compute-in-Memory (CIM) — สาขาที่คุณเป็นส่วนหนึ่ง

### ภาพรวมสาขา

หลังปี 2018 papers เรื่อง CIM/PIM (Processing-in-Memory / Compute-in-Memory) เพิ่มขึ้นอย่างรวดเร็วจากทั้ง academia และ industry:

**Industry players:**
- Samsung: in-DRAM PIM (HBM-PIM), ใช้ Samsung HBM2 ที่มี logic layer
- SK Hynix: AiM (Acceleration in Memory), DDR PIM
- Intel: in-SRAM CIM สำหรับ AI accelerators
- IBM: Phase-change memory (PCM) CIM
- Mythic: Analog flash memory CIM (startup, เจาะ edge AI)

**Academia leaders:**
- Stanford (Prof. Wong, Prof. Sze): crossbar CIM theory + non-ideal modeling
- MIT (Prof. Song Han): hardware-aware model compression สำหรับ CIM
- UC Berkeley (Prof. Shao): CIM architecture optimization
- IMEC (Belgium): analog CIM in standard CMOS process

### CIM Spectrum

```
Digital CIM ←─────────────────────────────→ Analog CIM

[SRAM near-   [DRAM logic   [In-cache    [Flash     [RRAM/PCM    [Capacitor
 memory       layer]        compute]     CIM]       crossbar]    crossbar]
 compute]                                                         (คุณ)

เพิ่ม noise  →
เพิ่ม efficiency →
ลด precision →
```

**Digital CIM** (เช่น SRAM near-memory):
- Logic อยู่ติดกับ SRAM ลด movement
- ยังคง exact digital precision
- Efficiency gain: 2-5× เทียบกับ standard SRAM+CPU

**Analog CIM** (เช่น resistive crossbar):
- Computation ใน analog domain
- Non-ideal แต่ efficiency gain: 10-100×
- ต้องการ noise-aware design/training

### Papers ที่สำคัญมาก

**ISAAC (2016)** — Shafiee et al., ISCA
ชื่อ: "A Convolutional Neural Network Accelerator with In-Situ Analog Arithmetic in Crossbars"
- Proof of concept สำหรับ crossbar-based CNN inference
- ใช้ memristor crossbars สำหรับ weight storage + MVM
- พบว่า: bit-slicing จำเป็น (memristor precision ไม่พอ)
- Energy: ~5× ดีกว่า GPU สำหรับ CNN inference

**Mythic M1076 (2020)** — commercial chip
- 76M parameters บน analog flash (NAND flash cell เป็น weight)
- 25 TOPS/W (เทียบกับ GPU ที่ ~1-2 TOPS/W)
- ใช้ใน edge AI (audio processing, keyword detection)
- แสดงว่า analog CIM เป็น viable commercial product

**PRIME (2016)** — Chi et al., ISCA
- ReRAM เป็นทั้ง main memory (normal mode) และ compute-in-memory (NN mode)
- "dual-mode" ReRAM: ใช้ memory array ทั่วไปสำหรับ CIM ด้วย
- Key finding: bandwidth ระหว่าง layers เป็น bottleneck ถ้า crossbar เล็กเกินไป

### Pattern ที่ซ้ำกันทุก Paper

Paper ทุกชิ้นในสาขานี้เจอปัญหาเดิม 4 ข้อ:

**1. Peripheral circuit overhead:**
ADC ที่ output ของ crossbar (แปลง analog current → digital bits) กิน area และ power มากกว่า crossbar เองในหลาย design ที่ไม่ระวัง

Rule of thumb: ADC resolution ต้องการ ≈ 2^N cells สำหรับ N-bit precision — ที่ crossbar ขนาด 128×128 = 16,384 cells ถ้าต้องการ 8-bit output ต้องมี ADC ที่ 256 levels → ADC power ≈ 30-50% ของ total chip power

วิธีแก้: ลด precision requirement (4-6 bits พอสำหรับหลาย tasks), ใช้ current-mirror output แทน ADC เต็มตัว, หรือ compute ใน current domain ตลอดโดยไม่ convert กลาง

**2. Non-idealities require calibration:**
Device variation ทำให้ต้อง measure จริงหลัง fabrication แล้ว adjust weights ด้วย (post-fabrication calibration) หรือ train model ที่ robust ต่อ variation ตั้งแต่ต้น (noise-aware training)

**3. Limited precision needs workarounds:**
- Bit-slicing: represent 8-bit weight เป็น 2 × 4-bit chunks, compute แยก, ผสมด้วย digital shift: 2× area แต่ 2× precision
- Multi-level cell: ถ้า device support 4 levels (2 bits) แทน 2 levels (1 bit): 0.5× area แต่ device harder to program

**4. On-chip learning ยังเป็น open problem:**
ส่วนใหญ่ focus บน inference เท่านั้น เพราะ learning ต้องการ:
- Gradient computation → ต้องการ precision สูงกว่า inference
- Weight update → ต้องการ fine-grained control ของ conductance
- Multi-epoch → device endurance (memristor: ~10^6 writes)

**นี่คือ niche ที่ project ของคุณ unique:** on-chip learning ด้วย SCFF + GD hybrid ที่ minimize gradient communication และ weight update frequency

### สำหรับเรา

คุณอยู่ใน CIM camp ชัดเจน แต่ approach ของคุณ unique ที่:
1. **On-chip learning**: ส่วนใหญ่ CIM papers focus inference ไม่ใช่ training
2. **SCFF + GD hybrid**: ไม่ใช่ pure backprop (ยาก on-chip) ไม่ใช่ pure local rule (weak) — hybrid ที่ minimize gradient communication
3. **Capacitor weight**: controllable, stable, CMOS compatible (เทียบกับ memristor ที่มี endurance issue)

สิ่งที่ควร borrow จาก CIM literature:
- **Noise-aware training** (train with device noise ตั้งแต่ simulation) — free regularization
- **Bit-slicing strategy** ถ้า Scap precision ไม่พอ — compute in 4-bit slices แล้ว combine
- **Differential pair** สำหรับ signed weights — draft-5 §15 ของคุณ correct แล้ว
- **Tile + stream** ถ้า crossbar ใหญ่เกินไป — systolic-style tiling สำหรับ analog

---

## สรุปทั้งไฟล์: กฎออกแบบที่สะอาด

**กฎ 1: Data movement แพงกว่า computation 2000-3000×**
→ Resident-weight (Scap ที่ไม่ออกจากชิป) แก้ที่ root ไม่ใช่ที่ symptom นี่คือ CIM thesis

**กฎ 2: Analog crossbar implement MVM ใน 1 settle time ผ่าน Ohm + Kirchhoff**
→ ต้นทุนหลักคือ **area** (N×M cells) ไม่ใช่ **time** ทุก decision ทุก crossbar size = decision เรื่อง chip area

**กฎ 3: Crossbar area = (n_input) × (n_output) cells, scale quadratically**
→ Ganglion ใหญ่ขึ้น 2× = area ใหญ่ขึ้น 4× Block-local grouping (ไฟล์ 11) คุม crossbar size ให้เล็ก แล้วใช้หลาย crossbar แทน

**กฎ 4: IR drop, sneak paths, device variation worse กับ larger crossbar**
→ ถ้าต้องการ network ใหญ่ขึ้น: tile crossbars เล็กๆ + stream activations (systolic-style) ไม่ใช่ make single crossbar ใหญ่ขึ้น

**กฎ 5: Non-idealities = regularization ถ้าเทรนกับ noise**
→ เทรน simulation ด้วย weight noise ตั้งแต่ต้น (ไม่ใช่ defer ไว้ทีหลัง) ทำให้ model robust โดยปริยายและ generalize ดีกว่า

**Design space ที่ถูกต้อง:**
- Spatial (crossbar settle) — ไม่ใช่ temporal (ALU วนซ้ำ)
- Block-local groups — ไม่ใช่ dense single crossbar ใหญ่
- Shuffle mixing — ไม่ใช่ dense translate clip
- Tile + stream ถ้าต้องสเกล — ไม่ใช่ ขยาย crossbar เดี่ยว

สัญชาตญาณ draft-5 ของคุณ (เดินสายทั้ง Ganglion เป็นวงจรตายตัว) คือ **spatial dataflow / full unrolling** ที่ถูกต้อง ปัญหาไม่ใช่ direction แต่คือ size: crossbar ต้องเล็กพอที่จะ fabricable และ accurate ซึ่งคือที่มาของ grouped architecture ใน 11-connectivity.md
