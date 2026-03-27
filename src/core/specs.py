"""Single Source of Truth for all design parameters.

THIS IS THE SINGLE SOURCE OF TRUTH. Every design parameter lives here.
Documentation, code, and tests derive from these values.

When a parameter changes here, the DAG propagation system ensures all
dependent components, calculations, and exports are updated.

Usage:
    from src.core.specs import SAILPLANE_SPEC, WING_SPEC, SPAR_SPEC

    # Access any parameter
    wingspan = WING_SPEC.wingspan
    root_chord = WING_SPEC.root_chord

    # Change a parameter (triggers validation)
    WING_SPEC.wingspan = 2200  # mm

All dimensions in mm, weights in grams, angles in degrees.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── Wing Specification ────────────────────────────────────────────

class AirfoilStation(BaseModel):
    """Airfoil at a specific span station."""
    span_fraction: float   # 0.0 = root, 1.0 = tip
    airfoil: str           # e.g. "AG24", "AG09", "AG03"
    chord: float           # mm, at this station (derived from taper)


class WingSpec(BaseModel):
    """Wing geometry specification."""
    wingspan: float = 2100.0           # mm total wingspan
    root_chord: float = 200.0          # mm
    tip_chord: float = 110.0           # mm
    panels_per_half: int = 3           # 3 panels per half = 6 total
    sweep_angle: float = 0.0           # degrees (TBD, AI-optimized)
    dihedral_angle: float = 0.0        # degrees (TBD, AI-optimized)
    washout_tip: float = 0.0           # degrees (TBD, AI-optimized, negative = nose down)

    # Airfoil blend stations
    airfoil_root: str = "AG24"
    airfoil_mid: str = "AG09"
    airfoil_tip: str = "AG03"

    # Structural
    main_spar_od: float = 8.0          # mm, carbon tube outer diameter
    rear_spar_width: float = 5.0       # mm, spruce strip width
    rear_spar_height: float = 3.0      # mm, spruce strip height
    skin_thickness: float = 0.5        # mm, LW-PLA wall thickness
    rib_thickness: float = 1.2         # mm, PLA rib wall thickness
    dbox_cutoff: float = 0.30          # fraction of chord for D-box (30%)

    # Computed properties
    @property
    def half_span(self) -> float:
        return self.wingspan / 2

    @property
    def taper_ratio(self) -> float:
        return self.tip_chord / self.root_chord

    @property
    def mean_chord(self) -> float:
        return (self.root_chord + self.tip_chord) / 2

    @property
    def wing_area_dm2(self) -> float:
        """Wing area in dm² (for wing loading calculation)."""
        area_mm2 = self.wingspan * self.mean_chord  # trapezoidal approx
        return area_mm2 / 10000  # mm² to dm²

    @property
    def aspect_ratio(self) -> float:
        return self.wingspan / self.mean_chord

    @property
    def panel_span(self) -> float:
        """Span of each panel in mm."""
        return self.half_span / self.panels_per_half

    @property
    def total_panels(self) -> int:
        return self.panels_per_half * 2

    def chord_at(self, span_fraction: float) -> float:
        """Chord at any span fraction (0=root, 1=tip). Linear taper."""
        return self.root_chord + (self.tip_chord - self.root_chord) * span_fraction

    def reynolds_at(self, span_fraction: float, velocity: float = 8.0) -> float:
        """Reynolds number at a span station. Default cruise velocity 8 m/s."""
        chord_m = self.chord_at(span_fraction) / 1000  # mm to m
        kinematic_viscosity = 1.5e-5  # m²/s for air at 20°C
        return velocity * chord_m / kinematic_viscosity


# ── Spar Specification ────────────────────────────────────────────

class SparSpec(BaseModel):
    """Spar specifications (off-the-shelf carbon + spruce)."""
    main_type: str = "carbon_tube"
    main_od: float = 8.0               # mm outer diameter (must fit in tip airfoil)
    main_id: float = 6.0               # mm inner diameter (1mm wall)
    main_material: str = "carbon_tube"
    main_position_chord_fraction: float = 0.28  # 28% chord

    rear_type: str = "spruce_strip"
    rear_width: float = 5.0            # mm
    rear_height: float = 3.0           # mm
    rear_material: str = "spruce"
    rear_position_chord_fraction: float = 0.65  # 65% chord

    boom_type: str = "carbon_tube"
    boom_od: float = 12.0              # mm
    boom_id: float = 10.0              # mm
    boom_length: float = 650.0         # mm


# ── Fuselage Specification ────────────────────────────────────────

class FuselageSpec(BaseModel):
    """Fuselage pod and boom specification."""
    pod_length: float = 220.0          # mm
    pod_max_width: float = 55.0        # mm
    pod_max_height: float = 50.0       # mm
    boom_od: float = 12.0              # mm (same as spar spec)
    boom_length: float = 650.0         # mm
    cg_target_chord_fraction: float = 0.32  # 32% of MAC


# ── Empennage Specification ───────────────────────────────────────

class EmpennageSpec(BaseModel):
    """Tail surfaces specification."""
    config: str = "conventional"       # conventional, v_tail, t_tail

    h_stab_span: float = 400.0        # mm
    h_stab_chord: float = 80.0        # mm
    h_stab_airfoil: str = "NACA0009"
    elevator_chord_ratio: float = 0.33 # elevator as fraction of chord

    v_stab_height: float = 120.0       # mm
    v_stab_root_chord: float = 100.0   # mm
    v_stab_tip_chord: float = 60.0     # mm
    v_stab_airfoil: str = "NACA0009"
    rudder_chord_ratio: float = 0.35

    tail_moment_arm: float = 650.0     # mm (boom length, approx CG to tail AC)


# ── Electronics (Fixed Constraints) ──────────────────────────────

class BatterySpec(BaseModel):
    """Battery specification - FIXED, owner's inventory.

    Racing 3S 1300mAh 75C LiPo. Typical brands: Tattu, GNB, CNHL, Turnigy.
    Dimensions are envelope max across common brands (for battery bay sizing).
    Owner has XT60 connectors soldered on.
    """
    name: str = "Racing 3S 1300mAh 75C"
    cells: int = 3
    voltage: float = 11.1              # nominal
    capacity_mah: int = 1300
    c_rating: int = 75
    weight: float = 155.0              # grams (pack only, typical racing 75C)
    weight_with_connector: float = 165.0  # grams (with XT60 + leads)
    length: float = 78.0               # mm (typical, design bay for 80mm)
    width: float = 38.0                # mm (typical, design bay for 40mm)
    height: float = 28.0               # mm (typical, design bay for 30mm)
    connector: str = "XT60"
    connector_weight: float = 10.0     # grams (XT60 + 14AWG leads)


class ReceiverSpec(BaseModel):
    """Receiver specification - FIXED, owner's inventory."""
    name: str = "Turnigy 9X V2 8ch"
    channels: int = 8
    weight: float = 18.0               # grams
    length: float = 52.0               # mm
    width: float = 35.0                # mm
    height: float = 15.0               # mm


# ── Control System ────────────────────────────────────────────────

class FlightMode(BaseModel):
    """Flight mode mixing definition."""
    name: str
    aileron_offset: float = 0.0        # degrees
    flap_offset: float = 0.0           # degrees
    elevator_trim: float = 0.0         # degrees
    description: str = ""


class ControlSpec(BaseModel):
    """Control surfaces and mixing specification."""
    servo_count: int = 6
    servo_weight: float = 9.0          # grams each (9g class)

    aileron_chord_ratio: float = 0.22  # aileron as fraction of wing chord
    aileron_span_start: float = 0.55   # fraction of half-span where aileron starts
    flap_chord_ratio: float = 0.27     # flap as fraction of wing chord
    flap_span_end: float = 0.55        # fraction of half-span where flap ends

    flight_modes: list[FlightMode] = Field(default_factory=lambda: [
        FlightMode(name="Launch", aileron_offset=2.0, flap_offset=2.0,
                   elevator_trim=-1.0, description="Motor climb, max speed"),
        FlightMode(name="Cruise", description="Normal flying"),
        FlightMode(name="Speed", flap_offset=1.0, elevator_trim=-0.5,
                   description="Wind penetration, reflex"),
        FlightMode(name="Thermal", aileron_offset=-2.0, flap_offset=-5.0,
                   elevator_trim=1.0, description="Circling, min sink, camber"),
        FlightMode(name="Landing", aileron_offset=45.0, flap_offset=-60.0,
                   elevator_trim=-3.0, description="Crow braking, steep descent"),
    ])


# ── Manufacturing ─────────────────────────────────────────────────

class PrintSpec(BaseModel):
    """3D printing specification."""
    printer_model: str = "Bambu A1 / P1S"
    bed_x: float = 256.0              # mm
    bed_y: float = 256.0              # mm
    bed_z: float = 256.0              # mm
    primary_material: str = "LW-PLA"
    structural_material: str = "PLA"
    flexible_material: str = "TPU"


# ── Top-Level Sailplane Spec ─────────────────────────────────────

class SailplaneSpec(BaseModel):
    """Top-level sailplane specification. THE single source of truth."""
    name: str = "AeroForge v0.1"
    wing: WingSpec = Field(default_factory=WingSpec)
    spar: SparSpec = Field(default_factory=SparSpec)
    fuselage: FuselageSpec = Field(default_factory=FuselageSpec)
    empennage: EmpennageSpec = Field(default_factory=EmpennageSpec)
    battery: BatterySpec = Field(default_factory=BatterySpec)
    receiver: ReceiverSpec = Field(default_factory=ReceiverSpec)
    controls: ControlSpec = Field(default_factory=ControlSpec)
    printing: PrintSpec = Field(default_factory=PrintSpec)

    @property
    def electronics_weight(self) -> float:
        """Total electronics weight in grams."""
        motor_est = 55.0       # TBD - will order ideal motor
        esc_est = 17.0
        prop_est = 17.0
        wiring_est = 22.0
        servo_total = self.controls.servo_count * self.controls.servo_weight
        return (self.battery.weight + self.receiver.weight + servo_total +
                motor_est + esc_est + prop_est + wiring_est)

    @property
    def wing_loading_at_auw(self) -> dict[str, float]:
        """Wing loading estimates at different AUW targets."""
        area = self.wing.wing_area_dm2
        return {
            "at_700g": 700 / area,
            "at_750g": 750 / area,
            "at_800g": 800 / area,
            "at_850g": 850 / area,
        }

    def summary(self) -> str:
        """Print a human-readable summary of all specs."""
        wl = self.wing_loading_at_auw
        return f"""
AeroForge Sailplane Specification Summary
==========================================
Wingspan:       {self.wing.wingspan:.0f}mm ({self.wing.wingspan/1000:.2f}m)
Root chord:     {self.wing.root_chord:.0f}mm
Tip chord:      {self.wing.tip_chord:.0f}mm
Taper ratio:    {self.wing.taper_ratio:.2f}
Aspect ratio:   {self.wing.aspect_ratio:.1f}
Wing area:      {self.wing.wing_area_dm2:.1f} dm²
Panels:         {self.wing.total_panels} ({self.wing.panels_per_half}/half, {self.wing.panel_span:.0f}mm each)
Airfoil:        {self.wing.airfoil_root} → {self.wing.airfoil_mid} → {self.wing.airfoil_tip}
Main spar:      {self.spar.main_od:.0f}mm carbon tube
Rear spar:      {self.spar.rear_width:.0f}x{self.spar.rear_height:.0f}mm spruce
Servos:         {self.controls.servo_count}x {self.controls.servo_weight:.0f}g
Battery:        {self.battery.cells}S {self.battery.capacity_mah}mAh ({self.battery.weight:.0f}g)
Electronics:    ~{self.electronics_weight:.0f}g
Wing loading:   {wl['at_750g']:.1f} g/dm² (at 750g AUW)
Re at root:     {self.wing.reynolds_at(0):.0f} (8 m/s cruise)
Re at tip:      {self.wing.reynolds_at(1):.0f} (8 m/s cruise)
"""


# ── Global Instance ───────────────────────────────────────────────
# Import this everywhere. Change it here, everything updates.

SAILPLANE = SailplaneSpec()
