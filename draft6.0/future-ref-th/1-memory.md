# 1 — hippocampus / คลังความจำระยะยาว

> คำถามของคุณ: *"hippocampus ควรหน้าตาเป็นยังไง?"* คำตอบของวงการตลอดสี่สิบปี: เป็นหน่วยความจำที่ **เร็ว, sparse, เชื่อมโยง (associative), ระบุด้วยเนื้อหา (content-addressable)** และเก็บไว้ *แยก* จากตัวคำนวณที่ช้า — และคุณก็เริ่มสร้างมันไปแล้ว (กลไก sleep + คลัง prototype แบบ LUT) ไฟล์นี้คือเมนูว่าคนอื่นเขาสร้างมันกันยังไง และทำไมแต่ละแบบถึงทำงานได้

---

## Complementary Learning Systems (CLS) — ทฤษฎีที่บอกว่า "มีสองความจำ โดยตั้งใจ"

*McClelland, McNaughton & O'Reilly, 1995; ปรับปรุงโดย Kumaran, Hassabis & McClelland, 2016 ([Trends in Cognitive Sciences](https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(16)30043-2)).*

### ปัญหาที่มันแก้

ปี 1985 มีเหตุการณ์แปลกประหลาดในสัตว์ทดลอง: สอน neural network ให้จำข้อเท็จจริงใหม่ พอจบ weight ที่เรียนรู้ข้อเท็จจริงเก่าก็ถูกทับทิ้งราบ ปรากฏการณ์นี้เรียกว่า **catastrophic forgetting** และ McClelland กับทีมถามคำถามที่ง่ายมาก: *สมองจัดการเรื่องนี้ยังไง? ทำไมคนเราถึงเรียนรู้ภาษาใหม่แล้วไม่ลืมชื่อแม่ตัวเอง?*

คำตอบที่พวกเขาพบมันหักหลายสัญชาตญาณ

### กลไกจริงๆ

คำตอบไม่ใช่ "แค่เรียนได้ดีกว่า" แต่คือสมองมี **ระบบเรียนรู้สองระบบที่ออกแบบให้ทำงานตรงข้ามกันโดยตั้งใจ**:

ระบบแรกคือ **hippocampus** ทำงานแบบ sparse มากๆ — ในทางชีววิทยา dentate gyrus (ส่วนหนึ่งของ hippocampus) มีเซลล์ประสาทที่ยิงพร้อมกันแค่ประมาณ **2% ต่อแพตเทิร์น** เทียบกับ neocortex ที่ 50% เพราะความ sparse นี้ แพตเทิร์นแต่ละอันจึงใช้ "ที่จอดรถ" คนละชุดเกือบทั้งหมด ความจำใหม่ไม่ไปชนความจำเก่า กระบวนการนี้เรียกว่า **pattern separation** และมันเป็นหัวใจของความสามารถในการจำแต่ละเหตุการณ์แยกจากกัน

ระบบที่สองคือ **neocortex** ทำงานตรงข้ามกันทุกอย่าง — ซ้อนทับกัน (overlapping), กระจาย (distributed), ช้า neocortex ไม่ได้เก็บเหตุการณ์แต่ละอัน แต่ค่อยๆ ถักรูปแบบทั่วไปจากหลายเหตุการณ์เข้าด้วยกัน นั่นคือที่มาของ "ความเข้าใจ" และ "การ generalize"

แล้วทั้งสองคุยกันยังไง? ผ่าน **sleep replay** ระหว่างหลับ hippocampus เล่นซ้ำเหตุการณ์ที่เกิดในวันนั้นด้วยความเร็ว **เร็วกว่าจริง 10–20 เท่า** (ในรูปแบบของ sharp-wave ripples) สลับกับ "เหตุการณ์เก่า" ที่ neocortex เคยรู้อยู่แล้ว neocortex ได้รับมิกซ์ของเก่าและใหม่ตลอดคืน จึงค่อยๆ integrate ความรู้ใหม่เข้าไปโดยไม่ลบของเก่า

### ผลที่น่าตื่นเต้น

เมื่อทีมของ McClelland ทำ simulation ของ CLS พวกเขาพบว่า:
- ถ้าบังคับให้เรียนรู้เร็วผ่านช่องทางเดียว → catastrophic forgetting เสมอ  
- ถ้าแยกระบบและใช้ sleep replay → สามารถเรียนรู้เหตุการณ์ใหม่ทีละอันได้โดยไม่ทำลายรูปแบบทั่วไป
- ผู้ป่วยที่ hippocampus เสียหาย (เช่น H.M.) ไม่สามารถสร้างความจำใหม่ได้เลย แต่ความรู้เก่ายังอยู่ครบ — ยืนยันว่า hippocampus คือ "ประตูรับ" ไม่ใช่ "ห้องเก็บ"

### สำหรับเรา

CLS คือ **ใบอนุญาตทางทฤษฎีที่แข็งแกร่งที่สุดสำหรับสถาปัตยกรรมที่คุณสร้างไปแล้ว** แผนผังตรงเป๊ะ:

- **SCFF/GD stack = neocortex** (ช้า overlapping เรียนรูปแบบทั่วไป)
- **LUT prototype store = hippocampus** (เร็ว sparse pattern-separated)
- **Sleep cycle = ช่องทาง replay** (ส่ง prototype จาก LUT กลับไป replay ผ่าน SCFF)

สิ่งที่เฟส 2 จะเพิ่มจาก CLS คือ: hippocampus ไม่ควรถูกใช้แค่ตอน "หลับ" แต่ควรถูก query **ระหว่างที่กำลังคิด** ด้วย เหมือนกับที่คุณหยิบ "ประสบการณ์ที่คล้ายกัน" ขึ้นมาแว่บในหัวระหว่างแก้โจทย์ เส้นด้ายนี้ลากไปยัง NTM ด้านล่าง

ในเชิงปฏิบัติสำหรับชิป: การ replay ไม่ต้องเล่นซ้ำ pixel จริงๆ — เล่นซ้ำ **feature vector ใน SCFF space** ก็พอ ซึ่งเล็กกว่ามากและอยู่ใน analog register อยู่แล้ว สิ่งที่ต้องออกแบบคือตารางเวลาของ sleep cycle กี่ก้าวถึง replay ครั้งหนึ่ง กี่ prototype ต่อรอบ และอัตราส่วน เก่า:ใหม่ ที่ 50:50 ตาม CLS แนะนำ

---

## Neural Turing Machine (NTM) — ตาข่ายที่มี RAM

*Graves, Wayne & Danihelka, 2014 ([arXiv 1410.5401](https://arxiv.org/pdf/1410.5401)).*

### ปัญหาที่มันแก้

ปี 2014 LSTM เพิ่งพิสูจน์ตัวเองในหลายงาน แต่มีสิ่งหนึ่งที่ทำไม่ได้เลย: **อัลกอริทึม** ลองสอน LSTM ให้ copy sequence ยาว 50 ตัว มันทำได้ถ้า train กับ sequence ยาวแค่นั้น แต่ถ้าเจอ sequence ยาว 100 ตัวตอน test มันพังทันที เพราะ LSTM ไม่มีที่ "วาง" ตัวแปรไว้ระหว่างประมวลผล มันแค่กดมันเข้าไปใน hidden state ที่มีขนาดตายตัว Graves เลยถามว่า: *ถ้าให้ตาข่ายมี RAM ภายนอกล่ะ?*

### กลไกจริงๆ

NTM แยกออกเป็นสองส่วนชัดเจน: **ตัวควบคุม (controller)** และ **เมทริกซ์หน่วยความจำ (memory matrix) M** ขนาด N×W (N แถว, W คอลัมน์)

ตัวควบคุมเป็น LSTM หรือ MLP ธรรมดา แต่แทนที่จะอ่านแค่ input มันยังอ่านจาก M ด้วย ผ่าน **หัวอ่าน (read head)** ซึ่งทำงานอย่างนี้:

1. ตัวควบคุมปล่อย **key vector k** และ **strength β** ออกมา
2. หัวอ่านคำนวณ **cosine similarity** ระหว่าง k กับทุกแถวของ M: score\_i = cosine(k, M[i]) × β
3. ผ่าน softmax → attention weight w\_i สำหรับแต่ละแถว
4. อ่านออกมาเป็น r = Σ\_i w\_i × M[i]

นั่นคือ "content-based addressing" และมันเป็น **การดึงคืนแบบเชื่อมโยง** ผ่านความคล้าย แต่ยังมีอีกโหมด: **location-based addressing** ที่ shift attention ไปตำแหน่งถัดไปแบบ circular — ใช้สำหรับการวนซ้ำและการเข้าถึงแบบ sequential สองโหมดนี้ถูก interpolate ด้วยกัน ทำให้ NTM เล่น patterns ทั้งแบบ "จำโดยเนื้อหา" และ "เดินตามลำดับ" พร้อมกัน

ฝั่งเขียน (write head) ทำงานคล้ายกัน แต่เขียนด้วยสองขั้น: **erase** (ลบเนื้อหาเก่าตามน้ำหนัก attention) แล้ว **add** (เพิ่มเนื้อหาใหม่ตามน้ำหนักเดิม) เพราะทุกอย่าง differentiable ทั้งหมดจึง backprop ได้

### ผลที่น่าตื่นเต้น

NTM เรียน **copy task** (รับ sequence ยาว N แล้ว output ซ้ำ) ได้สมบูรณ์แม้ test กับ sequence ที่ยาวกว่า training ซึ่ง LSTM ทำไม่ได้ มันเรียน **sort task** (เรียงตัวเลขให้น้อย-มาก) และ **associative recall** (จำคู่สัมพันธ์แล้วตอบ "X คู่กับอะไร?") ด้วย การทดลองพิสูจน์ว่าตาข่ายที่มีหน่วยความจำภายนอก **เรียนอัลกอริทึมได้ทั่วไปกว่า** ไม่ใช่แค่ pattern จากข้อมูล

### สำหรับเรา

NTM คือ **แผนผังที่สะอาดที่สุดของวงลูปเฟส 2** อ่านมันแล้วแปลทันที:

- **Controller = prefrontal cortex module** (ทำหน้าที่ตัดสินใจว่าจะ query อะไร)
- **Memory matrix M = hippocampus LUT crossbar** (เมทริกซ์ที่เก็บ prototype)
- **Read head = attention ในการเรียกคืน** (key → cosine similarity → weighted read)
- **Write head = การบันทึกประสบการณ์ใหม่** (มีการเลือกว่าเขียนที่แถวไหน)

ที่น่าสนใจกว่าคือ **ความแตกต่างระหว่าง content-based และ location-based addressing** — บน substrate ของคุณ content-based คือ analog dot-product (ทำโดย crossbar ได้ทันที) ส่วน location-based คือตัวนับ pointer แบบ digital ง่ายๆ และคุณต้องการทั้งคู่: "จำประสบการณ์ที่คล้ายที่สุด" ต้องการ content-based ส่วน "เล่นซ้ำลำดับเหตุการณ์ตามลำดับเวลา" ต้องการ location-based NTM บอกว่าให้ interpolate ทั้งสอง — เป็น design decision ที่ต้องทดสอบในเฟส 2

---

## Differentiable Neural Computer (DNC) — NTM ที่โตเต็มวัย

*Graves et al., 2016, Nature 538:471–476 ([DeepMind](https://github.com/google-deepmind/dnc)).*

### ปัญหาที่มันแก้

NTM มีข้อจำกัดสำคัญ: มันไม่มี "ระบบปฏิบัติการ" ของตัวเอง ถ้าเขียนทับแถวที่ยังใช้อยู่ ข้อมูลก็หาย ถ้าไม่มีการติดตามว่าเขียนอะไรเมื่อกี้ ก็ replay ตามลำดับไม่ได้ DNC แก้ทั้งสองอย่างนี้ เป็น NTM ที่มี memory management จริงๆ

### กลไกจริงๆ

DNC เพิ่ม **สามกลไก** ที่ NTM ขาด:

**กลไกแรก — การจัดสรร (Allocation):** มี **usage vector u** ขนาด N ติดตามว่าแต่ละแถวของ memory ถูกใช้มากแค่ไหน เมื่อจะเขียนของใหม่ ระบบเลือกแถวที่มี usage ต่ำสุด (เหมือน malloc) เมื่อ read แถวแล้วตัดสินใจว่า "ไม่ต้องการแล้ว" สามารถ free มันได้ (เหมือน free) นี่คือระบบ garbage collection สำหรับความจำ

**กลไกที่สอง — Temporal Link Matrix (L):** เมทริกซ์ N×N ที่ติดตามว่า "เขียนแถว j ก่อนแถว i ใช่ไหม?" — L[i,j] ≈ 1 ถ้า j เขียนทันทีก่อน i การ update คือ L ≈ prev\_usage ⊗ write\_weight (อธิบายด้วย outer product) ผลคือ DNC รู้ว่าความจำถูกเขียนในลำดับไหน และสามารถ **อ่านไปข้างหน้า** (forward read: ติดตาม L จากแถวปัจจุบัน) หรือ **อ่านย้อนหลัง** (backward read: ติดตาม L^T) เหมือนมี linked-list ใน memory

**กลไกที่สาม — การอ่านหลายหัว:** DNC มี read head หลายตัวพร้อมกัน แต่ละหัวเลือกระหว่าง 3 mode — content (cosine sim), forward (follow temporal link), backward (reverse temporal link) — ด้วยการ interpolate ทั้งสาม controller เรียนรู้เองว่าแต่ละสถานการณ์ควร query แบบไหน

### ผลที่น่าตื่นเต้น

DNC แก้ปัญหา **shortest-path บนรถไฟใต้ดินลอนดอน** — รับ query "จากสถานี X ไป Y" แล้วตอบเส้นทางสั้นสุด โดยเรียนจากตัวอย่างเท่านั้น ไม่มีอัลกอริทึม BFS ฝังเข้าไป มันยัง **อนุมานแผนผังเครือญาติ** — "Mary แม่ของ John, John พี่ของ Sue ดังนั้น Mary เป็นอะไรกับ Sue?" ได้ สิ่งเหล่านี้ต้องการ working memory ข้ามหลายก้าว NTM ทำไม่ได้ DNC ทำได้เพราะมัน track ว่าข้อมูลถูกเขียนเมื่อไหร่และในลำดับอะไร

### สำหรับเรา

DNC คือ **spec sheet ของ hippocampus ที่โตเต็มวัย** แปลกลไกสู่ substrate:

**Allocation → LUT memory management:** ระบบ LUT ของคุณต้องการวิธีตัดสินว่าจะเขียน prototype ใหม่ที่ slot ไหน และ slot ไหนสามารถ overwrite ได้ usage vector เป็น scalar register หนึ่งตัวต่อ slot ซึ่งถูกกว่า NTM มาก (สามารถ implement ด้วย leaky counter analog)

**Temporal link → "ประสบการณ์อะไรมาก่อนอะไร":** เฟส 2 เป็น time-series คุณจะต้องการไม่แค่ "ดึง prototype ที่คล้าย" แต่ "ดึง *สิ่งที่ตามมาหลังจากนั้น*" นี่คือที่ temporal link มีประโยชน์ ในแบบ sparse ที่สุด: เก็บ pointer "next" ต่อ slot ก็พอ (linked list) ไม่ต้องเป็น full N×N matrix

**สิ่งที่คุณยังไม่ต้องการตอนนี้แต่ควรรู้ไว้:** full L matrix ขนาด N×N หนักมาก สำหรับชิปให้ approximate ด้วย circular buffer หรือ sparse linked list — idea คือเดียวกัน implementation ถูกกว่ามาก

---

## Memory Networks — สล็อตที่ชัดเจน อ่านแบบหลายฮอป

*Weston, Chopra & Bordes, 2014; End-to-End Memory Networks, Sukhbaatar et al., 2015 ([arXiv 1503.08895](https://arxiv.org/abs/1503.08895)).*

### ปัญหาที่มันแก้

ถามว่า: "จอห์นไปห้องนั่งเล่น แมรี่ไปครัว จอห์นหยิบลูกฟุตบอล จอห์นไปสวน แมรี่ไปสวน ลูกฟุตบอลอยู่ที่ไหน?" ประโยคสุดท้ายต้องการ "trace" ย้อนกลับผ่านสามประโยค — ตาข่าย recurrent ธรรมดาจะพยายามยัดทุกอย่างเข้า hidden state และมันไม่ work เปเปอร์นี้บอกว่าเก็บประโยคแต่ละอันใน **memory slot แยกกัน** แล้วค่อย query

### กลไกจริงๆ

Memory Networks เก็บ **ข้อเท็จจริงแต่ละข้อ** เป็น memory vector m\_i (embed แต่ละประโยค) เวลา query ด้วยคำถาม q:

1. คำนวณ relevance: p\_i = softmax(q · m\_i) สำหรับทุก slot
2. อ่านออกมา: o = Σ\_i p\_i × m\_i
3. **อัปเดต query:** q\_new = q + o แล้ว **กลับไปทำซ้ำตั้งแต่ต้น**

วงลูป ดึง-ปรับ query-ดึงใหม่ นี่คือ **หลายฮอป** แต่ละฮอปคือการนำความรู้ที่ดึงออกมา "เพิ่มเข้า" กับคำถาม แล้วถามใหม่อีกรอบ ในตัวอย่าง "ลูกฟุตบอลอยู่ที่ไหน?" ฮอปแรกเจอ "จอห์นหยิบลูกฟุตบอล" ฮอปสองเจอ "จอห์นไปสวน" แล้วตอบ "สวน" — ต้องการสองฮอปถึงจะรู้คำตอบ

End-to-End Memory Networks (EM Networks) ทำให้ทุกอย่าง differentiable เทียมกัน: embedding matrices ต่างกันแต่ละฮอป, softmax ที่หาอนุพันธ์ได้, เทรนแบบ backprop ทั้งก้อน

### ผลที่น่าตื่นเต้น

บน **bAbI dataset** (20 ประเภทคำถาม-เหตุผล) Memory Networks ที่ใช้ 3 hop ผ่านได้ 95% ในขณะที่ LSTM ผ่านได้ 49% งานเรื่อง "ใครมีอะไร อยู่ที่ไหน ทำอะไรก่อน" ที่ต้องการ chain of reasoning ทำได้แน่นและสม่ำเสมอ

### สำหรับเรา

Memory Networks ให้กลไกที่เป็นรูปธรรมสำหรับ **การคิดแบบหลายรอบ** ที่คุณบรรยายไว้ในเฟส 2 — วงลูปที่คุณ query LUT หลายครั้ง แต่ละครั้งเพิ่มสิ่งที่เจอเข้าไปใน working memory แล้วถามใหม่ ถ้าวาด:

- **Working memory = q** (สิ่งที่ถูกถามหรือสิ่งที่กำลังคิดอยู่)
- **Memory slots = LUT rows** (prototype ที่เก็บไว้)
- **Hop = หนึ่งรอบของวงลูป settle** (query → retrieve → update → query again)
- **จำนวน hop = ความลึกของการคิด** ซึ่งเปเปอร์เรื่อง PonderNet ใน `3-recurrence.md` ทำให้เรียนรู้ได้

ข้อที่น่าสังเกต: multi-hop query ใน Memory Networks มีต้นทุนต่ำมากถ้า LUT อยู่ใน analog crossbar เพราะแต่ละ hop คือหนึ่ง MVM (matrix-vector multiply) บนวงจรเดิม ต่างจาก digital ที่ต้องรันโค้ดซ้ำ

---

## Modern Hopfield Networks — "การดึงคืน *คือ* attention"

*Ramsauer et al. (กลุ่ม Hochreiter), 2020, "Hopfield Networks is All You Need" ([arXiv 2008.02217](https://arxiv.org/abs/2008.02217)); ความจุจาก Demircigil et al. 2017.*

### ปัญหาที่มันแก้

Hopfield network แบบคลาสสิก (Hopfield, 1982) เป็นโมเดลที่สวยงามมาก: เก็บแพตเทิร์น {ξ¹, ξ², ..., ξⁿ} ลง weight matrix W = Σ ξᵏ(ξᵏ)ᵀ แล้ว retrieve ด้วยการ iterate x ← sign(Wx) จนนิ่ง มันเป็น **associative memory**: ใส่แพตเทิร์นที่เสียหายเข้าไป ได้แพตเทิร์นที่สมบูรณ์คืน แต่ปัญหาคือมันเก็บได้แค่ **~0.14N แพตเทิร์น** (N = จำนวนหน่วย) เกินนี้แพตเทิร์นต่างๆ รบกวนกัน และมันทำงานแค่กับ binary (±1) เท่านั้น เป็น toy ไม่ใช่ของจริง

### กลไกจริงๆ

Ramsauer และทีมเปลี่ยน energy function จาก:
- แบบคลาสสิก: `E = -0.5 * x^T W x` (quadratic)
- แบบใหม่: `E = -logsumexp(β * Ξ^T x) + 0.5 * x^T x + constant`

โดย Ξ คือ matrix ของ stored patterns (แต่ละคอลัมน์คือหนึ่งแพตเทิร์น) และ β คือ inverse temperature

การ retrieve คือการลด E โดย gradient descent บน x:
```
x_new = Ξ · softmax(β · Ξ^T · x)
```

และนี่คือ **discovery** ที่ทำให้เปเปอร์นี้ดังมาก: สูตร update นี้ **เหมือนกันทุกอย่างกับ attention mechanism ใน transformer เลย**:
- x คือ query
- Ξ^T x คือ raw attention scores
- softmax(β · Ξ^T x) คือ attention weights
- Ξ · softmax(...) คือ weighted sum ของ values

**Attention IS associative memory retrieval.** มันไม่ใช่เปรียบเปรย แต่เป็นทางคณิตศาสตร์เดียวกันแท้ๆ

ความจุของ Modern Hopfield พุ่งขึ้นเป็น **เลขชี้กำลัง** (~exp(N/2)) เทียบกับ linear ของแบบคลาสสิก เพราะ energy function ใหม่สร้าง "หลุม" ที่ลึกและชันกว่า ทำให้แพตเทิร์นแต่ละอันอยู่ในพื้นที่ของตัวเองได้โดยไม่กวนกัน และ retrieve ได้ใน **ก้าวเดียว** (ต่างจากคลาสสิกที่อาจต้องหลายก้าว)

### ผลที่น่าตื่นเต้น

ทีมพิสูจน์ว่า:
- Transformer attention layer = Modern Hopfield retrieval step ทางคณิตศาสตร์
- Hopfield Layer (ใช้ Modern Hopfield แทน attention) ให้ผลแทบเท่ากันใน BERT, immune repertoire tasks
- ที่ β สูง (ต่ำ): เลือก pattern ที่ใกล้สุดอย่างชัดเจน vs เฉลี่ย patterns หลายอัน
- สามารถ retrieve patterns ที่ไม่เคยเห็นในชุดเก็บได้ ถ้าอยู่ระหว่าง patterns สองอัน (interpolation)

### สำหรับเรา

นี่คือรายการสำคัญที่สุดในไฟล์นี้สำหรับฮาร์ดแวร์ของคุณ เพราะมันบอกว่า:

**LUT crossbar ของคุณคำนวณปฏิบัติการแกนกลางของ associative memory retrieval อยู่แล้ว** — crossbar ทำ matrix-vector multiply (Ξ^T · x) ซึ่งเป็นก้าวเดียวในสูตรข้างบน ตามด้วย softmax (ซึ่งทำด้วย analog WTA circuit ได้) ตามด้วย Ξ · weights (อีก MVM)

คุณไม่ต้องเลือกระหว่าง:
- "หน่วยความจำแบบ Hopfield"  
- "เลเยอร์ attention"  
- "LUT แบบ content-addressable"

เพราะ **สามอันนี้คือสิ่งเดียวกัน** มองคนละด้าน

และยังมีนัยสำคัญสำหรับ **β**: ถ้า β ต่ำ → ดึงคืนแบบเฉลี่ยหลาย prototype (เหมาะกับการ generalize); ถ้า β สูง → ดึงคืน prototype เดี่ยวชัดเจน (เหมาะกับ recall ที่แม่นยำ) บน analog substrate β คือ scale ของสัญญาณก่อน WTA — adjust ได้ด้วย bias voltage เดียว ซึ่งหมายความว่าคุณ tune "ความชัดเจนของความจำ" แบบ runtime ได้โดยไม่ต้องเปลี่ยน weight

---

## โมเดลเสริมการดึงคืน (kNN-LM, RETRO) — ความจำที่ไม่ต้องเทรนเข้าไปใน weight

*kNN-LM: Khandelwal et al., 2019 ([arXiv 1911.00172](https://arxiv.org/pdf/1911.00172)); RETRO: Borgeaud et al., 2021 ([arXiv 2112.04426](https://proceedings.mlr.press/v162/borgeaud22a/borgeaud22a.pdf)).*

### ปัญหาที่มันแก้

ปัญหาของ LLM แบบดั้งเดิม: ข้อเท็จจริงทุกอย่างถูกยัดเข้าไปใน weight ซึ่งหมายความว่าถ้าอยากเพิ่มความรู้ใหม่ต้องเทรนใหม่ทั้งหมด มันช้า แพง และทำลายของเก่า คำถาม: "ถ้าแยกความรู้ออกจาก reasoning ล่ะ?"

### กลไกจริงๆ

**kNN-LM** ทำงานสองขั้น:

ขั้น build (offline): รันโมเดลภาษาผ่านข้อมูล training ทั้งหมด สำหรับแต่ละตำแหน่ง t เก็บคู่ (context\_embedding\_t, next\_token\_t) ลงใน **datastore** ขนาดยักษ์ (อาจหลาย billion entries) ใช้ FAISS สร้าง approximate nearest neighbor index

ขั้น inference: เมื่อรับ context ใหม่ คำนวณ embedding ของมัน → ค้นหา k nearest neighbors ใน datastore → คำนวณ distribution ของ next token จาก neighbors (softmax over distances) → **interpolate** กับ distribution จากโมเดลหลัก:

```
p_final(w|c) = λ · p_kNN(w|c) + (1-λ) · p_LM(w|c)
```

λ ≈ 0.25–0.65 ขึ้นกับ domain ผล: perplexity ลดลงอย่างมีนัยสำคัญ **โดยไม่เทรนอะไรเพิ่มเลย**

**RETRO** ทำคล้ายกันแต่ scale ขึ้นถึงระดับ trillion tokens และ integrate เข้ากับ transformer architecture โดยตรงผ่าน **chunked cross-attention**: หั่นอินพุตเป็น chunks ขนาด 64 token แต่ละ chunk ดึง k=2 เพื่อนบ้านจาก datastore ท้าย Transformer blocks มี cross-attention layers ที่ attend ไปยัง retrieved chunks เหล่านี้

ผล: RETRO 7B parameters ทำได้ดีกว่า GPT-3 175B บน language modeling benchmarks — เพราะ "เปิดดูหนังสือ" แทนที่จะ "จำทุกอย่าง"

### สำหรับเรา

บทเรียนหลักที่เกี่ยวกับ substrate คุณ:

**"ความรู้" ≠ "weight ที่เทรนแล้ว"** นี่คือการ reframe ที่ทรงพลัง: ชิปของคุณมี Scap เป็น weight ช้า แต่ถ้า "ความรู้ factual" (เช่น prototype ของ class ต่างๆ) อยู่ใน LUT crossbar แทน น้ำหนักฝั่ง SCFF ไม่จำเป็นต้องเก็บมัน → น้ำหนักฝั่ง SCFF โฟกัสที่ feature extraction และ reasoning แทน

ความหมายในเชิง practical: เมื่อเจอข้อมูลของ "คลาสใหม่" คุณไม่ต้องเทรน SCFF stack ใหม่ แค่ **เพิ่ม entry ลง LUT** (fast write, O(1)) แล้ว inference ใช้ kNN retrieval เทียบกับ entry ใหม่ได้ทันที นี่คือ **few-shot capability แบบไม่ต้องเทรน** ที่ตรงตามเป้าหมาย lifelong learning ของเฟส 2

ข้อควรระวัง: การดึงคืนให้ *ความรู้* ไม่ใช่ *การให้เหตุผล* — "เจอ prototype ที่คล้าย" ≠ "เข้าใจโครงสร้างของมัน" วงลูปการคิดใน prefrontal ยังต้องอยู่

---

## Fast Weights — สเกลเวลาที่สาม ที่เร็วกว่า

*Ba, Hinton, Mnih, Leibo & Ionescu, 2016 ("Using Fast Weights to Attend to the Recent Past", [arXiv 1610.06258](https://arxiv.org/abs/1610.06258)).*

### ปัญหาที่มันแก้

ในสมองมีสเกลเวลาสามระดับ: **activation** (หน่วยมิลลิวินาที ใน hidden state), **working memory** (หน่วยวินาที ความจำระยะสั้น), **long-term memory** (หน่วยชั่วโมง-ปี ใน weight เปลี่ยนช้ามาก) แต่ neural network มีแค่สองอย่างแรก: hidden state + slow weights ไม่มีอะไรที่อยู่ระหว่างสองอย่างนั้น Ba และทีมถามว่า: "ถ้าเพิ่ม weight ที่เร็วกว่า slow weights แต่ช้ากว่า activation ล่ะ?"

### กลไกจริงๆ

Fast weights เป็น matrix A(t) ที่อัปเดตตาม **Hebbian rule พร้อม decay**:

```
A(t) = λ · A(t-1) + η · h(t) · h(t)^T
```

โดย λ ≈ 0.95 (fast decay), η เป็น learning rate เล็กๆ และ h(t) คือ hidden state ตอนนั้น ผลคือ A จำ "อะไรที่เกิดขึ้นไม่กี่ก้าวที่แล้ว" อยู่ในรูปของ pattern ที่มี inner product สูงกับสิ่งที่เกิดขึ้นล่าสุด

การ read จาก fast weights ทำผ่าน inner loop — iterate หลายรอบ:
```
h_new = LayerNorm(W_slow · x + A · h)
h ← h_new (ทำซ้ำ S ครั้ง)
```

การ iterate นี้ทำให้ตาข่าย "ค้นหา" ว่า fast weights เก็บอะไรที่เกี่ยวข้องกับ input ปัจจุบัน

### ผลที่น่าตื่นเต้น

Fast weights ช่วยงาน **associative retrieval ระยะสั้น** ได้ดีขึ้นมาก: "ถ้าเมื่อกี้เห็น A แล้วเห็น B ตอนนี้เห็น A อีกครั้ง B ตามมาไหม?" — slow LSTM ทำได้แย่, fast weights ทำได้ดีกว่ามาก เพราะ A เก็บคู่ (A→B) ไว้ในรูปของ outer product

### สำหรับเรา

นี่คือไอเดียที่ตรงกับ physics ของ substrate คุณที่สุด:

**คาปาซิเตอร์ที่รั่วเร็ว (short RC constant) คือ fast weight** — ถ้าคุณมี Scap สองชุดต่อ synapse: ชุดช้า (RC ยาว หน่วยวินาที = slow weight ที่เรียนรู้ด้วย SCFF/GD) และชุดเร็ว (RC สั้น หน่วย 10-100ms = fast weight ที่ update แบบ Hebbian ทันทีและ decay เร็ว) คุณได้สามสเกลเวลาบน physics เดิม ไม่ต้องเพิ่มวงจรใหม่ แค่เพิ่ม cap ที่ขนาดต่างกัน

**Working memory อาจไม่ต้องใช้ LUT เลยสำหรับอดีต *อันใกล้*** — fast Scap ถือมันไว้ได้โดยอัตโนมัติ LUT จึงไว้ใช้กับ "ประสบการณ์เก่าที่ต้องการเก็บระยะยาว" เท่านั้น การแยกสเกลเวลาแบบนี้ตรงกับ CLS เป๊ะๆ และลด pressure บน LUT ด้วย

---

## รูปร่างของคำตอบ (ไฟล์นี้)

hippocampus สำหรับเราคือ: **คลังความจำเชื่อมโยงแบบ content-addressable (= LUT crossbar = modern Hopfield = attention) เก็บแยกจากตัวคำนวณที่ช้า มีการจัดสรร/รีไซเคิลและ temporal link เขียนได้เร็วและถูก อ่านด้วยความคล้ายระหว่างคิด และ replay ระหว่างหลับ**

- **CLS** บอก *ว่าทำไม* มันต้องแยกและเร็ว (pattern separation + replay)
- **NTM/DNC** บอก *วิธี* เดินสายเชื่อมมันเข้ากับตัวควบคุม (controller-memory interface + memory management)
- **Modern Hopfield** บอกว่า *มันคือปฏิบัติการที่ crossbar ของคุณทำอยู่แล้ว* (attention = retrieval)
- **Memory Networks** บอกว่า *การคิดหลายรอบ = query หลายฮอป* ซึ่งถูกบนชิปแอนะล็อก
- **kNN-LM/RETRO** บอกว่า *เก็บความรู้ไว้ใน LUT ไม่ใช่ใน weight* (fast write, zero training)
- **Fast weights** บอกว่า *อดีตอันใกล้อยู่ใน leaky Scap แทนได้* (สามสเกลเวลาบน physics เดิม)
