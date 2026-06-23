# Brainstorm 2.2.x — Analog Distribution Storage Evolution

> Self-research timeline. From const-c backprop bottleneck → 2-3 capacitor cross-multiplication scheme.
> Scope: scap storage architecture for decentralized weight update.
> Decision at end: ship 16-bit SRAM in current scope, 2-3 cap as future optimization.

---

## Stage 0 — จุดเริ่มต้น: const-c backprop bottleneck

### ไอเดีย

- scap update ทั้ง die ต้องผ่าน ALU ส่วนกลาง → centralized bottleneck
- ต้องการ decentralize: ให้ scap แต่ละตัวถือ **1-bit distribution flag** (contribute กับคำตอบมั้ย?)
- หลัง compute loss แล้ว ใช้ **time pulse** จาก error magnitude มา drain capacitor ทุกตัว **พร้อมกันทั้ง die**

### Analysis

**จุดแข็ง:**

- decentralized ตัวจริง — scap update ตัวเอง parallel ทั้ง die
- ใช้ SRAM พื้นที่ที่เคยเป็น branch prediction กลับมา
- event-driven หลัง init เสร็จ ไม่ต้อง routing centralized อีก

**จุดอ่อนที่ทำให้ต้องไปต่อ:**

- 1-bit flag = binary decision เท่านั้น ("contribute" / "ไม่ contribute")
- **gradient หยาบเกินไป** — ไม่มีข้อมูลว่า contribute "มากแค่ไหน"
- ถ้า scap หลายตัวสำคัญต่างกัน 100 เท่า มันถูก treat เท่ากันหมด
- จะ converge ได้แค่ task ที่ง่ายมากๆ pattern complex จะ stuck

### สรุป Stage 0

const-c มัน **proof-of-concept ของ decentralization** แต่ไม่ใช่ training mechanism ที่ใช้งานได้จริง ต้องเพิ่ม resolution ของสิ่งที่แต่ละ scap เก็บ

---

## Stage 1 — Time-charge measurement (8-bit SRAM)

### Breakthrough

สังเกตว่า **ALU มี idle slot ขณะ charge output capacitor ของ Ganglion อยู่** — เวลานี้เอาไปวัด distribution ของ scap ได้

### ไอเดีย

- เพิ่ม **trigger capacitor 19 ตัวใน ALU** (reuse ตลอด)
- วัด distribution level ของแต่ละ scap เป็น **"time to charge from A% to B%"**
- ความชันของ charge curve ∝ current ที่ scap นั้นปล่อย ∝ contribution
- เก็บเป็น **8-bit ใน SRAM ของแต่ละ scap**

### Analysis

**จุดแข็ง:**

- **256 levels** แทน 2 levels — ละเอียดขึ้นแบบกระโดด
- exploit idle time ของ ALU → ไม่กิน critical path เพิ่ม
- time-based measurement → robust ต่อ voltage variation (ดูชันเทียบ reference)

**จุดอ่อน:**

- A% กับ B% ถ้า fix ไว้ → scap ที่ charge เร็วมาก/ช้ามากจะ saturate
- 8-bit ที่ output stage ของ Ganglion ดูพอ
- แต่พอ **gradient chain ผ่านหลาย layer** error accumulate
- โดยเฉพาะ Limbic Loop ที่มี backprop ข้าม Cortex/Hippocampus → quantization noise สะสม

### สรุป Stage 1

ดีกว่า Stage 0 มาก แต่ **ยังไม่ละเอียดพอสำหรับ deep recurrent architecture** ของ Limbic Loop

---

## Stage 2 — 16-bit SRAM + momentum

### ไอเดีย

ขยายเป็น **16-bit SRAM ต่อ scap** + เก็บ **momentum ข้าม batch**

- distribution ใหม่ของแต่ละ batch มา **sum ทับของเดิม**
- update scheme: running average แบบ `value = (value × n + new) / (n+1)`
- ถ้า loss สูงผิดปกติ → **mother signal** เปิด pulse นาน → reset/boost momentum

### Analysis

**จุดแข็ง:**

- **65,536 levels** — ละเอียดพอสำหรับ gradient chain ยาว
- momentum ช่วย **smooth out noise** ระหว่าง batch
- mother signal เป็น escape hatch กรณี loss spike

**จุดอ่อน:**

1. **+16-bit SRAM/scap = พื้นที่ใหญ่มาก**
   - scap หลักล้านตัวบน die → SRAM กิน area อย่างมหาศาล
   - contradict กับ goal เดิม (recover branch prediction area)

2. **+1/n averaging มีปัญหา math**
   - เมื่อ n → ใหญ่ขึ้น contribution ของ batch ใหม่ → เล็กลงเรื่อยๆ
   - momentum จะ **freeze** หลัง n เยอะพอ
   - ไม่ adaptive กับ distribution shift

3. **ทางแก้คือ EMA** (`α × old + (1-α) × new`)
   - แต่ EMA ต้องมี **multiplication** ใน circuit
   - ถ้า α เป็น power-of-2 (0.5, 0.25, ...) → ใช้ shift ได้
   - แต่ tunable α ต้องการ multiplier จริง → กิน area อีก

### สรุป Stage 2

momentum concept ถูก แต่ implementation cost สูง ทั้งพื้นที่ SRAM และ arithmetic circuit ต้อง rethink storage primitive

---

## Stage 3 — Analog momentum (single cap2)

### Breakthrough ที่ 2

**ทิ้ง SRAM ไป** ใช้ **capacitor analog แทน**

### Architecture

| Component | Role                                       | Location |
| --------- | ------------------------------------------ | -------- |
| **cap0**  | real weight (untouched until update)       | scap     |
| **cap1**  | reference, calibrated, ต่อ digital trigger | ALU      |
| **cap2**  | distribution storage, drain/charge รัวๆ    | scap     |

### กลไก

- ALU ใช้ cap1 เป็น timing reference
- cap2 ใน scap ถูก charge **parallel กับ ALU charging output ของ Ganglion**
- ไม่กิน critical path เพิ่มเลย — exploit slot ที่ ALU ต้องรอ output charge อยู่แล้ว
- update cap0 ค่อยทำตอน end-of-batch signal มา

### Analysis

**จุดแข็ง:**

- **continuous resolution** — ไม่มี quantization step
- **storage area เล็กลง** เทียบกับ 16-bit SRAM
- **parallel charge** = zero latency overhead

**จุดอ่อนสำคัญ:**

1. **Charge sharing ไม่ linear**
   - ถ้าใช้ direct charge sharing ระหว่าง cap จะได้ "ครึ่ง" เสมอ
   - ต้อง active circuit (cascode current source) ในการ load
   - กลายเป็น constant current source charging → linear กับ time

2. **Leakage drift**
   - capacitor รั่วต่อเนื่อง
   - momentum ข้าม batch อยู่ใน analog domain → drift ไม่ undo ได้
   - ต้องการ refresh circuit (แต่ refresh ก็ต้องการ ADC อ่านค่า ขัดกับ goal)

3. **Precision ของ cap เดี่ยว**
   - cap เดี่ยว ๆ ที่ใช้งานได้ ~6-7 bit equivalent (limited by noise floor)
   - ยังไม่ถึง 16-bit precision ที่ Stage 2 ต้องการ

### สรุป Stage 3

หลักการ analog momentum ใช้ได้ แต่ **precision ของ cap เดี่ยวยังไม่พอ** ต้องการ scheme ที่เพิ่ม effective resolution

---

## Stage 4 — 2D analog precision (cap2 × cap3 cross-multiplication)

### Breakthrough ที่ 3

แทนที่จะใช้ cap2 ตัวเดียวเก็บ linear scale → **ใช้ cap2 × cap3 เป็น 2D coordinate**

### Math

```
effective_value = cap2.voltage × cap3.voltage
```

- ถ้า cap แต่ละตัวมี 256 distinguishable levels
- combined → 256 × 256 = **65,536 effective levels**
- **เกิน 16-bit SRAM ของ Stage 2** ด้วย capacitor 2 ตัว

### Analysis

**จุดแข็งทางทฤษฎี:**

- **explosive range** — precision ระเบิดเป็นกำลังสอง
- pure analog → ไม่ต้อง ADC ตอน read
- พื้นที่ 2 cap < 16-bit SRAM (cap density สูงกว่า SRAM cell)

**ปัญหาเฉพาะหน้า — Ambiguity:**

```
cap2 × cap3 = constant → infinite solutions
```

ตัวอย่าง: ผลคูณ 0.21V² อาจมาจาก:

- cap2 = 0.3V, cap3 = 0.7V
- cap2 = 0.7V, cap3 = 0.3V
- cap2 = 0.21V, cap3 = 1.0V
- ...

ทำให้ตอน **update** ไม่รู้จะแก้ตัวไหน

### สรุป Stage 4

concept ถูก ground-breaking แต่ต้องการ **invariant** ที่ทำให้ representation ไม่ ambiguous

---

## Stage 5 — Fixed-larger normalization rule

### ไอเดีย

**Rule:** ตัวใหญ่กว่าคือ scale, ตัวเล็กกว่าคือ ratio

```
if cap2 ≥ cap3:
    cap2 = fixed (scale)
    cap3 = ratio ของ cap2
```

### ผลลัพธ์

- cap3 ไม่ใช่ absolute voltage อีกต่อไป
- cap3 = fraction of cap2 → **unique decomposition**
- **ambiguity หายไป**

### Reconstruction

ตอน read ค่ากลับ:

```
value = cap2 × cap3_ratio
```

- opamp ทำ multiplication ตรงๆ
- **ไม่ต้องมี lookup table, ไม่ต้องมี ADC**

### Analysis

**จุดแข็ง:**

- elegant — เปลี่ยน representation ทำให้ ambiguity หายเอง
- structurally คล้าย **floating point** (cap2 = exponent-like, cap3 = mantissa-like)
- read path เป็น passive analog → fast + low power

**จุดอ่อน:**

- ถ้า cap3 grow จนเกือบเท่า cap2 → invariant ใกล้พัง
- ต้องมี mechanism จัดการตอน cap3 → cap2 (Stage 7 จะมาแก้)

### สรุป Stage 5

ทำให้ Stage 4 implementable ได้จริง แต่ยังไม่ปิดวงจร update

---

## Stage 6 — Update equation (closing the loop)

### Setup

- cap1 (ใน ALU) เก็บ distribution ของ batch ปัจจุบัน เช่น 3.5V
- cap2, cap3 (ใน scap) เก็บ accumulated momentum
- ต้องการ update: ใส่ cap1 เข้าไปใน cap2 × cap3

### Math

ต้องการ:

```
cap2 × cap3_new = (cap2 × cap3_old) + cap1
```

cap2 fixed → solve cap3_new:

```
cap3_new = cap3_old + (cap1 / cap2)
```

### Key Insight

`cap1 / cap2` เป็น **constant scale factor** (เพราะ cap2 fixed) ทำให้:

- **ไม่ต้องการ active division**
- ทำได้ด้วย **passive voltage divider** (resistor ratio นิ่ง)
- หรือ **switched-capacitor scaling** ratio fixed ตาม cap2 stage

### Analysis

**จุดแข็ง:**

- **update เป็น pure analog operation** — charge transfer ผ่าน scaling network
- **ไม่ต้อง ADC, ไม่ต้อง multiplier, ไม่ต้อง division circuit**
- precision ขึ้นกับ matching ของ scaling network เท่านั้น

**จุดอ่อน:**

- voltage divider mismatch ทั่ว die → systematic error ระหว่าง scap
- ต้องการ calibration phase ตอน boot

### สรุป Stage 6

ปิดวงจร update ได้สวยมาก — analog throughout, no domain crossing

---

## Stage 7 — Cap swap mechanism (dynamic range expansion)

### ปัญหา

cap3 accumulate ต่อเนื่อง → จะถึงจุดที่ **cap3 ≈ cap2** → invariant พัง

### Solution

เมื่อ cap3 → ใกล้ cap2:

- **swap บทบาท cap2 ↔ cap3**
- cap3 (เดิม) กลายเป็น scale ตัวใหม่
- cap2 (เดิม) กลายเป็น ratio ของ cap3 ใหม่

### ผลลัพธ์

- effective storage range ขยายเป็น **กำลังสอง** ของ cap range
- คล้าย **floating point with shared exponent**
- decay precision เป็น **กำลังสอง** ที่ค่าเล็กๆ (tradeoff)

### Analysis

**จุดแข็ง:**

- range expansion มหาศาล
- **adaptive resolution** — ค่ามาก/น้อย แต่ละช่วง precision ต่างกัน
- เหมาะกับ neural weight (มัก concentrated ใน range กลางๆ → precision สูง)

**จุดอ่อน:**

1. **Swap timing**
   - swap = discrete event ที่ analog circuit ต้อง detect threshold crossing
   - hysteresis + noise อาจทำให้ swap ผิดจังหวะ → data corruption
   - corruption ไม่ detectable เพราะค่าที่ผิดยัง valid voltage อยู่

2. **Precision decay at extremes**
   - weight ที่ใกล้ 0 หรือใกล้ max → quantization noise สูง
   - ถ้า architecture มี sparse weight สำคัญ → อาจหายไป

3. **Implementation complexity**
   - comparator + control logic + swap switch ต่อ scap
   - เพิ่ม transistor count ต่อ scap

### สรุป Stage 7

range expansion ที่ powerful มาก แต่ **swap mechanism คือจุดเปราะที่สุด** ของทั้ง scheme

---

## Stage 8 — Batch-locked fixed cap (swap stability fix)

### ปัญหาที่ Stage 7 ทิ้งไว้

swap mechanism เป็น discrete event ที่ analog circuit ต้อง trigger ตอน threshold crossing — เปราะมาก เพราะ:

- threshold detection มี hysteresis + noise
- ระหว่าง batch ที่ cap3 อาจ oscillate ใกล้ cap2 → trigger swap ซ้ำๆ
- swap ผิดจังหวะ → silent data corruption (ค่ายัง valid voltage อยู่)

### ไอเดีย

**Lock fixed-cap assignment ต่อ batch** ไม่ให้ swap ระหว่าง batch

**Rule:**

- ตอน **เริ่ม batch ใหม่** → เปรียบเทียบ cap2 กับ cap3, ตัวใหญ่กว่า = fixed scale
- ระหว่าง batch → **ห้าม swap ไม่ว่ายังไง** แม้ ratio cap จะ update ใหญ่กว่า scale cap แล้วก็ตาม
- ตอน **end of batch** → ค่อยประเมินใหม่ → swap ถ้าจำเป็น

### Mechanics

```
[Start of batch N]
  if cap2 ≥ cap3:
      fixed = cap2     // lock
      variable = cap3
  else:
      fixed = cap3     // lock
      variable = cap2

[During batch N]
  // multiple updates
  variable += cap1 / fixed
  // ไม่สนว่า variable จะเกิน fixed หรือไม่
  // fixed ไม่เปลี่ยนเด็ดขาด

[End of batch N → Start of batch N+1]
  re-evaluate: ใครใหญ่กว่ากัน → lock ใหม่
```

### Analysis

**จุดแข็ง:**

1. **ตัด swap timing instability ออกทั้งหมด**
   - swap จุดเดียวที่เกิดได้ = batch boundary
   - เป็น **synchronous event** ที่ control logic จัดการได้ตรงๆ
   - ไม่ต้องใช้ analog comparator threshold detection

2. **Batch boundary = clean checkpoint**
   - ตอนสิ้น batch ระบบ idle อยู่แล้ว (รอ loss compute)
   - เปรียบเทียบ cap2 vs cap3 ตอนนี้ → **digital comparison** หลัง read ผ่าน opamp
   - swap (ถ้าจำเป็น) ทำได้ใน controlled state

3. **Math invariant ไม่เสียระหว่าง batch**
   - ระหว่าง batch fixed_cap คงที่ → update equation `variable_new = variable_old + cap1/fixed` ยัง linear
   - **reconstruction `effective = fixed × variable` ยังถูกต้อง** แม้ variable > fixed
   - แค่ swap convention ที่ "ตัวใหญ่กว่า = fixed" จะ violate ชั่วคราว — แต่ math ยังทำงาน

4. **ทำให้ analog circuit ง่ายลงเยอะ**
   - voltage divider scaling ratio ไม่เปลี่ยนระหว่าง batch
   - ไม่ต้องมี dynamic switching ระหว่าง compute
   - control logic ทำงานแค่ batch boundary

**จุดอ่อน:**

1. **Precision degradation ชั่วคราวเมื่อ variable > fixed**
   - ถ้า variable grow เกิน fixed มาก → effective precision ของ variable ลดลง
   - เพราะ variable เป็น "ratio of fixed" แต่ ratio > 1 หมายถึงใช้ headroom เกิน design point
   - **แต่เฉพาะ batch นั้น** — boundary ถัดไปจะ rebalance

2. **Batch size ต้องไม่ใหญ่เกิน**
   - ถ้า batch ยาวมาก variable อาจ saturate เต็ม cap ก่อนจบ batch
   - ต้อง bound: `cap1 × batch_size / fixed < cap_max`
   - ใช้ guide เลือก batch_size หรือ pulse magnitude ของ cap1

3. **ตอน swap ที่ boundary ต้อง re-anchor**
   - หลัง swap ratio variable ใหม่ = ratio variable เก่า ÷ ratio scale change
   - operation นี้ทำตอน boundary → ไม่กิน critical path
   - แต่ต้องการ active circuit ช่วงเวลาสั้นๆ

### Tradeoff Summary

| Aspect                         | Stage 7 (continuous swap)  | Stage 8 (batch-locked)           |
| ------------------------------ | -------------------------- | -------------------------------- |
| Swap event                     | anytime (threshold-driven) | batch boundary only              |
| Detection                      | analog comparator          | digital comparison after read    |
| Corruption risk                | สูง (silent)               | ต่ำ (synchronous, observable)    |
| Precision (steady-state)       | optimal                    | optimal                          |
| Precision (mid-batch overflow) | optimal (swap แก้ทันที)    | degraded ชั่วคราว                |
| Circuit complexity             | สูง (comparator + control) | ต่ำกว่า (control เฉพาะ boundary) |
| Math correctness               | sensitive to swap timing   | invariant throughout batch       |

### Key Insight

นี่คือการ **trade ค่าใช้จ่ายของ precision ชั่วคราว** กับ **stability ของ data**

precision loss ระหว่าง batch ที่ variable > fixed → **recoverable** (จะ rebalance ที่ boundary)

silent corruption จาก swap miss-trigger → **irrecoverable** (data หาย permanently)

### สรุป Stage 8

นี่คือ **stability fix สำคัญที่ทำให้ 2-3 cap scheme implementable** จริงในวงจร

- Stage 7 มี theoretical range ที่ดี แต่ swap mechanism ที่เปราะ
- Stage 8 **ยอมเสีย precision นิดหน่อยใน edge case** เพื่อแลกกับ data integrity และ circuit simplicity
- batch boundary เป็น natural synchronization point อยู่แล้ว — exploit มันให้คุ้ม

นี่ทำให้ scheme พร้อมที่จะลง SPICE simulation จริงๆ ใน Track B

---

## Stage 8 — Batch-locked role assignment

### ปัญหาที่ Stage 7 ยังเปิดทิ้งไว้

Swap mechanism ของ Stage 7 trigger ทันทีตอน cap3 → ใกล้ cap2:

- **threshold detection ใน analog domain ไม่เสถียร** — hysteresis + noise ทำให้ swap ผิดจังหวะได้
- ระหว่าง batch กำลัง compute อยู่ → swap event = data corruption ที่ไม่ detectable
- ต้องการ comparator + control logic ที่ active ตลอดเวลา → กิน power + area

### ไอเดีย Stage 8

**Lock role ของ cap2/cap3 ไว้ทั้ง batch — swap เฉพาะที่ batch boundary**

```
At start of batch:
    larger_cap  = max(cap2, cap3)  → fixed as "scale"
    smaller_cap = min(cap2, cap3)  → "ratio" ที่ update ได้

During batch:
    update เฉพาะ smaller_cap (ratio)
    larger_cap (scale) untouched
    แม้ smaller_cap จะ grow เกิน larger_cap → ไม่ swap

At end of batch:
    re-evaluate: ใครใหญ่กว่า → role ใหม่สำหรับ batch ถัดไป
```

### Mechanism

- ต้องการแค่ **1-bit role flag per scap** เก็บว่า batch นี้ "cap2 เป็น scale" หรือ "cap3 เป็น scale"
- flag อัพเดทตอน **batch boundary clock edge** เท่านั้น
- ระหว่าง batch → role static → no comparator active → no swap risk

### Analysis

**จุดแข็ง:**

1. **Eliminate mid-batch swap corruption**
   - swap risk หายไปทั้งหมดระหว่าง compute
   - data integrity guarantee ตลอด batch

2. **Synchronous swap = clean event**
   - batch boundary มี clock edge อยู่แล้ว (สำหรับ momentum update)
   - role swap piggyback บน clock เดียวกัน → no extra timing circuit
   - comparator fire **ครั้งเดียวต่อ batch** ไม่ใช่ตลอดเวลา → low power

3. **Mathematical correctness preserved**
   - ตอน read: `value = larger_cap × smaller_cap_ratio` ยัง valid
   - แม้ smaller > larger ชั่วคราว → math ยังถูก เพราะมัน fix แค่ "ตัวไหนเป็น scale" ไม่ใช่ "ตัวไหนต้องมากกว่า"
   - invariant ของ Stage 5 (fixed-larger normalization) ผ่อนคลายลงเป็น **"fixed-was-larger"**

4. **Simple implementation**
   - 1-bit flag per scap (เล็กมากเทียบกับ 16-bit SRAM)
   - comparator ทำงานแค่ที่ batch edge → reuse ได้ทั้ง die ผ่าน sequential scan

**Tradeoff:**

1. **Delayed role correction**
   - ถ้า scale ตัวเดิมเล็กไปสำหรับ batch ปัจจุบัน → ratio จะ exceed 1.0 ชั่วคราว
   - precision ในช่วงนี้ degrade เล็กน้อย (ratio > 1.0 = unusual operating region สำหรับ opamp scaling)
   - แก้: ออกแบบ scaling network ให้ tolerate ratio 0–2× แทน 0–1×

2. **Edge case: ทั้ง 2 cap ใกล้เคียงกัน**
   - ถ้า cap2 ≈ cap3 ที่ batch boundary → role assignment อาจ flip ทุก batch
   - oscillation ทำให้ momentum tracking ไม่ smooth
   - แก้: เพิ่ม hysteresis band ที่ batch boundary (ถ้าใกล้กันมาก → คง role เดิม)

3. **Worst case: extreme drift within batch**
   - ถ้า ratio cap grow แบบรุนแรงในหนึ่ง batch → อาจเกิน 2× scale
   - ต้องมี clamp circuit ป้องกัน saturate
   - แต่ใน practice neural momentum ไม่ค่อย spike แบบนี้ ยกเว้น early training

### สรุป Stage 8

แก้ Stage 7 ที่จุดเปราะที่สุด — **discrete swap event** ย้ายจาก **continuous async** → **synchronous at batch boundary**

ทำให้ทั้ง scheme เป็น **clocked analog system** ที่ predictable + verifiable

> Key insight: **Storage state ไม่จำเป็นต้อง represent ค่าจริงในจังหวะ optimal ตลอดเวลา** — แค่ต้อง represent ถูกต้อง **at read time** ของ Ganglion compute ก็พอ ระหว่าง batch ปล่อยให้ "scale ตัวที่เคยใหญ่" ยังเป็น scale ต่อไป — math ก็ยังถูกหมด

---

# Decision: ใช้อะไรในตอนนี้?

## Comparison Table

| Aspect                  | 16-bit SRAM                 | 2-3 Capacitor Scheme                              |
| ----------------------- | --------------------------- | ------------------------------------------------- |
| **Precision**           | 65,536 levels (fixed)       | 65,536+ levels (expandable via swap)              |
| **Stability**           | Perfect (digital)           | Drift จาก leakage                                 |
| **Process variation**   | Insensitive                 | Sensitive (cap matching ทั่ว die)                 |
| **Read latency**        | Fast (digital read)         | Fast (passive opamp multiply)                     |
| **Update circuit**      | Digital adder + register    | Voltage divider + charge transfer                 |
| **Area per scap**       | สูง (16 bit cells)          | ต่ำกว่า (2-3 cap + control)                       |
| **Calibration needed**  | ไม่ต้อง                     | ต้อง (cap1 reference + scaling network)           |
| **Refresh needed**      | ไม่ต้อง                     | อาจต้อง (depends on batch period vs leakage rate) |
| **Simulation accuracy** | Cycle-accurate ใน Python    | ต้อง SPICE หรือ noise model จริง                  |
| **Failure modes**       | bit flip (rare, detectable) | drift, swap miss-trigger, mismatch (silent)       |

## Decision: SRAM ก่อน เพราะ...

### 1. Scientific Method

**ต้องมี baseline ที่รู้ว่าทำงานถูกต้องก่อน** ถึงจะ benchmark optimization version ได้

- ถ้า H1 ไม่ converge บน SRAM (ideal storage) → architecture ผิด ไม่ใช่ storage ผิด
- ถ้า H1 ไม่ converge บน analog cap → ไม่รู้ว่าผิดที่ architecture หรือ storage

### 2. Simulation Fidelity

draft2 scope คือ **Python simulation** (§2 ของ draft)

- 16-bit SRAM model ได้เป๊ะใน Python — `int16` ตรงๆ
- analog cap model ใน Python จะ **idealize** leakage/noise/mismatch ทิ้ง
- ผลลัพธ์ที่ได้จะ over-optimistic → false confidence

ถ้าจะ model analog cap ให้ตรงต้อง:

- SPICE simulation (out of scope)
- หรือ noise-injected Python model ที่ calibrate ด้วย measurement จริง (มี chip ที่ไหน?)

### 3. Risk Isolation

H1 (update rule convergence) **already คือ central open question** ของ project (§3, §7 ของ draft)

- เอา analog storage มาผสมตอนนี้ = compound 2 unknown
- ถ้า fail แยกไม่ออกว่า fail เพราะอะไร
- isolate variables: storage = solved (SRAM), focus 100% บน update rule

### 4. Progressive Refinement

SRAM → analog เป็น **strict optimization** ไม่ใช่ paradigm shift

- ถ้า H1 ทำงานบน SRAM 16-bit ได้
- การ port ไป analog cap คือการลด precision + เพิ่ม noise → testable degradation
- มี ground truth ให้เทียบว่า analog version degrade เท่าไหร่ → **clean scientific contribution**

ถ้าทำ analog ก่อน — ไม่มีอะไรเทียบ → degraded result อาจถูก dismiss ว่าเป็น analog noise

---

# Roadmap

## Track A — Current Scope (draft2)

- [x] Architecture spec (§3-§4 ของ draft2)
- [ ] **Storage: 16-bit SRAM per scap**
- [ ] Phase 1-6 simulation ใน Python
- [ ] H1-H5 validation
- [ ] **Goal: prove architecture viable**

## Track B — Future Optimization (draft3+)

- [ ] Formal spec ของ 2-3 cap scheme
- [ ] SPICE simulation ของ single scap (charge dynamics + leakage)
- [ ] Noise-injected Python model calibrated ด้วย SPICE
- [ ] Compare convergence: SRAM baseline vs analog cap
- [ ] Quantify precision degradation per layer depth
- [ ] **Goal: validate ว่า analog optimization ไม่ทำลาย convergence**

---

# Open Questions (ส่งต่อไป draft3)

1. **Leakage rate vs batch period** — analog momentum อยู่ได้นานแค่ไหนก่อนต้อง refresh?
2. **Cap matching tolerance** — process variation ที่ tolerable คือเท่าไหร่?
3. **Swap miss-trigger handling** — มี mechanism detect/recover จาก corruption มั้ย?
4. **cap1 calibration** — bandgap reference? digital trim? คุ้มกับ area savings มั้ย?
5. **Sparse weight preservation** — Ganglion มี weight ใกล้ 0 ที่สำคัญมั้ย? ถ้ามี analog quantization noise จะกินมั้ย?

---

# Summary

จาก const-c (Stage 0) → 16-bit SRAM with momentum (Stage 2) → 2-3 cap cross-multiplication (Stage 4-7) → batch-locked role assignment (Stage 8) → batch-locked swap (Stage 8)

ทั้ง journey **ส่ง output ลงสู่ design decision เดียว**:

> **ใช้ 16-bit SRAM ใน draft2 เพราะมัน stable, simulatable, และเป็น clean baseline สำหรับ validate H1**
>
> **2-3 cap scheme (with Stage 8 batch-locking) เป็น optimization track ที่จะ revisit หลังจาก SRAM version converge แล้ว** — เพื่อให้ optimization มี ground truth ให้ benchmark

Storage primitive ไม่ใช่ bottleneck ของ research question ตอนนี้ — update rule (H1) คือ bottleneck ตัวจริง focus ตรงนั้นก่อน

---

# Overview of Summary Achitecture

## ALU

มี hardwire modified op-amp circuit that can compute 2-3-3-2 directly รองรับพวก relu/tanh ด้านในเลย

โดยที่รับเป็น 2 global capacitor สำหรับ input (not change or drain) กับ 2 global capacitor สำหรับ output (ALU have to charge it voltage level)

ซึ่ง 2-3-3-2 ganglion มันจะมี 29 wires ที่ใช้ scap เก็บค่า analog weight (21 weight scap + 8 bias scap) ทำให้ใน ALU เเต่ละตัว ต้องมีอีก 29 capacitor + DC time measure circuit สำหรับการอ่านค่าความเเรงของ 29 scaps พวกนั้น

โดยเราจะจับ trigger ว่า capacitor ใน ALU เปลี่ยนจาก A% ไป B% ภายในเวลากี่วิ ภายใน ALU ก็จะมี 16 bits SRAM \* 29 scap amount ถือเป็น temporary ให้ก่อน

จากนั้นเมื่อ measure เสร็จเเล้ว เเต่ละ ALU ก็จะเอาค่่า temp_time เข้าไปบวกในเเต่ละ scaps time จริงๆ โดยที่ 16 bits SRAM ใน scap เเต่ละตัวก็จะถือ momentum history ไว้

เราสามารถใช้ momentum history นั้นในการทำ multi batch compute, simgle batch momentum keep, หรือเเม้เเต่ adam optimization ได้ โดยที่ใช้ค่า decay 0.75 (3 ใน 4) หรือละเอียดกว่านั้นเเล้วเเต่การ shift

## Scap (SRAM + Capacitor)

มี capacitor หลักไว้เก็บค่า weight 1 อัน
มี 1 SRAM bit sign สำหรับทิศทางของ weight
มี 8 SRAM bit level สำหรับการ refill capacitor leak
มี 16 SRAM momentum history (ไม่ใช้ 1 bit history SRAM เเล้วเพราะว่าใช้ตัวนี้ได้เลย)
มี N\*M SRAM ไว้เก็บ community bit ตอน intial ว่า scap ตัวนี้ต้องใช้ bus ไหนในการรับ ใช้ bus ไหนในการส่ง ต้องอ่าน global input capacitor จากไหน, ต้องเอาไปเก็บไว้ไหน

มี update_signal เป็น input ที่ดึงมาจาก braodcast bus หลัก
เเละมี tri-ode ส่ง feed back มาว่า +, 0, หรือ -

โดยที่ master core จำทำกาเปรียบเทียบ prediction กับ label (future input) ไว้ จากนั้นคำนวณค่า loss เเล้วส่ง dynamic value กับมาเป็นเวลาที่จะเปิด update_signal ค้างไว้

โดยเมื่อ update_signal จาก broadcas bus = 1, เเต่ละ scap ก็จะอัพเดท weight capacitor ของโดยการคูณระยะเวลาจาก update_signal หลัก เเละ SRAM modemtum ของมัน (อาจจะใช้เป็น PWM หรืออะไรสักอย่าง) โดยที่จะเอา tri-ode feedback มาคำนวณกับ bit sign เพื่อหาทิศทางอัพเดทจริงอีกที

โดยที่ตอนนี้การทำ backpropagation จะถูก decentralize จาก master เลย เเค่เปิด broardcast update_signal ไว้ scap ทั้งชิปจะอัพเดทพร้อมกัน

เเละมี reset_history_signal ใน broadcast ด้วย เอาไว้ล้าง history นั่นเเหละ

# Global capacitor

สำหรับเก็บ stage ระหว่าง Ganglion จนถึงพวก Limbic Loop

เราน่าจะใช้ scap ได้เลยหรือ scap\* ที่เรา optimize มันสำหรับการอ่านเขียนโดยเฉพาะ

# Reuse G brain

ในตอนนี้เเต่ละ scap เราสามารถเก็บ mometum การอัพเดทได้เเล้ว จาก 16 bit SRAM architecture ใหม่ ทำให้ reuse Ganglion สามารถทำได้ง่ายๆเลย เเค่ทุกๆ layer ที่มันไป ค่า distribution ก็จะถูกเอาไปเก็บผสมเป็น momentum ไว้

# Multi batch training

เหมือนกับ G brain เลย ตอนนี้ achitecture ใหม่รองรับมันเเล้ว
