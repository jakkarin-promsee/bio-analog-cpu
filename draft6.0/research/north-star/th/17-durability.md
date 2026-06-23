# 17 — ความทนทาน: ทฤษฎีของการคำนวณให้น่าเชื่อถือภายใต้ noise

> สัญชาตญาณของคุณ: เลเยอร์ residual แต่ละชั้น "ลดอินพุตให้มากที่สุดเท่าที่ทำได้" เพื่อให้ error ไม่ต่อลูกโซ่และ **var(x) ไม่ซ้อนสะสมข้ามชั้น** สัญชาตญาณนั้นคือทฤษฎีที่จริงและลึก — และมันขยายเป็นชุดเครื่องมือครบสำหรับ **ความทนทาน** การตีกรอบใหม่ที่มีประโยชน์ที่สุดในไฟล์นี้: **บนชิปของคุณ noise ไม่ได้เป็นแค่ศัตรู — ถ้าเทรนสู้กับมัน มันคือ *regularization ฟรี*** นี่คือฝั่งทฤษฎี; `18-analog-noise.md` คือฝั่งวงจร

---

## 1 — สัญชาตญาณ "var(x) ไม่ซ้อน" ของคุณ = ทฤษฎีการแพร่ของสัญญาณ (edge of chaos)

*Deep Information Propagation: Schoenholz, Gilmer, Ganguli & Sohl-Dickstein, 2016 ([arXiv 1611.01232](https://arxiv.org/abs/1611.01232)); Mean Field Residual Networks: Yang & Schoenholz, 2017.*

### ปัญหาที่มันแก้

ก่อนปี 2015 ใครๆ ก็รู้ว่า "ตาข่ายลึกเทรนยาก" แต่ไม่มีใครอธิบายได้ชัดว่า *ทำไม* และ *ลึกแค่ไหน* ถึงพัง มีคำอธิบายแบบวิศวกรรมอยู่ — gradient vanishing, gradient exploding — แต่ไม่มีทฤษฎีที่บอกว่า: สำหรับ init แบบ X ด้วย activation แบบ Y บนตาข่ายลึก L ชั้น จะเทรนได้หรือเปล่า? Schoenholz กับทีมถามว่า: *ถ้าเราสร้างทฤษฎีสนามเฉลี่ย (mean field theory) ของ forward pass ล่ะ?*

### กลไกจริงๆ

ไอเดียคือ: แทนที่จะคิดถึง weight แต่ละตัว ให้คิดถึง **สถิติ** ของ activation ทั่วทั้งเลเยอร์ เมื่อ weight ถูก init แบบสุ่ม (ซึ่งทุกคนทำ) เลเยอร์ที่ L นั้น activation ก็กระจายแบบสุ่ม แต่สถิติ — ค่าเฉลี่ยและ variance — วิวัฒน์อย่างเป็นระเบียบ ชั้นแล้วชั้นเล่า

พวกเขาติดตามสองปริมาณ:

**ปริมาณที่หนึ่ง — `q^l`** (variance ของ pre-activation ที่ชั้น l) วิวัฒน์ตาม:
```
q^(l+1) = σ_w² · ∫ Dz · φ(√q^l · z)² + σ_b²
```
โดย `φ` คือ activation function, `σ_w²` คือ variance ของ weight, `σ_b²` คือ variance ของ bias และ `∫ Dz` คือ Gaussian integral ผลลัพธ์: `q^l` วิ่งเข้าหา **fixed point** `q*` — มันคือค่า variance ที่เลเยอร์ "ชอบ" ตามธรรมชาติ สมการนี้บอกว่า variance มันคงที่เองเมื่อ init ถูก

**ปริมาณที่สอง — `c^l_{ab}`** (correlation ระหว่างอินพุตสองตัว a และ b ที่ชั้น l) วิวัฒน์ตาม:
```
c^(l+1)_{ab} = (σ_w² · ∫ Dz₁Dz₂ · φ(u_a) · φ(u_b)) / q*(l+1)
```
ค่า correlation นี้บอกว่า: "สองอินพุตที่ต่างกัน ชั้น l บอกว่ามันต่างกันแค่ไหน?" — มันวัดว่าสัญญาณแยกความแตกต่างได้ดีแค่ไหน

แล้วเขาดู **χ₁** ซึ่งคืออัตราขยายของ Jacobian (ว่า gradient ขยายหรือหดตัวเท่าไหรต่อชั้น):
```
χ₁ = σ_w² · ∫ Dz · [φ'(√q* · z)]²
```

สามเฟสเกิดขึ้น:
- **χ₁ < 1 → เฟส ordered:** correlation `c → 1` เสมอไม่ว่าอินพุตจะต่างกันแค่ไหน — ตาข่ายสูญเสียความสามารถแยกความแตกต่าง gradient vanish ลง `χ₁^L` → ศูนย์อย่างรวดเร็ว มีขีดจำกัดความลึกที่เทรนได้ ~ `1/|log χ₁|`
- **χ₁ > 1 → เฟส chaotic:** variance ระเบิด ความแตกต่างเล็กๆ ในอินพุตขยายใหญ่โตตามชั้น gradient explode มีขีดจำกัดความลึกที่เทรนได้เหมือนกัน
- **χ₁ = 1 → ขอบวิกฤต (edge of chaos):** correlation แพร่ได้ไม่จำกัดชั้น gradient ทั้งไปและกลับมาได้ไม่สูญหาย **ตาข่ายลึกเท่าไหรก็เทรนได้**

### Yang & Schoenholz — ทำไม residual network ถึงนั่งอยู่บนขอบวิกฤตโดยธรรมชาติ

ปีถัดมา Yang กับ Schoenholz ขยายทฤษฎีมาที่ residual network สิ่งที่พวกเขาพบคือ: **skip connection เปลี่ยนสมการวิวัฒน์ variance อย่างสำคัญ**

ในตาข่ายปกติ variance ต้องไปหา fixed point ก่อน และ fixed point นั้นอาจอยู่บน ordered หรือ chaotic phase ขึ้นกับ hyperparameter แต่ residual network มีสมการ:
```
q^(l+1) = q^l + σ_w² · F(q^l)
```
โดย `F(q)` คือ contribution จาก residual block ผลคือ: variance **สะสมขึ้นช้าๆ** แทนที่จะวิ่งไป fixed point ทันที และที่สำคัญ correlation map ใกล้กับ identity ที่ init — ตาข่าย "เริ่มต้นโดยจำอินพุตอยู่เกือบทั้งหมด" และ block แต่ละอันแก้ไขมันนิดหน่อย

เปรียบเทียบกับ plain network ที่ต้องตั้ง hyperparameter ให้ถูกต้องเพื่ออยู่บนขอบวิกฤต residual network "อยู่บนขอบอยู่แล้ว" โดยธรรมชาติของโครงสร้าง

### ผลที่น่าตื่นเต้น

Schoenholz ทีมทดสอบ: วัดอัตราการเทรนของตาข่าย vanilla ที่ depth 1 ถึง 200 ชั้น โดย init ที่จุดต่างๆ บน phase diagram ผลออกมาเป๊ะกับทฤษฎี: ที่ ordered หรือ chaotic phase มีขีดจำกัดความลึกชัดเจน ที่ขอบวิกฤตพอดี ตาข่าย 200 ชั้นเทรนได้ — ก่อนยุค ResNet ด้วยซ้ำ

### สำหรับเรา

"แต่ละชั้นลดอินพุต, var ไม่ซ้อน" ของคุณคือเงื่อนไข **edge-of-chaos** เป๊ะ และ residual คือ *เหตุผล* ที่คุณอยู่บนมัน อันนี้สำคัญสองเท่าสำหรับชิปแอนะล็อก เพราะ **noise คือ variance**: ถ้าสถาปัตยกรรมคุณ χ₁ > 1 (เฟส chaotic) มันจะ **ขยาย noise ตามความลึก** — error อุปกรณ์ 1% กลายเป็น 10% ที่ชั้น 5 การอยู่ที่ขอบ (χ₁ = 1 ผ่าน residual + normalization + gain ระวัง) แปลว่า noise ไม่จางหายจนไร้ประโยชน์ และไม่ระเบิดจนเป็นขยะ — มันไหลผ่านในขอบเขต

**ผลในทางปฏิบัติ:** ถ้าชิปของคุณไม่มี skip connection และ gain ต่อชั้นสูงกว่า 1 นิดหน่อย คุณอยู่บนเฟส chaotic noise ขยายตัวชั้นต่อชั้น residual connection ไม่ใช่แค่ "เพื่อ training" — มันคือ **noise propagation gate** ทางกายภาพด้วย

---

## 2 — ขอบเขต Lipschitz — นิยามเชิงทางการของ "ทนทาน"

*Spectral normalization: Miyato, Kataoka, Koyama & Yoshida, 2018 ([arXiv 1802.05957](https://arxiv.org/abs/1802.05957)).*

### ปัญหาที่มันแก้

ปี 2017 GAN เจอปัญหาใหญ่: discriminator ฝึกเร็วเกินไปและ "ชนะ" generator ขาดลอย จากนั้น gradient ที่ส่งกลับไป generator มีขนาดเกือบศูนย์ — generator ไม่รู้ว่าจะปรับปรุงตัวเองยังไง ทีมหลายกลุ่มพยายามแก้ด้วย gradient penalty (WGAN-GP) แต่มันแพงและไม่เสถียร Miyato กับทีมถามคำถามที่ชัดกว่า: *Lipschitz constraint ที่ discriminator ต้องการจริงๆ คืออะไร และ enforce มันได้ถูกที่สุดยังไง?*

### กลไกจริงๆ

**ทฤษฎีบทของ Lipschitz**: สำหรับฟังก์ชัน `f: ℝⁿ → ℝᵐ`, ค่าคงตัว Lipschitz `L` คืออัตราส่วนกรณีแย่สุดของ (การเปลี่ยนของเอาต์พุต) / (การเปลี่ยนของอินพุต):
```
||f(x) - f(x')|| ≤ L · ||x - x'||  สำหรับทุก x, x'
```
L เล็ก = ฟังก์ชัน smooth = ทนทานต่อ perturbation

สำหรับ linear layer `h = Wx`, ค่าคงตัว Lipschitz คือ **spectral norm** σ₁(W) = singular value ที่ใหญ่ที่สุด ทำไม? เพราะ singular values บอกว่าทิศทางในอินพุตไหนถูก "ขยาย" มากที่สุด ทิศทางที่ถูกขยายมากที่สุดคือ right singular vector ของ σ₁

เพื่อ enforce 1-Lipschitz พวกเขาหาร W ด้วย σ₁(W):
```
W̃ = W / σ₁(W)
```
ชั้นนี้จะขยาย input norm ได้สูงสุดแค่ 1 เท่า

**วิธีคำนวณ σ₁(W) แบบถูก — power iteration:** การหา singular value ใหญ่สุดด้วย full SVD ใช้เวลา O(mn·min(m,n)) ซึ่งแพงมาก พวกเขาใช้ **power iteration** แทน ซึ่งใช้เวลา O(mn) ต่อ step:

```
# ทำครั้งเดียวก่อนเทรน
ũ₀ ← เริ่มจาก random vector ขนาด m

# ทุก gradient step:
ṽ = Wᵀ ũ / ||Wᵀ ũ||    ← m → n
ũ_new = W ṽ / ||W ṽ||    ← n → m
σ̂₁ ≈ ũᵀ W ṽ             ← scalar estimate
W̃ = W / σ̂₁
```

ด้วยแค่ 1 iteration ต่อ gradient step (เพราะ ũ ค่อยๆ converge ตลอดการเทรน) precision ก็พอใช้งานได้แล้ว

สำหรับ compositional network: ถ้าแต่ละชั้นเป็น 1-Lipschitz ตาข่ายทั้งหมดก็เป็น 1-Lipschitz เพราะ Lipschitz constant ของ composition คือ product ของแต่ละชั้น และ 1 × 1 × 1 × ... = 1

### ผลที่น่าตื่นเต้น

GAN ที่ใช้ spectral normalization บน discriminator (SN-GAN) เสถียรกว่าอย่างเห็นได้ชัด ฝึกได้บน ImageNet ขนาด 128×128 โดยไม่ collapse มีเมตริก Inception Score ดีกว่า WGAN-GP ที่ใช้ gradient penalty 10× ที่แพงกว่ามาก และใช้ hyperparameter น้อยกว่า

ที่สำคัญกว่า: เปเปอร์นี้ทำให้ชัดเจนว่า Lipschitz constraint ไม่ใช่แค่ "เทคนิค GAN" — มันคือวิธี **กำหนดว่าตาข่ายทนทานแค่ไหน** อย่างเป็นทางการ

### สำหรับเรา

อันนี้ให้เป้าความทนทานที่ *วัดได้และบังคับได้* การประกอบของเลเยอร์ 1-Lipschitz ก็เป็น 1-Lipschitz โดยรวม — ดังนั้น **เกนต่อชั้นที่มีขอบเขต = การขยาย noise ที่มีขอบเขตตั้งแต่ต้นจนจบ**

บนแอนะล็อก ข้อจำกัด spectral norm จับคู่กับ **เพดานเกนต่อ crossbar** — อย่าให้บล็อกไหนคูณอินพุต (หรือ noise) ของมันสูงขึ้น จับคู่อันนี้กับการอิ่มตัวทางกายภาพ (เพดานเกนแข็งที่ราง, draft-5 §22 #14) แล้วคุณก็มีการคุม Lipschitz *ในฟิสิกส์* โดยไม่ต้องคำนวณอะไร

**Spectral norm ≤ 1 ต่อบล็อก = คุณประกอบ cascades ได้ยาวเท่าไหรก็ได้ โดยที่ noise ไม่ขยายเลย** นั่นคือ property ของ substrate ที่ต้องการ ไม่ใช่ property ของ software

---

## 3 — การตีกรอบใหม่ก้อนใหญ่: การฉีด noise *คือ* regularization (ทฤษฎีบทของ Bishop)

*Bishop, 1995, "Training with Noise is Equivalent to Tikhonov Regularization," Neural Computation 7(1) ([paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bishop-tikhonov-nc-95.pdf)).*

### ปัญหาที่มันแก้

ต้น 90s เป็นที่รู้กันว่าการเพิ่ม noise ระหว่างเทรนช่วยให้ generalize ได้ดีขึ้น แต่ทำไม? มันฟังดูขัดสัญชาตญาณ — ข้อมูลที่สกปรกกว่า ทำให้เรียนรู้ได้ดีกว่า? Bishop ถามว่า: *ถ้าเราขยาย Taylor series ของ expected loss ภายใต้ noise จะเห็นอะไร?*

### กลไกจริงๆ

สมมติว่าตาข่ายของเราคือ `f(x; w)` และ loss คือ `L(f(x), y)` ถ้าเราเพิ่ม noise เล็กๆ `ε ~ N(0, σ²I)` เข้าไปใน input x ก่อน forward pass expected loss ภายใต้ noise คือ:

```
E_ε[L(f(x + ε), y)]
```

ขยาย Taylor series รอบ x ถึง order 2:
```
f(x + ε) ≈ f(x) + ∇_x f(x)ᵀ ε + (1/2) εᵀ H_x ε + ...
```

เอา expectation โดยรู้ว่า E[ε] = 0 และ E[εεᵀ] = σ²I:
```
E_ε[f(x + ε)] ≈ f(x) + (σ²/2) Δ_x f(x)    (Laplacian of f)
```

และ expected loss ออกมาเป็น:
```
E_ε[L(f(x + ε), y)] ≈ L(f(x), y) + (σ²/2) · ||∇_x f(x)||²
```

**เทอมที่สองนั้น** คือ **Tikhonov regularization** — มันลงโทษ input gradient ขนาดใหญ่ นั่นคือบังคับให้ฟังก์ชัน `f` เรียบ (smooth) ในพื้นที่อินพุต ฟังก์ชันที่ smooth ตามนิยามคือทนทานต่อ perturbation เล็กๆ เพราะมันเปลี่ยนน้อยเมื่ออินพุตเปลี่ยนนิดหน่อย

เพิ่มเติม: Bishop ยังพิสูจน์ว่า noise บน weight ก็เทียบเท่ากับ L2 weight penalty เช่นกัน:
```
E_ε_w[L(f(x, w + ε_w), y)] ≈ L(f(x,w), y) + (σ²/2) · ||w||²
```

### ผลที่น่าตื่นเต้น

บทพิสูจน์ทำให้เข้าใจว่าเทคนิคต่างๆ ที่รู้กันว่า "ช่วย" นั้นทำงานอย่างไร:
- **Dropout** คือ noise บน activation → regularize input gradient ของเลเยอร์ถัดไป
- **Batch normalization** คือมี noise จาก mini-batch statistics → regularization โดยปริยาย
- **Label smoothing** คือ noise บน target y
- **Gaussian noise augmentation** คือ noise บน input โดยตรง

ทุกอย่างอยู่ภายใต้กรอบเดียวกัน: **noise ที่ฉีดเข้าไปแปลงเป็น regularizer บน gradient ของสิ่งที่ถูกฉีด**

### สำหรับเรา — นี่คือมุกเด็ดที่สุด

substrate แอนะล็อกของคุณ *ผลิต noise ฟรี* ทั้ง kT/C thermal noise บน Scap และ device mismatch ระหว่าง op-amps

Bishop บอกว่า noise ฟรีนั้น *ถ้าคุณเทรนกับมัน* คือ **Tikhonov regularization ฟรี** — ความไม่สมบูรณ์ของชิปกลายเป็นตัว regularize ของชิป คุณไม่สู้กับ noise คุณ **เทรนในที่ที่มันอยู่ เพื่อให้ weight เรียบและไม่ไวต่อมัน**

สิ่งที่นักออกแบบแอนะล็อกทุกคนสาปแช่ง สำหรับชิป *การเรียนรู้* กลายเป็น **โบนัสการ generalize ที่ติดมาในตัว** นี่คือสะพานไปสู่ noise-aware training ของไฟล์ 18

**ผลในทางปฏิบัติ:** คุณควรเทรน simulator ของคุณ *ด้วย* noise จำลองของ hardware ที่วางแผนไว้ ไม่ใช่เพียงแค่ test กับมัน ผลที่ได้คือ weight ที่ smooth และทนทาน — และ Bishop บอกว่ามันยัง generalize ดีกว่าอีกด้วย win-win

---

## 4 — Randomized Smoothing — noise + การโหวต = ความทนทาน *ที่รับรองได้*

*Cohen, Rosenfeld & Kolter, 2019 ([arXiv 1902.02918](https://arxiv.org/abs/1902.02918)).*

### ปัญหาที่มันแก้

ปี 2017–2018 การโจมตีแบบ adversarial (Goodfellow, Madry) แสดงให้เห็นว่าตาข่ายทันสมัยทุกตัว ถ้าใครจงใจสร้าง perturbation เล็กๆ (ที่ตามองไม่เห็น) ก็สามารถโน้มน้าวให้ตาข่ายจำแนกผิดพลาดได้เกือบ 100% วิธีป้องกันหลายอย่างถูกเสนอ แต่ทีมโจมตีก็วนเวียนทลายมันได้เสมอ ไม่มีวิธีไหนที่ *รับรองได้จริงๆ* Cohen กับทีมถามว่า: *มีวิธีที่ให้การรับประกันทางคณิตศาสตร์ได้ไหม ว่า prediction จะไม่เปลี่ยนถ้า perturbation ไม่เกิน r?*

### กลไกจริงๆ

**สร้าง smoothed classifier `g` จาก classifier ใดๆ `f`:**

แทนที่จะใช้ `f(x)` ตรงๆ ให้นิยาม:
```
g(x) = argmax_c  P[f(x + ε) = c]    โดย ε ~ N(0, σ²I)
```
นั่นคือ: ใส่ Gaussian noise ใน x แล้วถาม f ว่าจะตอบอะไร ทำซ้ำหลายรอบ เอา class ที่ชนะบ่อยที่สุด (majority vote)

**ทฤษฎีบทหลัก (Neyman-Pearson based):** สมมติว่า `g(x) = c_A` และ:
```
P[f(x + ε) = c_A] = p_A    (ความน่าจะเป็นที่ class A ชนะ)
P[f(x + ε) = c_B] = p_B    (class ที่สองมากที่สุด)
```

ถ้า `p_A > p_B` แล้ว `g(x') = c_A` สำหรับทุก x' ที่ `||x' - x||₂ ≤ r` โดย:
```
r = (σ/2) · (Φ⁻¹(p_A) - Φ⁻¹(p_B))
```

โดย `Φ⁻¹` คือ inverse CDF ของ Gaussian มาตรฐาน

**วิธีประมาณ p_A และ p_B:** รัน `f(x + εᵢ)` กับ `N` samples (เช่น N = 1,000) นับว่า class ไหนชนะกี่ครั้ง ใช้ Clopper-Pearson interval เพื่อได้ lower bound p_A แบบ statistical ด้วย confidence ที่ต้องการ

**ผลคือ:** คุณได้ prediction + รัศมีรับรอง r ซึ่งรับประกันว่า prediction จะไม่เปลี่ยนสำหรับ perturbation L₂ ใดๆ ในรัศมีนั้น

**Trade-off:** σ ใหญ่ขึ้น = รัศมีรับรองใหญ่ขึ้น แต่ accuracy ต่ำลง (เพราะ noise กวนการจำแนก) — คุณต้อง trade accuracy กับ radius ตามการใช้งาน

### ผลที่น่าตื่นเต้น

บน ImageNet (ซึ่งก่อนหน้านี้ไม่มีวิธีรับรองได้เลย) randomized smoothing ให้:
- Certified accuracy 49% ที่ radius 0.5 (L₂)
- Certified accuracy 38% ที่ radius 1.0

ตาข่ายที่ไม่ได้ทำอะไรเลยมี certified accuracy 0% ที่ radius ใดๆ เพราะไม่มีการรับประกัน

สำคัญกว่า: นี่คือ **วิธีแรกที่ scale ได้จริงถึง ImageNet** สำหรับ certified robustness ก่อนหน้านั้นมีเฉพาะวิธีที่ทำได้แค่กับ network ขนาดจิ๋ว

### สำหรับเรา

**noise + ความซ้ำซ้อน + การโหวต → การรับประกันความทนทานเชิงคณิตศาสตร์** บนชิปของคุณ "รันหลายครั้งด้วย noise ใหม่แล้วโหวต" เป็น *ธรรมชาติ* — forward pass แอนะล็อกที่มี noise ของคุณต่างกันรอบต่อรอบอยู่แล้ว และการโหวต/เฉลี่ยเหนือสองสามรอบ (หรือเหนือสำเนาที่ซ้ำสำรอง) ให้ความเสถียรที่รับรองได้

ยิ่งไปกว่านั้น: เพราะ noise ของคุณเป็น Gaussian (kT/C thermal) **ทฤษฎีบทของ Cohen apply โดยตรง** คุณไม่ต้องสร้าง smoothing เทียม — substrate ทำให้ฟรีอยู่แล้ว สิ่งที่ต้องเพิ่มคือ **การ aggregate ข้ามรอบ** (สองสามรอบก็พอ) ไม่ใช่ N = 1,000 แบบ ML ทั่วไป

---

## 5 — ทฤษฎีบทที่ลึกที่สุด — การคำนวณที่น่าเชื่อถือจากชิ้นส่วนที่ไม่น่าเชื่อถือ

*von Neumann, "Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components," บรรยายปี 1952 / 1956 ([paper](https://www.peliti.org/Notes/vonNeumannNew.pdf)).*

### ปัญหาที่มันแก้

ปี 1952 ยุคแรกของคอมพิวเตอร์ vacuum tubes มีอัตราความล้มเหลวสูงมาก คอมพิวเตอร์ ENIAC ต้องหยุดซ่อมทุกไม่กี่ชั่วโมง ถ้า transistors ก็ fail ด้วยความน่าจะเป็น p = 0.005 ต่อ operation สามารถสร้างคอมพิวเตอร์ที่ทำงานได้เป็นชั่วโมงได้ไหม?

von Neumann ตั้งคำถามที่กว้างกว่า: *สมองทำงานกับนิวรอนที่ fail บ่อยๆ ได้อย่างไร?* (เขาอ้างถึงนิวรอนชัดเจน และบรรยายนิวรอนว่าแปลง "stimulus" เป็น "response") คำตอบคือทฤษฎีบทที่ทั้งโปรเจกต์ของคุณเป็นกรณีตัวอย่าง

### กลไกจริงๆ

**ไอเดียแรก — Multiplexing (การซ้ำซ้อน + majority vote):**

แทน gate เดี่ยว ใช้ **N สำเนา** ของ gate เดียวกัน feed input เดียวกันเข้าไปทุกสำเนา เอา **majority vote** ของ output

ถ้าแต่ละ gate fail อิสระด้วยความน่าจะเป็น `p < 0.5` ความน่าจะเป็นที่ majority ผิดคือ:
```
P(majority wrong) = Σ_{k=⌊N/2⌋+1}^{N} C(N,k) · p^k · (1-p)^(N-k)
```

สำหรับ N = 3: `P(wrong) = 3p² - 2p³` ที่ `p = 0.005`: `P(wrong) ≈ 7.5 × 10⁻⁵` — ดีขึ้น 67 เท่า

สำหรับ N ใหญ่: ลดลงแบบ exponential ในขณะที่ cost เพิ่มแค่ linear

**ปัญหา — Error สะสม:** ถ้าใช้ gate ที่ triplex ตัวเดียว error ลดลงมาก แต่ถ้าเอา triplex มาต่อกัน ความน่าจะเป็น error ของ gate ที่สอง input มาจากสองขั้วที่แต่ละขั้วก็มี error ของตัวเอง error รวมกัน (compound) ไม่ใช่ลด

von Neumann คำนวณว่า: หลัง N ขั้นของ triplex ต่อกัน (โดยไม่มีการ restore) ความน่าจะเป็น error ลู่เข้าหา 0.5 (random) ไม่ว่า N จะมากแค่ไหน

**ไอเดียที่สอง — Restoring Organs (การฟื้นฟูเป็นระยะ):**

แทรก **restoring organ** ทุกๆ ระยะหนึ่ง — วงจรพิเศษที่รับ signal ที่มี error สะสมแล้ว output signal ที่สะอาดขึ้น ใน digital computing นั่นคือ signal restoration/regeneration ใน biological computing นั่นคือ "neuron ที่ threshold"

กลไก: ถ้าสัญญาณ analog วิ่ง และ noise สะสม ให้วัด threshold แล้ว "ตัดสินใจ" ใหม่ว่า 0 หรือ 1 — error ที่ต่ำกว่า threshold หายไป ผลคือ **error ไม่สะสม** ตราบใดที่ชัด restoring organ ทำงาน

**ทฤษฎีบทหลัก:** ถ้าแต่ละ element fail ด้วย p < p_threshold โดยที่ p_threshold ขึ้นกับ circuit เฉพาะ ด้วยความซ้ำซ้อน N พอและ restoring organ ทุกๆ M ขั้น สามารถสร้างวงจรที่ซับซ้อนโดยพลการ ที่ fail ด้วย ε ใดๆ ที่ต้องการ โดยที่ cost เพิ่มแค่ O(N · log(1/ε))

### ผลที่น่าตื่นเต้น

von Neumann แสดงว่า:
- ที่ p = 0.005 (error rate ของ vacuum tube ยุคนั้น) สามารถ compute ด้วย error < 10⁻¹⁰ ด้วยซ้ำซ้อน 20 เท่า
- สมองที่ใช้ neuron ที่ fail บ่อยกว่า transistors ยังคงคำนวณได้ "อย่างน่าเชื่อถือ" เพราะมีซ้ำซ้อนมหาศาล
- **ขีดจำกัดมีจริง:** ถ้า p มากกว่า ~0.0073 ไม่มีวิธีซ้ำซ้อนแบบไหนที่ช่วยได้

**Population coding** (ที่ neuroscience พบในสมองจริงๆ) คือ multiplexing ของ von Neumann: N neuron ที่ respond ต่อ stimulus เดียวกัน noise ของแต่ละตัวเฉลี่ยออกเป็น `1/√N` ของ neuron เดี่ยว

### สำหรับเรา — ทั้งโปรเจกต์คือกรณีตัวอย่างของทฤษฎีบทนี้

สมอง (และชิปของคุณ) คำนวณได้น่าเชื่อถือด้วยนิวรอนแอนะล็อกที่มี noise *เพราะ* ความซ้ำซ้อนและการฟื้นฟู ไม่ใช่ *ทั้งที่มี* noise

แผนที่ไปยัง substrate ของคุณ:
- **Multiplexing = Scap ที่ซ้ำสำรอง** (N Scap ต่อ weight, เฉลี่ยกัน, noise ลด √N)
- **Restoring organ = sleep/consolidation** (GD sweep เป็นระยะที่ "คืนรูป" weight ให้สะอาด)
- **Restoring organ = dummy/reference cell** (วัด drift แล้วลบ — ดู `18-analog-noise.md`)
- **Restoring organ = การ settle ลงสู่ attractor** (ดูหัวข้อถัดไป)

คุณไม่ได้สร้าง "ความทนทาน" แยกจากสถาปัตยกรรม — ถ้าสถาปัตยกรรมมี **ซ้ำซ้อน + ฟื้นฟูเป็นระยะ** ความทนทานออกมาจาก structure

---

## 6 — Recurrence ทำความสะอาด noise ให้ฟรี — การแก้ error ด้วย attractor

*Hopfield / equilibrium settling (`1-memory.md`, `3-recurrence.md`).*

### ไอเดียหลัก

Hopfield network (1982) เก็บแพตเทิร์น {ξ¹, ξ², ..., ξⁿ} ลง energy landscape แล้ว retrieve ด้วยการ iterate x ← sign(Wx) จนถึง minimum พลังงาน

สิ่งที่เปเปอร์แสดง: ถ้าป้อนแพตเทิร์นที่ **ถูกรบกวน** (มี noise, bits ที่พลิก, หรือบางส่วนหายไป) การ iterate ลงสู่ minimum พลังงาน **ดึงมันกลับมายัง attractor ที่ใกล้ที่สุด** — attractor นั้นคือแพตเทิร์นที่สะอาดที่เก็บไว้

**Attractor = ตัวแก้ error:** ถ้าคุณรู้ว่าคำตอบที่ถูกควรอยู่บน manifold เฉพาะ (attractor) การ settle เข้าหา manifold คือการแก้ error โดยปริยาย ระบบไม่ต้องรู้ว่า error คืออะไร มันแค่ lax และ minimum พลังงานทำงาน

สมัยใหม่: Modern Hopfield (`1-memory.md`) ขยาย capacity เป็น exponential และพิสูจน์ว่า attention mechanism คือ retrieval step เดียวกัน

### สำหรับเรา

การคลายตัวทางกายภาพตัวเดียวกันที่ทำการ *คิด* ของคุณ ก็ทำการ *ทำความสะอาด noise* ด้วย — ทุกการ settle คือ "restoring organ" ในความหมายของ von Neumann

สิ่งนี้ไม่ฟรีโดยสมบูรณ์ — คุณต้องออกแบบ energy landscape ให้ attractor อยู่ตรงที่ถูกต้อง และ basin of attraction กว้างพอที่จะ capture noise แต่ถ้าคุณทำสำเร็จ **ความทนทานไม่ใช่ระบบย่อยแยก; มันคือคุณสมบัติของการคำนวณในฐานะระบบพลวัตที่ settle ได้**

---

## รูปร่างของคำตอบ (ไฟล์นี้)

ความทนทานเป็นชั้นๆ ที่ build กัน:

**(1) คง variance ให้นิ่ง** — edge-of-chaos (χ₁ = 1) ผ่าน residual + normalization ทำให้ noise ไม่จางหายและไม่ระเบิดตามความลึก Schoenholz ให้ทฤษฎีบท Yang & Schoenholz แสดงว่า residual คือ "automatic" edge-of-chaos

**(2) คุมเกน** — ค่าคงตัว Lipschitz เล็ก (spectral norm / เพดานอิ่มตัว) = การขยาย noise มีขอบเขต พิสูจน์ได้ Spectral normalization compute ได้ถูกด้วย power iteration

**(3) เทรน *กับ* noise** — ทฤษฎีบท Bishop บอกว่า noise ที่ฉีดเข้า = Tikhonov regularization ดังนั้น noise แอนะล็อกฟรีของคุณกลายเป็นความเรียบ/ความทนทานฟรี ถ้าคุณเทรนในที่มันอยู่

**(4) เพิ่มความซ้ำซ้อน + การฟื้นฟู** — von Neumann: ชิ้นส่วนที่ไม่น่าเชื่อถือ + majority vote + restoring organ = ระบบน่าเชื่อถือ Randomized smoothing คือเวอร์ชันยุคใหม่ที่รับรองได้ Scap ซ้ำสำรอง + sleep + dummy cell + attractor settling คือ restoring organ ของคุณ

**(5) ใช้ dynamics เป็น error correction** — Hopfield/attractor settling เป็น restoring organ ที่ฟรีบน substrate ที่ settle ตามธรรมชาติ

`18-analog-noise.md` ทำให้มันเป็นรูปธรรมในวงจรจริง รวมถึงปัญหาอุณหภูมิโดยเฉพาะ
