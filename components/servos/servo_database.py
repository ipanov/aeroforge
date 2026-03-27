"""Component database for off-the-shelf parts.

This module stores specifications for:
- Servos (dimensions, weight, torque, speed)
- Motors (KV, weight, dimensions)
- Batteries (capacity, weight, dimensions)
- Receivers
- Props

All for accurate mass and CG calculations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ServoSpec:
    """Servo specifications."""
    name: str
    brand: str

    # Dimensions (mm)
    length: float
    width: float
    height: float
    horn_height: Optional[float] = None

    # Performance
    torque_4_8v: float  # kg-cm at 4.8V
    torque_6_0v: float  # kg-cm at 6.0V
    speed_4_8v: float   # sec/60° at 4.8V
    speed_6_0v: float   # sec/60° at 6.0V

    # Weight (grams)
    weight: float

    # Wire
    wire_length: float  # mm
    connector: str = "JR"


# Common 9g class servos (plastic gear)
SERVO_DATABASE: Dict[str, ServoSpec] = {
    "towerpro_sg90": ServoSpec(
        name="SG90",
        brand="TowerPro",
        length=22.7,
        width=12.2,
        height=23.5,
        torque_4_8v=1.5,
        torque_6_0v=1.8,
        speed_4_8v=0.12,
        speed_6_0v=0.10,
        weight=9.0,
        wire_length=150,
    ),
    "hitec_hs_55": ServoSpec(
        name="HS-55",
        brand="Hitec",
        length=22.8,
        width=11.6,
        height=24.0,
        torque_4_8v=1.1,
        torque_6_0v=1.3,
        speed_4_8v=0.17,
        speed_6_0v=0.14,
        weight=8.0,
        wire_length=150,
    ),
    "emax_es08a": ServoSpec(
        name="ES08A",
        brand="EMAX",
        length=23.0,
        width=12.0,
        height=24.5,
        torque_4_8v=1.5,
        torque_6_0v=1.8,
        speed_4_8v=0.12,
        speed_6_0v=0.10,
        weight=9.5,
        wire_length=150,
    ),
    "turnigy_tg9": ServoSpec(
        name="TG9",
        brand="Turnigy",
        length=23.0,
        width=12.2,
        height=24.5,
        torque_4_8v=1.5,
        torque_6_0v=1.7,
        speed_4_8v=0.14,
        speed_6_0v=0.12,
        weight=9.0,
        wire_length=200,
    ),
}


# =============================================================================
# METAL GEAR MICRO SERVOS - Budget candidates for RC sailplane
# =============================================================================
# Gear types: MG = metal gear, SG = steel gear, TG = titanium gear
# All dimensions in mm, weight in grams, torque in kg-cm, speed in sec/60deg
#
# PRICE TIERS (AliExpress approximate, single unit):
#   $ = under $5    $$ = $5-15    $$$ = $15-30    $$$$ = $30+

METAL_GEAR_SERVO_DATABASE: Dict[str, ServoSpec] = {

    # --- TIER 1: Ultra-budget ($2-5 on AliExpress) ---

    "towerpro_mg90s": ServoSpec(
        name="MG90S",
        brand="TowerPro",
        length=22.5,
        width=12.0,
        height=35.5,       # NOTE: tall due to metal gear stack
        torque_4_8v=1.8,
        torque_6_0v=2.2,
        speed_4_8v=0.10,
        speed_6_0v=0.08,
        weight=13.4,
        wire_length=250,
        connector="JR",
    ),

    "emax_es08ma_ii": ServoSpec(
        name="ES08MA II",
        brand="EMAX",
        length=23.0,
        width=11.5,
        height=24.0,
        torque_4_8v=1.6,
        torque_6_0v=2.0,
        speed_4_8v=0.12,
        speed_6_0v=0.10,
        weight=12.0,
        wire_length=250,
        connector="JR",
    ),

    # --- TIER 2: Mid-budget digital ($6-10 on AliExpress) ---

    "jx_pdi_1109mg": ServoSpec(
        name="PDI-1109MG",
        brand="JX",
        length=23.2,
        width=12.0,
        height=25.5,
        torque_4_8v=2.2,
        torque_6_0v=2.5,
        speed_4_8v=0.12,
        speed_6_0v=0.10,
        weight=10.0,
        wire_length=180,
        connector="JR",
    ),

    "jx_pdi_933mg": ServoSpec(
        name="PDI-933MG",
        brand="JX",
        length=23.0,
        width=12.0,
        height=25.5,
        torque_4_8v=2.8,
        torque_6_0v=3.5,
        speed_4_8v=0.12,
        speed_6_0v=0.10,
        weight=13.0,
        wire_length=180,
        connector="JR",
    ),

    # --- TIER 3: Glider-specific slim wing servos ($15-30) ---

    "jx_pdi_hv0903mg": ServoSpec(
        name="PDI-HV0903MG",
        brand="JX",
        length=23.5,
        width=8.1,          # 8mm slim wing profile
        height=24.3,
        torque_4_8v=1.5,    # rated at 6V/7.4V primarily
        torque_6_0v=2.0,
        speed_4_8v=0.12,    # estimated; rated 0.09s at 6V
        speed_6_0v=0.09,
        weight=9.0,
        wire_length=150,
        connector="JR",
    ),

    "ptk_7308mg_d": ServoSpec(
        name="7308MG-D",
        brand="PTK",
        length=23.5,
        width=8.0,          # 8mm slim wing profile
        height=16.8,
        torque_4_8v=1.8,    # estimated from voltage curve
        torque_6_0v=2.5,
        speed_4_8v=0.14,    # estimated from voltage curve
        speed_6_0v=0.083,
        weight=8.0,
        wire_length=150,
        connector="JR",
    ),

    # --- TIER 4: Premium budget (KST alternative, $30-35) ---

    "kst_x08_v6": ServoSpec(
        name="X08 V6.0",
        brand="KST",
        length=23.5,
        width=8.0,          # 8mm slim wing profile
        height=16.8,
        torque_4_8v=1.4,    # rated at 4.2V=1.4, 6V=2.2, 8.4V=2.8
        torque_6_0v=2.2,
        speed_4_8v=0.18,    # rated at 4.2V=0.18, 6V=0.15, 8.4V=0.09
        speed_6_0v=0.15,
        weight=8.0,
        wire_length=150,
        connector="JR",
    ),
}


@dataclass
class MotorSpec:
    """Brushless motor specifications."""
    name: str
    brand: str

    # Dimensions
    diameter: float  # mm (stator)
    length: float    # mm (stator)
    shaft_diameter: float  # mm
    weight: float    # grams

    # Electrical
    kv: int          # RPM per volt
    cells: str       # e.g., "2-3S"
    max_current: float  # Amps
    resistance: float   # Ohms

    # Prop recommendations
    prop_2s: Optional[str] = None
    prop_3s: Optional[str] = None


# Sample motor database
MOTOR_DATABASE: Dict[str, MotorSpec] = {
    "turnigy_2217_1650": MotorSpec(
        name="2217 1650KV",
        brand="Turnigy",
        diameter=27.5,
        length=17.0,
        shaft_diameter=3.0,
        weight=46.0,
        kv=1650,
        cells="2-3S",
        max_current=22.0,
        resistance=0.078,
        prop_2s="8x4",
        prop_3s="7x4",
    ),
}


@dataclass
class BatterySpec:
    """Battery specifications."""
    name: str
    brand: str

    # Chemistry
    cells: int       # 2S, 3S, etc.
    capacity: int    # mAh

    # Dimensions
    length: float    # mm
    width: float     # mm
    height: float    # mm

    # Weight
    weight: float    # grams

    # Performance
    c_rating: int    # Discharge rate
    connector: str   # e.g., "XT30", "XT60"


BATTERY_DATABASE: Dict[str, BatterySpec] = {
    "turnigy_500_2s": BatterySpec(
        name="500mAh 2S",
        brand="Turnigy",
        cells=2,
        capacity=500,
        length=45,
        width=20,
        height=10,
        weight=36,
        c_rating=20,
        connector="XT30",
    ),
    "turnigy_850_2s": BatterySpec(
        name="850mAh 2S",
        brand="Turnigy",
        cells=2,
        capacity=850,
        length=55,
        width=25,
        height=12,
        weight=52,
        c_rating=20,
        connector="XT30",
    ),
}


def get_total_component_weight(
    servos: List[str] = None,
    motor: str = None,
    battery: str = None,
) -> dict:
    """Calculate total weight of selected components.

    Returns:
        Dictionary with component weights and total
    """
    weights = {"servos": 0.0, "motor": 0.0, "battery": 0.0, "total": 0.0}

    if servos:
        for servo_name in servos:
            if servo_name in SERVO_DATABASE:
                weights["servos"] += SERVO_DATABASE[servo_name].weight

    if motor and motor in MOTOR_DATABASE:
        weights["motor"] = MOTOR_DATABASE[motor].weight

    if battery and battery in BATTERY_DATABASE:
        weights["battery"] = BATTERY_DATABASE[battery].weight

    weights["total"] = sum([weights["servos"], weights["motor"], weights["battery"]])
    return weights
