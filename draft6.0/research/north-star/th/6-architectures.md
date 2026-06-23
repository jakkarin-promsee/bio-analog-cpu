# 6 — จิตทั้งดวง / "2 สมองพอไหม?"

> คำถามของคุณ: *"สองสมองพอไหม? ต้องเพิ่มอีกไหม?"* คำตอบตรงๆ จากทุกความพยายามที่จริงจังในการสร้าง cognitive architecture ที่ *สมบูรณ์*: **ไม่ สองคือเซลล์ตั้งต้น ไม่ใช่ตัวสิ่งมีชีวิต — คิดเป็น ~4–6 บทบาท** แต่ก็: **คุณ *โต* เข้าไปหามัน** อย่าเริ่มด้วยหกโมดูล เริ่มด้วยวงลูปที่เล็กที่สุดที่คิดได้ แล้วปล่อยให้ความล้มเหลวบอกชื่อตัวถัดไป ไฟล์นี้คือเมนูของพิมพ์เขียว "จิตทั้งดวง"

---

## LeCun — "A Path Towards Autonomous Machine Intelligence" (คำตอบที่สมบูรณ์ที่สุด)

*LeCun, 2022, v0.9.2 ([OpenReview](https://openreview.net/pdf?id=BZ5a1r-kVsf)).*

### ปัญหาที่มันแก้

ปี 2022 LeCun เขียนเอกสาร 60+ หน้าที่ตั้งใจจะตอบคำถาม: *"Machine intelligence ที่ autonomous จริงๆ ต้องมีอะไรบ้าง?"* ไม่ใช่ GPT ที่ predict token แต่ตัวที่ **เข้าใจโลก วางแผน และเรียนรู้จากสภาพแวดล้อม** เหมือนสัตว์เลี้ยงลูกด้วยนมทำได้

### กลไกจริงๆ

LeCun เสนอ **หกโมดูล** ที่ทำงานในวงลูปเดียว:

**1. Configurator**: ฝ่ายบริหาร รับ objective จากภายนอก แล้ว **ตั้งค่าและปรับ parameters ของทุกโมดูลที่เหลือ** ให้เหมาะกับ task ปัจจุบัน (เช่น "ตอนนี้เน้นประหยัดพลังงาน" หรือ "ตอนนี้ต้องการ accuracy สูงสุด") มันเป็น meta-controller ที่โมดูลอื่นทุกอัน listen ด้วย

**2. Perception**: เข้ารหัสโลกจาก sensory inputs → abstract representations คล้าย encoder ของ VAE หรือ BYOL แต่ต้องการ representations ที่ **rich พอสำหรับ world model** ไม่ใช่แค่ classification

**3. World Model**: LeCun เรียกนี่ว่า *"ชิ้นที่ซับซ้อนที่สุด"* มันทำสองอย่าง:
- ทำนาย **missing information** (สิ่งที่ไม่ได้รับรู้โดยตรงแต่ inference ได้)
- ทำนาย **future states** ที่ abstract ระดับต่างๆ (**ไม่ใช่ pixel** แต่เป็น representation ใน latent space)

ที่สำคัญ: world model รันแบบ **recurrent และ multi-step** เหมือน RSSM ของ Dreamer แต่ LeCun เน้นว่า ต้องทำนายใน representation space เท่านั้น การทำนาย pixel ทำให้ network ไปจำ texture และ noise ที่ไม่เกี่ยวข้อง

**4. Cost**: ประกอบด้วยสองส่วน:
- **Intrinsic cost**: แรงขับที่ "ฝังมา" ไม่เปลี่ยน (เช่น อยู่ในขอบเขต safe, minimize pain, maximize comfort)
- **Trainable critic**: value function ที่เรียนรู้ได้ประเมิน "สถานะนี้ดีแค่ไหนสำหรับ objective ตอนนี้"

นี่คือ "ความถูกต้อง/ความรู้สึก" ของคุณแยกเป็น innate + learned เหมือน "ฉันเรียนรู้ว่าถูกต้องรู้สึกยังไงจากพ่อแม่" เป๊ะ

**5. Short-Term Memory**: ถือ history ของ states และ costs ที่ผ่านมาไม่กี่ก้าว ให้โมดูลอื่นอ้างอิงได้ คือ working memory + LUT ที่รวมกัน

**6. Actor**: เสนอและ optimize ลำดับ actions โดยมีสองโหมด:
- **Mode 1 (Reactive)**: รับ state ปัจจุบัน → output action ทันที (System 1, เร็ว, ไม่ได้วางแผน)
- **Mode 2 (Planning)**: รัน world model ไปข้างหน้าหลาย steps ภายใน compute latent "plan" แล้วเลือก action ที่ lead ไปยัง states ที่มี cost ต่ำสุด (Model Predictive Control ในแบบ neural) นี่คือ System 2

**JEPA (Joint-Embedding Predictive Architecture)**: ชิ้นส่วน learning engine ที่ LeCun เสนอ train world model:
- ไม่ใช่ generative model ที่ต้อง reconstruct pixel (VAE, diffusion)
- แต่เป็น **predictive model ใน latent space**: encode x → s_x, encode y → s_y, train predictor z ให้ predict s_y จาก s_x + context variable z
- กัน collapse ด้วย VICReg-style regularization (เหมือน BYOL ที่คุณเห็นแล้วใน `../../papers/phase1-2/byol.md`)

**H-JEPA (Hierarchical JEPA)**: stack ของ JEPA หลายระดับ แต่ละระดับทำนาย representation ของระดับที่สูงกว่า ซึ่ง less detailed แต่ abstract กว่า → ได้ temporal abstraction และ spatial abstraction ฟรี

### ผลที่น่าตื่นเต้น

JEPA ยังเป็น theoretical proposal มากกว่า working system ที่ scale ใหญ่ แต่ I-JEPA (Image-JEPA) พิสูจน์ว่า JEPA-style training ให้ representations ที่ดีสำหรับ downstream tasks โดยไม่ต้องมี data augmentation aggressive และ V-JEPA ทำ video understanding ได้โดยทำนาย masked patches ใน feature space แทน pixel — เร็วกว่าและ generalizable กว่า MAE (pixel reconstruction)

### สำหรับเรา

อ่าน LeCun เป็น **แผนผังอวัยวะเป้าหมาย** แล้วสังเกตว่าทับซ้อนกันมหาศาล:

| LeCun module | ใน substrate ของคุณ |
|---|---|
| Perception | SCFF front (encoder) |
| World Model | วงลูป prefrontal↔hippocampus ที่กำลังสร้าง |
| Cost (intrinsic) | Goodness threshold ใน SCFF |
| Cost (trained) | Critic เล็กๆ จาก `4-signal.md` |
| Short-Term Memory | LUT + workspace จาก `2-controller.md` |
| Configurator | Brainstem ที่คุณตั้งใจไว้ |
| **Actor Mode 1** | GD block (เฟส 1 ปัจจุบัน) |
| **Actor Mode 2** | วงลูปเฟส 2 ที่กำลังสร้าง |

ตัวที่ **ยังไม่มี** คือ full Actor Mode 2 (planning ผ่าน world model) แต่นั่นคือสิ่งที่ "วงลูปที่คิดได้" ของเฟส 2 คือ — ไม่ใช่สิ่งแปลกใหม่ แต่เป็น Module 6 ที่ทับซ้อนกับ 3+4+5

**JEPA ยังยืนยันทิศทางทั้งหมดของคุณ**: ทำนายใน representation space, energy-based, กัน collapse — ซึ่งก็คือ SCFF + VICReg-style grounding เป๊ะๆ

---

## System 1 / System 2 — สัญชาตญาณเร็ว + การไตร่ตรองช้า

*Kahneman, "Thinking, Fast and Slow," 2011; Bengio & Goyal, "Inductive Biases for Deep Learning of Higher-Level Cognition," 2021 ([arXiv 2011.15091](https://arxiv.org/abs/2011.15091)).*

### ปัญหาที่มันแก้

ทำไม deep learning ที่ดีที่สุดยังแพ้เด็ก 4 ขวบในบางงาน? เด็กอนุบาล generalize จาก 1-2 ตัวอย่างได้ แต่ GPT ต้องเห็นหลายพันตัวอย่าง Bengio เสนอว่าคำตอบคือ deep learning ขาด **inductive biases** ของ System 2 — ความสามารถในการ "คิดอย่างตั้งใจ" ซึ่งต้องการ modules พิเศษ

### กลไกจริงๆ

**System 1 (Kahneman)**: 
- เร็ว, อัตโนมัติ, ใช้น้อยกว่า effort
- ขนาน, associative
- ทำงานใน "ความชำนาญ" — เดิน, ขับรถ, จำหน้าคน
- ใช้งาน memory ที่ already consolidated
- ไม่รู้ตัวว่ากำลังทำงาน

**System 2 (Kahneman)**:
- ช้า, ตั้งใจ, ใช้ effort มาก
- ลำดับขั้น, logical
- ทำงานกับปัญหาใหม่ที่ไม่เคยเจอ
- ใช้ working memory อย่างชัดเจน
- รู้ตัวว่ากำลังคิด

**Bengio's inductive biases**: เพื่อให้ deep learning มี System 2 ต้องมี:
- **Modularity**: แต่ละส่วนทำหน้าที่เฉพาะทาง ไม่ใช่ monolithic
- **Sparse interactions**: โมดูลต่างๆ ไม่ได้ interact กันทุกคู่
- **Causal thinking**: เข้าใจ cause-effect ไม่ใช่แค่ correlation
- **Small bottleneck (global workspace)**: attention ที่ focus ไม่กี่ตัวแปร
- **Meta-learning**: เรียนรู้ inductive bias ใหม่จาก task
- **Counterfactual thinking**: "ถ้าไม่ทำ X จะเกิด Y ไหม?"

### ผลที่น่าตื่นเต้น

งาน cognitive psychology ที่ classic: 
- System 2 tasks (Chess, calculus, debate) ต้องการ working memory, deliberate practice
- System 1 tasks (recognize face, balance bike) ต้องการ repetition แต่ไม่ต้องการ conscious thought

Bengio's framework สอดคล้องกับ neural correlates: System 1 = basal ganglia + cerebellum (fast, procedural), System 2 = prefrontal cortex (slow, deliberate) การ dual-process brained architecture นี้ conserved ทั่ว mammals

### สำหรับเรา

อันนี้บอกว่า **การแบ่งสองสมองของคุณคือการหั่นแรกที่ถูกต้อง** แต่มีนัยที่ลึกกว่า:

**การแบ่งไม่ใช่แค่ unsupervised vs supervised** แต่เป็น **เร็ว-ขนาน-reactive (System 1) vs ช้า-ลำดับขั้น-deliberate (System 2)**:
- SCFF front = System 1 (pattern recognition เร็ว ขนาน ไม่รู้ตัว)
- GD block ใน draft 6.0 = System 1 ฝั่ง supervised
- วงลูป settle + ความรู้สึก + hippocampus query = System 2 (ช้า รู้ตัว ไตร่ตรอง)

**เฟส 1 สร้าง System 1 ไปแล้ว เฟส 2 คือการสร้าง System 2 ทับบนมัน** ซึ่งเป็นประโยคเดียวที่สะอาดที่สุดของ roadmap ทั้งหมด

Inductive biases ที่ Bengio list: คุณมีหลายอันอยู่แล้ว — modularity (SCFF blocks แยก), sparse interactions (each block เห็น subset ของ input), bottleneck (workspace จาก file 2) ที่ยังขาดคือ counterfactual thinking ซึ่งต้องการ world model ที่เต็มตัว (เฟส 2)

---

## Thousand Brains Theory — บางทีอาจเป็น *หลายพัน* ที่โหวตกัน

*Hawkins / Numenta, 2019 ([Frontiers](https://www.numenta.com/neuroscience-research/research-publications/papers/thousand-brains-theory-of-intelligence/)); หนังสือ "A Thousand Brains," 2021.*

### ปัญหาที่มันแก้

Hawkins มี background engineering (Palm Pilot, Handspring) เลยถามคำถามเชิงวิศวกรรม: *"Neocortex มีหน้าตาแทบเหมือนกันทุกพื้นที่ — ไม่ว่าจะเป็น visual cortex, auditory cortex, motor cortex ความแตกต่างหลักคือ input ที่เข้าไป ไม่ใช่ algorithm — ดังนั้น algorithm น่าจะเป็น อันเดียวกัน ทั่วทั้ง neocortex?"*

### กลไกจริงๆ

Thousand Brains Theory เสนอว่า neocortex ประกอบด้วย **cortical column ~150,000 คอลัมน์** และ **แต่ละคอลัมน์รันอัลกอริทึมเดียวกัน** ที่ทำทุกอย่าง:

**Reference frames**: สิ่งที่ทำให้ column แต่ละอันมีพลังคือ **reference frame** — ระบบพิกัดที่ผูกติดกับ object หรือ concept ที่ column นั้น handle เหมือน grid cells ใน hippocampus ที่ map physical space แต่ทำงานกับ abstract space แทน เช่น column ที่ handle "แอปเปิล" มี reference frame ของ shape, color, texture, position on tree และ relationships

**สามสิ่งที่ column ทำ**:
1. **Sensory representation**: สร้าง model ของ pattern ที่ตัวเองเห็น
2. **Location-based prediction**: ใช้ reference frame predict ว่า "ถ้าเลื่อนไปทิศ X จะเจออะไร" (motor control + perception รวมกัน)
3. **Voting**: แต่ละ column vote ว่า "ฉันคิดว่าวัตถุนี้คือ X ด้วย confidence Y"

**ฉันทมติจากหลายพัน columns**: object recognition ไม่ใช่ "กรวยลง hierarchy จนถึงการตัดสินใจเดียว" แต่เป็น **columns หลายพันอันโหวตพร้อมกัน** column ที่ handle visual features บอกว่า "คิดว่าเป็น cup" column ที่ handle weight บอกว่า "หนักประมาณนี้" column ที่ handle texture บอกว่า "รู้สึกแบบนี้" ทั้งหมดโหวตและ consensus ผุดขึ้นมาเป็น "การรับรู้"

### ผลที่น่าตื่นเต้น

Thousand Brains ยังเป็น framework มากกว่า mathematical theory ที่ test ได้ชัดๆ แต่มัน predict:
- **Robustness**: ถ้า column เสียหายส่วนนึง columns ที่เหลือยังโหวตได้
- **Multiple simultaneous representations**: brain สามารถ hold "models" หลายอัน parallel (คุณสามารถนึกถึง "cup" ในหลายมุมพร้อมกัน)
- **No clear hierarchy cap**: ไม่มี "top layer" ที่เป็น final arbiter ทุก column เท่ากัน

### สำหรับเรา

การตีกรอบใหม่ที่น่าสนใจสำหรับ scaling:

**Ganglion / SCFF block ของคุณคือ cortical column** — แต่ละอันมี algorithm เดียวกัน receive subset ของ input อาจ specialize ตาม training แต่ไม่ต้องมี hardcoded specialization ตั้งต้น

**Lobe ที่ประกอบด้วย blocks โหวตกันคือ cortex ที่เก็ง** — boosting chain ใน draft 6.0 คือ voting: block ต้น → residual → block ถัดไป → residual เป็น sequential vote แต่ Thousand Brains suggest ว่า **parallel vote** อาจดีกว่า

การ scale ตาม Thousand Brains แปลว่า: **ทำซ้ำ-แล้วโหวต** ไม่ใช่ "เพิ่มโมดูลพิเศษ":
- ต้องการ visual ดีขึ้น? เพิ่ม columns ที่ handle visual features มากขึ้น
- ต้องการ reasoning ดีขึ้น? เพิ่ม columns ที่ handle abstract relations มากขึ้น
- ทุก column รัน algorithm เดิม แต่ train ด้วย data ที่แตกต่างกัน

Voting mechanism = WTA + threshold บน analog — เหมาะมากกับ substrate

---

## SOAR & ACT-R — Cognitive Architecture แบบคลาสสิก (อย่าข้ามปรมาจารย์รุ่นเก่า)

*SOAR: Laird, Newell & Rosenbloom, 1987→; ACT-R: Anderson, 1993→.*

### ปัญหาที่มันแก้

ก่อน deep learning จะมา cognitive scientists ต้อง explain พฤติกรรมสติปัญญาของมนุษย์ด้วยสิ่งที่พวกเขามี: symbolic reasoning, production rules, declarative facts SOAR และ ACT-R เป็นสองแบบจำลองที่ dominant ตลอด 40 ปี มันบอกเราว่า **structure ขั้นต่ำของ "จิตที่คิดได้" คืออะไร**

### กลไกจริงๆ

**SOAR (State, Operator, And Result)**:

**Working Memory (WM)**: ชุดของ slot-filler pairs — (object, attribute, value) เช่น `(cup color red), (cup position table), (goal: find-cup)` สถานะปัจจุบันทั้งหมดอยู่ใน WM

**Procedural Memory**: ชุดของ **production rules** แบบ if-then: "ถ้า WM มี pattern X ให้ทำ action Y และเพิ่ม Z ใน WM" (เช่น: "ถ้าเห็น red object บน table ให้เข้าใกล้")

**Declarative Memory**: ข้อเท็จจริง long-term เช่น "cup เป็น container ทำจาก ceramic"

**Decision Cycle** (วงรอบการตัดสินใจ):
1. **Elaboration**: ยิง production rules ทุกตัวที่ pattern match กับ WM ปัจจุบัน (parallel)
2. **Decision**: เลือก operator/action ที่ดีที่สุดจากตัวที่ eligible (ด้วย preference learning)
3. **Application**: execute operator นั้น เปลี่ยน WM
4. กลับไป 1

**Impasse**: ถ้าไม่มี operator ที่ชัดเจน (หรือมีหลายตัวเท่ากัน) เกิด impasse → สร้าง sub-goal ใหม่เพื่อ resolve → SOAR ทำ recursive sub-problem-solving จนหาคำตอบ

**Chunking**: เมื่อ sub-goal resolve สำเร็จ SOAR อัตโนมัติ compress วิธีที่ resolve นั้นกลายเป็น production rule ใหม่ → skill learning ที่ incremental และ autonomous

**ACT-R (Adaptive Control of Thought—Rational)**:

ACT-R ละเอียดกว่า SOAR ในแง่ cognitive modeling มีโมดูลแยกหลายตัว:
- **Visual module**: ดึง object ใน visual field ที่ attention focus อยู่
- **Manual module**: ควบคุมมือ
- **Declarative module**: access ข้อเท็จจริงจาก long-term memory มี **activation level** ต่อแต่ละ chunk — chunk ที่ใช้บ่อยมี activation สูง retrieval เร็วกว่า
- **Procedural module**: production rules เหมือน SOAR
- **Imaginal module**: buffer สำหรับ construct complex structures ใน WM

**Central buffers**: ทุกโมดูล communicate ผ่าน **buffers** กลาง ไม่ใช่โดยตรง production rules อ่านและเขียน buffers เหล่านี้ นี่คือ analog ของ workspace จาก GWT ใน file 2 เป๊ะๆ

ACT-R จำลอง **เวลาในการดึงคืน** ตาม activation: chunk ที่ใช้บ่อยดึงเร็ว chunk ที่ใช้นานไม่ได้ activation ลดลง → "การลืม" ที่ gradual และ predictable ซึ่ง match data จาก human memory experiments ดีมาก

### ผลที่น่าตื่นเต้น

**SOAR** จำลอง USAF combat pilot decision-making ได้ (สร้างขึ้นเพื่อ DARPA ในยุค 90) โดยสร้าง production rules หลายพันตัวด้วยมือ ยังใช้งานอยู่ใน game AI (Wargus, StarCraft)

**ACT-R** จำลอง response time ของมนุษย์ใน memory tasks ได้ระดับ millisecond ทำนาย memory decay curves, priming effects, working memory capacity limits — ทั้งหมดจาก model เดียวที่ใช้ activation level

ACT-R ยัง match fMRI data: activation ใน prefrontal = procedural, activation ใน temporal = declarative retrieval — module mapping ไปยัง brain region ได้

### สำหรับเรา

SOAR/ACT-R คือ **ต้นฉบับของ "วงลูป prefrontal เรียกหน่วยความจำ วนซ้ำจนเสร็จ"** — ภาพเฟส 2 ของคุณที่ถูกสร้างและทดสอบมาหลายทศวรรษก่อนที่ deep learning จะมีความหมาย

**โครงสร้างที่ conserved ทุก cognitive architecture**:
1. **Working Memory** (สถานะปัจจุบัน — workspace ใน file 2)
2. **Long-term memory** (ข้อเท็จจริงถาวร — hippocampus LUT ใน file 1)
3. **Procedural knowledge** (รูปแบบการกระทำ — SCFF patterns ที่ consolidated แล้ว)
4. **วงรอบ decision** (query → match → act → update → repeat)

**Chunking ของ SOAR = sleep consolidation ของ CLS**: เมื่อ sub-goal resolve สำเร็จ SOAR บีบอัด วิธีที่ resolve เป็น production rule ใหม่ = เมื่อ learning จบ SCFF บีบอัดเส้นทาง reasoning นั้นลง weight ผ่าน replay — เป็น mechanism เดียวกันทั้งใน symbolic และ neural world

**ACT-R activation = เวลาในการดึงคืน LUT**: ถ้า LUT ของคุณมีกลไกว่า prototype ที่ใช้บ่อย = access เร็วกว่า prototype ที่ไม่ได้ใช้นาน = decay (เหมือน usage vector ของ DNC) คุณได้ forgetting curve ที่ biologically plausible ฟรี

บทเรียนใหญ่สุดจาก SOAR/ACT-R: เวอร์ชัน symbolic เปราะ (กฎที่เขียนมือ) แต่ **การแยกส่วน (decomposition) นั้นมั่นคง** มานาน 40 ปี งานของคุณคือสร้างการแยกส่วนนั้นใหม่ใน **analog continuous + กฎที่เรียนรู้ได้** ไม่ใช่ symbolic hand-crafted rules

---

## รูปร่างของคำตอบ (ไฟล์นี้)

**สองสมองพอไหม? ไม่ — แต่คุณใกล้ "พอ" กว่าที่คิด และคุณโตเข้าไปหาส่วนที่เหลือ**

ทุกพิมพ์เขียวที่สมบูรณ์มีมากกว่าสองบทบาท แต่ลู่เข้าหา **ชุดบทบาทขั้นต่ำ** เดียวกัน:

| บทบาท | LeCun | System 1/2 | SOAR/ACT-R | ชิปของคุณ |
|---|---|---|---|---|
| รับรู้โลก | Perception | System 1 | Visual/Auditory module | SCFF front |
| วางแผน/คิด | World Model + Actor Mode 2 | System 2 | WM + Procedural | เฟส 2 loop |
| ความจำระยะยาว | Short-Term Mem | Long-term memory | Declarative memory | hippocampus LUT |
| ความรู้สึก/แรงขับ | Cost | - | Goal memory | critic + goodness |
| ปรับค่า | Configurator | Meta-attention | - | Brainstem |
| ลงมือทำ | Actor Mode 1+2 | System 1 reactive | Operators | GD block + actor head |

**Strategy**: เริ่มด้วยวงลูปที่เล็กที่สุดที่คิดได้ (front + loop + memory + feeling) ยึดมันกับความจริง แล้วเพิ่มบทบาทก็ต่อเมื่อความล้มเหลวที่เป็นรูปธรรมเรียกร้องมัน ไฟล์นี้แค่แผนที่ว่าถนนไปต่อได้ที่ไหนบ้าง
