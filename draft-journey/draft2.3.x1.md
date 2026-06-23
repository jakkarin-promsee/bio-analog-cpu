# Timeline: Analog Distribution Storage Evolution

## Stage 0 — จุดเริ่มต้น: const-c backprop

**ปัญหา:** scap update ทั้ง die ผ่าน ALU ส่วนกลาง → bottleneck

**ไอเดียแรก:** decentralize update โดยให้ scap แต่ละตัวถือ 1-bit ว่ามัน contribute กับคำตอบมั้ย แล้วใช้ time pulse จาก loss มา drain capacitor พร้อมกันทั้ง die

**จุดอ่อน:** const-c มันหยาบเกินไป gradient ไม่ละเอียดพอที่จะ converge

---

## Stage 1 — Time-charge measurement (8-bit SRAM)

**Breakthrough แรก:** ระหว่างที่ ALU charge output capacitor ของ Ganglion อยู่ มันมี idle slot ที่ใช้ได้

**ไอเดีย:** เพิ่ม trigger capacitor 19 ตัวใน ALU (reuse ตลอด) วัด distribution level ของแต่ละ scap เป็น "time charge from A% to B%" แล้วเก็บเป็น **8-bit ใน SRAM ของแต่ละ scap**

**จุดอ่อน:** 8-bit อาจหยาบไป โดยเฉพาะตอน gradient chain ผ่านหลาย layer error accumulate ได้

---

## Stage 2 — 16-bit + momentum

**ไอเดีย:** ขยายเป็น **16-bit SRAM** ต่อ scap แต่แลกมากับการเก็บ **momentum** ข้าม batch ด้วย (sum distribution เรื่อยๆ)

**Update scheme:** running average แบบ +1/n เก็บค่าเฉลี่ย ถ้า loss สูงจริงๆ ให้ mother signal เปิดเวลาค้างยาว

**จุดอ่อน:**

- +16-bit SRAM/scap = พื้นที่บน die เยอะมาก
- +1/n ทำให้ momentum freeze เมื่อ n ใหญ่ขึ้น (ควรเป็น EMA แต่ EMA ต้องใช้ multiplication)

---

## Stage 3 — Analog momentum (cap2 ตัวเดียว)

**Breakthrough ที่ 2:** ทิ้ง SRAM ไปเลย ใช้ **capacitor analog แทน**

**Architecture:**

- **cap0** = real weight (ไม่แตะจนกว่าจะ update)
- **cap1** = reference ใน ALU, calibrate ตลอด, ต่อกับ digital level trigger
- **cap2** = ใน scap, drain/charge รัวๆ เก็บ distribution level

**Key insight:** cap2 charge ได้ **parallel** ตอนที่ ALU charge output ของ Ganglion อยู่ ไม่กิน critical path เพิ่ม

**จุดอ่อน:**

- charge sharing ไม่ linear กับ time
- leakage drift ข้าม batch
- precision ของ cap2 ตัวเดียวยังจำกัด

---

## Stage 4 — 2D analog precision (cap2 × cap3 cross-multiplication)

**Breakthrough ที่ 3:** แทนที่จะใช้ cap2 ตัวเดียวเก็บ linear scale ใช้ **cap2 × cap3 เป็น 2D coordinate**

**ผลลัพธ์:** range × range = effective precision ระเบิดเป็นกำลังสอง

- 256 levels × 256 levels = **65,536 effective levels** จาก capacitor 2 ตัว
- เกิน 16-bit SRAM ด้วยพื้นที่น้อยกว่า

**ปัญหาเฉพาะหน้า:** cap2 × cap3 = constant มี infinite solutions → ambiguous

---

## Stage 5 — Fixed-larger normalization (แก้ ambiguity)

**Rule:** fix ตัวใหญ่กว่าไว้ update ตัวเล็กกว่า

**Example:** cap2 = 3V, cap3 = 1.5V → fix cap2, load cap3 ด้วย cap2 scale

**ผลลัพธ์:** cap3 กลายเป็น **ratio ของ cap2** เลย — ไม่ใช่ absolute voltage → ambiguity หายไป

**Reconstruction:** opamp คูณตรงๆ cap2 × cap3_ratio = ค่าจริง ไม่ต้องมี ADC

---

## Stage 6 — Addition equation (ปิดวงจร update)

**สมการ update ที่ derive ได้:**

```
cap2 × cap3_old + cap1 = cap2 × cap3_new
```

จัดรูป:

```
cap3_new = cap3_old + (cap1 / cap2)
```

**Key insight:** cap2 fixed → `cap1/cap2` กลายเป็น **constant scale factor** → ทำได้ด้วย **voltage divider ธรรมดา** (resistor ratio นิ่งๆ) ไม่ต้องมี active division

---

## Stage 7 — Cap swap mechanism (dynamic range expansion)

**ปัญหา overflow:** cap3 accumulate ไปเรื่อยๆ จะเกิน cap2 ในที่สุด → invariant พัง

**Solution:** เมื่อ cap3 overflow ให้ **swap บทบาท cap2 ↔ cap3**

**ผลลัพธ์:**

- effective range ขยายเป็น **กำลังสอง** (log-like scaling)
- precision decay เป็น **กำลังสอง** ที่ค่าเล็กๆ

**Open question:** Ganglion weight distribution มันกระจุกที่ range ไหน? ถ้า small weight สำคัญ → quantization noise จะกิน

---

# Summary: สิ่งที่ได้

จาก **16-bit SRAM** (กินพื้นที่ + ไม่ละเอียดพอ)
→ **2 capacitor (cap2, cap3)** + **fixed normalization rule** + **cap swap mechanism**

- **Storage:** capacitor 2 ตัว แทน SRAM 16-bit
- **Precision:** 65,536+ effective levels (vs 65,536 จาก 16-bit แต่ scale ได้ต่อ)
- **Update:** voltage divider + analog charge transfer (ไม่ต้อง ADC)
- **Decentralized:** scap update ตัวเอง parallel กับ ALU compute
