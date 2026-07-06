# 4 — สัญญาณการเรียนรู้ / "ความถูกต้องในฐานะความรู้สึก"

> ไอเดียที่ลึกที่สุดของคุณ: *ความถูกต้องคือความรู้สึกที่สร้างขึ้นเองและเรียนรู้ได้ ไม่ใช่ label จากภายนอก* วงการมีชื่อให้กับเรื่องนี้แทบเป๊ะ — **การทำให้ prediction-error / ความ surprise น้อยที่สุด** — และมีกรอบแม่บท (**Active Inference**) ที่ยังอธิบายส่วนที่ยากที่สุดของวิสัยทัศน์คุณ: **การตรวจสอบตัวเอง (self-verification)** นี่คือไฟล์ที่สัญชาตญาณของคุณมาเจอกับโครงการวิจัยจริง

---

## หลัก Free Energy & Active Inference — กรอบแม่บท

*Friston, 2006–ปัจจุบัน ภาพรวม: [Free Energy Principle (Wikipedia)](https://en.wikipedia.org/wiki/Free_energy_principle); [FEP for perception and action: a deep-learning perspective](https://pmc.ncbi.nlm.nih.gov/articles/PMC8871280/).*

### ปัญหาที่มันแก้

Friston ตั้งคำถามที่ใหญ่มาก: *"ทำไมสิ่งมีชีวิตถึงทำได้หลายอย่างมากขนาดนี้ด้วย mechanism เดียว?"* ไม่ว่าจะเป็นการรับรู้ การเรียนรู้ การวางแผน การเคลื่อนไหว ความอยากรู้ ความเชื่อ — ทั้งหมดนี้ดูเหมือนมีแกนร่วม Friston เสนอว่าแกนนั้นคือ **การทำให้ variational free energy น้อยที่สุด**

### กลไกจริงๆ

เริ่มจากนิยาม: เอเจนต์มี **แบบจำลองภายใน** ของโลก แบบจำลองนี้ assign ความน่าจะเป็นให้กับ observation x ผ่าน latent variables z:
```
p(x, z) = p(x|z) · p(z)    (generative model)
q(z|x)                      (recognition model / belief about causes)
```

**Free energy F** คือ upper bound ของ negative log evidence:
```
F = D_KL(q(z|x) || p(z)) - E_q[log p(x|z)]
     ↑ complexity              ↑ accuracy
```

หรือเขียนอีกแบบ:
```
F = -E_q[log p(x,z)] + E_q[log q(z|x)]
  = D_KL(q(z|x) || p(z|x)) + log p(x)
                                   ↑ เท่ากับ -log evidence เสมอ (negative ELBO)
```

เนื่องจาก D_KL ≥ 0 เสมอ → F ≥ log p(x) การทำให้ F น้อย = ทำให้ q(z|x) ใกล้ posterior จริง p(z|x) + ทำให้ evidence p(x) สูง (สิ่งที่เกิดขึ้น = สิ่งที่คาด)

**สองทางที่จะลด F**:
1. **การรับรู้ (Perception)**: เปลี่ยน q(z|x) → อัปเดต belief เกี่ยวกับสาเหตุให้ตรงกับ observation — นี่คือ "เรียนรู้ว่าโลกเป็นอย่างไร"
2. **การกระทำ (Action)**: เปลี่ยน x → ทำให้ observation ตรงกับ belief ที่มีอยู่ — นี่คือ "ทำให้โลกเป็นอย่างที่คาด" (เช่น ขยับแขนตามที่วางแผน)

**Epistemic vs Pragmatic value**: นอกจากสองอย่างนั้น ยังมี "epistemic action" — กระทำเพื่อ **ลดความไม่แน่ใจ** เลือกสถานการณ์ที่ F จะลดลงมากที่สุด (information gain สูงสุด) นี่คือ "ความอยากรู้"

### ผลที่น่าตื่นเต้น

FEP ทำนายหลายสิ่งที่ตรงกับข้อมูลประสาทวิทยา:
- ปรากฏการณ์ **rubber hand illusion** (สมองอัปเดต body model ให้ตรงกับ prediction)
- **Saccadic eye movements** (ตาเคลื่อนไหวเพื่อลด uncertainty ของ visual input)
- **Dopamine = precision-weighted prediction error** (ยิ่งความไม่แน่ใจสูง dopamine signal มีน้ำหนักต่อ weight update มากกว่า)
- **Autism hypothesis**: อาจเป็นการให้ precision weight ที่ miscalibrated → over/under-react ต่อ sensory input

### สำหรับเรา

**FEP คือทฤษฎีที่บ้านของ "ความถูกต้องคือความรู้สึก" ของคุณ** และมีสองอย่างที่ใหญ่มาก:

**หนึ่ง — ความรู้สึกนี้คำนวณได้และยึดกับความจริง (grounded)**: "ความถูกต้อง" = F ต่ำ = prediction error เล็กเมื่อเทียบกับ sensory input จริง ความรู้สึกโกหกได้ไม่นาน เพราะ F ถูกวัดเทียบกับโลกจริง ถ้าคุณเชื่อว่าถูกแต่ prediction error ยังสูง → ความรู้สึกจะไม่ยุบ → ยังต้องคิดต่อ

**สอง — มันอธิบายการตรวจสอบตัวเอง (self-verification)**: ตอนที่คุณไม่แน่ใจว่า "2x คือความชันของ x²" คุณ **สร้างจุดทดสอบ** (x=2,3,4,5) นั่นคือ epistemic action — เลือก observation ที่จะลด uncertainty ของคุณมากที่สุด ซึ่งใน active inference เรียกว่า "active sampling" หรือ "curiosity-driven exploration" จิตที่รัน self-verification เป็นจิตที่ทำ epistemic actions บน world model ของตัวเอง

ในเชิง implementation: F ≈ prediction error ที่ SCFF วัดอยู่แล้ว ("goodness" ใน forward-forward = negative F) ความรู้สึกถูกคือ F ที่ต่ำ (goodness สูง) หลังจาก settle ทั้ง world model loop จบ ไม่ต้องเพิ่มอะไรใหม่ แค่ **อ่าน F ที่มีอยู่แล้วในวงจรออกมาเป็น signal**

---

## ความอยากรู้ & Compression Progress — prediction error *ในฐานะรางวัล*

*Pathak, Agrawal, Efros & Darrell, 2017 ([ICM, PMLR](https://proceedings.mlr.press/v70/pathak17a/pathak17a.pdf)); Schmidhuber, 1991–2010 (compression progress / "ทฤษฎีทางการของความสร้างสรรค์").*

### ปัญหาที่มันแก้

สภาพแวดล้อมส่วนใหญ่ในโลกจริงไม่มี reward label — หุ่นยนต์ที่เดินในห้อง ไม่มีใครบอกว่า "ดีมาก" ทุกก้าว แต่สัตว์ยังสำรวจได้ เด็กยังเรียนรู้ได้ Pathak เลยถามว่า: *"ถ้าให้ prediction error ของตัวเองเป็น reward ล่ะ?"*

### กลไกจริงๆ

**Intrinsic Curiosity Module (ICM)** มีสามส่วน:

**ส่วน 1 — Inverse Model**: รับ state s_t และ s_{t+1} (สองภาพต่อเนื่อง) ทำนาย action a_t ที่ทำให้เกิด transition นั้น กระบวนการนี้บังคับให้ feature extractor φ เรียนรู้ **เฉพาะ features ที่ถูกควบคุมโดย action** ไม่ใช่ features ที่แค่เปลี่ยนตามสิ่งแวดล้อม (เช่น แสงกระพริบ, noise) เพราะ action ควบคุมสิ่งหลัง

**ส่วน 2 — Forward Model**: รับ φ(s_t) และ a_t → ทำนาย φ(s_{t+1}) โดยทำงานใน **feature space** ที่ผ่าน inverse model แล้ว ไม่ใช่ pixel ดิบ

**ส่วน 3 — Curiosity signal**: 
```
r_t_intrinsic = η/2 · ||φ̂(s_{t+1}) - φ(s_{t+1})||²
```
ยิ่ง forward model ทำนายผิด → curiosity สูง → reward สูง → เอเจนต์ออกตามหาสถานการณ์นั้น

เมื่อ forward model ดีขึ้น (เรียนรู้แล้ว) → curiosity ในสถานการณ์นั้นลดลง → เอเจนต์ย้ายไปหาสิ่งที่ยังไม่รู้ใหม่

**Schmidhuber's Compression Progress**: Schmidhuber เสนอ version ที่กว้างกว่า — น่าสนใจ = บีบอัดได้แต่ยังไม่ได้บีบ ความน่าสนใจ = **compression progress** (เรียนรู้ไปเยอะแค่ไหนในช่วงเวลานี้) ไม่ใช่ compression ปัจจุบัน ไอเดียนี้ทำนายว่า: ตอนเริ่มเรียน A ใหม่ → น่าสนใจมาก ตอนรู้จัก A ดีแล้ว → ไม่น่าสนใจ ไปหา B ที่ยังไม่รู้แทน ซึ่งตรงกับ human experience อย่างยิ่ง

### ผลที่น่าตื่นเต้น

ICM บน VizDoom (เกม first-person shooter): **โดยไม่มี extrinsic reward เลย** เอเจนต์สำรวจ 60-70% ของห้องทั้งหมด (เทียบกับ baseline random 30%)

ICM + extrinsic reward: ดีกว่า extrinsic reward อย่างเดียวเป็นอย่างมาก โดยเฉพาะในสภาพแวดล้อมที่ reward sparse

ICM ใน Super Mario Bros: เรียนรู้ไปถึง World 3 โดยไม่ได้บอกว่า "เดินไปทางขวาคือดี"

### สำหรับเรา

ICM ให้ **เครื่องยนต์ "อยากเรียนรู้ต่อไป"** — แรงขับที่ทำให้โมเดล active ไม่ใช่ passive ความรู้สึกถูกกับความรู้สึกอยากรู้ คือ **ฝาแฝด** ที่ควรอยู่คู่กัน:
- ความรู้สึกถูก = prediction error ต่ำ = "พอแล้ว หยุดคิด"
- ความรู้สึกอยากรู้ = prediction error สูงใน region ที่ยังไม่รู้ = "ไปหาข้อมูลเพิ่ม"

สังเกตรายละเอียดสำคัญ: **"พื้นที่ feature ที่เรียนรู้แล้ว"** ไม่ใช่ raw input ICM ทำงานใน φ-space ที่ inverse model clean ไว้ ซึ่งตรงกับ SCFF features ของคุณ เพราะถ้าวัด error ใน pixel space ตาข่ายจะไล่ตาม noise ที่ควบคุมไม่ได้แทน (TV noise ในห้องว่างก็ทำให้ curiosity สูงตลอด)

ในเชิง implementation ที่เป็นรูปธรรม: curiosity signal คือ output ของ **forward model error** ซึ่งก็คือ SCFF block ที่คาดว่า next state ควรเป็นอะไร เทียบกับ next state จริง ถ้า SCFF มี predictive head อยู่แล้ว (เฟส 2) curiosity ก็มาฟรี

---

## World Models — ให้จิตมีเครื่องจำลองไว้ตรวจสอบข้างใน

*Ha & Schmidhuber, 2018 ([arXiv 1803.10122](https://arxiv.org/pdf/1803.10122)); สาย Dreamer: Hafner et al., 2020–2023.*

### ปัญหาที่มันแก้

RL agent ที่เรียนรู้จาก real environment ต้องใช้ sample จำนวนมาก (DQN ใช้ 200 ล้าน frames บน Atari) เพราะทุก decision ต้องทดลองจริง สมองมนุษย์ไม่ทำอย่างนั้น — เรา "จินตนาการ" ผลลัพธ์ก่อนลงมือทำ Ha กับ Schmidhuber ถามว่า: *"ถ้าให้ network เรียน world model แล้วฝึกได้ใน imagination ล่ะ?"*

### กลไกจริงๆ

**World Models (Ha & Schmidhuber)** มีสามส่วน:

**V — Vision model (VAE)**: reparameterization trick → z_t ~ q(z_t|x_t) latent vector 32 dimensions เข้ารหัสภาพจาก pixel ลงเป็น compact representation ที่เรียนรู้ผ่าน reconstruction loss + KL term

**M — Memory model (MDN-LSTM)**: รับ z_t (visual latent) + a_t (action) + h_t (RNN hidden state) → ทำนาย z_{t+1} เป็น **mixture of Gaussians** (MDN) ไม่ใช่ single prediction เพราะโลกมี stochasticity: output คือ {π_k, μ_k, σ_k} สำหรับ K components → สามารถ sample "ความเป็นไปได้" ของ next state

**C — Controller**: linear layer เล็กมาก (size 4 × (32 + 256)) mapping [z_t, h_t] → action a_t เทรนด้วย CMA-ES (evolutionary strategy ที่ไม่ต้องการ gradient)

**การ "ฝัน" (Dream training)**: แทนที่จะรัน environment จริง:
1. Sample z_0 จาก V
2. รัน M เป็น "environment": a_t → M → z_{t+1} → a_{t+1} → ...
3. เทรน C ใน dream นี้
4. Deploy C ใน environment จริง

ผล: CarRacing — เทรน V+M 100 episodes, หา C ใน dream ไม่กี่พัน virtual steps → ทำ score 906/1000 เทียบ SOTA digital RL ที่ต้องการ episodes มากกว่า 10x

**Dreamer (Hafner et al.)** ขยายแนวนี้ด้วย **Recurrent State Space Model (RSSM)**:
```
Deterministic state:  h_t = f(h_{t-1}, z_{t-1}, a_{t-1})    (GRU)
Stochastic state:     z_t ~ p(z_t | h_t)                     (discrete/continuous latent)
Reconstruction:       x̂_t ~ p(x_t | h_t, z_t)
Reward prediction:    r̂_t ~ p(r_t | h_t, z_t)
```

ทั้ง actor และ critic ถูกเทรน **ใน imagination** โดย unroll RSSM ไป T=15 steps → compute return → backprop ผ่าน latent dynamics DreamerV2 เอาชนะมนุษย์บน 27/55 Atari games DreamerV3 generalize ข้ามโดเมนโดยไม่ต้องจูน hyperparameter

### ผลที่น่าตื่นเต้น

DreamerV3 เทรน **Minecraft** ให้หา diamond ได้เป็นครั้งแรก (ต้องวางแผน task chain ยาวกว่า 20k steps) นี่คือ milestone ที่RL แบบ model-free ทำไม่ได้เลย

DreamerV3 ยังทำ **quadruped locomotion** โดยเทรน entirely in imagination บน random noise policy แล้ว transfer ไปหุ่นยนต์จริงโดยไม่มี domain adaptation

### สำหรับเรา

"การคิด" ในตัวอย่างอนุพันธ์ของคุณ **คือการรัน world model ข้างใน** — คำนวณ x² ที่หลายๆ จุด ดูแนวโน้ม นั่นคือ forward model ที่รันหลายก้าว เปรียบเทียบ output ลองหา derivative แปลกลับมา:

- **V = SCFF front** (เข้ารหัส raw pattern ลง latent z)
- **M = วงลูป prefrontal↔hippocampus** (ทำนาย z_{t+1} จาก z_t + context)
- **C = actor head เล็กๆ** (map state → decision/action)
- **"ฝัน" = sleep หรือ internal rollout ระหว่าง "คิด"**

RSSM น่าสนใจมากสำหรับ substrate: deterministic state h_t เป็น GRU (มี gate ที่เรียนรู้ได้ → PBWM ทางชีววิทยา) + stochastic state z_t เป็น discrete latent (VQ-VAE style → ใช้ analog cluster centroids) ทั้งสองรัน in analog ได้

M ตัวเดียวกันทำงานสองโหมด: ตอนตื่น = ทำนายไปข้างหน้าเพื่อ planning; ตอนหลับ = generate replay ป้อนกลับ cortex → อวัยวะเดียว ใช้สองแบบ

---

## ตัว Critic ที่เรียนรู้ได้ — ความรู้สึกคือโมเดลที่เทรนได้ ไม่ใช่กฎตายตัว

*Actor-Critic: Sutton & Barto; Barto, Sutton & Anderson, 1983 เป็นต้นมา; Modern: A3C (Mnih et al., 2016), PPO (Schulman et al., 2017).*

### ปัญหาที่มันแก้

RL แบบ pure policy gradient มีปัญหา variance สูง — ถ้า reward มาช้า (หลายร้อย steps) gradient estimate กลายเป็น noise ทั้งนั้น Actor-critic แก้โดยเพิ่ม value function (critic) ที่ estimate expected return → ใช้แทน raw reward เพื่อลด variance

### กลไกจริงๆ

**Critic V(s)**: ตาข่ายที่เทรนให้ predict expected cumulative reward:
```
V(s_t) ≈ E[r_t + γr_{t+1} + γ²r_{t+2} + ...]
```
เทรนด้วย Temporal Difference (TD) error:
```
δ_t = r_t + γV(s_{t+1}) - V(s_t)    (TD error)
L_critic = δ_t²
```

**Actor π(a|s)**: ตาข่ายที่เทรนให้เลือก action ที่ maximize expected return โดย gradient:
```
∇L_actor = -E[log π(a_t|s_t) · A(s_t, a_t)]
```
โดย A(s_t, a_t) = TD error δ_t = advantage estimate ("action นี้ดีกว่าค่าเฉลี่ยมากแค่ไหน")

**Bootstrapping**: critic ใช้ V(s_{t+1}) ซึ่งเป็น estimate ของตัวเอง แทน Monte Carlo rollout ทั้งหมด ทำให้ update ได้ทุกก้าวไม่ต้องรอจบ episode

**Key insight**: critic เรียนรู้ว่า "สถานะนี้ดีแค่ไหน" จากประสบการณ์จริง ไม่ใช่จาก hardcoded rule ดังนั้นมันผิดได้ (คุณรู้สึกว่าถูกแต่จริงๆ ผิด) และมันดีขึ้นด้วย feedback (คุณเรียนรู้ว่าตัวเองถูกเมื่อไหร่จากผลลัพธ์จริง)

### ผลที่น่าตื่นเต้น

**A3C** (Asynchronous Advantage Actor-Critic): เทรนบน Atari 57 games พร้อมกัน ใช้ CPU หลายตัวแทน GPU โดย asynchronous update ดีกว่า DQN ใน 43/57 games

**PPO** (Proximal Policy Optimization): stable version ที่ clip gradient เพื่อไม่ให้ policy เปลี่ยนเร็วเกิน ใช้กันแพร่หลายมากที่สุดในปัจจุบัน training ง่าย, stable, ดีทั่วไป

Critic ที่ดีจะลด variance ของ gradient estimate 10-100x เมื่อเทียบ Monte Carlo ทำให้เรียนเร็วขึ้นมาก

### สำหรับเรา

Critic นี้ตอกย้ำประเด็นเชิงโครงสร้างที่คุณพูดเอง: **ความรู้สึกว่าถูกควรเป็นโมเดลเล็กๆ ที่เรียนรู้ได้ ไม่ใช่เกณฑ์ตายตัว**

สิ่งนี้หมายความว่า:
1. Critic มี **network เล็กๆ แยกต่างหาก** (2-3 layers, MLP) ที่เทรนคู่กับ main system
2. เทรนด้วย **TD error** จาก grounding events จริง (เช่น ครั้งที่ task จบสำเร็จ หรือ prediction error ต่อ ground truth)
3. มันผิดได้ (miscalibrated critic ตอนต้น) และดีขึ้นเมื่อเห็น feedback มากขึ้น
4. มันนั่งอยู่ข้าง main compute ไม่ใช่ข้างใน

บน substrate: critic เป็น **analog MLP เล็กๆ** ที่รับ current state summary (SCFF latent) → output scalar value ≈ "ดีแค่ไหน" ถูกมากและตรงกับ FEP: V(s) ≈ negative F ณ state นั้น critic เรียน F landscape แทนที่จะคำนวณตรงๆ

---

## รูปร่างของคำตอบ (ไฟล์นี้)

ความรู้สึกว่าถูก สำหรับเราคือ:

- **การยุบของ prediction error / free energy** เมื่อวงลูป settle (Active Inference) — grounded เพราะวัดเทียบกับ sensory input จริง โกหกได้ไม่นาน
- **ฝาแฝดของมันคือ curiosity signal** (prediction error สูง = "น่าสนใจ ไปเรียน") ที่ขับแรงหิว "ไม่หยุดนิ่ง" (ICM/Schmidhuber) คำนวณใน SCFF feature space ไม่ใช่ raw input
- **Implement เป็น critic เล็กๆ ที่เรียนรู้ได้** (actor-critic) เทรนด้วย grounding events — ไม่ใช่กฎตายตัว จึงถูกสอนได้ ผิดพลาดได้ และดีขึ้นได้
- **การตรวจสอบตัวเอง** = epistemic actions เหนือ world model — จิตรันการทดลอง ข้างในก่อนสัมผัสโลกจริง (World Models / Dreamer)
- **Active Inference** คือ unified framework ที่รวมทั้งหมดนี้ ทั้งการรับรู้ การเรียนรู้ การกระทำ และการสำรวจ ผ่านการทำให้ F น้อยที่สุด

---

## เมล็ดที่เพาะไว้แล้ว — direction-halt ที่เราสร้างไปแล้ว (เฟส 8; ไปลองเป็น experiment แยกในอนาคต)

*ไม่ใช่ paper — เป็นชิ้นส่วนของ neocortex ที่แช่แข็งแล้ว จอดไว้ตรงนี้ตั้งใจ เพราะมันเป็นของ gate แบบ recurrent ไม่ใช่ gate แบบ feed-forward*

เฟส 8.2 สร้างและ validate สัญญาณ gate แบบ **class-direction tap-drift** (label-free, `sig_tap_drift_direction`): มันดู *ทิศทาง* ที่ tap ของ SCFF หมุน แล้วยิงเมื่อแกน class ขยับจริง มัน **นำ labeled error ~8 steps** (MTD 6 vs 14), **invariant ต่อ nuisance covariate** (0.84× baseline) ขณะที่ magnitude-null false-fire บน 94% ของ nuisance steps และลงตรงกับ DriftLens (reference label-free ของวงการ) มัน **spine-clean โดยโครงสร้าง**: เป็น *ทิศทาง* ไม่ใช่ confidence magnitude

**Validate แล้วแต่ไม่ deploy** — gate ของ frozen loop คือ **DDM บน error-EMA ของ namer** (labeled error-rate) เพราะ DDM เป็น error-rate detector โดยโครงสร้าง ดังนั้น "DDM gate" (P8.1) กับ "tap-drift trigger" (P8.2) เป็นสองมติที่ compose ใน code path เดียวไม่ได้ และ P9.5 พบว่า *fire-timing* ของ gate เป็นเรื่องรอง — **sleep cadence** ที่ถี่ ไม่ใช่ trigger ที่กำหนด worst-point safety การ wire เข้า frozen loop เลยได้ค่าน้อย จึงเก็บเป็นเมล็ด

**ทำไมอยู่ไฟล์นี้** — gate แบบ recurrent คือ **halt** ("คิดจนความรู้สึกข้าม θ") halt นั้นควรยิงบน *ทิศทาง* (แกน class/readout) ไม่ใช่ confidence magnitude (spine; เหตุผลที่ P5 ตัด adaptive-exit selector) สัญญาณ tap-drift *คือ* halt นั้น สร้างและวัดแล้ว แค่ต้องการบ้านที่ **เป็น** halt — ซึ่ง recurrent loop เป็น แต่ frozen gate ไม่เป็น มันเข้าคู่กับ direction-seed อีกสองตัวที่จอดไว้: **cosine spine-pure head** (P7, argmax-flip 0.000) และ **better-than-confidence per-sample selector** (P5)

**จะลองยังไง — เป็น experiment แยก ไม่ใช่ retrofit** — เฟส 1–11 แช่แข็งแล้ว **อย่า** ไป re-wire frozen loop เมื่อสร้าง recurrent gate ให้ตั้ง experiment **ใหม่**: ป้อน `sig_tap_drift_direction` (หรือรูป single-sample แบบ CLAPP) เข้า recurrent halt เป็น "settle detector" แข่งกับ error/confidence halt บน task แบบ recurrent แล้วให้ *experiment นั้น* ตัดสิน โค้ดมีอยู่แล้ว (`p8lib.sig_tap_drift_direction`, validate ใน `phase8/exp2`) เมล็ดเพาะแล้ว การทดสอบเลื่อนไป

*ที่มา: [`../../src/phase9-final-architecture.md`](../../src/phase9-final-architecture.md) §4/§10 · [`../../src/phase8/exp2/experiment-2.md`](../../src/phase8/exp2/experiment-2.md)*
