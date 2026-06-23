# 7 — รูปร่างของอินพุต/เอาต์พุต และ "อย่าให้โมเดลหลอกตัวเอง"

> คำพูดของคุณ: *"อินพุตที่ label ไม่เยอะ แต่ก็ยังไม่ทำให้โมเดลหลอกตัวเอง"* นี่คือ **ปัญหา representation** และ "หลอกตัวเอง" มีชื่อเรียกที่แม่นยำสองชื่อ: **การ collapse (ยุบตัว)** (ตัวเข้ารหัสปล่อยเอาต์พุตเหมือนกันหมดไม่ว่าอินพุตจะเป็นอะไร — "สอดคล้องกัน" แบบไร้สาระ ไร้ประโยชน์สิ้นเชิง) และ **การเรียนทางลัด (shortcut learning)** (มันไปเกาะกับสัญญาณหลอก ๆ แทนโครงสร้างจริง) ไฟล์นี้คือเมนูของวิธีเข้ารหัสอินพุตที่ label น้อยให้เป็น representation ที่ *ซื่อตรง* — กัดเข้ากับ **draft 6.0 ตอนนี้เลย** ไม่ใช่แค่เฟส 2 เพราะงานทั้งหมดของ SCFF ก็คือการเข้ารหัส

---

## VICReg — สูตร "อย่า collapse" ที่สะอาดที่สุด

*Bardes, Ponce & LeCun, ICLR 2022 ([arXiv 2105.04906](https://arxiv.org/abs/2105.04906)).*

### ก่อนหน้า: ทุกคนต่อสู้กับ collapse ด้วยทริกที่ซ่อนอยู่

ปัญหาพื้นฐานของ self-supervised learning คือ: ถ้าคุณเทรนโมเดลให้ embed ทุกอย่างให้ "สอดคล้องกัน" ทางลัดที่ง่ายที่สุดคือ **embed ทุกอย่างเป็นเวกเตอร์ศูนย์** ทุกอินพุตสอดคล้องกันกับตัวเองเสมอ loss เป็นศูนย์ โมเดล "ชนะ" — แต่ไม่มีประโยชน์เลย นี่คือ **dimensional collapse**

ก่อน VICReg วิธีหลีก collapse มีสามตระกูล แต่ทุกตระกูลใช้กลไกที่ **ซ่อนอยู่ใต้พรม**:

- **Negative pairs (SimCLR):** ดึงสองมุมมองของรูปเดียวกันให้ใกล้กัน ผลัก pairs ที่ต่างกันออกจากกัน ต้องการ batch 4096+ เพื่อให้มี negatives เพียงพอ ต้นทุนสูง
- **Stop-gradient (BYOL, SimSiam):** หยุด gradient ฝั่งหนึ่งเพื่อทำลาย symmetry ที่ทำให้ collapse ทำงานได้จริง แต่ไม่มีใครอธิบายได้แน่ชัดว่าทำไม ต้อง momentum encoder อีกตัว
- **Batch normalization:** normalizing ป้องกัน collapse โดยปริยาย แต่ผูก performance กับ batch size ตาย

VICReg เปลี่ยนเรื่องนั้น: **พูดตรง ๆ เลยว่า "อย่า collapse" ด้วย loss ที่อ่านออก**

### กลไก: สามเทอม สามงาน

Architecture: อินพุตสองมุมมอง → encoder (ResNet-50) → projector (MLP 3 ชั้น, output 8192 dim) → คำนวณ loss ทั้งสามพร้อมกัน

**เทอม 1 — Variance (v):** บังคับให้ standard deviation ของแต่ละ dimension embedding วัดข้าม batch อยู่เหนือ threshold γ=1:
```
v(Z) = (1/d) Σ_j  max(0, γ − std(Z_j, ε))
```
ถ้า std ของ dimension ใดต่ำกว่า γ — เทอมนี้ penalize ทันที นี่คือ anti-collapse โดยตรง ไม่มีเล่ห์เหลี่ยม ถ้า embedding ทุกตัวกลายเป็นค่าเดียวกัน std → 0 → loss พุ่ง

**เทอม 2 — Invariance (s):** สองมุมมองของอินพุตเดียวกันต้องให้ embedding ที่ใกล้กัน:
```
s(Z, Z') = (1/n) Σ_i  ||z_i − z'_i||²
```
นี่คือสัญญาณการเรียนรู้จริง ๆ "สองมุมมองของสิ่งเดียวกันควรดูเหมือนกัน"

**เทอม 3 — Covariance (c):** ลงโทษ off-diagonal ของ covariance matrix ระหว่าง dimensions:
```
c(Z) = (1/d) Σ_{i≠j}  [Cov(Z)]²_{ij} / d
```
ถ้า dimension สอง dims มี covariance สูง = พวกมัน encode ข้อมูลเดิมซ้ำกัน เทอมนี้บอกว่า **ทุก dimension ต้องพกข้อมูลของตัวเอง**

Loss รวม: `L = λ·s + μ·v + ν·c` (paper ใช้ λ=25, μ=25, ν=1)

ไม่มี negative pairs ไม่มี stop-grad ไม่มี momentum encoder สามปุ่มนี้คือ *"จงให้ข้อมูล (variance), จงสอดคล้อง (invariance), จงไม่ซ้ำซ้อน (covariance)"* เป๊ะ ๆ

### ผลที่ได้

ImageNet linear evaluation (freeze encoder, train linear classifier บน top):
- VICReg: **73.2%** top-1
- SimCLR (batch 4096): 69.3%
- BYOL (momentum encoder): 74.3%
- Barlow Twins: 73.2%

VICReg ทำได้ใกล้ BYOL โดยใช้ batch size 256 และ architecture ที่อ่านออก ที่สำคัญกว่า: ถ้าตัดเทอมใดออก ประสิทธิภาพตกชัด ทั้งสามทำงานร่วมกัน ไม่ใช่ redundant

Transfer learning (fine-tune บน downstream tasks): VICReg ดีกว่า SimCLR ใน object detection และ segmentation — แสดงว่า feature ที่ได้ general จริง ไม่ใช่แค่ fit ImageNet proxy

### สำหรับเรา

SCFF ของคุณมีกลไกกัน collapse อยู่แล้วแบบ implicit: goodness threshold (positive ต้องดัง, negative ต้องเงียบ) บีบให้มีความต่างระหว่าง distributions VICReg คือเวอร์ชัน **ชัดเจน แยกส่วน ตีความได้**

จุดที่น่าตื่นเต้นสำหรับ substrate: เทอม Variance และ Covariance ล้วนเป็น **running statistics**:
- `std(Z_j)` ข้าม batch = ค่าเฉลี่ยเคลื่อนที่ของ `z_j²` และ `z_j` — capacitor รั่วพก running mean ได้แบบ native
- Covariance matrix ระหว่าง dimensions = outer product ของ embedding vector — ซึ่งคือ crossbar operation หนึ่ง sweep

**แผนปฏิบัติ:** ถ้า SCFF ดัน collapse ในซิม (ทุก unit ยิงเหมือนกัน หรือ goodness กระจุกที่ค่าเดียว) — เพิ่มพื้น variance + เทอม decorrelation บน goodness loss นั่นคือ VICReg และมันถูกในเชิงแอนะล็อก เทอม covariance สร้างแรงดันให้แต่ละ unit encode ข้อมูลคนละชุด ซึ่งก็คือ feature diversity ที่ทำให้ GD head ข้างบนทำงานได้ดีขึ้น

---

## Barlow Twins — กัน collapse ในฐานะการลดความซ้ำซ้อน

*Zbontar, Jing, Misra, LeCun & Deny, ICML 2021 ([arXiv 2103.03230](https://arxiv.org/abs/2103.03230)).*

### เบื้องหลัง: ทฤษฎีสมองของ Horace Barlow

ปี 1961 Horace Barlow นักประสาทวิทยาแห่ง Cambridge เสนอสมมติฐาน **Redundancy Reduction**: สมองเข้ารหัสข้อมูลประสาทสัมผัสโดยมีเป้าหมายเพื่อ **กำจัดความซ้ำซ้อนระหว่างนิวรอน**

เหตุผล: ถ้านิวรอน A และ B ยิงพร้อมกันเสมอ (correlated) คุณไม่ได้ข้อมูลสองชุด คุณได้ชุดเดียวที่ copy กัน นั่นคือ bandwidth เปล่า ๆ สมองที่ efficient ควร encode ข้อมูลใน representations ที่ **uncorrelated** เพื่อใช้แต่ละนิวรอนพกข้อมูลที่ unique

Barlow Twins นำหลักการ 60 ปีนี้มาเป็น loss function โดยตรง

### กลไก: cross-correlation matrix เข้าหา identity

Architecture: สองมุมมองของอินพุตเดียวกัน → encoder → projector → normalize แต่ละ dimension → embedding `Z_A` และ `Z_B`

Cross-correlation matrix (วัดระหว่าง dimensions ข้าม batch b):
```
C_ij = (Σ_b z^A_bi · z^B_bj) / sqrt(Σ_b (z^A_bi)²) · sqrt(Σ_b (z^B_bj)²)
```
C_ij คือ cosine similarity ระหว่าง dimension i ของ view A กับ dimension j ของ view B

Loss:
```
L_BT = Σ_i (1 − C_ii)² + λ Σ_i Σ_{j≠i} C_ij²
```

**แนวทแยง (diagonal) → ดัน C_ii → 1:** dimension เดียวกันจากสองมุมมองสอดคล้องกัน = invariance ต่อ augmentation

**นอกแนวทแยง (off-diagonal) → ดัน C_ij → 0:** feature ต่างคู่ไม่ควรสอดคล้องกันข้ามมุมมอง = redundancy elimination

สองงานในสมการเดียว ไม่มีเทอมแยก ไม่มีทริก

ทำไม target matrix คือ **identity**? เพราะถ้า C = I: แนวทแยง = 1 หมายความว่า "feature นี้ invariant" นอกแนวทแยง = 0 หมายความว่า "feature แต่ละตัว encode สิ่งที่ unique" ทั้งหมดคือนิยามของ representation ที่ดีในทฤษฎีสารสนเทศ

### ผลที่ได้

ImageNet linear evaluation:
- Barlow Twins (ResNet-50, projector 8192 dim): **73.2%**
- ที่ projector 8192 dim: **75.0%** — ยิ่ง embedding space กว้าง ยิ่งดีขึ้น
- Tolerant กับ batch size เล็ก (256) ดีกว่า SimCLR มาก เพราะ C matrix ประมาณ correlation จากข้อมูลที่มีได้ดี

Pattern สำคัญ: **ยิ่ง dimension ใหญ่ ยิ่งดี** เพราะ off-diagonal terms มากขึ้น redundancy elimination ทำงานได้ละเอียดกว่า ซึ่งตรงกับ SDR insight: high-dimensional sparse code มีประสิทธิภาพกว่า

### สำหรับเรา

**Cross-correlation matrix คือ outer product ของ crossbar:** ถ้า embedding เป็นเวกเตอร์ใน activation buffer คุณคำนวณ `Z_A^T · Z_B` ได้ด้วย one sweep ของ crossbar นั่นคือ C matrix ตรง ๆ พลังของ analog crossbar ที่คุณมีอยู่แล้ว

หลักการ **redundancy reduction ยังเป็นหลักการทน noise สำหรับ analog hardware:** ถ้า features ไม่มีความซ้ำซ้อน (uncorrelated) noise ที่มาถูก unit หนึ่งจะไม่ส่งผลต่อ unit อื่น เพราะพวกมัน encode ข้อมูลคนละชุด ถ้า unit A และ B highly correlated และ A ดริฟต์ — B จะดูแปลกด้วย เพราะ downstream unit ถูก train ให้คาดหวัง A↑⟺B↑ แต่ถ้า uncorrelated การดริฟต์ของ A ไม่กระทบ B — **decorrelation คือ PVT robustness ใน disguise**

---

## MAE vs I-JEPA — สร้าง *pixel* ขึ้นใหม่ หรือทำนายใน *พื้นที่ representation*?

*MAE: He et al., CVPR 2022 ([arXiv 2111.06377](https://arxiv.org/abs/2111.06377)); I-JEPA: Assran et al., CVPR 2023 ([arXiv 2301.08243](https://arxiv.org/abs/2301.08243)).*

### MAE: ปิดบัง 75%, ทำนาย pixel กลับ

MAE (Masked Autoencoders) มาจากสัญชาตญาณง่ายมาก: BERT เทรน NLP โดยปิดบังคำแล้วให้ทำนาย — ทำกับภาพได้มั้ย?

วิธีการ:
1. หั่นภาพเป็น patch 16×16 pixels ได้ ~196 patches (ภาพ 224×224)
2. **ปิดบัง 75%** แบบสุ่ม สูงกว่า BERT (15%) เพราะภาพมี spatial redundancy สูงกว่าข้อความมาก
3. Encoder ViT ประมวลผล **เฉพาะ patches 25%** ที่ไม่ถูกปิดบัง — ประหยัด compute ได้มากตรงนี้
4. Decoder ขนาดเล็กรับ encoded patches + mask tokens แล้ว reconstruct **pixel ที่หายไป**
5. Loss: MSE บน pixels ที่ถูกปิดบัง เฉพาะส่วนที่หายไป

ผล: ImageNet fine-tune **85.9%** (ดีมาก) แต่ linear probe เพียง **68.0%** — ต่างกันมาก หมายความว่า feature ที่ได้ยังต้องอาศัย task-specific fine-tuning จึงทำงานได้ดี representation ยัง "ดิบ" เกินไปสำหรับ linear readout

เหตุผลที่ linear probe แย่กว่า: การ predict pixel บังคับโมเดลให้ผลาญ capacity ไปจำ **texture, noise, lighting variation** ที่ไม่มีความหมายเชิง semantic แต่จำเป็นต้องจำเพื่อ predict pixel ที่ถูกต้อง

### I-JEPA: ทำนาย representation ไม่ใช่ pixel

LeCun ไม่พอใจกับ pixel prediction มานานแล้ว เหตุผล: "ภาพธรรมชาติมี noise ที่ทำนายไม่ได้อยู่มาก ถ้าบังคับโมเดลให้ทำนาย pixel จริง ๆ โมเดลต้องผลาญ capacity ไปสร้างรายละเอียดที่ไม่มีความหมายเชิง semantic" I-JEPA แก้ด้วยการเปลี่ยน **เป้าหมาย**

วิธีการ:
1. อินพุต → **context encoder** ประมวลผล patches ที่มองเห็น (ส่วนที่ไม่ถูกปิดบัง)
2. **Target encoder** (momentum-updated copy ของ encoder — EMA ไม่มี gradient ผ่าน) สร้าง representation ของ patches **ทั้งหมด** รวมถึงที่ถูกปิดบัง
3. Predictor รับ context representation + positional info ของส่วนที่ถูกปิดบัง แล้วทำนาย **representation ของ target encoder** สำหรับส่วนนั้น — ไม่ใช่ pixel
4. Loss: MSE ใน **representation space** ของ target encoder

ทำไม target encoder ถึงเป็น EMA? เพราะ representation ของมันค่อย ๆ พัฒนาแบบเสถียร ไม่กระโดด ทำให้ target ที่ predictor ต้อง match นั้น smooth และ well-defined — คล้าย teacher ใน knowledge distillation

### ทำไม representation space ถึงชนะ

ผลเปรียบเทียบ (ResNet-50 equivalent):
- Linear probe: I-JEPA **72.0%** vs MAE **68.0%** — ต่างกัน 4%
- 1% label fine-tune: I-JEPA **70.3%** vs MAE **60.0%** — ต่างกัน **10%** เมื่อมี label น้อย
- 10% label fine-tune: I-JEPA **77.9%** vs MAE **74.7%**

ยิ่ง label น้อย ช่องว่างยิ่งกว้าง — แสดงว่า feature ของ I-JEPA semantic กว่าจริง ๆ ไม่ใช่แค่ dataset เฉพาะ

คำอธิบายในภาษา Information Bottleneck: MAE บังคับ I(X;Z) สูง (โมเดลต้องจำ pixel level detail); I-JEPA ปล่อย I(X;Z) ต่ำ (ลืม noise ได้ จำ structure) — feature ที่ compression-efficient มาก generalize ได้ดีกว่า

### สำหรับเรา

SCFF ของคุณทำนายใน feature space อยู่แล้ว (goodness = norm ของ activation ไม่ใช่ reconstruction ของ input) — I-JEPA ยืนยันอย่างเป็นทางการว่านั่นถูก

**อย่าเพิ่ม reconstruction loss ของ input เข้าไปใน SCFF** ถ้าคิดจะทำ อาจดูเหมือนช่วยในตอนแรก (loss ลดไว) แต่ I-JEPA พิสูจน์แล้วว่าการ predict input โดยตรงให้ feature ที่แย่กว่า เมื่อมี label น้อย

สำหรับเฟส 2 ที่มี predictive coding ระหว่างระดับ (ดู `9-hierarchy.md`): ให้ระดับสูงทำนาย **representation** ของระดับล่าง ไม่ใช่ activation ดิบ — นั่นคือ I-JEPA ที่ scale ไปสู่ hierarchy และหลักการนี้แข็งแกร่งมากพอที่จะเชื่อได้แม้ก่อนจะรัน sim

---

## Sparse Coding & Sparse Distributed Representations — โค้ดที่ซื่อตรงและทน noise

*Sparse coding: Olshausen & Field, Nature 1996; SDR: Hawkins / Numenta ([arXiv 1503.07469](https://arxiv.org/pdf/1503.07469)).*

### Olshausen & Field: ทำไม V1 ถึงดูแบบนั้น

ปี 1996 Bruno Olshausen และ David Field ถามคำถามที่เรียบง่ายมาก: **ทำไม simple cells ใน V1 (visual cortex ชั้นแรก) ถึงตอบสนองต่อ oriented edges และ sinusoidal gratings?** เซลล์เหล่านี้มีรูปร่างตอบสนองที่เฉพาะมาก มันวิวัฒน์มาเพื่ออะไร?

แทนที่จะไปขุดชีววิทยา พวกเขาถาม: **"algorithm ที่เหมาะที่สุดในการ represent ภาพธรรมชาติคืออะไร?"** ถ้าคำตอบออกมาเหมือน V1 แสดงว่า evolution ค้นพบสิ่งเดียวกันกับ information theory

กำหนดว่า: ภาพ `x = Φa` โดย Φ คือ dictionary ของ basis functions และ a คือ coefficients เป้าหมาย: minimize จำนวน nonzero coefficients (||a||₀) ให้ `x ≈ Φa`

Formulation แบบ practical (L1 relaxation):
```
min_a  (1/2)||x − Φa||² + λ||a||₁
```

`||a||₁` promote sparsity — เหมือน Lasso regression กดให้ coefficients ส่วนใหญ่เป็นศูนย์ เรียน dictionary Φ ด้วย gradient descent บน natural image patches

**ผลลัพธ์ที่น่าตกใจ:** dictionary ที่เรียนรู้ได้กลายเป็น **oriented edge detectors** ทุกทิศทางและทุก spatial frequency — ดูเหมือน Gabor filter เหมือนที่วัดได้ใน V1 ของแมวและลิงจริง ๆ

ความหมาย: สมองเรียนรู้ edge detectors ไม่ใช่เพราะ hardwired แต่เพราะนั่นคือ **representation ที่ information-efficient ที่สุดสำหรับภาพธรรมชาติ** ธรรมชาติของภาพ (edges ยาว ๆ เกิดขึ้นบ่อย texture ซ้ำกัน) ทำให้ sparse code ที่ดีคือ edge detectors เสมอ

### SDR: push sparsity ไปสุดขีด

Numenta (Jeff Hawkins) เอา insight ของ Olshausen ไปไกลกว่ามาก สมองจริง ๆ ไม่ใช้ "ค่อนข้าง sparse" — มัน **extremely sparse** นิวรอน cortex ยิงประมาณ **1-2%** ของเวลาทั้งหมด Hawkins ถาม: ถ้า encode ข้อมูลด้วยความ sparse แบบนั้น มัน work ยังไง?

**SDR (Sparse Distributed Representation):** binary vector ขนาดใหญ่ (เช่น 2048 bits) ที่ active แค่ ~**2% (40 bits)**

คุณสมบัติที่พิสูจน์ได้ทางคณิตศาสตร์:

**1. Capacity มหาศาล:**
จำนวน SDR ที่เป็นไปได้ = C(2048, 40) ≈ 10^60 patterns มากกว่าจำนวน atoms ในจักรวาลโดยหลายเท่า สำหรับงานที่มีคลาสไม่กี่พัน นี่คือ effectively unlimited

**2. Noise tolerance:**
ถ้า 10% ของ active bits flip (4 จาก 40) การจำแนกยังถูกต้อง เพราะ overlap ยังสูง ถ้า active bits overlap มากกว่า 50% คุณรู้ว่ามันคือ pattern เดียวกัน Noisy input ≠ wrong answer

**3. Similarity by overlap:**
สอง SDR "คล้ายกัน" ก็ต่อเมื่อมี overlap สูง (Jaccard similarity = |A∩B| / |A∪B|) ไม่ต้องคำนวณ cosine similarity แพง ๆ แค่ count bits — ทำได้ใน analog ด้วย bitwise AND + popcount

**4. Distributed แต่ resilient:**
ไม่มี bit เดียวที่ critical ถ้า unit หนึ่งตาย (device failure) รูปแบบอื่น ๆ ยังทำงานได้ เพราะ 39 bits ที่เหลือยังเพียงพอสำหรับ matching

### สำหรับเรา

Sparse coding คือ **mathematical derivation ว่าทำไม substrate ของคุณถึงถูก** ถ้าคุณ constrain activation ให้ sparse ด้วย goodness threshold dictionary ที่เรียนรู้ได้จะลู่เข้าสู่ features ที่มีความหมาย — เหมือนที่ V1 ลู่เข้าสู่ edge detectors

SDR properties map โดยตรงสู่ substrate ของคุณ:
- **Noise tolerance = PVT tolerance:** capacitor drift และ device mismatch ทำให้บาง bits flip — แต่ถ้าโค้ด sparse พอ (2%) มัน robust โดยธรรมชาติ drift 10% ใน voltage ที่ active bits ยังไม่เปลี่ยน 50% ของ bits
- **Similarity by overlap = LUT matching:** hippocampus LUT ต้องหา nearest prototype การ match ด้วย bit overlap นั้นถูกมาก (AND + count) และ map ได้โดยตรงกับ crossbar operation
- **Capacity:** ด้วย units จำนวนพอสมควรที่ active 2% คุณมี representation space มากพอสำหรับทุก task เฟส 1

**คำถามปฏิบัติ:** ใน SCFF sparsity เกิดยังไง? goodness threshold กด activation ต่ำ แต่ถ้าอยากได้ SDR จริง ๆ ต้องเพิ่ม **k-winner-take-all**: เก็บ k units ที่มี activation สูงสุด zero ที่เหลือ มันคือ 1 operation ที่ทำได้ใน analog (comparator + inhibit circuit) และ k คือ knob ที่ set sparsity ตามต้องการ

---

## VQ-VAE — เปลี่ยนสัญญาณแอนะล็อกให้เป็นสัญลักษณ์ไม่ต่อเนื่องที่เสถียร

*van den Oord, Vinyals & Kavukcuoglu, NeurIPS 2017 ([arXiv 1711.00937](https://arxiv.org/abs/1711.00937)).*

### ปัญหาของ VAE: ความต่อเนื่องทำให้ blur

VAE เทรนโดยบังคับให้ latent space เป็น Gaussian distribution ปัญหา: ถ้าคุณ sample จาก Gaussian แล้ว decode ออกมา ภาพที่ได้จะ **blur** — เพราะ decoder ต้อง average over ความไม่แน่นอนใน latent space จุด z ที่ใกล้กันใน latent space อาจ correspond กับภาพที่ต่างกันมาก decoder จึงสร้าง "ค่าเฉลี่ย" ที่ไม่ตรงกับอะไรจริง ๆ

VQ-VAE แก้ด้วยการ **บังคับให้ latent เป็น discrete** — snap ไปยัง codeword ที่ใกล้ที่สุดในทุก step

### กลไก: Nearest-Neighbor ใน embedding space

**Step 1 — Encode:**
`E(x) → z_e ∈ R^d` — continuous vector จาก encoder

**Step 2 — Quantize:**
หา nearest codeword ใน codebook `C = {e_1, ..., e_K}`:
```
z_q = e_{k*}   where   k* = argmin_k  ||z_e − e_k||²
```
Output คือ **discrete token** k* และ codeword vector z_q

**Step 3 — Decode:**
`D(z_q) → x̂` — reconstruction จาก discrete code

**ปัญหา: gradient ผ่าน argmin ไม่ได้**
argmin ไม่ differentiable แก้ด้วย **straight-through gradient estimator:** ใน forward pass ใช้ z_q; ใน backward pass ส่ง gradient ผ่านราวกับ quantize เป็น identity: `∂L/∂z_e ≈ ∂L/∂z_q` (copy gradient ข้ามการกระโดด)

**Loss function:**
```
L = ||x − D(z_q)||²    (reconstruction)
  + ||sg[z_e] − z_q||²  (ดัน codebook entries หา encoder outputs)
  + β·||z_e − sg[z_q]||²  (commitment loss — ดัน encoder หา codebook)
```
`sg` = stop gradient, β=0.25

**Codebook update:** ใช้ exponential moving average แทน gradient (เสถียรกว่า):
```
e_k ← decay·e_k + (1−decay)·mean(z_e ที่ assign ให้ e_k)
```
แต่ละ codeword คือ running centroid ของ encoder outputs ที่ assigned ให้มัน

### ผลที่ได้

- Image generation: คมชัดกว่า VAE มาก เพราะ decoder ไม่ต้อง average — แต่ละ code correspond กับ cluster ของ inputs ที่ "เหมือนกัน"
- VQ-VAE codes สามารถ model ด้วย PixelCNN (autoregressive model) เพื่อ generate ภาพใหม่ → framework นำไปสู่ DALL-E
- VQ-VAE-2 (2019): hierarchical codebooks (global + local codes) → คุณภาพสูงมาก ใกล้เคียง GAN บน ImageNet
- Audio: speech codecs ปัจจุบัน (EnCodec, SoundStream) ใช้ VQ เพื่อ compress audio เป็น discrete tokens

### สำหรับเรา

**ความเชื่อมโยงที่ 1 — Codebook = LUT ที่เรียนรู้ได้:**
"snap ไปยัง nearest prototype" คือสิ่งที่ hippocampus LUT ของคุณทำ — ยกเว้นว่า LUT ของคุณต้องถูกสร้างขึ้น VQ-VAE บอกวิธีเรียนรู้ prototypes นั้น: ให้แต่ละ prototype update ด้วย EMA ของ inputs ที่ assigned ให้มัน นั่นคือ online clustering ที่ไม่ต้องมี backward pass — เหมาะกับ on-chip learning

**ความเชื่อมโยงที่ 2 — Discretization เป็น analog error correction:**
Analog capacitor ดริฟต์ แต่ถ้าทุก "รอบ sleep" คุณ snap activation ไปยัง nearest codeword ที่เสถียร คุณได้ **quantization-as-error-correction** voltage ที่ดริฟต์ไป 10% จะยัง snap ไปยัง codeword เดิม ตราบใดที่ drift น้อยกว่า separation ระหว่าง codewords ระบบ self-correcting ตรงนี้คือเหตุผลสำคัญว่าทำไม sleep consolidation ถึงเป็น idea ที่ดี — มันคือ VQ step ที่เกิดขึ้น periodic

**ความเชื่อมโยงที่ 3 — Nearest-match คือ crossbar operation:**
`argmin_k ||z_e − e_k||²` ขยายออกได้เป็น `argmax_k (2z_e·e_k − ||e_k||²)` ถ้า codebook normalized: ≈ `argmax_k z_e·e_k` = **dot product กับทุก codeword พร้อมกัน** = single crossbar sweep LUT matching คือ operation ที่ substrate ของคุณทำได้แบบ native และ cheap ที่สุด

---

## Information Bottleneck — หลักการของ representation ที่ซื่อตรง

*Tishby, Pereira & Bialek, 1999 ([arXiv 0004057](https://arxiv.org/abs/physics/0004057)); เวอร์ชัน deep: Tishby & Zaslavsky, ICLR 2015 ([arXiv 1503.02406](https://arxiv.org/abs/1503.02406)).*

### คำถาม: representation ที่ดีคืออะไรกันแน่?

ปัญหาที่ทุกวิธีข้างต้นพยายามแก้โดยไม่ได้พูดตรง ๆ คือ: **representation ที่ดีมีนิยามอะไร?** VICReg บอก "อย่า collapse อย่าซ้ำซ้อน" Barlow Twins บอก "ลด redundancy" I-JEPA บอก "ทำนายใน feature space" แต่มีกรอบทฤษฎีที่รวมทั้งหมดนี้ไว้ด้วยมั้ย?

Information Bottleneck คือคำตอบ

### กรอบทฤษฎี

กำหนด:
- X = input
- Y = label / target (สิ่งที่อยากทำนาย)
- Z = representation ที่เรียนรู้ได้

เราอยากได้ Z ที่ทำสองอย่างพร้อมกัน:
1. **ทำนาย Y ได้ดี:** I(Z;Y) สูง — Z มีข้อมูลเกี่ยวกับ task
2. **บีบอัด X ให้มากที่สุด:** I(X;Z) ต่ำ — Z ไม่จำ input ดิบมากเกินจำเป็น

Optimization problem:
```
min_Z  I(X;Z) − β·I(Z;Y)
```
β ควบคุม trade-off ระหว่าง compression และ predictiveness

ตีความ: representation ที่ดีที่สุดคือตัวที่ **ลืมอินพุตให้มากที่สุด** ขณะ **ยังจำทุกอย่างที่เกี่ยวกับ task** การเรียนรู้ที่ดีคือ *การลืมสิ่งที่ไม่เกี่ยวข้อง*

### Deep Learning version — controversy และ ของจริง

Tishby & Zaslavsky 2015 อ้างว่า SGD ทำ IB optimization โดยปริยาย โดยผ่านสองเฟส:
- **Phase 1 (fitting):** I(Z;Y) เพิ่มขึ้น — เรียนรู้ task
- **Phase 2 (compression):** I(X;Z) ลดลง — ลืมรายละเอียด input ที่ไม่จำเป็น

นี่ controversial: งานหลัง (Saxe et al. 2019) แสดงว่า compression phase มีจริงเฉพาะใน networks ที่ใช้ saturating activations (tanh, sigmoid) ไม่ใช่ ReLU สรุป: "SGD เรียน IB โดยปริยาย" ไม่ใช่ general truth แต่กรอบ IB เอง ยังสะอาดและ useful ในฐานะ **design criterion**

### สำหรับเรา

IB ให้ **คำนิยามที่แม่นยำ** ของสิ่งที่คุณอยากทำ

"**โมเดลหลอกตัวเอง**" ใน IB terms:
- **Shortcut learning:** I(X;Z) สูงเกินไป — โมเดลจำรายละเอียด spurious ของ input (background color, texture hacks)
- **Collapse:** I(Z;Y) ต่ำเกินไป — representation ไม่มีข้อมูลเกี่ยวกับ task
- **Overfit:** I(Z;Y) สูงบน training ต่ำบน test — generalize ไม่ได้

ทำไม I-JEPA ดีกว่า MAE ใน IB terms: MAE บังคับ I(X;Z) สูง (ต้องจำทุก pixel); I-JEPA ปล่อย I(X;Z) ต่ำ (ลืม noise จำ structure) feature ที่ compression-efficient generalize ดีกว่า

ทำไม VICReg/Barlow ป้องกัน collapse ใน IB terms: embedding เป็นศูนย์ทั้งหมด = I(Z;Y) = 0 ไม่มีข้อมูลอะไรเลย variance floor กัน I(Z;Y) → 0

สำหรับ SCFF: goodness training พยายาม maximize I(Z;Y) สำหรับ proxy task Y = "positive or negative" แต่ไม่ได้ minimize I(X;Z) โดยตรง ถ้า SCFF ดัน overfit รายละเอียด input ลอง **เพิ่ม L1 regularization บน activations** — นั่นคือ approximation ของการ minimize I(X;Z) บังคับให้ representation compact

---

## ฝั่งเอาต์พุต โดยสังเขป — label ที่มีน้อย (weak labels)

"อินพุตที่ label ไม่เยอะ" มีคำถามฝั่งเอาต์พุตด้วย กรอบที่เชื่อถือได้:

**Self-supervised pretrain + supervised head จิ๋ว:** การแบ่ง SCFF+GD ของคุณ *คือ* อันนี้ — เข้ารหัสโดยไม่ใช้ label อ่านผลด้วย label น้อย ทุก paper ข้างต้นยืนยันว่านี่คือทิศทางที่ถูก

**Semi-supervised:** มี label นิดเดียว + ไม่มี label เยอะ — เช่น FixMatch (2020): เทรน supervised บน labeled data + pseudo-label บน unlabeled ถ้า confidence สูงพอ เป็น simple baseline ที่แข็งแกร่ง

**Contrastive/metric output:** แทน output เป็น "class" ให้ทำนาย "อยู่ใกล้ anchor ที่ถูก" เหมือน Distance-Forward ใน `../../papers/phase1-2/distance-forward.md` — เข้ากับ SCFF เป๊ะ

กฎที่รวมทั้งหมด: **ให้ label จัดรูปเฉพาะก้าวสุดท้ายที่ถูก; ให้โครงสร้างทำส่วนที่เหลือ** นั่นคือ 80/20 ของคุณอยู่แล้ว

---

## รูปร่างของคำตอบ (ไฟล์นี้)

สำหรับเรา: **ทำนายในพื้นที่ representation อย่าทำนายอินพุตดิบ** (I-JEPA) โมเดลจะโกหกด้วยการจำ noise ไม่ได้; **กัน collapse อย่างชัดเจน** ด้วยพื้น variance + decorrelation (VICReg/Barlow Twins) — ทั้งคู่เป็นค่าสถิติแบบโลคอลที่เป็นมิตรกับคาปาซิเตอร์; **จัดรูปโค้ดให้ sparse และมิติสูง** (sparse coding / SDR) เพื่อความจุ ความทน noise และ similarity-by-overlap (= LUT ของคุณ); **ทำให้ไม่ต่อเนื่องเมื่อต้องการสัญลักษณ์เสถียร** (VQ) — codebook update = online clustering; และเล็งไปที่ **information bottleneck** โดยหลักการ — ลืมสิ่งไม่เกี่ยวข้อง คงสิ่งที่เกี่ยวกับงาน SCFF เป็นตัวเข้ารหัสในตระกูลนี้อยู่แล้ว เปเปอร์เหล่านี้คือวิธีทำให้มันซื่อตรงตอนที่มันเริ่มโคลงเคลง
