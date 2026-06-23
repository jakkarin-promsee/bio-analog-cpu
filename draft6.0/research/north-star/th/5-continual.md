# 5 — ไม่หยุดนิ่ง / การเรียนรู้ตลอดชีวิต

> เป้าหมายที่คุณยึดมั่น: *โมเดลที่ไม่หยุดเรียนรู้ในการใช้งานจริง — เป็นแก่นแท้ของมันตลอดชีวิต ไม่ใช่เกิดมาเพื่อจบ prompt แล้วตาย* นั่นคือ **continual / lifelong learning** และมันมีศัตรูตัวกลางเพียงตัวเดียว — **catastrophic forgetting** — กับชุดแนวป้องกันที่เชื่อถือได้ไม่กี่อย่าง ตัวที่ลึกที่สุดก็คือ sleep แบบ CLS ที่คุณสร้างไปแล้ว

---

## ปัญหา Stability–Plasticity Dilemma — ตั้งชื่อปัญหา

### ปัญหาที่ลึกกว่าที่คิด

ในปี 1989 McCloskey และ Cohen ทดลองอะไรง่ายๆ: เทรน neural network ให้เรียนคณิตศาสตร์ 1+1=2, 2+2=4, ... พอเรียนเสร็จแล้วให้เรียน task ใหม่ — กลับมาทดสอบ task แรก ผล: **แทบจำไม่ได้เลย** weight ที่ encoding task แรกถูกเขียนทับโดย task สองจนเกือบหมด

ปรากฏการณ์นี้เรียกว่า **catastrophic interference / forgetting** และมันเป็นปัญหาพื้นฐานของ connectionist model ทั้งหมด: gradient descent ที่ minimize loss ปัจจุบันจะเดิน weight ไปยัง minimum ของ current task เสมอ โดยไม่สนใจว่า weight นั้นสำคัญต่อ task เก่าแค่ไหน

**กรอบ stability-plasticity**: วิธี continual learning ทุกวิธีแก้ tension นี้:
- **Plasticity**: ความสามารถเรียนรู้ task ใหม่เร็ว (update weight เสรี)
- **Stability**: ความสามารถรักษา knowledge เก่า (ต่อต้านการเปลี่ยน weight)

สองอย่างนี้ขัดแย้งกันโดยตรง — ถ้า plastic มาก ก็ลืมเร็ว ถ้า stable มาก ก็เรียนใหม่ไม่ได้ โมเดลเชิงพาณิชย์อย่าง GPT หลีกเลี่ยง dilemma นี้ด้วยการ **หยุดเรียนรู้ทั้งหมดหลัง deploy** ซึ่งเป็นสิ่งที่คุณปฏิเสธที่จะยอมรับอย่างชัดเจน

### สำหรับเรา

ประเด็น stability-plasticity ไม่ใช่ edge case สำหรับชิปของคุณ — มันคือ **ความเสี่ยงหลัก** ทันทีที่ชิปยังเรียนรู้ระหว่าง deploy

ข่าวดี: คุณมีคำตอบเชิงโครงสร้างที่แข็งแกร่งสองอย่างอยู่แล้ว:
1. **SCFF slow weights** (Scap ที่เปลี่ยนช้า) = stability baseline
2. **LUT + sleep replay** = fast storage + consolidation path

เปเปอร์ข้างล่างมาช่วยลับให้คม

---

## Elastic Weight Consolidation (EWC) — หน่วง weight ที่สำคัญ

*Kirkpatrick et al., 2017, PNAS 114:3521 ([paper](https://www.pnas.org/doi/10.1073/pnas.1611835114)).*

### ปัญหาที่มันแก้

หลังเรียน task A จบแล้ว เราอยากให้ชิปเรียน task B โดยไม่ลืม A แต่ network ไม่รู้ว่า weight ตัวไหน "สำคัญต่อ A" EWC คำตอบ: **วัดความสำคัญของแต่ละ weight สำหรับ task A แล้วทำให้มันเปลี่ยนยากขึ้นตามสัดส่วน**

### กลไกจริงๆ

หลังเรียน task A เสร็จ คำนวณ **Fisher information matrix F_A**:
```
F_{A,i} = E_{x~D_A}[(∂log p(y|x, θ)/∂θ_i)²]
```

F_{A,i} วัดว่า "ถ้าเปลี่ยน θ_i เล็กน้อย loss ของ task A เปลี่ยนมากแค่ไหน" — ค่ายิ่งสูง weight นั้นยิ่งสำคัญ ใช้ diagonal approximation (แค่ F_{A,i} per parameter ไม่ใช่ full matrix N×N) เพื่อ tractability

เมื่อเรียน task B เพิ่ม **quadratic penalty** ลงใน loss:
```
L(θ) = L_B(θ) + Σ_i (λ/2) · F_{A,i} · (θ_i - θ*_{A,i})²
```

ผล: weight ที่สำคัญต่อ A (F_{A,i} สูง) ถูกดึงให้อยู่ใกล้ค่าเดิม (θ*_{A,i}) ส่วน weight ที่ไม่สำคัญ (F_{A,i} ≈ 0) เปลี่ยนได้อิสระ

**Online EWC**: สำหรับหลาย tasks รัน Fisher estimate แบบ exponential moving average แทนที่จะสะสมทุก task แยกกัน — ทำให้ overhead เป็น O(1) แทน O(n_tasks)

### ผลที่น่าตื่นเต้น

EWC เทรน Atari 10 games เป็นลำดับ (space invaders → Pong → ...) โดยวัดว่า performance บน game เก่าเสื่อมแค่ไหน:
- Baseline SGD: รูปแบบ "อ้วก" — game ใหม่ดีขึ้น game เก่าพังทันที
- EWC: game เก่ายังรักษาได้ 60-80% หลังเรียน 10 games

ยิ่งสำคัญ: EWC ไม่ต้องเก็บข้อมูล task เก่าเลย — แค่ Fisher matrix (vector ขนาด n_parameters) ก็พอ ประหยัด memory มาก

### สำหรับเรา

EWC คือเวอร์ชันที่มีหลักการของ **plasticity gradient** — แทนที่จะ "หน่วงเลเยอร์ตามความลึก" มันคือ "หน่วงแต่ละ weight ตาม *ความสำคัญที่วัดได้*"

บน substrate: F_{A,i} คือ scalar ต่อ Scap ที่เก็บได้ใน sidecar register เล็กๆ ความสำคัญสูง → RC constant ของ Scap นั้นยาวขึ้น (resistance สูงขึ้น → weight เปลี่ยนช้าลง) ทำได้ด้วยวงจร variable resistance ที่ controlled โดย F value นี่คือ **analog implementation ของ EWC** โดยตรง

ข้อควรระวัง: F ที่คำนวณจาก task A อาจ drift ไปเรื่อยเมื่อเรียน tasks มากขึ้น โดยเฉพาะถ้า task ใหม่เปลี่ยน landscape มาก ดังนั้น EWC เป็น "แพตช์แรก" ที่ดีที่สุด แต่ระยะยาวต้องคู่กับ replay เสมอ

---

## Synaptic Intelligence & Memory-Aware Synapses — วัดความสำคัญแบบ Online

*Zenke, Poole & Ganguli, 2017 ([Synaptic Intelligence](https://arxiv.org/abs/1703.04200)); Aljundi et al., 2018 (Memory-Aware Synapses / MAS).*

### ปัญหาที่มันแก้

EWC วัด Fisher information **หลัง** task จบ ในก้าวแบบ batch แต่ชิปของคุณทำงาน **always-on** ไม่มีขอบเขต task ที่ชัดเจน จึงต้องการวิธีวัดความสำคัญ **ระหว่างที่กำลังเรียน** และโดยไม่ต้องรู้ว่า task นั้นคืออะไร

### กลไกจริงๆ

**Synaptic Intelligence (SI)**: ที่แต่ละก้าว t ระหว่างเรียน task k สะสม **path integral of gradient × weight change**:
```
ω^k_i += (∂L^k/∂θ_i) · Δθ_i
```
(gradient ของ loss คูณกับว่า weight เปลี่ยนไปเท่าไหร่จริงๆ)

พอจบ task k normalize ด้วย magnitude ของการเปลี่ยน:
```
Ω_i = Σ_k ω^k_i / ((Δθ_i^task_k)² + ξ)
```

Ω_i สูง = weight ตัวนี้ช่วยลด loss มากใน history ที่ผ่านมา → สำคัญ → ต้องปกป้อง

**Memory-Aware Synapses (MAS)**: อีก approach หนึ่ง วัด **ความไวของ output ต่อ weight นั้น** แบบ unsupervised:
```
Ω_i = (1/N) Σ_n ||∂F(x_n; θ)/∂θ_i||²
```
โดย F(x_n; θ) คือ output ของ network (ไม่ใช่ loss) ค่านี้บอกว่า "ถ้าเปลี่ยน weight ตัวนี้ output จะเปลี่ยนมากแค่ไหน?" ถ้าเปลี่ยนมาก → weight สำคัญ ไม่ต้องมี label เลย

### ผลที่น่าตื่นเต้น

SI: เรียน permuted MNIST (100 tasks แต่ละ task คือ random permutation ของ pixel) บน 50 tasks สุดท้าย performance ยังสูงกว่า baseline ที่ใช้ SGD ธรรมดาถึง 30% และทัดเทียม EWC โดยมี overhead ต่ำกว่า (compute online แทน batch)

MAS: ทำงานดีบน **Tiny ImageNet → VOC** (เปลี่ยน domain) โดยไม่มี label ของ task แรกเลย เพราะ Ω วัดจาก output ไม่ใช่ loss

### สำหรับเรา

**SI และ MAS คือ version ที่เหมาะกับ substrate มากกว่า EWC** เพราะ:

SI: "สะสม gradient × Δθ ขณะรัน" = **accumulator register ต่อ Scap** ที่ update ทุก learning step — เป็น running statistics ที่ cheap มากบน analog

MAS: "วัด output sensitivity" = **perturbation test** — ลอง perturb weight ตัวนี้เล็กน้อย ดูว่า output เปลี่ยนมากแค่ไหน ไม่ต้องมี label ไม่ต้องรู้ task boundary ทำได้ระหว่าง idle cycle (เช่น ระหว่าง "หลับ")

แนะนำ: ใช้ MAS เป็น **baseline สำหรับ importance estimation** เพราะ unsupervised + online + ไม่ต้องรู้ task boundary — ตรงกับ operating condition ของชิป always-on พอดิบพอดี

---

## Deep Generative Replay — Sleep แต่ Hippocampus *ฝันถึงข้อมูลเก่า*

*Shin, Lee, Kim & Kim, 2017 ([arXiv 1705.08690](https://arxiv.org/abs/1705.08690)).*

### ปัญหาที่มันแก้

EWC/SI แก้ catastrophic forgetting ด้วยการปกป้อง weight แต่มันมีขีดจำกัด: ถ้า task ใหม่ต้องเปลี่ยน weight สำคัญจริงๆ (เพราะ weight นั้น overlap กัน) ก็ต้องลืมบ้างอยู่ดี CLS บอกว่าวิธีที่ biological robust กว่าคือ **replay** — เอาประสบการณ์เก่ามาผสมกับใหม่ แต่จะ replay ยังไงถ้าเก็บข้อมูลดิบเก่าไว้ไม่ได้?

### กลไกจริงๆ

Deep Generative Replay ใช้ **dual-model architecture**:

**Scholar (Generator)**: generative model (GAN หรือ VAE) ที่เรียนรู้ distribution ของ task ปัจจุบัน + task ที่แล้วๆ มาจาก pseudo-samples

**Solver (Classifier/Task model)**: ตาข่ายหลักที่ทำ task จริง

เมื่อ task ใหม่ (k+1) เข้ามา:
1. Scholar generate pseudo-samples จาก distribution ที่เรียนมาก่อน → ตัวอย่างที่ "เหมือน" ข้อมูล task เก่า แต่ไม่ได้เก็บจริงๆ
2. ผสม pseudo-samples กับ real data ของ task ใหม่ (50:50 หรือ adjust ตาม task proportion)
3. เทรน Solver บน mixture นี้ → ไม่ลืม task เก่าเพราะยังเห็น "memory" ของมัน
4. Fine-tune Scholar ให้ generate ทั้ง distribution ใหม่ด้วย (progressive refinement)

Scholar ฝัน pseudo-samples ที่ไม่ใช่ข้อมูลจริงแต่มีลักษณะเหมือน → brain replay during sleep นั่นเอง

ขั้นสูง: **Continual Learning with GAN** (Shin et al.) และ **Variational Continual Learning** (Nguyen et al. 2018) ซึ่งทำ probabilistic version ของ replay โดยใช้ VI ทำให้ scholar มี posterior ที่ calibrate ได้

### ผลที่น่าตื่นเต้น

Split MNIST (เรียน digit 0-1, แล้ว 2-3, แล้ว 4-5 ฯลฯ): Generative Replay ทำ accuracy 95%+ บน task แรกแม้เรียน task ที่ 5 แล้ว เทียบ baseline EWC 85% และ SGD ธรรมดา 50%

Permuted MNIST 10 tasks: ทุกวิธีลดลงบ้าง แต่ Generative Replay รักษาได้ดีกว่า EWC เมื่อ task มากขึ้น

### สำหรับเรา

**นี่คือ upgrade path ของกลไก sleep + LUT ของคุณ**:

**ขั้น 1 (ปัจจุบัน)**: sleep replay = ดึง prototype จาก LUT แล้ว replay ผ่าน SCFF (fixed buffer)

**ขั้น 2 (เฟส 2)**: sleep = hippocampus ฝัน — M (world model) generate synthetic experience จาก distribution ที่เรียนมา แทน buffer คงที่ ซึ่งขยายได้อนันต์โดยไม่ต้องเพิ่ม memory

สังเกตว่า **M ของ World Models ทำ replay ด้วยอวัยวะเดียวกัน**: ตอนตื่น M ทำนายไปข้างหน้า (planning), ตอนหลับ M generates replay samples (consolidation) นี่คือ dual-use ที่ elegant สุดในไฟล์นี้

---

## Progressive Neural Networks — โต ไม่ใช่เขียนทับ

*Rusu et al., 2016 ([arXiv 1606.04671](https://arxiv.org/abs/1606.04671)).*

### ปัญหาที่มันแก้

ทั้งหมดที่ผ่านมาพยายาม "เรียนสิ่งใหม่ใน weight เดิม" Progressive Networks บอกว่า: **ทำไมต้องทำอย่างนั้น? ถ้า task ใหม่ต้องการ capacity ใหม่ก็แค่ *เพิ่ม* ไป**

### กลไกจริงๆ

เมื่อเรียน task 1:
```
Column 1: h^1_i = f(W^1_i · h^1_{i-1})
```

เมื่อ task 2 เข้ามา: **freeze column 1 ทั้งหมด** และเพิ่ม column ใหม่:
```
Column 2: h^2_i = f(W^2_i · h^2_{i-1} + U^2_{1,i} · h^1_{i-1})
```

U^2_{1,i} คือ **lateral connections** จาก column 1 ไปยัง column 2 ที่ layer i ทำให้ column 2 สามารถ **ดึงฟีเจอร์จาก column 1 มาใช้ซ้ำ** ได้ โดยไม่แก้ weight ของ column 1 เลย

column 1 frozen ทั้งหมด → **zero forgetting โดยโครงสร้าง** เพราะ weight เก่าไม่เคยถูกแตะ

ข้อเสีย: โมเดลโตขึ้นทุก task → ไม่ scale สำหรับ tasks จำนวนมาก

**Progressive Knowledge Base (Schwarz et al. 2018)**: เวอร์ชันที่ไม่เพิ่ม column ใหม่ทั้งหมด แต่เพิ่มแค่ "adapter" เล็กๆ ที่ lateral connection เพื่อลด parameter overhead

### ผลที่น่าตื่นเต้น

Transfer learning บน Pong → Space Invaders → Breakout: Progressive Networks เร็วกว่า train from scratch อย่างมาก โดยใช้ lateral knowledge transfer และ forgetting = zero เพราะ column เก่า frozen

Sim-to-real transfer (robot manipulation): เทรน column 1 บน simulation, column 2 บน real robot ผ่าน lateral connections → Column 2 inherit simulation knowledge โดยไม่ต้องเทรนจาก scratch บน real-world ซึ่ง sample-intensive มาก

### สำหรับเรา

สำหรับชิปที่มี fixed Scap จำนวนตายตัว ไม่สามารถ "เพิ่ม column ไม่จำกัด" แต่ **ไอเดียของ Progressive Networks ยังใช้ได้**:

**ยืมแค่ "ปกป้องตัวที่ commit แล้ว เรียนรู้ในตัวที่ว่าง"**:
- SCFF blocks บางส่วนที่ fully consolidated (importance สูงทุก weight) → freeze โดยลด learning rate ลงมาก
- Scap ที่ยังมี capacity เหลือ (importance ต่ำ) → เปิดให้ plastic เต็มที่
- สำรอง fraction หนึ่งของ Scap ไว้เป็น "expansion budget" สำหรับ knowledge ใหม่ที่ conflict กับเก่า

Lateral connection ใน analog คือ **short-range coupling** ระหว่าง blocks ที่ถูกมาก สามารถ reuse output ของ block เก่า (frozen) เป็น input เพิ่มเติมของ block ใหม่ได้โดยไม่เพิ่ม Scap

---

## รูปร่างของคำตอบ (ไฟล์นี้)

การไม่หยุดนิ่ง สำหรับเราคือ **การป้องกันสองแนวรบที่คุณสร้างไปแล้วครึ่งหนึ่ง**:

**แนวรบที่ 1 — ฝั่ง weight (stability)**:
- EWC = ไอเดียหลัก: หน่วง weight สำคัญ (plasticity gradient) แต่ถ่วงด้วยความสำคัญที่วัดได้
- SI = รูปแบบ online ที่ชิปต้องการ (สะสมระหว่างรัน ไม่ต้องรู้ task boundary)
- MAS = unsupervised version (ไม่ต้องมี label เลย ดีที่สุดสำหรับ always-on chip)

**แนวรบที่ 2 — ฝั่ง memory (plasticity ที่ controlled)**:
- Sleep replay prototype (ปัจจุบัน) = แนวป้องกันแรก
- Generative Replay / World Model = upgrade — hippocampus ฝัน แทน buffer ขนาดตาย
- Progressive protection = freeze block ที่ commit แล้ว เปิด block ที่มี capacity เหลือ

stability-plasticity dilemma คือ **ภาษีของสิ่งที่ทำให้ชิปคุณไม่ใช่ LLM แช่แข็ง** แนวเหล่านี้คือวิธีจ่ายภาษีนั้นโดยไม่ล้มละลายเพราะการลืม
