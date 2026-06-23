# 16 — retina / vision front-end ที่เรียนรู้ด้วยการทำนาย (อนาคตไกล)

> แผนอนาคตไกลของคุณ: สร้าง **retina + CNN decoder** เป็นอินพุต แล้วให้โมเดล **เรียนรู้ด้วยการทำนายภาพ** — เพราะการมองเห็น *นามธรรมน้อยกว่าภาษา* และ front-end ทางประสาทสัมผัสแบบสิ่งมีชีวิตทำให้คุณลอกกลไก developmental ของจริง (พ่อแม่สอน, พฤติกรรมทารก) ได้ ไฟล์นี้ขยายจากหัวข้อนั้นด้วยกลไกจริงๆ ของแต่ละ paper — เพราะสัญชาตญาณถูกต้องแต่ "ทำนายภาพ" มีวิธีทำที่ต่างกันมาก บางวิธีทำให้โมเดลหลอกตัวเอง บางวิธีไม่

---

## ทำไมการทำนายถึงเป็นสัญญาณ self-supervised ที่ดีที่สุดสำหรับ vision

*Predictive coding ในฐานะทฤษฎีประสาทวิทยา: Rao & Ballard 1999, Nature Neuroscience; ในฐานะ self-supervised signal: Oord et al. (CPC) 2018; LeCun, "A Path Towards Autonomous Machine Intelligence" 2022.*

### ปัญหาที่มันแก้

Self-supervised learning บน vision ในช่วงแรก (2019–2020) อาศัย augmentation เป็นหลัก: เอาภาพเดิม crop/flip/color-jitter สองแบบ → บอกว่า embedding ต้องคล้ายกัน ปัญหา: augmentation ที่เลือกมาอย่างประณีตมีความ arbitrary สูง และการ tune augmentation เปลี่ยน task โดยตรง นักวิจัยถามว่า: *มีสัญญาณ self-supervised ที่ไม่ขึ้นกับ augmentation เลย หรืออย่างน้อย less arbitrary กว่านี้ ไหม?*

คำตอบจากประสาทวิทยา: สัญญาณที่คอร์เทกซ์สัตว์เลี้ยงลูกด้วยนมใช้จริงๆ คือ **การทำนาย** — คอร์เทกซ์ทุกชั้นทำนาย input ที่คาดว่าจะได้รับจากชั้นล่าง แล้วส่งแค่ error ขึ้นไปข้างบน (ทฤษฎีของ Rao & Ballard 1999) prediction error คือ signal การเรียนรู้ ไม่ใช่ label จากภายนอก

### กลไกจริงๆ

**ทำไมการทำนายเวิร์กในฐานะ self-supervised signal:**

1. **มันบังคับให้เรียนโครงสร้าง:** ถ้าคุณทำนายอะไรไม่ได้ (prediction error สูงตลอด) แสดงว่าคุณยังไม่เข้าใจ structure ของ input การลด prediction error บังคับให้ model ค้นหา regularity ในข้อมูลโดยตรง ไม่ใช่แค่จำ

2. **มันไม่ต้อง label:** ทุก frame ที่เห็นคือ ground truth ของ prediction จาก frame ก่อน — โลกตัวเองคือ teacher

3. **Prediction error = curiosity signal:** สิ่งที่ทำนายได้แล้ว (low error) น่าเบื่อ สิ่งที่ทำนายไม่ได้เลย (high error) ก็ไม่มีประโยชน์ สิ่งที่น่าสนใจที่สุดคือสิ่งที่ *เกือบ* ทำนายได้ — prediction error ระดับกลาง นั่นคือ intrinsic motivation (`4-signal.md`) ที่ define ตัวเองจาก vision

### ผลที่น่าตื่นเต้น

Contrastive Predictive Coding (CPC, Oord et al. 2018): เรียนรู้บน audio และ image โดยทำนาย representation อนาคต → feature ที่ได้ transfer ได้ดีบน downstream task ทั้งที่ไม่ train supervision เลย

LeCun ใน "A Path" (2022): การทำนายใน representation space คือ core mechanism ของ "world model" ที่ agent ต้องมี ก่อนที่จะ plan หรือ imagine ได้

---

## Dense Predictive Coding — ทำนาย representation ไม่ใช่ pixel

*Han et al., 2019, "Video Representation Learning by Dense Predictive Coding" ([arXiv 1909.04656](https://arxiv.org/abs/1909.04656)).*

### ปัญหาที่มันแก้

การทำนาย pixel ดิบตรงๆ ฟังดูตรงประเด็น แต่มีปัญหาร้ายแรง: **อนาคตที่ระบุไม่ได้แน่ชัด (under-determined future)** จากเฟรมปัจจุบัน เฟรมถัดไป *หลายแบบ* เป็นไปได้ (ใบไม้อาจปลิวซ้ายหรือขวา แสงอาจเปลี่ยนทิศ) ถ้าเทรน model ให้ minimize MSE ระหว่าง predicted pixel กับ actual pixel model จะต้อง:
- เฉลี่ยทุก possible future → prediction เบลอ (ความเบลอ = ค่าเฉลี่ยของหลายอนาคต)
- หรือเลือก hallucinate รายละเอียดที่ไม่มีจริง → "หลอกตัวเอง" จาก `7-encoding.md`

ทั้งสองกรณีทำให้ feature representation ที่เรียนได้ไม่มีคุณภาพ เพราะ model ถูกบังคับให้โฟกัสกับ pixel-level noise ที่ predict ไม่ได้โดยหลักการ

### กลไกจริงๆ

**Dense Predictive Coding (DPC)** แก้ด้วยการเปลี่ยน target จาก pixel → representation:

**สถาปัตยกรรม:**

```
Video frames:  [f_t-3, f_t-2, f_t-1, f_t] → [f_t+1, f_t+2, f_t+3]  (predict 3 future frames)
                        ↓
            Encoder (CNN+GRU)
                        ↓
            Context representation c_t  (embedding ของ context ทั้งหมดถึง f_t)
                        ↓
            Predictor network
                        ↓
            Predicted embeddings: [ẑ_t+1, ẑ_t+2, ẑ_t+3]
```

Target ไม่ใช่ pixel แต่เป็น **embedding ที่ encoder สร้างจาก future frame จริง** z_t+k = encoder(f_t+k) ผ่าน target encoder (EMA ของ encoder เพื่อ stability)

**Loss แบบ contrastive ไม่ใช่ MSE:**
```
L = -log [ exp(ẑ_t+k · z_t+k / τ) / Σ_{z'} exp(ẑ_t+k · z' / τ) ]
```
"ดึง" predicted embedding ให้ใกล้กับ actual future embedding, "ผลัก" ให้ห่างจาก random negative samples z' (frames จาก video อื่น) temperature τ ควบคุม sharpness

**ทำไม contrastive loss แก้ปัญหา under-determined future?** เพราะ loss ไม่ได้วัดว่า prediction ถูก pixel เป๊ะ แต่วัดว่า prediction อยู่ "ในโซนที่ถูกต้อง" ของ embedding space — ใบไม้จะปลิวซ้ายหรือขวาก็ได้ แต่ทั้งสองอยู่ใน "โซนของใบไม้ที่กำลังเคลื่อนไหว" model เรียนรู้ที่จะทำนาย semantic ไม่ใช่ pixel

**Curriculum — ทำนาย far future ด้วย less context:**
- Stage 1: ทำนาย 1 frame ข้างหน้าด้วย context 4 frames → ง่าย
- Stage 2: ทำนาย 3 frames ข้างหน้าด้วย context 4 frames → ยากขึ้น
- Stage 3: ทำนาย 3 frames ข้างหน้าด้วย context 2 frames → ยากขึ้นอีก

Curriculum นี้ทำให้ model เรียน representation ที่มี "abstraction" สูงขึ้นทีละน้อย เพราะการทำนายไกลขึ้นต้องการ semantic understanding มากกว่าแค่ pixel interpolation

**"Dense":** ทำ prediction ที่ **ทุก spatial position** ไม่ใช่แค่ global embedding เดียว model ทำนาย future feature map ทั้งก้อน (C×H'×W') ซึ่งบังคับให้ representation เรียน spatial structure ไม่ใช่แค่ global statistics

### ผลที่น่าตื่นเต้น

DPC เทรนบน Kinetics-400 (video dataset) โดยไม่มี label เลย แล้ว linear probe บน UCF-101 (action recognition): **75.7%** เทียบกับ supervised upper bound ~82% — เรียนได้เองจาก prediction ได้ 92% ของ supervised performance

สำคัญกว่า: feature ที่ DPC เรียนได้นั้น **transfer** ข้าม dataset ได้ดี ไม่ overfitting เฉพาะ Kinetics ซึ่งหมายความว่ามันเรียน structure ทั่วไปของ visual world ไม่ใช่แค่ pattern ของ dataset เดียว

DPC ยังทำได้ดีกว่า Methods ที่ทำนาย pixel ตรงๆ (PredNet, video auto-encoder) อย่างมีนัยสำคัญ — proof ว่า "ทำนาย representation ไม่ใช่ pixel" คือ design choice ที่สำคัญจริง

### สำหรับเรา

Retina → encode (conv front-end SCFF/CNN) → **ทำนาย *encoding* ของ future frames ด้วย contrastive loss** → prediction error คือสัญญาณเรียนรู้ที่ grounded

สิ่งสำคัญที่สุดที่ต้องพกต่อไป: **ไม่ทำนาย pixel** เด็ดขาด ทำนาย representation ที่ encoder สร้าง loss เป็น contrastive ไม่ใช่ MSE นั่นคือความแตกต่างระหว่าง model ที่เรียนโครงสร้างกับ model ที่เรียน noise

---

## PredNet — ลำดับชั้น prediction แบบ top-down/bottom-up

*Lotter, Kreiman & Cox, 2016, "Deep Predictive Coding Networks for Video Prediction and Unsupervised Learning" ([arXiv 1605.08104](https://arxiv.org/abs/1605.08104)).*

### ปัญหาที่มันแก้

DPC ทำนาย future representation จาก context แต่ไม่ได้สร้าง explicit hierarchy ระหว่างชั้น ทฤษฎี predictive coding ของ Rao & Ballard บอกว่าสมองทำงานแบบ hierarchical: ทุกชั้นทำนาย input ของตัวเองจาก top-down และส่งแค่ error ขึ้น bottom-up Lotter ถามว่า: *จะ implement hierarchy นี้ใน deep network สำหรับ video ยังไง?*

### กลไกจริงๆ

PredNet มีโครงสร้างแบบ **กองซ้อนของ LSTM** ที่แต่ละชั้น l ทำสี่สิ่งในแต่ละ timestep:

```
ชั้น l ประกอบด้วย 4 module:
1. A_l (Representation):   encode input ที่ชั้นนี้เห็น
2. Â_l (Prediction):       ทำนาย representation จาก hidden state t-1 + top-down signal จากชั้น l+1
3. E_l (Error):             E_l = A_l - Â_l  (prediction error ที่ชั้น l)
4. R_l (LSTM):              อัปเดต hidden state จาก E_l + top-down R_{l+1}
```

**การไหลของ information:**
- **Bottom-up:** A_l → E_l (error) → input ของชั้น l+1
- **Top-down:** R_{l+1} → Â_l (prediction) → E_l (ยิ่งทำนายได้แม่น error ยิ่งเล็ก)

Layer 0 เห็น pixel จริง ทำ prediction ใน pixel space เลย Layer สูงขึ้นเห็น representation ที่ abstract ขึ้น

Loss: ส่วนใหญ่คือ pixel prediction error ที่ layer 0 (เพื่อให้เทรนได้ end-to-end) แต่ error ที่ layer สูงก็ร่วมด้วยในสัดส่วนน้อยกว่า

**ข้อดีของ hierarchical prediction:** ชั้น 0 ทำนาย texture และ edge level; ชั้น 1 ทำนาย object motion; ชั้น 2 ทำนาย scene-level change ถ้าชั้นสูงทำนายได้ถูก ชั้นล่างไม่ต้อง propagate error ขึ้นไป = efficient coding เหมือน compression ในเวลา

### ผลที่น่าตื่นเต้น

- PredNet สามารถทำนาย video ได้ **10 frames ข้างหน้า** หลัง training บน KITTI driving dataset
- Feature ของ PredNet transfer ได้บน object detection และ optical flow (neuroscience benchmark) ดีกว่า pretrained VGG
- PredNet model ที่เทรนบน natural video ตอบสนองต่อ visual cortex บันทึกจาก fMRI ได้ดีกว่า CNN ที่เทรนด้วย ImageNet classification — ยืนยันว่า predictive hierarchy เป็น model ที่ดีกว่าสำหรับ visual cortex
- Error signal จาก PredNet มีความสอดคล้องกับ mismatch negativity ERP signal ในมนุษย์ — brain ตอบสนองต่อ prediction error เหมือนที่ PredNet ทำนาย

### สำหรับเรา

PredNet คือ blueprint ของ **hierarchical predictive coding ในชิป** ที่ชัดที่สุด: ทุกชั้นของ SCFF stack ทำนายชั้นก่อนหน้า ส่งแค่ error ขึ้น ซึ่งเป็นวิธีการ compute ที่มีประสิทธิภาพมากบนชิปเพราะ:
- ถ้า prediction แม่น error เล็ก → ต้นทุนการ compute เล็กตามไปด้วย (sparse error signals)
- top-down prediction ที่ดีลด load บน bottom-up path โดยตรง

ในเชิง circuit: top-down signal คือ expected value ของ Scap ถัดไป bottom-up signal คือ actual value error = actual - expected เก็บไว้เป็น difference signal ซึ่งบน analog circuit คือ differential pair ที่ถูกมาก

---

## I-JEPA — ทำนาย representation ของส่วนที่หายไปในภาพนิ่ง

*LeCun Lab: Assran et al., 2023, "Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture" ([arXiv 2301.08243](https://arxiv.org/abs/2301.08243)).*

### ปัญหาที่มันแก้

Masked Autoencoder (MAE, He et al. 2022) ทำอะไรได้ดีในแง่ downstream task: mask 75% ของ image patches แล้วเรียนรู้ reconstruct pixel ดิบ แต่มีปัญหาเชิงการออกแบบ: **MAE ต้องทำนาย pixel** ซึ่งบังคับให้เรียน low-level texture detail ที่ไม่ semantic (สีของ pixel ที่ถูก mask อาจเปลี่ยนได้จากแสง) LeCun ตั้งข้อสังเกตว่า: *โมเดลที่เรียน "รู้" อะไรบางอย่างเกี่ยวกับโลกควรทำนาย high-level representation ไม่ใช่ low-level pixel*

I-JEPA คือการ apply หลักการ "ทำนาย representation ไม่ใช่ pixel" (เหมือน DPC) กับภาพนิ่ง

### กลไกจริงๆ

**สามตัวละคร:**

1. **Context Encoder:** รับ image ที่ mask บางส่วนออก (เก็บ patches บางส่วน ลบบางส่วน) → สร้าง context embedding สำหรับ patches ที่มี
2. **Predictor network (เล็ก):** รับ context embedding + ตำแหน่งของ masked patches → ทำนาย embedding ของ masked patches
3. **Target Encoder (EMA ของ Context Encoder):** รับ image เต็มๆ → สร้าง target embedding ของ masked patches ที่ควรจะ predict

```
Image → [Context patches]  →  Context Encoder  →  context embedding
                                                          ↓
                          Target positions  →  Predictor  →  Predicted embeddings
                                                                      ↓ Loss (L2)
Image → [All patches]    →  Target Encoder  →  Target embeddings (stop gradient)
```

**ทำไม EMA (Exponential Moving Average) สำหรับ Target Encoder?** ถ้า Context Encoder และ Target Encoder เป็นโมเดลเดียวกัน model จะ collapse (เรียนทำนาย representation ที่ constant ทุก patch) EMA ทำให้ target เปลี่ยนช้าๆ เป็น "stable teacher" ที่ context encoder พยายาม match — เหมือน distillation แบบ self

**Loss: L2 ระหว่าง predicted embedding กับ target embedding**
```
L = ||Predictor(ContextEncoder(x_context), pos_mask) - TargetEncoder(x_full)||²
```
ไม่ใช่ contrastive (ไม่ต้องมี negative samples) ง่ายกว่า DPC แต่ต้องมีกลไก anti-collapse (EMA)

**Masking strategy:** I-JEPA mask แบบ "block" (สี่เหลี่ยมผืนผ้าขนาดใหญ่) ไม่ใช่ random patch ทีละอัน เหมือน MAE เพราะ block mask ทำให้ต้อง predict region ต่อเนื่อง ซึ่งต้องการ semantic understanding มากกว่าการ interpolate pixel จากเพื่อนบ้าน

### ผลที่น่าตื่นเต้น

- **I-JEPA ทำได้ดีกว่า MAE บน semantic tasks:** linear probe บน ImageNet ด้วย ViT-H: I-JEPA 77.5% vs MAE 68.0% — ต่างกัน 9.5% ทั้งๆ ที่เทรนด้วย compute เท่ากัน
- I-JEPA ทำได้ดีกว่าบน object detection และ depth estimation ด้วย — ยืนยันว่า representation ที่ I-JEPA เรียนได้ semantic มากกว่า MAE
- เทรนเร็วกว่า contrastive methods (ไม่ต้องมี negative sampling, batch ง่ายกว่า)
- Feature I-JEPA มี **low-frequency structure** มากกว่า MAE (ทำนาย semantic shape ไม่ใช่ texture) ซึ่งตรงกับ feature ที่เป็นประโยชน์สำหรับ downstream reasoning

**I-JEPA vs MAE — ความต่างที่ชัดเจน:**

| | MAE | I-JEPA |
|---|---|---|
| Target | Pixel ดิบ | Embedding ของ Target Encoder |
| Loss | MSE pixel | L2 embedding |
| เรียนอะไร | Low-level texture | High-level semantic |
| ImageNet linear | 68.0% | **77.5%** |
| ต้องการ neg. sample | ไม่ | ไม่ |

### สำหรับเรา

I-JEPA คือ **design reference ที่สะอาดที่สุด** สำหรับ vision front-end ของคุณในเชิง "อย่าทำนาย pixel" และ "ใช้ EMA teacher":

- **Retina → patches → context encoder (SCFF conv)** → context embedding
- **Predictor (GD readout เล็กๆ):** ทำนาย embedding ของส่วนที่ถูก mask
- **Target encoder (EMA ของ SCFF conv):** สร้าง target สำหรับ loss

บนชิปคุณ: EMA update ง่ายมาก — leaky Scap ที่มี RC ยาวทำ EMA โดยธรรมชาติ RC constant ของ target encoder ยาวกว่า context encoder → update ช้ากว่า → เป็น stable teacher โดยธรรมชาติ ไม่ต้องมีโค้ดพิเศษ

---

## มุม developmental — พ่อแม่สอน, ทารก, และ curriculum ที่สร้างขึ้นเอง

*Intrinsic motivation / curiosity: Schmidhuber 1991; CURIOUS: Colas et al. 2019; Curriculum Learning: Bengio et al. 2009; Developmental robotics: Oudeyer & Kaplan 2007.*

### ปัญหาที่มันแก้

ทารกไม่ได้เรียนจาก random data ไม่ได้เรียนจาก task ที่ไม่มี structure และไม่ได้รับ feedback จาก label ทุกอย่าง แต่ยัง develop ความสามารถที่น่าทึ่งใน 2–3 ปีแรก กลไกนั้นคืออะไร? คำตอบที่งานวิจัย developmental robotics มาถึง: ทารกมี **แรงจูงใจภายใน (intrinsic motivation)** ที่ผลักดันให้สำรวจสิ่งที่ "เรียนได้แต่ยังไม่ได้เรียน" และมีพ่อแม่ที่ **จัดรูป curriculum** โดยควบคุมว่าทารกเจออะไรเมื่อไหร่ สองอย่างนี้ร่วมกันสร้าง learning pathway ที่มีประสิทธิภาพโดยไม่ต้องมีใครออกแบบ

### กลไกจริงๆ

**Intrinsic motivation / curiosity — learning progress เป็น reward:**

Schmidhuber (1991) เสนอ idea แรก: reward ของ agent ควรเป็น **ความเร็วของการลดลงของ prediction error** (compression progress) ไม่ใช่ค่าของ prediction error เอง

ทำไม? เพราะ:
- สิ่งที่ error ต่ำแล้ว (เรียนแล้ว) → ลด error ไม่ได้ → reward = 0 → "น่าเบื่อ"
- สิ่งที่ error สูงมาก (ยากเกินไป random noise) → ลด error ไม่ได้ → reward = 0 → "ไม่มีประโยชน์"
- สิ่งที่ error ลดได้เรื่อยๆ (ท้าทายพอดี) → reward สูง → "น่าสนใจ"

```
Intrinsic_reward(t) = PredictionError(t-1) - PredictionError(t)
                    = ∂Error/∂t  (ความเร็วของการเรียนรู้)
```

งาน CURIOUS (Colas et al. 2019): robot แขนที่มี intrinsic reward แบบนี้สามารถ discover ว่า task ไหน "ท้าทายพอดี" และ explore ไปทาง task เหล่านั้นโดยอัตโนมัติ เรียน motor skills หลากหลายโดยไม่ต้องโปรแกรม curriculum

**Curriculum Learning (Bengio et al. 2009):**

เรียนจาก "ง่ายไปยาก" ดีกว่าเรียนจาก random order ทุกครั้ง paper นี้พิสูจน์บน NLP และ vision: curriculum ที่จัด sample ตาม difficulty → converge เร็วกว่า, generalize ได้ดีกว่า vs training แบบ random shuffled

"ง่าย" คือ sample ที่ model เกือบจะ predict ถูกแล้ว ยากคือ sample ที่ prediction error สูงมาก — curriculum เรียนรู้ได้จาก prediction error ของ model เอง (self-paced learning)

**ทารก + พ่อแม่ = multi-agent curriculum:**

พ่อแม่เป็น "curriculum controller" ที่เลือก environment ให้ทารก: ของเล่นที่ซับซ้อนพอเหมาะ ไม่เล็กเกินหรือใหญ่เกินสำหรับระดับพัฒนาการ ทารกเป็น "curiosity-driven agent" ที่เลือกจะ engage กับสิ่งที่ "interesting" (prediction error ระดับกลาง) ในสิ่งที่พ่อแม่เตรียมไว้

ในเชิง system: พ่อแม่ narrow distribution ของ training distribution ให้เหมาะสม; ทารก narrow ลงอีกด้วย attention โดย curiosity สองชั้นนี้ซ้อนกัน

**Developmental robotics (Oudeyer & Kaplan 2007):**

"Learning by stages" — ไม่ expose ทุก complexity ตั้งแต่ต้น แต่เริ่มจาก sensorimotor simple (จับของ) → ภาษา simple → โลกสังคม เหมือน bootstrapping curriculum ที่แต่ละ stage ใช้ capability ที่สร้างจาก stage ก่อน

### ผลที่น่าตื่นเต้น

- CURIOUS robot: discover และ master task ที่หลากหลายโดยไม่มี external reward signal — แค่ intrinsic motivation ตาม learning progress
- Curriculum Learning ใน NLP: เทรนด้วย curriculum ที่เรียงตาม sentence length → converge เร็วกว่า 3–5x บน machine translation
- Developmental robotics simulation (Oudeyer 2016): robot ที่มี intrinsic motivation พัฒนา "language-like" behavior จาก scratch ผ่าน stages ที่ emerge จาก curiosity โดยไม่ถูก program ไว้
- Human developmental study: ทารกมี prediction error ที่คำนวณได้จาก eye-tracking — พวกเขา preferentially look at สิ่งที่มี "surprising แต่ understandable" (ไม่ใช่ random noise และไม่ใช่สิ่งที่คุ้นเคยมากเกินไป) — ยืนยัน curiosity เป็น prediction-error-based จริง

### สำหรับเรา

"ดันกลไกพ่อแม่สอนและพฤติกรรมทารกเข้าไป" ของคุณมีรากฐานในสาขาวิชา developmental robotics + intrinsic motivation ที่มีอยู่จริง ชิ้นส่วนที่คุณมีอยู่แล้ว:

- **สัญญาณ prediction error** จาก SCFF front-end (ทำนาย future representation ไม่ได้) → ใช้เป็น curiosity reward ได้ตรงๆ
- **Threshold gate** ของ SCFF (เรียน SCFF เมื่อ goodness ต่ำ, เรียก GD เมื่อ SCFF stall) → นี่คือ self-paced curriculum แบบ implicit อยู่แล้ว
- **Sleep consolidation** → replay ที่ sample จาก hippocampus LUT ตาม recency + surprise (prediction error สูง) → ทารก prefer สิ่งที่ surprising

สิ่งที่เฟส 2 จะเพิ่ม:
- **พ่อแม่ = external curriculum controller** ที่จัดรูป distribution ของ input ตาม developmental stage
- **Multi-level curriculum:** simple patterns → complex patterns → rare/surprising events ตาม learning progress

อนาคตไกล แต่ชิ้นส่วน (prediction error, threshold gate, sleep replay) เป็นพวกที่คุณมีอยู่แล้วพอดี

---

## การปรับแต่งหนึ่งอย่างที่กอบกู้ทั้งระบบ: ทำนาย *representation* ไม่ใช่ *pixel*

นี่คือสิ่งสำคัญที่สุดอันเดียวที่ต้องพกต่อไป และมันคือบทเรียนเดียวกันจากสามเปเปอร์ข้างบน:

| | DPC | PredNet | I-JEPA |
|---|---|---|---|
| Target | Embedding อนาคต | Activation อนาคต (ไม่ใช่ pixel ดิบ) | Embedding ของ masked region |
| Loss | Contrastive | L2 error (per layer) | L2 embedding |
| ผล | Video representation | Hierarchical prediction | Semantic image feature |
| ปัญหา pixel prediction | หลีกเลี่ยง | Layer สูงหลีกเลี่ยง | หลีกเลี่ยงทั้งหมด |

ทั้งสามยืนยันตรงกัน: **ทำนาย representation ที่ encoder สร้าง ไม่ใช่ pixel ดิบ** คือ design principle ที่ทำให้ model เรียนโครงสร้าง ไม่เรียน noise

สำหรับชิปคุณ: vision front-end ไม่ใช่ระบบแยก — **มันคือวงลูปทำนายเฟส 2 ที่เอากล้องมาติด**: retina → encode (SCFF conv) → ทำนาย encoding ของอนาคต → prediction error = สัญญาณเรียนรู้ + curiosity signal + สัญญาณ "ความรู้สึก" ทุก component ที่มีอยู่ใน draft-6.0 ทำหน้าที่เดิมในระบบที่ใหญ่ขึ้น

---

## รูปร่างของคำตอบ (ไฟล์นี้)

Retina/vision front-end ที่เรียนรู้ด้วยการทำนายคือ **ทิศทางอนาคตไกลที่ถูกต้องและมีงานหนุนดี** — การทำนายอินพุตคือสัญญาณ self-supervised ระดับท็อป และการ ground ในการมองเห็นก่อนภาษาคือลำดับ developmental ที่ถูกต้อง **การปรับแต่งที่สำคัญจากสามเปเปอร์** (DPC, PredNet, I-JEPA): ทำนาย **representation ของอนาคต ไม่ใช่ pixel** ไม่งั้นอนาคตที่ระบุไม่ได้แน่ชัดจะบังคับให้โมเดลจำลอง noise และหลอกตัวเอง **DPC** แสดงวิธีทำนาย future embedding ด้วย contrastive loss บน video; **PredNet** แสดง hierarchical version ที่แต่ละชั้นทำนายชั้นก่อนหน้า; **I-JEPA** แสดง simplest design (ทำนาย masked region embedding ด้วย L2 + EMA teacher) สร้างแบบนั้นแล้ว **vision front-end ไม่ใช่ระบบแยก — มันคือวงลูปทำนายเฟส 2 ที่เอากล้องมาติด**: retina → encode → ทำนาย encoding ถัดไป → prediction error = สัญญาณเรียนรู้ + curiosity + ความรู้สึก สัญชาตญาณ **พ่อแม่สอน / พฤติกรรมทารก** คือ *developmental robotics + curriculum + intrinsic motivation* และมันนั่งทับบนชิ้นส่วน threshold gate, prediction error, และ sleep replay ที่คุณมีอยู่แล้วพอดี เก็บมันไว้ที่ขอบฟ้า; อย่าสร้างมันจนกว่าวงลูปง่ายๆ จะคิดได้
