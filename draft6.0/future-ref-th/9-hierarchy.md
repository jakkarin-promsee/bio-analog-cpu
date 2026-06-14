# 9 — ลำดับชั้น: คนอื่นเขาประกอบระดับชั้นกันยังไง

> คำพูดของคุณ: *"ลำดับชั้นของสมอง — แบบที่คนอื่นเขาทำกัน"* ลำดับชั้นของ draft-5 คุณ (Scap→Ganglion→Column→Lobe→Limbic) "ดูดี แต่ยังไม่สมบูรณ์" ไฟล์นี้คือวิธีที่ *คนอื่น* จัดโครงสร้างระดับชั้น — และข้อตระหนักสำคัญที่ปรากฏในทุกอัน: **ลำดับชั้นไม่ใช่แค่กองซ้อน มันคือวงลูป** (การทำนายจากบนมาเจอหลักฐานจากล่าง) ที่มี **โครงสร้างเปลี่ยนตามอินพุตแบบไดนามิก** ไม่ใช่พีระมิดตายตัว

---

## Hierarchical Predictive Coding — ลำดับชั้นคือถนนสองทาง

*Rao & Ballard, 1999; กรอบ: Friston. (ดู `4-signal.md`, `../concept/predictive-coding.detail.md` ด้วย)*

### ปัญหา: ลำดับชั้นที่ไหลทางเดียวขาดครึ่ง

CNN มาตรฐานและ draft-5 hierarchy ของคุณเป็น **bottom-up เพียงอย่างเดียว**: สัญญาณไหลขึ้นจาก input → features ต่ำ → features สูง → output Loss กระจายลงผ่าน backprop แต่นั่นเป็นเทรนเท่านั้น — ใน inference ข้อมูลไหลขึ้นเพียงอย่างเดียว

ปัญหาที่ตามมา: ระดับสูงไม่สามารถ "บอก" ระดับต่ำว่า "คาดหวังอะไร" จึงไม่มีกลไก top-down ที่ช่วยตีความอินพุตที่ ambiguous ไม่มี context ช่วย นั่นคือทำไมคุณรู้สึกว่า "ลำดับชั้นยังไม่สมบูรณ์"

### กลไก: ส่ง prediction ลง, ส่ง error ขึ้น

Rao & Ballard 1999 เสนอ model ของ visual cortex ที่เปลี่ยนทุกอย่าง:

**โครงสร้าง:** ลำดับชั้น L levels แต่ละ level มีสองส่วน:
- **Representation unit r:** state ของ level นี้ — เป็น belief ว่าโลกเป็นยังไง
- **Error unit e:** ความแตกต่างระหว่าง prediction จากบน กับ representation จากล่าง

**Dynamics ใน inference:**
1. Level ​L+1 ส่ง **top-down prediction** ลงมาที่ level L: `pred_L = f(r_{L+1})`
2. Level L คำนวณ **prediction error**: `e_L = r_L − pred_L`
3. Error ถูกส่ง **ขึ้น** ไปยัง level L+1 เพื่อ update r_{L+1}: `dr_{L+1}/dt ∝ −e_L`
4. ทั้งก้อน **iterate** จนกระทั่ง error ใน every level minimize (settle)

สัญญาณที่ขึ้นไม่ใช่ activation ดิบ มันคือ **prediction error** ที่ระดับสูงกว่ายังไม่สามารถอธิบายได้

**Karl Friston** ขยาย framework นี้เป็น **Active Inference** ซึ่ง agent ทำ action เพื่อ minimize prediction error ทั้งผ่านการเรียนรู้ (update model) และผ่าน action (เปลี่ยน world ให้ตรงกับ prediction)

### ผลที่ได้

Rao & Ballard ทดสอบบน natural image patches: model predictive coding สามารถ explain ปรากฏการณ์ใน V1 ที่ feedforward model ไม่สามารถอธิบายได้:
- **End-stopping:** นิวรอนที่ตอบสนองต่อ line segment ที่ไม่ยาวเกินไป — อธิบายได้ว่า long line ถูก predict ได้โดย higher level จึงมี error น้อย แต่ end ที่ไม่ถูก predict ให้ error สูง
- **Extra-classical receptive field effects:** context นอก receptive field ส่งผล — อธิบายได้ว่า top-down prediction จาก higher level พก context

งานสมัยใหม่ (Friston et al.): Predictive Coding เชื่อมกับ Bayesian Brain hypothesis — brain คือ Bayesian inference machine ที่ update prior (top-down) ด้วย likelihood (bottom-up error)

### สำหรับเรา

ลำดับชั้น draft-5 ของคุณเป็น bottom-up อย่างเดียว — ชิ้นที่ขาดคือ **top-down prediction loop**

สำหรับเฟส 2: template ชัดเจน — แต่ละ level ทำนายระดับล่าง ส่ง error ขึ้น ทั้งก้อน settle ก่อนตัดสินใจ มันยังบอกว่า *อะไรควรไหลระหว่างระดับ*: **prediction ลง, error ขึ้น** ไม่ใช่ activation ดิบ

ที่สำคัญสำหรับ substrate: prediction error `e = r - pred` เป็น **subtraction operation** ซึ่ง capacitor + differential amplifier ทำได้ native และ error ที่เป็น sparse (เฉพาะส่วนที่ predict ผิดพลาดถูกส่งขึ้น) ตรงกับ sparse computation ของ substrate

---

## GLOM — ลำดับชั้นเป็น *ไดนามิก* สร้างขึ้นจากการเห็นพ้อง

*Hinton, 2021 ([arXiv 2102.12627](https://arxiv.org/abs/2102.12627)).*

### ปัญหา: fixed hierarchy แยก input ที่ต่างกันเป็น part-whole tree ที่ต่างกันได้ยังไง?

นี่คือคำถามที่รบกวน Hinton มาหลายสิบปี: โลกประกอบด้วย *object* ที่มี *parts* ที่มี *subparts* แต่ tree structure แตกต่างกันสำหรับทุก input ("แมว" มี tree ต่างจาก "รถ") ถ้า hierarchy ถูก hardwired มันจะ parse object ที่ต่างกันด้วย structure ที่ต่างกันได้ยังไง?

คำตอบ: **ไม่ต้อง hardwire** ให้ parse tree ผุดขึ้นแบบ dynamic จากการเห็นพ้อง

### กลไก: columns ทุกตำแหน่ง × ทุกระดับ → islands of agreement

**Architecture:**

Image ถูกแบ่งเป็น grid ของ "locations" แต่ละ location มี **column** ที่พก embeddings หลายระดับ:
```
Location (x,y): [z_1(x,y), z_2(x,y), ..., z_L(x,y)]
```
z_l(x,y) คือ embedding ของ level l ที่ location (x,y) — เวกเตอร์หนึ่งตัวต่อ level ต่อ location

**Update rule สำหรับแต่ละ embedding:** ได้รับ influence จากสามทิศทาง:
1. **Bottom-up:** z_{l-1} ที่ location เดียวกัน (สิ่งที่ level ล่างเห็น)
2. **Top-down:** z_{l+1} ที่ location เดียวกัน (สิ่งที่ level สูงคาดหวัง)
3. **Lateral:** z_l ที่ locations *ใกล้เคียง* (consensus จาก neighbors ในระดับเดียวกัน) — นี่คือกุญแจ

Update ด้วย weighted average ของสามแหล่ง iterate หลายรอบ

**ผล: "Islands of Agreement"**

หลังจาก iterate parse tree ปรากฏเป็น **เกาะของ locations ที่ agree กันในแต่ละระดับ**: หากหลาย locations ที่ level 3 settle ลงสู่เวกเตอร์เดียวกัน นั่นหมายความว่าพวกมัน "agree" ว่าเป็น object เดียวกัน เป็น dynamic grouping ที่ไม่มีใคร "decide" — มันผุดขึ้นเองจากการเห็นพ้อง

ลำดับชั้นไม่ได้เดินสายมาตายตัว แต่ **ผุดขึ้นเป็นเกาะแห่งฉันทมติ สด ๆ สำหรับแต่ละ input**

### ผลที่ได้

GLOM เป็น position paper มากกว่า empirical work — Hinton ไม่ได้ implement เต็มรูปแบบ แต่แนวคิดถูก explore ต่อโดยคนอื่น:

- งาน follow-up แสดงว่า transformer attention เป็น approximation ของ lateral agreement ใน GLOM
- "Part-whole parsing" ที่ dynamic เป็น property ที่ vision model สมัยใหม่ยังต้องการ
- GLOM เป็น inspiration สำหรับ architectures หลายตัวที่ "object-centric" ในภายหลัง

### สำหรับเรา

นี่คือคำตอบของ "ลำดับชั้นฉันยังไม่สมบูรณ์" — ชิ้นที่ขาดมักเป็นว่า **ลำดับชั้นควรเป็นไดนามิกและอิงฉันทมติ ไม่ใช่พีระมิดตายตัว**

**"เกาะของการเห็นพ้อง"** คือกลไก vote/settle ที่ substrate แอนะล็อกทำได้แบบ native และ Thousand-Brains ใน `6-architectures.md` ก็สะท้อนกัน

GLOM ยังรวมระดับของคุณเข้าด้วยกัน: ทุกระดับเป็นคอลัมน์ *ชนิดเดียวกัน* ที่รัน *กระบวนการเดียวกัน* (bottom-up + top-down + lateral) — สัญชาตญาณ self-similar ของ draft-5 ที่ถูกต้อง แต่ต้องทำให้ชัดว่าเป็น **กระบวนการ** ที่ซ้ำ ไม่ใช่แค่โครงสร้าง

Lateral agreement ใน analog: capacitors ใน neighboring columns charge/discharge ผ่าน resistive coupling ตามธรรมชาติ — นั่นคือ lateral diffusion ที่ implement island formation ได้โดยไม่ต้องการ digital logic

---

## Hierarchical Temporal Memory (HTM) — ทุกบริเวณรัน *อัลกอริทึมเดียวกัน* บนโค้ด sparse

*Hawkins / Numenta. ([HTM School](https://numenta.com/htm-school/), [คุณสมบัติ SDR](https://arxiv.org/pdf/1503.07469)).*

### ปัญหา: ลำดับชั้นที่รู้เวลาและ self-similar คืออะไร?

Hawkins ถามว่า neocortex ทำอะไรกันแน่ทุก region ของ cortex มีโครงสร้างเหมือนกัน (6 ชั้น, minicolumns, มาโคร-columns) แสดงว่า **ทุก region รันอัลกอริทึมเดียวกัน** บน input ที่ต่างกัน ลำดับชั้นเกิดจาก region สูงกว่ารับ pattern ช้ากว่าและ abstract กว่าจาก region ต่ำกว่า — ไม่ใช่จาก algorithm ที่ต่างกัน

HTM เป็นความพยายามสร้าง "อัลกอริทึมเดียวนั้น"

### กลไก: SP + TM ซ้ำในทุกระดับ

HTM มีโมดูลหลักสองตัวที่ทุก region รัน:

---

**Spatial Pooler (SP):** แปลง input เป็น SDR ที่มี sparsity คงที่

Input: binary vector (หรือ SDR) จาก level ล่าง
Output: SDR ที่มี sparsity ≈ 2% เสมอ

วิธี: มี "minicolumns" จำนวนมาก แต่ละ minicolumn มี "proximal dendrites" ที่เชื่อมกับ input subset สุ่ม Feedforward input excite minicolumns ที่มี overlap กับ active inputs สูงสุด แล้ว **k-Winner-Take-All** เลือก k minicolumns ที่ excited ที่สุด ที่เหลือ inhibit การเรียนรู้: Hebbian — ถ้า minicolumn ชนะ, strengthen synapses กับ active inputs (online, local)

ผล: SP map input ที่หลากหลายเป็น SDR ที่ consistent — input ที่คล้ายกัน → SDR ที่ overlap กัน input ที่ต่างกัน → SDR ที่ไม่ overlap

---

**Temporal Memory (TM):** เรียนรู้ sequence ของ SDR และทำนาย next SDR

HTM columns แต่ละ column มีหลาย **cells** (ประมาณ 4-16 cells ต่อ column) cells แยกกัน encode context ที่ต่างกันของ column เดียวกัน

Mechanism:
1. เมื่อ column ถูก activate โดย SP: ถ้ามี cell ที่ **predict** ว่ามันจะ active (มี active distal dendrites จาก previous state) → เฉพาะ cell นั้นที่ active ("predicted activation") ถ้าไม่มี cell ที่ predict → ทุก cell ใน column active ("burst") = surprise
2. Cells ที่ predict: มี dendritic segments ที่เชื่อมกับ cells ที่ active ใน previous timestep เมื่อ enough cells ใน segment active → segment "fire" → cell "predict" ว่าตัวเองจะ active ใน next step
3. การเรียนรู้: ถ้า cell ถูก predict และ ถูก activate → reinforce dendritic segment ถ้า cell burst (ไม่ถูก predict) → cell ที่ active ใน previous step เรียนรู้ predictive segment ใหม่

ผล: หลังเรียนรู้ TM predict ว่า column ไหนจะ active ใน next timestep โดยเฉพาะ cells ที่ตรงกับ context ปัจจุบัน ถ้า context ต่างกัน (A→X vs B→X) cells ต่างกันใน column X จะ active ซึ่งจะ predict differently สำหรับ next step

### ผลที่ได้

HTM เป็น framework ที่ขยายได้ ใน benchmark ที่ Numenta รัน:
- TM เรียน sequence arbitrarily long ได้ โดยไม่ต้องการ training set ที่ complete — เรียนแบบ online one-shot
- SP + TM ร่วมกัน classify speech patterns บน Spoken MNIST ได้ด้วย label น้อยมาก
- ข้อจำกัด: ไม่ได้ scale ไป complex vision/NLP tasks ใน form ปัจจุบัน เป็น research framework

ความสำคัญที่แท้จริงของ HTM: มันเป็น **explicit formalization ของ self-similar temporal hierarchy** — อัลกอริทึมเดียวที่ทำ spatial encoding + temporal prediction รันซ้ำในทุกระดับ

### สำหรับเรา

HTM คือ template ที่สะอาดที่สุดของ **ลำดับชั้น self-similar ที่รู้เวลา** — ซึ่งตรงกับสัญชาตญาณ draft-5 ของคุณ "แต่ละระดับทำสิ่งเดียวกันกับลูกของมัน" แต่มีมิติเวลาฝังมาด้วย

SP = "SCFF ของคุณ" (แปลง input เป็น sparse code ที่ consistent, online, local)
TM = "วงลูปทำนาย temporal ของเฟส 2" ใน every level

ที่น่าตื่นเต้นสำหรับ substrate: ทั้ง SP และ TM เป็น **Hebbian, online, local** — ไม่มี backprop ไม่มี global signal เป็นกฎการเรียนรู้ที่ implement ได้ใน analog substrate อย่างตรงไปตรงมา

Distal dendrites ของ TM cells คือ **eligibility traces** ของ `10-realtime.md` — "ความทรงจำ" ว่า pre-synaptic cells ใด active ใน past ก่อน cell นี้จะ predict

---

## Slot Attention & Object-Centric Learning — ประกอบเป็น *สิ่งของ (things)*

*Locatello et al., NeurIPS 2020 ([arXiv 2006.15055](https://arxiv.org/abs/2006.15055)).*

### ปัญหา: ฉากมีหลาย object แต่ feature map ไม่รู้ว่ามีกี่ชิ้น

CNN และ ViT สร้าง feature map ที่ encode "มีอะไรอยู่ที่ตรงไหน" แต่ไม่ encode "มีกี่ object และ object แต่ละชิ้นคืออะไร" ถ้าอยาก reason เกี่ยวกับ "รถสองคันกับต้นไม้หนึ่งต้น" คุณต้องการ representation ที่ **แยกออกเป็น entities** ก่อน

Slot Attention แก้ปัญหานี้โดยไม่ต้องใช้ label ว่า object อยู่ตรงไหน

### กลไก: slots แข่งกัน "อ้างสิทธิ์" feature

**Setup:** K slots (fixed number) แต่ละ slot เป็นเวกเตอร์ขนาด d — "ตัวแทน" ของ entity หนึ่ง อาจ initialize แบบสุ่มหรือ learnable

**Iterative attention (ทำ T รอบ):**
1. แต่ละ slot คำนวณ attention score กับ feature map ทุก location:
   `A_{slot,loc} = softmax( dot(Q_slot, K_loc) / √d )`
2. **Normalize ข้าม slots** (แทน softmax ปกติที่ normalize ข้าม locations):
   `A'_{slot,loc} = A_{slot,loc} / Σ_{slots} A_{slot,loc}`
   ทำให้ locations ต้องเลือกว่าจะ "เป็นของ" slot ไหน
3. แต่ละ slot update ตัวเองด้วย weighted average ของ features ตาม attention:
   `slot ← GRU(slot, Σ_loc A'_{slot,loc} · V_loc)`

**Normalization ข้าม slots** คือ trick หลัก: มันทำให้ slots **แข่งกัน** ชิง features ถ้า slot A claim region หนึ่ง, slot B ต้อง claim region อื่น นั่นคือ soft exclusive assignment → slot แต่ละตัวจะ specialize ต่อ object ต่างกัน

เทรนด้วย reconstruction loss — decode จาก slots กลับไปสร้าง image ถ้า slots ไม่แยก objects ออก reconstruction ไม่ดี ไม่ต้องมี object labels

### ผลที่ได้

- CLEVR (3D synthetic scenes): Slot Attention แยก objects ออกได้แม่นยำมาก แม้ว่า objects ซ้อนกัน
- Object Properties: แต่ละ slot encode color, shape, size, position ของ object ที่มัน claim
- ใช้ label น้อยมาก: เรียน unsupervised ด้วย reconstruction loss เท่านั้น
- ข้อจำกัด: ยังต้องกำหนด K (จำนวน slots) ล่วงหน้า และ scale ไป real-world images ยากกว่า

### สำหรับเรา

Slot Attention เกี่ยวกับ "อะไรควรไหลระหว่างบล็อก" และกับ workspace concept (`2-controller.md`):

**Slot = "object in working memory"** ถ้าเฟส 2 ต้องการ reason เกี่ยวกับ entities (ไม่ใช่แค่ feature vectors) slots คือวิธีแยก entities จาก continuous input โดยไม่ใช้ labels

**การแข่งชิง slot เป็น winner-take-all:** ธรรมชาติของ analog — lateral inhibition ระหว่าง slots ทำได้ใน substrate การ "claim region" คือ analog attention ที่ implement ด้วย voltage competition

**K slots ที่ทำงาน parallel:** ตรงกับ workspace broadcast — K เรื่องที่กำลังประมวลผลพร้อมกัน แต่ละเรื่อง "own" feature cluster ของตัวเอง

---

## Mixture-of-Experts Routing — ลำดับชั้นที่ sparse และเรียนรู้ได้

*Shazeer et al., 2017 (sparse MoE); Switch Transformer, Fedus et al., NeurIPS 2022.*

### ปัญหา: network ต้องรู้ทุกเรื่องด้วย neurons ทุกตัวเสมอมั้ย?

Network ขนาดใหญ่มักมีปัญหา: เทรนทั้ง 1T parameters แต่สำหรับ input "รูปแมว" คุณ activate 1T parameters เพื่อ process มัน ส่วนใหญ่คงไม่เกี่ยวข้อง compute เปล่า ๆ

MoE ถามว่า: **ทำไมไม่ทำให้เฉพาะ "ผู้เชี่ยวชาญ" ที่ relevant ทำงาน?**

### กลไก: router เลือก expert ที่เกี่ยวข้อง

**Setup:**
- E "experts" — แต่ละตัวเป็น sub-network (มักเป็น FFN ใน transformer)
- Router ขนาดเล็ก G — เรียน assign input ไปยัง experts ที่เกี่ยวข้อง

**Sparse routing (top-k):**
```
g_e = softmax(W_router · x)_e
y = Σ_{e ∈ top-k(g)} g_e · Expert_e(x)
```
เลือกเฉพาะ k experts (มักเป็น k=1 หรือ k=2) ที่มี g_e สูงสุด experts ที่เหลือ **ไม่ทำงานเลย**

**Load balancing loss:** ถ้าไม่มี regularization router จะเรียน assign ทุกอย่างไปยัง expert เดียวที่ดีที่สุด (expert collapse) เพิ่ม auxiliary loss ที่บังคับให้ inputs กระจาย evenly ข้าม experts

Switch Transformer: k=1 (single expert per token) — ง่ายที่สุด compute ต่ำที่สุด ยังดี

### ผลที่ได้

- Switch-C (1.6T parameters, 2048 experts): ดีกว่า T5-XXL (11B) ด้วย training compute น้อยกว่า 7× บน translation/summarization
- 2K experts แต่ active แค่ 1 ต่อ token → effective model ใหญ่มาก แต่ inference cost เท่า expert เดียว
- Mixtral 8×7B (8 experts, top-2): เอาชนะ LLaMA 2 70B หลาย tasks ด้วย active parameters แค่ 13B จาก 47B total

Pattern สำคัญ: experts spontaneously specialize ตาม input type, language, domain — ไม่ต้อง label ว่า expert ไหนทำอะไร มันเกิดขึ้นเองจาก training

### สำหรับเรา

MoE คือไอเดียเดียวกับ RIMs (`2-controller.md`) ที่ระดับลำดับชั้น — **การ route แบบ sparse และมีเงื่อนไข** ให้เฉพาะส่วนที่เกี่ยวข้องทำงาน

นั่นคือคุณสมบัติ **sparse** ของ substrate คุณในฐานะหลักการสถาปัตยกรรม: ลำดับชั้นก้อนใหญ่ที่แต่ละ input จุดเส้นทางเล็ก ๆ ติด (รอบประจุไม่กี่รอบ) router เป็น gate เล็ก ๆ ที่เรียนรู้ได้ (ถูก)

Expert specialization ที่เกิดเอง = feature specialization ของ SCFF ที่คุณต้องการ — ถ้า blocks ของคุณเป็น "experts" ที่ router เลือกตาม input content blocks จะ spontaneously specialize โดยไม่ต้อง supervise

กฎที่ควรจำ: **ลำดับชั้นกว้างและส่วนใหญ่หลับ** ดีกว่า **ลึกและ active ทั้งหมด** ถ้ามี good router

---

## Greedy Layer-wise Growth — สร้างลำดับชั้นทีละระดับ

*Deep Belief Nets: Hinton, Osindero & Teh, Science 2006; Forward-Forward / local learning.*

### ปัญหา: เทรนลำดับชั้นลึก end-to-end ยากก่อน 2012

ก่อน ReLU และ residual connections การเทรน deep network ด้วย backprop โดยตรงทำไม่ได้จริง ๆ gradient vanish ก่อนถึงชั้นต้น Hinton แก้ด้วยการเทรน **ทีละชั้น แบบ greedy** โดยไม่ต้องรู้ว่าชั้นบนสุดจะทำอะไร

### กลไก: เทรนระดับ → แช่แข็ง → เทรนระดับถัดไป

1. เทรน RBM (Restricted Boltzmann Machine) ระดับ 1 บน raw input จนได้ feature ที่ดี
2. **แช่แข็ง** ระดับ 1 (ไม่เปลี่ยน weights อีก)
3. ใช้ output ของระดับ 1 เป็น input ของระดับ 2 เทรน RBM ระดับ 2
4. ทำซ้ำขึ้นไปเรื่อย ๆ
5. Fine-tune ทั้งก้อนด้วย supervised signal ในตอนท้าย (optional)

แนวคิดหลัก: แต่ละระดับ **เรียนรู้ feature ที่ดีของ representation ล่าง** โดยไม่ต้องการสัญญาณจาก task สุดท้าย เป็น greedy locally optimal strategy

นี่คือสิ่งที่ทำให้ deep learning เวิร์ก *ก่อน* ที่ end-to-end backprop จะ scale ได้ดี และมันคือจิตวิญญาณของ:
- **SCFF stacking:** แต่ละ block เรียน representation ที่ดีของ block ก่อน
- **BoostResNet** (`../ref/boostresnet.md`): โต hierarchy ด้วย boosting (greedy optimal ในแง่ loss)

### ผลที่ได้

- Deep Belief Nets (2006): breakthrough ครั้งแรกที่ deep network เทรนได้จริง ก่อน GPU computing
- แสดงว่า unsupervised pre-training + supervised fine-tuning เป็น paradigm ที่ powerful
- ปัจจุบัน greedy layer-wise training กลับมาเป็น active area ผ่าน Forward-Forward, SCFF, PCGrad — เพราะมันเป็น on-chip, local, และไม่ต้องการ global backprop

### สำหรับเรา

นี่คือ *วิธี* สร้างลำดับชั้นของคุณ — และคุณก็ใช้มันอยู่แล้ว (SCFF เป็น greedy-layerwise; blocks เชื่อมกันด้วย boosting)

บทเรียนที่ชัดเจนสำหรับเฟส 2: **โตลำดับชั้นการคิดทีละระดับ แต่ละระดับเทรนแบบ local/online** แทนที่จะออกแบบ hierarchy ทั้งหอคอยแล้วเทรนทีเดียว

ยิ่งไปกว่านั้น: greedy training หมายความว่าคุณสามารถ **test แต่ละระดับได้ก่อนที่จะเพิ่มระดับถัดไป** ซึ่งตรงกับวินัย "ง่ายก่อน แล้วค่อยปีน" ของคุณ experiment ladder ใน `ideas1.md` (1.0 SCFF → 1.1 GD → 2.x mix → 3.x sleep → 4.x block chain) คือ greedy layer-wise growth ในเชิงวิจัย

---

## รูปร่างของคำตอบ (ไฟล์นี้)

ลำดับชั้นสำหรับเรา *เป็นมากกว่ากองซ้อน* ความสมบูรณ์ที่ draft-5 ขาด:

1. **วงลูปสองทิศ:** prediction ไหล **ลง** (top-down), error ไหล **ขึ้น** (bottom-up), ทุกระดับ **settle** ก่อน output — Predictive Coding; error เป็น sparse analog operation native กับ substrate

2. **ไดนามิกและอิงฉันทมติ:** parse tree ผุดขึ้นเป็น "เกาะของการเห็นพ้อง" สด ๆ ต่อ input (GLOM, Thousand-Brains) ไม่ใช่พีระมิดตายตัว; lateral coupling ใน analog substrate = consensus mechanism ฟรี

3. **ทุกระดับรัน algorithm เดียวกัน บน sparse code มีเวลาฝัง:** (HTM: SP + TM ซ้ำในทุก level) — SP ≈ SCFF, TM = temporal prediction loop ที่เฟส 2 ต้องการ

4. **กว้างและส่วนใหญ่หลับ ด้วย sparse routing:** (MoE/RIMs) แต่ละ input จุดเส้นทางเล็ก ๆ; blocks เป็น experts ที่ specialize เอง

5. **โตแบบ greedy ทีละระดับ local:** (Forward-Forward / boosting) — คุณทำอยู่แล้ว; เฟส 2 ก็ทำแบบเดียวกัน

โครงร่าง draft-5 ถูกต้อง; สิ่งที่ขาดคือ **วงลูปทำนาย top-down, การเห็นพ้องแบบไดนามิก, และมิติเวลา**
