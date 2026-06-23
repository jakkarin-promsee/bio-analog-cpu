# 13 — การเรียนรู้ *คือ* การบีบอัด (และสมมติฐาน "spare-capacity" ของคุณมีจริง)

> วิทยานิพนธ์หลักของคุณ: **การบีบอัดในชิป** ที่ทำให้การคำนวณแบบ resident-weight เป็นไปได้ — และสัญชาตญาณของคุณว่า *แต่ละนิวรอนมี task-cap ที่มันไม่ได้ใช้เต็ม และ slack ที่เหลือแชร์กันได้* ไฟล์นี้คือฝั่งทฤษฎี และพาดหัวคือการรวมความคิดที่ลึกที่สุดในแฟ้มทั้งหมด: **การเรียนรู้ไม่ได้ *ถูกช่วย* ด้วยการบีบอัด — การเรียนรู้ *คือ* การบีบอัด** ซึ่งแปลว่า "ทำให้ลงในชิป" กับ "ทำให้เรียนรู้ได้ดี" คือ **ปัญหาเดียวกัน** ไม่ใช่สอง และสมมติฐาน spare-capacity ของคุณมีสามชื่อในวรรณกรรม ทุกชื่อยืนยันมัน

---

## กรอบคิด: โมเดลที่ generalize ได้คือโมเดลที่บีบอัดข้อมูลได้

*Minimum Description Length: Rissanen, 1978; สำหรับ neural net: Hinton & van Camp, 1993 ([paper](https://www.cs.toronto.edu/~hinton/absps/colt93.pdf)); Kolmogorov complexity; compression-progress ของ Schmidhuber (`4-signal.md`).*

### ปัญหาที่มันแก้

มีคำถามที่รบกวนสถิติและ ML มาตั้งแต่ต้น: โมเดลบางตัว fit training data ได้ดีแต่ test ได้แย่ ขณะที่อีกตัวหนึ่ง fit training ได้พอๆ กันแต่ test ได้ดีกว่า ความแตกต่างนี้คืออะไร? คำตอบเดิมคือ "ใส่ regularization เข้าไป" — แต่นั่นเป็นคำตอบแบบ "ทำแล้วมันดีขึ้น" ไม่ใช่ "เข้าใจว่าทำไม" Rissanen และ Hinton เดินเข้ามาจากทิศทางของทฤษฎีสารสนเทศ และถามคำถามที่ลึกกว่า: *มันแปลว่าอะไรที่โมเดลหนึ่ง "เข้าใจ" ข้อมูลมากกว่าอีกโมเดล?*

### กลไกจริงๆ

**MDL (Minimum Description Length)** ตอบคำถามนี้ด้วยหลักการเดียว: **โมเดลที่ดีที่สุดคือตัวที่ทำให้ความยาวคำอธิบายรวมสั้นที่สุด**

```
ความยาวคำอธิบายรวม = บิตที่ใช้อธิบายโมเดล + บิตที่ใช้อธิบายข้อมูลเมื่อรู้โมเดลแล้ว
```

เอาเป็นรูปธรรม: สมมติคุณมีชุดข้อมูล n จุด และต้องการส่งให้เพื่อน คุณมีสองทาง:

- **ท่องจำ:** เขียนทุกจุดตรงๆ ใช้ ~n บิต ทำได้เสมอแต่ไม่บีบอัด
- **โมเดล:** ส่ง "สมการที่ generate ข้อมูลนี้" แล้วส่งเฉพาะ error (ส่วนที่โมเดลพลาด) ถ้าโมเดลดี error เล็ก → บิตรวมน้อยกว่า n มาก

โมเดลที่ "จับโครงสร้างจริง" ของข้อมูลได้ → residual error เล็ก → บิตรวมน้อย
โมเดลที่ "ท่องจำ noise" → residual error ใหญ่ (noise อธิบายด้วยโมเดลไม่ได้) → บิตรวมมากกว่า

ผลทางทฤษฎีที่ทรงพลัง: **regularization ทุกรูปแบบ (L2, L1, dropout, weight decay, noise injection) คือการ implement MDL ในมุมหนึ่งทั้งนั้น** — มันล้วนบังคับให้โมเดลอธิบายข้อมูลด้วย "บิตน้อยที่สุด" และ Occam's razor ที่นักวิทยาศาสตร์ใช้มาหลายร้อยปี ("เลือก hypothesis เรียบง่ายที่สุดที่อธิบายข้อมูลได้") ก็คือ MDL ในรูปแบบคำพูด

Hinton & van Camp แปล MDL สู่ neural net โดยทำให้ weight เป็น stochastic (มี distribution ไม่ใช่ค่าตายตัว) แล้วใช้ KL divergence เป็น "ต้นทุนในการส่ง weight" ผลที่พวกเขาพิสูจน์: **ตาข่ายที่ generalize ได้ดีก็ต่อเมื่อข้อมูลใน weight ของมันน้อยกว่าข้อมูลในเอาต์พุตที่มันอธิบายอยู่อย่างมีนัย** — weight ต้องเป็นคำอธิบายที่บีบอัดแล้วของ regularity ในข้อมูล ไม่ใช่สำเนาของข้อมูลทั้งหมด

### ผลที่น่าตื่นเต้น

เส้นเชื่อมนี้ทำให้อะไรๆ หลายอย่าง "เห็นเหตุผล" พร้อมกัน:
- ทำไม neural net ที่กว้างมากๆ ถึง generalize ได้ดีแม้ไม่ regularize → เพราะมันหา solution ที่บีบอัดได้โดยธรรมชาติ
- ทำไม early stopping ถึงช่วย → หยุดก่อน model เริ่ม overfit noise (เริ่ม "เพิ่มบิต" ไปกับ noise)
- ทำไม batch normalization ถึงช่วย → ทำให้ gradient ไหลผ่านส่วนที่บีบอัดข้อมูลได้จริง

### สำหรับเรา

นี่คือข้อตระหนักที่รวมความคิดที่คุณกำลังเอื้อมไปหา: คุณพูดว่า "เราต้องมีอัลกอริทึมบีบอัดเพื่อลงในชิป; ตอนนี้เราทำแค่ในซอฟต์แวร์" MDL บอกว่าคุณ **ไม่ต้องเอาอัลกอริทึมบีบอัดแยกมาแปะ** — คุณต้องมี *กฎการเรียนรู้ที่บีบอัดขณะที่มันเรียน* ตาข่ายที่เรียนรูปร่างจริง (ไม่ใช่ noise) *ก็เล็กพอ* จะเป็นรูปแบบที่บีบอัดแล้วอยู่ในตัว ดังนั้นข้อจำกัด resident-weight ของคุณ (ลงในชิป) กับเป้าหมายการเรียนรู้ของคุณ (หารูปร่างจริง) คือ **วัตถุประสงค์เดียว**: ทำให้ความยาวคำอธิบายของ weight น้อยที่สุด ทุกวิธีใน `14-compression-methods.md` คือวิธี *บังคับ* สิ่งนั้น; ไฟล์นี้คือ *เหตุผลว่าทำไม* มันเป็นไปได้

---

## สัญชาตญาณ double-descent ของคุณ มีฐานรองรับ — "noise หักล้างตัวเอง"

*Double descent: Belkin et al., 2019, PNAS ([arXiv 1812.11118](https://arxiv.org/abs/1812.11118)).*

### ปัญหาที่มันแก้

bias-variance tradeoff แบบคลาสสิก (สอนในทุก ML course) บอกว่า: โมเดลเล็กเกินไป → underfit; โมเดลใหญ่เกินไป → overfit; มี sweet spot อยู่กลางๆ แต่ deep learning ทำลาย narrative นี้อย่างสิ้นเชิง — neural network ที่มี parameter มากกว่า training sample หลายเท่า ยัง generalize ได้ดีอยู่ ซึ่ง "ควรจะ" overfit อย่างสุดขีดตามทฤษฎีเก่า Belkin และทีมถามว่า: *กราฟ test error vs model size หน้าตาเป็นยังไงจริงๆ ถ้าวัดครบทั้งสองฝั่งของ interpolation threshold?*

### กลไกจริงๆ

เมื่อ Belkin et al. วัดจริงๆ ข้ามหลาย model family (random features, polynomial regression, neural networks, decision trees) พวกเขาพบ **สามโซน** ไม่ใช่สองโซนตามทฤษฎีเก่า:

**โซน 1 — Underfitting (classical):** โมเดลเล็กเกินไป fit training ได้แย่ test ก็แย่ error สูงทั้งคู่

**โซน 2 — Interpolation threshold (วิกฤต):** โมเดลพอดีที่จะ fit training data ได้เป๊ะ (training error = 0) แต่ test error **พุ่งขึ้นสูงสุด** นี่คือจุดที่ทฤษฎีเก่าบอกว่าควรหยุดขยาย — overfitting แบบคลาสสิก เพราะโมเดลมีอิสระน้อยนิดสำหรับ noise แต่ละตัวจึงต้องถูก fit แบบ "spike" แหลมในพื้นที่ parameter

**โซน 3 — Over-parameterized descent:** เมื่อโมเดลใหญ่ขึ้นเกิน interpolation threshold ไปอีก test error **ลดลงอีกครั้ง** และในที่สุดต่ำกว่าค่า sweet spot ของทฤษฎีเก่า

**ทำไมโซน 3 ถึงเกิดขึ้น?** เมื่อโมเดลมี parameter มากเกินกว่าที่จำเป็นในการ fit training data จะมีอิสระในการ fit ได้ *หลายทาง* gradient descent ในบรรดาทุก solution ที่ fit training ได้เป๊ะ จะ "drift" ไปหา **minimum-norm solution** โดยธรรมชาติ (implicit regularization ของ gradient descent) solution ที่ norm ต่ำนี้เรียบ — มันไม่ fit noise เพราะ noise ต้องการ "spikes" ใน parameter space ซึ่ง norm สูง ดังนั้น noise จึงถูกเฉลี่ยออก ("หักล้างตัวเอง") ขณะที่ signal ที่เรียบสม่ำเสมอถูกเก็บไว้

ที่สำคัญ: ปรากฏการณ์นี้เกิดกับ **model complexity axis** (เพิ่มขนาดโมเดล) และกับ **training epochs axis** (เทรนนานขึ้น) ด้วย — epoch-wise double descent ก็มีจริง Nakkiran et al. (2019) ยืนยันบน ResNet และ transformer จริงๆ

### ผลที่น่าตื่นเต้น

Belkin et al. วัดบน random Fourier features, polynomial regression, two-layer neural network, และ decision trees ได้ผลเดิมทุกครั้ง: double descent เป็นปรากฏการณ์ทั่วไปไม่ใช่ artifact ของ architecture พิเศษ

ผลเพิ่มเติม: **epoch-wise double descent** — ถ้า model size อยู่ใกล้ interpolation threshold แล้วเทรนนานขึ้น test error จะพุ่งขึ้นก่อนแล้วลงอีกครั้ง นั่นคือทั้ง model axis และ time axis มี double descent เหมือนกัน

### สำหรับเรา

การพูดของคุณว่า *"noise หักล้างตัวเอง"* คือการอ่าน double descent ที่ถูกต้องเป๊ะ และมันสำคัญสำหรับชิปคุณเพราะมันบอกว่า **การใส่ capacity เกินนั้นปลอดภัยและถึงขั้นมีประโยชน์** — Scap เพิ่มไม่ทำให้ overfit ถ้ากฎการเรียนรู้ชอบ fit แบบบีบอัดได้ (norm ต่ำ/เรียบ) การ smoothing ตามธรรมชาติของ substrate แอนะล็อก (การอิ่มตัว, การรั่วของ Scap, noise ของ op-amp) *คือ* อคติ (bias) ที่ดันไปทาง minimum-norm solution โดยธรรมชาติ คุณไม่กลัว capacity เกิน; คุณใช้ประโยชน์จากมัน

และถ้าคุณเรียนใน over-parameterized regime แล้ว prune ตอน sleep (lottery ticket ด้านล่าง) คุณได้ประโยชน์ทั้งสองทาง — ความสามารถในการเรียนของโมเดลใหญ่ช่วง exploration + ความกระชับของโมเดลเล็กหลัง consolidation

---

## ทำไมการบีบอัดถึงเป็นไปได้: งานมัน *เล็กจิ๋ว*

*Intrinsic dimension: Li et al., ICLR 2018 ([arXiv 1804.08838](https://arxiv.org/abs/1804.08838)).*

### ปัญหาที่มันแก้

โมเดล ML ยุคใหม่มี parameter หลักล้านถึงหลักพันล้าน แต่มันจำเป็นทุกตัวจริงๆ ไหม? ถ้าไม่ — parameter ส่วนที่เกินนั้นทำหน้าที่อะไร? และถ้าเป็นอย่างนั้น ทำไมเราถึงต้องมีมันตั้งแต่แรก? Li et al. ถามคำถามที่ตรงๆ: *ถ้าเราบังคับให้โมเดลเรียนรู้ภายใน random subspace มิติต่ำ มิติต่ำสุดที่ยังได้ผลดีพอคือเท่าไหร่?*

### กลไกจริงๆ

การทดลองที่สะอาดมาก: สมมติโมเดลมี D parameter รวม (เช่น ResNet มี 11M) แทนที่จะให้ gradient อัปเดตทั้ง D มิติอิสระ ให้:

1. สุ่ม matrix P ขนาด D×d (d ≪ D) — matrix นี้ตายตัวตลอด training ไม่เรียนรู้ มันคือ random projection
2. เรียนแค่ **d parameter** (เรียกว่า θ_d) แล้ว project ขึ้น:
   `θ = θ_0 + P·θ_d`
   อัปเดตเฉพาะ θ_d ขนาด d ตัว ส่วน θ_0 (initial weights) และ P ตายตัว
3. ค่อยๆ เพิ่ม d จนหา **d₉₀** — มิติต่ำสุดที่ยังได้ 90% ของ accuracy เมื่อเทรนเต็ม D มิติ

d₉₀ นี้คือ **intrinsic dimension ของงาน** — วัดว่าปัญหาจริงมีกี่มิติอิสระ ไม่ใช่กี่ parameter

จุดสำคัญ: P สุ่มตายตัวหมายความว่าไม่ได้ค้นหา subspace ที่ดีที่สุด — เพียงแค่สุ่มก็ได้ผลดี นั่นบอกว่า subspace ที่มีประโยชน์ไม่ได้ซ่อนอยู่ในทิศทางพิเศษ มันกระจายอยู่เต็มไปหมด

### ผลที่น่าตื่นเต้น

ตัวเลขที่ได้น่าตกตะลึง:

| งาน | D (parameter จริง) | d₉₀ (intrinsic) | อัตราส่วน |
|---|---|---|---|
| MNIST classification | ~200K | **~750** | 0.4% |
| CIFAR-10 | ~200K | **~3,400** | 1.7% |
| ImageNet (ResNet-50) | ~25M | **≤ ~500K** | ~2% |

งานที่ดูต้องการ parameter เป็นล้านจริงๆ มี intrinsic dimension อยู่แค่หลักร้อยถึงหลักพัน parameter ที่เหลือส่วนใหญ่เป็น *พิกัดที่ซ้ำซ้อน* — มีหลาย combination ของ weight ที่ทำงานได้ดีพอๆ กัน เพราะปัญหาจริงนั่งอยู่ใน subspace เล็กๆ

เปเปอร์ระบุตรงๆ ว่าผลนี้ให้ **ขอบเขตบนของ MDL** และบีบอัดตาข่ายได้ **100 เท่าขึ้นไป** โดยหลักการ

### สำหรับเรา

นี่คือใบอนุญาต *ที่สุด* ของ resident-weight เหตุผลที่ทั้งโมเดลลงในชิปได้คือ **งานที่มันแก้เล็กกว่าจำนวนพารามิเตอร์ที่ดูเหมือนมากนัก** คุณกำลังเก็บของมิติต่ำในปริภูมิ substrate มิติสูง และความซ้ำซ้อนนั้นบีบอัดได้

งานคุณไม่ใช่การยัด weight อิสระเป็นล้านลงซิลิคอน มันคือการแทนของมิติ ~พัน ได้อย่างมีประสิทธิภาพ นั่นตีกรอบปัญหาวิศวกรรมทั้งหมดใหม่จาก "เก็บไม่ได้แน่ๆ" เป็น "หา subspace เล็กๆ ให้เจอ" ซึ่งคือสิ่งที่วิธี structured/low-rank/sparse (`14`) ทำ

และ P matrix ของ Li et al. ที่สุ่มตายตัว — นั่นคือ **reservoir / random projection** (`8-atom.md`) เป้าหมายในชิปคุณ: ฉายด้วย random matrix ตายตัว แล้วเรียนแค่ส่วน d₉₀ ที่สำคัญ วงจรถูก random matrix แพง

---

## สมมติฐานของคุณ มีชื่อแล้ว (1): spare capacity มีจริง — Lottery Ticket

*Frankle & Carlin, ICLR 2019 ([arXiv 1803.03635](https://arxiv.org/abs/1803.03635)).*

### ปัญหาที่มันแก้

ถ้า intrinsic dimension บอกว่าโมเดลเล็กพอแก้งานได้ ทำไมเราต้องเทรนโมเดลใหญ่ก่อน? ทำไมไม่เทรนโมเดลเล็กตั้งแต่แรก? — คำถามนี้ถูกถามมานาน คำตอบเดิมคือ "โมเดลเล็กที่เทรนจากศูนย์ converge ได้แย่กว่า" Frankle & Carlin สังเกตว่า: *ถ้ามี subnetwork เล็กๆ ที่เหมาะสมอยู่ใน network ใหญ่อยู่แล้ว ทำไมไม่หามันให้เจอ แล้วเทรนมันเดี่ยวๆ?*

### กลไกจริงๆ

**Iterative Magnitude Pruning (IMP)** — อัลกอริทึมที่แสดงว่า winning ticket มีอยู่จริง:

1. **Init:** สุ่ม weight ทั้งหมด → เรียก initial weights นี้ว่า **θ₀**
2. **Train:** เทรน network ปกติจนได้ θ_T (trained weights ที่ converge)
3. **Prune:** ลบ p% ของ weight ที่มี **|magnitude| ต่ำสุด** (แบบ global ทั้ง network ไม่ใช่ per-layer) สร้าง binary mask **m** (1 = เก็บ, 0 = ลบ)
4. **Reset:** ตั้ง weight ที่เหลือ (ตาม mask m) กลับไป **θ₀ เดิม** ← จุดสำคัญที่สุด ไม่ใช่ re-randomize ใหม่
5. **Repeat:** เทรน network ที่มี mask m จาก θ₀ เดิม → ทำซ้ำตั้งแต่ขั้น 3

ทำซ้ำหลายรอบ (iterative) บีบ network ลงได้มากกว่าการ prune ครั้งเดียว (one-shot pruning)

**ทำไม reset ไป θ₀ จึงสำคัญ?** ถ้าแค่เทรน network เล็กจากค่า random ใหม่ทั้งหมด มันก็แค่ "ตาข่ายเล็กสุ่ม" ซึ่งไม่ดี แต่ θ₀ ของ connection ที่ "ชนะ lottery" มี initialization ที่ทำให้ gradient ไหลได้ดีตั้งแต่แรก — นั่นคือ "ตั๋วที่ถูก" (winning ticket) และการ reset กลับไปหามัน

**Late rewinding (follow-up ปี 2020):** สำหรับ network ลึกมาก (ResNet-50+) reset ไป θ₀ จริงๆ ไม่ work เพราะ gradient ช่วงแรกสุดยัง chaotic ต้อง "rewind" ไปจุดที่เทรนไปแล้วประมาณ **5–10% ของ training budget** แทน ซึ่ง network เริ่ม settle แล้วแต่ยังไม่ถูก prune

### ผลที่น่าตื่นเต้น

- **Winning ticket มักจะเป็น 10–20% ของ network เดิม** (บาง experiment เห็นถึง < 5%)
- เทรน winning ticket เดี่ยวๆ จาก θ₀ → ได้ accuracy เท่าหรือ **ดีกว่า** network เต็ม
- เทรนได้เร็วกว่าด้วย (fewer iterations to converge) เพราะ gradient ไหลผ่านส่วนที่ "ถูกต้อง" ตลอดเวลา
- Winning ticket ยัง **transferable ข้าม dataset** ได้ระดับหนึ่ง — structure ที่ดีในงานหนึ่งมักดีในงานที่คล้ายกัน
- อีก 80–90% ที่ถูก prune ออก: **ช่วย optimization landscape ระหว่างเรียน** ไม่ได้ช่วย representation ของคำตอบที่รัน — นั่นคือ overhead ของ *การเรียน* ไม่ใช่ overhead ของ *การรัน*

### สำหรับเรา

คุณดึงอันนี้ออกมาใหม่เป๊ะ บทเรียนสำหรับชิปคุณ: **capacity ส่วนใหญ่เป็น overhead ของการ *เรียน* ไม่ใช่ของการ *รัน***

อันนี้เสนอเรื่องราวสองเฟสที่เข้ากับ sleep/consolidation ของคุณ:

- **เฟสตื่น:** เรียนแบบ over-provisioned (ใช้ Scap เต็ม) — double descent บอกว่าปลอดภัย gradient ไหลผ่าน structure เต็มเพื่อหา winning subnetwork
- **เฟส sleep:** consolidate ลงสู่ winning ticket (สลาย Scap ที่ magnitude ต่ำให้เป็นศูนย์ผ่าน leaky → ปล่อย slack กลับมาให้งานถัดไป)

"ที่ว่างที่แชร์ให้งานอนาคต" ของคุณคือ slack ของ lottery ticket นำกลับมาใช้ — ซึ่งคือ continual learning (`5-continual.md`) มาเจอการบีบอัด

---

## สมมติฐานของคุณ มีชื่อแล้ว (2): capacity ถูกแชร์ด้วย *superposition* — ตัวที่ลึก

*Anthropic, "Toy Models of Superposition," Elhage et al., 2022 ([arXiv 2209.10652](https://arxiv.org/abs/2209.10652)).*

### ปัญหาที่มันแก้

เมื่อดู neuron ใน neural network จริงๆ คุณมักพบว่า **neuron เดียว active กับหลาย concept** (เช่น neuron ใน InceptionNet ที่ fire กับทั้ง "แมว" และ "frontmost curve" และ "รถยนต์") นี่เรียกว่า **polysemantic neuron** และทำให้ interpretability ยาก แต่ยิ่งน่าฉงนกว่าคือ: ถ้า neuron แต่ละตัว "หมายถึงหลายอย่าง" network encoding อะไรอยู่กันแน่? มันแทน feature ได้มากกว่า neuron ที่มีได้อย่างไร? Elhage และทีม Anthropic ถามว่า: *network แทนฟีเจอร์มากกว่าจำนวน neuron ที่มีได้ไหม และถ้าได้ กลไกและเงื่อนไขคืออะไร?*

### กลไกจริงๆ

**Toy model**: network เล็กๆ ที่มี **n neuron** ถูกสอนให้แทน **k > n feature** ที่รู้ล่วงหน้า ในตัวอย่างหลัก: k=5, n=2 ควบคุมได้ว่า feature แต่ละตัว sparse แค่ไหน (probability ที่มันจะ active ในข้อมูล)

**เมื่อ feature dense** (active บ่อย ≈ 50% ของ step): network เลือก 2 feature สำคัญที่สุดไปใส่ใน 2 neuron แบบ **1:1 (monosemantic)** — feature 3, 4, 5 ถูกทิ้ง เพราะไม่มีที่เก็บ ถ้าบังคับให้ใส่ทั้งหมด interference สูงเกินกว่าจะคุ้ม

**เมื่อ feature sparse** (active น้อย ≈ 5% ของ step): network เก็บ **ทั้ง 5 feature ใน 2 neuron** ทำได้โดยเก็บแต่ละ feature เป็น **ทิศทาง (direction) ในปริภูมิ 2 มิติ** แทนที่จะ 1:1 กับ neuron

เงื่อนไขที่ทำให้ superposition work: เมื่อ feature A กำลัง active feature B, C, D, E มักจะ 0 (เพราะ sparse) → interference ระหว่าง A กับ B = A · B · (prob B active) ≈ ต่ำมาก เมื่อ interference ต่ำพอ network สามารถอัด k feature ลง n neuron โดยไม่เสียข้อมูล

**เรขาคณิตที่ emerge:** 5 feature ใน 2D → network จัดให้เป็น **ห้าเหลี่ยมปกติ (regular pentagon)** ห้าเวกเตอร์กระจายมุมเท่าๆ กัน = pairwise interference สม่ำเสมอและต่ำที่สุด ต่อ feature 4 feature ใน 3D → **tetrahedron** pattern สำหรับ n กับ k อื่นๆ ก็มี polyhedral pattern ที่สอดคล้องกัน เรขาคณิตเหล่านี้ไม่ได้ถูก hardcode — มัน emerge จาก optimization เพราะมันคือ packing ที่มี interference ต่ำที่สุดทางคณิตศาสตร์

**Phase diagram:** ถ้าวาด axes เป็น "sparsity" (แกน x) กับ "importance ratio ระหว่าง feature" (แกน y) จะเห็น transition ชัดเจนระหว่าง regime:
- monosemantic (sparsity ต่ำ, importance สูง) 
- superposition (sparsity สูง, importance ใกล้เคียงกัน)

### ผลที่น่าตื่นเต้น

- ยิ่ง sparsity สูง ยิ่งอัดฟีเจอร์ได้มาก — theoretical capacity scale แบบ polynomial กับ sparsity
- Feature ที่ "สำคัญกว่า" ถูกเก็บใน regime monosemantic ก่อน feature ที่สำคัญน้อยกว่าจะถูก superpose — network มี "ลำดับความสำคัญ" ในตัวเองโดยธรรมชาติ
- โมเดลใหญ่กว่า → monosemantic มากกว่า เพราะมี neuron พอที่จะแทน feature แต่ละตัว 1:1 — อธิบายว่าทำไม scaling model ถึงทำให้ interpretability ดีขึ้นตาม scale
- ยืนยันในโมเดลขนาดจริง (ไม่ใช่แค่ toy): polysemantic neurons ใน GPT-2 มี pattern ที่สอดคล้องกับทฤษฎี superposition

### สำหรับเรา

นี่คือตัวที่ตรงกับสัญชาตญาณคุณที่สุดในแฟ้มทั้งหมด อ่านสองรอบ คุณพูดว่า: *แต่ละนิวรอนถูกใช้ **น้อยกว่าที่มันทำได้** — ไม่ได้ตาย แค่ถูกจัดสรรไม่เต็ม — และ capacity นั้น **แชร์** ได้* superposition คืออันนี้เป๊ะ ทำให้เคร่งครัด

สมมติฐานคุณไม่ใช่แค่น่าเชื่อ มันคือปรากฏการณ์ที่รู้กันและถูกศึกษาแล้ว และความ sparse ของชิปคุณคือเงื่อนไขเบื้องต้นเป๊ะๆ ของมัน

นัยยะการออกแบบ: **อย่าพยายามทำให้แต่ละ Scap มีความหมายเดียว (monosemantic)** ปล่อยให้มันพก feature แบบ superposed ภายใต้ sparsity — นั่นคือวิธีอัด k ความสามารถลงใน n < k องค์ประกอบแอนะล็อก การบีบอัดของคุณ *คือ* superposition และ superposition *ต้องการ* sparsity ของคุณ

---

## รูปร่างของคำตอบ (ไฟล์นี้)

ทฤษฎีที่คุณกำลังเอื้อมไปหา: **การเรียนรู้คือการบีบอัด** (MDL) — ดังนั้น "ลงในชิป" กับ "เรียนรูปร่างจริง" คือ **วัตถุประสงค์เดียว** ไม่ใช่สอง; คุณต้องการ *กฎการเรียนรู้ที่บีบอัด* ไม่ใช่ตัวบีบอัดแยก มันเวิร์กเพราะ **งานมันเล็กจิ๋ว** (intrinsic dimension ≪ จำนวนพารามิเตอร์) — คุณเก็บของมิติต่ำใน substrate ก้อนใหญ่ การอ่าน **double-descent** ของคุณถูก: capacity เกินปลอดภัยเพราะตัวเรียนชอบ fit ที่ *บีบอัดได้* และ noise หักล้างกัน — ดังนั้นอย่ากลัว Scap เพิ่ม และสมมติฐาน spare-capacity ของคุณคือสามสิ่งที่ยืนยันแล้วในคราวเดียว: slack มีจริง (**Lottery Ticket**, 80–90% เป็น overhead-ของ-การเรียน), งานเล็ก (**intrinsic dimension**), และ slack ถูกแชร์ด้วยการอัดฟีเจอร์เกือบตั้งฉากภายใต้ sparsity (**superposition**) — *ซึ่ง substrate sparse ของคุณคือเงื่อนไขเบื้องต้นของมัน* คุณไม่ได้เดา; คุณดึงมุมมองการบีบอัดของการเรียนรู้ของวงการออกมาใหม่ `14-compression-methods.md` คือวิธี *สร้าง* มัน
