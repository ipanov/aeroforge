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


# Common 9g class servos
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
