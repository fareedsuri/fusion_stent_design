import math
from dataclasses import dataclass

# ---------- Geometry helpers for a circular crown apex ----------


def theta_from_sagitta(h_mm: float, Rc_um: float) -> float:
    """Solve included angle θ (deg) from sagitta h (mm) and centerline radius Rc (µm)."""
    Rc = Rc_um / 1000.0
    # guard rounding
    c = max(-1.0, min(1.0, 1.0 - h_mm/(2.0*Rc)))
    return 2.0 * math.degrees(math.acos(c))


def sagitta_from_theta(theta_deg: float, Rc_um: float) -> float:
    """Sagitta h (mm) for included angle θ (deg) and centerline radius Rc (µm)."""
    Rc = Rc_um / 1000.0
    return 2.0 * Rc * (1.0 - math.cos(math.radians(theta_deg)/2.0))


def chord_from_theta(theta_deg: float, Rc_um: float) -> float:
    """Chord length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return 2.0 * Rc * math.sin(math.radians(theta_deg)/2.0)


def arc_len_from_theta(theta_deg: float, Rc_um: float) -> float:
    """Arc length (mm) for θ (deg) and Rc (µm)."""
    Rc = Rc_um / 1000.0
    return math.radians(theta_deg) * Rc


def Rc_from_theta_sagitta(theta_deg: float, h_mm: float) -> float:
    """Solve centerline radius Rc (µm) from θ (deg) and sagitta h (mm)."""
    theta = math.radians(theta_deg)
    Rc_mm = h_mm / (2.0 * (1.0 - math.cos(theta/2.0)))
    return Rc_mm * 1000.0


def curvature_from_Rc(Rc_um: float) -> float:
    """Curvature κ = 1/R (1/mm) from centerline Rc (µm)."""
    return 1.0 / (Rc_um / 1000.0)


def radius_to_width_ratio(Rc_um: float, w_um: float) -> float:
    """Rule‑of‑thumb check: Rc / strut width (dimensionless)."""
    return Rc_um / w_um

# (Optional) very rough in‑plane extreme‑fiber strain estimate if the arc curvature changes:
#   eps ≈ (Δκ) * (w/2), where Δκ is change in curvature (1/mm) and w in mm.
# For pure geometric sanity (no Δκ), you can look at (w/2)/Rc as a non‑dimensional index.


def geometric_index_w_over_Rc(w_um: float, Rc_um: float) -> float:
    """(w/2)/Rc (dimensionless). Lower is gentler curvature."""
    return (0.5 * w_um) / Rc_um

# ---------- Convenience container ----------


@dataclass
class CrownArc:
    Rc_um: float
    theta_deg: float

    def sagitta_mm(self) -> float:
        return sagitta_from_theta(self.theta_deg, self.Rc_um)

    def chord_mm(self) -> float:
        return chord_from_theta(self.theta_deg, self.Rc_um)

    def arc_len_mm(self) -> float:
        return arc_len_from_theta(self.theta_deg, self.Rc_um)

    def curvature_mm_inv(self) -> float:
        return curvature_from_Rc(self.Rc_um)

    def r_over_w(self, w_um: float) -> float:
        return radius_to_width_ratio(self.Rc_um, w_um)

    def geom_index(self, w_um: float) -> float:
        return geometric_index_w_over_Rc(w_um, self.Rc_um)
