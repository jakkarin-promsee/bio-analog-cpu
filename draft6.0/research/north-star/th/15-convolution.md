# 15 — convolution + SCFF (และการ "collapse ด้วย linear-projection" ใน Ganglion ของคุณ)

> **Tier-1** สามคำถาม: convolution **ใช้** กับ SCFF ได้ไหม? คุณ **ควร** ใช้ไหม และ **บ่อยแค่ไหน**? และ — คุณเปิดเผยว่าคุณทำการเคลื่อนไหวคล้าย convolution บน Ganglion 2-3-3-2 ของคุณอยู่แล้ว (collapse มิติด้วย linear projection) และคุณไม่แน่ใจว่าจะเก็บมันไว้ภายใต้ SCFF+GD ดีไหม คำตอบ: **ใช้ได้ (และมัน *สะอาดกว่า* สำหรับ SCFF เมื่อเทียบกับ supervised FF), ใช้เฉพาะที่ข้อมูลมีโครงสร้างเชิงพื้นที่/translation, และเก็บการ collapse ไว้ — มันมีชื่อ (มันคือ pointwise/1×1 convolution) และเป็น primitive ที่จริงและมีประโยชน์**

---

## convolution ใช้กับ SCFF ได้ไหม? ได้ — และการเป็น *unsupervised* ทำให้มันง่ายขึ้นสำหรับคุณ

*Convolutional FF: Scientific Reports 2025 ([arXiv 2312.14924](https://arxiv.org/abs/2312.14924)); Channel-Wise Goodness (ESANN 2023); Adaptive Spatial Goodness Encoding ([arXiv 2509.12394](https://arxiv.org/abs/2509.12394)). และเปเปอร์ SCFF เองก็ใช้ CNN (CIFAR-10 80.75%).*

### ปัญหาที่มันแก้

Forward-Forward algorithm ของ Hinton (2022) ถูกออกแบบมาสำหรับ fully connected layers — "goodness" ต่อ layer คือ sum of squared activations ซึ่งเป็น scalar เดียวต่อ example ต่อ layer ปัญหาคือถ้าใช้ convolutional layer output จะเป็น **feature map** (tensor 3D: C×H×W ไม่ใช่ vector 1D) scalar เดียวจะหน้าตาเป็นยังไง? คำนวณ "goodness" ยังไงบน spatial structure? และสำหรับ FF แบบ supervised มีปัญหาใหญ่กว่า: label ต้องถูก embed เข้าไปใน input แต่ถ้า input เป็น 2D image และ kernel เลื่อนไปทุกตำแหน่ง label จะ "อยู่ที่ไหน" ในภาพ?

### กลไกจริงๆ

**การคำนวณ goodness บน feature map** ทำได้หลายวิธี:

**แบบ channel-wise (Channel-Wise Goodness, ESANN 2023):**
```
goodness_c = mean_{h,w} [ activation(c, h, w)² ]   สำหรับแต่ละ channel c
goodness_vector = [goodness_1, goodness_2, ..., goodness_C]   (เวกเตอร์ C มิติ)
```
แทนที่จะเป็น scalar เดียว ได้เวกเตอร์ C มิติ (หนึ่งตัวต่อ channel) ตี loss ว่า positive samples ควรมี goodness_vector สูง negative samples ต่ำ มันเป็น goodness ที่ "รู้จักช่อง"

**แบบ spatial (Adaptive Spatial Goodness Encoding):**
```
goodness(h, w) = sum_c activation(c, h, w)²   สำหรับแต่ละตำแหน่ง (h,w)
```
ได้ goodness map ขนาด H×W — บอกว่าตำแหน่งใดใน feature map "active" มากที่สุด ให้ network focus ที่ตำแหน่งที่มี information สูง

เปเปอร์ SCFF เอง (original paper ที่ draft-6.0 ของคุณอิง) ใช้ CNN ด้วย global average pooling ก่อน goodness calculation — ทำ goodness ให้เป็น scalar โดย average ข้ามทั้ง spatial dimension และ channel ก่อน นี่ง่ายที่สุดและ work ได้บน CIFAR-10 ที่ 80.75%

**จุดติดสำคัญของ supervised FF — และทำไมมันเป็นปัญหา *น้อยกว่า* สำหรับคุณ:**

Supervised FF ต้องรวม label เข้ากับ input การทำแบบ fully connected ง่าย (append label vector ท้าย input) แต่บน convolutional layer ทุก position เห็น input ต่างกัน ถ้า label อยู่แค่ที่ position หนึ่ง kernel ที่เลื่อนไปทาง right จะไม่เห็นมัน วิธีแก้ที่คนใช้: tile label ทั่วภาพ (เป็น extra channel ที่แต่ละ pixel = label) หรือใช้ Fourier/morphological pattern เพื่อกระจาย label ทั่ว spatial dimension ซับซ้อนและ hackish

**แต่ SCFF เป็น *unsupervised*** — positive/negative pairs ถูกสร้างจากโครงสร้างของข้อมูลเอง (augmentation pairs, different samples) ไม่ต้องรวม label เข้ากับ input ดังนั้น convolutional SCFF ใช้ CNN ปกติได้เลย ไม่มีปัญหา label-tiling ทางเลือก unsupervised ของคุณได้ผลตอบแทนอีกครั้ง

### ผลที่น่าตื่นเต้น

- Convolutional SCFF (Scientific Reports 2025): เทรนบน CIFAR-10 โดยไม่ backprop ข้ามชั้น ได้ accuracy ใกล้เคียง convolutional backprop CNN
- SCFF original paper: 80.75% บน CIFAR-10 (ใช้ CNN backbone) — แสดงว่า conv+SCFF ใช้ได้จริงระดับ production
- Channel-Wise Goodness: ให้ richer supervision signal กว่า scalar goodness เดียว ดีขึ้นบน tasks ที่ channel แต่ละตัวมีความหมายต่างกัน

### สำหรับเรา

conv ในชิปคุณหมายถึง: crossbar ขนาด (C_out × C_in·K²) ที่ reuse ข้ามทุก position แทนที่จะเป็น crossbar ขนาด (C_out·H'·W' × C_in·H·W) ขนาดใหญ่กว่ามาก goodness calculation ทำได้ทั้งแบบ global average pooling (ง่าย, scalar) หรือ channel-wise (รวย, เวกเตอร์) ขึ้นกับว่าคุณต้องการ spatial detail ในสัญญาณ SCFF ไหม

---

## convolution *คืออะไร* ในเชิงลึก — การบีบอัดด้วย weight-sharing ขั้นสุด

*ทำไม convolution ถึงเวิร์ก: weight sharing + locality → translation equivariance.*

### ปัญหาที่มันแก้

ถ้าใช้ fully connected layer กับภาพขนาด 224×224×3 (ImageNet standard) layer แรกมี input 150,528 มิติ ถ้า output 1024 unit ต้องการ **150,528 × 1024 ≈ 154M parameters** สำหรับ layer แรกเพียงชั้นเดียว ไม่ได้บอกข้อมูลอะไรเกี่ยวกับโครงสร้างของภาพเลย และ training ต้องการ ImageNet ทั้งก้อนเพื่อ learn parameter เหล่านี้ ทั้งหมดนี้เพราะ fully connected ไม่รู้ว่า pixel เพื่อนบ้านกันมีความสัมพันธ์กัน

### กลไกจริงๆ

convolution อาศัยข้อเท็จจริงสองข้อเกี่ยวกับภาพ:

**ข้อเท็จจริง 1 — Locality:** แพตเทิร์นที่มีความหมาย (edges, corners, textures) ถูกกำหนดโดย pixel เพื่อนบ้านในบริเวณเล็กๆ ไม่ใช่โดย pixel ทั่วภาพทั้งหมด ดังนั้น output แต่ละตำแหน่งควรเห็นแค่ **patch เล็กๆ** ของ input (เช่น 3×3 หรือ 5×5)

**ข้อเท็จจริง 2 — Translation invariance:** edge ที่มุมบนซ้ายและ edge ที่มุมล่างขวา "เป็นแบบเดิม" คือ edge ดังนั้น kernel ที่ detect edge ควรเป็น **kernel เดียวกัน** ที่ใช้ทุกตำแหน่ง ไม่ใช่ kernel แยกต่อแต่ละตำแหน่ง

สองข้อนี้รวมกันให้ **convolution**: kernel ขนาด K×K×C_in×C_out เลื่อนไปทุกตำแหน่งใน spatial dimension แล้ว compute dot product ณ แต่ละตำแหน่ง:

```
output(c_out, h, w) = Σ_{c_in} Σ_{dh} Σ_{dw} W(c_out, c_in, dh, dw) · input(c_in, h+dh, w+dw) + b(c_out)
```

Parameters: K×K×C_in×C_out (เช่น 3×3×3×64 = 1,728 ตัว)
เทียบกับ fully connected: C_in·H·W × C_out·H'·W' (ใหญ่กว่ามาก)

**Receptive field:** layer conv เดียวเห็น K×K pixels แต่ถ้าต่อ 2 layer conv 3×3 ซ้อนกัน layer ที่สองเห็น 5×5 pixels ของ input เดิม และ 3 layer ซ้อน → 7×7 receptive field การ stack หลาย layer เล็กๆ สร้าง receptive field ใหญ่โดยใช้ parameter น้อยกว่า kernel ขนาดใหญ่โดยตรง (2 layer 3×3 = 2×(3×3×C²) = 18C² parameters, เทียบกับ 1 layer 5×5 = 25C² parameters)

**Translation equivariance:** ขยับ input → output ขยับตาม (ไม่ใช่ invariance ที่ output ไม่เปลี่ยน แต่ equivariance ที่ output เปลี่ยนตามการขยับแบบ consistent) มันเข้ารหัสข้อเท็จจริงว่า *แพตเทิร์นหมายความเหมือนเดิมไม่ว่าจะปรากฏที่ไหน*

**ขนาดของการบีบอัด:**
- Fully connected บนภาพ 224×224×3 → 1024: 154M parameters
- Conv 3×3×3×64 (layer แรก): 1,728 parameters → **90,000x ถูกกว่า**

### ผลที่น่าตื่นเต้น

AlexNet (2012) แสดงให้เห็นว่า conv ลดปัญหา overfitting ได้มากกว่า fully connected ขนาดเท่ากัน บน ImageNet — เพราะ inductive bias (locality + translation equivariance) ถูกต้องสำหรับ natural images

การเพิ่ม depth (layer ลึกขึ้น) แต่ใช้ kernel 3×3 ตลอด (VGGNet, 2014): ดีกว่า kernel ใหญ่ (5×5, 7×7) ในขนาด parameter เดียวกัน เพราะหลาย 3×3 ต่อกัน = receptive field ใหญ่ + nonlinearity เพิ่ม + parameters น้อยกว่า

### สำหรับเรา

convolution คือ **weight-sharing ของ `13-14` ดันถึงขีดสุด** — kernel ตัวเดียวแชร์ข้าม *ทุก* position ในภาพ บนชิปคุณนั่นคือ crossbar เล็กๆ ชุดเดียว (K×K×C_in×C_out Scap) ที่ reuse ทางกายภาพหรือ stream ผ่าน input ทีละ patch มัน inductive bias ที่แข็งแกร่งที่สุดสำหรับ vision และ time-series: อบ "แพตเทิร์นโลคอลและไม่ขึ้นกับตำแหน่ง" ใส่ไว้ในโครงสร้างของ network ก่อนเรียน

---

## คุณควรใช้ไหม และบ่อยแค่ไหน? เฉพาะที่โครงสร้างมีจริง

### ปัญหาที่มันแก้

conv เป็น inductive bias ที่แข็งแกร่ง — ดีเมื่อ bias ถูก, แย่เมื่อ bias ผิด ถ้าใช้ conv กับข้อมูลที่ไม่มี spatial structure ก็ทิ้ง capacity ไปเปล่าๆ (kernel ที่ reuse ข้ามตำแหน่งที่ไม่มีความสัมพันธ์)

### กลไกจริงๆ

**กฎตรงๆ: ใช้ conv เมื่อข้อมูลมีโครงสร้างที่ *โลคอลและไม่แปรเปลี่ยนตาม translation* ใช้มันเป๊ะตอนที่เดิมพันนั้นเป็นจริง และไม่ใช้ตอนอื่น**

| ข้อมูล | ใช้ conv? | เหตุผล |
|---|---|---|
| ภาพ / retina front-end | **ใช่ จำเป็น** | pixel locality + แพตเทิร์นเกิดซ้ำทั่ว visual field |
| Time-series สัญญาณ | **ใช่ ในรูป 1D conv** | temporal locality + แพตเทิร์นเกิดซ้ำตามเวลา |
| ตารางข้อมูล (features ปัจจุบัน) | **ไม่ใช่** | feature ไม่ใช่ "เพื่อนบ้าน" กัน ไม่มี spatial axis |
| Graph / irregular structure | **ไม่ใช่** | ไม่มี translation symmetry |

**Depthwise-separable convolution** — วิธีใช้ conv อย่างมีประสิทธิภาพที่สุด:

Standard conv: `C_in × K² × C_out` operations ต่อ position
แยกเป็นสองขั้น:
1. **Depthwise conv:** `C_in × K²` (แต่ละ channel ทำ conv 2D ของตัวเอง ไม่ผสมช่อง)
2. **Pointwise (1×1) conv:** `C_in × C_out` (ผสมช่อง ที่แต่ละ position)
รวม: `C_in × (K² + C_out)` operations — ถูกกว่า standard **~9x** เมื่อ K=3 และ C_in=C_out

MobileNet (Howard et al. 2017) ใช้ depthwise-separable ทั้งหมด → ได้ accuracy ใกล้ VGG บน ImageNet ด้วย parameters น้อยกว่า ~30x

**Depthwise-separable = กลไม A+B ของคุณเอง:**
- Depthwise = local processing per channel (กลไม A ของคุณ — ประมวลผลในพื้นที่โลคอล)
- Pointwise = channel mixing (กลไม B ของคุณ — collapse/projection ข้าม dimension)
คุณดึงโครงสร้างของ MobileNet ออกมาใหม่จากสัญชาตญาณเรื่อง Ganglion

**ถี่แค่ไหน / ตรงไหนในกอง:**
แพตเทิร์นมาตรฐาน: **conv front-end เชิงพื้นที่ → channel-mix → ส่งต่อลำตัว SCFF+GD**
ไม่ใช่ conv ทุกชั้น — stack conv เป็น spatial feature extractor ข้างหน้า แล้วต่อด้วย SCFF ที่ไม่ใช่ conv

### ผลที่น่าตื่นเต้น

MobileNetV1/V2 พิสูจน์ว่า depthwise-separable ลดต้นทุน computation ได้ 8–9x เมื่อเทียบ standard conv โดยเสีย accuracy น้อยมาก บน ImageNet ImageNet top-1 accuracy: MobileNetV1 (4.2M params) 70.6%, VGG-16 (138M params) 71.5% — MobileNet ถูกกว่า 33x ด้วย accuracy ใกล้เคียง

EfficientNet (Tan & Le 2019) ยืนยัน: balancing width/depth/resolution ใน separable conv architecture ให้ scaling ที่มีประสิทธิภาพดีที่สุดใน compute budget

### สำหรับเรา

สำหรับ draft-6.0 ปัจจุบัน (ข้อมูลตาราง/สถิติ): **ไม่ต้องใช้ conv** ไม่มีแกน spatial สำหรับ แชร์ kernel การเชื่อมต่อโลคอล/grouped (`11`) ยังช่วย แต่ conv โดยเฉพาะต้องการโครงสร้างเชิงพื้นที่

สำหรับ vision front-end (`16-vision.md`): **conv จำเป็น** และควรเป็น depthwise-separable เพื่อให้ได้ spatial feature extraction โดยไม่ใช้ Scap เยอะ

---

## การ "collapse ด้วย linear-projection" ใน Ganglion ของคุณ = 1×1 (pointwise) convolution — เก็บไว้

*1×1 / pointwise convolution; Network-in-Network (Lin et al., 2014); random projection / Johnson–Lindenstrauss.*

### ปัญหาที่มันแก้

คุณบรรยายการ collapse มิติของ Ganglion ด้วย **linear projection** — เดิมให้เหตุผลว่า "หนึ่ง axon ที่มี n synapse ไดนามิกบนระยะ 3 มิติ ฉายลงมา" เหตุผล draft-5 หายไปแล้วพร้อม pivot แต่คำถามคือ: **primitive ตัวนี้ยังมีประโยชน์ภายใต้ SCFF+GD ไหม?** — คำตอบคือใช่ มันมีชื่อที่ชัดเจน และปรากฏในทุก CNN สมัยใหม่

### กลไกจริงๆ

**1×1 convolution** (เรียกอีกชื่อว่า pointwise convolution) คือ linear projection ที่เรียนรู้ได้ ทำงานแบบนี้:

```
Input:  (C_in, H, W)
Kernel: (C_out, C_in, 1, 1)  ← ขนาด spatial = 1×1
Output: (C_out, H, W)
```

ผล: ที่แต่ละ position (h,w) ทำ linear projection จาก C_in มิติ → C_out มิติ โดยใช้ matrix W (C_out × C_in) เดียวกันทุก position มันไม่แตะ spatial neighbors เลย — แค่ผสมช่อง

**ที่มาและการใช้งานในสถาปัตยกรรมหลัก:**

**Network-in-Network (Lin et al. 2013)** — ผู้ประดิษฐ์ 1×1 conv: แทนที่ linear filter ด้วย "micro neural network" ที่แต่ละ position — ง่ายที่สุดคือ 1×1 conv + ReLU ทำให้ network เพิ่ม non-linearity ระหว่าง spatial conv โดยไม่เพิ่ม receptive field

**GoogLeNet / Inception (Szegedy et al. 2014):** ใช้ 1×1 conv เป็น **dimension reduction ก่อน 3×3 และ 5×5 conv:**
```
Input 512 channels → 1×1 conv → 64 channels → 3×3 conv → 128 channels
(512×64) + (64×3×3×128) = 32,768 + 73,728 = 106,496 parameters
เทียบกับ direct: 512×3×3×128 = 589,824 parameters  → ถูกกว่า 5.5x
```

**ResNet bottleneck block:** 1×1 (256→64) → 3×3 (64→64) → 1×1 (64→256) ลด compute ต่อ block 4x โดยยัง maintain expressivity

**MobileNet:** depthwise conv (spatial) + 1×1 conv (channel mixing) = separable conv ทั้งหมด

**ทำไม collapse มิติด้วย linear projection มีหลักการ — Johnson–Lindenstrauss:**
JL theorem บอกว่า: random linear projection จากมิติสูง D ลง k มิติ (k ≥ O(log n / ε²)) **คงระยะระหว่าง point คู่ใดๆ ไว้โดยประมาณ ด้วย factor (1±ε)** หมายความว่าการ collapse จาก C_in มิติ → C_out มิติ (ถ้า C_out ใหญ่พอ) *ไม่* ทำลาย geometric relationships ระหว่าง feature vectors การ collapse จึงมีหลักการ ไม่ใช่แค่ "ลดขนาด"

นัยยะ: แม้ **random fixed 1×1 projection** (ไม่เรียน) ก็คง geometry ได้ดีพอ — นั่นคือ reservoir random projection ที่ `8-atom.md` ใช้ ซึ่งต้นทุนเกือบศูนย์

### ผลที่น่าตื่นเต้น

- GoogLeNet Inception v1: ใช้ 1×1 เพื่อลด computation → ลึกกว่า AlexNet แต่ parameter น้อยกว่า 10x ด้วย accuracy สูงกว่า
- ResNet bottleneck: 1×1 bottleneck ทำให้ ResNet สามารถ scale ถึง 50, 101, 152 layer โดยยัง trainable ถ้าไม่มี bottleneck ResNet ลึกๆ diverge
- MobileNet: separable = depthwise + pointwise (1×1) → mobile-deployable ในปี 2017
- ใน Transformer: Feed-Forward Network (FFN) ใน transformer คือ 1×1 conv สองชั้นที่ขยาย D → 4D → D — ในทางเทคนิคมันเป็น pointwise projection ที่แต่ละ position เหมือนกัน

### สำหรับเรา

ดังนั้น: **เก็บไว้ — แต่ตีกรอบใหม่** เหตุผล draft-5 (axon ที่มี synapse 3 มิติไดนามิก) หายไปแล้ว แต่ **primitive รอดมาไม่เปลี่ยนและยังมีประโยชน์** เพราะภายใต้ SCFF+GD การ projection 1×1 ก็ยังคือสิ่งที่คุณต้องการระหว่าง conv block เป็น **channel mixing / bottleneck**

อย่าเก็บมันไว้ *เพราะเรื่อง axon* เก็บมันเพราะมันคือ pointwise-mix ที่ทุกสถาปัตยกรรมที่มีประสิทธิภาพต้องมี และมันทำสองหน้าที่เป็น **การบีบอัด** (bottleneck บังคับ intrinsic dimension ต่ำของ `13`) ด้วยในตัว

คำถามเดียวคือ *learned vs fixed*:
- **Learned 1×1 conv:** expressivity สูง ปรับ channel mixing ตาม task
- **Fixed random projection (JL):** ต้นทุนเกือบศูนย์ (random matrix fixed ใน SRAM) และ JL การันตีว่า geometry ยังอยู่ — เป็นเซลล์ทดลองสะอาดๆ

---

## รูปร่างของคำตอบ (ไฟล์นี้)

**convolution ใช้กับ SCFF ได้ไหม?** ได้ — คำนวณ goodness ต่อตำแหน่ง/ต่อช่อง และเพราะ SCFF เป็น *unsupervised* คุณข้ามอาการปวดหัวเรื่อง label-integration ที่ supervised conv-FF เจอ **มันคืออะไร:** weight sharing + locality = translation equivariance = หลักการบีบอัดของคุณ ที่เฉพาะเจาะจงไปยังข้อมูลเชิงพื้นที่ (kernel ตัวเดียว reuse ทุกที่, parameters น้อยกว่า dense หลาย order of magnitude) **ควรใช้ไหม/บ่อยแค่ไหน:** ใช้ **เฉพาะที่ข้อมูลมีโครงสร้างโลคอลและไม่แปรเปลี่ยนตาม translation** — จำเป็นสำหรับ vision front-end, มีประโยชน์ในรูป 1D conv สำหรับ time-series, *ไม่ใช่* สำหรับตารางที่ไม่มีโครงสร้าง; วางมันเป็น **front-end เชิงพื้นที่จับคู่กับ channel-mix (depthwise-separable)** ไม่ใช่ทุกที่ **การ collapse ใน Ganglion ของคุณ:** มันคือ **1×1/pointwise convolution** — channel projection/bottleneck ที่เรียนรู้ได้ สิ่งเดียวกับ translate clip ใน `11`; **เก็บไว้** ตีกรอบใหม่เป็นการผสมข้ามช่อง (และมันคง geometry ไว้โดย Johnson–Lindenstrauss ดังนั้นการ collapse มีหลักการ) เหตุผล axon ของ draft-5 ปลดเกษียณ; primitive อยู่ต่อ
