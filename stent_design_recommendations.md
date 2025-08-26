# Stent Design Recommendations (Intracranial, MP35N)
**Device context:** Balloon‑expandable, intracranial stent. Target flat pattern **width = 5.652 mm** (≈ Ø1.80 mm), **length = 8.000 mm**.  
**Lattice:** **6 rings × 8 crowns/ring** (45° crown spacing). Goal: **strong stent‑on‑balloon retention**, **low opening pressure (≈ 2–3 atm)**, and **minimal external dog‑boning**, with slightly **more openable ends** that **do not** force end‑first expansion.

---

## A) Core Geometry (what to draw)

### Material / Cross‑section
- **Alloy:** MP35N (work‑hardened)
- **Thickness \(t\):** **80 µm**
- **Final strut width \(w\):** **Body 50 µm**, **End rings 60–62 µm**
  - *Why:* End hoop stiffness in crimp \(\propto w^3\). 50→60 µm ≈ **1.73×** stiffer ends → higher retention with no profile penalty (profile set by \(t\)).

### Rings & Crowns
- **Rings:** 6 total, **8 crowns/ring** (45°).
- **Wave heights (centerline):** Let **\(H_0\)** be the body height.
  - \(H_1 = 1.20\,H_0\), \(H_2=H_3=H_4=H_5 = 1.00\,H_0\), \(H_6 = 1.10\,H_0\).
  - *Effect:* Ends are **more openable** (taller) but won’t automatically lead expansion.
- **Crown radii (inner \(R_i\); add 25 µm to get centerline \(R_c\)):**
  - **Ends:** \(R_i \approx 95–110\,µm\)
  - **Body:** \(R_i \approx 150–170\,µm\)

### Axial Spacing (apex‑to‑apex gaps)
- Define **\(g_0\)** so that overall height = **8.000 mm** (see formulas in §E).
- To keep ends openable but **not** force end‑first:
  \[
  g_{12} = g_0 - 0.10\,H_0,\quad
  g_{23}=g_{34}=g_{45}=g_0,\quad
  g_{56} = g_0 - 0.05\,H_0.
  \]
  *This reduces end “breathing” in crimp (retention) while taller \(H\) keeps the ends easy to open when needed.*

### Connectors (layout — crown‑to‑crown S‑links)
- **Interface pattern (6 rings → 5 interfaces):** **4 – 3 – 2 – 3 – 4**
  - **Ends (1↔2, 5↔6):** **4 links** at crowns **0,2,4,6**
  - **Near‑ends (2↔3, 4↔5):** **3 links** (e.g., **0,3,6**)
  - **Middle (3↔4):** **2 links**, **rotated +45°** (e.g., **1 & 5**)
- **Why:** Stiff→soft→stiff “breathing” gradient: **high retention at ends**, **low opening pressure centrally**, **uniform torsion**.

### Connectors (dimensions — dog‑bone S‑link)
- **Link‑end width:** ≈ **0.85×** local strut width  
  • Ends ≈ **51–52 µm**; Interior ≈ **43–45 µm**
- **Neck width:** **Ends 32–33 µm**; **Near‑ends 33–34 µm**; **Middle 29–31 µm**
- **Neck length:** **≈ 40 µm**
- **S‑elbow radius (centerline):** **110–120 µm** (≥ max{w, t})
- **Fillet into crowns:** **30–40 µm**, tangent‑continuous
- **Always crown‑to‑crown** (avoid mid‑strut links).

---

## B) Expected Behavior (why this works)
- **Retention ↑:** Wider end struts + **4 links** at ends + **reduced \(g_{12}, g_{56}\)** → higher crimped hoop stiffness → more normal force on balloon shoulders.
- **Low‑pressure onset (≈ 2–3 atm):** Larger **body crown radii** and **softer middle links** let the center start expanding at low pressure with minimal external dog‑bone.
- **End “openability” without early‑lead:** Taller **\(H_1, H_6\)** make ends easy to open **when they reach the wall**, but reduced **\(g\)** prevents automatic end‑first flare.

---

## C) Fold‑Lock (balloon–stent coupling)

1. **Fold count & clocking**  
   Use **6‑fold** (or 3‑fold) balloon. **Clock** so **crowns sit between fold crests** (offset ~**22–30°** relative to folds).

2. **Free balloon length (FBL)**  
   Keep **0.5–1.0 mm per end**. Longer FBL drives external dog‑boning.

3. **Surface friction where it matters**  
   **Mask hydrophilic coating** under the stent zone (leave shaft coated). Optional **micro‑texture** on the balloon stent zone (subtle matte).

4. **End‑only stent friction (safe)**  
   **ID micro‑texture** on *end crowns only*: **2–4 µm** deep dimples, **8–15 µm** pitch, **30–40%** area (fully covered by the balloon).

5. **Crimp & inflation recipe**  
   **Multi‑stage crimp with dwell** (allow folds to seat). **Pre‑inflate** to **1.5–2.0 atm for 5–10 s**, **deflate**, then **slow ramp** to deploy.

6. **Optional sleeves**  
   Thin **PTFE/Pebax sleeves** for delivery; **retract before inflation**.

**Bench checks (fold‑lock):**  
• **Break‑free retention**: balloon shoulder deforms **before** stent slips.  
• **Dog‑bone index @ 3 atm**: \((D_\text{ends}-D_\text{center})/D_\text{center} \approx 0\).  
• **Early P–D slope (0–3 atm)**: steeper in **center** than **ends**.

---

## D) Guardrails
- **Min internal radius** anywhere ≥ **~25 µm** (crowns, links, fillets).
- **S‑elbow radius** ≥ **80–100 µm** (you’re at 110–120 µm).
- **\(g\) floor** ≳ **0.12 mm** at ends (avoid tight link curvature).  
- **2‑link interfaces rotated +45°** each step (1&5 → 2&6 → 3&7 …) to avoid “rails.”
- **No mid‑strut links** (retention & fatigue penalty).
- **Smoothing allowance:** if polishing removes **6 µm/side**, draw **+12 µm** wider pre‑polish to land on final widths.

---

## E) Formulas (hit 8.000 mm height exactly)

Let **\(H_0\)** be body height; \(H_1=1.20H_0\), \(H_6=1.10H_0\).

**With end‑gap reductions (recommended):** All interface spacings become \(S = g_0 + H_0\).  
Total height (bands bbox):
\[
L \;=\; 5\,(g_0+H_0) \;+\; \tfrac{1}{2}\,(H_1+H_6) \;+\; w_\text{end}
\]
Solve:
\[
g_0 \;=\; \frac{L - w_\text{end} - \tfrac{1}{2}(H_1+H_6)}{5}\;-\;H_0
\]
Then set: \(g_{12}=g_0-0.10H_0\), \(g_{56}=g_0-0.05H_0\), others \(= g_0\).

**If you prefer one uniform gap everywhere (no end reductions):**
\[
g_0 \;=\; \frac{L - \tfrac{1}{2}\,(H_1 + 2H_2 + 2H_3 + 2H_4 + 2H_5 + H_6)}{5}
\]

> **Typical numeric anchor:** pick \(H_0 = 0.140\,\text{mm}\).

---

## F) Tuning Cheat‑Sheet
- **Retention too low →** increase end link necks **+1–2 µm** or end strut width to **62 µm**; ensure FBL ≤ 1 mm; consider end‑ID micro‑texture.
- **Opening pressure > 3 atm →** soften middle: necks **−1–2 µm** (e.g., 31→29), or increase body \(R_i\) (e.g., 160→175 µm).
- **External dog‑bone →** shorten FBL; keep \(g_{12}, g_{56}\) reduced; sleeves during delivery; pre‑inflate/deflate to set folds.
- **Connector fatigue hot‑spot →** increase S‑elbow radius (110→120–130 µm) or neck **+1–2 µm** at that interface.

---

## G) Ready‑to‑Build Defaults (drop‑in)
- **t = 80 µm**; **w_body = 50 µm**; **w_end = 60–62 µm**
- **H:** set \(H_0 = 0.140\,\text{mm}\) ⇒ \(H_1=0.168\), \(H_6=0.154\,\text{mm}\)
- **Gaps:** solve \(g_0\) with §E; then \(g_{12}=g_0-0.10H_0\), \(g_{56}=g_0-0.05H_0\)
- **Links:** **4–3–2–3–4**; link‑end ≈ **0.85×** local strut width; **neck**: ends **32–33 µm**, near‑ends **33–34 µm**, middle **29–31 µm**; **neck length ≈ 40 µm**; **\(R_S=110–120 µm\)**; **fillet 30–40 µm**
- **Fold‑lock:** **6‑fold** balloon; **crown–fold offset 22–30°**; **FBL 0.5–1.0 mm**; **stent zone uncoated**; optional **end‑ID micro‑texture**; **pre‑inflate 1.5–2.0 atm → deflate → slow ramp**.

---

## H) CAD Notes
- Use the **guide‑only Fusion script** to draw: exact rectangle **5.652 × 8.000 mm**, **6 ring centerlines**, **only the 3 interior gap midlines**, and **8 crown columns (C/8)**.
- If you later generate full rings, keep **crown‑to‑crown connectors** and **+45° rotation** of the 2‑link middle interface.

---

**Prepared for:** intracranial MP35N stent, 6 rings × 8 crowns, low‑pressure onset with strong retention and controlled expansion profile.
