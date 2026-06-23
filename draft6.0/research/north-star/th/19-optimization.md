# 19 — ทำไมการเรียนรู้ถึงลู่เข้า *และ* generalize ได้ (รากฐานด้าน optimization)

> ทั้งโปรเจกต์เดิมพันว่าตาข่าย *จะ* เทรนจนได้คำตอบที่ดี *และ* คำตอบนั้นจะทำงานกับข้อมูลที่ไม่เคยเห็น เดิมพันนั้นวางอยู่บนทฤษฎี optimization & generalization ซึ่งคนส่วนใหญ่รู้ผลลัพธ์ แต่ไม่รู้กลไก ไฟล์นี้จะเดินผ่านกลไกจริงๆ ทีละขั้น เพราะถ้าเข้าใจ "ทำไม" คุณก็ออกแบบชิปได้ดีขึ้น ไม่ใช่แค่ท่องผล **สิ่งที่มัดทุกอย่างเข้ากับโปรเจกต์นี้: สิ่งที่ทำให้คำตอบ generalize ได้ คือสิ่งเดียวกับที่ทำให้มันรอด noise แอนะล็อก — ความแบน (flatness) — และมันมาฟรีจากฟิสิกส์ของชิป**

---

## มันจะลู่เข้าไหม? Neural Tangent Kernel และการพิสูจน์ที่ไม่มีใครคาดคิด

*Neural Tangent Kernel: Jacot, Gabriel & Hongler, 2018 ([arXiv 1806.07572](https://arxiv.org/abs/1806.07572)).*

### ปัญหาที่ทุกคนรู้สึกก่อนปี 2018

ตาข่ายใหญ่มี parameter เป็นล้าน landscape ของ loss ซับซ้อนมหาศาล ทำไมมันถึงเทรนได้เลย? ทำไมตาข่ายที่ไม่ convex ถึงหา solution ดีๆ ได้สม่ำเสมอ? ทำไมไม่ติดอยู่ใน local minimum ที่แย่?

Jacot และทีมตั้งถามว่า ถ้าปล่อยให้ตาข่ายกว้างขึ้นเรื่อยๆ ไม่มีที่สิ้นสุด — **infinite width limit** — อะไรจะเกิดขึ้น?

### กลไกที่ทำให้ผลลัพธ์น่าตะลึง

ใน infinite width limit มีสิ่งประหลาดเกิดขึ้น: weights **แทบไม่ขยับเลย** relative to their initialization ราวกับ frozen ทั้งที่ loss ลดลงตลอด ทำไมถึงเป็นอย่างนั้น? เพราะเมื่อมี parameter จำนวนมหาศาล แต่ละ parameter ต้องรับผิดชอบการเปลี่ยน loss แค่นิดเดียว ดังนั้นแต่ละ weight ขยับแค่ tiny step แต่รวมกันก็ลด loss ได้มาก

เมื่อ weights แทบไม่ขยับ ฟังก์ชันของตาข่าย f(x; θ) สามารถ **linearize** รอบจุด initialization θ₀ ได้:

$$f(x; \theta) \approx f(x; \theta_0) + \nabla_\theta f(x; \theta_0) \cdot (\theta - \theta_0)$$

ตัว Jacobian ∇_θ f(x; θ₀) แทบไม่ขยับตาม (เพราะ weights ไม่ขยับ) ดังนั้นตัว kernel ที่นิยามว่า:

$$K(x, x') = \langle \nabla_\theta f(x; \theta_0), \nabla_\theta f(x'; \theta_0) \rangle$$

(dot product ของ Jacobians สองตัว) ซึ่งเรียกว่า **Neural Tangent Kernel (NTK)** มัน **คงที่ตลอดการเทรน** ไม่เปลี่ยนแปลงตาม weight

### ทำไมถึงเป็นข่าวดีใหญ่?

ทีนี้ถ้า NTK คงที่ การเทรนตาข่าย linearized นี้ด้วย gradient descent เทียบเท่าทางคณิตศาสตร์กับ **kernel regression** ด้วย kernel K

Kernel regression คืออะไร? มันคือการทำนาย:

$$\hat{y}(x) = \sum_{i=1}^{n} \alpha_i K(x, x_i)$$

โดย αᵢ คือ weights ที่หาจาก Kernel Ridge Regression (KRR) ซึ่งมี **closed-form solution เดียว** ไม่มีหลาย local minimum และปัญหานี้ **convex** — มี global minimum ที่ชัดเจนหนึ่งเดียว

ดังนั้นลำดับก็คือ: **กว้างมาก → NTK คงที่ → linearized system → kernel regression → convex → global convergence พิสูจน์ได้**

ผลพลอยได้ที่งดงาม: ใน infinite width limit พลวัตการเทรนกลายเป็น linear ODE: `dθ/dt = -η · K · (predictions - labels)` ซึ่งแก้ได้แบบ closed-form ลู่เข้า exponential สู่ global minimum โดยตรง ไม่วนเวียน ไม่ติดหล่ม

### ขอบเขตของทฤษฎี

ในชีวิตจริงตาข่ายไม่ได้กว้างอนันต์ แต่ **ตาข่ายที่กว้างและ over-parameterized** มีพฤติกรรมใกล้ NTK regime พอที่จะทำให้: convergence เป็นเรื่องปกติ local minimum ที่แย่มีน้อยมาก และพลวัตเกือบเป็น linear ปัญหาคือ: ยิ่งเข้า pure NTK regime ตาข่ายยิ่ง "เรียนรู้" ในฐานะ kernel แทนที่จะเรียน deep features จริงๆ — มัน "memorize ด้วย similarity" แทนที่จะ "สร้าง representation"

**สำหรับเรา:** ผลนี้ให้เหตุผล structural ว่าทำไม Scap เพิ่มถึงทำให้เทรน *ง่ายขึ้น* — ไม่ใช่แค่เพราะ double descent (`13`) แต่เพราะ over-parameterization ดันระบบเข้า near-NTK regime ที่พิสูจน์ได้ว่าลู่เข้า แต่ระวัง: กว้างเกินไปจนเข้า pure kernel regime อาจทำให้ไม่ได้ representation ที่ดี ดังนั้น design space จริงๆ คือ "กว้างพอที่จะ converge ง่าย แต่ไม่กว้างจนหยุดเรียน features" — ซึ่งเป็น tradeoff ที่ simulations ของเราจะต้องหา

นัยยะด้านฮาร์ดแวร์: ถ้าตาข่ายแอนะล็อก analog noise ทำให้ NTK ไม่ stable (เปลี่ยนไปตาม noise รอบต่อรอบ) การลู่เข้าจะช้ากว่า ideal แต่ถ้า noise ถูก average ออกในระดับ population (หลาย Scap เฉลี่ยกัน) NTK ก็ stable พอที่จะ convergence ดี — นี่คืออีกเหตุผลที่ population coding มีประโยชน์ (`17`)

---

## มันจะติดหล่มใน local minimum ที่แย่ไหม? ไม่ — เพราะทฤษฎี random matrix บอกว่าหล่มไม่มี

*Dauphin, Pascanu, Gulcehre, Cho, Ganguli & Bengio, 2014 ([arXiv 1406.2572](https://arxiv.org/abs/1406.2572)).*

### กลไกที่ใช้: Random Matrix Theory

ทุก critical point (ที่ gradient = 0) มี **Hessian** — matrix ของ second derivatives ที่บอกว่าพื้นผิว loss โค้งยังไงรอบจุดนั้น eigenvalues ของ Hessian บอกประเภทของ critical point:
- **eigenvalues บวกทั้งหมด** → local minimum (ชาม)
- **eigenvalues ลบทั้งหมด** → local maximum (เนินกลับหัว)
- **eigenvalues ผสม บวกและลบ** → **saddle point** (อานม้า — ลงทางหนึ่ง ขึ้นอีกทาง)

คำถาม: ใน loss landscape ที่มี N parameter ถ้าเราอยู่ที่ critical point สุ่มหนึ่ง ความน่าจะเป็นที่มันเป็น local minimum ที่แย่ (eigenvalues บวกทั้งหมด แต่ loss ยังสูง) คืออะไร?

### คำตอบจาก RMT: probability ลดเป็น exponential

RMT (Random Matrix Theory) บอกว่าเมื่อ N ใหญ่ Hessian ที่ critical point ทั่วไปมี eigenvalue spectrum ที่มีรูปร่างแบบ **Wigner semicircle** — ครอบคลุมทั้งค่าบวกและค่าลบเสมอ

ความน่าจะเป็นที่ eigenvalues **N ตัว** จะบวกทั้งหมดลดลงแบบ **exponential ตาม N** ดังนั้น:
- N = 100 → โอกาสที่จะเป็น local minimum = น้อยมาก
- N = 1,000,000 → โอกาสแทบเป็นศูนย์

ในทางปฏิบัติ: **ใน high-dimensional landscapes critical points ส่วนใหญ่เป็น saddle ไม่ใช่ local minima ที่แย่**

### ผลที่สำคัญกว่า: landscape จัดตัวตาม loss level

Dauphin แสดงว่ามี **correlation** ระหว่าง loss value กับ "index" ของ critical point (fraction ของ eigenvalues ที่เป็นลบ):

- **Critical points ที่ loss สูง** → index สูง (เต็มไปด้วย saddles ที่ไม่ดี ซึ่งทิศที่ "ลง" มีอยู่มากแต่ยังอยู่สูง)
- **Critical points ที่ loss ต่ำ** → index ต่ำ (ส่วนใหญ่เป็น minimum หรือ saddles ที่ใกล้ minimum)
- **Global minimum** → index = 0 (eigenvalues บวกทั้งหมด)

นั่นหมายความว่า landscape มีโครงสร้างแบบ **ยิ่งลึกยิ่งปลอดภัย**: ยิ่ง loss ต่ำ ยิ่งเจอ minimum มากขึ้น ยิ่ง loss สูง ยิ่งเจอ saddle หนาแน่น คุณไม่ "ตกหลุม" ที่แย่ — คุณเจอแค่ "ที่ราบ" รอบ saddles ที่อาจทำให้ช้า แต่ยังวิ่งลงต่อได้

### บทบาทของ noise: ช่วยหนี saddle

Saddle มีทิศที่ "ลงได้" (negative curvature directions) ถ้าเดินตาม gradient ปกติ คุณอาจวนอยู่บน **"plateau" รอบ saddle** นาน เพราะ gradient บนที่ราบ saddle ใกล้ศูนย์ ดูเหมือนว่า converge แล้วแต่จริงๆ แค่หยุดนิ่งชั่วคราว

noise ใน SGD (และ noise แอนะล็อกของเรา) **ผลัก** ระบบออกจากที่ราบ saddle ไปตาม "negative curvature direction" ที่ชัน ออกมาจาก saddle ไปได้เลย ตามทิศที่ลงต่อ

**สำหรับเรา:** นัยยะออกแบบสองข้อที่ concrete:

**ข้อ 1 — ไม่ต้องหา optimum จริงๆ:** local minimum ที่ loss ต่ำส่วนใหญ่ใกล้ global optimum ดังนั้นตาข่ายแอนะล็อกที่มี noise จะไม่มีวัน land เป๊ะที่ minimum แต่นั่นไม่สำคัญ แค่อยู่ในบริเวณ loss ต่ำก็เพียงพอ

**ข้อ 2 — analog noise ระหว่างเทรนเป็น saddle-escaping mechanism:** kT/C noise และ op-amp offset สุ่มรอบต่อรอบ ทำหน้าที่เดียวกับ SGD noise ใน digital ทุก noisy forward pass คือ "ลองเดินออกจาก plateau" ชิปแอนะล็อกจึงหนี saddle ได้โดยอัตโนมัติจากฟิสิกส์ ไม่ต้อง explicit รอดหรือ schedule learning rate schedule พิเศษ

ข้อนี้เชื่อมตรงกับ Bishop's theorem (`17`): noise ระหว่างเทรนไม่ใช่แค่ regularization — มันยัง **escape mechanism** ที่ทำให้ optimization ทำงานได้บน landscape จริงๆ

---

## มันจะ generalize ไหม? Flat Minima และการหลอมรวมสองเป้าหมายเข้าเป็นหนึ่ง

*Hochreiter & Schmidhuber, 1997; Keskar et al., 2017 ([arXiv 1609.04836](https://arxiv.org/abs/1609.04836)); SAM: Foret et al., 2020; SGD implicit regularization: Smith et al., 2021.*

### ชั้น 1: ทำไม flat ถึง generalize ดีกว่า (Hochreiter 1997)

Hochreiter กับ Schmidhuber ตั้งข้อสังเกตจาก intuition ง่ายๆ: test data ≠ training data เมื่อ distribution เปลี่ยน มันเหมือนว่า weights "ถูกรบกวนเล็กน้อย" ในทางนามธรรม

- **Sharp minimum** (หุบเขาแคบแหลม): loss พุ่งขึ้นทันทีถ้า weights ขยับนิดเดียว → เมื่อ test distribution เปลี่ยนนิด loss ก็พุ่งขึ้น → test performance แย่
- **Flat minimum** (หุบเขากว้างราบ): loss แทบไม่เปลี่ยนเมื่อ weights ขยับ → distribution shift ทำให้ loss เปลี่ยนนิดเดียว → test performance ดี

นั่นคือ: **ความแบนของ landscape รอบ solution = ความทนทานต่อ distribution shift = generalization**

### ชั้น 2: Keskar et al. 2017 — พิสูจน์เชิงประจักษ์ด้วย batch size

Keskar ทำ experiment ที่ elegant: เทรน ResNet บน CIFAR-10 ด้วย batch size ต่างๆ

ผลที่น่าตกใจ:
- **Small batch (256):** train accuracy 94.8%, **test accuracy 93.5%** → gap น้อย → generalize ดี
- **Large batch (8192):** train accuracy **95.2%** (ดีกว่าด้วยซ้ำ!), test accuracy **91.2%** → gap ใหญ่ → generalize แย่

Keskar วัด "sharpness" ด้วย eigenvalue ที่ใหญ่สุดของ Hessian: large-batch solution มี sharpness สูงกว่า small-batch ถึง **10x หรือมากกว่า**

ทำไม batch size ต่ำถึง generalize ดีกว่า? **เพราะ noise ใน gradient** — small batch คำนวณ gradient จากข้อมูลน้อย จึงมี noise สูง noise นี้ **ผลัก solution ออกจาก sharp minimum** (เพราะมัน "สั่น" มากพอที่จะกระโดดออกจากหุบเขาแคบ) แล้วไปจอดใน flat minimum ที่ยังใช้ได้ Large batch มี noise น้อย ไม่สั่น → ลงจอดใน sharp minimum ได้ง่าย → test performance แย่

### ชั้น 3: SAM — อัลกอริทึมที่หา flat minimum โดยตรง (Foret 2020)

SAM (Sharpness-Aware Minimization) ไม่ได้แค่ hope ว่า SGD noise จะหา flat minimum โดยบังเอิญ มัน **explicit หาโดยตรง** ด้วยสองขั้น:

**ขั้น 1 — หา "worst-case perturbation" ε\*:** หา perturbation ε ขนาดไม่เกิน ρ ที่ทำให้ loss **สูงสุด**:
$$\epsilon^* = \rho \cdot \frac{\nabla_w L}{\|\nabla_w L\|}$$
(เดินไป ρ หน่วย ตาม gradient — ทิศที่ loss ชันที่สุด)

**ขั้น 2 — compute gradient ที่ worst-case point แล้ว update:** คำนวณ gradient ที่ w + ε\* แล้ว update weights ไปตามทิศนั้น:
$$w \leftarrow w - \eta \cdot \nabla_w L(w + \epsilon^*)$$

ผลคือ SAM optimize **"loss ที่แย่สุดในรัศมี ρ รอบ w"** แทนที่จะ optimize loss ที่ w เอง ถ้า minimizer นี้อยู่ที่ w\* แปลว่าทุกจุดในรัศมี ρ รอบ w\* ก็มี loss ต่ำด้วย — นั่นคือ flat minimum โดยนิยาม

### ชั้น 4: ทำไม flat จึง formal generalize (PAC-Bayes)

มีการพิสูจน์ formal ผ่าน **PAC-Bayes theory**: generalization gap มีขอบเขตโดย KL-divergence ระหว่าง posterior (ที่เราได้จากเทรน) กับ prior (ที่เรากำหนดก่อน)

- **Flat minimum** → หลาย weight values รอบๆ ให้ loss ต่ำ → effective "posterior" กว้าง ครอบคลุมพื้นที่มาก → KL divergence ต่ำ → generalization bound **แน่น**
- **Sharp minimum** → แค่จุดแคบๆ ที่ loss ต่ำ → posterior แคบ → KL divergence สูง → generalization bound **หลวม**

### การหลอมรวมที่งดงามที่สุดสำหรับโปรเจกต์นี้

ทีนี้ดูว่า "flat" *หมายความว่า* อะไรในเชิง weight perturbation: **minimum ที่แบนคือตัวที่การรบกวน weight แทบไม่เปลี่ยน loss** นั่นคือ *นิยามของความทนทานต่อการรบกวน weight เป๊ะๆ* ดังนั้น:

> **minimum ที่แบน = generalize ดี = รอดการรบกวน weight = รอด noise แอนะล็อก ทั้งหมดคือ *คุณสมบัติเดียวกัน***

**สำหรับเรา — นี่คือ insight สำคัญที่สุดในไฟล์นี้:** คุณไม่ต้อง optimize เพื่อ generalization *และแยกต่างหาก* เพื่อความทน noise — **คุณ optimize เพื่อความแบน แล้วได้ทั้งคู่ฟรี**

และสิ่งที่น่าทึ่งคือ analog noise ระหว่างเทรน ทำงานเหมือน SAM โดยไม่ได้ตั้งใจ:

- SAM: perturb weights ด้วย ε\* ที่คำนวณมา แล้วเทรนที่ worst-case point
- Analog chip: weights ถูก perturb โดย thermal noise ทุกรอบอยู่แล้ว ทุก forward pass เป็น "SAM step" ที่ได้จาก physics ฟรี

ดังนั้น analog noise ไม่ใช่แค่ Bishop regularization (flattens the mapping) แต่ยัง approximate SAM (explicitly seeks flat minima) ทั้งสองชี้ไปยัง flat minima จาก mechanism ต่างกัน แต่ผลเดียวกัน ความไม่สมบูรณ์ของชิปคุณ ถ้าเทรนสู้กับมัน จะดันคุณไปยัง minimum ที่ *พร้อมกัน* generalize ได้ดีที่สุดและทนทานที่สุด

---

## คุณ *ต้อง* เลือก inductive bias — No Free Lunch บังคับให้ซื่อตรง

*Wolpert & Macready, 1997 ([No Free Lunch Theorems for Optimization](https://ieeexplore.ieee.org/document/585893)); Wolpert, 1996 (supervised).*

### สิ่งที่ Wolpert พิสูจน์จริงๆ

กำหนดให้ "ปัญหา" คือฟังก์ชัน f: X → Y ถ้าเราสุ่ม f จาก **distribution สม่ำเสมอเหนือฟังก์ชันที่เป็นไปได้ทั้งหมด** แล้ว:

> สำหรับ algorithm การ search/optimization ใดๆ ค่าเฉลี่ยของ performance เหนือทุก possible problem จะเท่ากันสำหรับทุก algorithm ไม่มี algorithm ใดชนะโดยเฉลี่ย

พิสูจน์โดย symmetry argument: ถ้าทุกฟังก์ชันเป็นไปได้เท่ากัน ก็ไม่มีข้อมูลในผลลัพธ์เกี่ยวกับโครงสร้างของปัญหา ดังนั้น random search และ gradient descent จะ perform เท่ากันเฉลี่ย

### ทำไมมันไม่ใช่ nihilism แต่เป็นคำสั่ง

สมมติฐานหลักคือ "ทุกฟังก์ชันเป็นไปได้เท่ากัน" แต่โลกจริงไม่เป็นเช่นนั้น ข้อมูลธรรมชาติมี **structure** ที่ไม่สม่ำเสมอ:

- ภาพมี locality เชิงพื้นที่ (pixels ข้างกันมีความสัมพันธ์สูง) และ translation invariance
- เสียงมี temporal continuity
- ฟิสิกส์มี smoothness (ฟังก์ชันที่ต่อเนื่องและ differentiable)
- โลกที่สิ่งมีชีวิตอยู่อาศัยมี hierarchy, prediction, sparse causality

ถ้า data มี structure และ algorithm มี **inductive bias** ที่ตรงกับ structure นั้น algorithm นั้นชนะทุก algorithm อื่นบนปัญหาแบบนั้น trade-off คือมัน underperform บนปัญหาที่ไม่มี structure นั้น — แต่นั่นยุติธรรมดี

### Inductive biases ที่พิสูจน์แล้วว่าตรงกับ structure โลก

| Algorithm | Bias ที่สมมติ | ชนะบนปัญหาแบบ |
|-----------|--------------|--------------|
| Convolution | Translation invariance + spatial locality | Vision, audio |
| RNN/LSTM | Temporal structure + variable-length | NLP คลาสสิก |
| Transformer | All-pairs interaction + permutation eq. | Long-range dependencies |
| Residual | Near-identity mapping | Deep networks ทุกแบบ |
| **Bio-inspired substrate (เรา)** | Sparsity, locality, predictive, continuous weight | Tasks ที่สมองวิวัฒน์มาเพื่อทำ |

### สมองเป็น "proof by evolution" ที่แข็งที่สุด

สมองไม่ได้ถูก designed ด้วย gradient descent มัน evolved ผ่านล้านปีของ natural selection บน tasks จริงในโลกธรรมชาติ inductive biases ของสมอง (hierarchical prediction, sparsity, local learning, continuous memory) ถูก shaped by ข้อมูลจริงที่สิ่งมีชีวิตเจอมาตลอดวิวัฒนาการ

ดังนั้น substrate ที่ copy inductive bias ของสมอง ก็กำลัง copy "result of ล้านปีของ validation บน real data" ซึ่งเป็น argument ที่แข็งมากกว่า architecture ใดๆ ที่ designed มาจาก first principles

**สำหรับเรา — No Free Lunch บังคับให้ commit อย่างชัดเจน:**

เดิมพันของโปรเจกต์นี้คือ: **"inductive bias ของการคำนวณเชิงชีวภาพตรงกับโครงสร้างของโลกธรรมชาติ"** ซึ่งหมายความว่า:
- เราชนะบน tasks ที่มี locality, hierarchy, temporal continuity, sparse causality → ซึ่งคือ tasks ที่สมองจัดการได้ดี
- เราแพ้บน tasks ที่เป็น arbitrary lookup, random permutation, combinatorial search → และนั่นถูกต้องที่จะแพ้

ดังนั้น "ไม่ไล่ตาม external benchmark" ไม่ใช่การหนี ไม่ใช่ความถ่อมตน มัน **เป็น logical consequence ของ No Free Lunch** — benchmark ที่ไม่ตรงกับ inductive bias ของเรา ก็ไม่ควร win อยู่แล้ว การ commit บน bias นี้คือ **การซื่อตรงกับทฤษฎี** ไม่ใช่การยกธงขาว

---

## รูปร่างของคำตอบ (ไฟล์นี้)

พื้น optimization ที่รองรับ "มันเรียนรู้ได้" มีสี่เสา:

**(1) NTK — over-parameterization พิสูจน์ได้ว่าลู่เข้า:** ตาข่ายกว้างแทบไม่ขยับ weights → linearization → kernel regression → convex → global convergence ดังนั้น Scap เพิ่มทำให้เทรน *ง่ายขึ้น* เชิงทฤษฎี ไม่ใช่แค่ปลอดภัยเชิง empirical แต่ไม่กว้างจนเข้า pure kernel regime (ซึ่งไม่เรียน features)

**(2) Saddle points — คุณจะไม่ติดกับดัก:** RMT บอกว่า critical points ในมิติสูงส่วนใหญ่เป็น saddle ไม่ใช่ local minimum ที่แย่ landscape จัดตัวตาม loss level (loss สูง → saddle; loss ต่ำ → minimum) และ analog noise ระหว่างเทรน ช่วยหนี saddle ได้โดยอัตโนมัติ — เปลี่ยน bug เป็น feature

**(3) Flat minima — generalization = ความทน noise = ความแบน:** Keskar แสดงว่า noise ใน gradient → flat minimum → generalize ดี Flat minimum นิยามว่า "weight perturbation ไม่เปลี่ยน loss" ซึ่งเป็น *นิยามเดียวกัน* กับ "ทน analog noise" SAM ทำ explicit; analog noise ทำ implicit ทั้งคู่ชี้ไปยัง flat minimum เป็น *เป้าเดียว* ที่ให้ generalization + robustness พร้อมกัน

**(4) No Free Lunch — bias เป็นเดิมพัน ไม่ใช่คำกล่าวอ้างสากล:** inductive bias ที่ชีวภาพเป็น "proof by evolution" ว่าตรงกับโครงสร้างของโลกจริง ทฤษฎีบทบอกให้ commit อย่างชัดเจน ซื่อตรงเรื่อง scope และปล่อยให้ tasks ที่ bias ไม่ตรงแพ้ได้โดยไม่อาย

เสาทั้งสี่ + double descent (`13`) รวมกันเป็น: over-provision ได้สบาย ปล่อยให้ noise (analog และ SGD) หา flat minima เป็นเจ้าของ bias ของตัวเอง และ convergence จะเป็นเรื่องปกติ ไม่ใช่โชค
