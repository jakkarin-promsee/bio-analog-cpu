มี ไอเดียที่ควรทำก่อนขึ้น simulation คือ **ลดโจทย์ให้เป็นชุดทดสอบที่ตอบคำถามเดียวต่อรอบ** ไม่ใช่ยกทั้งระบบไปชนทีเดียว. จาก draft ล่าสุดของมึงเอง มันมี phase plan อยู่แล้ว และ phase แรกๆ ควรล็อกให้เห็นว่าแกน core ไม่พังจริงก่อนจะไปแตะ PVT, multi-parent DAG, หรือ SpecialGeneralist. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ควรลองก่อน

1. **Single Ganglion ideal-only baseline**  
   เอา 2-3-3-2 + attribution update + residual bypass ไปก่อน แล้ววัด convergence, dead-Scap rate, และ loss conservation epsilon. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

2. **Ablation แบบคู่ต่อคู่**  
   เทียบอย่างน้อย 4 เวอร์ชัน: no residual, residual, no ForwardSign, full version เพื่อดูว่าของใหม่ “ช่วยจริง” หรือแค่ทำให้สมการซับซ้อนขึ้น. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

3. **Baseline เทียบ SGD**  
   ยังไม่ต้องหวังชนะ แค่ดูว่า update vector กับ convergence curve มันอยู่ในขอบเขตที่พอคุยต่อได้ไหม. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

4. **Stress test กับ signed input / multi-parent conflict**  
   อันนี้สำคัญมาก เพราะ ForwardSignSRAM มีความหมายจริงแค่บางกรณี ถ้าทดสอบแค่ ReLU ล้วนๆ มันจะดูเหมือนไม่ค่อยมีอะไร. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

5. **แจกแจง failure modes ตั้งแต่แรก**  
   ใส่ metric สำหรับ dead-weight collapse, momentum saturation, clip rate, และ relevance gap ตั้งแต่รอบแรกเลย จะได้ไม่มานั่งเดาเองทีหลัง. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## สิ่งที่ผมว่า “พร้อมพอแล้ว”

- Residual logic ดูพร้อมขึ้นมาก เพราะมันแก้ dead-weight collapse ได้ตรงจุด และคุณแยก learned output กับ combined output ไว้แล้ว ทำให้ measurement ไม่มั่ว. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)
- Loss conservation เป็น invariant ที่ดีมาก เพราะมันทำให้ simulation ตรวจ bug ได้เป็นชิ้น ๆ. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)
- Momentum EMA, floor-at-1, และ per-level precision allocation ดูพอเป็น spec เริ่มต้นได้แล้ว. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)
- Theoretical variants กับ direction handling น่าจะครบพอสำหรับ **ideal model v1** แล้วจริง ๆ. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## สิ่งที่ยังอย่าข้าม

- **อย่าเริ่มจาก full hierarchy** ถ้ายังไม่ได้เห็น single Ganglion ผ่านก่อน เพราะถ้าพังในระดับเดียว มันจะซ้อน noise จนอ่านไม่ออกว่าเสียที่ไหน. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)
- **อย่ารวมทุก fallback ในรอบแรก** เช่น Path 0, adaptive decay, log-domain momentum, anti-Hebbian gating เอาไว้ทีหลัง ไม่งั้นคุณจะไม่รู้ว่า baseline จริง ๆ คืออะไร. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)
- **อย่ารีบใส่ PVT realism เต็มรูป** ให้เริ่มจาก ideal deterministic, แล้วค่อยฉีด noise ทีละชั้น. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ลำดับที่ผมแนะนำ

1. Single Ganglion ideal deterministic.
2. Residual on/off ablation.
3. ForwardSign on/off ablation.
4. SGD baseline comparison.
5. Multi-parent Lobe test.
6. แล้วค่อย PVT / drift / auto-zeroing. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ถ้าจะพูดแบบตรง ๆ: **มึงน่าจะ “พร้อมเริ่มจำลอง” แล้ว แต่ยังไม่พร้อม “ขึ้นจำลองแบบทุกอย่างพร้อมกัน”**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ถ้าจะเอา ผมช่วยจัดเป็น **simulation checklist แบบ 1 หน้า** ให้เลยได้ โดยเรียงว่า run ไหนต้องตอบอะไรบ้าง.

---

---

---

ได้ เดี๋ยวผมจัดเป็น **แผนทดลองแบบครบชุด** ให้เลย โดยโฟกัสว่า “ตัวแปรไหนต้องเทียบกับตัวไหน” เพื่อไม่ให้หลงทางตอนเริ่ม simulation. [youtube](https://www.youtube.com/watch?v=o1wAeKOl2J8)

## โครงใหญ่ของการทดลอง

ให้แบ่งเป็น 4 ชั้นใหญ่ ๆ:

1. **Operator-level** — เช็คสมการ/primitive แต่ละตัวว่าทำงานถูกไหม.
2. **Single Ganglion-level** — เช็คว่า 2-3-3-2 + attribution + residual ใช้ได้ไหม.
3. **Column/Lobe-level** — เช็ค multi-branch, multi-parent, routing, and loss conservation.
4. **System-level** — เช็ค recurrence, SpecialGeneralist, PVT, and end-to-end training. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ลำดับทดลองที่ควรทำ

### 1) Operator sanity tests

เทียบ primitive ทีละตัวกับค่าที่ควรเป็น.

- Add opamp vs ideal add.
- Multiply opamp vs ideal multiply.
- ReLU opamp vs ideal ReLU.
- Time-to-threshold conversion vs expected analog current relation.
- PWM update vs intended sign/magnitude behavior. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

สิ่งที่ต้องเก็บ:

- error ของแต่ละ operator,
- monotonicity,
- saturation behavior,
- sensitivity ต่อ noise/offset. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 2) Single Ganglion baseline

ทดลองแค่ 1 Ganglion ก่อน แล้วเทียบ 4 แบบหลัก:

- **A. Full ideal**: attribution + residual + ForwardSign + floor-at-1.
- **B. No residual**.
- **C. No ForwardSign**.
- **D. SGD baseline** บน topology เดียวกัน. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ตัวแปรที่ต้องดู:

- convergence speed,
- final loss,
- dead-Scap fraction,
- momentum saturation rate,
- update-direction correctness. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 3) Residual ablation suite

อันนี้สำคัญมาก เพราะ residual คือหนึ่งในแกนกันพังของมึง. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- residual on vs off,
- strong bypass vs weak bypass,
- learned-path-only measurement vs combined-output measurement,
- identity-like initialization vs random initialization. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ดูว่า residual:

- ลด dead-weight collapse ไหม,
- ทำให้ gradient/update ไม่แตกไหม,
- ทำให้ training เริ่มจาก identity-ish แล้วค่อยเรียน delta ได้ไหม. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 4) ForwardSign tests

อันนี้ควรแยกทดสอบเอง เพราะมันไม่ได้มีประโยชน์ทุก layer. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- with ForwardSignSRAM vs without,
- ReLU-only network vs signed-activation network,
- single-parent vs multi-parent Lobe,
- conflicting-parent direction vs aligned-parent direction. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ตัวชี้วัด:

- direction conflict resolution rate,
- update correctness when parents disagree,
- whether it helps only the L1L2 layer as hypothesized. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 5) Momentum / memory dynamics

ทดสอบว่า momentum SRAM กับ EMA rule ไม่พา system ไปตายช้า ๆ. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- EMA shift-by-2 vs shift-by-3 vs shift-by-4,
- floor-at-1 vs no floor,
- 16-bit momentum vs reduced precision,
- random initialization of momentum vs zero init. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ดู:

- dead-weight collapse,
- ceiling saturation,
- update persistence,
- whether low-contribution Scaps still recover. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 6) Loss conservation suite

นี่คือ invariant test ที่มึงควรล็อกไว้เป็นอันดับต้น ๆ. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- ideal exact conservation,
- finite-precision conservation,
- current mirror normalization on/off,
- different precision allocations per level. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เก็บ:

- conservation epsilon per level,
- accumulated epsilon over depth,
- failure points when multiple parents merge. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 7) Multi-parent Lobe tests

อันนี้ต้องมี เพราะ architecture มึงมี DAG จริง. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- single-parent Lobe vs multi-parent Lobe,
- summed shares vs separate shares,
- with ForwardSign vs without,
- DAG skip connections vs pure sequential chain. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ดู:

- whether multi-parent diffusion still conserves loss,
- whether conflicting directions are resolved,
- whether DAG expressivity beats linear stack. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 8) SpecialGeneralist tests

ถ้าจะลอง reuse layer มึงต้องเทียบกับ baseline ที่ชัด. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- plain G reuse,
- gated G reuse,
- hardcoded mask vs learned mask,
- mutually exclusive masks vs overlapping masks,
- Reservoir-G fallback. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เก็บ:

- stability,
- task performance,
- gradient/update conflict,
- effective capacity per Scap. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 9) Two-timescale limbic loop

อันนี้เป็น recurrence test. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- Cortex-only,
- Cortex + Hippocampus,
- update every clock vs every k clocks,
- decay 0.8 / 0.9 / 0.95,
- accumulated loss over k clocks vs single pulse policy. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ดู:

- short-term prediction accuracy,
- memory recall from partial cue,
- stability of recurrent loop,
- noise amplification. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

### 10) PVT robustness tests

พอ core ผ่านแล้วค่อยใส่โลกจริง. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เทียบ:

- no PVT vs with PVT,
- no auto-zeroing vs auto-zeroing,
- no range sensitivity vs PGA coarse/fine,
- no dummy Scap vs dummy Scap calibration,
- no current mirror vs current mirror. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

เก็บ:

- performance drop under drift,
- loss conservation under perturbation,
- clip rate,
- calibration recovery. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ชุดเปรียบเทียบที่ “ควรมีแน่นอน”

ถ้าจะไม่ลืมอะไร ผมว่าชุดขั้นต่ำต้องมีแบบนี้:

- **Full model**
- **No residual**
- **No ForwardSign**
- **No momentum floor**
- **No current mirror / no conservation normalization**
- **SGD baseline**
- **Sequential chain baseline**
- **Single-parent baseline**
- **No gating vs gated reuse**
- **No PVT vs PVT**
- **No auto-zero vs auto-zero**
- **No recurrence vs recurrence**
- **No skip/DAG vs DAG** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ตัวแปรที่ควบคุมให้เหมือนกัน

เวลาทดลอง ให้ล็อกพวกนี้ไว้เหมือนกันทุก run:

- dataset/task,
- random seed,
- initialization range,
- total parameter count or Scap count,
- number of steps,
- batch size,
- learning-rate-like pulse width schedule,
- precision budget per level,
- same task split / same evaluation metric. [youtube](https://www.youtube.com/watch?v=o1wAeKOl2J8)

## ตัวชี้วัดหลักที่ควรบันทึก

- training loss curve,
- validation/task accuracy,
- dead-Scap fraction,
- ceiling saturation fraction,
- loss conservation epsilon,
- update direction correctness,
- convergence speed,
- ablation delta from full model,
- sensitivity to noise/drift,
- relevance vs activity gap. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ลำดับที่ผมแนะนำจริง ๆ

1. Operator sanity.
2. Single Ganglion ideal.
3. Residual ablation.
4. ForwardSign ablation.
5. Momentum dynamics.
6. Loss conservation.
7. Multi-parent Lobe.
8. SpecialGeneralist.
9. Recurrence / limbic loop.
10. PVT robustness. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

## ถ้าจะสรุปสั้นมาก

มึงควรคิดแบบนี้:  
**“หนึ่งรอบทดลอง = เปลี่ยนแค่ 1 เรื่อง”** แล้วเทียบ full model กับ ablation ที่ตัดเรื่องนั้นออก. [youtube](https://www.youtube.com/watch?v=o1wAeKOl2J8)
ถ้าทำทีเดียวหลายอย่าง มึงจะไม่รู้เลยว่ามันดีขึ้นเพราะ residual, เพราะ ForwardSign, เพราะ momentum floor, หรือเพราะโชค. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/994720471/15c113f5-9537-4806-8480-d36140bd256a/draft4.1.md)

ถ้าจะให้ผมจัดต่อ ผมสามารถทำเป็น **ตาราง experiment matrix แบบครบทุก ablation vs baseline** ให้เลยในข้อความเดียว.
