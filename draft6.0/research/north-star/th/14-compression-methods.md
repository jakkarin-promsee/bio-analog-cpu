# 14 — บีบอัดจริง ๆ ทำยังไง (วิธีต่าง ๆ, สองกลไกของคุณ, และเดิมพันบนชิป)

> `13-compression.md` บอก *ว่าทำไม* การบีบอัดถึงเป็นไปได้ (การเรียนรู้ **คือ** การบีบอัด; งานเล็กจิ๋ว; slack มีจริงและแชร์ได้) ไฟล์นี้คือ *ทำยังไง* — วิธีที่เป็นรูปธรรมและเชื่อถือได้ — บวกกับการจับคู่ตรงๆ ของ **สองกลไกของคุณ** (เลเยอร์ข้ามชั้นที่ "ขยายช่วง" และ "ทริกเกอร์ clipping") และทำไมมันถึง **เป็นความเป็นความตาย** ไม่ใช่ทางเลือก สำหรับชิป resident-weight

---

## เดิมพัน: สำหรับคุณ การบีบอัดคือการเอาตัวรอด ไม่ใช่การปรับให้ดีขึ้น

สำหรับโมเดลบน GPU การบีบอัดเป็นของมีก็ดี (ดาวน์โหลดเล็กลง, อนุมานเร็วขึ้น) แต่สำหรับ **ชิปคุณมันคือทั้งเกม**: resident-weight แปลว่า **ทุก weight ต้องลงบนซิลิคอนได้จริงทางกายภาพ และไม่เคยออกไปไหน** ถ้าโมเดลบีบอัดไม่ได้ มันก็ลงไม่ได้ และสถาปัตยกรรมก็ไม่มีอยู่จริง คุณพูดเองว่า: "ตอนนี้เราทำการบีบอัดแค่ในซอฟต์แวร์" เป้าหมายคือการบีบอัด **เชิงโครงสร้าง (structural)** — ตาข่าย *เกิดมา* เล็กเพราะ *รูปแบบ* ของมัน (sparsity, low-rank, การแชร์, superposition) บีบอัดในตัว — ไม่ใช่ตาข่ายใหญ่ที่ไปบีบทีหลัง วิธีข้างล่างคือเมนู เรียงจาก "บีบทีหลัง" ไปสู่ "เกิดมาเล็ก"

---

## Pruning / Deep Compression — เอา slack ออก (เก็บเกี่ยว lottery ticket)

*Han, Mao & Dally, ICLR 2016 ([arXiv 1510.00149](https://arxiv.org/abs/1510.00149)); ต้นกำเนิด: LeCun, "Optimal Brain Damage," 1989.*

### ปัญหาที่มันแก้

AlexNet (2012) ทำงานได้ดีแต่มีขนาด 240 MB — บน mobile และ embedded system ใช้ไม่ได้เลย คำถามที่ Han ถามคือ: *โมเดล production มันใหญ่เกินจริงไหม? เราตัดมันลงได้แค่ไหนโดยไม่เสียความแม่นยำ?* ไม่ใช่แค่ prune ครั้งเดียว แต่ทั้งไปป์ไลน์ที่บีบทุกบิตออกมา

### กลไกจริงๆ

ไปป์ไลน์สามขั้น ต่อเนื่องกัน:

**ขั้นที่ 1 — Iterative Pruning:**
เทรน network ปกติก่อน → กำหนด threshold τ → ลบ connection ทั้งหมดที่ |weight| < τ → fine-tune network ที่ sparse แล้วจนกลับมาได้ accuracy เดิม → ทำซ้ำ

เกณฑ์ที่ Han ใช้คือ magnitude-based แบบ **global** (ไม่ใช่ per-layer) เพราะ layer ต่างๆ ทน pruning ต่างระดับ — fully connected layer ทน 90%+ แต่ conv layer ทนแค่ 30–50% global threshold จึงให้ผลดีกว่าการบังคับทุก layer ให้ prune เท่ากัน

**ขั้นที่ 2 — Quantization + Weight Sharing:**
ใช้ k-means clustering บน weight ที่รอดมาจากการ prune (เช่น k=256 cluster ต่อ layer)
แทนที่จะเก็บ float 32-bit ต่อ weight เก็บแค่:
- **Codebook:** centroids k ตัว (256 ค่า เก็บใน 8 bit)
- **Index:** เลข cluster 8-bit ต่อ weight แต่ละตัว (แทน float 32-bit เดิม)

ตอน fine-tune: gradient ของ weight ทุกตัวใน cluster เดียวกันถูก **sum รวมกัน** แล้วอัปเดต centroid นั้น — เรียกว่า "soft weight sharing" หมายความว่า centroid เรียนรู้ค่าที่เหมาะที่สุดสำหรับทุก connection ในกลุ่ม ผล: 32 bits → 8 bits per weight แต่เพราะ sparse ด้วย effective bits ต่ำกว่านั้น

**ขั้นที่ 3 — Huffman Coding:**
ค่า weight ที่พบบ่อย (centroid ใกล้ศูนย์ — เพราะ distribution ของ weight มักจะ bell-shaped รอบศูนย์) encode ด้วย bit น้อย ค่าที่หายาก encode ด้วย bit มาก (entropy coding แบบเดียวกับ jpeg, zip) ลดขนาดได้อีก 20–30%

### ผลที่น่าตื่นเต้น

| โมเดล | ขนาดเดิม | หลัง Deep Compression | Compression ratio |
|---|---|---|---|
| AlexNet | 240 MB | **6.9 MB** | **35x** |
| VGG-16 | 552 MB | **11.3 MB** | **49x** |

accuracy ลดไม่ถึง 1% ทั้งคู่

ที่ทำให้เปเปอร์นี้สำคัญกว่าแค่ compression tool: มันพิสูจน์ว่า **slack ที่ Lottery Ticket สัญญาไว้มีจริงและเอาออกได้จริง** ขั้น pruning เก็บแค่ 10–20% ของ weight โดยไม่เสีย accuracy — ยืนยันว่า 80–90% เป็น overhead ของ optimization landscape ไม่ใช่ของ representation

### สำหรับเรา

*ไอเดีย* ถ่ายโอนได้ แต่ *กลไก* เปลี่ยนบน substrate แอนะล็อก:

- **Pruning แบบ analog:** ไม่ใช่ตัด connection ออกด้วย mask แต่ **ปล่อยให้ Scap ที่ magnitude ต่ำ leak เป็นศูนย์** ใน sleep cycle แล้วหยุด refill leaky capacitor ทำ pruning โดยธรรมชาติ คุณแค่ควบคุมว่า threshold magnitude เท่าไหร่ถึงจะ "ยอมรั่ว"
- **Weight sharing แบบ analog:** หลาย Scap อ้างอิง **reference voltage เดียวในรีจิสเตอร์ refill-SRAM** — analog ของ codebook ค่าใดค่าหนึ่งถูก share ข้าม synapse หลาย connection กลไก refill ของคุณเป็น primitive การแชร์อยู่แล้ว
- **Sleep cycle = prune-and-consolidate:** เรียนแบบ over-provisioned ตื่นอยู่ → prune slack ใน sleep → ปล่อย capacity กลับ → ใช้ใน task ถัดไป

ข้อควรระวัง (พูดตรงๆ): การ prune ลงสู่ sparse mask ตายตัวสู้กับ continual learning — ถ้า mask ล็อค connections ที่จำเป็นสำหรับงานใหม่ก็แย่ จับคู่กับ `5-continual.md` เพื่อให้ capacity ที่ปลดออกไปยัง task *ใหม่* ไม่ใช่ตายค้างไว้

---

## Knowledge Distillation — บีบอัด *ความสามารถ* ไม่ใช่ weight

*Hinton, Vinyals & Dean, 2015 ([arXiv 1503.02531](https://arxiv.org/abs/1503.02531)).*

### ปัญหาที่มันแก้

BERT (340M parameters) เก่งมาก แต่ inference บน mobile ไม่ได้ ปัญหาไม่ใช่แค่ขนาด ถ้าเทรน model เล็กตั้งแต่ต้น (เช่น 5M parameters) จาก hard labels → ได้ผลแย่กว่า BERT มาก ทั้งๆ ที่ BERT น่าจะ "รู้" อะไรบางอย่างที่ถ่ายโอนได้ คำถาม: *จะ "ถ่าย" ความรู้จาก model ใหญ่ (teacher) ไปยัง model เล็ก (student) ได้ยังไง? เพราะเหตุใด teacher ถึงรู้มากกว่าที่ hard label บอก?*

### กลไกจริงๆ

**แทนที่จะเทรน student ด้วย hard labels → เทรนด้วย soft outputs ของ teacher**

สมมติงาน 10-class classification:
- **Hard label:** [0, 0, 0, 1, 0, 0, 0, 0, 0, 0] (one-hot สำหรับ class 3)
- **Soft label จาก teacher:** [0.001, 0.003, 0.02, 0.85, 0.08, 0.001, 0.02, 0.01, 0.01, 0.005]

ความแตกต่างของ probability ในตัวเลข 0.08, 0.02, 0.01 เหล่านั้นคือ **"dark knowledge"** — teacher กำลังบอกว่า "class 4 คล้าย class 3 มากกว่า class 1 ที่ไม่เกี่ยวกันเลย" ข้อมูลนี้ไม่มีใน hard label แต่อยู่ใน soft label และ student เรียน **โครงสร้างของ input space** จากมัน

**Temperature scaling** เพื่อทำให้เห็น dark knowledge ชัดขึ้น:
```
p_i(T) = exp(z_i / T) / Σ exp(z_j / T)
```
T = 1 → normal softmax (ผล: winner-takes-almost-all, dark knowledge เบลอ)
T = 5–20 → distribution "นุ่ม" มากขึ้น (gap ระหว่าง class เล็กลง → student เรียน relationship ระหว่าง class ชัดขึ้น)

**Loss function รวม:**
```
L = α · CE(y_hard, p_student) + (1-α) · CE(p_teacher(T), p_student(T)) · T²
```
(ต้องคูณ T² ชดเชย scale ของ gradient ที่ลดลงเมื่อ T สูง)

ขั้นตอนทั้งหมด:
1. เทรน teacher ใหญ่ปกติ
2. รัน teacher บน training data → เก็บ soft probability ต่อ example
3. เทรน student ด้วย loss ข้างบน พร้อม T เดียวกันทั้งสองฝั่ง
4. Inference: ใช้ student เดี่ยวๆ ที่ T=1

### ผลที่น่าตื่นเต้น

- **DistilBERT** (66M parameters, 40% ขนาด BERT): ได้ **97% ของ BERT บน GLUE** benchmark, inference เร็วกว่า 60%
- DistilBERT ทำได้ดีกว่าเทรน BERT-small จากศูนย์อย่างมีนัยสำคัญ — proof ว่า dark knowledge จาก teacher มีค่าจริง
- T สูง (20–30) ให้ผลดีกว่า T=1 ใน task ที่ class มีความสัมพันธ์กัน เช่น NLP และ speech recognition
- **Ensemble distillation:** distill จาก ensemble ของหลาย teacher ลงใน student เดียว — student ได้ความหลากหลายของ teacher ทั้งหมดโดยไม่ต้องรัน ensemble ตอน inference
- ใช้ได้กับ representation distillation (ไม่ใช่แค่ output): บังคับให้ hidden state ของ student คล้าย teacher → transfer อย่างละเอียดมากขึ้น

### สำหรับเรา

นี่คือการบีบอัด *ความรู้* และคุณมีรูปร่างของมันอยู่แล้ว:

- **SCFF front ของคุณคือ teacher ตัวใหญ่:** รวย, over-provisioned, unsupervised — มันเรียนโครงสร้างของ input space โดยไม่มี label มี "dark knowledge" ของ feature relationships อยู่ใน representation
- **GD readout ของคุณคือ student:** บีบความรู้ของ SCFF ลงเป็นรูปแบบกระชับที่มี label เทียบ class
- **Sleep cycle = distillation session:** สมองช้าของชิป distill ประสบการณ์วันนี้ (fast SCFF updates) ลงเป็น resident weight ที่ compact ระหว่าง sleep — ครู (กิจกรรมวันนี้) → นักเรียน (weight ที่ consolidate แล้ว)

Dark knowledge ยังเป็นข้อโต้แย้งอีกชั้น: **การแจกแจงนุ่มๆ เต็มๆ พกโครงสร้าง; hard label ทิ้งมันไป** — นี่คือ *เหตุผล* ว่าทำไมโมเดลคุณควรเรียนจากเป้าหมาย representation/soft ไม่ใช่ hard label เพียงอย่างเดียว (ลับ `7-encoding.md`)

---

## Low-rank factorization / LoRA — เก็บปริภูมิย่อยเล็ก ไม่ใช่เมทริกซ์ใหญ่

*Low-rank NN compression (คลาสสิก); LoRA: Hu et al., 2021 ([arXiv 2106.09685](https://arxiv.org/abs/2106.09685)).*

### ปัญหาที่มันแก้

GPT-3 (175B parameters) fine-tune บน GPU เดียวไม่ได้ — แค่เก็บ gradient ของ full parameters ก็ออกนอก VRAM แล้ว (ต้องการ ~1.2 TB) แต่ถ้าไม่ fine-tune ก็ได้แค่ general capability ไม่ใช่ domain-specific LoRA ถามว่า: *การ fine-tune จำเป็นต้องอัปเดตทุก parameter จริงๆ ไหม หรือ update ที่มีประโยชน์อยู่ใน subspace เล็กๆ ใน weight space?*

### กลไกจริงๆ

**Insight จาก SVD:** Matrix weight W ขนาด D×D สามารถ decompose ได้ด้วย Singular Value Decomposition: W = U·Σ·Vᵀ ถ้า singular values ใน Σ ลดหลั่นเร็วมาก (ค่าใหญ่แค่ไม่กี่ตัวแรก) → W ≈ U_r·Σ_r·V_rᵀ ที่ rank r ต่ำ เก็บ r(D+D) = 2rD ตัวเลขแทน D² ตัว ถ้า r ≪ D ก็ประหยัดมาก

**LoRA ไม่ decompose W เดิม** (SVD หนัก) แต่ **freeze W₀** แล้วเรียน update แยก:

```
Forward: y = W₀·x + ΔW·x = W₀·x + (A·B)·x

A: matrix D×r  (init: random Gaussian small)
B: matrix r×D  (init: zero → ΔW เริ่มที่ 0 ไม่กระทบ pretrained behavior)
r ≪ D  (LoRA ใช้ r = 1, 2, 4, 8)
```

ระหว่าง training เรียนแค่ A และ B — W₀ ไม่เปลี่ยนเลย ตอน inference: merge กลับ W = W₀ + A·B แล้วเอา A, B ออก (zero extra latency cost)

**ทำไมถึงเวิร์ก?** เพราะ **intrinsic dimension ของ fine-tuning task ต่ำมาก** (`13-compression.md`) การเปลี่ยนจาก "general language model" เป็น "domain-specific" ต้องการ update ใน subspace เล็กๆ ใน weight space เท่านั้น LoRA rank 1 บน GPT-3 175B parameters เก็บแค่ **~0.01% ของ parameters เดิม** แต่ยังได้ผลเทียบเท่า full fine-tune

**Rank selection:** สูงกว่าไม่ได้ดีกว่าเสมอ — rank 4–8 มักดีกว่า rank 64 เพราะ low-rank constraint ทำหน้าที่เป็น regularization บังคับ update อยู่ใน subspace ที่มีประโยชน์

### ผลที่น่าตื่นเต้น

- LoRA rank 4 บน GPT-3 175B → ผลเทียบเท่า full fine-tune บน GLUE, SuperGLUE, commonsense reasoning
- Training memory ลดจาก **~1.2 TB → ~12 GB** — fit บน GPU เดียวได้
- LoRA adapters (ค่า A, B) สำหรับ task ต่างๆ สามารถ swap ออก-เข้าได้ที่ runtime โดยไม่ต้องเก็บ full model หลายชุด — ประหยัด storage มหาศาลในระบบ multi-task
- Adapter merging: LoRA จาก task A กับ task B สามารถ interpolate กัน (A_merged = A_A + A_B, B_merged = B_A + B_B) เพื่อสร้างโมเดลที่ถนัดทั้งสองงาน

### สำหรับเรา

Low-rank คือการบีบอัด **เชิงโครงสร้าง** และเป็นมิตรกับแอนะล็อก: W ≈ A·B แปลว่า crossbar ใหญ่กลายเป็น **crossbar เล็กสองตัวต่ออนุกรม** — (n×r) แล้ว (r×m) ใช้ r(n+m) Scap แทน n·m ตัว ถ้า r ≪ n,m ประหยัดพื้นที่มหาศาล (ต้นทุน `12-dataflow.md`)

มันต่อตรงกับไอเดีย butterfly/Monarch ใน `11-connectivity.md`: low-rank, butterfly, และ grouped ล้วนเป็นการบีบอัดแบบ **structured-matrix** รูปร่างต่างกันของ "อย่าสร้าง dense n×m" การเคลื่อนไหวที่รวมทั้งหมดสำหรับชิปคุณ: **อย่าสร้าง crossbar เต็ม; สร้างแบบมีโครงสร้าง (low-rank / butterfly / grouped)** — นั่นคือการบีบอัดในฐานะ *โทโพโลยีวงจร* ไม่ใช่ post-processing

---

## Weight sharing / hashing — หลายการเชื่อมต่อ ค่าที่เก็บไว้ค่าเดียว

*HashedNets: Chen et al., 2015 ([arXiv 1504.04788](https://arxiv.org/abs/1504.04788)); และขั้น quantization ของ Deep Compression.*

### ปัญหาที่มันแก้

fully connected layer D×D มี D² weight — เพิ่ม D สองเท่า เพิ่ม parameter สี่เท่า และก่อน training เราไม่รู้เลยว่า weight ไหนซ้ำซ้อนกัน (ต้องรอ prune ทีหลัง) HashedNets ถามว่า: *ถ้า force ให้ weight หลาย pair ใช้ค่าเดียวกันตั้งแต่ต้นล่ะ — โดยไม่ต้องรู้ล่วงหน้าว่า pair ไหนควรเหมือนกัน?*

### กลไกจริงๆ

ก่อน training สุ่มสร้าง **hash function** h: (i,j) → {1, 2, ..., K} ที่ map คู่ (input_index, output_index) ไปยัง bucket K buckets

แทนที่จะมี parameter W[i,j] = real number แยกต่อแต่ละคู่ มีแค่ **parameter ชุดเล็ก c[1], c[2], ..., c[K]** (K ≪ D²):
```
W[i,j] = c[h(i,j)]
```

Network ยังมี connections เยอะแบบเดิม (expressivity ยังครบ) แต่ *storage* เล็กกว่ามาก เพราะ edge เป็นพันๆ อ่าน parameter ชุดเดียวกัน

**Backprop ด้วย shared weights:**
```
gradient(c[k]) = Σ_{(i,j): h(i,j)=k}  ∂L/∂W[i,j]
```
รวม gradient จากทุก edge ที่ hash ไปยัง bucket k เดียวกัน แล้วอัปเดต c[k] จาก gradient รวมนั้น เทรนได้ด้วย backprop ปกติ ไม่ต้องแก้อะไร

**Hash collision** (edge หลายเส้นใน bucket เดียว) ดูเป็นปัญหาแต่จริงๆ ไม่แย่: ถ้า edge สองเส้นที่ share weight ทำงาน "ต่างกัน" (gradient ต่างเครื่องหมาย) พวกมันหักล้างกัน gradient รวมเป็นศูนย์ centroid ไม่เปลี่ยน; ถ้าทำงาน "คล้ายกัน" พวกมันสร้างเสริมกัน centroid อัปเดตอย่างมีประสิทธิภาพ ในทางเฉลี่ย network เรียน parameter ที่เหมาะกับ bucket ทั้งก้อน

### ผลที่น่าตื่นเต้น

- HashedNets บีบอัด **16x บน fully connected layers** ของ network สำหรับ MNIST/CIFAR โดยแทบไม่เสีย accuracy
- K = D²/16 (บีบ 16x) ยัง work ได้ดีเพราะ randomness ของ hash ทำให้ edge ต่างๆ กระจายทั่ว bucket ไม่มี systematic collision
- รวมกับ pruning ของ Deep Compression: weight sharing ทำ quantization (5-bit) ได้ดีกว่า naive quantization เพราะ shared weights มี gradient คุณภาพดีกว่า (รวม gradient จากหลาย edge มีความเสถียรกว่า)
- **Weight tying ใน language model:** input embedding = output projection matrix (tied weights) คือ weight sharing แบบ explicit ที่สุดขีด — standard ใน transformer และ LSTM LM ทุกตัว

### สำหรับเรา

นี่คือสัญชาตญาณ "นิวรอน/เลเยอร์ที่แชร์" ของคุณในฐานะสคีมการเก็บข้อมูล และบนแอนะล็อกมันเป็นธรรมชาติ: **หลาย Scap อ้างถึง reference voltage / ค่า SRAM ที่แชร์กันค่าเดียว** กลไก refill ของคุณเป็น primitive การแชร์อยู่แล้ว

มันบอกว่าชิปมี *การเชื่อมต่อ* รวยได้โดยไม่ต้องมี *ที่เก็บ* รวย — ชัยชนะ resident-weight เป๊ะ ผสมกับ superposition (`13`): การแชร์ *ที่เก็บ* (hashing) + การแชร์ *capacity* (superposition) คือสองแกนของการบีบอัดเดียวกัน หนึ่งอยู่ที่ hardware mapping หนึ่งอยู่ที่ representation geometry

---

## กลไม A ของคุณ = DenseNet feature reuse (ยืนยันแล้ว พร้อมข้อควรระวังที่คุณเห็น)

*DenseNet: Huang et al., CVPR 2017 ([arXiv 1608.06993](https://arxiv.org/abs/1608.06993)).*

### ปัญหาที่มันแก้

ResNet (2015) แก้ vanishing gradient ด้วย skip connection `y = F(x) + x` ได้แล้ว แต่ยังมีปัญหาหนึ่ง: feature ที่ layer ต้นๆ สร้างขึ้นถูก "กดทับ" โดย layer ถัดๆ มา และถ้า layer ลึกๆ ต้องการ low-level feature กลับมา (เช่น edge detector ที่สร้างตั้งแต่ layer 2) มันต้องสร้างมันใหม่ — waste computation Huang ถามว่า: *ถ้าเชื่อมทุก layer ไปยังทุก layer ที่ตามมาเลยล่ะ?*

### กลไกจริงๆ

**Dense block**: layer l รับ **concatenation** (ต่อกัน ไม่ใช่ sum) ของ output จากทุก layer ก่อนหน้า:

```
x_l = H_l([x_0, x_1, ..., x_{l-1}])
```

ทุก layer ยังเห็น raw feature จาก layer แรกเสมอ ไม่ใช่แค่ layer ก่อนหน้าทันที

**Growth rate k**: แต่ละ layer ผลิต feature maps ใหม่ **k ช่องเท่านั้น** (เช่น k=32) ดังนั้น layer l มี input `k₀ + (l-1)·k` channels ซึ่งเพิ่มขึ้น linear แต่เพราะ k ต่ำ (ไม่ใช่ 256 หรือ 512 แบบ ResNet) จำนวน parameters ต่อ layer น้อยมาก

**Composite function** H_l: ในเปเปอร์ใช้ BN → ReLU → 3×3 Conv (Pre-activation style) BatchNorm ก่อน conv ทุกครั้งเป็นสิ่งสำคัญ — ป้องกัน scale ของ feature จากหลาย layer ที่ต่อเข้ามา "ระเบิด" เข้าหากัน

**Transition layer** ระหว่าง dense block: 1×1 Conv + 2×2 avg pooling เพื่อลด spatial size และ "compress" channel count ลง (DenseNet-BC ลด channel 50% ทุก transition) ทำให้ network ไม่ระเบิดในแง่ channel เมื่อ block ลึกขึ้น

**ทำไม feature reuse บีบอัด?** ถ้า layer 3 สร้าง edge detector และ layer 8 ต้องการ edge detector → reuse โดยตรง ไม่ต้องเรียน edge detector ใหม่ นั่นหมายความว่า layer 8 ใช้ parameter ทั้งหมดไปกับสิ่งที่ "เพิ่มเติม" จากสิ่งที่มีอยู่แล้ว — ประสิทธิภาพ parameter สูงขึ้นมาก

### ผลที่น่าตื่นเต้น

| โมเดล | Parameters | CIFAR-10 Error |
|---|---|---|
| ResNet-1001 | 10.2M | 4.62% |
| DenseNet-BC k=12 | **0.8M** | **4.51%** |

DenseNet เล็กกว่า **12x** แต่ดีกว่า

บน ImageNet: DenseNet-121 (6.9M) เทียบเท่า ResNet-101 (44.5M) — ประหยัด 6x จาก feature reuse ล้วนๆ

ยิ่งไปกว่านั้น: DenseNet converge เร็วกว่า ResNet เพราะ gradient จาก loss ไหลตรงถึง layer ต้นๆ ผ่าน skip connections ทุกชั้น ไม่ต้องผ่าน intermediate layers

### สำหรับเรา

กลไม A ของคุณ — *ให้เลเยอร์รับอินพุตจากเลเยอร์ที่อยู่ก่อนหน้า 2 ชั้น ขยายช่วงให้ capacity ของแต่ละนิวรอนถูกจัดสรรมากขึ้น* — **คือ dense connectivity** เวอร์ชัน local (เชื่อมแค่ 2 layer แทนทั้งหมด) สัญชาตญาณถูกและมันคือสถาปัตยกรรมประสิทธิภาพระดับท็อป การ reuse ข้ามชั้นบีบอัดด้วยการ **ไม่คำนวณซ้ำ** slack ที่คุณอยากจัดสรรถูกเติมด้วยฟีเจอร์ที่ reuse แทนที่จะเป็นของใหม่ที่ซ้ำซ้อน

**และคุณยังเห็นโหมดความล้มเหลวจริงด้วยตัวเอง:** คุณพูดว่ากลไม A "อาจ diverge — อินพุตจากแต่ละชั้นหักล้างกันเองได้" นั่นคือความเสี่ยงจริงของ dense connectivity ซึ่งเป็นเหตุผลเป๊ะว่าทำไมคุณถึงประดิษฐ์กลไม B — และทำไม DenseNet ถึงใส่ BatchNorm ก่อน conv ทุกครั้ง

---

## กลไม B ของคุณ = supervised anchor (และมันคือการแก้ที่ถูกต้อง)

### ปัญหาที่มันแก้

Dense connectivity (กลไม A) ดีแต่ไม่เสถียร: ยิ่งเชื่อมหลายชั้น feature มีโอกาสรบกวนกันมากขึ้นโดยเฉพาะถ้า scale ของแต่ละ layer ต่างกัน ใน DenseNet แก้ด้วย BatchNorm ก่อน conv ทุกครั้ง แต่ในระบบ SCFF+GD ที่เรียนแบบ unsupervised+local คุณต้องการบางอย่างที่ **ยึดการ reuse ไว้กับความจริง** ไม่ใช่แค่ normalize scale

### กลไกจริงๆ

กลไม B ของคุณ — *"ทริกเกอร์ clipping" ที่ clip การผสมข้ามชั้น แล้ว **ฉีด label** เข้าไปเพื่อหยุดการ diverge* — คือ **supervised anchor / checkpoint normalization** ที่ทำสองสิ่งพร้อมกัน:

**หน้าที่ที่ 1 — Normalize/clip:** ตัดการรวม feature ที่เด้งออกจากช่วง ป้องกันฟีเจอร์ "ซุป" จากการรวมหลายชั้นโดยไม่ควบคุม (เป็น analog ของ BatchNorm ใน DenseNet) กลไมที่เทียบได้ในวรรณกรรม: **translate clip** (`11-connectivity.md`) และ **normalization layer** ระหว่าง dense block

**หน้าที่ที่ 2 — Ground ด้วย label:** ฉีด label เข้ามาเป็น anchor — บังคับให้ feature representation ที่ reuse กันนั้นยังเกี่ยวกับ "ความจริง" (ไม่ใช่แค่ "รูปแบบสถิติที่สวยแต่ไม่ตรงกับ task") feature drift ไปเป็นส่วนผสมที่ไม่ปะติดปะต่อไม่ได้

ในแง่สถาปัตยกรรมมันคือบทบาทเดียวกับ **GD checkpoint ของ draft-6.0**: SCFF block เรียนแบบ unsupervised แต่ GD readout ที่วางระหว่างบล็อก "ดึง" representation กลับมายังความจริงเป็นระยะ

งานของ Bengio et al. (Greedy Layer-wise Training 2006) ยืนยัน: การ "freeze" และ "grade" feature ที่แต่ละ layer ด้วย supervised signal ระหว่างกลาง ช่วยให้ deep network เทรนได้เสถียรกว่า end-to-end ล้วนๆ

### ผลที่น่าตื่นเต้น

ใน DenseNet: BatchNorm ก่อน conv (Pre-activation DenseNet) ทำให้ DenseNet ลึกมากๆ เทรนได้ stable ขณะที่ DenseNet ที่ไม่มี BN นั้น diverge เมื่อลึกขึ้น — proof of concept สำหรับกลไม B ว่า normalization ระหว่าง block เป็น "บังคับ" ไม่ใช่ "ทางเลือก"

ในบริบท SCFF+GD: GD checkpoint ที่วางระหว่าง SCFF block ทำหน้าที่เป็น loss anchor ซึ่งป้องกัน feature drift ที่สะสมข้ามบล็อก ยิ่ง chain ยาว ยิ่งจำเป็น

### สำหรับเรา

กลไม A+B ด้วยกันคือ **dense-reuse block + normalization ที่ยึดด้วย label** ซึ่งคือแพตเทิร์นที่ยืนยันแล้วในวรรณกรรม (DenseNet = dense block + transition layer; draft-6.0 = SCFF reuse + GD checkpoint) คุณดึงทั้งสองครึ่งออกมาใหม่: การ reuse (การบีบอัด) *และ* ตัวทำให้เสถียร (กัน diverge)

การปรับแต่งจากวรรณกรรม: ทำ clip ให้เป็น **normalization + supervised readout เล็กๆ** (n→m มีโครงสร้าง ไม่ใช่ dense n→1-per-output) วางไว้ *ระหว่าง* reuse block จุดติดบน threshold gate ตัวเดียวกับที่คุณใช้อยู่แล้ว

---

## รูปร่างของคำตอบ (ไฟล์นี้)

วิธีบีบอัด สำหรับคุณ ไม่ใช่การบีบทีหลัง — มันคือ **โทโพโลยีวงจรและวินัยการเรียนรู้** **Pruning** (สลาย slack ผ่าน leaky Scap, เรียกคืนเส้นทางประจุ) และ **weight sharing** (หลาย Scap, reference เดียว) จับคู่กับการควบคุมที่คุณสร้างไปแล้ว (การรั่ว, refill-SRAM) **Distillation** คือสิ่งที่การแบ่ง SCFF→GD ของคุณทำอยู่แล้ว (ครู front, นักเรียน readout) และสิ่งที่ sleep ควรทำ (distill ประสบการณ์วันนี้ลงเป็น weight กระชับ) **Low-rank / butterfly / grouped** คือไอเดียเดียวกัน — *อย่าสร้าง crossbar dense n×m; สร้างแบบมีโครงสร้าง* ซึ่งคือการบีบอัดในฐานะ **พื้นที่** **กลไม A ของคุณคือ DenseNet feature reuse** (~1/3 parameter ด้วยการไม่คำนวณซ้ำ) และ **กลไม B ของคุณคือตัวทำให้เสถียรที่ normalize และยึดด้วย label ซึ่งบังคับต้องมี** คุณดึงออกมาใหม่ทั้งการเคลื่อนไหวบีบอัดและสลักนิรภัยของมัน เส้นเชื่อมกับ `13`: **รูปแบบ (form) ที่เลือกมาดี (sparse + low-rank + แชร์ + superposed) เกิดมาบีบอัดแล้ว** ดังนั้นโครงสร้างเดียวกันที่ลงในชิปคือตัวที่เรียนรู้ได้ดี นั่นคืออัลกอริทึมบีบอัดในชิปที่คุณตามหา — มันไม่ใช่อัลกอริทึมเดียว มันคือ *การสร้างตาข่ายขึ้นจากโครงสร้างที่บีบอัดในตัว*
