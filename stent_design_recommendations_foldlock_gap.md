# Stent Design Recommendations (Intracranial, MP35N) — **with explicit Fold‑Lock Gap**
**Device context:** Balloon‑expandable, intracranial stent. Flat pattern **width = 5.652 mm** (≈ Ø1.80 mm), **length = 8.000 mm**.  
**Lattice:** **6 rings × 8 crowns/ring**. Goals: **strong stent‑on‑balloon retention**, **low opening pressure (≈ 2–3 atm)**, **minimal external dog‑boning**, and **more‑openable ends** that **don’t force** end‑first expansion.

---

## A) Core Geometry
- **Material:** MP35N; **thickness (t) = 80 µm**.  
- **Final strut width (w):** **Body 50 µm**, **End rings 60–62 µm**.

**Rings & crowns**
- **Wave heights:** H₁ = 1.20·H₀, H₂–H₅ = H₀, H₆ = 1.10·H₀.
- **Crown radii (inner Rᵢ):** **Ends 95–110 µm**, **Body 150–170 µm**.

**Connectors (crown‑to‑crown S‑links)**
- **Pattern:** **4 – 3 – 2 – 3 – 4** (ends → near‑ends → middle → near‑ends → ends).  
- **Dimensions:** link‑end ≈ **0.85×w**; neck **ends 32–33 µm**, **near‑ends 33–34 µm**, **middle 29–31 µm**; neck length **≈ 40 µm**; S‑elbow radius **110–120 µm**; fillet **30–40 µm**.

---

## B) Fold‑Lock (balloon–stent coupling)

### 1) Fold‑lock **gap** (explicit)
We define the **fold‑lock gap** as the **apex‑to‑apex window** between the **end ring** and the **first interior ring** (interfaces **1↔2** and **5↔6**) sized to capture balloon fold crests while keeping end “breathing” low for retention.

- **Recommended sizing rule:**  
  g_FL,12 = g₀ − 0.10·H₀,    g_FL,56 = g₀ − 0.05·H₀  
  where g₀ is the uniform body gap that sets overall length (see §E).

- **With your anchors** (H₀ = 0.140 mm, L = 8.000 mm):  
  - g₀ = 1.428 mm  
  - **Fold‑lock gaps:** g_FL,12 = 1.414 mm,  g_FL,56 = 1.421 mm

*Why this works:* taller end waves (H₁, H₆) make the ends **easy to open** when engaged; the **slightly smaller gaps** at the ends **dampen end breathing in crimp**, increasing normal force on the balloon and preventing early end‑first flare—yet the gaps remain large enough to **accept fold crests**.

### 2) Fold count, clocking, and free length
- **Balloon folds:** use **6‑fold** (or 3‑fold). **Clock** the stent so **crowns sit between fold crests** (offset ~**22–30°**).  
- **Free balloon length (FBL):** **0.5–1.0 mm per end** (short) to minimize external dog‑bone.  
- **Surface friction:** mask hydrophilic coating under stent; optional subtle micro‑texture in the stent zone.  
- **End‑only friction:** ID micro‑texture on end crowns (2–4 µm deep, 8–15 µm pitch, 30–40% area).  
- **Inflation recipe:** pre‑inflate **1.5–2.0 atm for 5–10 s**, deflate, then slow ramp.

---

## C) Guardrails
- **Minimum internal radius ≥ ~25 µm** (anywhere).  
- **S‑elbow radius ≥ 80–100 µm** (target 110–120 µm).  
- **Avoid mid‑strut links**.  
- **Rotate 2‑link middle interface +45°** each step to avoid rails/twist.  
- If smoothing removes **6 µm/side**, draw **+12 µm** wider pre‑polish.

---

## D) Expected Behavior
- **Retention ↑** (stout ends, 4 links, smaller end gaps).  
- **Low‑pressure onset (≈ 2–3 atm)** (gentle body crowns + soft middle links).  
- **Controlled profile** (FBL short; minimal external dog‑bone).

---

## E) Length‑setting formula
With H₁ = 1.20·H₀ and H₆ = 1.10·H₀ (and the end‑gap reductions above), **all interface spacings** equal S = g₀ + H₀.  
Total height L = 5·S + ½·(H₁ + H₆). Solve for g₀:

g₀ = (L − ½·(H₁ + H₆)) / 5 − H₀

Then set g_FL,12 = g₀ − 0.10·H₀,  g_FL,56 = g₀ − 0.05·H₀.

---

## F) Ready‑to‑build numbers (example)
- H₀ = 0.140 mm → H₁ = 0.168 mm, H₆ = 0.154 mm  
- Solved g₀ = 1.428 mm → **fold‑lock gaps:** g_FL,12 = 1.414 mm, g_FL,56 = 1.421 mm  
- Links: **4–3–2–3–4** with neck widths **[32–33, 33–34, 29–31] µm** (ends, near‑ends, middle), neck length **≈40 µm**, S‑elbow radius **110–120 µm**.  
- Fold‑lock implementation: **6‑fold balloon**, **22–30° offset**, **FBL 0.5–1.0 mm**, **pre‑inflate → deflate → slow ramp**.
