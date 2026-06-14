# 8 — อะตอม: หนึ่งบล็อกคำนวณควรเป็นอะไร?

> คำพูดของคุณ: *"อะตอมของแต่ละบล็อก — ตัว ganglion และ ganglion ALU"* หน่วยที่เรียนรู้ได้ที่เล็กที่สุดที่ถูกต้องคืออะไร? คำตอบค่าตั้งต้น (นิวรอน = dot-product + nonlinearity ตายตัว) เป็นทางเลือก **หนึ่ง** ในหลาย ๆ ทาง และอาจไม่ใช่ทางที่ดีที่สุดสำหรับ substrate ที่เป็น *แอนะล็อกและเวลาต่อเนื่อง* ไฟล์นี้คือเมนูของอะตอม — และสองในนั้น (liquid neuron, reservoir) ใกล้เคียงกับ "วงจรแอนะล็อกที่อธิบายในฐานะ learning primitive" อย่างน่าตกใจ

---

## ค่าตั้งต้น และทำไมถึงควรตั้งคำถามกับมัน

นิวรอนมาตรฐานคำนวณ `y = φ(Σ wᵢxᵢ)` — **dot product** แล้วตามด้วย nonlinearity ที่ **ตายตัว** (ReLU) Scap-crossbar ของ draft-6.0 คุณคำนวณอันนี้เป๊ะ และ Ganglion 2-3-3-2 เก่าของคุณคือการจัดอันชาญฉลาด มันใช้ได้ แต่มันฝังสมมติฐานบางอย่างไว้: nonlinearity *ตายตัว*, เวลา *ไม่ต่อเนื่อง* (หนึ่งก้าว = หนึ่งเลเยอร์), และ expressivity ทั้งหมดอยู่ใน *การเชื่อมต่อ* ไม่ใช่ใน *ตัวหน่วย*

อะตอมข้างล่างแต่ละตัวคลายสมมติฐานหนึ่งออก — และอะตอมที่ถูกต้องสำหรับคุณคือตัวที่สมมติฐานของมันตรงกับ *ฟิสิกส์ของคาปาซิเตอร์*

---

## Kolmogorov–Arnold Networks (KAN) — ย้ายการเรียนรู้ไปอยู่ใน *activation* ไม่ใช่ใน weight

*Liu et al., 2024 ([arXiv 2404.19756](https://arxiv.org/abs/2404.19756)).*

### ปัญหา: MLP เรียนที่ weight แต่ activation ตาย

MLP แบบดั้งเดิมมีโครงสร้าง: **ตายตัวบน node** (activation function เช่น ReLU หรือ sigmoid), **เรียนรู้ได้บน edge** (weight) การ express ฟังก์ชันที่ซับซ้อนต้องอาศัย weight จำนวนมากร่วมกัน ซึ่งทำให้ตีความยาก และ network ใหญ่มีประสิทธิภาพมาก แต่เข้าใจน้อย

KAN ถามว่า: **"ถ้าเราย้ายความสามารถในการเรียนรู้ไปอยู่ที่ edge แทน node ล่ะ?"**

### กลไก: spline บน edge แทน weight คงที่

KAN อ้างอิงทฤษฎีบท Kolmogorov–Arnold (1957): ฟังก์ชัน multivariate ใด ๆ สามารถแสดงเป็นผลรวมของฟังก์ชัน univariate ได้เสมอ นั่นหมายความว่าถ้าคุณมีฟังก์ชัน univariate ที่เรียนรู้ได้เพียงพอ คุณ represent ฟังก์ชัน multivariate ใด ๆ ได้โดยไม่ต้องมี linear weight

สถาปัตยกรรม:
- แต่ละ edge พก **B-spline ที่เรียนรู้ได้** แทน scalar weight
- B-spline คือ piecewise polynomial — มี "grid points" กำหนดรูปร่าง เรียนรู้ได้ผ่าน gradient บน control points
- ไม่มี fixed activation function เลย เส้นโค้งของ spline บน edge *คือ* activation
- Node เป็นแค่ตัวรวมค่า (sum) — ไม่มีการคำนวณที่ node

สมการ forward ของ KAN layer:
```
y_j = Σ_i  φ_{ij}(x_i)
```
โดย φ_{ij} คือ learnable spline บน edge (i→j) — แต่ละเส้นเชื่อมมีเส้นโค้งของตัวเอง

การเรียนรู้: ปรับ control points ของ spline แต่ละตัวด้วย gradient descent

### ผลที่ได้

- KAN ขนาดเล็กมาก (เช่น [2,5,1] = input 2, hidden 5, output 1) ทำ symbolic regression ได้ดีกว่า MLP ที่ใหญ่กว่ามาก
- Interpretability สูง: คุณ plot φ_{ij}(x) ได้เลย เห็นว่า edge นั้น encode ฟังก์ชันอะไร (sin, x², log x) ในงาน physics: KAN สามารถ "discover" สมการทางฟิสิกส์จากข้อมูลได้โดยตรง
- สำหรับ scientific functions (ฟังก์ชันที่มี structure ชัด): KAN ดีกว่า MLP อย่างชัดเจน
- สำหรับ large-scale vision/language: ยังสู้ MLP ไม่ได้ เพราะ spline overhead สูงและ GPU-parallelism น้อยกว่า
- เทรนช้ากว่า MLP ประมาณ 10× บน hardware ปัจจุบัน

### สำหรับเรา

ไอเดียที่ยั่วใจที่สุด: *"ถ้า learnable parameter ไม่ใช่ weight แต่เป็นรูปร่างของเส้นตอบสนองของสาย?"*

บน substrate แอนะล็อก "ฟังก์ชัน univariate ที่เรียนรู้ได้บน edge" คือ **องค์ประกอบถ่ายโอน nonlinear ที่โปรแกรมได้** อะตอมแบบ KAN = "ปรับเส้นโค้ง transfer function ของ op-amp" แทน "ปรับ gain" — ซึ่งบน silicon ทำได้ด้วยการโปรแกรมค่า bias/threshold ของ nonlinear element

KAN บอกว่า expressivity-ต่อ-parameter สูงกว่าได้ถ้าคุณเรียน *เส้นโค้งถ่ายโอน* แทน *เกน (gain)* สำหรับงานที่มี structure เชิงฟิสิกส์ (ซึ่ง analog substrate มักเจอ) KAN อาจ efficient กว่ามาก

ไม่ใช่อะตอมเฟส-1 ของคุณ (dot-product crossbar ยังถูกและเพียงพอ) แต่มันคือคำตอบของคำถาม "อะตอมรวยกว่านี้ได้ยังไง" และมันเข้ากับแอนะล็อกดีกว่าดิจิทัล (spline = analog curve fitting, ไม่ใช่ discrete operation)

---

## Liquid Time-Constant Networks — อะตอมคือนิวรอนแบบ *เวลาต่อเนื่อง*

*Hasani, Lechner, Amini, Rus & Grosu, AAAI 2021 ([arXiv 2006.04439](https://arxiv.org/abs/2006.04439)).*

### **อ่านอันนี้ให้ละเอียด — มันแทบจะเป็นคำอธิบายชิปของคุณ**

### ปัญหา: นิวรอนดิจิทัลไม่ใช่ธรรมชาติของเวลา

RNN และ LSTM เทรนด้วย BPTT (Backpropagation Through Time) ซึ่งมีสมมติฐานว่า **เวลาเป็นก้าวไม่ต่อเนื่อง (discrete steps)** — ก้าว t=1, t=2, t=3 ในโลกจริงเวลาต่อเนื่อง และ substrate ของคุณก็ต่อเนื่องเช่นกัน การบังคับให้วงจรแอนะล็อกทำงานแบบ discrete timestep คือการผลาญ precision ไปฟรี ๆ

Liquid Time-Constant Networks (LTC) แก้ด้วยการอธิบายนิวรอนเป็น **สมการเชิงอนุพันธ์** ไม่ใช่ discrete recurrence

### กลไก: ODE ที่มี time constant แปรผัน

Liquid neuron ไม่ใช่ก้าวไม่ต่อเนื่อง แต่เป็น **ระบบพลวัตแบบเวลาต่อเนื่อง:**

```
dx/dt = −x/τ(x, I(t)) + f(x, I(t), θ)
```

โดย:
- `x` = state ของนิวรอน
- `τ(x, I(t))` = **time constant ที่แปรผัน** ตามทั้ง state ปัจจุบัน (x) และอินพุต (I(t)) — นี่คือ "liquid" ส่วน
- `f(x, I(t), θ)` = driving term (สัญญาณที่ไหลเข้า)
- เทอม `−x/τ` = leaky/decay term (คาปาซิเตอร์รั่วนั่นเอง)

Time constant ที่ **ขึ้นกับอินพุต** คือกุญแจสำคัญ: เมื่ออินพุตเปลี่ยนเร็ว τ ปรับตัวเพื่อ integrate ช้าลง เมื่ออินพุตเสถียร τ ปรับตัวเพื่อตอบสนองเร็วขึ้น — นิวรอนปรับ timescale ของตัวเองตาม context

Forward pass ทำโดยใช้ ODE solver (explicit Euler หรือ Runge-Kutta) integrate สมการนี้ตลอดช่วงเวลา เทรนด้วย adjoint method (backprop ผ่าน ODE solver)

### ผลที่ได้

**ผลลัพธ์ลือลั่น: 19 นิวรอน เรียนขับรถได้**

ทีม MIT/TU Wien เทรน liquid network ขนาดจิ๋ว 19 นิวรอน บน 25 ชั่วโมง video ของนักขับรถผู้เชี่ยวชาญ แล้วนำไปควบคุมรถจริง ๆ บนเส้นทางที่ไม่เคยเห็น แสดงพฤติกรรมที่ถูกต้องในสภาพแสง สภาพถนน และสภาพการจราจรที่หลากหลาย

ทำไม 19 นิวรอนถึงพอ? เพราะ liquid neurons มี **expressive power ต่อหน่วยสูงมาก** — time-varying dynamics ทำให้แต่ละนิวรอนพกข้อมูลเชิงเวลาได้มาก แทนที่จะ encode แค่ "activation ณ เวลานี้"

ผลอื่น:
- ทน noise ดีกว่า LSTM บน time-series tasks
- เสถียรและมีขอบเขต (proved Lyapunov stable ภายใต้เงื่อนไข regularity)
- Interpretable: state x ของแต่ละนิวรอนสัมพันธ์กับ concept จริง ๆ ที่อ่านออกได้

**Closed-form Continuous-time (CfC):** variant ที่ออกมาหลังจาก Hasani et al. 2022 ให้ **รูปแบบปิด (closed form)** ไม่ต้องวนลูป ODE solver ทำให้ fast กว่ามาก:
```
x(t) = σ(-f(x_0, I, θ))·x_0 + (1 − σ(-f))·g(x_0, I, θ)
```
นั่นคือ **interpolation ระหว่างสถานะสองสถานะ** ด้วย learned sigmoidal gate — รัน single forward pass ได้เลย ไม่ต้อง integrate

### สำหรับเรา

**คาปาซิเตอร์รั่วคือ liquid neuron** — ตรงตัวอย่างไม่ต้องตีความ

สมการ `dx/dt = −x/τ + input` คือสมการ RC circuit เป๊ะ: capacitor charge ไหลออกผ่าน resistor (−x/τ) และถูก drive โดย current source (input) liquid neuron คือ RC circuit ที่มี τ ปรับได้ตาม input voltage

ถ้า τ ปรับด้วย voltage-controlled resistor หรือ transconductance amplifier — คุณมี liquid neuron ใน hardware แล้ว

นี่คือตัวเก็งที่แข็งแกร่งที่สุดของ **อะตอม time-series เฟส 2**:
- เวลาต่อเนื่อง — ธรรมชาติของ substrate
- จิ๋ว แต่ expressive (19 นิวรอนขับรถ)
- เสถียร (Lyapunov stable)
- Variable timescale = attention-like behavior ในเวลา โดยไม่มี attention mechanism

ข้อควรระวัง: gradient เทรนด้วย BPTT through ODE จางหายในซีเควนซ์ยาว แต่คุณไม่ได้เทรนด้วย BPTT คุณใช้ local/online learning (e-prop จาก `10-realtime.md`) — จุดอ่อนนี้ไม่ใช่ปัญหาของคุณ

---

## Neural ODEs — ใบอนุญาตเชิงแนวคิด

*Chen, Rubanova, Bettencourt & Duvenaud, NeurIPS 2018 ([arXiv 1806.07366](https://arxiv.org/abs/1806.07366)).*

### ปัญหา: discrete layers เป็นการประมาณที่หยาบ

ทุก neural network ที่ลึกคือ: ใส่อินพุต → ผ่านเลเยอร์ 1 → เลเยอร์ 2 → ... → เลเยอร์ L → ได้เอาต์พุต นั่นคือ transformation ที่ **discrete** ถ้า L ใหญ่มาก มันใกล้เคียงกับ ODE — แต่ทำไมไม่ใช้ ODE ตรง ๆ เลย?

### กลไก: depth = integration time

Neural ODE กำหนดว่าแทนที่จะมีเลเยอร์ตายตัว ให้นิยาม dynamics เป็น:
```
dh(t)/dt = f(h(t), t, θ)
```
โดย h(t) คือ hidden state ณ เวลา t, f คือ neural network ขนาดเล็ก (ที่เรียนรู้ θ)

Output = h(T) ที่ได้จาก **integrate จาก t=0 ถึง t=T** ด้วย ODE solver

"ความลึก" กลายเป็น *เวลาในการ integrate* — T สูง = deep network T ต่ำ = shallow และ T ปรับตัวตาม accuracy ที่ต้องการ

Backprop ใช้ **adjoint method:** แทนที่จะ store activations ทุกก้าว (แพง) ให้ solve ODE ย้อนหลังเพื่อ reconstruct activations (memory O(1) ต่อ batch)

### ผลที่ได้

- Memory constant บน depth — เทรน "infinitely deep" network ด้วย memory เท่า single layer
- Adaptive computation: ODE solver ปรับ step size ตาม difficulty ของอินพุต — input ง่ายใช้ steps น้อย, ยากใช้มาก (computation-on-demand)
- Continuous normalizing flows: Neural ODE นำไปสู่ generative model ที่มี exact likelihood

### สำหรับเรา

Neural ODE คือ **ใบอนุญาตเชิงแนวคิดของ "ปล่อยให้พลวัตแอนะล็อกเป็นการคำนวณ"**

ชิปคุณไม่ได้ประมวลผลเลเยอร์ทีละชั้น — มันวิวัฒน์ประจุตามเวลา ถ้าคุณมองระบบแอนะล็อกที่ settle ไปสู่ equilibrium ผ่าน RC dynamics นั่นคือ Neural ODE ที่รัน f = network weight เป็น connection strength ระหว่าง nodes

รวม liquid neuron + Neural ODE: "ให้ ODE รัน" = ปล่อยให้คาปาซิเตอร์ชาร์จ/คายประจุตาม physics จนระบบ settle คุณสมบัติ "adaptive depth" ของ Neural ODE เทียบเท่ากับ "ปล่อยให้ settle นาน กว่าถ้า input ยาก"

---

## Capsule Networks — อะตอมในฐานะ *เวกเตอร์* ไม่ใช่ scalar

*Sabour, Frosst & Hinton, NeurIPS 2017 ([arXiv 1710.09829](https://arxiv.org/abs/1710.09829)).*

### ปัญหา: scalar activation ทิ้ง pose information

CNN มาตรฐานมีปัญหา: pooling layers ทิ้งข้อมูล spatial แม้จะ detect วัตถุในภาพที่ rotate แล้วได้ แต่ถ้าคุณถามว่า "วัตถุอยู่ตรงไหน? หมุนไปแค่ไหน? scale เท่าไหร่?" — ข้อมูลนั้นหายไปแล้ว

Hinton เสนอว่านิวรอนควรปล่อยเอาต์พุตเป็น **เวกเตอร์** ไม่ใช่ scalar:
- **ความยาว** ของเวกเตอร์ = confidence ที่ entity นี้มีอยู่ (0 → 1)
- **ทิศทาง** ของเวกเตอร์ = instantiation parameters ของ entity นั้น (pose, orientation, scale, deformation)

### กลไก: routing by agreement

Capsule ระดับล่าง j ส่งเวกเตอร์ u_j ขึ้นไปยัง capsule ระดับสูง i ด้วยการ transform:
```
û_{j|i} = W_{ij} · u_j
```
W_{ij} คือ transformation matrix ที่เรียนรู้ว่า "ถ้า capsule j detect ส่วนนี้ใน pose นี้ capsule i ควรคาดหวังอะไร?"

จากนั้น "routing by agreement": capsule ระดับบนจะรับเวกเตอร์จาก capsule ล่างที่ **เห็นพ้องกัน** มากที่สุด ผ่านกระบวนการ iterative (dynamic routing):

1. Initialize coupling coefficients c_{ij} เท่ากัน
2. Compute weighted sum: `s_i = Σ_j c_{ij} û_{j|i}`
3. Squash: `v_i = ||s_i||² / (1 + ||s_i||²) · s_i/||s_i||` (normalize ให้ length ∈ [0,1])
4. Update agreement: `b_{ij} += û_{j|i} · v_i` (dot product บอกว่า prediction ตรงกับ output แค่ไหน)
5. Softmax c จาก b: `c_{ij} = softmax(b_{ij})` over i
6. Repeat 2-5 สองสามรอบ

Capsule ที่ "เห็นด้วย" กับ parent จะได้รับ coupling weight สูงขึ้น ที่ไม่เห็นด้วยจะถูกลด — เป็นการ vote แบบ soft

### ผลที่ได้

- MNIST: 99.75% (ดีกว่า CNN baseline เล็กน้อย)
- ทน viewpoint variation ดีกว่า CNN อย่างชัดเจน — test บน affNIST (distorted MNIST): 79% vs CNN 66%
- ต้องการ training data น้อยกว่า
- ปัญหา: ช้ามาก ไม่ scale ไป ImageNet ได้ดี routing algorithm แพง Hinton เองก้าวข้าม capsule ไปสู่ GLOM (`9-hierarchy.md`)

### สำหรับเรา

ส่วนใหญ่เป็นฝั่งไอเดีย แต่คำถามที่มันยกขึ้นมาคม:

**อะตอมของคุณควรปล่อยเลขตัวเดียว หรือเวกเตอร์เล็ก ๆ ของคุณสมบัติ?**

อะตอมแบบเวกเตอร์พกโครงสร้างต่อหน่วยมากกว่า ถ้าแต่ละ output unit เป็น (magnitude, direction) คุณ encode "มีอยู่ไหม + มีลักษณะยังไง" ในหน่วยเดียว แทน encode เฉพาะ "มีอยู่ไหม"

"Routing by agreement" = ปฏิบัติการโหวต/ฉันทมติที่ substrate แอนะล็อกทำได้ — winner-take-all + lateral inhibition เป็น analog vote ที่ถูก

เกี่ยวข้องถ้าการคิดเฟส 2 ต้องส่งของ "ที่มีโครงสร้าง" (typed bundle ไม่ใช่ scalar) ระหว่างบล็อก ถือมันเป็น "อะตอมอาจเป็นชุดข้อมูลเล็ก ๆ ไม่ใช่ scalar"

---

## Dendritic computation — นิวรอนชีวภาพหนึ่งตัวก็เป็นตาข่าย 2 ชั้นอยู่แล้ว

*Poirazi & Mel, 2003 (Neuron); Beniaguev, Segev & London, 2021 ([Neuron](https://www.cell.com/neuron/fulltext/S0896-6273(21)00501-8)).*

### ปัญหา: "นิวรอน = dot product" ผิดตั้งแต่ต้น

คณิตศาสตร์ของ neural network สมมติว่านิวรอนหนึ่งตัวทำ: รับ synaptic inputs → sum ทั้งหมด → apply nonlinearity → ส่งออก แต่นิวรอนชีวภาพจริง ๆ ไม่ได้เป็นแบบนั้น

### สิ่งที่ Poirazi & Mel ค้นพบ

พวกเขา model dendritic tree ของ pyramidal neuron ใน hippocampus อย่างละเอียด ผลที่น่าตกใจ: **เดนไดรต์ของนิวรอนหนึ่งตัวทำการคำนวณ nonlinear แบบโลคอล** ก่อนที่ soma จะรวมสัญญาณ

โครงสร้างจริง ๆ:
1. Synapse หลาย ๆ ตัวบน **dendritic branch** เดียวกัน interact กันแบบ nonlinear ภายใน branch
2. แต่ละ dendritic branch ปล่อย "branch output" ออกมา
3. Soma รวม branch outputs ทั้งหมด (summation) แล้วยิง spike ถ้าเกิน threshold

นั่นหมายความว่านิวรอนหนึ่งตัว ≈ **two-layer network ขนาดเล็ก**: เลเยอร์แรกคือ dendritic branches (nonlinear integration), เลเยอร์สองคือ soma (final summation + threshold)

**Beniaguev et al. 2021** ยืนยันนี้อย่างชัดเจน: พวกเขาเทรน deep neural network ให้ simulate การทำงานของนิวรอน L5 pyramidal neuron เดี่ยว ๆ และพบว่าต้องการ network ที่มี **5-8 ชั้นที่มี 128 units ต่อชั้น** ถึงจะ match behavior ได้ — นิวรอนชีวภาพหนึ่งตัวมีความซับซ้อนเทียบเท่าตาข่ายลึก

### ผลที่ได้

งานทดลอง (Poirazi et al.): แยก XOR pattern ได้โดยใช้นิวรอนจำนวนน้อยกว่าถ้าใช้ dendritic computation เทียบกับ point neuron ที่ต้องเพิ่มจำนวนหรือจำนวนชั้นเพื่อ solve task เดียวกัน

หลักการ: dendritic nonlinearity ให้ expressivity ต่อ parameter สูงกว่า point neuron มาก

### สำหรับเรา

นี่คือใบอนุญาตให้ทำอะตอมของคุณ **nonlinear ภายในตัว** ซึ่ง **Ganglion 2-3-3-2 เก่าของคุณก็เป็นอยู่แล้ว** — บล็อกหลายองค์ประกอบที่ทำตัวเป็นอะตอมเดียว นั่นคือ dendritic computation ใน disguise

บทเรียน: อย่าคิดว่าอะตอมต้องเป็นปฏิบัติการเดียว อะตอมของสมองชีวภาพคือตาข่ายย่อย nonlinear เล็ก ๆ และของคุณก็เป็นได้ เลเยอร์จิ๋วสองชั้น (input → nonlinear combination → output) ภายใน unit เดียวทำให้ network ลึกทั้งก้อนมี expressivity สูงขึ้นโดยไม่ต้องเพิ่มจำนวนชั้น

สำหรับเฟส 2: อะตอม recurrent อาจเป็น liquid neuron เล็ก ๆ (มี dendritic timescale integration) + soma (threshold/output) ซ้อนกัน แทนจะเป็น unit เดียวแบน

---

## Reservoir computing — อะตอมที่คุณ *ไม่เทรน*

*Echo State Networks: Jaeger, 2001; Liquid State Machines: Maass, 2002. ([รีวิว](https://www.sciencedirect.com/science/article/abs/pii/S1574013709000173)).*

### ปัญหา: เทรน RNN ยากมาก

RNN เทรนด้วย BPTT ซึ่งมี gradient vanishing/exploding ปัญหา เป็น computationally expensive และต้องการ hyperparameter tuning มาก Jaeger และ Maass ตั้งคำถาม: **"จำเป็นต้องเทรน RNN ทั้งก้อนจริง ๆ มั้ย?"**

### กลไก: ตรึง reservoir เทรนแค่ readout

ทำ **RNN recurrent ขนาดใหญ่ที่ตายตัวและสุ่ม** ("reservoir") แล้ว**ไม่เทรนเลย** จากนั้นเทรนแค่ **linear readout layer** ข้างบน

เหตุผลที่ทำงาน: reservoir สุ่มที่ตายตัวทำ **nonlinear projection** ของอินพุตเข้าสู่พื้นที่มิติสูง ที่ซึ่งปัญหาที่ไม่ linear separable ใน input space กลายเป็น linearly separable ได้ เหมือน kernel method แต่เป็น recurrent

เงื่อนไขที่ reservoir ต้อง satisfy คือ **echo state property:** state ของ reservoir ต้องถูก determine โดย input history เพียงพอ ไม่ใช่ initial conditions arbitrarily ทั้งนี้ทำได้โดยตั้ง spectral radius ของ weight matrix < 1

**Echo State Networks (ESN):** ใช้ continuous-valued neurons, เทรน readout ด้วย linear regression (closed form, ทันที)

**Liquid State Machines (LSM):** ใช้ spiking neurons, เข้ากับ neuroscience มากกว่า

ความสัมพันธ์กับ liquid neuron: LSM ชื่อ "liquid" เพราะ reservoir มีพลวัตที่ "liquid-like" คล้ายของเหลว — Hasani ยืมคำนี้มาตั้งชื่อ liquid networks

### ผลที่ได้

- ESN เรียนรู้ chaotic time series (Mackey-Glass) ได้ดีกว่า LSTM training ด้วย compute น้อยกว่ามาก
- LSM แสดงว่าวงจร cortical column สุ่มอาจเป็น reservoir ที่ natural อยู่แล้ว
- Speech recognition ด้วย readout เดียวบน reservoir สุ่ม: ทำได้แต่แย่กว่า trained RNN ใน benchmark ปัจจุบัน
- งานควบคุม robot: reservoir + linear readout ทำ motor control ได้เร็วกว่า trained network มาก (online adaptation ทันที)

### สำหรับเรา

**ทางลัดที่ลึกซึ้งสำหรับ substrate แอนะล็อก:** วงจรแอนะล็อก recurrent ที่ **สุ่มและตายตัว** แทบจะฟรี — มันก็แค่ตาข่ายแอนะล็อกยุ่ง ๆ ที่ไม่ต้องทำให้แม่นยำ device mismatch ที่คุณกังวล? reservoir บอกว่า *randomness คือ feature ไม่ใช่ bug*

สำหรับต้นแบบเฟส 2 อันแรก นี่คือวงลูปการคิดที่ใช้แรงน้อยที่สุดที่อาจเวิร์ก: **reservoir แอนะล็อกตายตัว + readout ที่เทรนด้วย SCFF/GD**

- Inference: reservoir วิวัฒน์ไปกับอินพุตแบบ realtime (เป็น ODE ต่อเนื่อง)
- Learning: เทรนแค่ linear readout ด้วย recursive least squares (online, single pass)
- Hardware: ไม่ต้อง precision ใน reservoir connections เลย — สุ่มก็ได้ ไม่เปลือง Scap

**มันยังทน device mismatch โดยดีไซน์:** reservoir ควรจะสุ่มอยู่แล้ว device mismatch แค่ทำให้มัน "สุ่มกว่า" นิดหน่อย — spectral radius คือ thing เดียวที่ต้อง control และทำได้ด้วยการ scale connection strength globally

เป็นตัวเก็งที่แข็งแกร่งของ "โกงด้วยกฎแอนะล็อก" ก่อนจะ commit กับ full liquid network ที่เทรนทั้งก้อน

---

## รูปร่างของคำตอบ (ไฟล์นี้)

อะตอม สำหรับเรา: ค่าตั้งต้น (dot-product + ReLU, Scap-crossbar) ใช้ได้ดีกับส่วนที่เป็น **feed-forward เฟส 1** สำหรับ **แกน time-series เฟส 2** อะตอมที่เข้ากับ substrate ล้วนเป็น **เวลาต่อเนื่อง**:

- **Liquid neuron** (RC circuit ที่มี τ เรียนรู้ได้และขึ้นกับสถานะ) คือตัวที่ใกล้ "วงจรของคุณในฐานะ learning primitive" ที่สุด 19 นิวรอนขับรถ — substrate ของคุณทำได้แบบ native
- **Neural ODE** คือกรอบที่บอกว่า "ปล่อยให้พลวัตแอนะล็อกเป็นการคำนวณ" — depth = integration time
- **KAN** บอกว่า expressivity อยู่ใน *เส้นโค้งถ่ายโอนที่เรียนรู้ได้* ไม่ใช่ gain — เป็นมิตรกับแอนะล็อก
- **Dendritic computation** บอกว่าอะตอมเป็น *ตาข่ายย่อยภายในเล็ก ๆ* ได้ — Ganglion ของคุณก็เป็นแล้ว
- **Reservoir** บอกว่าคุณอาจไม่ต้องเทรนแกน recurrent เลย — แค่ readout — ซึ่งคือการโกงแอนะล็อกที่ถูกที่สุดที่มี และ random device mismatch คือ feature

เลือกอะตอมที่คณิตศาสตร์ของมันคือฟิสิกส์ของคุณ: นั่นชี้แรง ๆ ไปที่ **liquid / ODE / reservoir** — ทั้งสามล้วน native กับ RC dynamics ที่ substrate ของคุณสร้างมา
