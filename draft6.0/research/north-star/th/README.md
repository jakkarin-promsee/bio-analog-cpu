# `north-star/` — แฟ้มงานวิจัยดาวเหนือ (the north-star research dossier, beyond the numbered phases)

> **ไฟล์นี้คืออะไร** ดาวเหนือตัวจริงของโปรเจกต์ — อยู่เลยเฟสที่มีหมายเลข (เฟส 1–4 เสร็จแล้ว: โครงสร้าง · ความลึกรอบ 1 · ความลึกรอบ 2/เปลี่ยนกรอบ · การวัดความสามารถ; เฟส 5 = การปรับให้เหมาะสม) — คือ **สมองที่คิดได้** ซึ่งมี recurrence และเรียนรู้ไปตลอดชีวิต — เป็นวงลูประหว่าง prefrontal↔hippocampus ที่ซึ่ง *ความถูกต้องคือความรู้สึกที่ตัวมันสร้างขึ้นเอง (correctness is a self-generated feeling)* เรา**ตั้งใจยังไม่เขียนสเปกมัน** ("ทำปัญญาแบบง่าย ๆ ให้ได้ก่อน"; ดู `docs/essence/the-essence.md`) โฟลเดอร์นี้คือ **แผนที่ของดินแดน** เอาไว้ใช้ตอนที่เราไปถึงจุดนั้น — รวมทุกเปเปอร์ที่นิยม/เชื่อถือได้และควรรู้ เล่าเป็นเรื่องราว พร้อมบรรทัด **"สำหรับเรา (For us)"** กำกับในแต่ละอัน ครอบคลุมทั้ง **ฝั่งไอเดีย** (ทฤษฎี ประสาทวิทยา กรอบความคิด) และ **ฝั่งลงมือทำ** (วิธีที่สร้างได้จริงเป็นรูปธรรม)
>
> ไม่มีอะไรในนี้เป็น "การตัดสินใจ" มันคือเมนู ไม่ใช่ออเดอร์ที่สั่งไปแล้ว อ่านเพื่อจับทิศทาง แล้วเถียงกับมันได้เลย

---

## ไฟล์เหล่านี้ตอบคำถามของคุณอย่างไร

คุณถามมา 5 เรื่อง นี่คือไฟล์ที่ตอบแต่ละข้อ:

| คำถามของคุณ | ไฟล์ | คำตอบสั้น ๆ (ที่เถียงไว้ในไฟล์) |
| --- | --- | --- |
| "**hippocampus** ควรหน้าตาเป็นยังไง?" | [`1-memory.md`](1-memory.md) | เป็น **หน่วยความจำแบบเชื่อมโยง/ดึงคืน (associative / retrieval memory)** — ก็คือ LUT prototype store ของคุณที่โตเต็มวัย การเรียกคืนแบบระบุด้วยเนื้อหา (content-addressable) = attention = modern Hopfield |
| "**prefrontal cortex** ควรหน้าตาเป็นยังไง? ใช้โมเดลไหน?" | [`2-controller.md`](2-controller.md) | เป็น **พื้นที่ทำงานกลางที่จำกัดแบนด์วิดท์ + กลไก gating** ที่ถือไว้นิดเดียวแล้วไป query ส่วนที่เหลือ ไม่ใช่ตาข่ายใหญ่ก้อนเดียว แต่เป็น *ตัวประสานงาน (coordinator)* ของหลาย ๆ โมดูล |
| "ต้องเป็น **LSTM เต็มตัว** ไหม? recurrent แค่ไหน?" | [`3-recurrence.md`](3-recurrence.md) | **ไม่ ไม่ใช่ LSTM เป็นแกน** การ "คิดวนหลายรอบจนนิ่ง" คือการคำนวณแบบ **equilibrium / fixed-point** + **กลไกหยุดที่เรียนรู้ได้ (learned halt)** — ทั้งคู่เป็นธรรมชาติของแอนะล็อก |
| "พวกมัน **สื่อสารกัน** ยังไง?" | [`2-controller.md`](2-controller.md) + [`6-architectures.md`](6-architectures.md) | ใช้ **การ broadcast ผ่าน workspace ที่ใช้ร่วมกัน** + **อ่าน/เขียนผ่าน attention** การที่แบนด์วิดท์จำกัดคือ *ข้อดี* (มันบังคับให้แต่ละส่วนแตกความชำนาญ) |
| "**2 สมองพอไหม**? ต้องเพิ่มอีกไหม?" | [`6-architectures.md`](6-architectures.md) | **คงไม่ใช่แค่สอง — คิดเป็น ~4–6 บทบาท** ทุกข้อเสนอ cognitive-architecture ที่จริงจัง (LeCun, Thousand-Brains, SOAR) มีมากกว่านั้น แต่ให้เพิ่มบทบาทก็ต่อเมื่อมีความล้มเหลวจริง ๆ ที่เรียกร้องมัน |
| "อินพุตที่ **มี label น้อยแต่ไม่หลอกตัวเอง**?" | [`7-encoding.md`](7-encoding.md) | ทำนายใน **พื้นที่ representation ไม่ใช่อินพุตดิบ** (มันจะได้จำ noise ไม่ได้); เติม **พื้น variance + การลดสหสัมพันธ์ (decorrelation)** ไว้ชัด ๆ เพื่อกันการยุบตัว (collapse) ทั้งสองอย่างเป็นค่าสถิติของคาปาซิเตอร์แบบโลคอล |
| "**อะตอม** (Ganglion / ALU) ควรเป็นอะไร?" | [`8-atom.md`](8-atom.md) | สำหรับงาน time-series ควรเป็น **อะตอมแบบเวลาต่อเนื่อง (continuous-time atom)** (liquid neuron = องค์ประกอบ RC ที่มีค่าคงตัวเวลา (time-constant) เรียนรู้ได้) ฟิสิกส์ของคุณ *คือ* คณิตศาสตร์ตัวนั้นเอง |
| "คนอื่นเขาสร้าง **ลำดับชั้น (hierarchy)** ยังไง?" | [`9-hierarchy.md`](9-hierarchy.md) | ไม่ใช่กองซ้อนตายตัว แต่เป็น **วงลูปทำนายลง/ข้อผิดขึ้น (predict-down / error-up) แบบสองทิศ** ที่มี **การเห็นพ้องแบบไดนามิก (dynamic agreement)** และ **มิติเวลา** — นั่นคือสิ่งที่โครงร่างของ draft-5 ขาดไป |
| "**forward + เรียนรู้แบบเร็ว/realtime**?" | [`10-realtime.md`](10-realtime.md) | ทิ้ง BPTT ไป ใช้ **ร่องรอย forward แบบโลคอล × สัญญาณ broadcast** (e-prop) — ตัว eligibility trace ก็คือคาปาซิเตอร์รั่ว (leaky cap) ที่คุณมีอยู่แล้ว |
| "แต่ละบล็อกเห็นอินพุตแค่ **เสี้ยวเดียว** — มันคุ้มไหม? ทำ GD พังไหม? แล้ว **กำแพง ALU**?" | [`11-connectivity.md`](11-connectivity.md) + [`12-dataflow.md`](12-dataflow.md) | **คุ้ม (ถูกลง g เท่า), ไม่พัง GD (กลับทำให้การให้เครดิตเป็นโลคอล), และมีวิธีผสมที่ดีกว่า** สิ่งที่คุณคิดขึ้น = grouped/depthwise-separable conv; ผสมด้วย shuffle/butterfly (ลึกแค่ log) ไม่ใช่ clip แบบ dense |
| "**การบีบอัด (compression)** ที่ทำให้คำนวณในชิปได้?" | [`13-compression.md`](13-compression.md) + [`14-compression-methods.md`](14-compression-methods.md) | **คุณไม่ได้เอาตัวบีบอัดมาแปะ — การเรียนรู้ *คือ* การบีบอัดอยู่แล้ว (MDL)** สร้างตาข่ายจาก *โครงสร้าง* ที่บีบอัดในตัว (sparse + low-rank + แชร์ + superposed) มันเกิดมาเล็กตั้งแต่แรก สมมติฐานเรื่อง spare-capacity ของคุณ = superposition + lottery ticket ยืนยันแล้ว |
| "**convolution** ใช้กับ SCFF ได้ไหม? ควรใช้ไหม? บ่อยแค่ไหน?" | [`15-convolution.md`](15-convolution.md) | **ได้ — *สะอาดกว่า* ในแบบ unsupervised ด้วย — แต่ใช้เฉพาะที่ข้อมูลมีโครงสร้างเชิงพื้นที่/translation** (ภาพ ใช่; ตาราง ไม่ใช่) ใช้ conv เป็น front-end **จับคู่กับ channel-mix** ส่วน 'การ collapse' ใน Ganglion ของคุณ = 1×1 conv; เก็บไว้ |
| "**front-end แบบ retina + ทำนายภาพ**?" | [`16-vision.md`](16-vision.md) | **ทิศทางอนาคตไกลที่ถูกต้อง** — แต่ให้ทำนาย *representation* ของอนาคต ไม่ใช่ตัว pixel (ไม่งั้นมันจะไปจำลอง noise และหลอกตัวเอง) มันคือวงลูปเฟส 2 ที่เอากล้องมาติด |
| "เพิ่ม **ความทนทาน (durability)** / รับมือ **noise แอนะล็อก (อุณหภูมิ)**?" | [`17-durability.md`](17-durability.md) + [`18-analog-noise.md`](18-analog-noise.md) | **จับคู่วิธีแก้ให้ตรงกับ timescale ของ noise:** *ลบทิ้ง* สำหรับ drift ที่ช้า (differential / auto-zero — draft-5 ของคุณมีอยู่แล้ว), *เฉลี่ย* สำหรับ kT/C ที่เร็ว (คาป่าใหญ่ขึ้น + ทำซ้ำสำรอง) และ **เทรน *พร้อมกับ* noise** (Bishop: noise = regularization ฟรี) ส่วนการคุม variance ด้วย residual ของคุณ = edge-of-chaos |
| "แล้วมันจะ **ลู่เข้า / generalize / นิ่ง** ได้จริงไหม — และ *เพราะอะไร*?" | [`19-optimization.md`](19-optimization.md) + [`20-dynamics.md`](20-dynamics.md) | **ได้ พร้อมเหตุผล:** ตาข่ายที่กว้างพิสูจน์ได้ว่าลู่เข้า (NTK); อุปสรรคเดียวคือ saddle ไม่ใช่ minimum ที่แย่ (noise หนีออกได้); **flat minima ทั้ง generalize *และ* ทน noise** (เป้าเดียวกัน); dynamics แบบหดเข้า (contracting) พิสูจน์ได้ว่านิ่ง |
| "มี **หลักการเดียว** ที่อยู่ใต้ทั้งหมดนี้ไหม?" | [`21-energy.md`](21-energy.md) | **พลังงาน (Energy)** การอนุมาน = กลิ้งลงเขา; การเรียนรู้ = แกะสลักหุบเขา SCFF / memory / recurrence / ความรู้สึก / เสถียรภาพ *ล้วน* เป็นการไหลลงตามพลังงาน — และชิปแอนะล็อกของคุณรันมัน *ทางกายภาพ* Landauer: นิ่ง-ไม่-ลบ **คือ** เส้นทางที่ถูกที่สุด |

และเส้นด้ายที่ลึกที่สุด — **"ความถูกต้องคือความรู้สึก"** — ร้อยอยู่ใน [`4-signal.md`](4-signal.md) (สัญญาณเรียนรู้/หยุดที่สร้างขึ้นเอง) และ [`5-continual.md`](5-continual.md) (จะไม่หยุดเรียนรู้โดยไม่เน่าได้อย่างไร)

---

## ไฟล์ทั้งหมด — สองชั้น

แฟ้มนี้แบ่งเป็น **หกชั้น (A–F) บวกอีกสองไฟล์ที่ตัดขวางทุกชั้น** ไฟล์ **1–6** (A) คือ **ระบบการรู้คิด (cognitive system)** (สมองที่คิดได้ของเฟส 2) ไฟล์ **7–10** (B) คือ **ชั้น substrate** (ตัว *อะตอม*, การ *เข้ารหัส*, การ *ประกอบ*, *realtime*) ไฟล์ **11–12** (C) คือ **ชั้นการจัดวางทางกายภาพ** (connectivity และกำแพง ALU/dataflow) ไฟล์ **13–14** (D) คือ **ชั้นการบีบอัด** (ทำไมโมเดลถึงลงในชิปได้) ไฟล์ **15–16** เป็นพวก **ตัดขวาง / อนาคตไกล** (convolution; vision front-end) ไฟล์ **17–18** (E) คือ **ความทนทาน** (เอาตัวรอดจาก noise) ไฟล์ **19–21** (F) คือ **รากฐาน** (ทำไมมันถึงลู่เข้า นิ่ง และทำงานได้เลยตั้งแต่ต้น — พื้นที่รองรับทุกอย่าง) ชั้น B–F **กัดเข้ากับงาน draft-6.0 ที่กำลังสร้างอยู่ตอนนี้** ไม่ใช่แค่เฟส 2

**ชั้น A — ระบบการรู้คิด (เฟส 2):**

1. **[`1-memory.md`](1-memory.md) — hippocampus / คลังความจำระยะยาว** ทฤษฎี CLS, Neural Turing Machine, Differentiable Neural Computer, Memory Networks, Modern Hopfield, การดึงคืน (kNN-LM / RETRO), Fast Weights
2. **[`2-controller.md`](2-controller.md) — prefrontal / working memory / ตัวประสานงาน** Global Workspace Theory, Shared Global Workspace (Bengio), Recurrent Independent Mechanisms, the Consciousness Prior, PBWM gating
3. **[`3-recurrence.md`](3-recurrence.md) — วงลูป / "คิดจนกว่าจะนิ่ง"** Deep Equilibrium Models, Equilibrium Propagation, predictive coding, Adaptive Computation Time / PonderNet, Universal Transformer, LSTM/GRU (และทำไมถึงไม่เอามาเป็นแกน)
4. **[`4-signal.md`](4-signal.md) — สัญญาณการเรียนรู้ / "ความถูกต้องในฐานะความรู้สึก"** Free Energy / Active Inference, ความอยากรู้ & compression-progress, World Models, ตัว critic ที่เรียนรู้ได้
5. **[`5-continual.md`](5-continual.md) — ไม่หยุดนิ่ง / เรียนรู้ตลอดชีวิต** Elastic Weight Consolidation, Synaptic Intelligence, Deep Generative Replay, Progressive Networks, ปัญหา stability-plasticity dilemma
6. **[`6-architectures.md`](6-architectures.md) — จิตทั้งดวง / "2 สมองพอไหม?"** เส้นทาง H-JEPA ของ LeCun, System 1/System 2, Thousand Brains, SOAR & ACT-R

**ชั้น B — substrate (กัดเข้ากับงานที่สร้างอยู่ด้วย):**

7. **[`7-encoding.md`](7-encoding.md) — รูปร่างของอินพุต/เอาต์พุต & "อย่าให้มันหลอกตัวเอง"** VICReg, Barlow Twins, MAE vs I-JEPA, sparse coding / SDR, VQ-VAE, Information Bottleneck *(การ collapse + การเรียนทางลัด (shortcut learning) คือสองวิธีที่โมเดลใช้โกหก)*
8. **[`8-atom.md`](8-atom.md) — อะตอม / Ganglion & ALU** Kolmogorov-Arnold Networks, **Liquid Time-Constant Networks**, Neural ODEs, Capsules, การคำนวณแบบ dendritic, reservoir computing *(อะตอมที่เข้ากับ substrate ล้วนเป็นแบบเวลาต่อเนื่อง)*
9. **[`9-hierarchy.md`](9-hierarchy.md) — การประกอบ / ลำดับชั้นของสมอง** hierarchical predictive coding, GLOM, HTM, Slot Attention, Mixture-of-Experts, การโตแบบ greedy ทีละชั้น *(โครงร่าง draft-5 ของคุณ + วงลูป top-down, การเห็นพ้องแบบไดนามิก และเวลาที่มันขาดไป)*
10. **[`10-realtime.md`](10-realtime.md) — forward + เรียนรู้แบบเร็วและ realtime** RTRL, **e-prop**, reservoir computing, liquid networks, spiking/neuromorphic, State-Space Models / Mamba *(ทิ้ง BPTT; ร่องรอยโลคอล × สัญญาณ broadcast = การเรียนรู้แบบ online)*

**ชั้น C — การจัดวางทางกายภาพ / กำแพง ALU (ดินแดน draft-5 ของคุณ):**

11. **[`11-connectivity.md`](11-connectivity.md) — อินพุตโลคอล + การผสม** grouped/depthwise-separable convolution (**= Ganglion + translate clip ของคุณ**), channel shuffle, butterfly/Monarch matrices, Mixture-of-Experts, MLP-Mixer *(สิ่งที่คุณคิดคือทริกแกนกลางของ MobileNet; วิธีผสมที่ถูกกว่าคือลึกแค่ log/การสับเปลี่ยน ไม่ใช่ dense)*
12. **[`12-dataflow.md`](12-dataflow.md) — กำแพง ALU / spatial vs temporal** กำแพงหน่วยความจำ (memory wall), การแลกระหว่าง spatial-vs-temporal, analog crossbar MVM, systolic arrays *(Ganglion แบบสายตายตัวของคุณ = spatial dataflow; ทำ crossbar ให้เล็กด้วยการ grouping)*

**ชั้น D — การบีบอัด / ทำให้ลงในชิป (หัวข้อแกนกลางที่ทำให้ทุกอย่างเป็นไปได้):**

13. **[`13-compression.md`](13-compression.md) — การเรียนรู้ *คือ* การบีบอัด + สมมติฐาน spare-capacity ของคุณ** MDL / learning-is-compression, double descent, intrinsic dimension, Lottery Ticket, **superposition** *("task-cap / slack ที่แชร์กันข้ามงาน" ของคุณ = superposition + lottery ticket ยืนยันแล้ว; ความ sparse คือเงื่อนไขเบื้องต้น)*
14. **[`14-compression-methods.md`](14-compression-methods.md) — บีบอัดจริง ๆ ทำยังไง + สองกลไกของคุณ** Pruning / Deep Compression, knowledge distillation, low-rank / LoRA, weight-sharing / hashing, **DenseNet** (= กลไก A ของคุณ), supervised anchor (= กลไก B ของคุณ) *(อย่าสร้าง crossbar แบบ dense — สร้างแบบมีโครงสร้าง; เกิดมาบีบอัดแล้ว ไม่ใช่ไปบีบทีหลัง)*

**ตัดขวาง & อนาคตไกล:**

15. **[`15-convolution.md`](15-convolution.md) — convolution + SCFF (tier-1)** Conv-FF/SCFF (สะอาดกว่าในแบบ *unsupervised*), weight-sharing ในฐานะการบีบอัดขั้นสุด, ควรใช้ conv เมื่อไหร่/บ่อยแค่ไหน, และการ collapse ด้วย linear-projection ใน Ganglion ของคุณ (= 1×1 pointwise conv — **เก็บไว้** ตีกรอบใหม่เป็น channel-mix)
16. **[`16-vision.md`](16-vision.md) — retina / vision front-end (อนาคตไกล)** predictive vision, กฎ *ทำนาย-representation-ไม่ใช่-pixel*, การเรียนรู้แบบ developmental/curriculum *(vision front-end ก็คือวงลูปเฟส 2 ที่เอากล้องมาติด)*

**ชั้น E — ความทนทาน / เอาตัวรอดจาก noise:**

17. **[`17-durability.md`](17-durability.md) — ทฤษฎีของการคำนวณให้น่าเชื่อถือภายใต้ noise** การแพร่ของสัญญาณ/variance (edge of chaos = ข้อค้นพบเรื่อง residual ของคุณ), ขอบเขต Lipschitz, **การฉีด noise = Tikhonov regularization** (ความทนทานแบบฟรี), randomized smoothing, **von Neumann** สร้างของน่าเชื่อถือจากชิ้นส่วนที่ไม่น่าเชื่อถือ *(noise ถ้าเทรนสู้กับมัน คือ regularization ฟรี)*
18. **[`18-analog-noise.md`](18-analog-noise.md) — noise แอนะล็อก & ปัญหาอุณหภูมิ** อนุกรมวิธานของ noise แยกตาม timescale, การหักล้าง drift ที่ช้า (differential / chopper / auto-zero / dummy — **= §15 ของ draft-5 คุณ**), การปรับขนาดคาปเพื่อสู้ kT/C & การเฉลี่ย, การเทรนแบบรู้ noise *(noise ช้า ลบทิ้ง; noise เร็ว เฉลี่ย)*

**ชั้น F — รากฐาน (ทำไมมันถึงทำงานได้เลยตั้งแต่ต้น):**

19. **[`19-optimization.md`](19-optimization.md) — ทำไมการเรียนรู้ถึงลู่เข้า & generalize** NTK (กว้าง → ลู่เข้า), saddle points (ไม่ใช่ minimum ที่แย่), **flat minima = generalization = ทน noise**, การ regularize โดยปริยายของ SGD, No Free Lunch *(ใส่ capacity เกินได้สบาย; noise หา flat minima เจอ; เป็นเจ้าของ inductive bias ของตัวเอง)*
20. **[`20-dynamics.md`](20-dynamics.md) — ระบบแอนะล็อกของคุณจะนิ่งไหม?** การคำนวณในฐานะระบบพลวัต (dynamical system), เสถียรภาพแบบ Lyapunov, ทฤษฎี contraction, edge of chaos, attractor-ในฐานะ-การคำนวณ *(ทำให้ dynamics หดเข้าใกล้ ๆ ขอบ → ได้ทั้งการนิ่ง + ความทนทาน + ความจำพร้อมกัน)*
21. **[`21-energy.md`](21-energy.md) — มุมมองพลังงาน (บทสรุปยอดเขา)** การเรียนรู้แบบ energy-based รวม SCFF / Hopfield / EqProp / predictive-coding / ความรู้สึก / เสถียรภาพ เข้าด้วยกัน; + ขีดจำกัดเชิงอุณหพลศาสตร์ของ Landauer *(ชิปของคุณคือเครื่องปั้นพลังงาน (energy-shaping machine) ที่คำนวณด้วยการไหลลงตามภูมิทัศน์ที่มันไม่เคยลบ)*

---

## ถ้าจะอ่านแค่ห้าอย่าง

1. **Complementary Learning Systems** (`1-memory.md`) — *ข้อพิสูจน์* ว่าการมีหน่วยความจำเร็ว-sparse คู่กับหน่วยความจำช้า-ทั่วไป คือการแบ่งงานที่ถูกต้อง คุณสร้างไปแล้วครึ่งหนึ่ง (sleep + LUT)
2. **Shared Global Workspace** (`2-controller.md`) — คำตอบที่สร้างได้จริงของคำถาม "ชิ้นส่วนคุยกันยังไง"
3. **Deep Equilibrium Models** (`3-recurrence.md`) — ฝั่งลงมือทำของ "นิ่งลงสู่ fixed point" และมันเป็นธรรมชาติของแอนะล็อก
4. **Active Inference / Free Energy** (`4-signal.md`) — กรอบแม่บทของ "ความถูกต้องคือความรู้สึก" *และ* ของการตรวจสอบตัวเอง (ลงมือทำเพื่อลดความไม่แน่ใจของตัวเอง)
5. **"A Path Towards Autonomous Machine Intelligence" ของ LeCun** (`6-architectures.md`) — คำตอบที่ตีพิมพ์แล้วซึ่งสมบูรณ์ที่สุดของ "ต้องมีกี่สมอง และสมองไหนบ้าง"

---

## บทสังเคราะห์หนึ่งบท ก่อนจะดำดิ่งลงไป

เปเปอร์ทั้งหลายลู่เข้าหาภาพเดียวกัน ซึ่งตรงกับสัญชาตญาณของคุณอย่างน่าขนลุก และมัน **ไม่ใช่** "LSTM ที่ใหญ่ขึ้น":

- **ความจำเป็นแบบเชื่อมโยงและระบุที่อยู่ได้ เก็บไว้ *นอก* ตัวคำนวณที่เร็ว** (CLS, NTM/DNC, Hopfield) LUT ที่เป็น hippocampus ของคุณคือเมล็ดพันธุ์; "attention" ก็แค่การเรียกคืนตามความคล้ายเหนือมัน
- **การคิดคือการค่อย ๆ นิ่งลงแบบวนซ้ำ ไม่ใช่ feed-forward รอบเดียว** (DEQ, predictive coding, equilibrium prop) — ซึ่งฮาร์ดแวร์แอนะล็อกทำให้ *ฟรี* และเป็นสิ่งที่ทั้ง LSTM และ transformer พลาดไป
- **ตัวควบคุมตั้งใจให้เล็กและจำกัดแบนด์วิดท์** (global workspace) — มันถือไว้นิดเดียว ไป query หน่วยความจำ แล้ว broadcast บทสรุปออกไป ความขาดแคลนนี่แหละที่บังคับให้แต่ละส่วนแตกความชำนาญ
- **สัญญาณเรียนรู้/หยุดถูกสร้างขึ้นเองและยึดกับความจริง (grounded)** (active inference, ความอยากรู้) — นี่แหละ "ความถูกต้องคือความรู้สึก" เป๊ะ ๆ และมันต้องผูกอยู่กับ prediction-error ไม่งั้นมันจะยุบ
- **จิตหนึ่งดวงคือหลายบทบาท ไม่ใช่สองบทบาท** (LeCun, Thousand Brains) — แต่คุณ *โต* เข้าไปหามัน คุณไม่ได้เริ่มจากตรงนั้น

จุดสำคัญระดับเมตาที่ต้องพูดตรง ๆ: เฟส 2 เป็นปัญหา **cognitive architecture (สถาปัตยกรรมการรู้คิด)** และวงการนี้มีคำตอบที่ร่างไว้ *มากมาย* แต่ที่ทำเสร็จแล้ว *ศูนย์* ดังนั้นโฟลเดอร์นี้คือเข็มทิศ ไม่ใช่พิมพ์เขียว เลือกวงลูปที่เล็กที่สุดที่คิดได้ ยึดมันกับความจริง แล้วปล่อยให้ความล้มเหลวบอกชื่อโมดูลถัดไป — วิธีการของคุณเอง เล็งไปที่เป้าที่ใหญ่ที่สุด
