# 18 — noise แอนะล็อก และปัญหาอุณหภูมิที่คุณแกะไม่ออก

> `17-durability.md` ให้ทฤษฎี; อันนี้คือความจริงของวงจร — noise อะไรบ้างที่ชนเข้ากับชิป weight-คาปาซิเตอร์จริงๆ และโดยเฉพาะความกังวลเรื่อง **อุณหภูมิ / การแกว่งเร็ว** ของคุณ กุญแจเชิงแนวคิดดอกเดียวที่คุณขาด: **จับคู่เทคนิคให้ตรงกับ *timescale* ของ noise noise ช้าให้ลบทิ้ง (เทียบกับ reference); noise เร็วให้เฉลี่ย (ตามเวลาหรือสำเนา)** พอรู้ความถี่ของ noise เทคนิคก็แทบถูกบังคับ และข่าวดี: **คุณออกแบบส่วนใหญ่ของอันนี้ไว้แล้วใน draft-5 (§15) — คุณแค่ไม่รู้ทฤษฎีเบื้องหลังว่าทำไมมันเวิร์ก**

---

## 1 — ก่อนอื่น: ตั้งชื่อศัตรู (อนุกรมวิธาน noise แอนะล็อก)

ชิป weight-คาปาซิเตอร์ที่คำนวณด้วย crossbar เจอเมนูเฉพาะ — รู้ว่าตัวไหนเป็นตัวไหน เพราะ *การแก้ขึ้นกับ timescale*:

| Noise | Timescale | ที่มา | ฆ่าด้วย |
| --- | --- | --- | --- |
| **kT/C thermal** | **เร็ว** (broadband) | การกวนเชิงความร้อนบนทุกคาป | คาปใหญ่ขึ้น; การเฉลี่ย |
| **Shot noise** | เร็ว | ตัวพาประจุที่ไม่ต่อเนื่อง | การเฉลี่ย; สัญญาณใหญ่ขึ้น |
| **1/f (flicker)** | **ช้า** | กับดักในอุปกรณ์ (device traps) | chopper / auto-zero |
| **Offset / mismatch** | **คงที่→ช้า** | ความแปรปรวนระหว่างอุปกรณ์ | differential; auto-zero; calibration |
| **Temperature drift** | **ช้า** | T เปลี่ยน conductance/threshold | differential; chopper; reference cell |
| **Supply / coupling** | เร็ว→ช้า | `V` noise, crosstalk | differential (common-mode reject) |
| **Conductance drift** | ช้า | weight ที่เก็บไว้แก่ตัวลง | refresh; noise-aware training |

การแบ่งที่จัดระเบียบทุกอย่าง: **ของช้า (อุณหภูมิ, 1/f, offset, drift) เทียบ ของเร็ว (kT/C, shot, coupling)** ชุดเครื่องมือสองชุดที่ต่างกันอย่างสิ้นเชิง

---

## 2 — kT/C noise: ฟิสิกส์ขั้นพื้นฐานที่เลี่ยงไม่ได้

*Johnson, 1928; Nyquist, 1928 (ทฤษฎีบทความผันผวน-ผลต้านทาน, fluctuation-dissipation theorem)*

### ปัญหาที่มันแก้ (หรือพูดให้ถูก: ปัญหาที่มันสร้าง)

นี่ไม่ใช่เรื่องการออกแบบที่แย่ มันคือ **ทฤษฎีบทของเทอร์โมไดนามิกส์** เมื่อไรก็ตามที่มีความร้อน (`T > 0 K`) และมี capacitor อยู่ในวงจร จะมี noise ของแรงดันบน capacitor นั้นเสมอ ไม่มีทางหลีกเลี่ยง

### กลไกจริงๆ

**ฟิสิกส์:** thermal noise เกิดจาก *Brownian motion ของอิเล็กตรอน* ในตัวนำ ที่อุณหภูมิ T > 0 K อิเล็กตรอนแต่ละตัวสั่น (Boltzmann energy ~ kT) สิ่งนี้สร้าง random current ที่เรียกว่า Johnson-Nyquist noise ขนาด:
```
Power spectral density ของ voltage noise = 4kTR  (V²/Hz)
```

เมื่อ random current นี้ไหลผ่าน resistor R เข้าชาร์จ capacitor C สิ่งที่น่าแปลกใจเกิดขึ้น: ถ้าคุณ integrate noise power ทุกความถี่ตั้งแต่ 0 ถึง ∞:

```
V_noise² = ∫₀^∞ (4kTR / (1 + (2πfRC)²)) · (1/(2πRC)) df
           = kT/C
```

R **หายไป!** ผลลัพธ์คือ:
```
V_rms = √(kT/C)
```

ที่อุณหภูมิห้อง (T = 300K, k = 1.38×10⁻²³ J/K):
- C = 100 fF: V_rms = **200 μV** 
- C = 1 pF: V_rms = **64 μV**
- C = 10 pF: V_rms = **20 μV**
- C = 100 pF: V_rms = **6.4 μV**

นี่คือ **noise floor ขั้นต่ำที่ฟิสิกส์บังคับ** ไม่สามารถลด R หรือเปลี่ยน process ให้หายไปได้ ทางเดียวคือ **C ใหญ่ขึ้น** (ลด noise ≈ √10x ต่อ C ที่เพิ่มขึ้น 10x)

**ผลกระทบต่อ weight:** Scap ของคุณที่เก็บ weight เป็นคาปาซิเตอร์ ถ้า Scap มีขนาด C_w และ weight ถูก encode เป็น voltage บน C_w แล้ว weight แต่ละตัวจะมี noise level √(kT/C_w) อยู่เสมอ ที่ C_w = 1 pF นั่นคือ 64 μV ถ้า weight range คือ ±1 V (full scale = 2V) นั่นคือ noise ~0.003% ซึ่งยอมรับได้ แต่ถ้า C_w = 10 fF (เล็กมาก) V_rms = 640 μV หรือ 0.032% — เริ่มสำคัญขึ้น

### ผลที่น่าตื่นเต้น

Nyquist พิสูจน์ในปี 1928 ว่า Johnson noise คือผลจาก **fluctuation-dissipation theorem** — ความร้อนที่ resistor "dissipate" และ noise ที่มันสร้างมาจากกลไกเดียวกันและ trade กัน คุณไม่สามารถมีทั้ง zero noise AND ไม่มี dissipation ในระบบสมดุล อุณหพลศาสตร์บังคับ

ทฤษฎีบทนี้ยืนหยัดมาตั้งแต่ 1928 และยังไม่เคยถูกพิสูจน์ว่าผิดในวงจรแอนะล็อกใดๆ

### สำหรับเรา

**kT/C เป็น noise floor ของ weight ทุกตัวในชิป** และมันเป็นฟิสิกส์ขั้นพื้นฐาน ทางออกมีสามอย่างเท่านั้น:

1. **C ใหญ่ขึ้น** — ลด noise แต่เพิ่มพื้นที่และทำ weight ชาร์จช้าลง การ trade นี้ต้องเลือกตาม weight ว่าสำคัญแค่ไหน (weight ใน GD layer ที่ต้องแม่น → C ใหญ่; weight ใน SCFF layer ที่ tolerant ต่อ noise → C เล็กได้)
2. **เฉลี่ย** — รันหลายรอบ noise เฉลี่ยออก ลดลง 1/√N (von Neumann multiplexing)
3. **เทรนกับมัน** — Bishop บอกว่ามันกลายเป็น regularization ฟรี

เลือก three of the above ตามความสำคัญของ weight แต่ละตัว

---

## 3 — 1/f Noise และ Offset: ศัตรูช้าสองตัว

### 1/f Noise (Flicker Noise)

**ปัญหา:** ทุก MOSFET มี noise ที่มีขนาดใหญ่มากที่ความถี่ต่ำ (เรียกว่า "pink noise" หรือ flicker noise) และลดลงตามความถี่ f:
```
Noise power ∝ 1/f^α    (α ≈ 1)
```

ที่มา: อุปกรณ์ semiconductor มี **กับดักอิเล็กตรอน (charge traps)** ในชั้น gate oxide แต่ละกับดักจับและปล่อยอิเล็กตรอนแบบสุ่มด้วย timescale ต่างๆ ตั้งแต่ไมโครวินาทีถึงวินาที ผลรวมของ trap หลายตัวที่ timescale ต่างๆ สร้าง noise ที่มีสเปกตรัม 1/f

**ขนาดที่น่ากลัว:** สำหรับ precision op-amp ทั่วไปที่ node ต่ำกว่า 10 kHz:
- ที่ 1 Hz: noise อาจสูงถึง 100 nV/√Hz
- ที่ 10 kHz: ลงมาที่ ~10 nV/√Hz (ใกล้กับ white noise floor)

สำหรับ analog weight update ที่ช้า (ทำงานที่ความถี่ต่ำ kHz) 1/f noise สำคัญมาก

### Offset Voltage

**ปัญหา:** ถ้าต่อ input ของ op-amp ทั้งสองข้างเข้า ground output ควรเป็น 0V แต่จริงๆ มันไม่เป็น เพราะ transistor สองตัวในตัว differential pair ของ op-amp ไม่เหมือนกันทุกประการ (process variation ระหว่างอุปกรณ์) ผลต่างนี้เรียกว่า **offset voltage** V_OS

ขนาดทั่วไป: 0.1–10 mV สำหรับ standard op-amp, ~1 μV สำหรับ precision auto-zero op-amp

**Drift:** V_OS ยังเปลี่ยนตาม temperature ด้วย (เรียกว่า temperature coefficient of offset) ปกติ 1–10 μV/°C สำหรับ IC ทั่วไป ที่ ΔT = 50°C นั่นคือ drift 50–500 μV เพิ่มจาก offset ตั้งต้น

---

## 4 — Differential Signaling / Common-Mode Rejection — ตัวเอ้สำหรับ Temperature Drift

*ความรู้คลาสสิกในวงจรแอนะล็อก, consolidated ใน: Razavi, "Design of Analog CMOS Integrated Circuits," 2001*

### ปัญหาที่มันแก้

temperature drift ทำให้ **ทุกอย่างในชิปเปลี่ยนพร้อมกัน** — conductance ของ MOSFET ทุกตัว, threshold voltage ทุกตัว, และ current mirror ทุกตัว เมื่ออุณหภูมิขึ้น ทุกสิ่งเหล่านี้เปลี่ยนไปในทิศทางเดียวกัน (ลดลงสำหรับ NMOS g_m, เพิ่มขึ้นสำหรับ carrier mobility) ถ้าคุณวัด single-ended (voltage เดียวเทียบกับ ground) คุณจะเห็น drift นั้นทั้งหมด

### กลไกจริงๆ

**หลักการ Differential:** แทนที่จะส่งสัญญาณเป็น voltage เดียว V เทียบ ground ให้ส่งเป็น **คู่**: V+ และ V- โดยที่สัญญาณจริงคือผลต่าง:
```
V_signal = V+ - V-
```

ทุกครั้งที่ noise หรือ drift กระทบทั้ง V+ และ V- เท่ากัน (เรียกว่า **common mode**) มันหักล้างในผลต่าง:
```
V_diff = (V+ + noise_cm) - (V- + noise_cm) = V+ - V-
```

temperature drift เป็น common mode เพราะมันกระทบวงจรทุกส่วนพร้อมกัน ถ้า circuit symmetric (V+ และ V- ผ่านวงจรที่เหมือนกัน) drift หักล้างเกือบสมบูรณ์

**CMRR (Common-Mode Rejection Ratio):** วัดว่าดี differential circuit แยก signal จาก common-mode ได้ดีแค่ไหน:
```
CMRR = Differential gain A_d / Common-mode gain A_cm
```

สำหรับ differential pair transistor ง่ายๆ:
- A_d = g_m × R_D (differential signal ถูกขยาย)
- A_cm = -R_D / (2 × R_tail) (common-mode ถูก reject)
- CMRR = g_m × 2 × R_tail

**คันโยก:** R_tail สูง = CMRR สูง นั่นคือเหตุผลที่ **current mirror เป็น tail transistor** (effective R_tail ≈ r_o ของ mirror transistor ซึ่งอาจเป็น MΩ) แทนที่จะใช้ resistor ธรรมดา

**ตัวเลขจริง:** CMRR > 80 dB (10,000×) ทั่วไปสำหรับ op-amp, > 100 dB สำหรับ precision ดังนั้น temperature drift ที่ทำให้ V+ และ V- เปลี่ยน 10 mV พร้อมกัน จะทำให้ output เปลี่ยนแค่ 10 mV / 10,000 = 1 μV

### ผลที่น่าตื่นเต้น

**Differential signaling คือเหตุผลที่ analog precision ทำงานได้เลย** ไม่มี differential pair ก็ไม่มี op-amp ไม่มี op-amp ก็ไม่มี ADC ที่แม่น ทุกวงจรแอนะล็อก precision ตั้งแต่ชิปเสียงไปถึง instrumentation amplifier ใช้หลักการนี้

### สำหรับเรา

**Draft-5 §15 "Differential Pair op-amps" ของคุณทำอันนี้เป๊ะ** นั่นคือทำไมมันอยู่ในสเปก — เป็น fundamental tool สำหรับ temperature rejection ไม่ใช่ "nice to have"

**Fully differential weight:** ถ้า weight ถูก represent เป็น charge differential บน Scap คู่ (V_w+ และ V_w-) temperature shift บน Scap ทั้งคู่หักล้างกัน และ weight accuracy ขึ้นกับ **matching** ระหว่าง Scap สองตัว ไม่ใช่ absolute accuracy ของแต่ละตัว — matching ทำได้ดีกว่า absolute calibration มาก (precision ของ layout สำคัญกว่า process uniformity)

---

## 5 — Chopper Stabilization — กำจัด 1/f และ Offset ในเชิงเวลา

*Enz C.C. & Temes G.C., "Circuit Techniques for Reducing the Effects of Op-Amp Imperfections: Autozeroing, Correlated Double Sampling, and Chopper Stabilization," Proceedings of the IEEE, 84(11):1584–1614, 1996.*

### ปัญหาที่มันแก้

Differential signaling จัดการ common-mode drift ได้ดี แต่ 1/f noise และ **DC offset** ของ amplifier เอง ไม่ใช่ common-mode — มันเกิดจาก mismatch ภายใน amplifier ตัวเดียว เทคนิค differential ไม่ช่วยกับปัญหาภายในของ amplifier เอง

ก่อนปี 1980 วิธีเดียวที่ได้ precision amplifier คือ calibrate ด้วยมือ (ซึ่งแพงและ drift ใหม่ตามอุณหภูมิ) หรือใช้ discrete components คุณภาพสูงมาก (ซึ่งแพงมาก)

### กลไกจริงๆ

**ไอเดียของ chopper:** แทนที่จะต่อ signal เข้า amplifier ตรงๆ ให้ **modulate มันก่อน** ขึ้นไปที่ความถี่ carrier f_c จากนั้น amplify แล้ว **demodulate กลับลงมา**

step by step:

**Step 1 — Input modulation:**
signal s(t) ถูกคูณด้วย square wave c(t) = +1/-1 ที่ f_c (chopper frequency ปกติ 10 kHz–1 MHz)
```
s_mod(t) = s(t) × c(t)
```
ในสเปกตรัมความถี่: signal เดิมที่ baseband ถูก shift ขึ้นไปรอบๆ f_c, 3f_c, 5f_c, ...

**Step 2 — Amplification:**
amplifier ขยาย s_mod(t) ด้วย gain G ในเวลาเดียวกัน amplifier's own noise n_amp(t) (ซึ่งมี 1/f ใหญ่ที่ baseband) ก็ถูกขยายด้วย:
```
output = G × [s_mod(t) + n_amp(t)]
       = G × s(t) × c(t) + G × n_amp(t)
```

**Step 3 — Output demodulation:**
คูณ output ด้วย c(t) อีกรอบ:
```
demod_output = G × s(t) × c(t) × c(t) + G × n_amp(t) × c(t)
             = G × s(t) × 1 + G × n_amp(t) × c(t)
```
เพราะ c(t) × c(t) = 1 เสมอ signal กลับมา baseband แต่ noise ของ amplifier n_amp(t) ถูก modulate ขึ้นไปที่ f_c!

**Step 4 — Low-pass filter:**
กรอง f_c ออก → noise ของ amplifier ถูกกำจัด; signal ที่ clean อยู่ที่ baseband

สรุป: **signal อยู่ที่ f_c ระหว่างขั้นขยาย** (ห่างจาก 1/f region) แต่ **noise ของ amplifier อยู่ที่ baseband** (ซึ่งถูก shift ขึ้น f_c ตอน demodulate) ทั้งสองสิ่งไม่เคยอยู่ที่เดิมพร้อมกัน

**ปัญหาของ chopper — ripple:** เมื่อ DC offset ของ amplifier (V_OS) ถูก modulate ด้วย c(t) มันสร้าง spike ที่ f_c ใน output ก่อน LPF เรียกว่า **chopper ripple** ถ้า LPF ไม่สมบูรณ์ ripple รั่วเข้ามาใน output กลายเป็น error

วิธีแก้ ripple: ใช้ Notch filter ที่ f_c หรือใช้ "chopper with ripple reduction" (amplifier สองขั้นที่ offset สองตัวหักล้างกัน)

### ผลที่น่าตื่นเต้น

Chopper-stabilized op-amp (เช่น LTC2057, ADA4522) ทำได้:
- Offset voltage: **< 1 μV** (เทียบกับ 1–5 mV ของ standard op-amp)
- Offset drift: **< 0.005 μV/°C** (เทียบกับ 1–10 μV/°C)
- 1/f noise corner: **< 1 Hz** (เทียบกับ 1–100 kHz)

นั่นคือ improvement 1000× ใน offset และ drift โดยแทบไม่ต้องเพิ่ม die area มาก

### สำหรับเรา

สำหรับ op-amp ใน crossbar ที่ทำ summation บน weight ถ้าต้องการ precision สูง chopper คือทางเลือก **แต่มี tradeoff สำคัญ:**

- chopper ต้องการ clock (f_c generator) → เพิ่ม complexity และ power
- ripple ต้องการ LPF → เพิ่ม latency
- เหมาะกับงานที่ precision สำคัญกว่า speed (เช่น weight update ใน training loop ที่ช้า)
- ไม่เหมาะกับ inference ที่ต้องการ fast throughput

**draft-5 §15 mention "Auto-Zeroing" แต่ chopper และ auto-zero ใช้ได้ทั้งคู่** และ complement กัน: chopper ดีกว่าสำหรับ low-frequency, wide-bandwidth แต่สร้าง ripple; auto-zero ดีกว่าสำหรับ narrowband และ burst sampling (ดูหัวข้อถัดไป)

---

## 6 — Auto-Zeroing — วัด offset แล้วลบ

*ใน Enz & Temes 1996 เดียวกัน; ดูเพิ่มเติมใน Johns & Martin, "Analog Integrated Circuit Design," 1997*

### กลไกจริงๆ

Auto-zeroing ทำงานเป็นสองเฟสสลับกัน:

**เฟส 1 — Auto-zero phase:**
- ตัด input จาก signal จริง
- ต่อ input ของ amplifier เข้า reference (หรือ short ทั้งสอง)
- วัด output ของ amplifier — output นี้คือ offset ที่ขยายแล้ว: V_out = G × V_OS
- เก็บ correction voltage V_corr = -V_OS บน **storage capacitor C_az** (capacitor เล็กๆ ภายใน)
- ทำในเวลาสั้น (เช่น 1 μs)

**เฟส 2 — Signal amplification phase:**
- ต่อ signal จริงเข้า input
- บวก V_corr จาก C_az เข้ากับ output (หรือ input minus)
- V_corrected_out = G × (V_signal + V_OS) - G × V_OS = G × V_signal
- offset ถูก subtract ออก!

**Residual offset:** offset ที่เหลือหลัง auto-zero คือ:
1. **kT/C noise บน C_az** — เมื่อ charge บน C_az ถูก sample ด้วย switch มี noise √(kT/C_az) ติดมาด้วย ยิ่ง C_az ใหญ่ ยิ่ง residual offset น้อย
2. **Drift ใน signal phase** — ถ้า offset drift เร็วมาก (ซึ่งปกติไม่เป็น) correction เริ่มผิด แก้ด้วยการ refresh บ่อยขึ้น

**Correlated Double Sampling (CDS):** เป็น auto-zero ที่ใช้กันทั่วไปใน CCD/CMOS image sensor — sample noise/offset ใน "dark phase" แล้วลบจาก "signal phase" ทุกๆ pixel clock

### ผลที่น่าตื่นเต้น

LTC1050 (auto-zero op-amp คลาสสิก):
- Offset: **< 5 μV**
- Drift: **< 0.05 μV/°C**

Modern auto-zero op-amp (MAX4238):
- Offset: **< 0.3 μV**
- Drift: **< 0.003 μV/°C** (แทบเป็นศูนย์)

ที่น่าสนใจ: auto-zero ไม่ต้องการ external chopper clock — ใช้ internal switching sequence ที่ sync กับ system clock ได้โดยตรง

### สำหรับเรา

**draft-5 §15 "Auto-Zeroing" ของคุณคืออันนี้เป๊ะ** — เป็น mechanism ที่ถูกที่สุดสำหรับชิปที่มี **duty cycle** (เพราะ auto-zero phase กินเวลา)

สำหรับชิปของคุณ: ถ้า crossbar ทำ MVM (matrix-vector multiply) ใน bursts (ไม่ใช่ continuous streaming) ให้แทรก auto-zero phase ระหว่าง burst — ทุกๆ N MVM ทำ auto-zero ครั้งหนึ่ง residual offset จะต่ำมาก และ overhead ตามสัดส่วน: 1 auto-zero cycle ต่อ N MVM cycles

---

## 7 — Dummy / Reference Cell — ฝาแฝดที่ drift ไปด้วยกัน

### กลไกจริงๆ

ไอเดียง่ายมากแต่ทรงพลัง: สร้าง **dummy Scap** ที่:
- อยู่ในพื้นที่เดิมของชิป (thermal environment เดียวกัน)
- เห็น input ที่ **รู้ค่า** (เช่น reference voltage V_ref) แทน signal จริง
- connected ในวิธีเดียวกันกับ Scap จริง

เมื่อ temperature เปลี่ยน dummy Scap และ Scap จริงต่าง **drift ไปในทิศทางเดียวกันเกือบเท่ากัน** เพราะอยู่ใกล้กันในชิป

ถ้าเอา output ของ dummy Scap มาลบจาก output ของ Scap จริง:
```
V_corrected = V_real - V_dummy
            = (V_signal + drift) - (V_ref + drift)
            = V_signal - V_ref
```

drift หายไป! เหลือแค่ผลต่างระหว่าง signal และ reference

**ตัวเลข matching:** สำหรับ Scap คู่ที่อยู่ใกล้กันในชิป (ระยะห่าง < 50 μm) temperature matching อยู่ที่ ~0.01°C → drift mismatch ต่ำมาก สำหรับ Scap ที่ห่างกัน (ข้ามชิป) mismatch อาจถึง 1–2°C → ต้องระวัง layout

### สำหรับเรา

**draft-5 §15 "Dummy Scap" ของคุณคืออันนี้เป๊ะ** และ **"Current Mirror" (§22 #13)** ก็ทำงานด้วยหลักการเดียวกัน — MOSFET สองตัวที่ match กันดี drift ไปด้วยกัน ratio ของ current ยังคงที่

> **ดังนั้นปัญหาอุณหภูมิของคุณ แก้ไปแล้วสามในสี่ส่วนใน draft-5 ของคุณเอง:** Differential pair + auto-zero + dummy cell คือ "สามเสาหลัก" ในการจัดการ drift ช้า และคุณสเปกทั้งสามไว้เองโดยอิสระ ทฤษฎีข้างบนแค่บอก *ว่าทำไม* มันเวิร์ก: noise ช้าเป็น common-mode และลบได้

---

## 8 — noise เร็ว (kT/C): สามลูกบิดที่คุณมี

กลับมาที่ kT/C noise — ลูกบิดสามตัว:

### ลูกบิด 1: C ใหญ่ขึ้น

```
V_noise = √(kT/C)
```

ทุกๆ C เพิ่มขึ้น 4× = noise ลด 2× (6 dB)

**Trade-off:**
- พื้นที่เพิ่ม linear กับ C
- เวลาชาร์จ RC เพิ่ม linear กับ C (ถ้า R คงที่)
- bandwidth ลดลง (pole ต่ำลง)

**กลยุทธ์ที่เหมาะสม:** ไม่ต้องให้ Scap ทุกตัวมีขนาดเท่ากัน ให้ **weight ที่ precision สำคัญ** (เช่น weight ใน GD layer ที่ต้องแม่นยำสำหรับ class boundary) มี C ใหญ่ ส่วน **weight ใน SCFF** (ที่ noise เป็น regularization — เทียบกับ Bishop ใน `17`) มี C เล็กได้ ประหยัดพื้นที่มาก

### ลูกบิด 2: เฉลี่ยตามเวลา (Integration / Low-pass filtering)

noise เร็ว random เฉลี่ยเป็นศูนย์เมื่อ integrate นานพอ ถ้า integrate เป็นเวลา T:
```
V_noise_rms ∝ 1/√(T × Bandwidth)
```

**Settle time ในวงลูปแอนะล็อก:** การ settle ลงสู่ equilibrium (**`3-recurrence.md`**) คือการ integrate นี้โดยอัตโนมัติ ยิ่ง settle นาน noise ยิ่งน้อย แต่ latency สูงขึ้น

**Trade-off speed vs. noise:** นี่คือ trade-off พื้นฐานของ analog inference ต่อ weight update step ต้องการ noise ต่ำแค่ไหน?

### ลูกบิด 3: เฉลี่ยตามสำเนา (Population Coding / Redundancy)

N Scap ที่ noise อิสระ เฉลี่ย output:
```
V_noise_aggregate = V_noise_single / √N
```

นี่คือ **population coding ของสมอง** (ดู von Neumann multiplexing ใน `17`) และ **randomized smoothing** ของ Cohen — หลักการเดียวกันในสามบริบท

**ตัวอย่างตัวเลข:**
- N = 4: noise ลด 2× (−6 dB) ด้วย area เพิ่ม 4×
- N = 9: noise ลด 3× (−9.5 dB) ด้วย area เพิ่ย 9×
- N = 16: noise ลด 4× (−12 dB) ด้วย area เพิ่ม 16×

**สมองใช้ N หลายร้อยถึงหลายพัน** neurons ต่อ representational unit → noise ต่ำมาก แม้แต่ละ neuron มี noise สูง

**ผลพลอยได้:** N สำเนาต่อ weight ยังให้ fault tolerance — ถ้า Scap ตัวหนึ่งเสีย (stuck-at-0 หรือ stuck-at-1) ผลรวมยังดีอยู่ ลดด้วย (N-1)/N เท่านั้น

---

## 9 — Noise-Aware Training (Variation-Aware Training) — ฝั่งซอฟต์แวร์

*Jain et al., "Compensating Hardware Imperfections in Analog Neural Networks," 2020; Guo et al., "Survey on noise-aware training for analog in-memory computing," 2022; Nandakumar et al., "Mixed-precision deep learning for RRAM crossbar," 2020.*

### ปัญหาที่มันแก้

งาน analog in-memory computing ก่อน ~2018 train ตาข่ายบน GPU (เหมือนตาข่ายปกติ) แล้ว deploy weight ลงบนชิป analog ผลคือ catastrophic: accuracy ที่ train ได้ 95% drop เหลือ 60–70% เมื่อ deploy เพราะ weight noise, device variation, และ IR drop ทำให้ MVM ผิดพลาด

คำถาม: *ถ้าเราฝึก model ให้ "รู้จัก" noise ของ hardware ตัวเองล่วงหน้าล่ะ?*

### กลไกจริงๆ

**Stochastic weight perturbation training:**

ขณะ train สำหรับแต่ละ weight `w_ij` แทนที่จะใช้ `w_ij` ตรงๆ ให้ sample:
```
w_ij_noisy = w_ij + ε_ij    โดย ε_ij ~ N(0, σ_device²)
```

โดย `σ_device²` คือ **variance ของ noise ที่วัดได้จาก hardware** (จาก characterization) ใช้ `w_ij_noisy` ใน forward pass แต่ update `w_ij` (mean) ใน backward pass

**สิ่งที่เกิดขึ้น:**
- gradient เป็น: `∂L/∂w_ij = E_ε[∂L/∂(w_ij + ε_ij)]`
- ตามทฤษฎีบทของ Bishop (`17`): นี่เทียบเท่ากับ Tikhonov regularization บน `w_ij`
- weight ที่ออกมาจึงเป็น **weight ที่เรียบ** — ไม่ไวต่อ perturbation ขนาด `σ_device`
- เมื่อ deploy บน hardware จริงที่มี noise `σ_device` performance จึงยังดี

**Inject noise หลายแบบ:**
- Weight noise: `w + ε_w ~ N(0, σ_w²)` — จำลอง kT/C noise และ device variation
- Activation noise: `a + ε_a ~ N(0, σ_a²)` — จำลอง ADC noise
- Quantization: round weight ไป fixed levels — จำลอง limited precision storage

สามารถ inject ทั้งหมดพร้อมกัน เพราะ hardware จริงมีทั้งสามพร้อมกัน

### ผลที่น่าตื่นเต้น

กลุ่มทดสอบบน CIFAR-10 กับ ResNet-18:
- **ไม่ใช้ noise-aware training + 15% weight noise:** accuracy จาก 93% → 68% (−25%)
- **ใช้ noise-aware training (inject 15% noise ตอน train) + 15% weight noise:** accuracy จาก 93% → 90.5% (−2.5% เท่านั้น)

นอกจากนี้ team Nandakumar (EPFL) แสดงบน RRAM crossbar จริงๆ:
- ก่อน noise-aware training: 91% → 71% เมื่อ deploy บน RRAM
- หลัง noise-aware training: 91% → 88% — retain 97% ของ accuracy

**ขีดจำกัดที่ค้นพบ:** ถ้า noise สูงเกิน σ ≈ 30% ของ full weight range noise-aware training ยังช่วยได้บ้างแต่ accuracy ยังตก อันนี้บอกว่ามี "noise budget" ที่ hardware ต้องรักษาไว้ ไม่สามารถ compensate software ได้ทั้งหมด

**ที่น่าประหลาดใจ:** noise-aware training ยัง **improve generalization บน clean data** ด้วย ไม่ใช่แค่ maintain accuracy บน noisy hardware — Bishop's theorem ทำนายสิ่งนี้: noise ระหว่างเทรน = regularization ทุก test condition จึงดีขึ้น

### สำหรับเรา — นี่คือ "แก้ในซอฟต์แวร์ เก็บฮาร์ดแวร์ให้เร็วและสะอาด"

**การแบ่งงานที่ถูกต้อง:**

| Layer | จัดการ noise ชนิดใด | ด้วยอะไร |
|-------|---------------------|----------|
| **วงจร** | drift ช้า (อุณหภูมิ, 1/f, offset) | differential, chopper, auto-zero, dummy cell |
| **วงจร** | kT/C ตรงที่สำคัญ | C ใหญ่ขึ้น + เฉลี่ย |
| **สถาปัตยกรรม** | noise propagation ข้ามชั้น | residual (edge-of-chaos), Scap ซ้ำสำรอง |
| **Training** | device variation ที่เหลือ | inject noise ตอน train → Bishop theorem |

**สามชั้นนี้ complement กัน:** วงจรฆ่า drift ช้า (ถูกกว่าในซิลิคอน); สถาปัตยกรรมจำกัดการขยาย noise ข้ามชั้น (ฟรีจาก residual); training เก็บกวาด residual variation ที่เหลือด้วย regularization (ฟรีจาก Bishop) ไม่ต้องทำให้ hardware สมบูรณ์แบบ ทำให้มัน **เร็วและหยาบ** แล้วให้ software ทำงานของมัน

**สำหรับ simulator:** เมื่อ simulate behavioral model ควร inject noise จำลองด้วยตั้งแต่ต้น ไม่ใช่ test หลัง train ถ้า inject แล้ว simulate กับ weight ที่ train แบบ noise-aware → accuracy จะสูงกว่า train แบบ clean แล้ว add noise ทีหลัง อย่างมีนัยสำคัญ

---

## รูปร่างของคำตอบ (ไฟล์นี้)

กุญแจเชิงแนวคิดที่คุณขาด: **จำแนก noise ตาม timescale แล้วการแก้ก็ถูกบังคับ**

**noise ช้า (อุณหภูมิ, 1/f, offset, drift) คุณ SUBTRACT ออก** เทียบกับ reference:
- **Differential / common-mode rejection** — อุณหภูมิเป็น common-mode → หักล้างในผลต่าง CMRR > 80 dB ทั่วไป คุณต้องการ fully-differential weight representation
- **Chopper stabilization** — modulate signal ขึ้นไปที่ f_c > 1/f region, amplify, demodulate กลับ → 1/f และ offset ถูกกำจัด เหมาะกับ low-speed precision (weight update), ไม่เหมาะกับ fast inference
- **Auto-zeroing** — วัด offset ใน auto-zero phase, subtract ใน signal phase → offset ลงถึง < 1 μV ด้วย overhead ต่ำ เหมาะกับ duty-cycled operation
- **Dummy / reference cell** — ฝาแฝดที่ drift เหมือนกัน → ลบ drift ออก ต้องการ layout ที่ symmetric และ close

**ปัญหาอุณหภูมิของคุณคืออันนี้ และ draft-5 §15 ของคุณสเปกสามในสี่กลไกไว้แล้ว** — คุณออกแบบทางแก้ไว้ก่อนรู้ทฤษฎี

**noise เร็ว (kT/C thermal — ตัวตลอดกาลของ capacitor-weight) คุณ AVERAGE ออก:**
- **C ใหญ่ขึ้น** (`V_noise = √(kT/C)`) — ลูกบิดตรงที่สุด แลกพื้นที่กับ noise ด้วย 1/√C ไม่จำเป็นต้องทำเท่ากันทุก Scap — weight precision-critical ได้ C ใหญ่, ที่เหลือ C เล็ก
- **Integration time ยาวขึ้น** — การ settle ของ analog dynamics ของคุณทำอันนี้ในตัว ยิ่ง settle นาน noise ยิ่งต่ำ
- **N สำเนา** — population coding / von Neumann multiplexing → noise ลด √N fault tolerance ฟรี

**กาวยุคใหม่: noise-aware training** — inject noise จำลอง hardware ใน simulator ระหว่างเทรน → weight เรียน weight ที่ทนต่อ noise เฉพาะนั้น bishop theorem พิสูจน์ว่ามันคือ regularization ฟรีด้วย hardware accuracy 88–90% ที่ deploy บน RRAM จริงๆ (เทียบกับ 71% ถ้าไม่ทำ)

**สามชั้น — วงจร → สถาปัตยกรรม → training** ทำงานร่วมกัน ไม่ใช่ทดแทนกัน hardware ไม่ต้องสมบูรณ์ ต้องพอดี "noise budget" แค่นั้น
