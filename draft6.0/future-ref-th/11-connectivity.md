# 11 — อินพุตโลคอล + การผสม: เรื่องราวทั้งหมดของการแบ่งงาน

> ไฟล์นี้ตอบคำถามที่ draft-5 ตั้งไว้ว่า "แต่ละบล็อกเห็นแค่เสี้ยวเดียวได้ไหม?" — คำตอบคือใช่ และมีชื่อเรียก กลไกเบื้องหลัง ตัวเลขจริง และวิธีผสมที่ดีกว่า translate clip แบบ dense

---

## บทนำ: ปัญหาที่ทำให้ทุกอย่างในไฟล์นี้เกิดขึ้น

ลองนึกภาพเลเยอร์เดียวที่รับ input 512 channels ออก 512 channels ถ้าทำแบบ dense — เชื่อมทุก input เข้ากับทุก output — ต้องมี 512 × 512 = **262,144 weights** ต่อหนึ่งเลเยอร์ สำหรับ image ขนาด 224×224 ที่มี filter 3×3 คูณออกมาคือ 2.4 ล้าน parameters ต่อเลเยอร์เดียว

คำถามที่วงการถามคือ: จำเป็นไหม? feature ใน channel 1 ต้องรู้เรื่อง channel 400 จริงๆ ไหม? หรือว่าส่วนใหญ่ความรู้ที่ useful อยู่ภายใน "กลุ่ม" channels ที่เกี่ยวข้องกัน?

คำตอบที่วงการค้นพบ: ส่วนใหญ่ ไม่ต้อง — และนี่คือหัวใจของไฟล์ทั้งไฟล์

---

## บทที่ 1: AlexNet (2012) — ความบังเอิญที่กลายเป็นหลักการ

### เรื่องราวที่คนลืมเล่า

Krizhevsky, Sutskever และ Hinton สร้าง AlexNet เพื่อ challenge ILSVRC 2012 สถาปัตยกรรมมี 5 conv layers + 3 fully-connected layers — ใหญ่มากในยุคนั้น ปัญหาคือ GPU ที่ดีที่สุดในปี 2012 (NVIDIA GTX 580) มี VRAM แค่ 3GB model ใหญ่เกินกว่าที่ GPU เดียวจะรับได้

การแก้ปัญหา: **แบ่ง** model ออกเป็นสองซีก ใช้ GPU สองตัว แต่ละตัวถือ feature maps "ครึ่งหนึ่ง" ทำ convolution บน channels ของตัวเองโดยไม่ต้อง communicate ข้าม GPU ยกเว้นที่ layers บางตัวที่เลือกไว้

นั่นคือ **grouped convolution** โดยบังเอิญ ไม่ใช่ design choice

สิ่งที่น่าตื่นเต้นกว่า: มันไม่แค่ "แก้ปัญหา" memory — accuracy **ดีขึ้นด้วย** เมื่อเทียบกับ single-GPU baseline ที่เล็กกว่า เหมือนว่าการบังคับให้ each half specialize แทนที่จะให้ทุก channel รู้ทุกอย่าง ทำให้ model เรียนได้ดีกว่า

### กลไกที่แท้จริง — ตัวเลขทุกตัว

Standard conv ที่เชื่อม `C_in` channels เข้า `C_out` channels:
- Parameters: `C_in × kernel_size × C_out`
- สำหรับ C_in=C_out=C, 3×3 kernel: `9C²`

**Grouped conv ด้วย g groups:**
- แบ่ง input channels เป็น g กลุ่ม: กลุ่มละ `C/g` channels
- แบ่ง output channels เป็น g กลุ่ม: กลุ่มละ `C/g` channels
- กฎเหล็ก: output group j เห็น **เฉพาะ** input group j เท่านั้น
- Parameters ต่อกลุ่ม: `(C/g) × 9 × (C/g)` = `9C²/g²`
- Parameters รวม g กลุ่ม: `g × 9C²/g²` = **`9C²/g`** — ถูกกว่า dense g เท่า

ตัวอย่างรูปธรรม (C=512):
```
Dense:       9 × 512² = 2,359,296 weights
g=2:         9 × 512²/2 = 1,179,648 weights   (ถูกกว่า 2×)
g=8:         9 × 512²/8 = 294,912 weights      (ถูกกว่า 8×)
g=32 (ResNeXt-style): 9 × 512²/32 = 73,728   (ถูกกว่า 32×)
```

สำหรับ AlexNet ใช้ g=2 บน layers แรก บาง layers ใช้ g=1 (fully connected ข้าม GPU) ผลลัพธ์: model เต็มใน VRAM สองตัวรวม 6GB แทนที่จะต้องการ 6GB ตัวเดียว

### ผลลัพธ์จริง

AlexNet ชนะ ILSVRC 2012 ด้วย top-5 error **15.3%** เทียบกับ runner-up ที่ **26.2%** ห่างกัน 11% — margin นี้ไม่เคยเกิดขึ้นในประวัติศาสตร์ competition และทำให้ deep learning กลายเป็นกระแสหลักของทั้งวงการ

### สำหรับเรา

Grouped conv บน analog crossbar หมายถึง: แทนที่จะสร้าง crossbar ขนาด `n×m` ชิ้นเดียวใหญ่ (interconnect มาก สร้างยาก area ใหญ่) เราสร้าง `g` crossbar ขนาด `(n/g)×(m/g)` วางคู่กัน พื้นที่รวมถูกกว่า g เท่า — นั่นคือพลังงานของ Ganglion block architecture ที่คุณคิด เป็น grouped conv ทางกายภาพตรงๆ

---

## บทที่ 2: ResNeXt (2017) — เมื่อ "ความหลากหลาย" ดีกว่า "ความกว้าง"

### เรื่องราว

หลัง ResNet (2015) ทุกคนรู้ว่า depth ช่วย แต่คำถามคือ "ถ้าจะเพิ่ม capacity โดยไม่เพิ่ม depth หรือ parameter count จะทำได้ไหม?" Xie et al. ที่ Facebook Research ดูที่ Inception module (GoogLeNet) ซึ่งมีหลาย "paths" parallel กัน แล้วถามว่า "เราจะทำให้ simple กว่านี้ได้ไหม?"

แนวคิดหลัก: เพิ่ม **cardinality** (จำนวน parallel paths) แทนที่จะเพิ่ม depth หรือ width ทดลองแล้วพบว่า: "doubling cardinality is more effective than doubling width or depth at the same parameter budget"

### กลไกที่แท้จริง

ResNeXt block มี C parallel branches (C คือ cardinality) แต่ละ branch ทำงานเหมือน bottleneck ResNet block แต่เล็กกว่า:

```
Input (256 channels)
  ├── Branch 1:  256 → 4 → 4    (bottleneck width 4)
  ├── Branch 2:  256 → 4 → 4
  ├── Branch 3:  256 → 4 → 4
  │   ... (C=32 branches รวม)
  └── Branch 32: 256 → 4 → 4
      ↓
  Concatenate: 32 × 4 = 128 channels
      ↓
  1×1 conv: 128 → 256
      ↓
  + Residual skip
Output (256 channels)
```

ด้วย C=32, bottleneck=4: parameter count = 32 × (256×4 + 4×9 + 4×256) ≈ เท่ากับ ResNet ที่มี bottleneck=64 แต่ accuracy ดีกว่า

ทำไม? ทฤษฎีว่า: การ optimize หลาย paths น้อยๆ ง่ายกว่า path เดียวใหญ่ แต่ละ branch มี gradient flow ที่ชัดเจน ไม่รบกวนกัน และ paths หลายอันสร้าง natural ensemble effect

นอกจากนี้: grouped conv และ ResNeXt **เทียบเท่ากันในเชิงคณิตศาสตร์** ResNeXt paper แสดงว่า C parallel branches × bottleneck B = grouped conv ที่มี g=C, width=B คือ formulation เดียวกัน

### ผลลัพธ์จริง

ResNeXt-101 (cardinality=32, bottleneck=4d):
- Top-1 error บน ImageNet: **20.4%** เทียบกับ ResNet-101: **22.0%**
- ที่ parameter count เกือบเท่ากัน (~44M vs ~44M)
- ชนะ ILSVRC 2016 object detection

### สำหรับเรา

Cardinality ใน ResNeXt = จำนวน Ganglion ที่ parallel กันใน layer ของคุณ แทนที่จะมี Ganglion ใหญ่ตัวเดียวที่รู้ทุกอย่าง มีหลายตัวที่แต่ละตัว specialize ต่างกัน — แล้วผสม ทฤษฎีบอกว่าที่ parameter count เท่ากัน แบบ multi-path ดีกว่า single-path ข้อนี้ support การใช้หลาย Ganglion แทน Ganglion ใหญ่ตัวเดียว

---

## บทที่ 3: MobileNet + Xception (2017) — แยก "ที่ไหน" กับ "อะไร" ออกจากกัน

### เรื่องราว

Chollet ที่ Google Brain (Xception paper) และ Howard et al. (MobileNet paper) มาถึงที่เดียวกันในปีเดียวกัน: ใน standard convolution เราทำ **สองอย่างพร้อมกัน** ซึ่งไม่จำเป็น

- **อย่างที่ 1: Spatial filtering** — หาว่า pattern อยู่ตรงไหนใน 2D space (ความสัมพันธ์ใน spatial dimension)
- **อย่างที่ 2: Channel mixing** — รวม features จาก channels ต่างๆ เข้าด้วยกัน

คำถาม: ต้องทำพร้อมกันไหม? คำตอบ: **ไม่ต้อง** และการแยกมันลดต้นทุนลง ~8-9 เท่า

### กลไกที่แท้จริง — ทีละก้าว

**Standard 3×3 conv** (C channels → C channels, filter 3×3):
```
Weight: C × (3×3) × C = 9C²  parameters
FLOPs ต่อ output position: 9C² multiply-adds
```

**Depthwise Separable** แบ่งเป็น 2 steps:

**Step 1 — Depthwise Conv (3×3):**
```
Rule: 1 filter ต่อ 1 input channel ไม่มี cross-channel mixing
Weight: C × (3×3) × 1 = 9C   parameters  (แทน 9C²!)
```
แต่ละ channel ถูก filter ด้วย filter ของตัวเอง แต่ channels ไม่ได้ "คุยกัน" เลย output ยังคง C channels แต่ filtered แล้ว

**Step 2 — Pointwise Conv (1×1):**
```
Rule: filter ขนาด 1×1 (ไม่มี spatial extent) ผสม channels
Weight: C × 1 × C = C²   parameters
```
ผสม channels เข้าด้วยกัน **ที่ spatial position เดิม** ไม่มีการ spatial filter เพิ่มเติม

**ประหยัดทั้งหมด:**
```
Standard:          9C²
Depthwise + Pointwise: 9C + C² = C(9 + C)

ประหยัด = 9C² / C(9+C) ≈ 9C / (9+C) ≈ C/1  สำหรับ C >> 9
```

ตัวอย่าง C=512:
```
Standard:               9 × 512² = 2,359,296 weights
Depthwise separable:    9×512 + 512² = 4,608 + 262,144 = 266,752 weights
ถูกกว่า: 2,359,296 / 266,752 = 8.85 เท่า
```

### ตัวอย่างรูปธรรม — RGB image 4×4

สมมติ input เป็น RGB 4×4:

**Step 1 (Depthwise):**
```
Channel R: กรอง R ด้วย filter_R (3×3) → R_filtered  (local R pattern)
Channel G: กรอง G ด้วย filter_G (3×3) → G_filtered  (local G pattern)
Channel B: กรอง B ด้วย filter_B (3×3) → B_filtered  (local B pattern)

ผล: ยังคง 3 channels แต่ filtered แล้ว ยังไม่มี cross-channel info
```

**Step 2 (Pointwise):**
```
แต่ละ position (x, y):
  ผสม [R_filtered, G_filtered, B_filtered] → [ch_out_0, ch_out_1, ..., ch_out_N]
  ใช้ 1×1 weight ที่มี N output channels

ผล: N channels ที่ผสม R, G, B เข้ากันแล้ว แต่ไม่มี spatial filtering เพิ่ม
```

นี่คือ "Ganglion (local per channel) → translate clip (mix across channels)" ของคุณ เป็น depthwise separable ตรงๆ

### ผลลัพธ์จริง

MobileNet v1 บน ImageNet:
- Top-1 accuracy: **70.6%** เทียบกับ VGG16: **71.5%**
- Parameters: **4.2M** เทียบกับ VGG16: **138M** — เล็กกว่า **33 เท่า**
- Computation: **569M FLOPs** เทียบกับ VGG16: **15,300M FLOPs** — เร็วกว่า **27 เท่า**
- Accuracy ลดแค่ **~1%** แต่ size และ speed ต่างกัน 27-33 เท่า

นี่คือ trade-off ที่ทำให้ deep learning รันบนมือถือได้ ทั้ง Google Photos, Face Unlock, Siri ใช้สถาปัตยกรรมแบบนี้

### สำหรับเรา

บน analog crossbar:
- **Depthwise = crossbar เล็กๆ หนึ่งตัวต่อ channel group** ขนาด kernel_size × 1 (ถ้า 1D) หรือ K×K × 1 (ถ้า 2D spatial)
- **Pointwise = crossbar ขนาด C × C_out** ทำ channel mixing ที่ spatial position เดียว

ต้นทุน crossbar รวม: C × (K²) + C × C_out ≈ ถูกกว่า standard crossbar ขนาด K²C × C_out อยู่ ~C/K² เท่า สำหรับ C=512, K=3 คือ ถูกกว่า ~57 เท่า ซึ่งเป็นตัวเลขที่ใหญ่มากในแง่ chip area

---

## บทที่ 4: ShuffleNet (2017) — ผสมได้โดยไม่ต้องคำนวณ

### เรื่องราว

Zhang et al. ที่ Megvii ต่อยอดจาก MobileNet แต่เจอปัญหา: pointwise conv (1×1) ที่ทำ channel mixing ใช้ C² weights — ถ้า C ใหญ่นี่ยังแพงมาก ไม่ใช่ตัวใหญ่แต่ถ้า optimize ทุกอย่างก็ยังเป็น bottleneck

พวกเขาสังเกตเห็นปัญหาอีกอย่าง: ถ้าใช้ grouped conv หลาย layers ติดกัน และ groups ไม่เคย "คุยกัน" เลย model จะกลายเป็น g ตาข่ายอิสระที่แยกขาดจากกัน ซึ่งสูญเสีย expressivity ไปมาก

คำถาม: มีวิธีผสม information ข้าม groups โดยไม่ต้องใช้ dense 1×1 conv ไหม?
คำตอบ: **Channel Shuffle** — ฟรีโดยสมบูรณ์

### กลไกที่แท้จริง — Channel Shuffle ทีละขั้ว

สมมติมี output จาก grouped conv: 12 channels จาก 3 groups (แต่ละ group 4 channels)

**Before shuffle:**
```
[Group 0: ch 0, 1, 2, 3] [Group 1: ch 4, 5, 6, 7] [Group 2: ch 8, 9, 10, 11]
→ flatten: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
```

**Reshape เป็น matrix (g × C/g):**
```
Row 0 (Group 0): 0  1  2  3
Row 1 (Group 1): 4  5  6  7
Row 2 (Group 2): 8  9  10 11
```

**Transpose matrix:**
```
Col 0: 0  4  8
Col 1: 1  5  9
Col 2: 2  6  10
Col 3: 3  7  11
```

**Flatten:**
```
[0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11]
```

**หลัง shuffle:** channel 1 (เดิมอยู่ Group 0) อยู่ถัดจาก channel 4 (เดิมอยู่ Group 1) ตอนทำ grouped conv ครั้งถัดไป พวกมันอยู่ใน group เดียวกัน → interact กันได้

ทำ shuffle สองสามครั้งข้ามหลาย layers → ทุก channel ได้ interact กับทุก channel อื่นผ่านห่วงโซ่ของ group interactions

**ต้นทุน:** ศูนย์ทาง arithmetic (แค่ memory access pattern ต่างกัน ไม่มี multiply-add เพิ่ม)

### ShuffleNet v2 (2018) — ต่อยอดด้วย Channel Split

ไม่ใช่แค่ shuffle แต่ **channel split**: แบ่ง input เป็นสองส่วน ส่วนหนึ่ง pass ตรง (residual) อีกส่วนผ่าน transform แล้ว concatenate แล้ว shuffle

```
Input (C channels)
  → Split เป็น [C/2 ซ้าย] [C/2 ขวา]
                    ↓              ↓
            (identity)     1×1 → DW 3×3 → 1×1
                    ↓              ↓
                  Concat (C channels)
                    ↓
                  Shuffle
```

ทำไมดีกว่า: ส่วน identity ทำหน้าที่เป็น gradient highway (เหมือน ResNet skip) ทำให้ training มั่นคงกว่า ขณะที่ส่วน transform สร้าง new features

### ผลลัพธ์จริง

ShuffleNet v2 1x (C=116):
- ImageNet top-1: **69.4%**
- MFLOPs: **146** (เทียบกับ MobileNet v2 ที่ให้ accuracy ใกล้เคียงกันด้วย **300 MFLOPs**)
- ถูกกว่า **2 เท่า** ที่ accuracy เดียวกัน — เพราะเอา channel shuffle มาแทน 1×1 group conv บางส่วน

### สำหรับเรา

Translate clip ของคุณ — เอา output จาก Ganglia ทั้งหมดมาผสม — ถ้าทำเป็น dense 1×1 conv ต้องใช้ crossbar ขนาด C×C (C² paths แพงมาก)

**Channel shuffle = routing ตายตัว บน analog hardware:**
- ไม่มี crossbar เพิ่ม
- แค่ hardwired permutation ของ output lines
- ไม่กิน charge ไม่กิน settle time ไม่มี ALU operation ใดๆ
- ทำ 2-3 ครั้ง → information กระจายทั่วทุก Ganglion ใน 2-3 layers

กฎปฏิบัติ: อย่าสร้าง dense translate clip ก่อน ลอง channel shuffle + stack ก่อน ถ้า task ง่ายพออาจพอแล้ว

---

## บทที่ 5: Butterfly / Monarch Matrices (2019/2022) — log(n) คือ optimal

### เรื่องราว

Dao et al. ที่ Stanford ตั้งคำถามว่า: "FFT เร็วกว่า DFT ธรรมดา O(n²) เป็น O(n log n) ได้ เพราะอะไร? และหลักการนั้นใช้กับ neural network ได้ไหม?"

คำตอบ: FFT เร็วเพราะ DFT matrix มี **โครงสร้าง butterfly** — สามารถ factorize เป็น log(n) "ขั้น" ของการผสมขนาดเล็กที่วางซ้อนกัน แต่ละขั้น sparse ปัญหาของ dense weight matrices ใน ML คือส่วนใหญ่มีโครงสร้างแบบนี้ด้วย — เราแค่ไม่ได้ exploit มัน

**Butterfly matrices (2019):** กรอบทั่วไปที่พิสูจน์ว่า dense matrices หลาย classes สามารถ factorize เป็น log(n) sparse factors ที่ multiply ซ้อนกัน

**Monarch matrices (2022):** ทำให้ practical กว่า: dense matrix ≈ B × P × B โดย B = block-diagonal, P = permutation matrix และ B, P เหล่านี้ **learnable** ไม่ใช่ตายตัว

### กลไกที่แท้จริง — FFT เป็นตัวอย่างของ butterfly

DFT ของ vector ขนาด 8 ต้องการ 8×8=64 complex multiply-adds ถ้าทำ naive

FFT ทำใน **3 ขั้น** (log₂8=3):

```
ขั้นที่ 1: ผสม pairs ห่างกัน 4:
  [a₀,a₁,a₂,a₃,a₄,a₅,a₆,a₇]
  pair: (a₀,a₄), (a₁,a₅), (a₂,a₆), (a₃,a₇) — 4 butterfly ops จิ๋ว

ขั้นที่ 2: ผสม pairs ห่างกัน 2:
  [X₀,X₁,X₂,X₃,X₄,X₅,X₆,X₇]
  pair: (X₀,X₂), (X₁,X₃), (X₄,X₆), (X₅,X₇) — 4 butterfly ops

ขั้นที่ 3: ผสม adjacent pairs:
  pair: (Y₀,Y₁), (Y₂,Y₃), ... — 4 butterfly ops
```

รวม: 3 ขั้น × 4 ops = **12 operations** แทน 64 — **ถูกกว่า 5.3 เท่า ที่ n=8**

ที่ n=1024: 1024² = 1,048,576 vs 1024×10 ≈ 10,240 — **ถูกกว่า ~100 เท่า**

**Butterfly matrix สำหรับ n=8:**

แต่ละขั้นคือ sparse matrix ขนาด 8×8 ที่มีแค่ 2 ค่าต่อ row (ที่เหลือเป็น 0) เมื่อ multiply 3 matrices ซ้อนกัน ผลเท่ากับ DFT matrix เต็มๆ แต่ทำได้เร็วกว่ามาก

**Monarch matrices** ขยายนี้ให้ general: แทนที่จะ factorize fixed FFT butterfly ใช้ **learned** block-diagonal matrices:

```
Dense W (n×n) ≈ B₁ × P × B₂

B₁ = block-diagonal matrix (k blocks, แต่ละ block n/k × n/k)
P  = permutation matrix (learned หรือ fixed)
B₂ = block-diagonal matrix อีกตัว
```

Parameter count: 2 × k × (n/k)² + permutation ≈ 2n²/k แทน n²

ตัวอย่าง n=1024, k=32:
```
Dense:   1024² = 1,048,576 params
Monarch: 2 × 1024² / 32 = 65,536 params — ถูกกว่า 16 เท่า
```

### การเชื่อมกับ architecture ของคุณ

Monarch บอกว่า: "Ganglion (block-diagonal) + shuffle (permutation) + Ganglion (block-diagonal)" ของคุณ คือ Monarch factorization 2 ขั้น

ซึ่งหมายความว่า:
1. สิ่งที่คุณสร้างเป็น **approximation ที่ provably efficient** ของ dense transform
2. ไม่ใช่ approximation เพราะ "อยากประหยัด" แต่เพราะ **structure นี้คือ optimal** สำหรับ class ของ matrices ที่ useful ที่สุดใน ML
3. ถ้าซ้อนลึก log(n) ชั้น (แต่ละชั้น block + shuffle) คุณสามารถ express **ทุก dense matrix** ที่สำคัญได้

### ผลลัพธ์จริง

Monarch matrices บน GPT-2:
- Replace dense attention projection layers ด้วย Monarch
- Accuracy: ลดลงแค่ 0.1% perplexity
- Parameters: ลดลง **2-4×** ที่ layer เหล่านั้น
- Training speed: เร็วขึ้น **~23%** เพราะ sparse multiply เร็วกว่า dense

### สำหรับเรา

ถ้า translate clip ของคุณต้องผสม channels ขนาด 128:
- Dense crossbar: 128×128 = 16,384 cells ต้องสร้าง
- Monarch (2 ก้าว): 2 × (32×32×4) = 8,192 cells + permutation routing — ถูกกว่า 2× ที่ quality เดียวกัน
- Monarch (3 ก้าว): ถูกกว่า 4× ที่ quality เกือบเท่ากัน

ยิ่ง C ใหญ่ยิ่ง savings ใหญ่ตาม log(C) ซึ่งสำคัญมากเมื่อ chip ถูกจำกัดด้วย area

---

## บทที่ 6: Switch Transformer / Mixture-of-Experts (2021) — ผสมเฉพาะที่จำเป็น

### เรื่องราว

ปัญหาใน language model ขนาดใหญ่: อยากมี capacity มากโดยไม่เพิ่ม compute ต่อ token Shazeer et al. (Google) คิดว่า: แทนที่ทุก layer ทำงานสำหรับทุก input ให้มี "experts" หลายคน แต่แต่ละ input ใช้แค่ไม่กี่คน

**Sparsely Gated MoE** (2017, Shazeer): มี N experts, top-k routing, ใช้ k experts ต่อ input ปัญหาคือ complex และ training ไม่ stable

**Switch Transformer** (2021, Fedus et al.): simplify ลงสุดคือ **k=1** ส่งแต่ละ token ไปหา expert ตัวเดียว เรียกว่า "switch" เพราะ switch ไปหา expert ที่ router เลือก

### กลไกที่แท้จริง

```
Input token x
  ↓
Router (linear layer เล็กๆ):
  scores = Softmax(W_r · x)   [W_r มีขนาด d_model × N_experts]
  expert_k = argmax(scores)   [เลือก expert ตัวเดียวที่ score สูงสุด]
  ↓
ส่ง x ไปยัง expert_k เท่านั้น:
  output = Expert_k(x)        [Expert_k คือ FFN เต็มตัว]
  ↓
ผลลัพธ์ × scores[k]          [scale ตาม routing probability]
```

ระหว่าง training: N experts ทั้งหมดมีอยู่บน chip (parameter รวม = N × expert_size) แต่ต่อ token ใช้แค่ 1 expert ดังนั้น **FLOPs ต่อ token = 1/N ของที่จะเป็นถ้าใช้ทุก expert**

**ปัญหา Load Balancing:**
Router อาจเรียน "routing collapse" — ส่งทุก token ไป expert เดียว (expert 0 ได้ update เยอะ → เก่งขึ้น → router ส่งไปอีก → cycle ไม่หยุด)

**วิธีแก้ด้วย auxiliary loss:**
```
L_balance = α × Σ_i f_i × P_i

f_i = fraction of tokens ที่ถูกส่งไป expert i
P_i = average routing probability ไป expert i

ต้องการ: f_i ≈ 1/N สำหรับทุก i
```
Loss นี้บังคับให้ tokens กระจายเท่าๆ กัน ป้องกัน collapse

**ตัวเลขจริง:**
```
Token ขนาด d=768 → Router: 768 × N weights
ถ้า N=32 experts, expert size = 2048 hidden dim:
  Parameters รวม: 32 × (768×2048 + 2048×768) = 100M extra params
  FLOPs ต่อ token: 1 × (768×2048 + 2048×768) = 3.1M FLOPs (เท่ากับ 1 expert)
  แต่ capacity = 32 experts × 3.1M = 100M FLOPs equivalent
```

### ผลลัพธ์จริง

Switch-Base (เทียบกับ T5-Base):
- Parameters: **7× มากกว่า** T5-Base (experts ทั้งหมด)
- Training speed: **7× เร็วกว่า** ที่ compute budget เดียวกัน
- ไม่ใช่ "เร็วกว่าเพราะใช้ compute น้อย" แต่เพราะ **parameter count ใหญ่ขึ้น = เรียนเร็วขึ้น** ที่ compute เดียวกัน

### สำหรับเรา

MoE กับ Ganglion architecture: แทนที่ activate ทุก Ganglion ทุก forward pass router เล็กๆ (linear + argmax) ตัดสินว่า input นี้ควรไป Ganglion กลุ่มไหน

ผลลัพธ์:
- Ganglia ส่วนใหญ่ idle = ไม่ settle = ไม่กิน charge = ประหยัดพลังงานมาก
- Capacity ใหญ่ขึ้น (Ganglia หลายตัว) โดยไม่เพิ่ม active compute

ข้อระวัง: บน analog hardware ต้นทุนของ "ตัดสินใจ" router อาจไม่ถูก ถ้า router เป็น digital → ADC → linear → argmax → DAC → route นั่นอาจแพงกว่าแค่ let ทุก Ganglion settle ตลอด ต้องทดสอบว่า savings จาก idle Ganglia คุ้มกับ router overhead ไหม

---

## บทที่ 7: MLP-Mixer (2021) — พิสูจน์ว่าสองทิศทางพอ

### เรื่องราว

Tolstikhin et al. ที่ Google Brain ถาม: "Attention (ใน ViT) และ Convolution (ใน ResNet) จำเป็นจริงๆ ไหม? ถ้าเอาออกทั้งคู่ เหลือแค่ MLP ล้วน จะยังใช้งานได้ไหม?"

คำตอบที่พบ: **ได้** และ competitive กับ ViT และ ResNet บน ImageNet ถ้า pretrain บน dataset ใหญ่พอ — แม้ไม่ชนะทุกอย่าง แต่พิสูจน์ว่า pattern ที่ใช้ไม่ใช่ attention หรือ conv แต่คือ **ทิศทางของ mixing**

### กลไกที่แท้จริง

**Input preparation:**
- แบ่ง image เป็น S patches (เช่น image 224×224 → 196 patches ขนาด 16×16)
- Project แต่ละ patch เป็น vector ขนาด C → ได้ matrix ขนาด S×C

**Architecture: L layers ของ mixing ที่สลับกัน**

**Token-mixing MLP** (ผสมข้าม patches):
```
Input: [S × C]
Transpose → [C × S]
Apply MLP_1 ต่อแต่ละ row (dim C เดียว, ผสม S positions):
  MLP_1: S → 4S → S  (แต่ละ row คือ 1 feature ที่ผสมข้าม patch positions)
Transpose กลับ → [S × C]
```
ทำแบบนี้ต่อทุก feature dimension (C features) แยกกัน

**Channel-mixing MLP** (ผสมข้าม features):
```
Input: [S × C]
Apply MLP_2 ต่อแต่ละ row (dim S เดียว, ผสม C features):
  MLP_2: C → 4C → C  (แต่ละ row คือ 1 position ที่ผสมข้าม features)
```
ทำแบบนี้ต่อทุก position (S positions) แยกกัน

**Stack:** L × (Token-mixing → Channel-mixing) แล้ว global average pool → classifier

```
Layer 1:
  Token-mix: ผสม spatial (มองข้ามทุก patch positions สำหรับแต่ละ feature)
  Channel-mix: ผสม features (มองข้ามทุก features สำหรับแต่ละ position)

Layer 2: เหมือนกัน
...
Layer L: เหมือนกัน
```

ไม่มี attention mechanism ไม่มี spatial convolution ไม่มี positional encoding พิเศษ แค่ MLP สองชนิดสลับกัน

### ผลลัพธ์จริง

Mixer-L/16 (Large model, patch 16×16):
- ImageNet top-1 (ImageNet-21k pretrain): **84.15%**
- เทียบกับ ViT-L/16 (same data): **85.30%**
- เทียบกับ BiT-L (ResNet 152×4): **87.54%**

ไม่ชนะ แต่ **competitive มากสำหรับ architecture ที่ "เอา fancy ทุกอย่างออก"** — พิสูจน์ว่า pattern ที่จำเป็น คือ token mixing + channel mixing สลับกัน ไม่ใช่ mechanism ใดๆ โดยเฉพาะ

### สำหรับเรา

MLP-Mixer พิสูจน์ว่า: **การสลับ "ประมวลผลภายใน dimension" กับ "ผสมข้าม dimension" เป็น computational pattern ที่ sufficient** สำหรับ representation learning ทั่วไป

Pattern ของคุณ:
- Ganglion = "channel-mixing within spatial group" + "spatial filtering within channel"
- Translate clip / shuffle = "token mixing" ข้าม groups

คือ MLP-Mixer แบบ sparse (grouped แทน full) ที่ทำงานบน analog physics แทน digital compute ความที่ Mixer ใช้ได้หมายความว่า: pattern ของคุณ — ถ้า compute พอ — จะ sufficient

---

## สรุปทั้งไฟล์: pattern เดียวกัน เจอจากหลายทาง

| Paper | ปี | วิธีที่เจอ | หลักการ |
|---|---|---|---|
| AlexNet | 2012 | บังเอิญ (GPU ไม่พอ) | Groups force specialization, ถูกกว่า g× |
| ResNeXt | 2017 | ทดลอง (cardinality) | Parallel paths > single wide at same params |
| MobileNet/Xception | 2017 | ออกแบบ (efficiency) | Separate spatial from channel mixing |
| ShuffleNet | 2017 | ออกแบบ (zero-cost mix) | Permutation = mixing ฟรีทาง compute |
| Butterfly/Monarch | 2019/22 | ทฤษฎี (matrix structure) | Log-depth = optimal สำหรับ useful transforms |
| Switch Transformer | 2021 | Scale (conditional compute) | Route to few experts = capacity without compute |
| MLP-Mixer | 2021 | Ablation (เอาทุกอย่างออก) | Two-directional mixing เป็น sufficient pattern |

ทุกอันบอกว่า: **local processing + cheap mixing = complete computation** คุณมาถึงที่เดียวกันด้วยเหตุผลเชิงวงจร ซึ่ง arguably clean กว่าเพราะมาจาก physics ไม่ใช่จาก empirical search

**กฎปฏิบัติสำหรับ design ของเรา (เรียงตามลำดับลอง):**

1. **อย่า dense clip ก่อน** — ลอง channel shuffle + stack ก่อนเสมอ ถูกที่สุด
2. **ถ้า shuffle ไม่พอ** — ใช้ Monarch (block + shuffle) 2-3 ขั้น ถูกกว่า dense 4-16× ที่ quality เกือบเท่ากัน
3. **ถ้าต้องการ capacity สูงโดยไม่เพิ่ม active compute** — MoE routing แต่ต้องทดสอบ router overhead บน analog
4. **ถ้ากังวลว่า pattern จะไม่ sufficient** — MLP-Mixer พิสูจน์แล้วว่าพอ ถ้า depth พอ
